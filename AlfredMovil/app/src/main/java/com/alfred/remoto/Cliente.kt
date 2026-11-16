package com.alfred.remoto

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

/** Enlace que Alfred muestra en ☰ Menú → Remoto: http://192.168.1.20:47654/#t=CLAVE */
object Enlace {
    const val PUERTO = 47654

    class Datos(val base: String, val clave: String?)

    fun analizar(entrada: String): Datos? {
        var resto = entrada.trim()
        if (resto.isEmpty()) return null
        var clave: String? = null
        val i = resto.indexOf("#t=")
        if (i >= 0) {
            clave = resto.substring(i + 3).trim().ifEmpty { null }
            resto = resto.substring(0, i)
        }
        if (!resto.startsWith("http://") && !resto.startsWith("https://")) resto = "http://$resto"
        val m = Regex("^(https?://[^/?#\\s]+)").find(resto) ?: return null
        return Datos(m.groupValues[1], clave)
    }

    fun tienePuerto(base: String): Boolean = Regex(":\\d+$").containsMatchIn(base)
}

class Cliente(val base: String, val clave: String) {

    class Resp(val codigo: Int, val json: JSONObject?)

    fun pedir(
        metodo: String,
        ruta: String,
        cuerpo: JSONObject? = null,
        lecturaMs: Int = 10000,
        conClave: Boolean = true
    ): Resp = peticion(base, metodo, ruta, cuerpo, 5000, lecturaMs, if (conClave) clave else null)

    companion object {
        fun peticion(
            base: String, metodo: String, ruta: String, cuerpo: JSONObject?,
            conexionMs: Int, lecturaMs: Int, clave: String?
        ): Resp {
            val c = URL(base.trimEnd('/') + ruta).openConnection() as HttpURLConnection
            try {
                c.requestMethod = metodo
                c.connectTimeout = conexionMs
                c.readTimeout = lecturaMs
                c.setRequestProperty("Accept", "application/json")
                if (clave != null) c.setRequestProperty("Authorization", "Bearer $clave")
                if (cuerpo != null) {
                    c.doOutput = true
                    c.setRequestProperty("Content-Type", "application/json; charset=utf-8")
                    c.outputStream.use { it.write(cuerpo.toString().toByteArray(Charsets.UTF_8)) }
                }
                val codigo = c.responseCode
                val flujo = if (codigo in 200..299) c.inputStream else c.errorStream
                val texto = flujo?.bufferedReader(Charsets.UTF_8)?.use { it.readText() } ?: ""
                val json = try { JSONObject(texto) } catch (e: Exception) { null }
                return Resp(codigo, json)
            } finally {
                c.disconnect()
            }
        }

        /** ¿Hay un Alfred en esa dirección? (/api/ping no pide clave y no devuelve datos). */
        fun hayAlfred(base: String): Boolean = try {
            val r = peticion(base, "GET", "/api/ping", null, 1500, 1500, null)
            r.codigo == 200 && r.json?.optString("app") == "alfred"
        } catch (e: Exception) {
            false
        }

        /** Si la dirección no trae puerto, prueba los 6 que Alfred puede usar (47654 al 47659). */
        fun descubrir(base: String): String? {
            if (Enlace.tienePuerto(base)) return if (hayAlfred(base)) base else null
            for (p in Enlace.PUERTO until Enlace.PUERTO + 6) {
                val b = "$base:$p"
                if (hayAlfred(b)) return b
            }
            return null
        }
    }
}
