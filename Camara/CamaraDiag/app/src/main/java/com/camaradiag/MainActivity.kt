package com.camaradiag

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.graphics.Typeface
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.extensions.ExtensionsManager
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {

    private lateinit var output: TextView
    private var report: String = ""
    private val io = Executors.newSingleThreadExecutor()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val dp = resources.displayMetrics.density
        val pad = (12 * dp).toInt()

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, pad, pad, pad)
            fitsSystemWindows = true
        }

        val buttons = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        val btnCopy = Button(this).apply {
            text = "Copiar informe"
            setOnClickListener { copyReport() }
        }
        val btnShare = Button(this).apply {
            text = "Compartir"
            setOnClickListener { shareReport() }
        }
        val btnRetry = Button(this).apply {
            text = "Reanalizar"
            setOnClickListener { runDiagnostics() }
        }
        val lp = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        buttons.addView(btnCopy, lp)
        buttons.addView(btnShare, lp)
        buttons.addView(btnRetry, lp)

        output = TextView(this).apply {
            typeface = Typeface.MONOSPACE
            textSize = 11f
            setTextIsSelectable(true)
            setPadding(0, pad, 0, pad)
        }
        val scroll = ScrollView(this).apply { addView(output) }

        root.addView(buttons)
        root.addView(
            scroll,
            LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                0,
                1f
            )
        )
        setContentView(root)

        runDiagnostics()
    }

    override fun onDestroy() {
        super.onDestroy()
        io.shutdown()
    }

    // ------------------------------------------------------------------ Diagnóstico

    private fun runDiagnostics() {
        output.text = "Analizando cámaras…"
        report = ""

        io.execute {
            val device = safe { Diagnostics.deviceInfo() }
            val apps = safe { Diagnostics.cameraApps(this) }
            val cam2 = try {
                Diagnostics.camera2(this)
            } catch (e: Throwable) {
                Camera2Result("== RESUMEN CÁMARAS (Camera2) ==\nError: $e", "")
            }
            runOnUiThread { collectCameraX(device, apps, cam2) }
        }
    }

    private fun collectCameraX(device: String, apps: String, cam2: Camera2Result) {
        val providerFuture = ProcessCameraProvider.getInstance(this)
        providerFuture.addListener({
            try {
                val provider = providerFuture.get()
                val extFuture = ExtensionsManager.getInstanceAsync(this, provider)
                extFuture.addListener({
                    val camX = try {
                        Diagnostics.cameraX(provider, extFuture.get())
                    } catch (e: Throwable) {
                        "== EXTENSIONES VÍA CAMERAX ==\nError: $e"
                    }
                    show(device, apps, cam2, camX)
                }, ContextCompat.getMainExecutor(this))
            } catch (e: Throwable) {
                show(device, apps, cam2, "== EXTENSIONES VÍA CAMERAX ==\nError: $e")
            }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun show(device: String, apps: String, cam2: Camera2Result, camX: String) {
        report = listOf(
            "DIAGNÓSTICO DE CÁMARA v1.0",
            device,
            cam2.summary,
            camX,
            apps,
            cam2.details
        ).filter { it.isNotBlank() }.joinToString("\n\n")
        output.text = report
    }

    private fun safe(block: () -> String): String =
        try {
            block()
        } catch (e: Throwable) {
            "Error: $e"
        }

    // ------------------------------------------------------------------ Acciones

    private fun copyReport() {
        if (report.isEmpty()) return
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        clipboard.setPrimaryClip(ClipData.newPlainText("diagnostico_camara", report))
        Toast.makeText(this, "Informe copiado", Toast.LENGTH_SHORT).show()
    }

    private fun shareReport() {
        if (report.isEmpty()) return
        val send = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_SUBJECT, "Diagnóstico de cámara")
            putExtra(Intent.EXTRA_TEXT, report)
        }
        startActivity(Intent.createChooser(send, "Compartir diagnóstico"))
    }
}
