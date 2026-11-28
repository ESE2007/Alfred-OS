package com.tonada.mobile

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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Computer
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.FavoriteBorder
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Repeat
import androidx.compose.material.icons.filled.RepeatOne
import androidx.compose.material.icons.filled.Shuffle
import androidx.compose.material.icons.filled.SkipNext
import androidx.compose.material.icons.filled.SkipPrevious
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Slider
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp

@Composable
fun NowPlayingScreen(onClose: () -> Unit, onDevices: () -> Unit) {
    val n = Model.now
    val accent = MaterialTheme.colorScheme.primary
    val dim = MaterialTheme.colorScheme.onSurfaceVariant

    Surface(Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        Column(
            Modifier.fillMaxSize().padding(horizontal = 20.dp, vertical = 8.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                IconButton(onClick = onClose) { Icon(Icons.Filled.KeyboardArrowDown, contentDescription = "Cerrar") }
                Text(
                    "Reproduciendo en " + activeDeviceName(),
                    modifier = Modifier.weight(1f),
                    textAlign = TextAlign.Center,
                    maxLines = 1, overflow = TextOverflow.Ellipsis,
                    style = MaterialTheme.typography.bodyMedium, color = dim,
                )
                Spacer(Modifier.width(48.dp))
            }

            if (n == null) {
                Box(Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) {
                    Text(
                        if (Model.controlPc) "El PC no está reproduciendo nada." else "No hay nada sonando.",
                        color = dim,
                    )
                }
                OutlinedButton(onClick = onDevices) { Text("Cambiar de dispositivo") }
                return@Column
            }

            Spacer(Modifier.height(12.dp))
            Cover(n.track, n.coverKey, Modifier.size(280.dp), 16.dp)
            Spacer(Modifier.height(20.dp))
            Text(
                n.title, style = MaterialTheme.typography.headlineSmall,
                maxLines = 2, overflow = TextOverflow.Ellipsis, textAlign = TextAlign.Center,
            )
            Text(
                listOf(n.artist, n.album).filter { it.isNotEmpty() }.joinToString(" · "),
                style = MaterialTheme.typography.bodyMedium, color = dim,
                maxLines = 1, overflow = TextOverflow.Ellipsis, textAlign = TextAlign.Center,
            )

            Spacer(Modifier.height(16.dp))
            val pos by rememberPosition(300L)
            var drag by remember { mutableStateOf<Float?>(null) }
            val dur = if (n.durSec > 1.0) n.durSec else 1.0
            val shownPos = (drag ?: pos.toFloat()).coerceIn(0f, dur.toFloat())
            Slider(
                value = shownPos,
                onValueChange = { drag = it },
                onValueChangeFinished = {
                    drag?.let { Model.seek(it.toDouble()) }
                    drag = null
                },
                valueRange = 0f..dur.toFloat(),
            )
            Row(Modifier.fillMaxWidth().padding(horizontal = 4.dp)) {
                Text(fmtTime(shownPos.toDouble()), style = MaterialTheme.typography.bodySmall, color = dim)
                Spacer(Modifier.weight(1f))
                Text(fmtTime(n.durSec), style = MaterialTheme.typography.bodySmall, color = dim)
            }

            Spacer(Modifier.height(8.dp))
            Row(
                Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                IconButton(onClick = { Model.toggleShuffle() }) {
                    Icon(Icons.Filled.Shuffle, contentDescription = "Aleatorio", tint = if (n.shuffle) accent else dim)
                }
                IconButton(onClick = { Model.prev() }, modifier = Modifier.size(56.dp)) {
                    Icon(Icons.Filled.SkipPrevious, contentDescription = "Anterior", modifier = Modifier.size(36.dp))
                }
                Box(
                    Modifier.size(68.dp).clip(CircleShape).background(accent).clickable { Model.toggle() },
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(
                        if (n.playing) Icons.Filled.Pause else Icons.Filled.PlayArrow,
                        contentDescription = "Reproducir / pausa",
                        modifier = Modifier.size(40.dp), tint = Color.White,
                    )
                }
                IconButton(onClick = { Model.next() }, modifier = Modifier.size(56.dp)) {
                    Icon(Icons.Filled.SkipNext, contentDescription = "Siguiente", modifier = Modifier.size(36.dp))
                }
                IconButton(onClick = { Model.cycleRepeat() }) {
                    Icon(
                        if (n.repeat == "one") Icons.Filled.RepeatOne else Icons.Filled.Repeat,
                        contentDescription = "Repetir",
                        tint = if (n.repeat == "off") dim else accent,
                    )
                }
            }

            val vol = Model.volume
            if (vol != null) {
                var vdrag by remember { mutableStateOf<Float?>(null) }
                var lastSent by remember { mutableStateOf(0L) }
                Row(Modifier.fillMaxWidth().padding(top = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Filled.VolumeUp, contentDescription = "Volumen del PC", tint = dim)
                    Slider(
                        value = vdrag ?: vol.toFloat().coerceIn(0f, 1f),
                        onValueChange = {
                            vdrag = it
                            val t = System.currentTimeMillis()
                            if (t - lastSent > 150) {
                                lastSent = t
                                Model.setVolume(it.toDouble())
                            }
                        },
                        onValueChangeFinished = {
                            vdrag?.let { Model.setVolume(it.toDouble()) }
                            vdrag = null
                        },
                        valueRange = 0f..1f,
                        modifier = Modifier.weight(1f),
                    )
                    if (n.fav != null) {
                        IconButton(onClick = { Model.toggleFav() }) {
                            Icon(
                                if (n.fav) Icons.Filled.Favorite else Icons.Filled.FavoriteBorder,
                                contentDescription = "Favorita",
                                tint = if (n.fav) accent else dim,
                            )
                        }
                    }
                }
            }

            Spacer(Modifier.weight(1f))
            OutlinedButton(onClick = onDevices) {
                Icon(Icons.Filled.Computer, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(Modifier.width(8.dp))
                Text("Dispositivos")
            }
        }
    }
}
