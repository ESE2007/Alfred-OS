package com.camaraauto2

import android.annotation.SuppressLint
import android.content.ContentValues
import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.BitmapRegionDecoder
import android.graphics.ImageFormat
import android.graphics.Matrix
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
import androidx.exifinterface.media.ExifInterface
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.Executor
import java.util.concurrent.Executors
import kotlin.math.abs
import kotlin.math.ln
import kotlin.math.max
import kotlin.math.min

/** Resultado de guardar una foto, ya listo para mostrar al usuario. */
data class Outcome(val ok: Boolean, val message: String, val uri: String? = null)

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
        private const val PRECAPTURE_TIMEOUT_MS = 2_000L
        private const val NATIVE_RATIO = 4f / 3f
    }

    // Estado que la interfaz puede leer
    @Volatile var measuredEv100 = Float.NaN
        private set
    @Volatile var evIndex = 0
        private set
    @Volatile var zoom = 1f
        private set
    @Volatile var flashMode = FlashMode.OFF
        private set
    var hasFlash = false
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

    // Secuencia de pre-captura del flash
    private var precaptureDone: (() -> Unit)? = null
    private var sawPrecapture = false

    private val clearRegions = Runnable {
        regions = null
        updatePreview()
    }

    private val captureTimeout = Runnable {
        val p = pending ?: return@Runnable
        pending = null
        capturing = false
        main.post { p.onSaved(Outcome(false, "La captura tardó demasiado y se canceló")) }
    }

    private val precaptureTimeout = Runnable { finishPrecapture() }

    private class Pending(
        val requested: CaptureMode,
        val applied: CaptureMode,
        val warning: String?,
        val ratio: Float,
        val onProcessed: () -> Unit,
        val onSaved: (Outcome) -> Unit,
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
        hasFlash = chars.get(CameraCharacteristics.FLASH_INFO_AVAILABLE) == true

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

        // Foto: el mayor tamaño JPEG 4:3 que ofrece el teléfono
        val jpegSizes = map.getOutputSizes(ImageFormat.JPEG)
        jpegSize = jpegSizes.filter { it.width * 3 == it.height * 4 }
            .maxByOrNull { it.width * it.height } ?: jpegSizes.maxByOrNull { it.width * it.height }!!

        // Vista previa: liviana (hasta 1280 px) para dejar más recursos al procesamiento de la foto
        val prevSizes = map.getOutputSizes(SurfaceTexture::class.java)
        val prev43 = prevSizes.filter { it.width * 3 == it.height * 4 }
        previewSize = prev43.filter { it.width <= 1280 }.maxByOrNull { it.width * it.height }
            ?: prev43.filter { it.width <= 1600 }.maxByOrNull { it.width * it.height }
            ?: prevSizes.minByOrNull { it.width * it.height }!!
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
            // Secuencia de pre-captura del flash: se espera a que la exposición termine de ajustarse
            if (precaptureDone != null) {
                val state = result.get(CaptureResult.CONTROL_AE_STATE)
                if (state == CaptureResult.CONTROL_AE_STATE_PRECAPTURE) {
                    sawPrecapture = true
                } else if (sawPrecapture && state != null) {
                    finishPrecapture()
                }
            }

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

    /**
     * Parámetros comunes de vista previa y foto.
     * still/effective: para la foto, el flash AUTO solo actúa si el modo final es NORMAL.
     */
    private fun applyCommon(b: CaptureRequest.Builder, still: Boolean = false, effective: CaptureMode = CaptureMode.NORMAL) {
        b.set(CaptureRequest.CONTROL_MODE, CaptureRequest.CONTROL_MODE_AUTO)
        b.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
        b.set(CaptureRequest.CONTROL_AE_EXPOSURE_COMPENSATION, evIndex)
        b.set(CaptureRequest.CONTROL_ZOOM_RATIO, zoom)
        regions?.let {
            b.set(CaptureRequest.CONTROL_AF_REGIONS, it)
            b.set(CaptureRequest.CONTROL_AE_REGIONS, it)
        }

        var aeMode = CaptureRequest.CONTROL_AE_MODE_ON
        var flash = CaptureRequest.FLASH_MODE_OFF
        if (hasFlash) {
            when (flashMode) {
                FlashMode.OFF -> {}
                FlashMode.AUTO -> if (!still || effective == CaptureMode.NORMAL) {
                    aeMode = CaptureRequest.CONTROL_AE_MODE_ON_AUTO_FLASH
                }
                FlashMode.ON -> aeMode = CaptureRequest.CONTROL_AE_MODE_ON_ALWAYS_FLASH
                FlashMode.TORCH -> flash = CaptureRequest.FLASH_MODE_TORCH
            }
        }
        b.set(CaptureRequest.CONTROL_AE_MODE, aeMode)
        b.set(CaptureRequest.FLASH_MODE, flash)
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

    fun setFlash(mode: FlashMode) {
        flashMode = if (hasFlash) mode else FlashMode.OFF
        handler.post { updatePreview() }
    }

    /** nx, ny: posición del toque, de 0 a 1, sobre la imagen completa de la cámara (vertical). */
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
     * Toma una foto en el modo pedido.
     *  - ratio: proporción (lado largo / lado corto) de la foto final; 4/3 guarda la imagen sin recortar.
     *  - onProcessed: la cámara ya terminó; se puede volver a disparar (el guardado sigue en segundo plano).
     *  - onSaved: la foto ya está guardada (o hubo un error).
     * Ambos avisos llegan en el hilo principal.
     */
    fun capture(
        mode: CaptureMode,
        deviceOrientation: Int,
        ratio: Float,
        onProcessed: () -> Unit,
        onSaved: (Outcome) -> Unit
    ) {
        handler.post { doCapture(mode, deviceOrientation, ratio, onProcessed, onSaved) }
    }

    private fun doCapture(
        mode: CaptureMode,
        deviceOrientation: Int,
        ratio: Float,
        onProcessed: () -> Unit,
        onSaved: (Outcome) -> Unit
    ) {
        if (camera == null || session == null || reader == null) {
            main.post { onSaved(Outcome(false, "La cámara no está lista")) }
            return
        }
        if (capturing) return
        capturing = true

        // Con flash ON la foto se toma en modo NORMAL: los modos de varias fotos no se llevan bien con un destello
        var effective = mode
        var warning: String? = null
        if (hasFlash && flashMode == FlashMode.ON && mode != CaptureMode.NORMAL) {
            effective = CaptureMode.NORMAL
            warning = "con flash ON se usa el modo NORMAL"
        }

        val needsPrecapture = hasFlash && effective == CaptureMode.NORMAL &&
            (flashMode == FlashMode.AUTO || flashMode == FlashMode.ON)

        if (needsPrecapture) {
            startPrecapture { shoot(mode, effective, warning, deviceOrientation, ratio, onProcessed, onSaved) }
        } else {
            shoot(mode, effective, warning, deviceOrientation, ratio, onProcessed, onSaved)
        }
    }

    private fun startPrecapture(then: () -> Unit) {
        val cam = camera
        val sess = session
        val surface = previewSurface
        if (cam == null || sess == null || surface == null) {
            then()
            return
        }
        try {
            val b = cam.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW)
            b.addTarget(surface)
            applyCommon(b, still = true, effective = CaptureMode.NORMAL)
            b.set(
                CaptureRequest.CONTROL_AE_PRECAPTURE_TRIGGER,
                CaptureRequest.CONTROL_AE_PRECAPTURE_TRIGGER_START
            )
            sawPrecapture = false
            precaptureDone = then
            handler.postDelayed(precaptureTimeout, PRECAPTURE_TIMEOUT_MS)
            sess.capture(b.build(), null, handler)
        } catch (e: Exception) {
            Log.w(TAG, "startPrecapture", e)
            precaptureDone = null
            then()
        }
    }

    private fun finishPrecapture() {
        val done = precaptureDone ?: return
        precaptureDone = null
        handler.removeCallbacks(precaptureTimeout)
        done()
    }

    private fun shoot(
        requested: CaptureMode,
        effective: CaptureMode,
        initialWarning: String?,
        deviceOrientation: Int,
        ratio: Float,
        onProcessed: () -> Unit,
        onSaved: (Outcome) -> Unit
    ) {
        val cam = camera
        val sess = session
        val rd = reader
        if (cam == null || sess == null || rd == null) {
            capturing = false
            main.post { onSaved(Outcome(false, "La cámara no está lista")) }
            return
        }

        try {
            val b = cam.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE)
            b.addTarget(rd.surface)
            applyCommon(b, still = true, effective = effective)
            b.set(CaptureRequest.JPEG_QUALITY, 100.toByte())
            b.set(CaptureRequest.JPEG_ORIENTATION, jpegOrientation(deviceOrientation))

            var applied = CaptureMode.NORMAL
            var warning = initialWarning
            val keyName = effective.keyName
            if (keyName != null) {
                val key = reqKeys[keyName]
                if (key == null) {
                    warning = "este teléfono no tiene el modo ${effective.label}; se usó NORMAL"
                } else if (!setVendor(b, key, 1)) {
                    warning = "no se pudo activar el modo ${effective.label}; se usó NORMAL"
                } else {
                    applied = effective
                }
            }

            pending = Pending(requested, applied, warning, ratio, onProcessed, onSaved, SystemClock.elapsedRealtime())
            sess.capture(b.build(), captureCallback, handler)
            handler.postDelayed(captureTimeout, CAPTURE_TIMEOUT_MS)
        } catch (e: Exception) {
            Log.e(TAG, "shoot", e)
            pending = null
            capturing = false
            main.post { onSaved(Outcome(false, "Error al capturar: ${e.message}")) }
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
            main.post { p.onSaved(Outcome(false, "Falló la captura (razón ${failure.reason})")) }
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

        // La cámara ya está libre: se puede disparar de nuevo mientras esta foto se guarda
        capturing = false
        main.post { p.onProcessed() }

        try {
            saver.execute {
                val saved = saveFinal(bytes, p.applied, p.ratio)
                val message = if (saved.uri == null) {
                    "No se pudo guardar la foto"
                } else {
                    val mp = saved.width.toLong() * saved.height / 1e6
                    buildString {
                        append(
                            String.format(
                                Locale.US, "Foto guardada · %s · %.1f s\n%d×%d (%.1f MP)",
                                p.applied.label, seconds,
                                max(saved.width, saved.height), min(saved.width, saved.height), mp
                            )
                        )
                        p.warning?.let { append("\n($it)") }
                        saved.note?.let { append("\n($it)") }
                        if (!echoed) append("\n(la cámara no confirmó el modo)")
                    }
                }
                main.post { p.onSaved(Outcome(saved.uri != null, message, saved.uri)) }
            }
        } catch (e: Exception) {
            main.post { p.onSaved(Outcome(false, "No se pudo guardar la foto")) }
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

    // ------------------------------------------------------------------ Guardado y recorte

    private class SaveResult(val uri: String?, val width: Int, val height: Int, val note: String?)
    private class Cropped(val bytes: ByteArray, val width: Int, val height: Int)

    /**
     * 4:3 se guarda tal como sale de la cámara (máxima resolución, sin tocar).
     * Otros formatos se recortan del centro de esa misma imagen.
     */
    private fun saveFinal(bytes: ByteArray, mode: CaptureMode, ratio: Float): SaveResult {
        var data = bytes
        var width = 0
        var height = 0
        var note: String? = null

        if (abs(ratio - NATIVE_RATIO) > 0.02f) {
            val cropped = try {
                cropToRatio(bytes, ratio)
            } catch (t: Throwable) {
                Log.e(TAG, "cropToRatio", t)
                null
            }
            if (cropped != null) {
                data = cropped.bytes
                width = cropped.width
                height = cropped.height
            } else {
                note = "no se pudo recortar; se guardó en 4:3"
            }
        }

        if (width == 0) {
            val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
            BitmapFactory.decodeByteArray(data, 0, data.size, bounds)
            width = bounds.outWidth
            height = bounds.outHeight
        }

        return SaveResult(saveBytes(data, mode), width, height, note)
    }

    private fun exifRotation(bytes: ByteArray): Int {
        return try {
            val exif = ExifInterface(ByteArrayInputStream(bytes))
            when (exif.getAttributeInt(ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_NORMAL)) {
                ExifInterface.ORIENTATION_ROTATE_90 -> 90
                ExifInterface.ORIENTATION_ROTATE_180 -> 180
                ExifInterface.ORIENTATION_ROTATE_270 -> 270
                else -> 0
            }
        } catch (t: Throwable) {
            0
        }
    }

    /** Recorta del centro la proporción pedida (lado largo / lado corto) y deja la foto derecha. */
    private fun cropToRatio(bytes: ByteArray, ratio: Float): Cropped? {
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        BitmapFactory.decodeByteArray(bytes, 0, bytes.size, bounds)
        val w = bounds.outWidth
        val h = bounds.outHeight
        if (w <= 0 || h <= 0) return null

        val rotation = exifRotation(bytes)
        val sideways = rotation == 90 || rotation == 270
        val uw = if (sideways) h else w // ancho de la foto ya derecha
        val uh = if (sideways) w else h

        val desired = if (uw >= uh) ratio else 1f / ratio // ancho / alto
        var cw = uw.toFloat()
        var ch = cw / desired
        if (ch > uh) {
            ch = uh.toFloat()
            cw = ch * desired
        }
        val cwi = (cw.toInt() / 2) * 2
        val chi = (ch.toInt() / 2) * 2
        val x0 = (uw - cwi) / 2
        val y0 = (uh - chi) / 2
        val x1 = x0 + cwi
        val y1 = y0 + chi

        // Pasa el recorte de la foto derecha a coordenadas de la imagen tal como viene de la cámara
        val rect = when (rotation) {
            90 -> Rect(y0, h - x1, y1, h - x0)
            270 -> Rect(w - y1, x0, w - y0, x1)
            180 -> Rect(w - x1, h - y1, w - x0, h - y0)
            else -> Rect(x0, y0, x1, y1)
        }

        val decoder = BitmapRegionDecoder.newInstance(bytes, 0, bytes.size)
        var bmp: Bitmap = try {
            decoder.decodeRegion(rect, BitmapFactory.Options().apply { inPreferredConfig = Bitmap.Config.ARGB_8888 })
        } finally {
            decoder.recycle()
        }

        if (rotation != 0) {
            val m = Matrix().apply { postRotate(rotation.toFloat()) }
            val rotated = Bitmap.createBitmap(bmp, 0, 0, bmp.width, bmp.height, m, true)
            bmp.recycle()
            bmp = rotated
        }

        val out = ByteArrayOutputStream(8 * 1024 * 1024)
        bmp.compress(Bitmap.CompressFormat.JPEG, 100, out)
        val result = Cropped(out.toByteArray(), bmp.width, bmp.height)
        bmp.recycle()
        return result
    }

    private fun saveBytes(bytes: ByteArray, mode: CaptureMode): String? {
        return try {
            val stamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
            val modeTag = mode.label.replace(' ', '_').replace('Ú', 'U')
            val values = ContentValues().apply {
                put(MediaStore.MediaColumns.DISPLAY_NAME, "IMG_${stamp}_$modeTag")
                put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg")
                put(MediaStore.MediaColumns.RELATIVE_PATH, "Pictures/CamaraAuto2")
                put(MediaStore.Images.Media.DATE_TAKEN, System.currentTimeMillis())
                put(MediaStore.MediaColumns.IS_PENDING, 1)
            }
            val resolver = context.contentResolver
            val uri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values) ?: return null
            val stream = resolver.openOutputStream(uri)
            if (stream == null) {
                resolver.delete(uri, null, null)
                return null
            }
            stream.use { it.write(bytes) }
            val done = ContentValues().apply { put(MediaStore.MediaColumns.IS_PENDING, 0) }
            resolver.update(uri, done, null, null)
            uri.toString()
        } catch (e: Throwable) {
            Log.e(TAG, "saveBytes", e)
            null
        }
    }
}
