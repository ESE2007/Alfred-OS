package com.camaraauto2

import android.Manifest
import android.content.ActivityNotFoundException
import android.content.ContentUris
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.SurfaceTexture
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.provider.MediaStore
import android.util.Size
import android.view.GestureDetector
import android.view.Gravity
import android.view.MotionEvent
import android.view.OrientationEventListener
import android.view.ScaleGestureDetector
import android.view.TextureView
import android.view.View
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import java.util.Locale
import java.util.concurrent.Executors
import kotlin.math.max
import kotlin.math.pow
import kotlin.math.roundToInt

class MainActivity : AppCompatActivity(), CameraEngine.Listener {

    // Vistas
    private lateinit var root: FrameLayout
    private lateinit var previewWindow: FrameLayout
    private lateinit var textureView: TextureView
    private lateinit var gridOverlay: GridOverlay
    private lateinit var focusRing: View
    private lateinit var sceneLabel: TextView
    private lateinit var zoomLabel: TextView
    private lateinit var processing: TextView
    private lateinit var btnFlash: TextView
    private lateinit var btnMode: TextView
    private lateinit var btnGrid: TextView
    private lateinit var btnAspect: TextView
    private lateinit var btnSpeed: TextView
    private lateinit var thumb: ImageView
    private lateinit var shutter: View

    // Cámara
    private var engine: CameraEngine? = null
    private var textureReady = false
    private var resumed = false
    private var permissionAsked = false
    private var ready = false

    // Estado
    private var uiMode = UiMode.AUTO
    private var aspect = AspectOption.R43
    private var fast = false
    private var flash = FlashMode.OFF
    private var frameRatio = 4f / 3f // alto / ancho de la ventana visible = proporción de la foto
    private var busy = false
    private var deviceOrientation = 0
    private var captureStart = 0L
    private var captureMode = CaptureMode.NORMAL
    private var lastUri: Uri? = null

    // Detección de escena (modo AUTO)
    private var smoothedEv = Float.NaN
    private var currentScene = Scene.NORMAL
    private var pendingScene = Scene.NORMAL
    private var pendingCount = 0
    private var autoMode = CaptureMode.SUPER_RES
    private var clippedFrac = 0f
    private var darkFrac = 0f

    private val handler = Handler(Looper.getMainLooper())
    private val io = Executors.newSingleThreadExecutor()

    private val prefs by lazy { getSharedPreferences("cfg", Context.MODE_PRIVATE) }

    private val tick = object : Runnable {
        override fun run() {
            onTick()
            handler.postDelayed(this, 500)
        }
    }

    private val processingTick = object : Runnable {
        override fun run() {
            if (!busy) return
            val seconds = (SystemClock.elapsedRealtime() - captureStart) / 1000f
            processing.text = String.format(
                Locale.US,
                "Procesando en modo %s… %.0f s\nNo muevas el teléfono",
                captureMode.label, seconds
            )
            handler.postDelayed(this, 250)
        }
    }

    private val orientationListener by lazy {
        object : OrientationEventListener(this) {
            override fun onOrientationChanged(orientation: Int) {
                if (orientation != ORIENTATION_UNKNOWN) deviceOrientation = orientation
            }
        }
    }

    private val permissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) {
                maybeOpen()
            } else {
                toast("Necesito el permiso de cámara para funcionar")
                finish()
            }
        }

    // ------------------------------------------------------------------ Ciclo de vida

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        root = findViewById(R.id.root)
        previewWindow = findViewById(R.id.previewWindow)
        textureView = findViewById(R.id.textureView)
        gridOverlay = findViewById(R.id.gridOverlay)
        focusRing = findViewById(R.id.focusRing)
        sceneLabel = findViewById(R.id.sceneLabel)
        zoomLabel = findViewById(R.id.zoomLabel)
        processing = findViewById(R.id.processing)
        btnFlash = findViewById(R.id.btnFlash)
        btnMode = findViewById(R.id.btnMode)
        btnGrid = findViewById(R.id.btnGrid)
        btnAspect = findViewById(R.id.btnAspect)
        btnSpeed = findViewById(R.id.btnSpeed)
        thumb = findViewById(R.id.thumb)
        shutter = findViewById(R.id.shutter)

        // Últimas opciones usadas
        uiMode = UiMode.values().getOrElse(prefs.getInt("mode", 0)) { UiMode.AUTO }
        aspect = AspectOption.values().getOrElse(prefs.getInt("aspect", 0)) { AspectOption.R43 }
        fast = prefs.getBoolean("fast", false)

        textureView.surfaceTextureListener = object : TextureView.SurfaceTextureListener {
            override fun onSurfaceTextureAvailable(st: SurfaceTexture, w: Int, h: Int) {
                textureReady = true
                maybeOpen()
            }

            override fun onSurfaceTextureSizeChanged(st: SurfaceTexture, w: Int, h: Int) {}

            override fun onSurfaceTextureDestroyed(st: SurfaceTexture): Boolean {
                textureReady = false
                return true
            }

            override fun onSurfaceTextureUpdated(st: SurfaceTexture) {}
        }

        root.addOnLayoutChangeListener { _, left, top, right, bottom, oldLeft, oldTop, oldRight, oldBottom ->
            if (right - left != oldRight - oldLeft || bottom - top != oldBottom - oldTop) {
                applyPreviewLayout()
            }
        }

        setupTouch()
        shutter.setOnClickListener { onShutter() }
        thumb.setOnClickListener { openLastPhoto() }
        btnFlash.setOnClickListener { cycleFlash() }
        btnMode.setOnClickListener { cycleMode() }
        btnAspect.setOnClickListener { cycleAspect() }
        btnSpeed.setOnClickListener { toggleSpeed() }
        btnGrid.setOnClickListener {
            gridOverlay.visibility = if (gridOverlay.visibility == View.VISIBLE) View.GONE else View.VISIBLE
        }

        refreshButtons()
    }

    override fun onResume() {
        super.onResume()
        resumed = true
        orientationListener.enable()
        handler.post(tick)
        refreshThumb(null)

        if (!hasPermission() && !permissionAsked) {
            permissionAsked = true
            permissionLauncher.launch(Manifest.permission.CAMERA)
        } else {
            maybeOpen()
        }
    }

    override fun onPause() {
        super.onPause()
        resumed = false
        orientationListener.disable()
        handler.removeCallbacks(tick)
        handler.removeCallbacks(processingTick)
        engine?.close()
        engine = null
        ready = false
        busy = false
        processing.visibility = View.GONE
        shutter.alpha = 1f
        sceneLabel.text = "Iniciando cámara…"
    }

    override fun onDestroy() {
        super.onDestroy()
        io.shutdown()
    }

    private fun hasPermission() =
        ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED

    private fun maybeOpen() {
        if (!resumed || !textureReady || engine != null || !hasPermission()) return
        val st = textureView.surfaceTexture ?: return

        val eng = CameraEngine(applicationContext, this)
        try {
            eng.prepare()
            engine = eng
            root.post { applyPreviewLayout() }
            eng.open(st)
        } catch (e: Exception) {
            eng.close()
            engine = null
            toast("No se pudo abrir la cámara: ${e.message}")
        }
    }

    // ------------------------------------------------------------------ Formato de la foto

    /**
     * La ventana visible tiene la proporción de la foto final. La vista previa (siempre 3:4 vertical)
     * se agranda hasta cubrir la ventana, y lo que sobra queda recortado, igual que en la foto.
     */
    private fun applyPreviewLayout() {
        val eng = engine ?: return
        val bufRatio = eng.previewSize.width.toFloat() / eng.previewSize.height // alto / ancho vertical
        val cw = root.width - root.paddingLeft - root.paddingRight
        val ch = root.height - root.paddingTop - root.paddingBottom
        if (cw <= 0 || ch <= 0) return

        var fw = cw.toFloat()
        var fh = when (aspect) {
            AspectOption.R43 -> fw * 4f / 3f
            AspectOption.R169 -> fw * 16f / 9f
            AspectOption.R11 -> fw
            AspectOption.FULL -> ch.toFloat()
        }
        if (fh > ch) {
            val k = ch / fh
            fw *= k
            fh = ch.toFloat()
        }
        val th = max(fh, fw * bufRatio)
        val tw = th / bufRatio

        frameRatio = fh / fw
        previewWindow.layoutParams = FrameLayout.LayoutParams(fw.roundToInt(), fh.roundToInt(), Gravity.CENTER)
        textureView.layoutParams = FrameLayout.LayoutParams(tw.roundToInt(), th.roundToInt(), Gravity.CENTER)
    }

    // ------------------------------------------------------------------ Avisos del motor

    override fun onReady() {
        ready = true
        resetSceneState()
        val eng = engine
        if (eng != null) {
            btnFlash.visibility = if (eng.hasFlash) View.VISIBLE else View.GONE
            if (flash == FlashMode.TORCH) flash = FlashMode.OFF // la luz no queda encendida al reabrir la app
            eng.setFlash(flash)
        }
        refreshButtons()
    }

    override fun onError(message: String) {
        toast(message)
    }

    // ------------------------------------------------------------------ Controles

    private fun cycleFlash() {
        val eng = engine
        if (eng == null || !eng.hasFlash) {
            toast("Esta cámara no tiene flash")
            return
        }
        val all = FlashMode.values()
        flash = all[(flash.ordinal + 1) % all.size]
        eng.setFlash(flash)
        refreshButtons()
        when (flash) {
            FlashMode.AUTO -> toast("Flash AUTO: se usa solo en modo NORMAL")
            FlashMode.ON -> toast("Flash ON: las fotos se toman en modo NORMAL")
            FlashMode.TORCH -> toast("Luz encendida: funciona con todos los modos")
            FlashMode.OFF -> {}
        }
    }

    private fun cycleMode() {
        if (busy) return
        val all = UiMode.values()
        uiMode = all[(uiMode.ordinal + 1) % all.size]
        prefs.edit().putInt("mode", uiMode.ordinal).apply()
        engine?.setEvIndex(0)
        resetSceneState()
        refreshButtons()
    }

    private fun cycleAspect() {
        if (busy) return
        val all = AspectOption.values()
        aspect = all[(aspect.ordinal + 1) % all.size]
        prefs.edit().putInt("aspect", aspect.ordinal).apply()
        applyPreviewLayout()
        refreshButtons()
        if (aspect != AspectOption.R43) toast("Las fotos ${aspect.label} se recortan del centro de la imagen 4:3")
    }

    private fun toggleSpeed() {
        if (busy) return
        fast = !fast
        prefs.edit().putBoolean("fast", fast).apply()
        autoMode = modeForScene(currentScene, fast)
        refreshButtons()
        toast(
            if (fast) "Rápido: AUTO evita los modos lentos"
            else "Calidad: AUTO usa el mejor modo para cada escena"
        )
    }

    private fun resetSceneState() {
        smoothedEv = Float.NaN
        currentScene = Scene.NORMAL
        pendingScene = Scene.NORMAL
        pendingCount = 0
        autoMode = modeForScene(Scene.NORMAL, fast)
    }

    private fun refreshButtons() {
        btnFlash.text = flash.label
        btnMode.text = "MODO: ${uiMode.label}"
        btnAspect.text = aspect.label
        btnSpeed.text = if (fast) "⏱ RÁPIDO" else "✨ CALIDAD"

        val manual = uiMode.capture
        if (manual != null) {
            sceneLabel.text = if (manual.approxSeconds > 1) {
                "Manual: ${manual.label} (≈ ${manual.approxSeconds} s por foto)"
            } else {
                "Manual: ${manual.label}"
            }
        } else if (!ready) {
            sceneLabel.text = "Iniciando cámara…"
        }
    }

    // ------------------------------------------------------------------ Escena (modo AUTO)

    private fun onTick() {
        val eng = engine ?: return
        zoomLabel.text = String.format(Locale.US, "%.1fx", eng.zoom)
        if (busy || !ready) return

        analyzeContrast()
        if (uiMode != UiMode.AUTO) return

        val measured = eng.measuredEv100
        if (measured.isNaN()) return

        // Brillo real de la escena = brillo medido + compensación aplicada (evita un bucle de ajuste)
        val sceneEv = measured + eng.evIndex * eng.evStep
        smoothedEv = if (smoothedEv.isNaN()) sceneEv else smoothedEv * 0.6f + sceneEv * 0.4f

        val candidate = classifyScene(smoothedEv, clippedFrac, darkFrac)
        if (candidate == pendingScene) {
            pendingCount++
        } else {
            pendingScene = candidate
            pendingCount = 1
        }

        // La escena debe mantenerse ~1.5 s antes de cambiar el ajuste (evita parpadeos)
        if (pendingCount >= 3 && candidate != currentScene) {
            currentScene = candidate
            autoMode = modeForScene(candidate, fast)
            if (eng.evStep > 0f) {
                eng.setEvIndex((candidate.ev / eng.evStep).roundToInt())
            }
        }

        val lux = (2.5 * 2.0.pow(smoothedEv.toDouble())).roundToInt()
        sceneLabel.text = "${currentScene.label} · ≈ $lux lux\n→ ${autoMode.label}"
    }

    /** Mide qué parte de la imagen está quemada o en sombras, a partir de un cuadro reducido de la vista previa. */
    private fun analyzeContrast() {
        if (!textureView.isAvailable) return
        val bmp: Bitmap? = try {
            textureView.getBitmap(90, 120)
        } catch (e: Exception) {
            null
        }
        if (bmp == null) return

        val w = bmp.width
        val h = bmp.height
        val px = IntArray(w * h)
        bmp.getPixels(px, 0, w, 0, 0, w, h)
        bmp.recycle()

        var clipped = 0
        var dark = 0
        for (p in px) {
            val luma = 0.299f * ((p shr 16) and 0xFF) + 0.587f * ((p shr 8) and 0xFF) + 0.114f * (p and 0xFF)
            if (luma >= 240) clipped++
            if (luma <= 25) dark++
        }
        clippedFrac = clipped.toFloat() / px.size
        darkFrac = dark.toFloat() / px.size
    }

    // ------------------------------------------------------------------ Disparo

    private fun onShutter() {
        val eng = engine ?: return
        if (busy || !ready) return

        val mode = uiMode.capture ?: autoMode
        // Con flash ON el motor usa NORMAL; el aviso en pantalla muestra lo que realmente se hará
        captureMode = if (flash == FlashMode.ON && mode != CaptureMode.NORMAL) CaptureMode.NORMAL else mode
        captureStart = SystemClock.elapsedRealtime()
        busy = true
        shutter.alpha = 0.4f
        processing.visibility = View.VISIBLE
        handler.post(processingTick)

        eng.capture(
            mode,
            deviceOrientation,
            frameRatio,
            onProcessed = { unlock() },
            onSaved = { outcome ->
                unlock()
                Toast.makeText(this, outcome.message, Toast.LENGTH_LONG).show()
                val uri = outcome.uri
                if (outcome.ok && uri != null) refreshThumb(Uri.parse(uri))
            }
        )
    }

    /** Vuelve a habilitar el disparador (puede llamarse dos veces sin problema). */
    private fun unlock() {
        if (!busy) return
        busy = false
        shutter.alpha = 1f
        processing.visibility = View.GONE
        handler.removeCallbacks(processingTick)
        refreshButtons()
    }

    // ------------------------------------------------------------------ Galería

    /** Muestra la miniatura de la última foto (la indicada o la más reciente de la carpeta de la app). */
    private fun refreshThumb(known: Uri?) {
        if (io.isShutdown) return
        io.execute {
            val uri = known ?: queryLastPhoto()
            val bmp: Bitmap? = if (uri == null) null else try {
                contentResolver.loadThumbnail(uri, Size(200, 200), null)
            } catch (e: Exception) {
                null
            }
            runOnUiThread {
                lastUri = uri
                if (bmp != null) thumb.setImageBitmap(bmp) else thumb.setImageDrawable(null)
            }
        }
    }

    private fun queryLastPhoto(): Uri? {
        val collection = MediaStore.Images.Media.EXTERNAL_CONTENT_URI
        return try {
            contentResolver.query(
                collection,
                arrayOf(MediaStore.Images.Media._ID),
                "${MediaStore.MediaColumns.RELATIVE_PATH} LIKE ?",
                arrayOf("Pictures/CamaraAuto2%"),
                "${MediaStore.Images.Media.DATE_ADDED} DESC"
            )?.use { c ->
                if (c.moveToFirst()) ContentUris.withAppendedId(collection, c.getLong(0)) else null
            }
        } catch (e: Exception) {
            null
        }
    }

    private fun openLastPhoto() {
        val uri = lastUri
        if (uri == null) {
            toast("Aún no hay fotos")
            return
        }
        val view = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "image/jpeg")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        try {
            startActivity(view)
        } catch (e: ActivityNotFoundException) {
            toast("No hay una app para ver fotos")
        }
    }

    // ------------------------------------------------------------------ Gestos

    private fun setupTouch() {
        val scaleDetector = ScaleGestureDetector(
            this,
            object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
                override fun onScale(detector: ScaleGestureDetector): Boolean {
                    val eng = engine ?: return true
                    eng.setZoom(eng.zoom * detector.scaleFactor)
                    return true
                }
            }
        )

        val tapDetector = GestureDetector(
            this,
            object : GestureDetector.SimpleOnGestureListener() {
                override fun onSingleTapUp(e: MotionEvent): Boolean {
                    focusAt(e.x, e.y)
                    return true
                }
            }
        )

        textureView.setOnTouchListener { _, event ->
            scaleDetector.onTouchEvent(event)
            if (!scaleDetector.isInProgress) {
                tapDetector.onTouchEvent(event)
            }
            true
        }
    }

    /** x, y: toque en coordenadas de la vista previa. */
    private fun focusAt(x: Float, y: Float) {
        val eng = engine ?: return
        if (!ready || textureView.width == 0 || textureView.height == 0) return

        eng.focusAt(x / textureView.width, y / textureView.height)

        val tl = IntArray(2)
        val rl = IntArray(2)
        textureView.getLocationOnScreen(tl)
        root.getLocationOnScreen(rl)
        focusRing.animate().cancel()
        focusRing.x = (tl[0] - rl[0]) + x - focusRing.width / 2f
        focusRing.y = (tl[1] - rl[1]) + y - focusRing.height / 2f
        focusRing.alpha = 1f
        focusRing.animate().alpha(0f).setStartDelay(900).setDuration(400).start()
    }

    private fun toast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}
