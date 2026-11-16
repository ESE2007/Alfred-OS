package com.alfred.remoto

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/** Guarda la dirección del PC y la clave. La clave se cifra con una llave del Android Keystore (no sale del teléfono). */
class Almacen(ctx: Context) {
    private val p = ctx.getSharedPreferences("alfred_remoto", Context.MODE_PRIVATE)

    var direccion: String
        get() = p.getString("dir", "") ?: ""
        set(v) { p.edit().putString("dir", v).apply() }

    var clave: String
        get() = descifrar(p.getString("clave", "") ?: "")
        set(v) { p.edit().putString("clave", cifrar(v)).apply() }

    fun borrar() { p.edit().clear().apply() }

    private fun llave(): SecretKey {
        val ks = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        (ks.getKey(ALIAS, null) as? SecretKey)?.let { return it }
        val gen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        gen.init(
            KeyGenParameterSpec.Builder(ALIAS, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256)
                .build()
        )
        return gen.generateKey()
    }

    private fun cifrar(texto: String): String {
        if (texto.isEmpty()) return ""
        return try {
            val c = Cipher.getInstance("AES/GCM/NoPadding")
            c.init(Cipher.ENCRYPT_MODE, llave())
            val datos = c.iv + c.doFinal(texto.toByteArray(Charsets.UTF_8))
            Base64.encodeToString(datos, Base64.NO_WRAP)
        } catch (e: Exception) {
            ""
        }
    }

    private fun descifrar(b64: String): String {
        if (b64.isEmpty()) return ""
        return try {
            val datos = Base64.decode(b64, Base64.NO_WRAP)
            val c = Cipher.getInstance("AES/GCM/NoPadding")
            c.init(Cipher.DECRYPT_MODE, llave(), GCMParameterSpec(128, datos, 0, 12))
            String(c.doFinal(datos, 12, datos.size - 12), Charsets.UTF_8)
        } catch (e: Exception) {
            ""
        }
    }

    companion object {
        private const val ALIAS = "alfred_remoto_clave"
    }
}
