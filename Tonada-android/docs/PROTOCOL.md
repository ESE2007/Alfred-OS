# Tonada Remote – protocolo v1

Control remoto del reproductor del PC desde la app móvil, desde cualquier red, sin servidor propio.
Los mensajes viajan por un broker **MQTT público** (MQTT 3.1.1 sobre WebSocket seguro) y van **cifrados de extremo a extremo**:
el broker solo ve bytes aleatorios.

## 1. Vinculación (QR)
El PC genera una vez `room` (16 bytes aleatorios, 32 hex) y `key` (32 bytes aleatorios, AES-256).
QR / código de texto:

```
tonada://pair?v=1&r=<room hex>&k=<key base64url sin relleno>&b=<url del broker, urlencoded>&n=<nombre del PC, urlencoded>
```
Cualquiera que tenga room+key puede controlar el PC: el QR es una contraseña. "Desvincular todo" genera un room y key nuevos.

## 2. Transporte
- Broker por defecto: `wss://broker.hivemq.com:8884/mqtt` (también `wss://broker.emqx.io:8084/mqtt`, `wss://test.mosquitto.org:8081/`).
- Sub-protocolo WebSocket `mqtt`. Solo QoS 0. Keep-alive 30 s (PINGREQ cada 15 s). Sesión limpia.
- Temas (room = hex de 32 caracteres):
  - `tonada/v1/<room>/pc`  PC → móviles  (`state` con *retain*, `queue`, `art`, `ack`)
  - `tonada/v1/<room>/m`   móviles → PC  (`cmd`)
- El PC registra un *last will* en `/pc` (retain) con un `state` cifrado `{t:"state",off:1,ts:0}` para marcarse desconectado.
  Al detener el remoto limpiamente publica ese mismo `state` con `off:1`.

## 3. Cifrado de cada mensaje
`payload = IV(12 bytes aleatorios) ‖ AES-256-GCM(JSON UTF-8)` donde el resultado de GCM es `ciphertext ‖ tag(16)`,
con **AAD = el nombre del tema en UTF-8**. (Web Crypto: `tagLength:128, additionalData`. Java: `GCMParameterSpec(128, iv)` + `updateAAD`.)
Un mensaje que no descifra se descarta en silencio.

## 4. Mensajes (JSON)
Todos llevan `"t"` (tipo) y `"ts"` (ms epoch del emisor).

### PC → móvil
`state` (cada cambio y cada 5 s):
```
{t:"state", v:1, ts, name, off?:1,
 playing:bool, pos:seg, dur:seg, vol:0..1, muted:bool, shuffle:bool, repeat:"off"|"all"|"one",
 speed:1.0, fav:bool, cur:Ent|null, qi:int, qn:int, q:"nombre de la cola"}
```
La posición actual se interpola en el móvil: `pos + (ahora - tiempo_de_recepción)` si `playing`.

`queue` (al cambiar o ante `sync`): `{t:"queue", ts, off:int, total:int, cur:int, name, items:[Ent]}`
(`items` es una ventana de ≤300 pistas que empieza en el índice absoluto `off`; `cur` es el índice absoluto actual.)

`art` (al cambiar la pista o ante `sync`): `{t:"art", ts, k:<Ent.k>, d:<JPEG 96×96 en base64url, "" si no hay>}`

`ack`: `{t:"ack", ts, n:<nonce del comando>, ok:bool, err?:string, miss?:int}`

### Ent (pista)
`{k, a, t, ar, al, d}` — título `t`, artista `ar`, álbum `al`, duración `d` (s, entero) y dos claves de identidad:
- `k` (principal): `"f:" + nombreDeArchivo.toLowerCase() + "|" + tamañoEnBytes`
- `a` (alternativa): `"t:" + norm(artista) + "|" + norm(título)`

`norm(s)`: Unicode NFD → quitar marcas combinantes (`\p{M}`) → minúsculas → conservar solo letras y dígitos (`\p{L}\p{N}`).
El artista desconocido (`<unknown>`, "Artista desconocido", vacío) se normaliza como cadena vacía.
Como el usuario tiene **los mismos archivos** en PC y móvil, las pistas se emparejan por `k`; si no coincide, por `a` (con duración ±3 s).

### móvil → PC
`cmd`: `{t:"cmd", ts, n:<nonce 16 hex>, did:<id del móvil>, dn:<nombre del móvil>, c:<comando>, ...}`
El PC ignora comandos con |ts − ahora| > 5 min o con `n` ya visto (anti-repetición).

| `c` | parámetros | efecto |
|---|---|---|
| `hello` / `sync` | – | el PC publica `state`, `queue` y `art` |
| `hb` | – | latido (presencia del móvil) |
| `toggle` `play` `pause` `next` `prev` | – | transporte |
| `seek` | `pos` (s) | |
| `vol` | `v` 0..1 | |
| `shuffle` | `on` bool | |
| `repeat` | `m` "off"/"all"/"one" | |
| `fav` | `on` bool | |
| `jump` | `i` índice absoluto en la cola, `k` clave de verificación | salta a esa pista |
| `playTracks` | `items:[{k,a,d}]`, `start`, `pos` (s), `play` bool, `name` | reemplaza la cola y reproduce (transferir reproducción al PC) |
| `enqueue` | `items`, `where` "next"/"end" | añade a la cola |

## 5. Transferir reproducción
- **Móvil → PC**: el móvil envía `playTracks` con su cola, pista actual y posición; luego pausa su reproductor local.
- **PC → móvil**: el móvil toma `queue`, `cur` y `pos` del último `state`, resuelve las pistas en su biblioteca local y reproduce; luego envía `pause` al PC.
