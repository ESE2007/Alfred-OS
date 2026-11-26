package com.camaralab

import android.annotation.SuppressLint
import android.content.ContentValues
import android.content.Context
import android.graphics.BitmapFactory
import android.graphics.ImageFormat
import android.graphics.SurfaceTexture
import android.hardware.camera2.CameraCaptureSession
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraDevice
import android.hardware.camera2.CameraManager
import android.hardware.camera2.CaptureFailure
import android.hardware.camera2.CaptureRequest
import android.hardware.camera2.CaptureResult
import android.hardware.camera2.TotalCaptureResult
import android.hardware.camera2.params.OutputConfiguration
import android.hardware.camera2.params.SessionConfiguration
import android.os.Build
import android.os.Handler
import android.os.HandlerThread
import android.os.SystemClock
import android.provider.MediaStore
import android.view.Surface
import java.util.Locale
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executor
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit
import kotlin.math.abs

/** Una prueba: poner una clave del fabricante con distintos valores enteros. */
data class VendorTest(val key: String, val values: List<Int>, val what: String)

/** Resultado de una captura. */
data class Record(
    val label: String,
    val error: String? = null,
    val ms: Long = 0,
    val bytes: Int = 0,
    val mean: Float = 0f,
    val dark: Float = 0f,
    val bright: Float = 0f,
    val detail: Float = 0f,
    val vendor: Map<String, String> = emptyMap(),
    val changes: List<String> = emptyList(),
    val notable: List<String> = emptyList()
)

class CameraLab(
    private val context: Context,
    private val texture: SurfaceTexture,
    private val onLog: (String) -> Unit
) {

    @Volatile
    var cancelled = false

    @Volatile
    private var disconnected = false

    private val camThread = HandlerThread("lab-cam").apply { start() }
    private val camHandler = Handler(camThread.looper)
    private val camExecutor = Executor { camHandler.post(it) }

    private var camera: CameraDevice? = null
    private var session: CameraCaptureSession? = null
    private var reader: ImageReader2? = null
    private var previewSurface: Surface? = null
    private lateinit var chars: CameraCharacteristics
    private var reqKeys: Map<String, CaptureRequest.Key<*>> = emptyMap()
    private val imageQueue = LinkedBlockingQueue<ByteArray>()
    private var counter = 0

    // Claves que se prueban. Los valores son conjeturas: lo que se mide es si algo cambia.
    private val tests = listOf(
        VendorTest("com.mediatek.mfnrfeature.mfbmode", listOf(0, 1, 2, 3), "MediaTek: reducción de ruido con varias fotos"),
        VendorTest("com.mediatek.mfnrfeature.aismode", listOf(0, 1), "MediaTek: variante AIS de varias fotos"),
        VendorTest("com.mediatek.hdrfeature.hdrMode", listOf(0, 1, 2, 3, 4), "MediaTek: modo HDR"),
        VendorTest("com.mediatek.nrfeature.3dnrmode", listOf(0, 1), "MediaTek: reducción de ruido 3D"),
        VendorTest("com.mediatek.control.capture.singleYuvNr.mode", listOf(0, 1), "MediaTek: reducción de ruido de un cuadro"),
        VendorTest("com.mediatek.control.capture.highQualityYuv", listOf(0, 1), "MediaTek: YUV de alta calidad"),
        VendorTest("com.mediatek.control.capture.zsl.mode", listOf(0, 1), "MediaTek: captura sin retardo (ZSL)"),
        VendorTest("com.transsion.hdrMode", listOf(0, 1, 2), "Infinix: modo HDR"),
        VendorTest("com.transsion.LowlightHdrMode", listOf(0, 1), "Infinix: HDR con poca luz"),
        VendorTest("com.transsion.lowLightMode", listOf(0, 1), "Infinix: modo poca luz"),
        VendorTest("com.transsion.denoiseMode", listOf(0, 1, 2), "Infinix: reducción de ruido"),
        VendorTest("com.transsion.supernightfilter", listOf(0, 1), "Infinix: filtro Super Night"),
        VendorTest("com.transsion.nighthawkmode", listOf(0, 1), "Infinix: Nighthawk (noche)"),
        VendorTest("com.transsion.camkitNightMode", listOf(0, 1), "Infinix: modo noche"),
        VendorTest("com.transsion.superAIRawMode", listOf(0, 1), "Infinix: super RAW con IA"),
        VendorTest("com.transsion.megSuperlowlightMode", listOf(0, 1), "Infinix: super poca luz"),
        VendorTest("com.transsion.megSuperresolutionMode", listOf(0, 1), "Infinix: super resolución"),
        VendorTest("com.transsion.enhanceImageQuality", listOf(0, 1), "Infinix: mejora de calidad de imagen"),
        VendorTest("com.transsion.dromode", listOf(0, 1), "Infinix: rango dinámico (DRO)"),
        VendorTest("com.transsion.deFlareMode", listOf(0, 1), "Infinix: reducción de destellos")
    )

    // ------------------------------------------------------------------ Ejecución

    /** Corre todas las pruebas y devuelve el informe. Bloquea: llamar desde un hilo de fondo. */
    fun run(): String {
        val baselines = mutableListOf<Record>()
        val results = mutableListOf<Pair<VendorTest, List<Pair<Int, Record>>>>()
        var fatal: String? = null
        val skipped = mutableListOf<String>()

        try {
            openCamera()
            startSession()
            onLog("Calentando cámara (2 s)…")
            Thread.sleep(2000)

            onLog("Foto base 1…")
            baselines += captureOne("BASE-1", null, null)
            Thread.sleep(500)
            onLog("Foto base 2…")
            baselines += captureOne("BASE-2", null, null)

            val b1 = baselines[0]
            val b2 = baselines[1]
            val noisy = if (b1.error == null && b2.error == null) {
                (b1.vendor.keys + b2.vendor.keys).filter { b1.vendor[it] != b2.vendor[it] }.toSet()
            } else emptySet()

            val ok = baselines.filter { it.error == null }
            val avgBytes = ok.map { it.bytes }.average()
            val avgDark = ok.map { it.dark.toDouble() }.average()
            val avgBright = ok.map { it.bright.toDouble() }.average()
            val avgDetail = ok.map { it.detail.toDouble() }.average()
            val avgMs = ok.map { it.ms.toDouble() }.average()

            val total = tests.sumOf { it.values.size }
            var done = 0

            for (test in tests) {
                if (cancelled || disconnected) break
                if (!reqKeys.containsKey(test.key)) {
                    skipped += test.key
                    done += test.values.size
                    continue
                }
                val rows = mutableListOf<Pair<Int, Record>>()
                for (v in test.values) {
                    if (cancelled || disconnected) break
                    done++
                    onLog("[$done/$total] ${test.key.substringAfterLast('.')} = $v")
                    var rec = captureOne(test.key.substringAfterLast('.') + "=" + v, test.key, v)
                    if (rec.error == null && ok.isNotEmpty()) {
                        rec = annotate(rec, b1, noisy, avgBytes, avgDark, avgBright, avgDetail, avgMs)
                    }
                    rows += v to rec
                    Thread.sleep(600)
                }
                results += test to rows
            }
            if (disconnected) fatal = "La cámara se desconectó durante las pruebas (informe parcial)."
            if (cancelled) fatal = "Pruebas detenidas por el usuario (informe parcial)."
        } catch (t: Throwable) {
            fatal = "Error general: $t"
        } finally {
            close()
        }

        return buildReport(baselines, results, skipped, fatal)
    }

    private fun annotate(
        rec: Record,
        base: Record,
        noisy: Set<String>,
        avgBytes: Double,
        avgDark: Double,
        avgBright: Double,
        avgDetail: Double,
        avgMs: Double
    ): Record {
        val changes = mutableListOf<String>()
        for (k in (rec.vendor.keys + base.vendor.keys)) {
            if (k in noisy) continue
            val a = base.vendor[k]
            val b = rec.vendor[k]
            if (a != b) changes += "$k: ${a ?: "-"} -> ${b ?: "-"}"
        }
        val notable = mutableListOf<String>()
        if (changes.isNotEmpty()) notable += "cambian ${changes.size} claves de resultado"
        if (avgBytes > 0 && abs(rec.bytes - avgBytes) / avgBytes > 0.12) {
            notable += "tamaño JPEG ${pct(rec.bytes.toDouble(), avgBytes)}"
        }
        if (avgDetail > 0 && abs(rec.detail - avgDetail) / avgDetail > 0.15) {
            notable += "detalle ${pct(rec.detail.toDouble(), avgDetail)}"
        }
        if (abs(rec.dark - avgDark) > 3) notable += "sombras ${fmt1(avgDark)}% -> ${fmt1(rec.dark.toDouble())}%"
        if (abs(rec.bright - avgBright) > 3) notable += "luces quemadas ${fmt1(avgBright)}% -> ${fmt1(rec.bright.toDouble())}%"
        if (avgMs > 0 && rec.ms > avgMs * 2) notable += "tarda ${pct(rec.ms.toDouble(), avgMs)}"
        return rec.copy(changes = changes, notable = notable)
    }

    private fun pct(value: Double, base: Double): String {
        val d = (value - base) / base * 100
        return String.format(Locale.US, "%+.0f%%", d)
    }

    private fun fmt1(v: Double) = String.format(Locale.US, "%.1f", v)

    // ------------------------------------------------------------------ Cámara

    @SuppressLint("MissingPermission")
    private fun openCamera() {
        val cm = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
        val id = "0"
        chars = cm.getCameraCharacteristics(id)
        reqKeys = chars.availableCaptureRequestKeys.associateBy { it.name }

        val latch = CountDownLatch(1)
        var error: String? = null
        cm.openCamera(id, camExecutor, object : CameraDevice.StateCallback() {
            override fun onOpened(c: CameraDevice) {
                camera = c
                latch.countDown()
            }

            override fun onDisconnected(c: CameraDevice) {
                c.close()
                camera = null
                disconnected = true
                latch.countDown()
            }

            override fun onError(c: CameraDevice, e: Int) {
                c.close()
                camera = null
                disconnected = true
                error = "código $e"
                latch.countDown()
            }
        })
        if (!latch.await(10, TimeUnit.SECONDS) || camera == null) {
            throw IllegalStateException("No se pudo abrir la cámara ${error ?: ""}")
        }
    }

    private fun startSession() {
        val map = chars.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)!!
        val jpegSizes = map.getOutputSizes(ImageFormat.JPEG)
        val jpegSize = jpegSizes.filter { it.width * 3 == it.height * 4 }
            .maxByOrNull { it.width * it.height } ?: jpegSizes.maxByOrNull { it.width * it.height }!!
        val prevSizes = map.getOutputSizes(SurfaceTexture::class.java)
        val prevSize = prevSizes.filter { it.width * 3 == it.height * 4 && it.width <= 1600 }
            .maxByOrNull { it.width * it.height } ?: prevSizes.minByOrNull { it.width * it.height }!!

        texture.setDefaultBufferSize(prevSize.width, prevSize.height)
        val preview = Surface(texture)
        previewSurface = preview

        val imgReader = android.media.ImageReader.newInstance(jpegSize.width, jpegSize.height, ImageFormat.JPEG, 3)
        imgReader.setOnImageAvailableListener({ r ->
            val img = r.acquireNextImage()
            if (img != null) {
                try {
                    val buf = img.planes[0].buffer
                    val bytes = ByteArray(buf.remaining())
                    buf.get(bytes)
                    imageQueue.offer(bytes)
                } finally {
                    img.close()
                }
            }
        }, camHandler)
        reader = ImageReader2(imgReader)

        val outputs = listOf(OutputConfiguration(preview), OutputConfiguration(imgReader.surface))
        val latch = CountDownLatch(1)
        var configured = false
        val config = SessionConfiguration(
            SessionConfiguration.SESSION_REGULAR,
            outputs,
            camExecutor,
            object : CameraCaptureSession.StateCallback() {
                override fun onConfigured(s: CameraCaptureSession) {
                    session = s
                    configured = true
                    latch.countDown()
                }

                override fun onConfigureFailed(s: CameraCaptureSession) {
                    latch.countDown()
                }
            }
        )
        camera!!.createCaptureSession(config)
        if (!latch.await(10, TimeUnit.SECONDS) || !configured) {
            throw IllegalStateException("No se pudo configurar la sesión de cámara")
        }

        val pb = camera!!.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW)
        pb.addTarget(preview)
        pb.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
        session!!.setRepeatingRequest(pb.build(), null, camHandler)
        onLog("Cámara lista: JPEG ${jpegSize.width}x${jpegSize.height}")
    }

    private class ImageReader2(val reader: android.media.ImageReader) {
        val surface: Surface get() = reader.surface
    }

    private fun close() {
        try { session?.close() } catch (e: Throwable) {}
        try { camera?.close() } catch (e: Throwable) {}
        try { reader?.reader?.close() } catch (e: Throwable) {}
        try { previewSurface?.release() } catch (e: Throwable) {}
        camThread.quitSafely()
    }

    // ------------------------------------------------------------------ Captura

    private fun captureOne(label: String, keyName: String?, value: Int?): Record {
        val cam = camera ?: return Record(label, error = "cámara no disponible")
        val sess = session ?: return Record(label, error = "sin sesión")
        val surface = reader?.surface ?: return Record(label, error = "sin lector de imágenes")

        try {
            val builder = cam.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE)
            builder.addTarget(surface)
            builder.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
            builder.set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON)
            builder.set(CaptureRequest.JPEG_QUALITY, 100.toByte())

            if (keyName != null) {
                val key = reqKeys[keyName] ?: return Record(label, error = "la clave no existe")
                try {
                    @Suppress("UNCHECKED_CAST")
                    builder.set(key as CaptureRequest.Key<Any>, value!!)
                } catch (t: Throwable) {
                    return Record(label, error = "la clave no acepta un entero (${t.javaClass.simpleName})")
                }
            }

            imageQueue.clear()
            val holder = arrayOfNulls<TotalCaptureResult>(1)
            val done = CountDownLatch(1)
            var failure: String? = null
            val t0 = SystemClock.elapsedRealtime()

            sess.capture(builder.build(), object : CameraCaptureSession.CaptureCallback() {
                override fun onCaptureCompleted(
                    session: CameraCaptureSession,
                    request: CaptureRequest,
                    result: TotalCaptureResult
                ) {
                    holder[0] = result
                    done.countDown()
                }

                override fun onCaptureFailed(
                    session: CameraCaptureSession,
                    request: CaptureRequest,
                    f: CaptureFailure
                ) {
                    failure = "falló la captura (razón ${f.reason})"
                    done.countDown()
                }
            }, camHandler)

            if (!done.await(40, TimeUnit.SECONDS)) return Record(label, error = "tiempo agotado esperando el resultado")
            failure?.let { return Record(label, error = it) }
            val bytes = imageQueue.poll(25, TimeUnit.SECONDS) ?: return Record(label, error = "no llegó la imagen")
            val ms = SystemClock.elapsedRealtime() - t0

            val stats = analyze(bytes)
            counter++
            save(bytes, String.format(Locale.US, "LAB_%02d_%s", counter, label.replace('=', '_')))

            return Record(
                label = label,
                ms = ms,
                bytes = bytes.size,
                mean = stats[0],
                dark = stats[1],
                bright = stats[2],
                detail = stats[3],
                vendor = vendorResult(holder[0]!!)
            )
        } catch (t: Throwable) {
            return Record(label, error = "excepción: ${t.javaClass.simpleName} ${t.message ?: ""}".trim())
        }
    }

    private fun vendorResult(result: CaptureResult): Map<String, String> {
        val map = sortedMapOf<String, String>()
        for (key in result.keys) {
            if (key.name.startsWith("android.")) continue
            map[key.name] = try {
                fmt(result.get(key))
            } catch (t: Throwable) {
                "error"
            }
        }
        return map
    }

    private fun fmt(v: Any?): String {
        val s = when (v) {
            null -> "null"
            is IntArray -> list(v.toList())
            is LongArray -> list(v.toList())
            is FloatArray -> list(v.toList())
            is DoubleArray -> list(v.toList())
            is ByteArray -> "bytes[${v.size}] #${v.contentHashCode()}"
            is Array<*> -> list(v.toList())
            else -> v.toString()
        }
        return if (s.length > 100) s.take(100) + "…" else s
    }

    private fun list(items: List<Any?>): String =
        items.take(12).joinToString(",", "[", if (items.size > 12) ",…]" else "]")

    /** Devuelve: brillo medio, % sombras, % luces quemadas, detalle (varianza del laplaciano). */
    private fun analyze(bytes: ByteArray): FloatArray {
        val opts = BitmapFactory.Options().apply { inSampleSize = 2 }
        val bmp = BitmapFactory.decodeByteArray(bytes, 0, bytes.size, opts)
            ?: return floatArrayOf(0f, 0f, 0f, 0f)
        val w = bmp.width
        val h = bmp.height
        val px = IntArray(w * h)
        bmp.getPixels(px, 0, w, 0, 0, w, h)
        bmp.recycle()

        val luma = FloatArray(w * h) { i ->
            val p = px[i]
            0.299f * ((p shr 16) and 0xFF) + 0.587f * ((p shr 8) and 0xFF) + 0.114f * (p and 0xFF)
        }
        var sum = 0.0
        var dark = 0
        var bright = 0
        for (v in luma) {
            sum += v
            if (v < 30) dark++
            if (v > 240) bright++
        }

        var lapSum = 0.0
        var lapSq = 0.0
        var n = 0
        for (y in h / 4 until 3 * h / 4) {
            for (x in w / 4 until 3 * w / 4) {
                val i = y * w + x
                val l = 4 * luma[i] - luma[i - 1] - luma[i + 1] - luma[i - w] - luma[i + w]
                lapSum += l
                lapSq += l * l
                n++
            }
        }
        val m = lapSum / n
        val variance = lapSq / n - m * m

        return floatArrayOf(
            (sum / luma.size).toFloat(),
            dark * 100f / luma.size,
            bright * 100f / luma.size,
            variance.toFloat()
        )
    }

    private fun save(bytes: ByteArray, name: String) {
        try {
            val values = ContentValues().apply {
                put(MediaStore.MediaColumns.DISPLAY_NAME, name)
                put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg")
                put(MediaStore.MediaColumns.RELATIVE_PATH, "Pictures/CamaraLab")
            }
            val uri = context.contentResolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values) ?: return
            context.contentResolver.openOutputStream(uri)?.use { it.write(bytes) }
        } catch (e: Throwable) {
            // si no se puede guardar, igual seguimos con las pruebas
        }
    }

    // ------------------------------------------------------------------ Informe

    private fun line(r: Record): String =
        if (r.error != null) {
            "${r.label}: ERROR - ${r.error}"
        } else {
            String.format(
                Locale.US,
                "%s: OK %.1f s | %.1f MB | brillo %.0f | sombras %.1f%% | quemado %.1f%% | detalle %.0f",
                r.label, r.ms / 1000.0, r.bytes / 1e6, r.mean, r.dark, r.bright, r.detail
            )
        }

    private fun buildReport(
        baselines: List<Record>,
        results: List<Pair<VendorTest, List<Pair<Int, Record>>>>,
        skipped: List<String>,
        fatal: String?
    ): String = buildString {
        appendLine("LABORATORIO DE CLAVES v1.0")
        appendLine("Dispositivo: ${Build.MANUFACTURER} ${Build.MODEL} | Android ${Build.VERSION.RELEASE} (SDK ${Build.VERSION.SDK_INT})")
        appendLine("Fotos guardadas en Imágenes/CamaraLab (LAB_nn_clave_valor.jpg) para compararlas a ojo.")
        fatal?.let { appendLine("\n!! $it") }

        appendLine("\n== FOTOS BASE (sin tocar nada) ==")
        baselines.forEach { appendLine(line(it)) }

        // Resumen de pruebas notables
        val notables = results.flatMap { (test, rows) ->
            rows.filter { it.second.notable.isNotEmpty() }.map { test to it }
        }
        appendLine("\n== RESUMEN: PRUEBAS QUE CAMBIARON ALGO ==")
        if (notables.isEmpty()) {
            appendLine("Ninguna prueba produjo un cambio claro.")
        } else {
            for ((test, row) in notables) {
                appendLine("* ${test.key.substringAfterLast('.')} = ${row.first}: ${row.second.notable.joinToString("; ")}")
            }
        }

        appendLine("\n== DETALLE DE CADA PRUEBA ==")
        for ((test, rows) in results) {
            appendLine("\n-- ${test.key} (${test.what}) --")
            for ((_, rec) in rows) {
                appendLine((if (rec.notable.isNotEmpty()) "* " else "  ") + line(rec))
                if (rec.changes.isNotEmpty()) {
                    rec.changes.take(8).forEach { appendLine("      $it") }
                    if (rec.changes.size > 8) appendLine("      … y ${rec.changes.size - 8} más")
                }
            }
        }

        if (skipped.isNotEmpty()) {
            appendLine("\n== CLAVES QUE ESTE TELÉFONO NO TIENE (omitidas) ==")
            skipped.forEach { appendLine("  $it") }
        }

        val b1 = baselines.firstOrNull { it.error == null }
        if (b1 != null) {
            appendLine("\n== VALORES QUE DEVUELVE LA CÁMARA EN LA FOTO BASE (claves del fabricante) ==")
            b1.vendor.forEach { (k, v) -> appendLine("  $k = $v") }
        }
    }
}
