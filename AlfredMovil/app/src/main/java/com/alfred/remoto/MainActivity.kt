package com.alfred.remoto

import android.app.Activity
import android.app.AlertDialog
import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.speech.RecognizerIntent
import android.text.Editable
import android.text.InputType
import android.text.TextWatcher
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.EditorInfo
import android.widget.ArrayAdapter
import android.widget.EditText
import android.widget.HorizontalScrollView
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import org.json.JSONObject
import java.util.Locale

class MainActivity : Activity() {

    private lateinit var almacen: Almacen
    private var cliente: Cliente? = null

    private lateinit var estado: TextView
    private lateinit var registro: LinearLayout
    private lateinit var scroll: ScrollView
    private lateinit var entrada: EditText

    @Volatile
    private var sondeoId = 0

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

    private val rapidos = listOf(
        "🔉 Vol −" to "baja el volumen",
        "🔊 Vol +" to "sube el volumen",
        "🔇 Silencio" to "silencio",
        "▶ Play" to "play",
        "⏸ Pausa" to "pausa",
        "⏭ Siguiente" to "siguiente canción",
        "⏮ Anterior" to "canción anterior",
        "🎵 ¿Qué suena?" to "qué suena",
        "📷 Captura" to "captura de pantalla",
        "🖥 Descanso" to "descanso",
        "🔒 Bloquear" to "bloquea la pantalla",
        "📊 Estado PC" to "estado del sistema"
    )

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()

    // ── ciclo de vida ────────────────────────────────────────────────────────
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        almacen = Almacen(this)
        window.statusBarColor = FONDO
        window.navigationBarColor = FONDO
        setContentView(construirUI())
        cargarCliente()
        if (cliente == null) mostrarAjustes()
    }

    override fun onStart() {
        super.onStart()
        iniciarSondeo()
    }

    override fun onStop() {
        sondeoId++            // detiene el sondeo en segundo plano: la app solo escucha mientras está a la vista
        super.onStop()
    }

    private fun cargarCliente() {
        val d = almacen.direccion
        val k = almacen.clave
        cliente = if (d.isNotEmpty() && k.isNotEmpty()) Cliente(d, k) else null
    }

    // ── interfaz ─────────────────────────────────────────────────────────────
    private fun chip(texto: String, accion: () -> Unit): TextView {
        val t = TextView(this)
        t.text = texto
        t.setTextColor(TEXTO)
        t.textSize = 14f
        t.gravity = Gravity.CENTER
        t.setPadding(dp(14), dp(9), dp(14), dp(9))
        val fondo = GradientDrawable()
        fondo.cornerRadius = dp(18).toFloat()
        fondo.setColor(PANEL)
        fondo.setStroke(dp(1), BORDE)
        t.background = fondo
        t.setOnClickListener { accion() }
        return t
    }

    private fun margenes(izq: Int = 0, der: Int = 6): LinearLayout.LayoutParams {
        val p = LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        p.setMargins(dp(izq), 0, dp(der), 0)
        return p
    }

    private fun construirUI(): View {
        val raiz = LinearLayout(this)
        raiz.orientation = LinearLayout.VERTICAL
        raiz.setBackgroundColor(FONDO)
        raiz.setPadding(dp(14), dp(14), dp(14), dp(10))

        // cabecera
        val fila = LinearLayout(this)
        fila.orientation = LinearLayout.HORIZONTAL
        fila.gravity = Gravity.CENTER_VERTICAL
        val titulo = TextView(this)
        titulo.text = "ALFRED"
        titulo.setTextColor(CIAN)
        titulo.textSize = 22f
        titulo.typeface = Typeface.create("sans-serif-medium", Typeface.BOLD)
        titulo.letterSpacing = 0.25f
        fila.addView(titulo, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        fila.addView(chip("📖") { mostrarComandos() }, margenes())
        fila.addView(chip("⚙") { mostrarAjustes() }, margenes(0, 0))
        raiz.addView(fila)

        estado = TextView(this)
        estado.text = "● Sin conectar"
        estado.setTextColor(GRIS)
        estado.textSize = 13f
        estado.setPadding(0, dp(4), 0, dp(8))
        raiz.addView(estado)

        // botones rápidos
        val barra = HorizontalScrollView(this)
        barra.isHorizontalScrollBarEnabled = false
        val chips = LinearLayout(this)
        chips.orientation = LinearLayout.HORIZONTAL
        for ((etiqueta, frase) in rapidos) chips.addView(chip(etiqueta) { enviar(frase) }, margenes())
        barra.addView(chips)
        raiz.addView(barra)

        // registro de lo que oye, hace y dice Alfred
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
        lpScroll.setMargins(0, dp(10), 0, dp(10))
        raiz.addView(scroll, lpScroll)

        // escribir / hablar / enviar
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
                enviar(entrada.text.toString())
                true
            } else false
        }
        abajo.addView(entrada, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        abajo.addView(chip("🎤") { hablar() }, margenes(6, 6))
        abajo.addView(chip("➤") { enviar(entrada.text.toString()) }, margenes(0, 0))
        raiz.addView(abajo)

        return raiz
    }

    private fun agregar(ev: JSONObject) {
        val color = when (ev.optString("tipo")) {
            "orden" -> CIAN
            "voz" -> VERDE
            "aviso" -> AMBAR
            else -> GRIS
        }
        val tv = TextView(this)
        tv.text = ev.optString("hora") + "  " + ev.optString("texto")
        tv.setTextColor(color)
        tv.textSize = 13f
        tv.setPadding(0, dp(3), 0, dp(3))
        tv.setTextIsSelectable(true)
        registro.addView(tv)
        while (registro.childCount > 250) registro.removeViewAt(0)
        scroll.post { scroll.fullScroll(View.FOCUS_DOWN) }
    }

    private fun pintarEstado(texto: String, color: Int) {
        runOnUiThread {
            estado.text = "● $texto"
            estado.setTextColor(color)
        }
    }

    private fun avisar(msg: String) {
        runOnUiThread { Toast.makeText(this, msg, Toast.LENGTH_LONG).show() }
    }

    // ── enviar órdenes ───────────────────────────────────────────────────────
    private fun enviar(texto: String) {
        val t = texto.trim()
        if (t.isEmpty()) return
        val c = cliente
        if (c == null) {
            mostrarAjustes()
            return
        }
        entrada.setText("")
        Thread {
            try {
                val r = c.pedir("POST", "/api/orden", JSONObject().put("texto", t).put("espera", 0), 10000)
                when {
                    r.codigo == 401 -> avisar("Clave incorrecta. Revísala en ⚙.")
                    r.codigo == 429 -> avisar("Demasiados intentos fallidos; espera unos minutos.")
                    r.codigo !in 200..299 -> avisar(r.json?.optString("error") ?: "Error ${r.codigo}")
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

    private fun textoEstado(j: JSONObject): String {
        val nombre = j.optString("nombre", "Alfred")
        val esc = if (j.optBoolean("escuchando")) "escuchando" else "sin escuchar"
        val rep = if (j.isNull("reproductor")) "" else j.optString("reproductor", "")
        return "$nombre · $esc" + (if (rep.isNotEmpty()) " · $rep" else "")
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
                        pintarEstado("Clave incorrecta (⚙)", ROJO)
                        return
                    }
                    val j = e.json
                    if (e.codigo == 200 && j != null) {
                        pintarEstado(textoEstado(j), VERDE)
                        ultimoEstado = ahora
                    }
                }
                val ruta = "/api/eventos?desde=$desde&espera=20" + (if (primera) "&ultimos=40" else "")
                val r = c.pedir("GET", ruta, null, 30000)
                if (id != sondeoId) return
                if (r.codigo == 401) {
                    pintarEstado("Clave incorrecta (⚙)", ROJO)
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
                pintarEstado("Sin conexión con el PC", AMBAR)
                ultimoEstado = 0L
                try {
                    Thread.sleep(3000)
                } catch (e2: InterruptedException) {
                    return
                }
            }
        }
    }

    // ── ajustes: enlace + clave ──────────────────────────────────────────────
    private fun mostrarAjustes() {
        val caja = LinearLayout(this)
        caja.orientation = LinearLayout.VERTICAL
        caja.setPadding(dp(20), dp(10), dp(20), 0)

        val ayuda = TextView(this)
        ayuda.text = "En el PC: ☰ Menú → Remoto → activa el control remoto y «Permitir otros dispositivos de mi red Wi-Fi». " +
            "Toca «Copiar enlace», envíatelo (WhatsApp, correo…) y pégalo aquí. También puedes escribir solo la IP del PC y la clave."
        ayuda.textSize = 13f
        caja.addView(ayuda)

        val enlace = EditText(this)
        enlace.hint = "Enlace o IP del PC (http://192.168.1.20:47654/#t=…)"
        enlace.isSingleLine = true
        enlace.inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_URI
        enlace.setText(almacen.direccion)
        caja.addView(enlace)

        val clave = EditText(this)
        clave.hint = if (almacen.clave.isNotEmpty()) "Clave (guardada; déjala vacía para conservarla)" else "Clave (solo si no va en el enlace)"
        clave.isSingleLine = true
        clave.inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
        caja.addView(clave)

        val resultado = TextView(this)
        resultado.textSize = 13f
        resultado.setPadding(0, dp(8), 0, 0)
        caja.addView(resultado)

        val dialogo = AlertDialog.Builder(this, android.R.style.Theme_Material_Dialog_Alert)
            .setTitle("Conectar con Alfred")
            .setView(caja)
            .setPositiveButton("Guardar y probar", null)
            .setNeutralButton("Olvidar PC", null)
            .setNegativeButton("Cerrar", null)
            .create()
        dialogo.show()

        dialogo.getButton(AlertDialog.BUTTON_NEUTRAL).setOnClickListener {
            sondeoId++
            almacen.borrar()
            cliente = null
            registro.removeAllViews()
            pintarEstado("Sin conectar", GRIS)
            enlace.setText("")
            clave.setText("")
            resultado.setTextColor(GRIS)
            resultado.text = "Datos borrados de este teléfono."
        }

        dialogo.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
            val datos = Enlace.analizar(enlace.text.toString())
            if (datos == null) {
                resultado.setTextColor(ROJO)
                resultado.text = "Esa dirección no es válida."
                return@setOnClickListener
            }
            val claveFinal = datos.clave ?: clave.text.toString().trim().ifEmpty { almacen.clave }
            if (claveFinal.isEmpty()) {
                resultado.setTextColor(ROJO)
                resultado.text = "Falta la clave (aparece en el enlace de Alfred o en ☰ Menú → Remoto)."
                return@setOnClickListener
            }
            resultado.setTextColor(GRIS)
            resultado.text = "Buscando a Alfred…"
            Thread {
                val base = Cliente.descubrir(datos.base)
                if (base == null) {
                    runOnUiThread {
                        resultado.setTextColor(ROJO)
                        resultado.text = "No encuentro a Alfred en ${datos.base}. Comprueba que el control remoto esté activo, " +
                            "que «Permitir otros dispositivos de mi red Wi-Fi» esté encendido y que el teléfono esté en la misma red."
                    }
                    return@Thread
                }
                val codigo = try {
                    Cliente(base, claveFinal).pedir("GET", "/api/estado", null, 8000).codigo
                } catch (e: Exception) {
                    -1
                }
                runOnUiThread {
                    when (codigo) {
                        200 -> {
                            almacen.direccion = base
                            almacen.clave = claveFinal
                            cargarCliente()
                            registro.removeAllViews()
                            dialogo.dismiss()
                            iniciarSondeo()
                        }
                        401 -> {
                            resultado.setTextColor(ROJO)
                            resultado.text = "Encontré a Alfred, pero la clave es incorrecta."
                        }
                        429 -> {
                            resultado.setTextColor(AMBAR)
                            resultado.text = "Demasiados intentos fallidos. Espera unos minutos."
                        }
                        else -> {
                            resultado.setTextColor(ROJO)
                            resultado.text = "No pude comprobar la clave (código $codigo)."
                        }
                    }
                }
            }.start()
        }
    }

    // ── lista de comandos del PC (/api/comandos) ─────────────────────────────
    private fun mostrarComandos() {
        val c = cliente
        if (c == null) {
            mostrarAjustes()
            return
        }
        Thread {
            try {
                val r = c.pedir("GET", "/api/comandos", null, 10000)
                val arr = r.json?.optJSONArray("comandos")
                if (r.codigo != 200 || arr == null) {
                    avisar("No pude leer la lista de comandos.")
                    return@Thread
                }
                val todos = ArrayList<Pair<String, String>>()     // (descripción, ejemplo)
                for (i in 0 until arr.length()) {
                    val o = arr.getJSONObject(i)
                    todos.add(o.optString("descripcion") to o.optString("ejemplo"))
                }
                runOnUiThread { dialogoComandos(todos) }
            } catch (e: Exception) {
                avisar("No pude leer la lista: " + (e.message ?: e.javaClass.simpleName))
            }
        }.start()
    }

    private fun dialogoComandos(todos: List<Pair<String, String>>) {
        val caja = LinearLayout(this)
        caja.orientation = LinearLayout.VERTICAL
        caja.setPadding(dp(16), dp(8), dp(16), 0)

        val buscar = EditText(this)
        buscar.hint = "Buscar comando…"
        buscar.isSingleLine = true
        caja.addView(buscar)

        val lista = ListView(this)
        caja.addView(lista, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(380)))

        val mostrados = ArrayList<Pair<String, String>>(todos)
        val adaptador = ArrayAdapter(this, android.R.layout.simple_list_item_1, ArrayList<String>())
        fun texto(p: Pair<String, String>) = p.first + "\n«" + p.second + "»"
        fun refrescar(filtro: String) {
            val f = filtro.trim().lowercase()
            mostrados.clear()
            mostrados.addAll(todos.filter { f.isEmpty() || (it.first + " " + it.second).lowercase().contains(f) })
            adaptador.clear()
            adaptador.addAll(mostrados.map { texto(it) })
        }
        lista.adapter = adaptador
        refrescar("")
        buscar.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable?) { refrescar(s?.toString() ?: "") }
            override fun beforeTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
            override fun onTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
        })

        val dialogo = AlertDialog.Builder(this, android.R.style.Theme_Material_Dialog_Alert)
            .setTitle("Comandos de Alfred")
            .setView(caja)
            .setNegativeButton("Cerrar", null)
            .create()
        lista.setOnItemClickListener { _, _, pos, _ ->
            // Pasa el primer ejemplo al cuadro de texto, sin la palabra de activación, para ajustarlo y enviarlo
            var ej = mostrados[pos].second.substringBefore(" / ").trim()
            if (ej.startsWith("Alfred ", ignoreCase = true)) ej = ej.substring(7)
            entrada.setText(ej)
            entrada.setSelection(entrada.text.length)
            entrada.requestFocus()
            dialogo.dismiss()
        }
        dialogo.show()
    }
}
