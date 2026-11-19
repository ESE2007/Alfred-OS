# Controlar Alfred desde el móvil por internet, con tu cuenta de Google

Esta guía acompaña a `alfred_3_3_0.pyw` y a la carpeta `alfred_movil/`.

## Cómo funciona

Alfred no abre ningún puerto en tu router. El PC se conecta hacia fuera, por HTTPS, a una base de datos de Firebase que hace de buzón. El móvil deja ahí sus órdenes y el PC las recoge al instante y las borra.

- El móvil entra con «Continuar con Google».
- El PC tiene su propia identidad anónima de Firebase. No guarda ni usa tu cuenta de Google.
- Se vinculan escaneando un código QR que vale 5 minutos y para un solo móvil. Además, Alfred te pregunta en el PC si lo aceptas.
- Las reglas de la base de datos solo dejan dar órdenes a los móviles vinculados, y el PC lo vuelve a comprobar antes de ejecutar.

En la nube solo quedan el estado de Alfred, las últimas 60 líneas del registro, el correo de los móviles vinculados y las órdenes pendientes (se borran al leerlas). Lo dictado, lo escrito y el portapapeles no se publican, igual que en la API local.

## Puesta en marcha (una sola vez, unos 15 minutos)

Esto lo haces tú como autor de Alfred. Quien use Alfred después solo hace el apartado «Uso diario».

1. **Crea un proyecto** en <https://console.firebase.google.com> (plan gratuito Spark).
2. **Authentication → Sign-in method.** Activa **Google** (te pide un correo de soporte) y **Anónimo**.
3. **Realtime Database → Crear base de datos.** Elige la región y empieza en modo bloqueado. Copia su dirección, por ejemplo `https://mi-alfred-default-rtdb.firebaseio.com`.
4. **Configuración del proyecto → General.** Copia la **Clave de API web**. No es secreta: va dentro de cualquier web de Firebase.
5. **Sube la página y las reglas.** Instala Node.js y luego, en una terminal:

   ```
   npm install -g firebase-tools
   firebase login
   cd alfred_movil
   firebase use --add        (elige tu proyecto)
   firebase deploy
   ```

   Esto publica `public/index.html` en `https://<proyecto>.web.app` y las reglas de `database.rules.json`. Si prefieres no usar la terminal, pega el contenido de `database.rules.json` en Realtime Database → Reglas → Publicar. La página sí necesita el despliegue (o cualquier otro alojamiento web con HTTPS).
6. **Dile a Alfred tus tres datos.** Pon en `alfred_config.json` (así también sirve para instalarlo en otras PCs sin tocar el código):

   ```json
   "nube_api_key": "AIza...",
   "nube_db_url": "https://mi-alfred-default-rtdb.firebaseio.com",
   "nube_web_url": "https://mi-alfred.web.app"
   ```

   O escríbelos en las constantes `NUBE_API_KEY`, `NUBE_DB_URL` y `NUBE_WEB_URL` del `.pyw`.

Si alojas la página fuera de Firebase Hosting (GitHub Pages u otro), rellena `CONFIG_MANUAL` al inicio del script de `index.html` y añade ese dominio en Authentication → Settings → Dominios autorizados.

## Uso diario

1. En el PC: **☰ Menú → Remoto → Activar el enlace por internet.** Pulsa **Vincular un móvil**; aparece un código QR.
2. En el móvil: escanea el QR con la cámara, pulsa **Continuar con Google** y entra.
3. En el PC aparece un aviso: «¿Quieres que… controle este PC?». Pulsa **Sí** solo si acabas de escanear tú el código.
4. Listo. La próxima vez abre la misma página (conviene «Añadir a pantalla de inicio»): ya no hace falta QR.

Para quitar un móvil: **☰ Menú → Remoto → Quitar** junto a su correo. Si no tienes acceso al PC, borra el nodo `pcs/<id>/owners/<uid>` en Realtime Database desde la consola de Firebase.

Si abres el enlace dentro de otra aplicación (Instagram, WhatsApp…), Google no deja iniciar sesión: ábrelo en Chrome o Safari.

## Seguridad: qué debes tener en cuenta

- Un móvil vinculado puede dar las mismas órdenes que tu voz en el PC: abrir programas, escribir texto, mover archivos, bloquear. Una orden remota no puede confirmar una acción delicada (apagar, borrar…): eso se sigue confirmando con la voz en el PC.
- Quien controle esa cuenta de Google en un móvil vinculado controla Alfred. Activa la verificación en dos pasos de la cuenta y quita los móviles que pierdas o vendas.
- Las órdenes que llegan con más de 45 segundos de retraso se descartan (por ejemplo, si el PC estaba sin internet), para que una orden antigua no se ejecute de golpe al volver. Hay un tope de 30 órdenes por minuto y 5 móviles vinculados.
- La página no lleva una política de seguridad de contenido (CSP) porque no pude probarla con el inicio de sesión de Google; sí lleva las cabeceras básicas en `firebase.json`.
- Si repartes Alfred a otras personas con tu mismo proyecto, cada PC mantiene una conexión abierta con la base de datos. Revisa en la consola los límites de conexiones simultáneas del plan gratuito, porque cambian con el tiempo.

## Si algo falla

Alfred muestra el motivo en **☰ Menú → Remoto**:

| Mensaje | Qué hacer |
|---|---|
| Falta la clave de API o la dirección… | Completa los tres datos del paso 6. |
| Activa el método de acceso «Anónimo»… | Paso 2: habilita Anónimo en Authentication. |
| La clave de API no es válida | Revisa `nube_api_key` (paso 4). |
| La base de datos rechazó al PC… | Publica las reglas (paso 5). |
| La dirección de la base de datos no existe | Revisa `nube_db_url` (paso 3). Debe acabar en `firebaseio.com` o `firebasedatabase.app`. |
| «El código no es válido o ya caducó» en el móvil | El QR vale 5 minutos y un solo uso: genera otro. |
| El PC no responde y el móvil dice «sin conexión» | Alfred debe estar abierto y el PC con internet y sin suspender. |

## Alternativa sin proyecto propio: Tailscale

Si no quieres montar Firebase, Tailscale hace lo mismo con otra cuenta de Google y sin servidor tuyo:

1. Instala Tailscale en el PC y en el móvil e inicia sesión con la misma cuenta de Google en ambos.
2. En Alfred: **☰ Menú → Remoto**, activa el control remoto y **Permitir otros dispositivos de mi red**. En la versión 3.3 el enlace con la dirección `100.x.y.z` de Tailscale aparece entre los enlaces.
3. Abre ese enlace en el móvil con Tailscale conectado.

Es más simple de montar, pero hace falta la app de Tailscale en el móvil (en Android ocupa la conexión VPN) y la conexión va por HTTP dentro del túnel cifrado de Tailscale.

## Lo que no está probado

La lógica del PC (conexión, vinculación por QR, órdenes, descarte de órdenes viejas, límite por minuto, reconexión al caducar el token) se probó contra un Firebase simulado en local. No se probó contra Firebase y Google reales: ni la página del móvil con el inicio de sesión de Google, ni las reglas publicadas. En la primera prueba real, comprueba por este orden: que Alfred muestre «Conectado», que el QR se vea, que el móvil entre con Google, que aparezca el aviso en el PC y que una orden como «qué hora es» llegue y se responda.
