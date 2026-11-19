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

/**
 * Guarda el PC vinculado: sus direcciones (Wi-Fi, Tailscale…), su identificador y la clave de ESTE teléfono.
 * La clave se cifra con una llave del Android Keystore (no sale del teléfono).
 * Los nombres "dir" y "clave" son los de la versión 1.0: quien actualiza conserva su vinculación.
 */
class Almacen(ctx: Context) {
    private val p = ctx.getSharedPreferences("alfred_remoto", Context.MODE_PRIVATE)

    /** Dirección por la que se conectó la última vez. */
    var direccion: String
        get() = p.getString("dir", "") ?: ""
        set(v) { p.edit().putString("dir", v).apply() }

    /** Todas las direcciones conocidas del PC, en orden de preferencia. */
    var rutas: List<String>
        get() {
            val guardadas = (p.getString("rutas", "") ?: "").split("\n").map { it.trim() }.filter { it.isNotEmpty() }
            if (guardadas.isNotEmpty()) return guardadas
            return if (direccion.isNotEmpty()) listOf(direccion) else emptyList()   // viene de la versión 1.0
        }
        set(v) { p.edit().putString("rutas", v.distinct().joinToString("\n")).apply() }

    /** Nombre del PC (para mostrarlo). */
    var nombrePc: String
        get() = p.getString("pc", "") ?: ""
        set(v) { p.edit().putString("pc", v).apply() }

    /** Identificador del PC: sirve para reconocerlo si cambia de IP. */
    var idPc: String
        get() = p.getString("idpc", "") ?: ""
        set(v) { p.edit().putString("idpc", v).apply() }

    var clave: String
        get() = descifrar(p.getString("clave", "") ?: "")
        set(v) { p.edit().putString("clave", cifrar(v)).apply() }

    val vinculado: Boolean
        get() = clave.isNotEmpty() && rutas.isNotEmpty()

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
