package com.tonada.mobile.core

/** Minimal JSON (no external dependency, identical behaviour on the JVM and on Android). */
object Json {
    fun parse(s: String): Any? {
        val p = Parser(s)
        p.ws()
        val v = p.value()
        p.ws()
        if (p.i != s.length) throw IllegalArgumentException("trailing data at ${p.i}")
        return v
    }

    fun stringify(v: Any?): String {
        val sb = StringBuilder()
        write(sb, v)
        return sb.toString()
    }

    private fun write(sb: StringBuilder, v: Any?) {
        when (v) {
            null -> sb.append("null")
            is Boolean -> sb.append(if (v) "true" else "false")
            is Int, is Long -> sb.append(v.toString())
            is Double -> if (v.isNaN() || v.isInfinite()) sb.append("null") else if (v == Math.rint(v) && Math.abs(v) < 1e15) sb.append(v.toLong()) else sb.append(v.toString())
            is Float -> write(sb, v.toDouble())
            is Number -> sb.append(v.toString())
            is String -> quote(sb, v)
            is Map<*, *> -> {
                sb.append('{')
                var first = true
                for ((k, x) in v) {
                    if (!first) sb.append(',')
                    first = false
                    quote(sb, k.toString())
                    sb.append(':')
                    write(sb, x)
                }
                sb.append('}')
            }
            is Iterable<*> -> {
                sb.append('[')
                var first = true
                for (x in v) {
                    if (!first) sb.append(',')
                    first = false
                    write(sb, x)
                }
                sb.append(']')
            }
            else -> quote(sb, v.toString())
        }
    }

    private fun quote(sb: StringBuilder, s: String) {
        sb.append('"')
        for (c in s) {
            when {
                c == '"' -> sb.append("\\\"")
                c == '\\' -> sb.append("\\\\")
                c == '\n' -> sb.append("\\n")
                c == '\r' -> sb.append("\\r")
                c == '\t' -> sb.append("\\t")
                c < ' ' -> sb.append(String.format("\\u%04x", c.code))
                else -> sb.append(c)
            }
        }
        sb.append('"')
    }

    private class Parser(val s: String) {
        var i = 0

        fun err(msg: String = "unexpected input") = IllegalArgumentException("$msg at $i")

        fun ws() {
            while (i < s.length && (s[i] == ' ' || s[i] == '\n' || s[i] == '\r' || s[i] == '\t')) i++
        }

        fun value(): Any? {
            ws()
            if (i >= s.length) throw err("unexpected end")
            val c = s[i]
            return when {
                c == '{' -> obj()
                c == '[' -> arr()
                c == '"' -> str()
                c == 't' -> lit("true", true)
                c == 'f' -> lit("false", false)
                c == 'n' -> lit("null", null)
                c == '-' || (c in '0'..'9') -> num()
                else -> throw err()
            }
        }

        fun lit(word: String, v: Any?): Any? {
            if (!s.startsWith(word, i)) throw err()
            i += word.length
            return v
        }

        fun num(): Double {
            val st = i
            while (i < s.length && (s[i] in '0'..'9' || s[i] == '-' || s[i] == '+' || s[i] == '.' || s[i] == 'e' || s[i] == 'E')) i++
            return s.substring(st, i).toDoubleOrNull() ?: throw err("bad number")
        }

        fun str(): String {
            i++ // opening quote
            val sb = StringBuilder()
            while (true) {
                if (i >= s.length) throw err("unterminated string")
                val c = s[i++]
                if (c == '"') return sb.toString()
                if (c != '\\') {
                    sb.append(c)
                    continue
                }
                if (i >= s.length) throw err()
                when (val e = s[i++]) {
                    '"' -> sb.append('"')
                    '\\' -> sb.append('\\')
                    '/' -> sb.append('/')
                    'b' -> sb.append('\b')
                    'f' -> sb.append('\u000c')
                    'n' -> sb.append('\n')
                    'r' -> sb.append('\r')
                    't' -> sb.append('\t')
                    'u' -> {
                        if (i + 4 > s.length) throw err("bad unicode escape")
                        sb.append(s.substring(i, i + 4).toInt(16).toChar())
                        i += 4
                    }
                    else -> throw err("bad escape \\$e")
                }
            }
        }

        fun arr(): List<Any?> {
            i++
            val out = ArrayList<Any?>()
            ws()
            if (i < s.length && s[i] == ']') {
                i++
                return out
            }
            while (true) {
                out.add(value())
                ws()
                if (i >= s.length) throw err()
                val c = s[i++]
                if (c == ']') return out
                if (c != ',') throw err("expected , or ]")
            }
        }

        fun obj(): Map<String, Any?> {
            i++
            val out = LinkedHashMap<String, Any?>()
            ws()
            if (i < s.length && s[i] == '}') {
                i++
                return out
            }
            while (true) {
                ws()
                if (i >= s.length || s[i] != '"') throw err("expected key")
                val k = str()
                ws()
                if (i >= s.length || s[i] != ':') throw err("expected :")
                i++
                out[k] = value()
                ws()
                if (i >= s.length) throw err()
                val c = s[i++]
                if (c == '}') return out
                if (c != ',') throw err("expected , or }")
            }
        }
    }
}
