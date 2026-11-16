# Alfred Móvil (cliente Android para Alfred 3.2.x)

App Android que controla tu Alfred del PC usando su **API de control remoto** (la que trae `alfred_3_2_2.pyw`
en ☰ Menú → Remoto). No hace falta tocar el código de Alfred.

Qué hace la app:
- Botones rápidos (volumen, play/pausa, siguiente, captura, bloquear…).
- Escribir una orden, o dictarla con el micrófono del teléfono (🎤).
- Ver en vivo lo que Alfred oye, hace y responde.
- 📖 Lista de todos los comandos de tu Alfred, con buscador (se lee del PC, siempre actualizada).
- La clave se guarda cifrada en el Android Keystore.

## 1. Preparar el PC
1. En Alfred: ☰ Menú → **Remoto**.
2. Activa **«Activar el control remoto»** y **«Permitir otros dispositivos de mi red Wi-Fi»**.
3. Pulsa **«Copiar enlace»** (algo como `http://192.168.1.20:47654/#t=CLAVE`) y envíatelo al teléfono
   (WhatsApp, correo, notas…).
4. Si Windows pregunta por el Firewall, permite Python en **redes privadas**.

## 2. Conseguir el APK (elige una vía)

**A) Sin instalar nada (GitHub Actions, gratis)**
1. Crea un repositorio en GitHub y sube todo el contenido de esta carpeta.
2. Pestaña *Actions* → «Compilar APK» → *Run workflow* (o se lanza solo al subir).
3. Al terminar, descarga el artefacto **Alfred-Movil-APK** (contiene `app-debug.apk`).

**B) Android Studio**
1. *Open* → selecciona esta carpeta (deja que sincronice Gradle).
2. *Build → Build Bundle(s) / APK(s) → Build APK(s)*.
3. El archivo queda en `app/build/outputs/apk/debug/app-debug.apk`.

**C) Línea de comandos** (con JDK 17 y Android SDK): `gradle assembleDebug`

## 3. Instalar y conectar
1. Pasa el APK al teléfono y ábrelo (Android pedirá permitir «instalar apps desconocidas» para tu gestor de archivos).
2. Abre **Alfred**, pega el enlace en la ventana de ajustes (⚙) y pulsa **Guardar y probar**.
   También sirve escribir solo la IP del PC y la clave.

## Notas
- El teléfono y el PC deben estar en la misma Wi-Fi. Fuera de casa, usa una red privada como **Tailscale**
  (Alfred acepta sus direcciones 100.x.x.x); Alfred nunca acepta direcciones públicas de internet.
- La app solo sigue los eventos mientras está abierta (no corre en segundo plano).
- Acciones delicadas (apagar, reiniciar…): Alfred 3.2.2 exige confirmarlas con la voz en el PC; una orden remota no puede decir «sí».
- Si activaste HTTPS en Alfred con un certificado propio (autofirmado), esta versión no lo aceptará: usa HTTP en tu red local.
- Si cambias la clave en Alfred («Clave nueva»), vuelve a pegar el enlace nuevo en ⚙.
- El APK es de depuración (firmado con la llave de depuración): sirve para uso personal.
