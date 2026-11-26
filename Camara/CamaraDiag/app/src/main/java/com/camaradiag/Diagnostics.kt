package com.camaradiag

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.ImageFormat
import android.graphics.SurfaceTexture
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraManager
import android.os.Build
import android.provider.MediaStore
import android.util.Size
import androidx.camera.core.CameraSelector
import androidx.camera.extensions.ExtensionMode
import androidx.camera.extensions.ExtensionsManager
import androidx.camera.lifecycle.ProcessCameraProvider
import java.util.Locale

data class Camera2Result(val summary: String, val details: String)

object Diagnostics {

    private val capNames = mapOf(
        0 to "BACKWARD_COMPATIBLE", 1 to "MANUAL_SENSOR", 2 to "MANUAL_POST_PROCESSING",
        3 to "RAW", 4 to "PRIVATE_REPROCESSING", 5 to "READ_SENSOR_SETTINGS",
        6 to "BURST_CAPTURE", 7 to "YUV_REPROCESSING", 8 to "DEPTH_OUTPUT",
        9 to "CONSTRAINED_HIGH_SPEED_VIDEO", 10 to "MOTION_TRACKING",
        11 to "LOGICAL_MULTI_CAMERA", 12 to "MONOCHROME", 13 to "SECURE_IMAGE_DATA",
        14 to "SYSTEM_CAMERA", 15 to "OFFLINE_PROCESSING",
        16 to "ULTRA_HIGH_RESOLUTION_SENSOR", 17 to "REMOSAIC_REPROCESSING",
        18 to "DYNAMIC_RANGE_TEN_BIT", 19 to "STREAM_USE_CASE", 20 to "COLOR_SPACE_PROFILES"
    )

    private val extNames = mapOf(
        0 to "AUTOMATIC", 1 to "FACE_RETOUCH", 2 to "BOKEH", 3 to "HDR", 4 to "NIGHT"
    )

    // ------------------------------------------------------------------ Dispositivo

    fun deviceInfo(): String = buildString {
        appendLine("== DISPOSITIVO ==")
        appendLine("Fabricante: ${Build.MANUFACTURER}")
        appendLine("Marca: ${Build.BRAND}")
        appendLine("Modelo: ${Build.MODEL}")
        appendLine("Dispositivo: ${Build.DEVICE}")
        appendLine("Producto: ${Build.PRODUCT}")
        appendLine("Hardware: ${Build.HARDWARE}")
        appendLine("Placa: ${Build.BOARD}")
        appendLine("SoC: ${Build.SOC_MANUFACTURER} ${Build.SOC_MODEL}")
        appendLine("Android: ${Build.VERSION.RELEASE} (SDK ${Build.VERSION.SDK_INT})")
        appendLine("Parche de seguridad: ${Build.VERSION.SECURITY_PATCH}")
        append("Compilación: ${Build.DISPLAY}")
    }

    // ------------------------------------------------------------------ Apps de cámara

    @Suppress("DEPRECATION")
    fun cameraApps(context: Context): String = buildString {
        appendLine("== APPS QUE ATIENDEN 'TOMAR FOTO' ==")
        val pm = context.packageManager
        val actions = listOf(
            MediaStore.ACTION_IMAGE_CAPTURE to "IMAGE_CAPTURE (tomar una foto y devolverla)",
            "android.media.action.STILL_IMAGE_CAMERA" to "STILL_IMAGE_CAMERA (abrir la cámara)"
        )
        for ((action, label) in actions) {
            appendLine("- $label:")
            val found = try {
                pm.queryIntentActivities(Intent(action), PackageManager.MATCH_ALL)
            } catch (e: Exception) {
                emptyList()
            }
            if (found.isEmpty()) {
                appendLine("    (ninguna)")
            } else {
                found.forEach {
                    appendLine("    ${it.loadLabel(pm)}  [${it.activityInfo.packageName}]")
                }
            }
        }
    }.trimEnd()

    // ------------------------------------------------------------------ Camera2

    fun camera2(context: Context): Camera2Result {
        val cm = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
        val summary = StringBuilder("== RESUMEN CÁMARAS (Camera2) ==\n")
        val details = StringBuilder("== DETALLE POR CÁMARA ==\n")

        val ids = cm.cameraIdList
        summary.appendLine("Cámaras expuestas a apps: ${ids.joinToString()}")

        for (id in ids) {
            val c = cm.getCameraCharacteristics(id)

            val facing = when (c.get(CameraCharacteristics.LENS_FACING)) {
                CameraCharacteristics.LENS_FACING_BACK -> "trasera"
                CameraCharacteristics.LENS_FACING_FRONT -> "frontal"
                CameraCharacteristics.LENS_FACING_EXTERNAL -> "externa"
                else -> "?"
            }
            val level = when (c.get(CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL)) {
                CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_LEGACY -> "LEGACY"
                CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_LIMITED -> "LIMITED"
                CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_FULL -> "FULL"
                CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_3 -> "LEVEL_3"
                CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_EXTERNAL -> "EXTERNAL"
                else -> "?"
            }
            val caps = c.get(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES)?.toList() ?: emptyList()
            val hasRaw = 3 in caps
            val hasManual = 1 in caps
            val hasMaxRes = 16 in caps
            val extensions = extensionsInfo(cm, id)

            summary.appendLine(
                "Cámara $id ($facing): nivel $level | RAW: ${yn(hasRaw)} | " +
                    "manual ISO/obturador: ${yn(hasManual)} | máx. resolución: ${yn(hasMaxRes)} | " +
                    "extensiones: ${extensions.names}"
            )

            details.appendLine()
            details.appendLine("---- Cámara $id ($facing) ----")
            details.appendLine("Nivel de hardware: $level")
            details.appendLine("Capacidades: " + caps.joinToString { capNames[it] ?: "#$it" })

            val physical = try {
                c.physicalCameraIds
            } catch (e: Exception) {
                emptySet()
            }
            if (physical.isNotEmpty()) details.appendLine("Cámaras físicas internas: ${physical.joinToString()}")

            c.get(CameraCharacteristics.SENSOR_INFO_PIXEL_ARRAY_SIZE)?.let {
                details.appendLine("Sensor (píxeles): ${it.width}x${it.height}")
            }
            c.get(CameraCharacteristics.SENSOR_INFO_PHYSICAL_SIZE)?.let {
                details.appendLine("Sensor (tamaño físico): ${it.width} x ${it.height} mm")
            }
            c.get(CameraCharacteristics.LENS_INFO_AVAILABLE_FOCAL_LENGTHS)?.let {
                details.appendLine("Distancias focales (mm): ${it.joinToString()}")
            }
            c.get(CameraCharacteristics.LENS_INFO_AVAILABLE_APERTURES)?.let {
                details.appendLine("Aperturas (f/): ${it.joinToString()}")
            }
            c.get(CameraCharacteristics.SENSOR_INFO_SENSITIVITY_RANGE)?.let {
                details.appendLine("Rango ISO: $it")
            }
            c.get(CameraCharacteristics.SENSOR_MAX_ANALOG_SENSITIVITY)?.let {
                details.appendLine("ISO analógico máximo: $it")
            }
            c.get(CameraCharacteristics.SENSOR_INFO_EXPOSURE_TIME_RANGE)?.let {
                details.appendLine("Rango de exposición (ns): $it")
            }
            c.get(CameraCharacteristics.CONTROL_ZOOM_RATIO_RANGE)?.let {
                details.appendLine("Rango de zoom: $it")
            }
            details.appendLine("Flash: ${yn(c.get(CameraCharacteristics.FLASH_INFO_AVAILABLE) == true)}")
            c.get(CameraCharacteristics.LENS_INFO_AVAILABLE_OPTICAL_STABILIZATION)?.let {
                details.appendLine("Estabilización óptica (modos): ${it.joinToString()}")
            }
            c.get(CameraCharacteristics.CONTROL_AVAILABLE_SCENE_MODES)?.let { modes ->
                details.appendLine(
                    "Modos de escena: " + modes.joinToString {
                        when (it) {
                            5 -> "5 (NIGHT)"
                            18 -> "18 (HDR)"
                            else -> it.toString()
                        }
                    }
                )
            }
            c.get(CameraCharacteristics.NOISE_REDUCTION_AVAILABLE_NOISE_REDUCTION_MODES)?.let {
                details.appendLine("Modos reducción de ruido: ${it.joinToString()} (2 = alta calidad)")
            }
            c.get(CameraCharacteristics.EDGE_AVAILABLE_EDGE_MODES)?.let {
                details.appendLine("Modos de nitidez: ${it.joinToString()} (2 = alta calidad)")
            }

            val map = c.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
            details.appendLine("Tamaños JPEG: ${sizesText(map?.getOutputSizes(ImageFormat.JPEG))}")
            details.appendLine("Tamaños YUV: ${sizesText(map?.getOutputSizes(ImageFormat.YUV_420_888))}")
            details.appendLine("Tamaños RAW: ${sizesText(map?.getOutputSizes(ImageFormat.RAW_SENSOR))}")

            val mapMax = c.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP_MAXIMUM_RESOLUTION)
            if (mapMax != null) {
                details.appendLine("Modo máxima resolución, JPEG: ${sizesText(mapMax.getOutputSizes(ImageFormat.JPEG))}")
                details.appendLine("Modo máxima resolución, RAW: ${sizesText(mapMax.getOutputSizes(ImageFormat.RAW_SENSOR))}")
            } else {
                details.appendLine("Modo máxima resolución: no expuesto")
            }

            details.appendLine("Extensiones Camera2 (HDR/Noche/etc.): ${extensions.names}")
            if (extensions.detail.isNotEmpty()) details.append(extensions.detail)

            details.append(vendorKeys(c))
        }

        return Camera2Result(summary.toString().trimEnd(), details.toString().trimEnd())
    }

    private class ExtInfo(val names: String, val detail: String)

    private fun extensionsInfo(cm: CameraManager, id: String): ExtInfo {
        return try {
            val ec = cm.getCameraExtensionCharacteristics(id)
            val supported = ec.supportedExtensions
            if (supported.isEmpty()) return ExtInfo("ninguna", "")
            val detail = StringBuilder()
            for (e in supported) {
                val name = extNames[e] ?: "#$e"
                val jpeg = try {
                    sizesText(ec.getExtensionSupportedSizes(e, ImageFormat.JPEG).toTypedArray(), 2)
                } catch (ex: Exception) {
                    "error"
                }
                val preview = try {
                    sizesText(ec.getExtensionSupportedSizes(e, SurfaceTexture::class.java).toTypedArray(), 2)
                } catch (ex: Exception) {
                    "error"
                }
                detail.appendLine("    $name -> foto: $jpeg | vista previa: $preview")
            }
            ExtInfo(supported.joinToString { extNames[it] ?: "#$it" }, detail.toString())
        } catch (e: Exception) {
            ExtInfo("error (${e.javaClass.simpleName})", "")
        }
    }

    /** Claves que NO son del estándar de Android: las agregó el fabricante o MediaTek. */
    private fun vendorKeys(c: CameraCharacteristics): String {
        fun nonStandard(names: List<String>) = names.filter { !it.startsWith("android.") }.sorted()

        val sb = StringBuilder()
        try {
            val chars = nonStandard(c.keys.map { it.name })
            val requests = nonStandard(c.availableCaptureRequestKeys.map { it.name })
            val results = nonStandard(c.availableCaptureResultKeys.map { it.name })

            sb.appendLine("Claves del fabricante (no estándar):")
            sb.appendLine("  Características (${chars.size}):")
            chars.forEach { sb.appendLine("    - $it") }
            sb.appendLine("  Para pedir en una captura (${requests.size}):")
            requests.forEach { sb.appendLine("    - $it") }
            sb.appendLine("  Que devuelve la cámara (${results.size}):")
            results.forEach { sb.appendLine("    - $it") }
        } catch (e: Exception) {
            sb.appendLine("Claves del fabricante: error (${e.javaClass.simpleName})")
        }
        return sb.toString()
    }

    // ------------------------------------------------------------------ CameraX

    fun cameraX(provider: ProcessCameraProvider, ext: ExtensionsManager): String = buildString {
        appendLine("== EXTENSIONES VÍA CAMERAX ==")
        val modes = listOf(
            "AUTO" to ExtensionMode.AUTO,
            "BOKEH" to ExtensionMode.BOKEH,
            "HDR" to ExtensionMode.HDR,
            "NOCHE" to ExtensionMode.NIGHT,
            "RETOQUE FACIAL" to ExtensionMode.FACE_RETOUCH
        )
        for ((lensName, lens) in listOf(
            "Trasera" to CameraSelector.LENS_FACING_BACK,
            "Frontal" to CameraSelector.LENS_FACING_FRONT
        )) {
            val selector = CameraSelector.Builder().requireLensFacing(lens).build()
            val exists = try {
                provider.hasCamera(selector)
            } catch (e: Exception) {
                false
            }
            if (!exists) {
                appendLine("$lensName: sin cámara")
                continue
            }
            val line = modes.joinToString(" | ") { (name, mode) ->
                val ok = try {
                    ext.isExtensionAvailable(selector, mode)
                } catch (e: Exception) {
                    false
                }
                "$name: ${yn(ok)}"
            }
            appendLine("$lensName -> $line")
        }
    }.trimEnd()

    // ------------------------------------------------------------------ Utilidades

    private fun yn(value: Boolean) = if (value) "SÍ" else "NO"

    private fun sizesText(sizes: Array<Size>?, n: Int = 4): String {
        if (sizes == null || sizes.isEmpty()) return "ninguno"
        return sizes
            .sortedByDescending { it.width.toLong() * it.height }
            .take(n)
            .joinToString(", ") {
                String.format(Locale.US, "%dx%d (%.1f MP)", it.width, it.height, it.width * it.height / 1e6)
            }
    }
}
