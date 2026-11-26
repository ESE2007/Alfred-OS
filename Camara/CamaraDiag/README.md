# Diagnóstico Cámara

App de solo lectura que revisa qué le permite hacer tu teléfono a una app de terceros con la cámara.
No toma fotos ni pide permisos.

## Qué reporta

- Modelo, SoC y versión de Android (para saber si tienes el Note 40 Pro 4G o el 5G).
- Por cada cámara: nivel de Camera2, RAW, control manual de ISO/obturador, máxima resolución del sensor, tamaños de foto, modos de escena, reducción de ruido y nitidez.
- Extensiones del fabricante (HDR, Noche, Bokeh, Auto, Retoque facial) por Camera2 y por CameraX.
- Claves no estándar agregadas por el fabricante o MediaTek.
- Qué apps de cámara atienden la acción "tomar foto" (para ver si la cámara de Infinix puede llamarse desde otra app).

## Cómo compilar el APK

1. Abre la carpeta `CamaraDiag` en Android Studio (`File > Open`). Espera el Gradle Sync (necesita internet).
2. Menú **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
3. Al terminar, pulsa *locate* en el aviso. El archivo queda en `app/build/outputs/apk/debug/app-debug.apk`.
4. Pásalo al teléfono e instálalo (permite "instalar apps de origen desconocido" para el explorador de archivos que uses).

También puedes conectar el teléfono con Depuración USB y pulsar **Run ▶**.

## Después

Pulsa **Copiar informe** o **Compartir** y pega el texto en el chat.
