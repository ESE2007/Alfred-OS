# Tonada para Android — control remoto y reproductor móvil

App Android nativa (Kotlin + Jetpack Compose + Media3) que hace dos cosas:

1. **Reproductor propio**: lee la música del teléfono y la reproduce con notificación y controles en la pantalla de bloqueo.
2. **Control remoto del PC (tipo Spotify Connect)**: eliges «Reproducir en: tu PC», tocas una canción y suena en el PC; controlas pausa, siguiente, barra de posición, volumen, aleatorio, repetir, favoritas y la cola. Puedes **pasar lo que suena** del teléfono al PC y del PC al teléfono, en el mismo punto.

Funciona **por internet, sin estar en la misma red**: PC y teléfono solo tienen que estar vinculados. La comunicación pasa por un servidor MQTT público gratuito (por defecto HiveMQ), pero va **cifrada de extremo a extremo** (AES‑256‑GCM): el servidor solo ve mensajes ilegibles. La llave viaja únicamente en el código QR.

> Para que las canciones coincidan entre los dos equipos, ambos deben tener **los mismos archivos**: se reconocen por nombre de archivo + tamaño (o, si no coincide, por título + artista).

---

## 1. Compilar la app (una sola vez)

Necesitas **Android Studio** (gratis): https://developer.android.com/studio

1. Instálalo y ábrelo. En «Open» elige **esta carpeta** (`android`, la que contiene `settings.gradle.kts`).
2. Espera a que termine «Gradle sync» (la primera vez descarga Gradle 8.9 y las librerías; tarda unos minutos y necesita internet). Si te ofrece instalar el **Android SDK Platform 34** u otros componentes, acepta («Install missing SDK package»).
3. Menú **Build → Build Bundle(s) / APK(s) → Build APK(s)**.
4. Al terminar, pulsa «locate» en el aviso. El archivo es `app/build/outputs/apk/debug/app-debug.apk`.

Otra opción: activa «Depuración USB» en el teléfono, conéctalo y pulsa el botón ▶ (Run) de Android Studio; instala y abre la app directamente.

## 2. Instalar en el teléfono

1. Copia `app-debug.apk` al teléfono (cable, Drive, correo…).
2. Ábrelo. Android pedirá permitir «instalar apps de origen desconocido» para ese gestor de archivos: permítelo. (El APK es de depuración y no está firmado en la Play Store; es normal.)
3. Al abrir Tonada concede el permiso de **música/audio** y el de **notificaciones**.

## 3. Vincular con el PC

1. En Tonada para PC: **Ajustes → Control remoto móvil** → activa «Activar control remoto móvil» → **Mostrar código QR…**.
2. En el teléfono: pestaña **Dispositivos → Escanear código QR** (o pega el código de texto).
3. Toca la tarjeta del PC. Estado «En línea» = listo.

El código QR es una **llave**: quien lo tenga puede controlar tu reproductor. No lo compartas. Si dudas, en el PC usa «Desvincular todos los teléfonos» y vincula de nuevo.

## 4. Uso

- **Dispositivos → tarjeta del PC**: a partir de ahora, tocar una canción de *Biblioteca* la reproduce en el PC; la barra inferior y la pantalla «Reproduciendo» muestran y controlan el PC.
- **Dispositivos → tarjeta «Este teléfono»**: vuelve a reproducir en el móvil (el PC se pausa).
- **Seguir en el PC lo que suena aquí** / **Traer al teléfono lo que suena en el PC**: transfieren cola y posición.
- Menú ⋮ de cada canción: «Reproducir después» y «Añadir al final de la cola» (en el dispositivo activo).
- La conexión con el PC está activa mientras la app está en pantalla. Si la cierras, el PC sigue sonando y al volver se resincroniza.
- Tonada debe estar **abierto en el PC** con el control remoto activado.

## 5. Si algo falla

- *Gradle no sincroniza / error de SDK*: en Android Studio, File → Settings → Languages & Frameworks → Android SDK, instala «Android 14 (API 34)». Si falta JDK, usa el que trae Android Studio (Settings → Build Tools → Gradle → Gradle JDK = «jbr-17» o superior).
- *«Sin conexión» en el estado del PC*: el relé público puede estar saturado; en el PC, Ajustes → Control remoto móvil → «Servidor de enlace» permite elegir otro (después hay que escanear el QR otra vez).
- *Una canción no suena al «traer al teléfono»*: no está en el teléfono con el mismo nombre/tamaño ni mismo título+artista.
- Cualquier error de compilación: copia el texto completo del panel «Build» y mándalo; se corrige.

## 6. Protocolo

`docs/PROTOCOL.md` describe el formato de los mensajes por si quieres hacer otro cliente.
