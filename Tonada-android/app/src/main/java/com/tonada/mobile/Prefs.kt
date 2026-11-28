package com.tonada.mobile

import android.content.Context
import android.os.Build
import com.tonada.mobile.core.Crypto
import com.tonada.mobile.core.PairInfo
import java.net.URLEncoder

/** Small persistent settings: the paired PC and this phone's identity. */
class Prefs(ctx: Context) {
    private val sp = ctx.getSharedPreferences("tonada", Context.MODE_PRIVATE)

    val deviceId: String
        get() {
            var id = sp.getString("deviceId", null)
            if (id == null) {
                id = Crypto.randomHex(6)
                sp.edit().putString("deviceId", id).apply()
            }
            return id
        }

    var deviceName: String
        get() = sp.getString("deviceName", null) ?: (Build.MODEL ?: "Teléfono")
        set(v) {
            sp.edit().putString("deviceName", v).apply()
        }

    fun loadPair(): PairInfo? {
        val r = sp.getString("pairRoom", null) ?: return null
        val k = sp.getString("pairKey", null) ?: return null
        val b = sp.getString("pairBroker", null) ?: return null
        val n = sp.getString("pairName", null) ?: "Tonada PC"
        return PairInfo(r, k, b, n)
    }

    fun savePair(p: PairInfo?) {
        val e = sp.edit()
        if (p == null) {
            e.remove("pairRoom").remove("pairKey").remove("pairBroker").remove("pairName")
        } else {
            e.putString("pairRoom", p.room).putString("pairKey", p.key)
                .putString("pairBroker", p.broker).putString("pairName", p.name)
        }
        e.apply()
    }

    /** Same text as the PC's QR code, so the pairing can be moved between phones. */
    fun pairText(p: PairInfo): String =
        "tonada://pair?v=1&r=${p.room}&k=${p.key}&b=${URLEncoder.encode(p.broker, "UTF-8")}&n=${URLEncoder.encode(p.name, "UTF-8")}"
}
