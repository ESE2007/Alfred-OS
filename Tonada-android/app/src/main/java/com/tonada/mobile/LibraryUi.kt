package com.tonada.mobile

import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Sort
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.tonada.mobile.core.Identity

private const val UNKNOWN_ARTIST = "Artista desconocido"

@Composable
fun TrackRow(t: Track, current: Boolean, onClick: () -> Unit) {
    var menu by remember { mutableStateOf(false) }
    Row(
        Modifier.fillMaxWidth().clickable { onClick() }.padding(horizontal = 12.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Cover(t, null, Modifier.size(44.dp), 6.dp)
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(
                t.title.ifEmpty { t.fileName },
                maxLines = 1, overflow = TextOverflow.Ellipsis,
                color = if (current) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface,
            )
            Text(
                listOf(t.artist, t.album).filter { it.isNotEmpty() }.joinToString(" · "),
                maxLines = 1, overflow = TextOverflow.Ellipsis,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Box {
            IconButton(onClick = { menu = true }) {
                Icon(Icons.Filled.MoreVert, contentDescription = "Más")
            }
            DropdownMenu(expanded = menu, onDismissRequest = { menu = false }) {
                DropdownMenuItem(
                    text = { Text("Reproducir después") },
                    onClick = {
                        menu = false
                        Model.enqueue(t, true)
                    },
                )
                DropdownMenuItem(
                    text = { Text("Añadir al final de la cola") },
                    onClick = {
                        menu = false
                        Model.enqueue(t, false)
                    },
                )
            }
        }
    }
}

@Composable
fun GroupRow(title: String, subtitle: String, sample: Track?, onClick: () -> Unit) {
    Row(
        Modifier.fillMaxWidth().clickable { onClick() }.padding(horizontal = 12.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Cover(sample, null, Modifier.size(48.dp), 6.dp)
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(title, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Text(
                subtitle, maxLines = 1, overflow = TextOverflow.Ellipsis,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
fun LibraryScreen(onDevices: () -> Unit) {
    var granted by remember { mutableStateOf(Model.hasPermission()) }
    val permLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { ok ->
        granted = ok
        if (ok) Model.loadLibrary()
    }

    Column(Modifier.fillMaxSize()) {
        DeviceBanner(onDevices)
        if (!granted) {
            Column(
                Modifier.fillMaxSize().padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = androidx.compose.foundation.layout.Arrangement.Center,
            ) {
                Text("Tonada necesita permiso para leer la música del teléfono.", style = MaterialTheme.typography.bodyLarge)
                Spacer(Modifier.size(16.dp))
                Button(onClick = { permLauncher.launch(Model.permissionName()) }) { Text("Dar permiso") }
            }
            return@Column
        }
        when (Model.libState) {
            0, 1 -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
            else -> LibraryContent()
        }
    }
}

@Composable
private fun LibraryContent() {
    var sub by remember { mutableIntStateOf(0) }
    var query by remember { mutableStateOf("") }
    var sort by remember { mutableIntStateOf(0) }
    var sortMenu by remember { mutableStateOf(false) }
    var detail by remember { mutableStateOf<Pair<Int, String>?>(null) }
    BackHandler(enabled = detail != null) { detail = null }

    val all = Model.tracks
    if (all.isEmpty()) {
        Box(Modifier.fillMaxSize().padding(24.dp), contentAlignment = Alignment.Center) {
            Text(
                "No se encontró música en este teléfono. Copia aquí los mismos archivos que tienes en el PC.",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        return
    }

    val d = detail
    if (d != null) {
        val list = remember(all, d) {
            val base = if (d.first == 1) all.filter { it.album == d.second }
            else all.filter { (it.artist.ifEmpty { UNKNOWN_ARTIST }) == d.second }
            if (d.first == 1) base.sortedWith(compareBy<Track>({ it.trackNo }, { it.title.lowercase() }))
            else base.sortedBy { it.title.lowercase() }
        }
        Row(Modifier.fillMaxWidth().padding(horizontal = 4.dp), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = { detail = null }) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Volver")
            }
            Text(d.second, maxLines = 1, overflow = TextOverflow.Ellipsis, style = MaterialTheme.typography.titleMedium)
        }
        TrackList(list, d.second)
        return
    }

    TabRow(selectedTabIndex = sub) {
        listOf("Canciones", "Álbumes", "Artistas").forEachIndexed { i, s ->
            Tab(selected = sub == i, onClick = { sub = i }, text = { Text(s) })
        }
    }

    if (sub == 0) {
        Row(Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 4.dp), verticalAlignment = Alignment.CenterVertically) {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                singleLine = true,
                placeholder = { Text("Buscar") },
                leadingIcon = { Icon(Icons.Filled.Search, contentDescription = null) },
                trailingIcon = {
                    if (query.isNotEmpty()) {
                        IconButton(onClick = { query = "" }) { Icon(Icons.Filled.Close, contentDescription = "Borrar") }
                    }
                },
                modifier = Modifier.weight(1f),
            )
            Box {
                IconButton(onClick = { sortMenu = true }) { Icon(Icons.Filled.Sort, contentDescription = "Ordenar") }
                DropdownMenu(expanded = sortMenu, onDismissRequest = { sortMenu = false }) {
                    listOf("Por título", "Por artista", "Recién agregadas").forEachIndexed { i, s ->
                        DropdownMenuItem(text = { Text(if (sort == i) "✓ $s" else s) }, onClick = {
                            sort = i
                            sortMenu = false
                        })
                    }
                }
            }
        }
        val list = remember(all, query, sort) {
            val q = Identity.norm(query)
            val f = if (q.isEmpty()) all else all.filter { it.search.contains(q) }
            when (sort) {
                1 -> f.sortedWith(compareBy<Track>({ it.artist.lowercase() }, { it.title.lowercase() }))
                2 -> f.sortedByDescending { it.dateAdded }
                else -> f
            }
        }
        TrackList(list, if (query.isEmpty()) "Biblioteca" else "Búsqueda")
    } else if (sub == 1) {
        val groups = remember(all) { all.groupBy { it.album.ifEmpty { "Sin álbum" } }.toList().sortedBy { it.first.lowercase() } }
        LazyColumn(Modifier.fillMaxSize()) {
            items(groups, key = { it.first }) { g ->
                GroupRow(g.first, "${g.second.size} canciones", g.second.first()) { detail = Pair(1, g.first) }
            }
        }
    } else {
        val groups = remember(all) { all.groupBy { it.artist.ifEmpty { UNKNOWN_ARTIST } }.toList().sortedBy { it.first.lowercase() } }
        LazyColumn(Modifier.fillMaxSize()) {
            items(groups, key = { it.first }) { g ->
                GroupRow(g.first, "${g.second.size} canciones", g.second.first()) { detail = Pair(2, g.first) }
            }
        }
    }
}

@Composable
private fun TrackList(list: List<Track>, name: String) {
    val state = rememberLazyListState()
    val playingId = if (Model.controlPc) null else Model.lId
    LazyColumn(Modifier.fillMaxSize(), state = state) {
        itemsIndexed(list, key = { _, t -> t.id }) { i, t ->
            TrackRow(t, t.id == playingId) { Model.playList(list, i, name) }
        }
    }
}

@Composable
fun QueueScreen(onDevices: () -> Unit) {
    val items = Model.queueItems()
    val state = rememberLazyListState()
    LaunchedEffect(Model.controlPc) {
        val i = Model.queueItems().indexOfFirst { it.current }
        if (i > 0) state.scrollToItem(i)
    }
    Column(Modifier.fillMaxSize()) {
        DeviceBanner(onDevices)
        if (items.isEmpty()) {
            Box(Modifier.fillMaxSize().padding(24.dp), contentAlignment = Alignment.Center) {
                Text(
                    if (Model.controlPc) "El PC no tiene cola o aún no se conecta." else "La cola del teléfono está vacía.",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        } else {
            LazyColumn(Modifier.fillMaxSize(), state = state) {
                items(items, key = { it.index }) { q ->
                    Column(Modifier.fillMaxWidth().clickable { Model.jump(q) }.padding(horizontal = 16.dp, vertical = 8.dp)) {
                        Text(
                            q.title, maxLines = 1, overflow = TextOverflow.Ellipsis,
                            color = if (q.current) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface,
                        )
                        Text(
                            q.artist, maxLines = 1, overflow = TextOverflow.Ellipsis,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
        }
    }
}
