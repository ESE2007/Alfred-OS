package com.tonada.mobile.core

import java.util.Timer
import java.util.TimerTask

/**
 * The phone's side of Tonada Remote (docs/PROTOCOL.md): receives the PC's state and sends it commands.
 * Callbacks arrive on a background thread; the Android layer posts them to the main thread.
 */
class RemoteClient(
    private val pair: PairInfo,
    private val deviceId: String,
    private val deviceName: String,
    newTransport: () -> WsTransport,
    private val l: Listener,
) : MqttClient.Handler {

    interface Listener {
        fun onStatus(status: MqttClient.Status, detail: String?)
        fun onState(s: RemoteState)
        fun onQueue(q: RemoteQueue)
        fun onArt(key: String, jpeg: ByteArray?)
        fun onAck(nonce: String, ok: Boolean, err: String?, miss: Int)
    }

    private val box = Crypto.Box(Crypto.b64uDecode(pair.key))
    private val tPc = "tonada/v1/${pair.room}/pc"
    private val tM = "tonada/v1/${pair.room}/m"
    private val mq = MqttClient(newTransport, pair.broker, "tonada-m-" + Crypto.randomHex(5), tPc, this)
    private var timer: Timer? = null

    val online: Boolean get() = mq.online

    fun start() {
        mq.start()
        val t = Timer("tonada-hb", true)
        t.schedule(object : TimerTask() {
            override fun run() {
                if (mq.online) send("hb")
            }
        }, 40000, 40000)
        timer = t
    }

    fun stop() {
        timer?.cancel()
        timer = null
        mq.release()
    }

    /** Sends a command and returns its nonce (the PC answers with an `ack` carrying the same nonce). */
    fun send(c: String, params: Map<String, Any?> = emptyMap()): String {
        val n = Crypto.randomHex(8)
        val m = LinkedHashMap<String, Any?>()
        m["t"] = "cmd"
        m["ts"] = System.currentTimeMillis()
        m["n"] = n
        m["did"] = deviceId
        m["dn"] = deviceName
        m["c"] = c
        m.putAll(params)
        mq.publish(tM, box.seal(Json.stringify(m), tM), false)
        return n
    }

    fun playTracks(items: List<Ent>, start: Int, posSec: Double, play: Boolean, name: String): String =
        send("playTracks", mapOf("items" to items.map { it.toRef() }, "start" to start, "pos" to posSec, "play" to play, "name" to name))

    fun enqueue(items: List<Ent>, next: Boolean): String =
        send("enqueue", mapOf("items" to items.map { it.toRef() }, "where" to if (next) "next" else "end"))

    // ------------------------------------------------------------ MqttClient.Handler
    override fun onStatus(status: MqttClient.Status, detail: String?) = l.onStatus(status, detail)

    override fun onConnected() {
        send("hello")
    }

    override fun onMessage(topic: String, payload: ByteArray) {
        if (topic != tPc) return
        val js = box.open(payload, topic) ?: return
        val m = try { Json.parse(js) as? Map<*, *> } catch (e: Exception) { null } ?: return
        when (m["t"]) {
            "state" -> l.onState(parseState(m, System.currentTimeMillis()))
            "queue" -> l.onQueue(parseQueue(m))
            "art" -> {
                val d = m.str("d")
                l.onArt(m.str("k"), if (d.isEmpty()) null else try { Crypto.b64uDecode(d) } catch (e: Exception) { null })
            }
            "ack" -> l.onAck(m.str("n"), m.bool("ok"), (m["err"] as? String), m.num("miss").toInt())
        }
    }
}
