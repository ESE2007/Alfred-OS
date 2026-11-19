package com.alfred.remoto

import org.json.JSONObject
import java.io.IOException
import java.net.HttpURLConnection
import java.net.InetSocketAddress
import java.net.NetworkInterface
import java.net.Socket
import java.net.URL
import java.net.URLDecoder
import java.security.SecureRandom
import java.util.Collections
import java.util.concurrent.Callable
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

/** Lo que el teléfono entiende cuando le llega un QR o un enlace de Alfred. */
object Enlace {
    const val PUERTO = 47654

    /** Enlace de vinculación (el QR del PC): alfred://v2?c=CÓDIGO&n=NOMBRE&h=IP:PUERTO&h=IP:PUERTO… */
    class Vinculo(val codigo: String, val nombrePc: String, val rutas: List<String>)

    /** Enlace de la versión 1.0 / de la página web: http://IP:PUERTO/#t=CLAVE (o solo la IP). */
    class Antiguo(val base: String, val clave: String?)

    fun esVinculo(texto: String): Boolean = texto.trim().startsWith("alfred://", ignoreCase = true)

    /** «192.168.1.20:47654» → «http://192.168.1.20:47654». Deja pasar http:// y https://. */
    fun normalizarRuta(entrada: String): String {
        var r = entrada.trim()
        if (!r.startsWith("http://", ignoreCase = true) && !r.startsWith("https://", ignoreCase = true)) r = "http://$r"
        val m = Regex("^(https?://[^/?#\\s]+)", RegexOption.IGNORE_CASE).find(r)
        return m?.groupValues?.get(1) ?: r
    }

    fun analizarVinculo(entrada: String): Vinculo? {
        val t = entrada.trim()
        if (!esVinculo(t)) return null
        val q = t.substringAfter("?", "")
        if (q.isEmpty()) return null
        var codigo = ""
        var nombre = ""
        val rutas = ArrayList<String>()
        for (par in q.split("&")) {
            val k = par.substringBefore("=")
            val v = try {
                URLDecoder.decode(par.substringAfter("=", ""), "UTF-8")
            } catch (e: Exception) {
                ""
            }
            if (k == "c") codigo = v
            else if (k == "n") nombre = v
            else if (k == "h" && v.isNotEmpty()) rutas.add(normalizarRuta(v))
        }
        if (codigo.isEmpty() || rutas.isEmpty()) return null
        return Vinculo(codigo, if (nombre.isEmpty()) "PC" else nombre, rutas.distinct())
    }

    fun analizarAntiguo(entrada: String): Antiguo? {
        var resto = entrada.trim()
        if (resto.isEmpty()) return null
        var clave: String? = null
        val i = resto.indexOf("#t=")
        if (i >= 0) {
            val k = resto.substring(i + 3).trim()
            clave = if (k.isEmpty()) null else k
            resto = resto.substring(0, i)
        }
        val base = normalizarRuta(resto)
        if (!Regex("^https?://[^/?#\\s]+$", RegexOption.IGNORE_CASE).matches(base)) return null
        return Antiguo(base, clave)
    }

    fun tienePuerto(base: String): Boolean = Regex(":\\d+$").containsMatchIn(base)

    /** «Wi-Fi», «Tailscale» o «Red» según la dirección usada. */
    fun tipoDeRuta(base: String): String {
        val host = base.substringAfter("://").substringBefore(":").substringBefore("/")
        val p = host.split(".")
        if (p.size == 4) {
            val a = p[0].toIntOrNull() ?: -1
            val b = p[1].toIntOrNull() ?: -1
            if (a == 100 && b in 64..127) return "Tailscale"
            if (a == 10 || (a == 192 && b == 168) || (a == 172 && b in 16..31)) return "Wi-Fi"
        }
        if (host.endsWith(".ts.net")) return "Tailscale"
        return "Red"
    }
}

/** Criptografía de la vinculación: es la MISMA cuenta que hace Alfred en el PC (HMAC-SHA256 con el código del QR). */
object Cripto {
    fun hmacHex(clave: String, mensaje: String): String {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(clave.toByteArray(Charsets.UTF_8), "HmacSHA256"))
        val sal = mac.doFinal(mensaje.toByteArray(Charsets.UTF_8))
        val sb = StringBuilder()
        for (b in sal) sb.append("%02x".format(b.toInt() and 0xff))
        return sb.toString()
    }

    /** 16 caracteres hexadecimales al azar. */
    fun nonce(): String {
        val b = ByteArray(8)
        SecureRandom().nextBytes(b)
        val sb = StringBuilder()
        for (x in b) sb.append("%02x".format(x.toInt() and 0xff))
        return sb.toString()
    }
}

/**
 * Habla con Alfred. Conoce VARIAS direcciones del PC (Wi-Fi de casa, Tailscale…): usa la que funcione y, si deja de
 * responder, prueba las demás sola. `idPc` sirve para estar seguros de que la dirección es el mismo PC.
 */
class Cliente(rutas: List<String>, val clave: String, val idPc: String, preferida: String?) {

    class Resp(val codigo: Int, val json: JSONObject?)

    @Volatile
    var rutas: List<String> = rutas

    @Volatile
    var activa: String = if (preferida != null && rutas.contains(preferida)) preferida else rutas.first()

    fun pedir(metodo: String, ruta: String, cuerpo: JSONObject? = null, lecturaMs: Int = 10000): Resp {
        try {
            return peticion(activa, metodo, ruta, cuerpo, 4000, lecturaMs, clave)
        } catch (e: IOException) {
            val otra = reconectar()          // ¿cambió la red? prueba las demás direcciones
            // Una orden (POST) no se repite sola: podría ejecutarse dos veces. Las lecturas (GET) sí.
            if (otra == null || metodo != "GET") throw e
            return peticion(otra, metodo, ruta, cuerpo, 4000, lecturaMs, clave)
        }
    }

    /** Prueba todas las direcciones a la vez y se queda con la primera (por orden de preferencia) que responda. */
    fun reconectar(): String? {
        val lista = rutas
        if (lista.isEmpty()) return null
        val ejecutor = Executors.newFixedThreadPool(lista.size)
        try {
            val tareas = ArrayList<Callable<String?>>()
            for (r in lista) tareas.add(Callable<String?> { if (hayAlfred(r, idPc)) r else null })
            val futuros = ejecutor.invokeAll(tareas, 3, TimeUnit.SECONDS)
            for (f in futuros) {
                if (f.isCancelled) continue
                val r = try {
                    f.get()
                } catch (e: Exception) {
                    null
                }
                if (r != null) {
                    activa = r
                    return r
                }
            }
        } catch (e: InterruptedException) {
            // sondeo cancelado
        } finally {
            ejecutor.shutdownNow()
        }
        return null
    }

    /** Añade una dirección nueva (la más probable primero) y la usa. */
    fun agregarRuta(base: String) {
        rutas = listOf(base) + rutas.filter { it != base }
        activa = base
    }

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
                val json = try {
                    JSONObject(texto)
                } catch (e: Exception) {
                    null
                }
                return Resp(codigo, json)
            } finally {
                c.disconnect()
            }
        }

        /** ¿Hay un Alfred en esa dirección (y es el PC esperado, si se sabe cuál)? /api/ping no pide clave. */
        fun hayAlfred(base: String, idPc: String = ""): Boolean = try {
            val r = peticion(base, "GET", "/api/ping", null, 1500, 1500, null)
            val j = r.json
            r.codigo == 200 && j != null && j.optString("app") == "alfred" &&
                (idPc.isEmpty() || j.optString("id").isEmpty() || j.optString("id") == idPc)
        } catch (e: Exception) {
            false
        }

        /** Datos públicos del Alfred de esa dirección (para saber su identificador). */
        fun ping(base: String): JSONObject? = try {
            peticion(base, "GET", "/api/ping", null, 1500, 1500, null).json
        } catch (e: Exception) {
            null
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

        /** De varias direcciones, las que responden ahora mismo (en paralelo), en el mismo orden. */
        fun alcanzables(rutas: List<String>): List<String> {
            if (rutas.isEmpty()) return emptyList()
            val ejecutor = Executors.newFixedThreadPool(rutas.size)
            val res = ArrayList<String>()
            try {
                val tareas = ArrayList<Callable<Boolean>>()
                for (r in rutas) tareas.add(Callable<Boolean> { hayAlfred(r) })
                val futuros = ejecutor.invokeAll(tareas, 4, TimeUnit.SECONDS)
                for (i in rutas.indices) {
                    val f = futuros[i]
                    val ok = if (f.isCancelled) false else try {
                        f.get()
                    } catch (e: Exception) {
                        false
                    }
                    if (ok) res.add(rutas[i])
                }
            } catch (e: InterruptedException) {
                // cancelado
            } finally {
                ejecutor.shutdownNow()
            }
            return res
        }
    }
}

/** Busca el PC en la Wi-Fi actual cuando su dirección cambió (el router le dio otra IP). */
object Red {
    /** Prefijos de las redes locales del teléfono: «192.168.1.» */
    fun prefijosLocales(): List<String> {
        val res = ArrayList<String>()
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces() ?: return res
            for (ni in Collections.list(interfaces)) {
                if (!ni.isUp || ni.isLoopback) continue
                for (dir in Collections.list(ni.inetAddresses)) {
                    val ip = dir.hostAddress ?: continue
                    if (dir.isSiteLocalAddress && !ip.contains(":")) {
                        val pref = ip.substringBeforeLast(".") + "."
                        if (!res.contains(pref)) res.add(pref)
                    }
                }
            }
        } catch (e: Exception) {
            // sin interfaces legibles: no se busca
        }
        return res
    }

    private fun abierto(host: String, puerto: Int): Boolean = try {
        Socket().use { it.connect(InetSocketAddress(host, puerto), 400) }
        true
    } catch (e: Exception) {
        false
    }

    /** Recorre las 254 direcciones de cada red local mirando el puerto de Alfred; devuelve la del PC con ese id. */
    fun buscarPc(idPc: String): String? {
        for (pref in prefijosLocales()) {
            val ejecutor = Executors.newFixedThreadPool(48)
            try {
                val tareas = ArrayList<Callable<String?>>()
                for (i in 1..254) {
                    val host = pref + i
                    tareas.add(Callable<String?> {
                        if (abierto(host, Enlace.PUERTO)) {
                            val base = "http://$host:${Enlace.PUERTO}"
                            if (Cliente.hayAlfred(base, idPc)) base else null
                        } else null
                    })
                }
                for (f in ejecutor.invokeAll(tareas, 8, TimeUnit.SECONDS)) {
                    if (f.isCancelled) continue
                    val r = try {
                        f.get()
                    } catch (e: Exception) {
                        null
                    }
                    if (r != null) return r
                }
            } catch (e: InterruptedException) {
                return null
            } finally {
                ejecutor.shutdownNow()
            }
        }
        return null
    }
}
