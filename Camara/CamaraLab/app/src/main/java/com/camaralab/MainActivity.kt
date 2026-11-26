package com.camaralab

import android.Manifest
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.SurfaceTexture
import android.graphics.Typeface
import android.os.Bundle
import android.view.TextureView
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {

    private lateinit var textureView: TextureView
    private lateinit var logView: TextView
    private lateinit var scroll: ScrollView
    private lateinit var btnStart: Button
    private lateinit var btnStop: Button

    private var previewSurfaceTexture: SurfaceTexture? = null
    private var lab: CameraLab? = null
    private var running = false
    private var report = ""
    private val io = Executors.newSingleThreadExecutor()

    private val permissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) {
                startLab()
            } else {
                Toast.makeText(this, "Necesito el permiso de cámara", Toast.LENGTH_LONG).show()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        val dp = resources.displayMetrics.density
        val pad = (12 * dp).toInt()

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, pad, pad, pad)
            fitsSystemWindows = true
        }

        val intro = TextView(this).apply {
            text = "Apoya el teléfono quieto, apuntando a una escena con zonas claras y oscuras " +
                "(por ejemplo una ventana con luz y un interior en sombra). No lo muevas durante " +
                "las pruebas. La vista previa se ve girada: es normal."
            textSize = 13f
        }

        textureView = TextureView(this).apply {
            surfaceTextureListener = object : TextureView.SurfaceTextureListener {
                override fun onSurfaceTextureAvailable(st: SurfaceTexture, w: Int, h: Int) {
                    previewSurfaceTexture = st
                }

                override fun onSurfaceTextureSizeChanged(st: SurfaceTexture, w: Int, h: Int) {}

                override fun onSurfaceTextureDestroyed(st: SurfaceTexture): Boolean {
                    previewSurfaceTexture = null
                    return true
                }

                override fun onSurfaceTextureUpdated(st: SurfaceTexture) {}
            }
        }

        val row1 = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        btnStart = Button(this).apply {
            text = "Iniciar pruebas"
            setOnClickListener { onStartClicked() }
        }
        btnStop = Button(this).apply {
            text = "Detener"
            isEnabled = false
            setOnClickListener { lab?.cancelled = true }
        }
        val lp = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        row1.addView(btnStart, lp)
        row1.addView(btnStop, lp)

        val row2 = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        row2.addView(Button(this).apply {
            text = "Copiar informe"
            setOnClickListener { copyReport() }
        }, lp)
        row2.addView(Button(this).apply {
            text = "Compartir"
            setOnClickListener { shareReport() }
        }, lp)

        logView = TextView(this).apply {
            typeface = Typeface.MONOSPACE
            textSize = 11f
            setTextIsSelectable(true)
            setPadding(0, pad, 0, pad)
        }
        scroll = ScrollView(this).apply { addView(logView) }

        root.addView(intro)
        root.addView(textureView, LinearLayout.LayoutParams((200 * dp).toInt(), (150 * dp).toInt()))
        root.addView(row1)
        root.addView(row2)
        root.addView(
            scroll,
            LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f)
        )
        setContentView(root)
    }

    override fun onPause() {
        super.onPause()
        lab?.cancelled = true
    }

    override fun onDestroy() {
        super.onDestroy()
        lab?.cancelled = true
        io.shutdown()
    }

    private fun onStartClicked() {
        if (running) return
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) ==
            PackageManager.PERMISSION_GRANTED
        ) {
            startLab()
        } else {
            permissionLauncher.launch(Manifest.permission.CAMERA)
        }
    }

    private fun startLab() {
        val st = previewSurfaceTexture
        if (st == null) {
            Toast.makeText(this, "La vista previa aún no está lista, intenta de nuevo", Toast.LENGTH_SHORT).show()
            return
        }
        running = true
        report = ""
        btnStart.isEnabled = false
        btnStop.isEnabled = true
        logView.text = "Iniciando…\n"

        val newLab = CameraLab(this, st) { message -> runOnUiThread { appendLog(message) } }
        lab = newLab

        io.execute {
            val result = try {
                newLab.run()
            } catch (t: Throwable) {
                "Error: $t"
            }
            runOnUiThread {
                report = result
                logView.text = result
                running = false
                btnStart.isEnabled = true
                btnStop.isEnabled = false
                scroll.fullScroll(View.FOCUS_UP)
            }
        }
    }

    private fun appendLog(message: String) {
        logView.append(message + "\n")
        scroll.post { scroll.fullScroll(View.FOCUS_DOWN) }
    }

    private fun copyReport() {
        if (report.isEmpty()) {
            Toast.makeText(this, "Todavía no hay informe", Toast.LENGTH_SHORT).show()
            return
        }
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        clipboard.setPrimaryClip(ClipData.newPlainText("laboratorio_camara", report))
        Toast.makeText(this, "Informe copiado", Toast.LENGTH_SHORT).show()
    }

    private fun shareReport() {
        if (report.isEmpty()) {
            Toast.makeText(this, "Todavía no hay informe", Toast.LENGTH_SHORT).show()
            return
        }
        val send = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_SUBJECT, "Laboratorio de cámara")
            putExtra(Intent.EXTRA_TEXT, report)
        }
        startActivity(Intent.createChooser(send, "Compartir informe"))
    }
}