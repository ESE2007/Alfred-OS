# Cámara Auto 2

Cámara para el Infinix Note 40 Pro que usa el procesamiento propio de Infinix (el mismo de su app de cámara)
y elige el modo según la escena.

## Modos

| Modo | Qué activa | Tarda |
|---|---|---|
| NORMAL | Foto estándar, sin procesamiento extra | ~0.5 s |
| SÚPER RES | `com.transsion.megSuperresolutionMode`: más detalle (varias fotos combinadas) | ~5 s |
| HDR | `com.transsion.hdrMode`: menos luces quemadas | ~3 s |
| NOCHE | `com.transsion.megSuperlowlightMode`: sombras más claras con poca luz | ~7 s |
| AUTO | Elige uno de los anteriores según la escena | según el modo |

El botón **MODO** los recorre en ese orden.

## Cómo decide AUTO

Cada medio segundo mide el brillo real de la escena (ISO, tiempo de exposición y apertura) y cuánta parte de la imagen está quemada o en sombras.
La escena debe mantenerse ~1.5 s antes de cambiar.

- Noche o poca luz (por debajo de ~EV 6, unos 160 lux): NOCHE
- Alto contraste (muchas luces quemadas y muchas sombras): HDR
- Resto de escenas: SÚPER RES
- Además ajusta la exposición: −0.5 EV con mucha luz y −0.3 EV con alto contraste, para proteger las luces.

Los umbrales y la elección están en `Scene.kt` (`classifyScene` y `modeForScene`) por si quieres cambiarlos.

## Uso

- Toca la pantalla para enfocar y medir luz. Pellizca para zoom (hasta 15x).
- Al disparar en SÚPER RES, HDR o NOCHE aparece "Procesando…": **no muevas el teléfono** hasta que termine.
- Las fotos se guardan en `Imágenes/CamaraAuto2`. El nombre incluye el modo usado.
- Si la cámara no confirma que aplicó el modo, la app lo avisa en el mensaje al guardar.

## Cómo compilar el APK

1. Abre la carpeta `CamaraAuto2` en Android Studio (`File > Open`) y espera el Gradle Sync (necesita internet).
2. **Build > Build Bundle(s) / APK(s) > Build APK(s)**. El APK queda en `app/build/outputs/apk/debug/app-debug.apk`.
3. Instálalo en el teléfono (o conéctalo con Depuración USB y pulsa **Run**).

## Límites actuales

- Solo cámara trasera principal (sin frontal, sin flash, sin ultra gran angular).
- Pensada para este modelo: usa claves de Infinix que otros teléfonos no tienen (en ese caso toma una foto normal y lo avisa).
- Las pruebas del laboratorio se hicieron con una sola escena de luz media. Si algún modo se ve mal en otra situación, cámbialo a mano con el botón MODO y cuéntame qué pasó.
