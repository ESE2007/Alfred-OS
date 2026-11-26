package com.camaraauto2

import android.annotation.SuppressLint
import android.content.ContentValues
import android.content.Context
import android.graphics.ImageFormat
import android.graphics.Rect
import android.graphics.SurfaceTexture
import android.hardware.camera2.CameraCaptureSession
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraDevice
import android.hardware.camera2.CameraManager
import android.hardware.camera2.CaptureFailure
import android.hardware.camera2.CaptureRequest
import android.hardware.camera2.CaptureResult
import android.hardware.camera2.TotalCaptureResult
import android.hardware.camera2.params.MeteringRectangle
import android.hardware.camera2.params.OutputConfiguration
import android.hardware.camera2.params.SessionConfiguration
import android.media.ImageReader
import android.os.Handler
import android.os.HandlerThread
import android.os.Looper
import android.os.SystemClock
import android.provider.MediaStore
import android.util.Log
import android.util.Size
import android.view.Surface
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.Executor
import java.util.concurrent.Executors
import kotlin.math.ln
import kotlin.math.min

/** Resultado de una captura, ya listo para mostrar al usuario. */
data class Outcome(val ok: Boolean, val message: String)

/**
 * Maneja la cámara trasera con Camera2. Todas las operaciones de cámara corren en un hilo propio;
 * los avisos a la interfaz llegan siempre en el hilo principal.
 */
class CameraEngine(
    private val context: Context,
    private val listener: Listener
) {

    interface Listener {
        fun onReady()
        fun onError(message: String)
    }

    companion object {
        private const val TAG = "CamaraAuto2"
        private const val CAPTURE_TIMEOUT_MS = 45_000L
    }

    // Estado que la interfaz puede leer
    @Volatile var measuredEv100 = Float.NaN
        private set
    @Volatile var evIndex = 0
        private set
    @Volatile var zoom = 1f
        private set
    var evStep = 0f
        private set
    var zoomMin = 1f
        private set
    var zoomMax = 1f
        private set
    lateinit var previewSize: Size
        private set

    private var evMin = 0
    private var evMax = 0

    private val main = Handler(Looper.getMainLooper())
    private val thread = HandlerThread("cam2-engine").apply { start() }
    private val handler = Handler(thread.looper)
    private val executor = Executor { handler.post(it) }
    private val saver = Executors.newSingleThreadExecutor()

    private val cm = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
    private lateinit var cameraId: String
    private lateinit var chars: CameraCharacteristics
    private lateinit var jpegSize: Size
    private var reqKeys: Map<String, CaptureRequest.Key<*>> = emptyMap()
    private var sensorOrientation = 90
    private var activeArray = Rect(0, 0, 4000, 3000)

    private var texture: SurfaceTexture? = null
    private var camera: CameraDevice? = null
    private var session: CameraCaptureSession? = null
    private var reader: ImageReader? = null
    private var previewSurface: Surface? = null

    @Volatile private var regions: Array<MeteringRectangle>? = null
    @Volatile private var closed = false
    @Volatile private var capturing = false
    private var pending: Pending? = null
    private val clearRegions = Runnable {
        regions = null
        updatePreview()
    }
    private val captureTimeout = Runnable {
        val p = pending ?: return@Runnable
        pending = null
        capturing = false
        main.post { p.callback(Outcome(false, "La captura tardó demasiado y se canceló")) }
    }

    private class Pending(
        val requested: CaptureMode,
        val applied: CaptureMode,
        val warning: String?,
        val callback: (Outcome) -> Unit,
        val startMs: Long
    ) {
        var result: TotalCaptureResult? = null
        var bytes: ByteArray? = null
    }

    // ------------------------------------------------------------------ Preparación y apertura

    /** Lee las características de la cámara trasera y devuelve el tamaño de vista previa (4:3). */
    fun prepare(): Size {
        cameraId = cm.cameraIdList.first {
            cm.getCameraCharacteristics(it).get(CameraCharacteristics.LENS_FACING) ==
                CameraCharacteristics.LENS_FACING_BACK
        }
        chars = cm.getCameraCharacteristics(cameraId)
        reqKeys = chars.availableCaptureRequestKeys.associateBy { it.name }
        sensorOrientation = chars.get(CameraCharacteristics.SENSOR_ORIENTATION) ?: 90
        activeArray = chars.get(CameraCharacteristics.SENSOR_INFO_ACTIVE_ARRAY_SIZE) ?: activeArray

        evStep = chars.get(CameraCharacteristics.CONTROL_AE_COMPENSATION_STEP)?.toFloat() ?: 0f
        chars.get(CameraCharacteristics.CONTROL_AE_COMPENSATION_RANGE)?.let {
            evMin = it.lower
            evMax = it.upper
        }
        chars.get(CameraCharacteristics.CONTROL_ZOOM_RATIO_RANGE)?.let {
            zoomMin = it.lower
            zoomMax = it.upper
        }

        val map = chars.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)!!
        val jpegSizes = map.getOutputSizes(ImageFormat.JPEG)
        jpegSize = jpegSizes.filter { it.width * 3 == it.height * 4 }
            .maxByOrNull { it.width * it.height } ?: jpegSizes.maxByOrNull { it.width * it.height }!!
        val prevSizes = map.getOutputSizes(SurfaceTexture::class.java)
        previewSize = prevSizes.filter { it.width * 3 == it.height * 4 && it.width <= 1600 }
            .maxByOrNull { it.width * it.height } ?: prevSizes.minByOrNull { it.width * it.height }!!
        return previewSize
    }

    @SuppressLint("MissingPermission")
    fun open(surfaceTexture: SurfaceTexture) {
        texture = surfaceTexture
        cm.openCamera(cameraId, executor, object : CameraDevice.StateCallback() {
            override fun onOpened(c: CameraDevice) {
                if (closed) {
                    c.close()
                    return
                }
                camera = c
                createSession()
            }

            override fun onDisconnected(c: CameraDevice) {
                c.close()
                camera = null
                if (!closed) main.post { listener.onError("La cámara se desconectó") }
            }

            override fun onError(c: CameraDevice, error: Int) {
                c.close()
                camera = null
                if (!closed) main.post { listener.onError("Error de cámara (código $error)") }
            }
        })
    }

    private fun createSession() {
        val cam = camera ?: return
        val tex = texture ?: return
        try {
            tex.setDefaultBufferSize(previewSize.width, previewSize.height)
            val preview = Surface(tex)
            previewSurface = preview

            val imageReader = ImageReader.newInstance(jpegSize.width, jpegSize.height, ImageFormat.JPEG, 3)
            imageReader.setOnImageAvailableListener({ r ->
                r.acquireNextImage()?.let { img ->
                    try {
                        val buf = img.planes[0].buffer
                        val bytes = ByteArray(buf.remaining())
                        buf.get(bytes)
                        onImage(bytes)
                    } finally {
                        img.close()
                    }
                }
            }, handler)
            reader = imageReader

            val outputs = listOf(OutputConfiguration(preview), OutputConfiguration(imageReader.surface))
            val config = SessionConfiguration(
                SessionConfiguration.SESSION_REGULAR,
                outputs,
                executor,
                object : CameraCaptureSession.StateCallback() {
                    override fun onConfigured(s: CameraCaptureSession) {
                        if (closed) {
                            s.close()
                            return
                        }
                        session = s
                        updatePreview()
                        main.post { listener.onReady() }
                    }

                    override fun onConfigureFailed(s: CameraCaptureSession) {
                        if (!closed) main.post { listener.onError("No se pudo configurar la cámara") }
                    }
                }
            )
            cam.createCaptureSession(config)
        } catch (e: Exception) {
            Log.e(TAG, "createSession", e)
            main.post { listener.onError("Error al iniciar la cámara: ${e.message}") }
        }
    }

    fun close() {
        closed = true
        handler.removeCallbacksAndMessages(null)
        try { session?.close() } catch (e: Throwable) { Log.w(TAG, e) }
        try { camera?.close() } catch (e: Throwable) { Log.w(TAG, e) }
        try { reader?.close() } catch (e: Throwable) { Log.w(TAG, e) }
        try { previewSurface?.release() } catch (e: Throwable) { Log.w(TAG, e) }
        session = null
        camera = null
        reader = null
        previewSurface = null
        thread.quitSafely()
        saver.shutdown()
    }

    // ------------------------------------------------------------------ Vista previa

    private val previewCallback = object : CameraCaptureSession.CaptureCallback() {
        override fun onCaptureCompleted(
            session: CameraCaptureSession,
            request: CaptureRequest,
            result: TotalCaptureResult
        ) {
            val iso = result.get(CaptureResult.SENSOR_SENSITIVITY) ?: return
            val expNs = result.get(CaptureResult.SENSOR_EXPOSURE_TIME) ?: return
            val aperture = result.get(CaptureResult.LENS_APERTURE) ?: 1.8f
            if (iso <= 0 || expNs <= 0L) return
            val seconds = expNs / 1e9
            // Brillo real de la escena (EV a ISO 100)
            val ev = ln((aperture * aperture / seconds) * (100.0 / iso)) / ln(2.0)
            measuredEv100 = ev.toFloat()
        }
    }

    private fun applyCommon(b: CaptureRequest.Builder) {
        b.set(CaptureRequest.CONTROL_MODE, CaptureRequest.CONTROL_MODE_AUTO)
        b.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
        b.set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON)
        b.set(CaptureRequest.CONTROL_AE_EXPOSURE_COMPENSATION, evIndex)
        b.set(CaptureRequest.CONTROL_ZOOM_RATIO, zoom)
        regions?.let {
            b.set(CaptureRequest.CONTROL_AF_REGIONS, it)
            b.set(CaptureRequest.CONTROL_AE_REGIONS, it)
        }
    }

    private fun updatePreview() {
        val cam = camera ?: return
        val sess = session ?: return
        val surface = previewSurface ?: return
        try {
            val b = cam.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW)
            b.addTarget(surface)
            applyCommon(b)
            sess.setRepeatingRequest(b.build(), previewCallback, handler)
        } catch (e: Exception) {
            Log.w(TAG, "updatePreview", e)
        }
    }

    // ------------------------------------------------------------------ Controles

    fun setEvIndex(index: Int) {
        evIndex = index.coerceIn(evMin, evMax)
        handler.post { updatePreview() }
    }

    fun setZoom(ratio: Float) {
        zoom = ratio.coerceIn(zoomMin, zoomMax)
        handler.post { updatePreview() }
    }

    /** nx, ny: posición del toque, de 0 a 1, sobre la vista previa vertical. */
    fun focusAt(nx: Float, ny: Float) {
        val w = activeArray.width()
        val h = activeArray.height()
        val z = zoom
        val visW = w / z
        val visH = h / z

        // La imagen del sensor está girada respecto a la pantalla: se convierte el toque a coordenadas del sensor
        val u: Float
        val v: Float
        when (sensorOrientation) {
            90 -> {
                u = w / 2f + (ny - 0.5f) * visW
                v = h / 2f + (0.5f - nx) * visH
            }
            270 -> {
                u = w / 2f + (0.5f - ny) * visW
                v = h / 2f + (nx - 0.5f) * visH
            }
            else -> return
        }

        val half = (min(w, h) * 0.06f / z).toInt().coerceAtLeast(20)
        val x0 = (u - half).toInt().coerceIn(0, w - 2 * half) + activeArray.left
        val y0 = (v - half).toInt().coerceIn(0, h - 2 * half) + activeArray.top
        val rect = MeteringRectangle(x0, y0, 2 * half, 2 * half, MeteringRectangle.METERING_WEIGHT_MAX - 1)
        regions = arrayOf(rect)

        handler.post {
            updatePreview()
            triggerAutofocus()
            handler.removeCallbacks(clearRegions)
            handler.postDelayed(clearRegions, 4000)
        }
    }

    private fun triggerAutofocus() {
        val cam = camera ?: return
        val sess = session ?: return
        val surface = previewSurface ?: return
        try {
            val b = cam.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW)
            b.addTarget(surface)
            applyCommon(b)
            b.set(CaptureRequest.CONTROL_AF_TRIGGER, CaptureRequest.CONTROL_AF_TRIGGER_START)
            sess.capture(b.build(), null, handler)
        } catch (e: Exception) {
            Log.w(TAG, "triggerAutofocus", e)
        }
    }

    // ------------------------------------------------------------------ Captura

    /**
     * Toma una foto en el modo pedido. El resultado llega en el hilo principal.
     * deviceOrientation: grados del sensor de orientación del teléfono (0 a 359).
     */
    fun capture(mode: CaptureMode, deviceOrientation: Int, callback: (Outcome) -> Unit) {
        handler.post { doCapture(mode, deviceOrientation, callback) }
    }

    private fun doCapture(mode: CaptureMode, deviceOrientation: Int, callback: (Outcome) -> Unit) {
        val cam = camera
        val sess = session
        val rd = reader
        if (cam == null || sess == null || rd == null) {
            main.post { callback(Outcome(false, "La cámara no está lista")) }
            return
        }
        if (capturing) return
        capturing = true

        try {
            val b = cam.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE)
            b.addTarget(rd.surface)
            applyCommon(b)
            b.set(CaptureRequest.JPEG_QUALITY, 100.toByte())
            b.set(CaptureRequest.JPEG_ORIENTATION, jpegOrientation(deviceOrientation))

            var applied = CaptureMode.NORMAL
            var warning: String? = null
            val keyName = mode.keyName
            if (keyName != null) {
                val key = reqKeys[keyName]
                if (key == null) {
                    warning = "este teléfono no tiene el modo ${mode.label}; se usó NORMAL"
                } else if (!setVendor(b, key, 1)) {
                    warning = "no se pudo activar el modo ${mode.label}; se usó NORMAL"
                } else {
                    applied = mode
                }
            }

            pending = Pending(mode, applied, warning, callback, SystemClock.elapsedRealtime())
            sess.capture(b.build(), captureCallback, handler)
            handler.postDelayed(captureTimeout, CAPTURE_TIMEOUT_MS)
        } catch (e: Exception) {
            Log.e(TAG, "doCapture", e)
            pending = null
            capturing = false
            main.post { callback(Outcome(false, "Error al capturar: ${e.message}")) }
        }
    }

    private val captureCallback = object : CameraCaptureSession.CaptureCallback() {
        override fun onCaptureCompleted(
            session: CameraCaptureSession,
            request: CaptureRequest,
            result: TotalCaptureResult
        ) {
            pending?.result = result
            tryFinish()
        }

        override fun onCaptureFailed(
            session: CameraCaptureSession,
            request: CaptureRequest,
            failure: CaptureFailure
        ) {
            val p = pending ?: return
            pending = null
            capturing = false
            handler.removeCallbacks(captureTimeout)
            main.post { p.callback(Outcome(false, "Falló la captura (razón ${failure.reason})")) }
        }
    }

    private fun onImage(bytes: ByteArray) {
        val p = pending ?: return
        p.bytes = bytes
        tryFinish()
    }

    /** La captura termina cuando llegaron tanto el resultado como la imagen (en cualquier orden). */
    private fun tryFinish() {
        val p = pending ?: return
        val bytes = p.bytes ?: return
        val result = p.result ?: return
        pending = null
        handler.removeCallbacks(captureTimeout)

        val seconds = (SystemClock.elapsedRealtime() - p.startMs) / 1000f
        val keyName = p.applied.keyName
        val echoed = keyName == null || result.keys.any { it.name == keyName }

        try {
            saver.execute {
                val saved = save(bytes, p.applied)
                capturing = false
                val message = if (!saved) {
                    "No se pudo guardar la foto"
                } else {
                    buildString {
                        append(String.format(Locale.US, "Foto guardada · %s · %.1f s", p.applied.label, seconds))
                        p.warning?.let { append("\n($it)") }
                        if (!echoed) append("\n(la cámara no confirmó el modo)")
                    }
                }
                main.post { p.callback(Outcome(saved, message)) }
            }
        } catch (e: Exception) {
            capturing = false
            main.post { p.callback(Outcome(false, "No se pudo guardar la foto")) }
        }
    }

    /**
     * Las claves del fabricante casi siempre son arreglos: se prueba cada formato hasta que uno sea aceptado.
     */
    private fun setVendor(builder: CaptureRequest.Builder, key: CaptureRequest.Key<*>, value: Int): Boolean {
        @Suppress("UNCHECKED_CAST")
        val k = key as CaptureRequest.Key<Any>
        val attempts = listOf<Any>(
            intArrayOf(value),
            byteArrayOf(value.toByte()),
            value,
            longArrayOf(value.toLong())
        )
        for (candidate in attempts) {
            try {
                builder.set(k, candidate)
                return true
            } catch (t: Throwable) {
                // probar el siguiente formato
            }
        }
        return false
    }

    private fun jpegOrientation(deviceOrientation: Int): Int {
        val d = (deviceOrientation + 45) / 90 * 90
        return (sensorOrientation + d + 360) % 360
    }

    private fun save(bytes: ByteArray, mode: CaptureMode): Boolean {
        return try {
            val stamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
            val modeTag = mode.label.replace(' ', '_').replace('Ú', 'U')
            val values = ContentValues().apply {
                put(MediaStore.MediaColumns.DISPLAY_NAME, "IMG_${stamp}_$modeTag")
                put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg")
                put(MediaStore.MediaColumns.RELATIVE_PATH, "Pictures/CamaraAuto2")
            }
            val uri = context.contentResolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
                ?: return false
            context.contentResolver.openOutputStream(uri)?.use { it.write(bytes) } ?: return false
            true
        } catch (e: Throwable) {
            Log.e(TAG, "save", e)
            false
        }
    }
}
