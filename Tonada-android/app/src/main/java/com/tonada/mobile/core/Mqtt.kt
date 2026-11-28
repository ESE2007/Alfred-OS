package com.tonada.mobile.core

import java.util.concurrent.Executors
import java.util.concurrent.ScheduledFuture
import java.util.concurrent.TimeUnit

/** A WebSocket, abstracted so the same code runs on Android (OkHttp) and on the JVM (tests). */
interface WsTransport {
    interface Listener {
        fun onOpen()
        fun onBinary(data: ByteArray)
        fun onClosed(reason: String)
    }

    fun connect(url: String, subprotocol: String, listener: Listener)
    fun send(data: ByteArray)
    fun close()
}

/**
 * Minimal MQTT 3.1.1 client over WebSocket: QoS 0 publish/subscribe, keep-alive, automatic reconnection.
 * All state lives on one single-threaded executor; callbacks to [Handler] come from that thread.
 */
class MqttClient(
    private val newTransport: () -> WsTransport,
    private val url: String,
    private val clientId: String,
    private val subscribeTopic: String,
    private val h: Handler,
) {
    enum class Status { OFF, CONNECTING, ONLINE, OFFLINE, ERROR }

    interface Handler {
        fun onStatus(status: Status, detail: String?)
        fun onMessage(topic: String, payload: ByteArray)
        fun onConnected()
    }

    private val exec = Executors.newSingleThreadScheduledExecutor { r -> Thread(r, "tonada-mqtt").apply { isDaemon = true } }
    private var gen = 0
    private var ws: WsTransport? = null
    private var buf = ByteArray(0)
    private var lastRx = 0L
    private var retry = 0
    private var closed = true
    private var pingTask: ScheduledFuture<*>? = null
    private var retryTask: ScheduledFuture<*>? = null

    @Volatile
    var online = false
        private set

    fun start() {
        exec.execute {
            closed = false
            connect()
        }
    }

    /** Stops for good: closes the socket and the worker thread. */
    fun release() {
        exec.execute {
            closed = true
            pingTask?.cancel(false)
            retryTask?.cancel(false)
            val w = ws
            ws = null
            online = false
            gen++
            if (w != null) {
                try { w.send(byteArrayOf(0xE0.toByte(), 0)) } catch (e: Exception) { }
                try { w.close() } catch (e: Exception) { }
            }
            h.onStatus(Status.OFF, null)
        }
        exec.shutdown()
    }

    fun publish(topic: String, payload: ByteArray, retain: Boolean = false) {
        try {
            exec.execute {
                if (!online) return@execute
                val t = topic.toByteArray(Charsets.UTF_8)
                val body = 2 + t.size + payload.size
                val out = ArrayList<Byte>(body + 5)
                out.add((0x30 or (if (retain) 1 else 0)).toByte())
                for (b in varint(body)) out.add(b)
                out.add((t.size shr 8).toByte())
                out.add((t.size and 255).toByte())
                val pkt = out.toByteArray() + t + payload
                try { ws?.send(pkt) } catch (e: Exception) { }
            }
        } catch (e: java.util.concurrent.RejectedExecutionException) {
        }
    }

    // ---------------------------------------------------------------- internals (exec thread)

    private fun connect() {
        if (closed) return
        val my = ++gen
        h.onStatus(Status.CONNECTING, null)
        val t = newTransport()
        ws = t
        buf = ByteArray(0)
        try {
            t.connect(url, "mqtt", object : WsTransport.Listener {
                override fun onOpen() = post { if (my == gen && !closed) t.send(connectPacket()) }
                override fun onBinary(data: ByteArray) = post { if (my == gen) feed(data) }
                override fun onClosed(reason: String) = post { if (my == gen) down(reason) }
            })
        } catch (e: Exception) {
            down(e.message ?: "connect failed")
        }
    }

    private fun post(f: () -> Unit) {
        try { exec.execute { try { f() } catch (e: Exception) { } } } catch (e: java.util.concurrent.RejectedExecutionException) { }
    }

    private fun down(reason: String) {
        pingTask?.cancel(false)
        ws = null
        online = false
        if (closed) return
        h.onStatus(Status.OFFLINE, reason)
        val delay = minOf(60000L, 2000L shl minOf(retry++, 5)) + (Math.random() * 500).toLong()
        retryTask?.cancel(false)
        retryTask = exec.schedule({ connect() }, delay, TimeUnit.MILLISECONDS)
    }

    private fun mqttStr(s: String): ByteArray {
        val b = s.toByteArray(Charsets.UTF_8)
        return byteArrayOf((b.size shr 8).toByte(), (b.size and 255).toByte()) + b
    }

    private fun varint(n0: Int): ByteArray {
        var n = n0
        val o = ArrayList<Byte>()
        do {
            var b = n % 128
            n /= 128
            if (n > 0) b = b or 128
            o.add(b.toByte())
        } while (n > 0)
        return o.toByteArray()
    }

    private fun connectPacket(): ByteArray {
        val vh = byteArrayOf(0, 4, 0x4D, 0x51, 0x54, 0x54, 4, 0x02, 0, 30)
        val pl = mqttStr(clientId)
        return byteArrayOf(0x10) + varint(vh.size + pl.size) + vh + pl
    }

    private fun feed(data: ByteArray) {
        buf += data
        while (true) {
            if (buf.size < 2) return
            var mul = 1
            var len = 0
            var i = 1
            var b: Int
            do {
                if (i >= buf.size) return
                b = buf[i++].toInt() and 0xff
                len += (b and 127) * mul
                mul *= 128
                if (mul > 128 * 128 * 128 * 128) {
                    ws?.close()
                    return
                }
            } while (b and 128 != 0)
            if (buf.size < i + len) return
            val type = (buf[0].toInt() and 0xff) shr 4
            val flags = buf[0].toInt() and 15
            val body = buf.copyOfRange(i, i + len)
            buf = buf.copyOfRange(i + len, buf.size)
            packet(type, flags, body)
        }
    }

    private fun packet(type: Int, flags: Int, body: ByteArray) {
        lastRx = System.currentTimeMillis()
        if (type == 2) { // CONNACK
            val rc = if (body.size > 1) body[1].toInt() and 0xff else 255
            if (rc != 0) {
                h.onStatus(Status.ERROR, "broker refused the connection ($rc)")
                ws?.close()
                return
            }
            online = true
            retry = 0
            h.onStatus(Status.ONLINE, null)
            val t = subscribeTopic.toByteArray(Charsets.UTF_8)
            val sub = byteArrayOf(0, 1, (t.size shr 8).toByte(), (t.size and 255).toByte()) + t + byteArrayOf(0)
            ws?.send(byteArrayOf(0x82.toByte()) + varint(sub.size) + sub)
            pingTask?.cancel(false)
            pingTask = exec.scheduleAtFixedRate({ ping() }, 15, 15, TimeUnit.SECONDS)
            h.onConnected()
        } else if (type == 3) { // PUBLISH
            val qos = (flags shr 1) and 3
            val tl = ((body[0].toInt() and 0xff) shl 8) or (body[1].toInt() and 0xff)
            val topic = String(body, 2, tl, Charsets.UTF_8)
            var p = 2 + tl
            if (qos > 0) {
                val b0 = body[p]
                val b1 = body[p + 1]
                p += 2
                if (qos == 1) ws?.send(byteArrayOf(0x40, 2, b0, b1))
            }
            h.onMessage(topic, body.copyOfRange(p, body.size))
        }
    }

    private fun ping() {
        if (!online) return
        if (System.currentTimeMillis() - lastRx > 50000) {
            ws?.close()
            return
        }
        try { ws?.send(byteArrayOf(0xC0.toByte(), 0)) } catch (e: Exception) { }
    }
}
