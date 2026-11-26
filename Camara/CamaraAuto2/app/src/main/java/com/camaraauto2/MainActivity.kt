package com.camaraauto2

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.SurfaceTexture
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.view.GestureDetector
import android.view.Gravity
import android.view.MotionEvent
import android.view.OrientationEventListener
import android.view.ScaleGestureDetector
import android.view.TextureView
import android.view.View
import android.widget.FrameLayout
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import java.util.Locale
import kotlin.math.pow
import kotlin.math.roundToInt

class MainActivity : AppCompatActivity(), CameraEngine.Listener {

    // Vistas
    private lateinit var textureView: TextureView
    private lateinit var gridOverlay: GridOverlay
    private lateinit var focusRing: View
    private lateinit var sceneLabel: TextView
    private lateinit var zoomLabel: TextView
    private lateinit var processing: TextView
    private lateinit var btnMode: TextView
    private lateinit var btnGrid: TextView
    private lateinit var shutter: View

    // Cámara
    private var engine: CameraEngine? = null
    private var textureReady = false
    private var resumed = false
    private var permissionAsked = false
    private var ready = false

    // Estado
    private var uiMode = UiMode.AUTO
    private var busy = false
    private var deviceOrientation = 0
    private var captureStart = 0L
    private var captureMode = CaptureMode.NORMAL

    // Detección de escena (modo AUTO)
    private var smoothedEv = Float.NaN
    private var currentScene = Scene.NORMAL
    private var pendingScene = Scene.NORMAL
    private var pendingCount = 0
    private var autoMode = CaptureMode.SUPER_RES
    private var clippedFrac = 0f
    private var darkFrac = 0f

    private val handler = Handler(Looper.getMainLooper())

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

        textureView = findViewById(R.id.textureView)
        gridOverlay = findViewById(R.id.gridOverlay)
        focusRing = findViewById(R.id.focusRing)
        sceneLabel = findViewById(R.id.sceneLabel)
        zoomLabel = findViewById(R.id.zoomLabel)
        processing = findViewById(R.id.processing)
        btnMode = findViewById(R.id.btnMode)
        btnGrid = findViewById(R.id.btnGrid)
        shutter = findViewById(R.id.shutter)

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

        setupTouch()
        shutter.setOnClickListener { onShutter() }
        btnMode.setOnClickListener { cycleMode() }
        btnGrid.setOnClickListener {
            gridOverlay.visibility = if (gridOverlay.visibility == View.VISIBLE) View.GONE else View.VISIBLE
        }
        refreshModeButton()
    }

    override fun onResume() {
        super.onResume()
        resumed = true
        orientationListener.enable()
        handler.post(tick)

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

    private fun hasPermission() =
        ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED

    private fun maybeOpen() {
        if (!resumed || !textureReady || engine != null || !hasPermission()) return
        val st = textureView.surfaceTexture ?: return

        val eng = CameraEngine(applicationContext, this)
        try {
            val size = eng.prepare()
            layoutPreview(size.width, size.height)
            engine = eng
            eng.open(st)
        } catch (e: Exception) {
            eng.close()
            toast("No se pudo abrir la cámara: ${e.message}")
        }
    }

    /** La vista previa se muestra vertical: el alto es el ancho multiplicado por 4/3. */
    private fun layoutPreview(bufferWidth: Int, bufferHeight: Int) {
        val screenW = resources.displayMetrics.widthPixels
        val h = (screenW * bufferWidth.toFloat() / bufferHeight).toInt()
        val lp = FrameLayout.LayoutParams(screenW, h, Gravity.CENTER)
        textureView.layoutParams = lp
        gridOverlay.layoutParams = FrameLayout.LayoutParams(lp)
    }

    // ------------------------------------------------------------------ Avisos del motor

    override fun onReady() {
        ready = true
        resetSceneState()
        refreshModeButton()
    }

    override fun onError(message: String) {
        toast(message)
    }

    // ------------------------------------------------------------------ Modos y escena

    private fun cycleMode() {
        if (busy) return
        val all = UiMode.values()
        uiMode = all[(uiMode.ordinal + 1) % all.size]
        engine?.setEvIndex(0)
        resetSceneState()
        refreshModeButton()
    }

    private fun resetSceneState() {
        smoothedEv = Float.NaN
        currentScene = Scene.NORMAL
        pendingScene = Scene.NORMAL
        pendingCount = 0
        autoMode = CaptureMode.SUPER_RES
    }

    private fun refreshModeButton() {
        btnMode.text = "MODO: ${uiMode.label}"
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
            autoMode = modeForScene(candidate)
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
        captureMode = mode
        captureStart = SystemClock.elapsedRealtime()
        busy = true
        shutter.alpha = 0.4f
        processing.visibility = View.VISIBLE
        handler.post(processingTick)

        eng.capture(mode, deviceOrientation) { outcome ->
            busy = false
            shutter.alpha = 1f
            processing.visibility = View.GONE
            handler.removeCallbacks(processingTick)
            Toast.makeText(this, outcome.message, Toast.LENGTH_LONG).show()
            refreshModeButton()
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

    private fun focusAt(x: Float, y: Float) {
        val eng = engine ?: return
        if (!ready || textureView.width == 0 || textureView.height == 0) return

        eng.focusAt(x / textureView.width, y / textureView.height)

        focusRing.animate().cancel()
        focusRing.x = textureView.x + x - focusRing.width / 2f
        focusRing.y = textureView.y + y - focusRing.height / 2f
        focusRing.alpha = 1f
        focusRing.animate().alpha(0f).setStartDelay(900).setDuration(400).start()
    }

    private fun toast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}
