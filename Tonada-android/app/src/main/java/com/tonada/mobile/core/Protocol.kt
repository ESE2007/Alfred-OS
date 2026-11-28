package com.tonada.mobile.core

import java.net.URLDecoder
import java.text.Normalizer

/** A track as exchanged with the PC (docs/PROTOCOL.md "Ent"). */
data class Ent(val k: String, val a: String, val t: String, val ar: String, val al: String, val d: Int) {
    fun toMap(): Map<String, Any?> = linkedMapOf("k" to k, "a" to a, "t" to t, "ar" to ar, "al" to al, "d" to d)
    /** Only what the PC needs to find the track. */
    fun toRef(): Map<String, Any?> = linkedMapOf("k" to k, "a" to a, "d" to d)
}

data class RemoteState(
    val name: String, val off: Boolean, val ts: Long, val playing: Boolean, val pos: Double, val dur: Double,
    val vol: Double, val muted: Boolean, val shuffle: Boolean, val repeat: String, val speed: Double, val fav: Boolean,
    val cur: Ent?, val qi: Int, val qn: Int, val queueName: String, val rxAt: Long,
) {
    /** Playback position now, interpolated from the last state message. */
    fun livePos(now: Long): Double {
        if (!playing || off) return pos
        val p = pos + (now - rxAt) / 1000.0
        return if (dur > 0) minOf(p, dur) else p
    }
}

data class RemoteQueue(val off: Int, val total: Int, val cur: Int, val name: String, val items: List<Ent>)

object Identity {
    /** NFD, drop combining marks, lowercase, keep only letters and digits (same as the PC). */
    fun norm(s: String?): String {
        if (s == null) return ""
        val d = Normalizer.normalize(s, Normalizer.Form.NFD)
        val sb = StringBuilder()
        d.codePoints().forEach { cp ->
            when (Character.getType(cp).toByte()) {
                Character.NON_SPACING_MARK, Character.COMBINING_SPACING_MARK, Character.ENCLOSING_MARK -> {}
                Character.UPPERCASE_LETTER, Character.LOWERCASE_LETTER, Character.TITLECASE_LETTER, Character.MODIFIER_LETTER,
                Character.OTHER_LETTER, Character.DECIMAL_DIGIT_NUMBER, Character.LETTER_NUMBER, Character.OTHER_NUMBER -> sb.appendCodePoint(cp)
                else -> {}
            }
        }
        return sb.toString().lowercase(java.util.Locale.ROOT)
    }

    fun keyF(fileName: String, size: Long): String = "f:" + fileName.lowercase(java.util.Locale.ROOT) + "|" + size

    /** Artist placeholders ("<unknown>") count as empty, like on the PC. */
    fun keyT(artist: String?, title: String?): String {
        val a = artist ?: ""
        val artistN = if (a == "<unknown>" || a.equals("unknown", true)) "" else norm(a)
        return "t:" + artistN + "|" + norm(title)
    }
}

/** What the QR code of the PC carries. */
data class PairInfo(val room: String, val key: String, val broker: String, val name: String) {
    companion object {
        fun parse(text: String): PairInfo? {
            val s = text.trim()
            if (!s.startsWith("tonada://pair?")) return null
            val q = HashMap<String, String>()
            for (part in s.substring("tonada://pair?".length).split('&')) {
                val i = part.indexOf('=')
                if (i > 0) q[part.substring(0, i)] = try { URLDecoder.decode(part.substring(i + 1), "UTF-8") } catch (e: Exception) { return null }
            }
            if (q["v"] != "1") return null
            val room = q["r"] ?: return null
            val key = q["k"] ?: return null
            val broker = q["b"] ?: return null
            if (!Regex("[0-9a-f]{32}").matches(room)) return null
            if (!Regex("wss?://.+").matches(broker)) return null
            try {
                if (Crypto.b64uDecode(key).size != 32) return null
            } catch (e: Exception) {
                return null
            }
            return PairInfo(room, key, broker, q["n"] ?: "Tonada PC")
        }
    }
}

internal fun Map<*, *>.str(k: String): String = (this[k] as? String) ?: ""
internal fun Map<*, *>.num(k: String): Double = (this[k] as? Number)?.toDouble() ?: 0.0
internal fun Map<*, *>.bool(k: String): Boolean = (this[k] as? Boolean) ?: false

internal fun parseEnt(m: Any?): Ent? {
    val x = m as? Map<*, *> ?: return null
    return Ent(x.str("k"), x.str("a"), x.str("t"), x.str("ar"), x.str("al"), x.num("d").toInt())
}

internal fun parseState(m: Map<*, *>, now: Long) = RemoteState(
    name = m.str("name"), off = m.bool("off") || (m["off"] as? Number)?.toInt() == 1, ts = m.num("ts").toLong(), playing = m.bool("playing"),
    pos = m.num("pos"), dur = m.num("dur"), vol = m.num("vol"), muted = m.bool("muted"), shuffle = m.bool("shuffle"),
    repeat = m.str("repeat").ifEmpty { "off" }, speed = m.num("speed").let { if (it == 0.0) 1.0 else it }, fav = m.bool("fav"),
    cur = parseEnt(m["cur"]), qi = (m["qi"] as? Number)?.toInt() ?: -1, qn = m.num("qn").toInt(), queueName = m.str("q"), rxAt = now,
)

internal fun parseQueue(m: Map<*, *>): RemoteQueue = RemoteQueue(
    off = m.num("off").toInt(), total = m.num("total").toInt(), cur = (m["cur"] as? Number)?.toInt() ?: -1, name = m.str("name"),
    items = (m["items"] as? List<*>)?.mapNotNull { parseEnt(it) } ?: emptyList(),
)
