package com.tonada.mobile

import android.Manifest
import android.app.Application
import android.content.ComponentName
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.widget.Toast
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.core.content.ContextCompat
import androidx.media3.common.C
import androidx.media3.common.MediaItem
import androidx.media3.common.MediaMetadata
import androidx.media3.common.Player
import androidx.media3.session.MediaController
import androidx.media3.session.SessionToken
import com.tonada.mobile.core.Ent
import com.tonada.mobile.core.MqttClient
import com.tonada.mobile.core.PairInfo
import com.tonada.mobile.core.RemoteClient
import com.tonada.mobile.core.RemoteQueue
import com.tonada.mobile.core.RemoteState

/** What is playing right now on the active device (this phone or the PC). */
class Now(
    val title: String,
    val artist: String,
    val album: String,
    val durSec: Double,
    val playing: Boolean,
    val shuffle: Boolean,
    val repeat: String,
    val fav: Boolean?,
    val coverKey: String,
    val track: Track?,
)

/** One row of the queue of the active device. */
class QItem(val index: Int, val title: String, val artist: String, val current: Boolean, val key: String)

/**
- Single place that holds the UI state. Everything here runs on the main thread;
- the network and MediaStore work posts its results back.
 */
object Model {
    lateinit var app: Application
    lateinit var prefs: Prefs
    private val main = Handler(Looper.getMainLooper())

    // ---------------------------------------------------------------- library
    var tracks by mutableStateOf<List<Track>>(emptyList())
    var libState by mutableIntStateOf(0) // 0 = not loaded, 1 = loading, 2 = loaded
    private var byId: Map<Long, Track> = emptyMap()
    private val byKey = HashMap<String, Track>()
    private val byAlt = HashMap<String, Track>()

    fun permissionName(): String =
        if (Build.VERSION.SDK_INT >= 33) Manifest.permission.READ_MEDIA_AUDIO else Manifest.permission.READ_EXTERNAL_STORAGE

    fun hasPermission(): Boolean =
        ContextCompat.checkSelfPermission(app, permissionName()) == PackageManager.PERMISSION_GRANTED

    fun loadLibrary() {
        if (libState == 1 || !hasPermission()) return
        libState = 1
        Thread {
            val list = try {
                Library.scan(app)
            } catch (e: Exception) {
                emptyList()
            }
            main.post { applyLibrary(list) }
        }.start()
    }

    private fun applyLibrary(list: List<Track>) {
        byId = list.associateBy { it.id }
        byKey.clear()
        byAlt.clear()
        for (t in list) {
            val e = t.toEnt()
            byKey[e.k] = t
            if (t.title.isNotBlank() && !byAlt.containsKey(e.a)) byAlt[e.a] = t
        }
        tracks = list
        libState = 2
        syncLocal(true)
    }

    private fun resolve(e: Ent): Track? = byKey[e.k] ?: byAlt[e.a]

    // ----------------------------------------------------------------- local player
    private var controller: MediaController? = null
    var lId by mutableStateOf<Long?>(null)
    var lPlaying by mutableStateOf(false)
    var lShuffle by mutableStateOf(false)
    var lRepeat by mutableIntStateOf(Player.REPEAT_MODE_OFF)
    var lDurMs by mutableStateOf(0L)
    var lIndex by mutableIntStateOf(-1)
    var lQueueIds by mutableStateOf<List<Long>>(emptyList())

    private val playerListener = object : Player.Listener {
        override fun onEvents(player: Player, events: Player.Events) {
            syncLocal(events.contains(Player.EVENT_TIMELINE_CHANGED))
        }
    }

    private fun syncLocal(rebuildQueue: Boolean = false) {
        val c = controller ?: return
        val st = c.playbackState
        lPlaying = c.playWhenReady && st != Player.STATE_ENDED && st != Player.STATE_IDLE
        lShuffle = c.shuffleModeEnabled
        lRepeat = c.repeatMode
        lIndex = if (c.mediaItemCount == 0) -1 else c.currentMediaItemIndex
        lDurMs = if (c.duration == C.TIME_UNSET) 0L else c.duration
        lId = c.currentMediaItem?.mediaId?.toLongOrNull()
        if (rebuildQueue || c.mediaItemCount != lQueueIds.size) {
            lQueueIds = (0 until c.mediaItemCount).map { c.getMediaItemAt(it).mediaId.toLongOrNull() ?: -1L }
        }
    }

    private fun connectController() {
        val token = SessionToken(app, ComponentName(app, PlayerService::class.java))
        val f = MediaController.Builder(app, token).buildAsync()
        f.addListener({
            try {
                val c = f.get()
                controller = c
                c.addListener(playerListener)
                syncLocal(true)
            } catch (e: Exception) {
                msg("No se pudo iniciar el reproductor")
            }
        }, ContextCompat.getMainExecutor(app))
    }

    private fun mediaItem(t: Track): MediaItem {
        val md = MediaMetadata.Builder()
            .setTitle(t.title)
            .setArtist(t.artist)
            .setAlbumTitle(t.album)
            .setArtworkUri(t.albumArtUri)
            .build()
        return MediaItem.Builder()
            .setMediaId(t.id.toString())
            .setUri(t.uri)
            .setRequestMetadata(MediaItem.RequestMetadata.Builder().setMediaUri(t.uri).build())
            .setMediaMetadata(md)
            .build()
    }

    private fun playLocal(list: List<Track>, start: Int, posMs: Long, play: Boolean): Boolean {
        val c = controller
        if (c == null) {
            msg("El reproductor aún no está listo")
            return false
        }
        c.setMediaItems(list.map { mediaItem(it) }, start, posMs)
        c.prepare()
        if (play) c.play() else c.pause()
        return true
    }

    // --------------------------------------------------------------------- remote
@set:JvmName("setPairProp")
    var pair by mutableStateOf<PairInfo?>(null)
        private set
    var rStatus by mutableStateOf(MqttClient.Status.OFF)
    var rDetail by mutableStateOf<String?>(null)
    var rState by mutableStateOf<RemoteState?>(null)
    var rQueue by mutableStateOf<RemoteQueue?>(null)
    val rArt = mutableStateMapOf<String, Bitmap>()
    var controlPc by mutableStateOf(false)
    private var rc: RemoteClient? = null

    val pcReachable: Boolean get() = rStatus == MqttClient.Status.ONLINE && rState?.off != true

    private val remoteListener = object : RemoteClient.Listener {
        override fun onStatus(status: MqttClient.Status, detail: String?) {
            main.post {
                rStatus = status
                rDetail = detail
            }
        }

        override fun onState(s: RemoteState) {
            main.post { rState = s }
        }

        override fun onQueue(q: RemoteQueue) {
            main.post { rQueue = q }
        }

        override fun onArt(key: String, jpeg: ByteArray?) {
            if (jpeg == null || jpeg.isEmpty()) return
            val bmp = BitmapFactory.decodeByteArray(jpeg, 0, jpeg.size) ?: return
            main.post {
                if (rArt.size > 40) rArt.clear()
                rArt[key] = bmp
            }
        }

        override fun onAck(nonce: String, ok: Boolean, err: String?, miss: Int) {
            main.post {
                if (!ok) msg("El PC no pudo hacerlo" + (if (err.isNullOrBlank()) "" else ": $err"))
                else if (miss > 0) msg("$miss canciones no están en el PC")
            }
        }
    }

    fun startRemote() {
        val p = pair ?: return
        if (rc != null) return
        val client = RemoteClient(p, prefs.deviceId, prefs.deviceName, { OkHttpWs() }, remoteListener)
        rc = client
        client.start()
    }

    fun stopRemote() {
        rc?.stop()
        rc = null
        rStatus = MqttClient.Status.OFF
    }

    fun setPair(p: PairInfo?) {
        stopRemote()
        prefs.savePair(p)
        pair = p
        rState = null
        rQueue = null
        rArt.clear()
        if (p == null) controlPc = false else startRemote()
    }

    fun sync() {
        rc?.send("sync")
    }

    /** Chooses which device is controlled; the one that is left stops, so only one plays at a time. */
    fun setActive(pc: Boolean) {
        if (pc == controlPc) return
        if (pc) {
            controller?.pause()
            controlPc = true
            sync()
        } else {
            rc?.send("pause")
            controlPc = false
        }
    }

    // ------------------------------------------------------------------ lifecycle
    fun init(a: Application) {
        app = a
        prefs = Prefs(a)
        pair = prefs.loadPair()
        connectController()
    }

    fun onStart() {
        startRemote()
        if (hasPermission() && libState == 0) loadLibrary()
    }

    fun onStop() {
        stopRemote()
    }

    fun msg(s: String) {
        Toast.makeText(app, s, Toast.LENGTH_SHORT).show()
    }

    // ------------------------------------------------------------ unified playback
    val now: Now?
        get() {
            if (controlPc) {
                val s = rState ?: return null
                val cur = s.cur ?: return null
                if (s.off) return null
                return Now(
                    cur.t, cur.ar, cur.al, if (s.dur > 0) s.dur else cur.d.toDouble(), s.playing, s.shuffle, s.repeat,
                    s.fav, cur.k, null
                )
            }
            val t = lId?.let { byId[it] } ?: return null
            val rep = when (lRepeat) {
                Player.REPEAT_MODE_ONE -> "one"
                Player.REPEAT_MODE_ALL -> "all"
                else -> "off"
            }
            return Now(t.title, t.artist, t.album, lDurMs / 1000.0, lPlaying, lShuffle, rep, null, "l:" + t.id, t)
        }

    /** Position in seconds (read it from a ticking composable). */
    fun position(): Double {
        if (controlPc) return rState?.livePos(System.currentTimeMillis()) ?: 0.0
        return (controller?.currentPosition ?: 0L) / 1000.0
    }

    /** Volume of the PC (0..1), or null when the active device is this phone (use the hardware keys). */
    val volume: Double? get() = if (controlPc) rState?.vol else null

    fun toggle() {
        if (controlPc) {
            rc?.send("toggle")
            return
        }
        val c = controller ?: return
        if (lPlaying) c.pause() else {
            if (c.playbackState == Player.STATE_IDLE) c.prepare()
            if (c.playbackState == Player.STATE_ENDED) c.seekToDefaultPosition()
            c.play()
        }
    }

    fun next() {
        if (controlPc) rc?.send("next") else controller?.seekToNext()
    }

    fun prev() {
        if (controlPc) rc?.send("prev") else controller?.seekToPrevious()
    }

    fun seek(sec: Double) {
        if (controlPc) rc?.send("seek", mapOf("pos" to sec)) else controller?.seekTo((sec * 1000).toLong())
    }

    fun toggleShuffle() {
        val n = now ?: return
        if (controlPc) {
            rc?.send("shuffle", mapOf("on" to !n.shuffle))
        } else {
            controller?.shuffleModeEnabled = !n.shuffle
        }
    }

    fun cycleRepeat() {
        val n = now ?: return
        val next = when (n.repeat) {
            "off" -> "all"
            "all" -> "one"
            else -> "off"
        }
        if (controlPc) rc?.send("repeat", mapOf("m" to next)) else {
            controller?.repeatMode = when (next) {
                "all" -> Player.REPEAT_MODE_ALL
                "one" -> Player.REPEAT_MODE_ONE
                else -> Player.REPEAT_MODE_OFF
            }
        }
    }

    fun setVolume(v: Double) {
        if (controlPc) rc?.send("vol", mapOf("v" to v.coerceIn(0.0, 1.0)))
    }

    fun toggleFav() {
        val n = now ?: return
        if (controlPc && n.fav != null) rc?.send("fav", mapOf("on" to !n.fav))
    }

    fun queueItems(): List<QItem> {
        if (controlPc) {
            val q = rQueue ?: return emptyList()
            return q.items.mapIndexed { i, e -> QItem(q.off + i, e.t, e.ar, q.off + i == q.cur, e.k) }
        }
        return lQueueIds.mapIndexed { i, id ->
            val t = byId[id]
            QItem(i, t?.title ?: "?", t?.artist ?: "", i == lIndex, "l:$id")
        }
    }

    fun jump(q: QItem) {
        if (controlPc) rc?.send("jump", mapOf("i" to q.index, "k" to q.key)) else {
            controller?.seekToDefaultPosition(q.index)
            controller?.play()
        }
    }

    /** Plays [list] from [start] on the active device (this phone or the PC). */
    fun playList(list: List<Track>, start: Int, name: String) {
        if (list.isEmpty() || start !in list.indices) return
        if (controlPc) {
            val client = rc
            if (client == null || !pcReachable) {
                msg("El PC no está conectado")
                return
            }
            // at most 300 songs travel to the PC, centred on the chosen one
            var from = (start - 100).coerceAtLeast(0)
            val to = (from + 300).coerceAtMost(list.size)
            from = (to - 300).coerceAtLeast(0)
            val part = list.subList(from, to)
            client.playTracks(part.map { it.toEnt() }, start - from, 0.0, true, name)
        } else {
            playLocal(list, start, 0L, true)
        }
    }

    /** Adds a song to the queue of the active device, right after the current one or at the end. */
    fun enqueue(t: Track, next: Boolean) {
        if (controlPc) {
            val client = rc
            if (client == null || !pcReachable) {
                msg("El PC no está conectado")
                return
            }
            client.enqueue(listOf(t.toEnt()), next)
            msg(if (next) "Sonará después en el PC" else "Añadida a la cola del PC")
        } else {
            val c = controller ?: return
            if (c.mediaItemCount == 0) {
                playLocal(listOf(t), 0, 0L, true)
                return
            }
            val idx = if (next) c.currentMediaItemIndex + 1 else c.mediaItemCount
            c.addMediaItem(idx, mediaItem(t))
            msg(if (next) "Sonará después" else "Añadida a la cola")
        }
    }

    fun setDeviceName(name: String) {
        prefs.deviceName = name.trim().ifEmpty { Build.MODEL ?: "Teléfono" }
        if (rc != null) {
            stopRemote()
            startRemote()
        }
    }

    // ------------------------------------------------------------------ transfer
    /** What plays on the PC continues on this phone, at the same position. */
    fun transferToPhone() {
        val s = rState
        val cur = s?.cur
        if (s == null || s.off || cur == null) {
            msg("El PC no está reproduciendo nada")
            return
        }
        if (libState != 2) {
            msg("Aún no se cargó la música del teléfono")
            return
        }
        val q = rQueue
        val ents: List<Ent>
        val start: Int
        if (q != null && q.cur - q.off in q.items.indices && q.items[q.cur - q.off].k == cur.k) {
            ents = q.items
            start = q.cur - q.off
        } else {
            ents = listOf(cur)
            start = 0
        }
        val resolved = ArrayList<Track>()
        var startIdx = -1
        var missing = 0
        for ((i, e) in ents.withIndex()) {
            val t = resolve(e)
            if (t == null) {
                missing++
                continue
            }
            if (i == start) startIdx = resolved.size
            resolved.add(t)
        }
        if (startIdx < 0) {
            msg("Esa canción no está en este teléfono")
            return
        }
        if (!playLocal(resolved, startIdx, (s.livePos(System.currentTimeMillis()) * 1000).toLong(), s.playing)) return
        rc?.send("pause")
        controlPc = false
        if (missing > 0) msg("$missing canciones de la cola no están en el teléfono")
    }

    /** What plays on this phone continues on the PC, at the same position. */
    fun transferToPc() {
        val c = controller
        val client = rc
        if (c == null || c.mediaItemCount == 0) {
            msg("El teléfono no está reproduciendo nada")
            return
        }
        if (client == null || !pcReachable) {
            msg("El PC no está conectado")
            return
        }
        val list = lQueueIds.mapNotNull { byId[it] }
        val curId = lId
        val start = list.indexOfFirst { it.id == curId }
        if (start < 0) return
        var from = (start - 100).coerceAtLeast(0)
        val to = (from + 300).coerceAtMost(list.size)
        from = (to - 300).coerceAtLeast(0)
        client.playTracks(list.subList(from, to).map { it.toEnt() }, start - from, c.currentPosition / 1000.0, true, "Desde el teléfono")
        c.pause()
        controlPc = true
    }
}