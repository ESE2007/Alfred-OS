plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.alfred.remoto"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.alfred.remoto"
        minSdk = 24
        targetSdk = 34
        versionCode = 2
        versionName = "2.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    // Lector de códigos QR de Google Play Services: no pide permiso de cámara y no añade peso a la app.
    implementation("com.google.android.gms:play-services-code-scanner:16.1.0")
}
