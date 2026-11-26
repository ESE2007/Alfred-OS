package com.camaraauto2

/**
 * Modos de captura. Cada uno activa una clave del procesamiento de Infinix
 * (la que el laboratorio comprobó que sí cambia la foto en el Note 40 Pro).
 */
enum class CaptureMode(val label: String, val keyName: String?, val approxSeconds: Int) {
    NORMAL("NORMAL", null, 1),
    SUPER_RES("SÚPER RES", "com.transsion.megSuperresolutionMode", 5),
    HDR("HDR", "com.transsion.hdrMode", 3),
    NIGHT("NOCHE", "com.transsion.megSuperlowlightMode", 7)
}

/** Lo que el usuario elige con el botón de modo. AUTO decide según la escena. */
enum class UiMode(val label: String, val capture: CaptureMode?) {
    AUTO("AUTO", null),
    NORMAL("NORMAL", CaptureMode.NORMAL),
    SUPER_RES("SÚPER RES", CaptureMode.SUPER_RES),
    HDR("HDR", CaptureMode.HDR),
    NIGHT("NOCHE", CaptureMode.NIGHT)
}

/** Tipos de escena y la compensación de exposición (en pasos EV) que se aplica a cada una. */
enum class Scene(val label: String, val ev: Float) {
    NIGHT("🌙 Noche", 0f),
    LOW_LIGHT("💡 Poca luz", 0f),
    HIGH_CONTRAST("🌗 Alto contraste", -0.3f),
    BRIGHT("☀️ Mucha luz", -0.5f),
    NORMAL("🙂 Escena normal", 0f)
}

/**
 * Clasifica la escena.
 *  - ev100: brillo real de la escena (a partir de ISO, tiempo de exposición y apertura).
 *  - clipped: fracción de píxeles casi blancos (luces quemadas).
 *  - dark: fracción de píxeles casi negros (sombras cerradas).
 * Los umbrales se pueden ajustar aquí.
 */
fun classifyScene(ev100: Float, clipped: Float, dark: Float): Scene = when {
    ev100 < 3.5f -> Scene.NIGHT
    clipped > 0.10f && dark > 0.20f -> Scene.HIGH_CONTRAST
    ev100 < 6f -> Scene.LOW_LIGHT
    ev100 > 13.5f -> Scene.BRIGHT
    else -> Scene.NORMAL
}

/** Qué modo usa AUTO para cada escena. */
fun modeForScene(scene: Scene): CaptureMode = when (scene) {
    Scene.NIGHT, Scene.LOW_LIGHT -> CaptureMode.NIGHT
    Scene.HIGH_CONTRAST -> CaptureMode.HDR
    Scene.BRIGHT, Scene.NORMAL -> CaptureMode.SUPER_RES
}
