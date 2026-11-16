# Control remoto de Alfred / Sara OS (API v1)

Alfred 3.2 incluye un servidor HTTP + JSON pensado como base para una versión móvil (o cualquier otro cliente:
atajos de iOS/Android, Home Assistant, otro PC, scripts).

## Activarlo

1. En el PC: **☰ Menú → Remoto → Activar el control remoto**.
2. Para usarlo desde el móvil, activa también **«Permitir otros dispositivos de mi red Wi-Fi»**.
3. Copia el enlace (lleva la clave) y ábrelo en el navegador del móvil, que debe estar en la misma Wi-Fi.
   Verás una página con botones rápidos, el registro en vivo y una caja para escribir órdenes.
4. La primera vez, Windows puede preguntar por el Firewall: permite solo **Redes privadas**.

Está **desactivado por defecto**. Con «red» apagado solo responde a este mismo PC.

## Seguridad

- Toda la API (salvo `/` y `/api/ping`) exige la clave: `Authorization: Bearer <clave>` (o `X-Alfred-Token`, o `?t=`).
- Solo se aceptan direcciones **loopback, privadas, link-local y Tailscale (100.64.0.0/10)**; nunca IPs públicas.
- 8 claves incorrectas seguidas desde una IP → bloqueo de 5 minutos.
- La conexión es **HTTP sin cifrar**: úsalo solo en una red de confianza (o por Tailscale/VPN). Opcionalmente puedes
  poner HTTPS con un certificado propio (ver claves de configuración).
- Una orden remota puede hacer lo mismo que tu voz (abrir programas, teclear, bloquear…). Las acciones delicadas
  (apagar, reiniciar, borrar) siguen pidiendo confirmación: envía `sí` como otra orden.
- «🔑 Clave nueva» invalida todos los dispositivos enlazados.

## Endpoints

| Método | Ruta | Clave | Descripción |
|---|---|---|---|
| GET | `/` | no | Página web para el móvil |
| GET | `/api/ping` | no | `{"app":"alfred","api":1}` (para comprobar que es un Alfred) |
| GET | `/api/estado` | sí | Nombre, versión, si escucha, idioma, dictado, reproductor activo |
| GET | `/api/comandos` | sí | Lista de comandos: `id`, `ejemplo`, `descripcion`, `seccion` |
| POST | `/api/orden` | sí | Ejecuta una orden escrita (no hace falta decir el nombre) |
| POST | `/api/decir` | sí | Hace que el PC diga un texto en voz alta |
| GET | `/api/eventos` | sí | Lo que Alfred oye, hace y dice (sondeo largo) |

### `POST /api/orden`

```json
{ "texto": "reproduce la carpeta mis canciones", "espera": 4 }
```

`espera` (0–15 s, por defecto 4) es lo máximo que aguarda la respuesta antes de contestar. Respuesta:

```json
{ "ok": true, "ultimo": 128,
  "eventos": [ {"id":127,"hora":"20:04:03","tipo":"orden","texto":"📱 reproduce la carpeta mis canciones"},
               {"id":128,"hora":"20:04:03","tipo":"voz","texto":"🗣️ Reproduciendo Mis canciones."} ] }
```

### `GET /api/eventos?desde=N&espera=20&ultimos=40`

Devuelve los eventos con `id > N`. Si no hay, espera hasta `espera` segundos (máx. 25) a que aparezca alguno.
Con `ultimos=K` y `desde=0` devuelve los K más recientes (primera conexión). `tipo` es `orden`, `voz`, `aviso` o `log`.

## Ejemplos

```bash
CLAVE="..."            # la del enlace (?t=...)
HOST="http://192.168.1.50:47654"

curl -H "Authorization: Bearer $CLAVE" $HOST/api/estado
curl -H "Authorization: Bearer $CLAVE" -H "Content-Type: application/json" \
     -d '{"texto":"siguiente canción"}' $HOST/api/orden
```

El puerto por defecto es **47654** (si está ocupado prueba hasta 47659; el enlace del menú muestra el real).

## Cómo construir la app móvil encima

1. **Enlazar**: pedir host + clave (o abrir el enlace `?t=`), comprobar `/api/ping` y guardar la clave.
2. **Pantalla principal**: `/api/estado` cada ~10 s; botones rápidos que envían órdenes a `/api/orden`.
3. **Registro en vivo**: bucle de `GET /api/eventos?desde=<último id>&espera=20`; al reconectar, repite con el último `id`.
4. **Menú de comandos**: generado desde `/api/comandos` (cada `ejemplo` es una orden válida).
5. Las respuestas hoy también se **hablan en el PC**; si tu app prefiere solo texto, es el siguiente paso natural
   (un parámetro para silenciar la voz en las órdenes remotas).

## Claves de configuración (`alfred_config.json`)

| Clave | Por defecto | Para qué |
|---|---|---|
| `remoto_activo` | `false` | Enciende el servidor |
| `remoto_lan` | `false` | Escucha en toda la red (si no, solo este PC) |
| `remoto_token` | (se genera) | Clave de acceso |
| `remoto_cors` | vacío | Origen permitido si un cliente web de otro origen usa la API |
| `remoto_cert` / `remoto_clave_tls` | vacío | Rutas a un certificado y su clave privada para servir por HTTPS |
