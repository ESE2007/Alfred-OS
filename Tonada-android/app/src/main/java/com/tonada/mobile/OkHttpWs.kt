package com.tonada.mobile

import com.tonada.mobile.core.WsTransport
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import okio.ByteString
import okio.ByteString.Companion.toByteString
import java.util.concurrent.TimeUnit

/** WebSocket transport for the MQTT client, backed by OkHttp. */
class OkHttpWs : WsTransport {
    companion object {
        private val client: OkHttpClient = OkHttpClient.Builder()
            .connectTimeout(12, TimeUnit.SECONDS)
            .readTimeout(0, TimeUnit.MILLISECONDS)
            .build()
    }

    @Volatile
    private var ws: WebSocket? = null

    override fun connect(url: String, subprotocol: String, listener: WsTransport.Listener) {
        val req = Request.Builder().url(url).header("Sec-WebSocket-Protocol", subprotocol).build()
        ws = client.newWebSocket(req, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                listener.onOpen()
            }

            override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
                listener.onBinary(bytes.toByteArray())
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                webSocket.close(1000, null)
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                listener.onClosed("cerrado ($code)")
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                listener.onClosed(t.message ?: "error de red")
            }
        })
    }

    override fun send(data: ByteArray) {
        ws?.send(data.toByteString())
    }

    override fun close() {
        try {
            ws?.close(1000, null)
        } catch (e: Exception) {
        }
    }
}
