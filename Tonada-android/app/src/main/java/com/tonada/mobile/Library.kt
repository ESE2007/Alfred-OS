package com.tonada.mobile

import android.content.ContentUris
import android.content.Context
import android.graphics.Bitmap
import android.net.Uri
import android.provider.MediaStore
import android.util.LruCache
import android.util.Size
import com.tonada.mobile.core.Ent
import com.tonada.mobile.core.Identity

/** A song of the phone's own library (MediaStore). */
data class Track(
    val id: Long,
    val title: String,
    val artist: String,
    val album: String,
    val albumId: Long,
    val durationMs: Long,
    val fileName: String,
    val size: Long,
    val dateAdded: Long,
    val trackNo: Int = 0,
) {
    /** Normalised text used by the search box (computed once, on first search). */
    val search: String by lazy { Identity.norm(title + artist + album) }

    val uri: Uri get() = ContentUris.withAppendedId(MediaStore.Audio.Media.EXTERNAL_CONTENT_URI, id)
    val albumArtUri: Uri get() = ContentUris.withAppendedId(Uri.parse("content://media/external/audio/albumart"), albumId)

    /** The way both devices recognise the same song (docs/PROTOCOL.md). */
    fun toEnt(): Ent = Ent(
        Identity.keyF(fileName, size),
        Identity.keyT(artist, title),
        title, artist, album, (durationMs / 1000).toInt(),
    )
}

object Library {
    fun scan(ctx: Context): List<Track> {
        val out = ArrayList<Track>()
        val proj = arrayOf(
            MediaStore.Audio.Media._ID,
            MediaStore.Audio.Media.TITLE,
            MediaStore.Audio.Media.ARTIST,
            MediaStore.Audio.Media.ALBUM,
            MediaStore.Audio.Media.ALBUM_ID,
            MediaStore.Audio.Media.DURATION,
            MediaStore.Audio.Media.DISPLAY_NAME,
            MediaStore.Audio.Media.SIZE,
            MediaStore.Audio.Media.DATE_ADDED,
            MediaStore.Audio.Media.TRACK,
        )
        val sel = MediaStore.Audio.Media.IS_MUSIC + " != 0"
        val c = ctx.contentResolver.query(
            MediaStore.Audio.Media.EXTERNAL_CONTENT_URI, proj, sel, null, MediaStore.Audio.Media.TITLE + " COLLATE NOCASE ASC"
        ) ?: return out
        c.use {
            val iId = it.getColumnIndexOrThrow(MediaStore.Audio.Media._ID)
            val iT = it.getColumnIndexOrThrow(MediaStore.Audio.Media.TITLE)
            val iAr = it.getColumnIndexOrThrow(MediaStore.Audio.Media.ARTIST)
            val iAl = it.getColumnIndexOrThrow(MediaStore.Audio.Media.ALBUM)
            val iAlId = it.getColumnIndexOrThrow(MediaStore.Audio.Media.ALBUM_ID)
            val iD = it.getColumnIndexOrThrow(MediaStore.Audio.Media.DURATION)
            val iN = it.getColumnIndexOrThrow(MediaStore.Audio.Media.DISPLAY_NAME)
            val iS = it.getColumnIndexOrThrow(MediaStore.Audio.Media.SIZE)
            val iDa = it.getColumnIndexOrThrow(MediaStore.Audio.Media.DATE_ADDED)
            val iTr = it.getColumnIndexOrThrow(MediaStore.Audio.Media.TRACK)
            while (it.moveToNext()) {
                val artist = it.getString(iAr) ?: ""
                out.add(
                    Track(
                        id = it.getLong(iId),
                        title = it.getString(iT) ?: "",
                        artist = if (artist == "<unknown>") "" else artist,
                        album = it.getString(iAl) ?: "",
                        albumId = it.getLong(iAlId),
                        durationMs = it.getLong(iD),
                        fileName = it.getString(iN) ?: "",
                        size = it.getLong(iS),
                        dateAdded = it.getLong(iDa),
                        trackNo = it.getInt(iTr),
                    )
                )
            }
        }
        return out
    }

    private val thumbs = object : LruCache<Long, Bitmap>(60) {}
    private val noThumb = HashSet<Long>()

    /** Cover of a track (blocking: call from a background thread). */
    fun thumbnail(ctx: Context, t: Track): Bitmap? {
        thumbs.get(t.id)?.let { return it }
        synchronized(noThumb) { if (noThumb.contains(t.id)) return null }
        return try {
            val b = ctx.contentResolver.loadThumbnail(t.uri, Size(256, 256), null)
            thumbs.put(t.id, b)
            b
        } catch (e: Exception) {
            synchronized(noThumb) { noThumb.add(t.id) }
            null
        }
    }
}
