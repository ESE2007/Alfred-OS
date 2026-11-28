package com.tonada.mobile

import android.app.Application
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent

class TonadaApp : Application() {
    override fun onCreate() {
        super.onCreate()
        Model.init(this)
    }
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TonadaTheme {
                AppRoot()
            }
        }
    }

    // The relay connection lives only while the app is on screen.
    override fun onStart() {
        super.onStart()
        Model.onStart()
    }

    override fun onStop() {
        super.onStop()
        Model.onStop()
    }
}
