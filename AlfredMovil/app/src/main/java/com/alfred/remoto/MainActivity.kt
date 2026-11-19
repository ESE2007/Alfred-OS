package com.alfred.remoto

import android.app.Activity
import android.app.AlertDialog
import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.speech.RecognizerIntent
import android.text.Editable
import android.text.InputType
import android.text.TextWatcher
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.EditorInfo
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.SeekBar
import android.widget.TextView
import android.widget.Toast
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.codescanner.GmsBarcodeScannerOptions
import com.google.mlkit.vision.codescanner.GmsBarcodeScanning
import org.json.JSONObject
import java.util.Locale

class MainActivity : Activity() {

    /** Un comando de Alfred tal como lo describe el PC, con su nivel de permiso para el móvil. */
    class Cmd(val id: String, val ejemplo: String, val desc: String, val categoria: String, val remoto: String)

    private lateinit var almacen: Almacen
    private var cliente: Cliente? = null

    // pantalla principal
    private lateinit var estado: TextView
    private lateinit var registro: LinearLayout
    private lateinit var scroll: ScrollView
    private lateinit var entrada: EditText
    private lateinit var listaComandos: LinearLayout
    private lateinit var buscador: EditText
    private var panelAvanzado: LinearLayout? = null
    private var paneles: Array<View> = emptyArray()
    private var navItems: Array<TextView> = emptyArray()
    // pantalla de bienvenida
    private var msgBienvenida: TextView? = null

    private var catalogo: List<Cmd> = emptyList()
    private var propios: List<Pair<String, String>> = emptyList()      // (frase, nivel)

    @Volatile
    private var avanzado = false

    @Volatile
    private var sondeoId = 0

    @Volatile
    private var ultimaBusqueda = 0L

    private var avisoClave = false

    // ── colores ──────────────────────────────────────────────────────────────
    private val FONDO = Color.parseColor("#0B1220")
    private val PANEL = Color.parseColor("#111A2E")
    private val BORDE = Color.parseColor("#1E3A5F")
    private val CIAN = Color.parseColor("#22D3EE")
    private val VERDE = Color.parseColor("#4ADE80")
    private val AMBAR = Color.parseColor("#FBBF24")
    private val ROJO = Color.parseColor("#F87171")
    private val GRIS = Color.parseColor("#94A3B8")
    private val TEXTO = Color.parseColor("#E2E8F0")

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()

    // ── ciclo de vida ────────────────────────────────────────────────────────
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        almacen = Almacen(this)
        window.statusBarColor = FONDO
        window.navigationBarColor = FONDO
        cargarCliente()
        render()
        procesarIntent(intent)
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        setIntent(intent)
        procesarIntent(intent)
    }

    override fun onStart() {
        super.onStart()
        if (cliente != null) iniciarSondeo()
    }

    override fun onStop() {
        sondeoId++            // la app solo sigue al PC mientras está a la vista
        super.onStop()
    }

    private fun procesarIntent(i: Intent?) {
        val d = i?.dataString ?: return
        if (Enlace.esVinculo(d)) vincular(d)
    }

    private fun cargarCliente() {
        val rutas = almacen.rutas
        val k = almacen.clave
        cliente = if (rutas.isNotEmpty() && k.isNotEmpty()) {
            Cliente(rutas, k, almacen.idPc, almacen.direccion.ifEmpty { null })
        } else null
    }

    /** Dibuja la bienvenida (sin PC vinculado) o la pantalla principal. */
    private fun render() {
        if (cliente == null) {
            sondeoId++
            setContentView(pantallaBienvenida())
        } else {
            msgBienvenida = null
            setContentView(pantallaPrincipal())
            avisoClave = false
            cargarCatalogo()
            iniciarSondeo()
        }
    }

    // ── piezas de interfaz ───────────────────────────────────────────────────
    private fun chip(texto: String, accion: () -> Unit): TextView {
        val t = TextView(this)
        t.text = texto
        t.setTextColor(TEXTO)
        t.textSize = 14f
        t.gravity = Gravity.CENTER
        t.setPadding(dp(12), dp(10), dp(12), dp(10))
        val fondo = GradientDrawable()
        fondo.cornerRadius = dp(18).toFloat()
        fondo.setColor(PANEL)
        fondo.setStroke(dp(1), BORDE)
        t.background = fondo
        t.setOnClickListener { accion() }
        return t
    }

    private fun botonPrincipal(texto: String, accion: () -> Unit): TextView {
        val t = chip(texto, accion)
        t.textSize = 17f
        t.setTextColor(Color.parseColor("#04121A"))
        t.setTypeface(t.typeface, Typeface.BOLD)
        t.setPadding(dp(16), dp(16), dp(16), dp(16))
        val fondo = GradientDrawable()
        fondo.cornerRadius = dp(26).toFloat()
        fondo.setColor(CIAN)
        t.background = fondo
        return t
    }

    private fun margenes(izq: Int = 0, der: Int = 6): LinearLayout.LayoutParams {
        val p = LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        p.setMargins(dp(izq), 0, dp(der), 0)
        return p
    }

    private fun pesos(): LinearLayout.LayoutParams {
        val p = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
        p.setMargins(dp(3), dp(3), dp(3), dp(3))
        return p
    }

    private fun texto(t: String, color: Int, tam: Float): TextView {
        val v = TextView(this)
        v.text = t
        v.setTextColor(color)
        v.textSize = tam
        return v
    }

    private fun seccion(titulo: String): TextView {
        val v = texto(titulo.uppercase(Locale.getDefault()), CIAN, 12f)
        v.letterSpacing = 0.12f
        v.setPadding(dp(2), dp(14), 0, dp(4))
        return v
    }

    /** Una fila de botones del mismo ancho; cada uno manda una frase al PC. */
    private fun botones(vararg pares: Pair<String, String>): LinearLayout {
        val f = LinearLayout(this)
        f.orientation = LinearLayout.HORIZONTAL
        for ((etiqueta, frase) in pares) f.addView(chip(etiqueta) { enviar(frase) }, pesos())
        return f
    }

    private fun deslizador(titulo: String, comando: String, inicial: Int): View {
        val caja = LinearLayout(this)
        caja.orientation = LinearLayout.VERTICAL
        val t = texto("$titulo: $inicial %", TEXTO, 13f)
        t.setPadding(dp(2), dp(6), 0, 0)
        val s = SeekBar(this)
        s.max = 100
        s.progress = inicial
        s.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(sb: SeekBar?, p: Int, deUsuario: Boolean) {
                t.text = "$titulo: $p %"
            }

            override fun onStartTrackingTouch(sb: SeekBar?) {}

            override fun onStopTrackingTouch(sb: SeekBar?) {
                enviar("$comando al ${s.progress}")
            }
        })
        caja.addView(t)
        caja.addView(s)
        return caja
    }

    private fun pintarEstado(texto: String, color: Int) {
        runOnUiThread {
            if (!::estado.isInitialized) return@runOnUiThread
            estado.text = "● $texto"
            estado.setTextColor(color)
        }
    }

    private fun avisar(msg: String) {
        runOnUiThread { Toast.makeText(this, msg, Toast.LENGTH_LONG).show() }
    }

    private fun dialogo(): AlertDialog.Builder = AlertDialog.Builder(this, android.R.style.Theme_Material_Dialog_Alert)

    // ── bienvenida: vincular con un QR ───────────────────────────────────────
    private fun pantallaBienvenida(): View {
        val raiz = LinearLayout(this)
        raiz.orientation = LinearLayout.VERTICAL
        raiz.setBackgroundColor(FONDO)
        raiz.setPadding(dp(24), dp(40), dp(24), dp(24))
        raiz.gravity = Gravity.CENTER_HORIZONTAL

        val titulo = texto("ALFRED", CIAN, 34f)
        titulo.typeface = Typeface.create("sans-serif-medium", Typeface.BOLD)
        titulo.letterSpacing = 0.25f
        raiz.addView(titulo)
        raiz.addView(texto("Controla tu PC desde el móvil", GRIS, 15f))

        val pasos = texto(
            "1.  En el PC abre Alfred:  ☰ Menú → Remoto → «Vincular teléfono».\n\n" +
                "2.  Aquí toca «Escanear código QR» y apunta a la pantalla del PC.\n\n" +
                "Listo: no hay que escribir IPs ni claves. Funciona en tu Wi-Fi y, con Tailscale, también fuera de casa.",
            TEXTO, 15f
        )
        val fondo = GradientDrawable()
        fondo.cornerRadius = dp(14).toFloat()
        fondo.setColor(PANEL)
        pasos.background = fondo
        pasos.setPadding(dp(18), dp(18), dp(18), dp(18))
        val lpPasos = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        lpPasos.setMargins(0, dp(30), 0, dp(24))
        raiz.addView(pasos, lpPasos)

        val lpBoton = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        raiz.addView(botonPrincipal("📷  Escanear código QR") { escanear() }, lpBoton)

        val lpSec = LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        lpSec.setMargins(0, dp(14), 0, 0)
        raiz.addView(chip("Pegar enlace") { pegarEnlace() }, lpSec)

        val msg = texto("", GRIS, 14f)
        msg.gravity = Gravity.CENTER
        msg.setPadding(0, dp(20), 0, 0)
        raiz.addView(msg)
        msgBienvenida = msg
        return raiz
    }

    private fun info(texto: String, color: Int) {
        runOnUiThread {
            val m = msgBienvenida
            if (m != null) {
                m.text = texto
                m.setTextColor(color)
            } else Toast.makeText(this, texto, Toast.LENGTH_LONG).show()
        }
    }

    /** Abre el lector de QR de Google Play Services (no pide permiso de cámara). */
    private fun escanear() {
        try {
            val opciones = GmsBarcodeScannerOptions.Builder().setBarcodeFormats(Barcode.FORMAT_QR_CODE).build()
            GmsBarcodeScanning.getClient(this, opciones).startScan()
                .addOnSuccessListener { codigo ->
                    val t = codigo.rawValue
                    if (t.isNullOrBlank()) info("No pude leer ese código. Inténtalo de nuevo.", AMBAR) else vincular(t)
                }
                .addOnFailureListener {
                    info("No pude abrir el lector de QR en este teléfono. Usa «Pegar enlace» (en el PC: «Copiar enlace»).", AMBAR)
                }
        } catch (e: Exception) {
            info("No pude abrir el lector de QR en este teléfono. Usa «Pegar enlace» (en el PC: «Copiar enlace»).", AMBAR)
        }
    }

    private fun pegarEnlace() {
        val caja = LinearLayout(this)
        caja.orientation = LinearLayout.VERTICAL
        caja.setPadding(dp(20), dp(10), dp(20), 0)
        val ayuda = texto(
            "Pega el enlace que copiaste en el PC («Copiar enlace» en la ventana de vinculación). " +
                "También sirve el enlace web de versiones anteriores (http://…/#t=clave) o la IP del PC con su clave.", TEXTO, 13f
        )
        caja.addView(ayuda)
        val enlace = EditText(this)
        enlace.hint = "alfred://…  o  http://192.168.1.20:47654/#t=…"
        enlace.isSingleLine = true
        enlace.inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_URI
        caja.addView(enlace)
        val clave = EditText(this)
        clave.hint = "Clave (solo si el enlace no la incluye)"
        clave.isSingleLine = true
        clave.inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
        caja.addView(clave)
        dialogo().setTitle("Pegar enlace").setView(caja)
            .setPositiveButton("Conectar") { _, _ ->
                val t = enlace.text.toString().trim()
                if (Enlace.esVinculo(t)) vincular(t) else vincularAntiguo(t, clave.text.toString().trim())
            }
            .setNegativeButton("Cancelar", null)
            .show()
    }

    private fun nombreTelefono(): String {
        val limpio = Regex("[^A-Za-z0-9 ._()-]").replace(Build.MODEL ?: "", "").trim().take(40)
        return if (limpio.isEmpty()) "Android" else limpio
    }

    private fun sinRespuesta() {
        info("No encuentro tu PC.", ROJO)
        dialogo().setTitle("No encuentro tu PC")
            .setMessage(
                "• En casa: comprueba que el PC esté encendido, con Alfred abierto, y que el teléfono esté en la misma Wi-Fi.\n\n" +
                    "• Fuera de casa: necesitas Tailscale (gratis) en el teléfono y en el PC, con la misma cuenta.\n\n" +
                    "Después vuelve a escanear: en el PC pulsa «Código nuevo» si caducó."
            )
            .setPositiveButton("Abrir Tailscale") { _, _ -> abrirTailscale() }
            .setNegativeButton("Cerrar", null)
            .show()
    }

    private fun abrirTailscale() {
        val i = packageManager.getLaunchIntentForPackage("com.tailscale.ipn")
        try {
            if (i != null) startActivity(i)
            else startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=com.tailscale.ipn")))
        } catch (e: Exception) {
            try {
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://tailscale.com/download")))
            } catch (e2: Exception) {
                avisar("Instala Tailscale desde tu tienda de aplicaciones.")
            }
        }
    }

    private fun dialogoFuera() {
        dialogo().setTitle("Usar Alfred fuera de casa")
            .setMessage(
                "Alfred se conecta con tu PC por la red que haya: tu Wi-Fi de casa o Tailscale.\n\n" +
                    "Para usarlo fuera de casa (datos móviles, otra Wi-Fi):\n" +
                    "1. Instala Tailscale (gratis) en el PC y en este teléfono.\n" +
                    "2. Inicia sesión con la MISMA cuenta en los dos.\n" +
                    "3. En el PC, en la ventana de vincular, pulsa «Código nuevo» y escanéalo otra vez.\n\n" +
                    "La app prueba sola todas las direcciones y se queda con la que funcione."
            )
            .setPositiveButton("Abrir Tailscale") { _, _ -> abrirTailscale() }
            .setNegativeButton("Cerrar", null)
            .show()
    }

    /** Vincula con el QR/enlace de Alfred 3.5: sin clave que escribir; la clave de este teléfono se deriva del código. */
    private fun vincular(texto: String) {
        val v = Enlace.analizarVinculo(texto)
        if (v == null) {
            info("Ese código no es de Alfred. En el PC: ☰ Menú → Remoto → «Vincular teléfono».", ROJO)
            return
        }
        info("Buscando «${v.nombrePc}»…", GRIS)
        Thread {
            val alcanzables = Cliente.alcanzables(v.rutas)
            if (alcanzables.isEmpty()) {
                runOnUiThread { sinRespuesta() }
                return@Thread
            }
            val base = alcanzables[0]
            val nombre = nombreTelefono()
            val nonce = Cripto.nonce()
            val cuerpo = JSONObject()
                .put("nombre", nombre)
                .put("nonce", nonce)
                .put("prueba", Cripto.hmacHex(v.codigo, "prueba|$nonce|$nombre"))
            info("Vinculando…", GRIS)
            val r = try {
                Cliente.peticion(base, "POST", "/api/vincular", cuerpo, 5000, 8000, null)
            } catch (e: Exception) {
                info("No pude hablar con el PC: " + (e.message ?: e.javaClass.simpleName), ROJO)
                return@Thread
            }
            val j = r.json
            if (r.codigo != 200 || j == null || !j.optBoolean("ok")) {
                val motivo = when (r.codigo) {
                    429 -> "Demasiados intentos fallidos; espera unos minutos."
                    else -> j?.optString("error").orEmpty().ifEmpty { "código ${r.codigo}" }
                }
                info("El PC no aceptó el código: $motivo", ROJO)
                return@Thread
            }
            val token = Cripto.hmacHex(v.codigo, "token|$nonce|$nombre")      // la clave NUNCA viajó por la red
            val idPc = j.optString("id_pc")
            val prueba = try {
                Cliente(listOf(base), token, idPc, base).pedir("GET", "/api/estado", null, 8000).codigo
            } catch (e: Exception) {
                -1
            }
            if (prueba != 200) {
                info("Vinculado, pero no pude comprobar la conexión (código $prueba). Inténtalo otra vez.", ROJO)
                return@Thread
            }
            val todas = ArrayList<String>()
            todas.add(base)
            val deLaRespuesta = j.optJSONArray("rutas")
            if (deLaRespuesta != null) for (i in 0 until deLaRespuesta.length()) todas.add(Enlace.normalizarRuta(deLaRespuesta.getString(i)))
            todas.addAll(v.rutas)
            almacen.rutas = todas
            almacen.direccion = base
            almacen.clave = token
            almacen.idPc = idPc
            almacen.nombrePc = j.optString("pc", v.nombrePc).ifEmpty { v.nombrePc }
            runOnUiThread {
                cargarCliente()
                render()
                Toast.makeText(this, "✓ Vinculado con ${almacen.nombrePc}", Toast.LENGTH_LONG).show()
            }
        }.start()
    }

    /** Enlaces de la versión 1.0 (http://IP:PUERTO/#t=CLAVE): siguen valiendo con la clave maestra del PC. */
    private fun vincularAntiguo(texto: String, claveExtra: String) {
        val d = Enlace.analizarAntiguo(texto)
        if (d == null) {
            info("Esa dirección no es válida.", ROJO)
            return
        }
        val clave = d.clave ?: claveExtra
        if (clave.isEmpty()) {
            info("Falta la clave. Mejor vincula con el código QR del PC.", ROJO)
            return
        }
        info("Buscando a Alfred…", GRIS)
        Thread {
            val base = Cliente.descubrir(d.base)
            if (base == null) {
                runOnUiThread { sinRespuesta() }
                return@Thread
            }
            val codigo = try {
                Cliente(listOf(base), clave, "", base).pedir("GET", "/api/estado", null, 8000).codigo
            } catch (e: Exception) {
                -1
            }
            when (codigo) {
                200 -> {
                    almacen.rutas = listOf(base)
                    almacen.direccion = base
                    almacen.clave = clave
                    almacen.idPc = Cliente.ping(base)?.optString("id").orEmpty()
                    almacen.nombrePc = "PC"
                    runOnUiThread { cargarCliente(); render() }
                }
                401 -> info("Encontré a Alfred, pero la clave es incorrecta.", ROJO)
                429 -> info("Demasiados intentos fallidos. Espera unos minutos.", AMBAR)
                else -> info("No pude comprobar la clave (código $codigo).", ROJO)
            }
        }.start()
    }

    // ── pantalla principal: Control · Actividad · Comandos ───────────────────
    private fun pantallaPrincipal(): View {
        val raiz = LinearLayout(this)
        raiz.orientation = LinearLayout.VERTICAL
        raiz.setBackgroundColor(FONDO)
        raiz.setPadding(dp(14), dp(14), dp(14), dp(8))

        val cab = LinearLayout(this)
        cab.orientation = LinearLayout.HORIZONTAL
        cab.gravity = Gravity.CENTER_VERTICAL
        val titulo = texto("ALFRED", CIAN, 22f)
        titulo.typeface = Typeface.create("sans-serif-medium", Typeface.BOLD)
        titulo.letterSpacing = 0.25f
        cab.addView(titulo, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        cab.addView(chip("⚙") { mostrarAjustes() }, margenes(0, 0))
        raiz.addView(cab)

        estado = texto("● Conectando…", GRIS, 13f)
        estado.setPadding(0, dp(4), 0, dp(8))
        raiz.addView(estado)

        val contenedor = LinearLayout(this)
        contenedor.orientation = LinearLayout.VERTICAL
        paneles = arrayOf(panelControl(), panelActividad(), panelComandos())
        for (p in paneles) contenedor.addView(p, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        raiz.addView(contenedor, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))

        val nav = LinearLayout(this)
        nav.orientation = LinearLayout.HORIZONTAL
        nav.setPadding(0, dp(6), 0, 0)
        val nombres = arrayOf("🎛  Control", "💬  Actividad", "📖  Comandos")
        val items = ArrayList<TextView>()
        for (i in nombres.indices) {
            val t = texto(nombres[i], GRIS, 14f)
            t.gravity = Gravity.CENTER
            t.setPadding(0, dp(10), 0, dp(10))
            t.setOnClickListener { mostrarPanel(i) }
            nav.addView(t, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
            items.add(t)
        }
        navItems = items.toTypedArray()
        raiz.addView(nav)
        mostrarPanel(0)
        return raiz
    }

    private fun mostrarPanel(n: Int) {
        for (i in paneles.indices) paneles[i].visibility = if (i == n) View.VISIBLE else View.GONE
        for (i in navItems.indices) {
            navItems[i].setTextColor(if (i == n) CIAN else GRIS)
            navItems[i].setTypeface(null, if (i == n) Typeface.BOLD else Typeface.NORMAL)
        }
        if (n == 2 && catalogo.isEmpty()) cargarCatalogo()
    }

    private fun panelControl(): View {
        val sv = ScrollView(this)
        val c = LinearLayout(this)
        c.orientation = LinearLayout.VERTICAL
        c.setPadding(0, 0, 0, dp(12))

        c.addView(seccion("Música"))
        c.addView(botones("⏮" to "canción anterior", "⏸" to "pausa", "▶" to "dale play", "⏭" to "siguiente canción"))
        c.addView(botones("🔉" to "baja el volumen", "🔇" to "silencio", "🔊" to "sube el volumen"))
        c.addView(botones("🎵 ¿Qué suena?" to "qué suena"))
        c.addView(deslizador("🔊 Volumen", "volumen", 50))
        c.addView(deslizador("☀ Brillo", "brillo", 50))

        c.addView(seccion("Mi PC"))
        c.addView(botones("🔒 Bloquear" to "bloquea la pantalla", "📷 Captura" to "captura de pantalla"))
        c.addView(botones("🖥 Descanso" to "descanso", "📊 Estado" to "estado del sistema"))
        c.addView(botones("🌙 Oscuro" to "modo oscuro", "☀ Claro" to "modo claro"))
        c.addView(botones("Pantalla off" to "apaga la pantalla", "Pantalla on" to "enciende la pantalla"))
        c.addView(botones("😴 Suspender" to "suspende el equipo"))

        c.addView(seccion("Abrir"))
        c.addView(botones("📁 Explorador" to "abre el explorador", "🧮 Calculadora" to "calculadora"))
        c.addView(botones("📝 Bloc" to "bloc de notas", "📥 Descargas" to "abre descargas"))
        c.addView(botones("▶ YouTube" to "abre youtube", "📋 Tareas" to "abre el administrador de tareas"))

        c.addView(seccion("Ventanas y páginas"))
        c.addView(botones("Cambiar ventana" to "cambia de ventana", "Vista general" to "vista de tareas"))
        c.addView(botones("Minimizar" to "minimiza esta ventana", "Maximizar" to "maximiza esta ventana"))
        c.addView(botones("⬆" to "flecha arriba", "⬇" to "flecha abajo", "⬅" to "flecha izquierda", "➡" to "flecha derecha"))
        c.addView(botones("Subir página" to "sube la página", "Bajar página" to "baja la página"))
        c.addView(botones("Pantalla completa" to "pantalla completa", "Espacio" to "espacio", "Recargar" to "recarga"))

        c.addView(seccion("Temporizador"))
        c.addView(botones("⏱ 5 min" to "temporizador de 5 minutos", "10 min" to "temporizador de 10 minutos", "30 min" to "temporizador de 30 minutos"))
        c.addView(botones("Cancelar temporizador" to "cancela el temporizador"))

        // teclado y ratón: solo se muestra si el PC lo tiene activado (☰ Menú → Remoto → Avanzado)
        val av = LinearLayout(this)
        av.orientation = LinearLayout.VERTICAL
        av.addView(seccion("Teclado y ratón (avanzado)"))
        av.addView(botones("⏎ Enter" to "enter", "Esc" to "escape", "Tab" to "tabulador", "⌫" to "retroceso"))
        av.addView(botones("Clic" to "clic", "Doble clic" to "doble clic", "Clic derecho" to "clic derecho"))
        av.addView(botones("Copiar" to "copia", "Pegar" to "pega", "Guardar" to "guarda", "Todo" to "selecciona todo"))
        val escribir = EditText(this)
        escribir.hint = "Escribir en el PC…"
        escribir.setHintTextColor(GRIS)
        escribir.setTextColor(TEXTO)
        escribir.isSingleLine = true
        escribir.imeOptions = EditorInfo.IME_ACTION_SEND
        escribir.setOnEditorActionListener { _, accion, _ ->
            if (accion == EditorInfo.IME_ACTION_SEND) {
                val t = escribir.text.toString().trim()
                if (t.isNotEmpty()) enviar("escribe $t")
                escribir.setText("")
                true
            } else false
        }
        av.addView(escribir)
        av.visibility = if (avanzado) View.VISIBLE else View.GONE
        panelAvanzado = av
        c.addView(av)

        sv.addView(c)
        return sv
    }

    private fun panelActividad(): View {
        val caja = LinearLayout(this)
        caja.orientation = LinearLayout.VERTICAL

        scroll = ScrollView(this)
        registro = LinearLayout(this)
        registro.orientation = LinearLayout.VERTICAL
        scroll.addView(registro)
        val panel = GradientDrawable()
        panel.cornerRadius = dp(12).toFloat()
        panel.setColor(PANEL)
        scroll.background = panel
        scroll.setPadding(dp(10), dp(8), dp(10), dp(8))
        val lpScroll = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f)
        lpScroll.setMargins(0, 0, 0, dp(10))
        caja.addView(scroll, lpScroll)

        val abajo = LinearLayout(this)
        abajo.orientation = LinearLayout.HORIZONTAL
        abajo.gravity = Gravity.CENTER_VERTICAL
        entrada = EditText(this)
        entrada.hint = "Escribe una orden…"
        entrada.setHintTextColor(GRIS)
        entrada.setTextColor(TEXTO)
        entrada.isSingleLine = true
        entrada.inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_CAP_SENTENCES
        entrada.imeOptions = EditorInfo.IME_ACTION_SEND
        entrada.setOnEditorActionListener { _, accion, _ ->
            if (accion == EditorInfo.IME_ACTION_SEND) {
                enviarEntrada()
                true
            } else false
        }
        abajo.addView(entrada, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        abajo.addView(chip("🎤") { hablar() }, margenes(6, 6))
        abajo.addView(chip("➤") { enviarEntrada() }, margenes(0, 0))
        caja.addView(abajo)
        return caja
    }

    private fun agregar(ev: JSONObject) {
        val color = when (ev.optString("tipo")) {
            "orden" -> CIAN
            "voz" -> VERDE
            "aviso" -> AMBAR
            else -> GRIS
        }
        val tv = texto(ev.optString("hora") + "  " + ev.optString("texto"), color, 13f)
        tv.setPadding(0, dp(3), 0, dp(3))
        tv.setTextIsSelectable(true)
        registro.addView(tv)
        while (registro.childCount > 250) registro.removeViewAt(0)
        scroll.post { scroll.fullScroll(View.FOCUS_DOWN) }
    }

    private fun panelComandos(): View {
        val caja = LinearLayout(this)
        caja.orientation = LinearLayout.VERTICAL
        buscador = EditText(this)
        buscador.hint = "Buscar comando…"
        buscador.setHintTextColor(GRIS)
        buscador.setTextColor(TEXTO)
        buscador.isSingleLine = true
        buscador.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable?) { pintarComandos() }
            override fun beforeTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
            override fun onTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
        })
        caja.addView(buscador)
        val sv = ScrollView(this)
        listaComandos = LinearLayout(this)
        listaComandos.orientation = LinearLayout.VERTICAL
        listaComandos.addView(texto("Cargando comandos…", GRIS, 14f))
        sv.addView(listaComandos)
        caja.addView(sv, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))
        return caja
    }

    private fun etiquetaNivel(nivel: String): Pair<String, Int> = when (nivel) {
        "confirmar" -> "⚠ Pide confirmación en el teléfono" to AMBAR
        "avanzado" -> {
            if (avanzado) "⌨ Activo (modo Avanzado del PC)" to VERDE
            else "⌨ Requiere activar «Avanzado» en el PC" to AMBAR
        }
        "parcial" -> {
            if (avanzado) "◐ Todo activo (modo Avanzado del PC)" to VERDE
            else "◐ Flechas, zoom y desplazar: sí. El resto requiere «Avanzado» en el PC" to AMBAR
        }
        "bloqueado" -> "🔒 Solo desde el PC (por seguridad)" to ROJO
        else -> "" to GRIS
    }

    private fun primerEjemplo(ejemplo: String): String {
        var ej = ejemplo.substringBefore(" / ").trim()
        if (ej.startsWith("Alfred ", ignoreCase = true)) ej = ej.substring(7)
        return ej
    }

    private fun pintarComandos() {
        if (!::listaComandos.isInitialized) return
        val f = buscador.text.toString().trim().lowercase(Locale.getDefault())
        listaComandos.removeAllViews()
        if (catalogo.isEmpty()) {
            listaComandos.addView(texto("Cargando comandos…", GRIS, 14f))
            return
        }
        val categorias = ArrayList<String>()
        for (c in catalogo) if (!categorias.contains(c.categoria)) categorias.add(c.categoria)
        var mostrados = 0
        val misPropios = propios.filter { f.isEmpty() || it.first.lowercase(Locale.getDefault()).contains(f) }
        if (misPropios.isNotEmpty()) {
            listaComandos.addView(seccion("Tus comandos"))
            for ((frase, nivel) in misPropios) {
                mostrados++
                listaComandos.addView(filaComando(frase, "«$frase»", nivel, frase))
            }
        }
        for (cat in categorias) {
            val delGrupo = catalogo.filter {
                it.categoria == cat && (f.isEmpty() || (it.desc + " " + it.ejemplo).lowercase(Locale.getDefault()).contains(f))
            }
            if (delGrupo.isEmpty()) continue
            listaComandos.addView(seccion(cat))
            for (c in delGrupo) {
                mostrados++
                listaComandos.addView(filaComando(c.desc, "«" + c.ejemplo + "»", c.remoto, primerEjemplo(c.ejemplo)))
            }
        }
        if (mostrados == 0) listaComandos.addView(texto("No hay comandos con esa palabra.", GRIS, 14f))
    }

    private fun filaComando(titulo: String, ejemplo: String, nivel: String, aEscribir: String): View {
        val fila = LinearLayout(this)
        fila.orientation = LinearLayout.VERTICAL
        fila.setPadding(dp(12), dp(10), dp(12), dp(10))
        val fondo = GradientDrawable()
        fondo.cornerRadius = dp(10).toFloat()
        fondo.setColor(PANEL)
        fila.background = fondo
        val lp = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        lp.setMargins(0, dp(3), 0, dp(3))
        fila.layoutParams = lp
        fila.addView(texto(titulo, if (nivel == "bloqueado") GRIS else TEXTO, 14f))
        fila.addView(texto(ejemplo, if (nivel == "bloqueado") GRIS else CIAN, 12f))
        val (etiqueta, color) = etiquetaNivel(nivel)
        if (etiqueta.isNotEmpty()) fila.addView(texto(etiqueta, color, 12f))
        fila.setOnClickListener {
            if (nivel == "bloqueado") {
                avisar("Esa orden solo se puede dar desde el PC.")
            } else {
                // pasa el ejemplo al cuadro de texto (sin la palabra de activación) para ajustarlo y enviarlo
                mostrarPanel(1)
                entrada.setText(aEscribir)
                entrada.setSelection(entrada.text.length)
                entrada.requestFocus()
            }
        }
        return fila
    }

    private fun cargarCatalogo() {
        val c = cliente ?: return
        Thread {
            try {
                val r = c.pedir("GET", "/api/comandos", null, 10000)
                val arr = r.json?.optJSONArray("comandos")
                if (r.codigo != 200 || arr == null) return@Thread
                val lista = ArrayList<Cmd>()
                for (i in 0 until arr.length()) {
                    val o = arr.getJSONObject(i)
                    var cat = o.optString("categoria")
                    if (cat.isEmpty()) cat = o.optString("seccion")
                    if (cat.isEmpty()) cat = "Comandos"
                    lista.add(Cmd(o.optString("id"), o.optString("ejemplo"), o.optString("descripcion"), cat, o.optString("remoto", "libre")))
                }
                val mios = ArrayList<Pair<String, String>>()
                val pa = r.json?.optJSONArray("personalizados")
                if (pa != null) for (i in 0 until pa.length()) {
                    val o = pa.getJSONObject(i)
                    mios.add(o.optString("frase") to o.optString("remoto", "libre"))
                }
                catalogo = lista
                propios = mios
                runOnUiThread { pintarComandos() }
            } catch (e: Exception) {
                // se reintenta al abrir la pestaña
            }
        }.start()
    }

    // ── enviar órdenes ───────────────────────────────────────────────────────
    private fun enviarEntrada() {
        val t = entrada.text.toString()
        if (t.isBlank()) return
        entrada.setText("")
        enviar(t)
    }

    private fun enviar(texto: String, confirmado: Boolean = false) {
        val t = texto.trim()
        if (t.isEmpty()) return
        val c = cliente
        if (c == null) {
            render()
            return
        }
        Thread {
            try {
                val cuerpo = JSONObject().put("texto", t).put("espera", 0)
                if (confirmado) cuerpo.put("confirmado", true)
                val r = c.pedir("POST", "/api/orden", cuerpo, 10000)
                when {
                    r.codigo == 401 -> runOnUiThread { clavePerdida() }
                    r.codigo == 409 -> {
                        val pregunta = r.json?.optString("mensaje").orEmpty().ifEmpty { "¿Seguro que quieres hacerlo?" }
                        runOnUiThread {
                            dialogo().setMessage(pregunta)
                                .setPositiveButton("Sí, hazlo") { _, _ -> enviar(t, true) }
                                .setNegativeButton("Cancelar", null)
                                .show()
                        }
                    }
                    r.codigo == 403 -> avisar(r.json?.optString("error").orEmpty().ifEmpty { "Esa orden no se puede dar desde el móvil." })
                    r.codigo == 429 -> avisar("Demasiados intentos fallidos; espera unos minutos.")
                    r.codigo !in 200..299 -> avisar(r.json?.optString("error").orEmpty().ifEmpty { "Error ${r.codigo}" })
                }
            } catch (e: Exception) {
                avisar("No pude enviar: " + (e.message ?: e.javaClass.simpleName))
            }
        }.start()
    }

    private fun hablar() {
        val i = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault().toLanguageTag())
            .putExtra(RecognizerIntent.EXTRA_PROMPT, "Dile a Alfred qué hacer")
        try {
            startActivityForResult(i, 1)
        } catch (e: Exception) {
            avisar("Este teléfono no tiene reconocimiento de voz.")
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == 1 && resultCode == RESULT_OK) {
            val t = data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)?.firstOrNull()
            if (!t.isNullOrBlank()) enviar(t)
        }
    }

    /** La clave dejó de valer: quitaron este teléfono de la lista del PC o cambiaron la clave. */
    private fun clavePerdida() {
        if (avisoClave) return
        avisoClave = true
        sondeoId++
        pintarEstado("Teléfono no vinculado", ROJO)
        dialogo().setTitle("Teléfono no vinculado")
            .setMessage("El PC ya no reconoce a este teléfono (lo quitaron de la lista o cambiaron la clave). Vincúlalo otra vez con el código QR.")
            .setPositiveButton("Vincular de nuevo") { _, _ ->
                almacen.borrar()
                cliente = null
                render()
                escanear()
            }
            .setNegativeButton("Cerrar", null)
            .show()
    }

    // ── seguir lo que pasa en el PC (sondeo largo a /api/eventos) ────────────
    private fun iniciarSondeo() {
        val c = cliente
        if (c == null) {
            pintarEstado("Sin conectar", GRIS)
            return
        }
        val id = ++sondeoId
        Thread { bucleSondeo(id, c) }.start()
    }

    private fun textoEstado(c: Cliente, j: JSONObject): String {
        val pc = j.optString("pc").ifEmpty { almacen.nombrePc.ifEmpty { j.optString("nombre", "Alfred") } }
        val esc = if (j.optBoolean("escuchando")) "escuchando" else "sin escuchar"
        val rep = if (j.isNull("reproductor")) "" else j.optString("reproductor", "")
        return pc + " · " + Enlace.tipoDeRuta(c.activa) + " · " + esc + (if (rep.isNotEmpty()) " · $rep" else "")
    }

    /** El PC cuenta cuáles son sus direcciones actuales: se guardan para la próxima vez. */
    private fun actualizarRutas(c: Cliente, j: JSONObject) {
        val idNuevo = j.optString("id_pc")
        if (almacen.idPc.isEmpty() && idNuevo.isNotEmpty()) almacen.idPc = idNuevo      // vinculaciones de la 1.0
        val arr = j.optJSONArray("rutas") ?: return
        val nuevas = ArrayList<String>()
        for (i in 0 until arr.length()) nuevas.add(Enlace.normalizarRuta(arr.getString(i)))
        if (nuevas.isEmpty()) return
        val lista = if (nuevas.contains(c.activa)) nuevas else listOf(c.activa) + nuevas
        if (lista != c.rutas) {
            c.rutas = lista
            almacen.rutas = lista
        }
        if (almacen.direccion != c.activa) almacen.direccion = c.activa
    }

    private fun aplicarAvanzado(valor: Boolean) {
        if (valor == avanzado) return
        avanzado = valor
        runOnUiThread {
            panelAvanzado?.visibility = if (valor) View.VISIBLE else View.GONE
            pintarComandos()
        }
    }

    /** Si el PC cambió de IP, lo busca por la Wi-Fi (como mucho una vez por minuto). */
    private fun buscarEnRed(id: Int, c: Cliente) {
        val ahora = System.currentTimeMillis()
        if (c.idPc.isEmpty() || ahora - ultimaBusqueda < 60000) return
        ultimaBusqueda = ahora
        val r = Red.buscarPc(c.idPc) ?: return
        if (id != sondeoId) return
        c.agregarRuta(r)
        almacen.rutas = c.rutas
        almacen.direccion = r
    }

    private fun bucleSondeo(id: Int, c: Cliente) {
        var desde = 0L
        var primera = true
        var ultimoEstado = 0L
        while (id == sondeoId) {
            try {
                val ahora = System.currentTimeMillis()
                if (ahora - ultimoEstado > 15000) {
                    val e = c.pedir("GET", "/api/estado", null, 8000)
                    if (id != sondeoId) return
                    if (e.codigo == 401) {
                        runOnUiThread { clavePerdida() }
                        return
                    }
                    val j = e.json
                    if (e.codigo == 200 && j != null) {
                        pintarEstado(textoEstado(c, j), VERDE)
                        aplicarAvanzado(j.optBoolean("avanzado"))
                        actualizarRutas(c, j)
                        ultimoEstado = ahora
                    }
                }
                val ruta = "/api/eventos?desde=$desde&espera=20" + (if (primera) "&ultimos=40" else "")
                val r = c.pedir("GET", ruta, null, 30000)
                if (id != sondeoId) return
                if (r.codigo == 401) {
                    runOnUiThread { clavePerdida() }
                    return
                }
                val j = r.json ?: throw IllegalStateException("respuesta vacía")
                val ev = j.optJSONArray("eventos")
                if (ev != null && ev.length() > 0) {
                    runOnUiThread { for (i in 0 until ev.length()) agregar(ev.getJSONObject(i)) }
                }
                desde = j.optLong("ultimo", desde)      // si Alfred se reinició, la numeración vuelve a empezar
                primera = false
            } catch (e: Exception) {
                if (id != sondeoId) return
                pintarEstado("Sin conexión con el PC · buscándolo…", AMBAR)
                ultimoEstado = 0L
                try {
                    buscarEnRed(id, c)
                    Thread.sleep(3000)
                } catch (e2: InterruptedException) {
                    return
                }
            }
        }
    }

    // ── ajustes ──────────────────────────────────────────────────────────────
    private fun mostrarAjustes() {
        val c = cliente
        if (c == null) {
            render()
            return
        }
        val titulo = (almacen.nombrePc.ifEmpty { "Mi PC" }) + "\n" + Enlace.tipoDeRuta(c.activa) + " · " +
            c.activa.substringAfter("://")
        val acciones = arrayOf(
            "📷  Vincular otro PC (escanear QR)",
            "📋  Pegar enlace",
            "🔎  Buscar mi PC en esta Wi-Fi",
            "🌍  Usar fuera de casa (Tailscale)",
            "🗑  Olvidar este PC"
        )
        dialogo().setTitle(titulo)
            .setItems(acciones) { _, cual ->
                when (cual) {
                    0 -> escanear()
                    1 -> pegarEnlace()
                    2 -> buscarAhora()
                    3 -> dialogoFuera()
                    4 -> confirmarOlvidar()
                }
            }
            .setNegativeButton("Cerrar", null)
            .show()
    }

    private fun buscarAhora() {
        val c = cliente ?: return
        avisar("Buscando tu PC en esta Wi-Fi…")
        Thread {
            val alc = c.reconectar()
            if (alc != null) {
                avisar("Conectado: " + Enlace.tipoDeRuta(alc))
                return@Thread
            }
            val r = if (c.idPc.isEmpty()) null else Red.buscarPc(c.idPc)
            if (r == null) {
                avisar("No lo encuentro. ¿Está encendido y en la misma Wi-Fi? Fuera de casa necesitas Tailscale.")
            } else {
                c.agregarRuta(r)
                almacen.rutas = c.rutas
                almacen.direccion = r
                avisar("¡Encontrado! Conectado por Wi-Fi.")
            }
        }.start()
    }

    private fun confirmarOlvidar() {
        dialogo().setTitle("Olvidar este PC")
            .setMessage("Este teléfono dejará de controlar a ${almacen.nombrePc.ifEmpty { "tu PC" }} y se quitará de su lista de teléfonos vinculados.")
            .setPositiveButton("Olvidar") { _, _ -> olvidar() }
            .setNegativeButton("Cancelar", null)
            .show()
    }

    private fun olvidar() {
        val c = cliente
        sondeoId++
        Thread {
            try {
                c?.pedir("POST", "/api/desvincular", JSONObject(), 5000)      // avisa al PC si lo alcanza (si no, no pasa nada)
            } catch (e: Exception) {
                // sin conexión: el PC conservará el teléfono en su lista hasta que lo quites allí
            }
            runOnUiThread {
                almacen.borrar()
                cliente = null
                catalogo = emptyList()
                propios = emptyList()
                avanzado = false
                render()
            }
        }.start()
    }
}
