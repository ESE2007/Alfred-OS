package com.tonada.mobile.core

import java.security.SecureRandom
import java.util.Base64
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

/** AES-256-GCM boxes, see docs/PROTOCOL.md section 3. */
object Crypto {
    private val rnd = SecureRandom()

    fun b64uEncode(b: ByteArray): String = Base64.getUrlEncoder().withoutPadding().encodeToString(b)
    fun b64uDecode(s: String): ByteArray = Base64.getUrlDecoder().decode(s)

    fun randomBytes(n: Int): ByteArray = ByteArray(n).also { rnd.nextBytes(it) }
    fun randomHex(n: Int): String = randomBytes(n).joinToString("") { String.format("%02x", it.toInt() and 0xff) }

    class Box(key: ByteArray) {
        private val k = SecretKeySpec(key, "AES")

        init {
            require(key.size == 32) { "key must be 32 bytes" }
        }

        /** IV(12) || ciphertext || tag(16), AAD = topic. */
        fun seal(json: String, topic: String): ByteArray {
            val iv = randomBytes(12)
            val c = Cipher.getInstance("AES/GCM/NoPadding")
            c.init(Cipher.ENCRYPT_MODE, k, GCMParameterSpec(128, iv))
            c.updateAAD(topic.toByteArray(Charsets.UTF_8))
            return iv + c.doFinal(json.toByteArray(Charsets.UTF_8))
        }

        /** Returns the JSON text or null if the message is not authentic. */
        fun open(data: ByteArray, topic: String): String? {
            if (data.size < 12 + 16) return null
            return try {
                val c = Cipher.getInstance("AES/GCM/NoPadding")
                c.init(Cipher.DECRYPT_MODE, k, GCMParameterSpec(128, data.copyOfRange(0, 12)))
                c.updateAAD(topic.toByteArray(Charsets.UTF_8))
                String(c.doFinal(data, 12, data.size - 12), Charsets.UTF_8)
            } catch (e: Exception) {
                null
            }
        }
    }
}
