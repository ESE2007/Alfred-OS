# Alfred Móvil 2.0 (cliente Android para Alfred 3.5)

Controla tu Alfred del PC desde el teléfono. **Requiere `alfred_3_5_0.pyw`** (o posterior) en el PC: la vinculación con QR,
las claves por teléfono y los límites de seguridad viven allí. Con un Alfred 3.4 antiguo sigue funcionando el enlace
clásico (⚙ → «Pegar enlace»), pero sin QR ni límites por comando.

## Novedades de la 2.0
- **Vincular con un QR**: en el PC `☰ Menú → Remoto → «Vincular teléfono»`, en la app «Escanear código QR». Sin IPs ni claves.
- **Funciona dentro y fuera de casa**: el QR lleva todas las direcciones del PC (Wi-Fi y Tailscale). La app prueba todas a
  la vez, se queda con la que responde y se reconecta sola si cambias de Wi-Fi a datos móviles. Si el router le da otra IP al PC,
  lo vuelve a encontrar en tu Wi-Fi.
- **Una clave por teléfono**, que no viaja por la red al vincular (se deriva del código del QR). Se puede quitar desde el PC.
- **Pantalla de Control** con música, volumen y brillo (deslizadores), bloquear, captura, abrir apps, ventanas,
  flechas/zoom para vídeos y presentaciones, temporizadores…
- **Catálogo de comandos con candados**: cada comando muestra si es libre, si pide confirmación o si solo se da desde el PC.
- **Confirmaciones en el teléfono** para lo delicado pero útil (suspender, hibernar, cerrar programas).
- **Teclado y ratón a distancia**, solo si lo activas en el PC (`Remoto → Avanzado`).

## Qué se puede hacer desde el móvil
La regla la aplica **el PC** con cada orden, no solo la app (así una app modificada tampoco puede saltársela).

| Nivel | Ejemplos |
|---|---|
| Libre | música, volumen, brillo, captura, bloquear, abrir apps y webs, ventanas, temporizador, notas, estado del PC, flechas y zoom |
| Pide confirmación en el teléfono | suspender, hibernar, cerrar un programa o ventana |
| Solo con «Avanzado» activado en el PC | escribir texto, atajos de teclado (copiar, pegar, Enter…), clics y mover el ratón |
| Nunca desde el móvil | apagar, reiniciar, cerrar sesión, desconectar el Wi-Fi, cerrar Alfred, abrir consolas (cmd, PowerShell) o el registro, vaciar la papelera, forzar el cierre de programas |

Un comando que Alfred añada en el futuro queda **bloqueado** hasta que se clasifique en `POLITICA_REMOTA` (en el `.pyw`).
Los comandos de «Mis comandos» se clasifican por lo que hacen: los que borran, o llaman a algo bloqueado, no se lanzan desde el móvil.

## 1. Preparar el PC
1. Cierra Alfred y arranca `alfred_3_5_0.pyw`.
2. `☰ Menú → Remoto → Vincular teléfono` (activa el control remoto si no lo estaba).
3. Si Windows pregunta por el Firewall, permite **solo «Redes privadas»**.

## 2. Conseguir el APK (elige una vía)
**A) GitHub Actions (gratis, sin instalar nada)**: sube esta carpeta a un repositorio → pestaña *Actions* → «Compilar APK» →
descarga el artefacto **Alfred-Movil-APK** (`app-debug.apk`).

**B) Android Studio**: *Open* → esta carpeta → *Build → Build APK(s)* → `app/build/outputs/apk/debug/app-debug.apk`.

**C) Línea de comandos** (JDK 17 + Android SDK): `gradle assembleDebug`

## 3. Vincular
1. Instala el APK (Android pedirá permitir «instalar apps desconocidas»). Si ya tenías la 1.0, se actualiza encima y conserva su vinculación.
2. Abre **Alfred** → **Escanear código QR** → apunta a la pantalla del PC. Listo.
   - El lector de QR es el de Google Play Services (no pide permiso de cámara). Si tu teléfono no lo tiene: en el PC «Copiar enlace»
     y en la app «Pegar enlace».

## 4. Usarlo fuera de casa
Alfred nunca se abre a internet: acepta solo direcciones privadas. Para llegar desde fuera se usa **Tailscale** (gratis, cifrado):
1. Instala Tailscale en el PC y en el teléfono e inicia sesión con la **misma cuenta**.
2. En el PC, en la ventana de vincular, pulsa «Código nuevo» y escanéalo otra vez (para que el QR incluya la dirección de Tailscale).
3. Desde entonces la app elige sola: Wi-Fi de casa si estás en casa, Tailscale si no. En la parte superior verás por cuál va.

La conexión por Wi-Fi de casa va en HTTP sin cifrar (como antes): úsala en una red de confianza. Por Tailscale va cifrada.

## Notas técnicas
- Protocolo de vinculación: el QR lleva un código de un solo uso (10 min, 5 intentos). El teléfono manda un HMAC-SHA256 del código
  (la «prueba»); la clave del teléfono es `HMAC(código, "token|nonce|nombre")` y se calcula en ambos lados, **no se transmite**. El PC solo
  guarda su SHA-256. La clave en el teléfono se cifra con el Android Keystore.
- La app solo sigue los eventos mientras está a la vista (no corre en segundo plano).
- Si el PC cambia de IP, la app lo busca en tu Wi-Fi (puerto 47654; necesita que el PC use el puerto habitual).
- Si activaste HTTPS con certificado propio en Alfred, esta app no lo acepta: usa HTTP en tu red o Tailscale.
- Para subir `targetSdk` a 37 (Android 17) habrá que declarar y pedir el permiso de red local; con `targetSdk 34` no afecta.
- El APK es de depuración (firmado con la llave de depuración): sirve para uso personal.
