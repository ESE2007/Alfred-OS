package com.tonada.mobile

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.os.Build
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Computer
import androidx.compose.material.icons.filled.Devices
import androidx.compose.material.icons.filled.LibraryMusic
import androidx.compose.material.icons.filled.MusicNote
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.QueueMusic
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.State
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext

/** m:ss */
fun fmtTime(sec: Double): String {
    val s = if (sec.isNaN() || sec < 0) 0 else sec.toInt()
    return "%d:%02d".format(s / 60, s % 60)
}

/** Position of the active device, refreshed a few times per second. */
@Composable
fun rememberPosition(everyMs: Long = 400L): State<Double> {
    val s = remember { mutableStateOf(Model.position()) }
    LaunchedEffect(Unit) {
        while (true) {
            s.value = Model.position()
            delay(everyMs)
        }
    }
    return s
}

/** Cover art: from the phone's own file, or the small JPEG the PC sends. */
@Composable
fun Cover(track: Track?, pcKey: String?, modifier: Modifier, radius: Dp = 8.dp) {
    val ctx = LocalContext.current
    var bmp by remember(track?.id) { mutableStateOf<Bitmap?>(null) }
    if (track != null) {
        LaunchedEffect(track.id) {
            bmp = withContext(Dispatchers.IO) { Library.thumbnail(ctx, track) }
        }
    }
    val shown: Bitmap? = if (track != null) bmp else if (pcKey != null) Model.rArt[pcKey] else null
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(radius))
            .background(MaterialTheme.colorScheme.surfaceVariant),
        contentAlignment = Alignment.Center,
    ) {
        if (shown != null) {
            Image(
                bitmap = shown.asImageBitmap(),
                contentDescription = null,
                contentScale = ContentScale.Crop,
                modifier = Modifier.fillMaxSize(),
            )
        } else {
            Icon(Icons.Filled.MusicNote, contentDescription = null, tint = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

/** Name of the device that is playing / being controlled. */
fun activeDeviceName(): String = if (Model.controlPc) (Model.pair?.name ?: "PC") else "Este teléfono"

@Composable
fun AppRoot() {
    var tab by remember { mutableIntStateOf(0) }
    var showNow by remember { mutableStateOf(false) }
    val ctx = LocalContext.current

    val notifLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { }
    LaunchedEffect(Unit) {
        if (Build.VERSION.SDK_INT >= 33 &&
            ContextCompat.checkSelfPermission(ctx, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) {
            notifLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
    }

    BackHandler(enabled = showNow) { showNow = false }

    Box(Modifier.fillMaxSize()) {
        Scaffold(
            containerColor = MaterialTheme.colorScheme.background,
            bottomBar = {
                Column {
                    MiniBar(onOpen = { showNow = true })
                    NavigationBar {
                        NavigationBarItem(
                            selected = tab == 0,
                            onClick = { tab = 0 },
                            icon = { Icon(Icons.Filled.LibraryMusic, contentDescription = null) },
                            label = { Text("Biblioteca") },
                        )
                        NavigationBarItem(
                            selected = tab == 1,
                            onClick = { tab = 1 },
                            icon = { Icon(Icons.Filled.QueueMusic, contentDescription = null) },
                            label = { Text("Cola") },
                        )
                        NavigationBarItem(
                            selected = tab == 2,
                            onClick = { tab = 2 },
                            icon = { Icon(Icons.Filled.Devices, contentDescription = null) },
                            label = { Text("Dispositivos") },
                        )
                    }
                }
            },
        ) { pad ->
            Box(Modifier.padding(pad).fillMaxSize()) {
                when (tab) {
                    0 -> LibraryScreen(onDevices = { tab = 2 })
                    1 -> QueueScreen(onDevices = { tab = 2 })
                    else -> DevicesScreen()
                }
            }
        }
        if (showNow) {
            NowPlayingScreen(onClose = { showNow = false }, onDevices = {
                showNow = false
                tab = 2
            })
        }
    }
}

@Composable
fun MiniBar(onOpen: () -> Unit) {
    val n = Model.now ?: return
    val pos by rememberPosition(500L)
    val frac = if (n.durSec > 0) (pos / n.durSec).toFloat().coerceIn(0f, 1f) else 0f
    Surface(color = MaterialTheme.colorScheme.surfaceVariant, modifier = Modifier.fillMaxWidth().clickable { onOpen() }) {
        Column {
            LinearProgressIndicator(progress = { frac }, modifier = Modifier.fillMaxWidth().height(2.dp))
            Row(
                Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 6.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Cover(n.track, n.coverKey, Modifier.size(44.dp), 6.dp)
                Spacer(Modifier.width(10.dp))
                Column(Modifier.weight(1f)) {
                    Text(n.title, maxLines = 1, overflow = TextOverflow.Ellipsis, style = MaterialTheme.typography.bodyMedium)
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        if (Model.controlPc) {
                            Icon(
                                Icons.Filled.Computer, contentDescription = null,
                                modifier = Modifier.size(14.dp), tint = MaterialTheme.colorScheme.primary,
                            )
                            Spacer(Modifier.width(4.dp))
                        }
                        Text(
                            n.artist.ifEmpty { activeDeviceName() },
                            maxLines = 1, overflow = TextOverflow.Ellipsis,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
                IconButton(onClick = { Model.toggle() }) {
                    Icon(if (n.playing) Icons.Filled.Pause else Icons.Filled.PlayArrow, contentDescription = null)
                }
            }
        }
    }
}

/** One line telling where the music plays; tapping it opens the devices tab. */
@Composable
fun DeviceBanner(onClick: () -> Unit) {
    val pc = Model.controlPc
    val sub = when {
        !pc -> ""
        Model.rStatus != com.tonada.mobile.core.MqttClient.Status.ONLINE -> " · sin conexión"
        Model.rState?.off == true -> " · cerrado"
        else -> ""
    }
    Row(
        Modifier.fillMaxWidth().clickable { onClick() }.padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.Start,
    ) {
        Icon(
            if (pc) Icons.Filled.Computer else Icons.Filled.Devices, contentDescription = null,
            modifier = Modifier.size(18.dp), tint = MaterialTheme.colorScheme.primary,
        )
        Spacer(Modifier.width(8.dp))
        Text(
            "Reproduciendo en: " + activeDeviceName() + sub,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}
