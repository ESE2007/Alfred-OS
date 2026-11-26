# Laboratorio Cámara v1.1

Cambios respecto a la v1.0: las claves ahora se prueban como arreglos (`int[]`, `byte[]`), que es el formato que usa la cámara de Infinix; antes se probaban como números sueltos y todas fallaban. Se agregaron pruebas para activar la detección de escena.

Prueba, una por una, las claves ocultas de Infinix y MediaTek que tu teléfono anunció en el diagnóstico,
para saber cuáles activan de verdad algún procesamiento (HDR, reducción de ruido por varias fotos, modo noche, etc.).

## Cómo compilar el APK

1. Abre la carpeta `CamaraLab` en Android Studio (`File > Open`) y espera el Gradle Sync (necesita internet).
2. **Build > Build Bundle(s) / APK(s) > Build APK(s)**. El archivo queda en `app/build/outputs/apk/debug/app-debug.apk`.
3. Instálalo en el teléfono (o conéctalo con Depuración USB y pulsa **Run**).

## Cómo usarlo

1. Apoya el teléfono quieto (en una mesa, contra un libro) apuntando a una escena con zonas muy claras y otras oscuras, por ejemplo una ventana con luz natural y el interior en sombra.
2. Abre la app, concede el permiso de cámara y pulsa **Iniciar pruebas**. Dura unos 3 a 6 minutos y toma unas 50 fotos. No muevas el teléfono ni salgas de la app.
3. Al terminar pulsa **Copiar informe** (o **Compartir**) y pégalo en el chat.

## Qué hace

- Toma 2 fotos base sin tocar nada, para medir la variación natural.
- Después toma una foto por cada valor de cada clave (unas 20 claves) y compara contra la base: tamaño del JPEG, brillo, sombras, luces quemadas, detalle, tiempo de captura y cambios en las claves que devuelve la cámara.
- Marca con `*` las pruebas donde algo cambió.
- Guarda todas las fotos en `Imágenes/CamaraLab` con el nombre de la prueba, para que las compares a ojo en la Galería.

## Notas

- Los valores probados (0, 1, 2…) son conjeturas, porque Infinix no documenta estas claves. Lo que se mide es si algo cambia.
- Si la cámara se bloquea o se cierra durante las pruebas, el informe sale parcial. Reabre la app y vuelve a iniciar; si se repite, reinicia el teléfono.
- Usa solo la cámara trasera principal.
- Cuando termines puedes borrar la carpeta `Imágenes/CamaraLab` desde la Galería.
