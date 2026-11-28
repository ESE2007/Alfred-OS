# Cámara Auto 2 — versión 2.1

Cámara para el Infinix Note 40 Pro que usa el procesamiento propio de Infinix (el mismo de su app de cámara)
y elige el modo según la escena.

## Novedades de la 2.1

- **Última foto:** el círculo de abajo a la izquierda muestra la última foto. Tócalo para verla en la galería del teléfono.
- **Formatos:** botón `4:3` / `16:9` / `1:1` / `COMPLETA`. La vista previa muestra exactamente lo que saldrá en la foto. COMPLETA usa la proporción de la pantalla.
- **Flash:** botón `⚡` con OFF, AUTO, ON y `🔦 LUZ` (linterna encendida mientras apuntas y disparas).
- **Velocidad:** botón `✨ CALIDAD` / `⏱ RÁPIDO` (ver abajo).
- **Disparo más ágil:** en cuanto la cámara termina de procesar puedes volver a disparar; el guardado sigue en segundo plano.
- **Recuerda** el último modo, formato y velocidad usados.

## Modos

| Modo | Qué activa | Tarda (medido en el laboratorio) |
|---|---|---|
| NORMAL | Foto estándar | ~0.5 s |
| SÚPER RES | `com.transsion.megSuperresolutionMode`: más detalle | ~5 s |
| HDR | `com.transsion.hdrMode`: menos luces quemadas | ~3 s |
| NOCHE | `com.transsion.megSuperlowlightMode`: sombras más claras | ~7 s |
| AUTO | Elige uno según la escena | según el modo |

## Velocidad

Los tiempos de SÚPER RES, HDR y NOCHE los marca el procesamiento de Infinix; la app no puede acelerarlos.
Lo que sí se puede es evitar los modos lentos cuando no hacen falta:

- **✨ CALIDAD:** AUTO usa NOCHE con poca luz, HDR con alto contraste y SÚPER RES en el resto.
- **⏱ RÁPIDO:** AUTO usa NORMAL en escenas normales (~0.5 s), HDR con alto contraste y NOCHE solo si la escena es realmente oscura.
- Los modos elegidos a mano no cambian.

Además la vista previa es más liviana para dejar más recursos al procesamiento. Cada mensaje al guardar muestra los segundos que tardó la cámara, para que compares.

## Flash

- **OFF:** sin flash.
- **AUTO / ON:** destello normal. Solo funciona en modo NORMAL: con flash ON, cualquier modo se cambia a NORMAL; con flash AUTO, los modos de varias fotos no usan destello.
- **🔦 LUZ:** la linterna queda encendida durante las fotos y funciona con todos los modos. Se apaga al salir de la app.

## Resolución y guardado

- Las fotos se guardan en `Imágenes/CamaraAuto2` (el nombre incluye el modo).
- En **4:3** se guarda la imagen tal como sale de la cámara, sin tocarla: **3968×2976 (11.8 MP)**, el mayor tamaño JPEG que el teléfono ofrece a las apps, con calidad 100. Los 108 MP del sensor no se entregan a apps de terceros.
- **16:9, 1:1 y COMPLETA** se recortan del centro de esa misma imagen, así que tienen menos píxeles: 16:9 ≈ 3968×2232 (8.9 MP), 1:1 = 2976×2976 (8.9 MP), COMPLETA ≈ 7 a 8 MP según la pantalla. Si quieres el máximo de resolución, usa 4:3.
- El mensaje al guardar indica la resolución real de cada foto.

## Cómo decide AUTO

Cada medio segundo mide el brillo real de la escena (ISO, tiempo de exposición y apertura) y cuánta parte de la imagen está quemada o en sombras. La escena debe mantenerse ~1.5 s antes de cambiar. Los umbrales y la elección están en `Scene.kt`.

## Uso

- Toca la pantalla para enfocar. Pellizca para zoom (hasta 15x).
- En SÚPER RES, HDR y NOCHE aparece "Procesando…": **no muevas el teléfono** hasta que termine.

## Cómo compilar el APK

1. Abre la carpeta `CamaraAuto2` en Android Studio (`File > Open`) y espera el Gradle Sync (necesita internet).
2. **Build > Build Bundle(s) / APK(s) > Build APK(s)**. El APK queda en `app/build/outputs/apk/debug/app-debug.apk`.
3. Instálalo en el teléfono: reemplaza la versión 2.0 y conserva tus fotos.

## Límites

- Solo cámara trasera principal (sin frontal ni ultra gran angular).
- Pensada para este modelo: usa claves de Infinix que otros teléfonos no tienen.
- Los modos se probaron en el laboratorio con una sola escena de luz media.
