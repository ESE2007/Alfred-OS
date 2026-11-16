# -*- coding: utf-8 -*-
"""
ALFRED 3.2 - Asistente de voz offline para Windows

Novedades de la 3.2.2 (seguridad y privacidad):
  • DESCARGAS: solo HTTPS, SHA-256 comprobado sobre el .part antes de moverlo (si no coincide se borra y se registra);
    HASHES_SHA256 para fijar los oficiales y, sin ellos, «confianza en el primer uso» (alfred_hashes.json). Los zip se
    extraen sin zip-slip ni zip-bomb. pip prefiere «ruedas» (no ejecuta código al instalar)
  • BINARIOS DE WINDOWS con ruta absoluta (ruta_sistema: System32; explorer.exe está en %SystemRoot%) y shell=False.
    La voz de respaldo por PowerShell ya no pega el texto dentro del script (inyección con comillas «’»)
  • CONFIRMACIÓN: se quitó el ajuste confirmar_energia=false; una orden remota no puede decir «sí» a una acción
    delicada; mover y eliminar archivos validan ruta_peligrosa (con enlaces simbólicos resueltos y la carpeta de Alfred)
  • CONTROL REMOTO: la clave ya no va en la URL (?t=): se usa #t= una vez y una cookie de sesión HttpOnly +
    SameSite=Strict (con defensa CSRF y comprobación de Host); la clave se guarda con DPAPI; sin mensajes de error internos
  • INSTANCIA ÚNICA (puerto 47653) con token efímero en %LOCALAPPDATA%/Alfred (permisos NTFS solo del usuario)
  • REGISTROS: lo dictado, lo escrito y el portapapeles no se escriben en alfred.log ni en el bus remoto (solo tipo y
    número de caracteres); el token de Spotify también va con DPAPI
  • CARPETAS: nada en C:/Users/Public; si el perfil tiene acentos se usa el nombre 8.3 de %LOCALAPPDATA%/Alfred o
    %PROGRAMDATA%/Alfred/<usuario> con permisos restringidos. Etiquetas y hashes viven en esa carpeta privada
  • ARRANQUE: el índice de canciones y etiquetas se prepara en segundo plano tras esperar_escucha()

Novedades de la 3.2.1 (música que entiende, controla y pone canciones en Spotify):
  • «SIGUIENTE / ANTERIOR / PLAY» EN HARMONOID (y Spotify, apps de la tienda, navegadores): Alfred mandaba el mensaje
    clásico de Windows (WM_APPCOMMAND), que Windows aceptaba aunque el reproductor lo ignorara, así que nunca probaba
    otra vía. Ahora los reproductores modernos se controlan por la sesión multimedia de Windows (SMTC, la misma de la
    pantalla de bloqueo) y, si no está disponible, con la tecla multimedia. «Pausa» pausa y «play» reproduce (antes
    ambas alternaban). «Qué suena» lee el título y el artista de esa sesión
  • «REPRODUCE X» YA NO SE CONFUNDE CON OTRA CANCIÓN: además del nombre de archivo y de carpeta, ahora lee las
    ETIQUETAS (artista y álbum) de tus canciones (FLAC, MP3, M4A…) y las guarda en alfred_etiquetas.json. Si dices el
    nombre de una banda se reproducen sus canciones; «canciones de X», «música de X» o «la banda X» piden artista
  • MÚSICA EN PLATAFORMAS: «pon Numb en Spotify», «reproduce Linkin Park en YouTube Music». Spotify: con tu cuenta
    Premium y un Client ID (☰ Menú → General) busca y pone la canción o el artista de verdad en la app de Spotify.
    YouTube y YouTube Music: abren el primer resultado en tu navegador. «Plataforma por defecto» en el menú hace que
    «reproduce X» use siempre esa plataforma; si no encuentra algo en tu biblioteca y Spotify está conectado, lo busca ahí

Novedades de la 3.2.0 (arranque ágil, música sin fallos y control desde el móvil):
  • ARRANQUE CON WINDOWS: la ventana y el icono de la bandeja aparecen al instante (antes Alfred esperaba hasta 150 s
    a ciegas antes de mostrar nada); la espera de barra de tareas y micrófono ocurre en segundo plano y se ve en el
    estado. Las cargas pesadas (voz Kokoro, inglés, comprensión semántica) esperan a que ya escuche, así el micrófono
    queda listo antes. Si Python viene de la Microsoft Store se usa un lanzador válido, un segundo arranque ya no
    «muestra» la ventana, y el log anota cuánto tardó cada fase («⏱️ Arranque…»)
  • CARPETAS DE MÚSICA: «reproduce la carpeta mis canciones» fallaba porque «mis» y «canciones» se descartaban como
    relleno y quedaba un nombre vacío. Ahora, si todo era relleno, ese ES el nombre de la carpeta
  • NOMBRES EN INGLÉS («Mystery Skulls», «Word»…): se prueban TODAS las lecturas del audio (español + inglés y sus
    alternativas) y gana la que mejor coincide con tu biblioteca; la fonética entiende mejor cómo suena el inglés dicho
    en español («guord» = word, «escuelas» ~ skulls). Si no encuentra nada, el registro dice lo más parecido que hay
  • CONTROL REMOTO (base para la versión móvil): API HTTP + JSON con clave, y una página web para el móvil
    (☰ Menú → Remoto). Desactivado por defecto; documentación en alfred_remoto_API.md

Novedades de la 3.1.0 (inicio con Windows que sí arranca, diseño nuevo, manual al día):
  • INICIO CON WINDOWS REPARADO: el registro guardaba la ruta exacta del archivo, así que al cambiar de versión
    (alfred_2_x → 3_x) apuntaba a un archivo que ya no existía. Ahora Alfred lo repara solo al abrirse, quita las
    entradas muertas de versiones viejas, reactiva la entrada si el Administrador de tareas la había desactivado,
    espera a que Windows tenga barra de tareas y micrófono antes de arrancar, y avisa en la bandeja cuando ya escucha
  • DISEÑO NUEVO: oscuro azulado con acentos cian, indicador HUD animado, tarjetas con borde fino y tipografía
    Bahnschrift (si Windows la tiene); todas las ventanas comparten el mismo estilo
  • MANUAL DE COMANDOS con buscador y secciones; «Mis comandos» ahora puede pulsar teclas, escribir texto y
    ejecutar cualquier comando de Alfred (macros: «modo presentación» = cerrar notificaciones + captura + …)

Novedades de la 3.0.0 (control total del PC solo con la voz):
  • ENERGÍA: bloquear, suspender, hibernar, apagar, reiniciar, cerrar sesión (con «sí» de seguridad, 20 s para
    cancelar), apagado programado, apagar solo la pantalla. Aviso por voz de batería baja
  • VENTANAS Y TECLADO: cerrar / minimizar / maximizar / acomodar ventanas, cambiar a cualquier programa, cerrar
    programas por nombre, escritorios virtuales, ~60 atajos hablados (copiar, pegar, guardar, pestañas, zoom…)
  • ESCRIBIR POR VOZ: «escribe …» y MODO DICTADO (sin repetir mi nombre) con acentos, ñ y signos hablados
  • RATÓN: clic, doble clic, clic derecho, desplazar, mover y CUADRÍCULA numerada para hacer clic en cualquier
    punto de la pantalla sin tocar el ratón
  • SISTEMA: capturas de pantalla, batería / CPU / memoria / disco / internet / Wi-Fi / IP, qué consume más,
    ajustes de Windows, administrador de tareas, modo oscuro, portapapeles, papelera, Wi-Fi
  • TIEMPO: temporizadores y alarmas persistentes, calculadora por voz
  • RENDIMIENTO: menos CPU en reposo (la interfaz y el audio ya no hacen trabajo inútil), traducción y búsqueda
    de órdenes en caché

Novedades de la 2.9.0 (oír mejor, entender mejor, reconocer tu voz):
  • PUERTA DE VOZ: el reconocedor (español + inglés) solo trabaja mientras hablas; en reposo no gasta CPU. Además
    cierra cada frase al terminar de hablar, así el ruido de fondo continuo ya no deja a Alfred sin responder
  • MODELO DE ALTA PRECISIÓN (opcional): Vosk grande en español (~1.4 GB), bastante más acertado que el pequeño. Se
    descarga con permiso y se activa en ☰ Menú → Escucha. Si no carga (poca memoria) Alfred vuelve solo al normal
  • RECONOCER TU VOZ (opcional): registras 5 frases y Alfred solo obedece a tu voz (huella de voz con el modelo
    «spk» de Vosk, ~13 MB, sin librerías nuevas). Muestra la distancia en el registro para que ajustes la exigencia
  • ENTENDER MEJOR (opcional): comprensión semántica offline (fastembed + MiniLM multilingüe): «no se escucha nada»
    → sube el volumen, «está muy oscura la pantalla» → sube el brillo… Solo actúa si ninguna frase exacta coincide

Novedades de la 2.8.1 (arreglo de «deja de detectar comandos sin razón»):
  • VOZ ATASCADA: si la voz de Alfred se queda colgada (cambio de dispositivo de audio, Kokoro o SAPI sin responder),
    antes Alfred se «oía a sí mismo» para siempre y descartaba todo tu audio. Ahora, a los 45 s, la da por perdida,
    arranca otra y vuelve a escuchar (queda anotado en alfred.log)
  • FRASES QUE NO TERMINAN: con ruido continuo Vosk no cierra la frase; ahora se fuerza el cierre cada 20 s
  • RETRASO ACUMULADO: si el audio se atrasa más de 4 s se descarta lo viejo en vez de procesarlo tarde
  • ERRORES EN UNA ORDEN: ya no tumban el micrófono (antes: 5 s sordo + reinicio de PortAudio)
  • PortAudio ya no se reinicia mientras Alfred está hablando

Novedades de la 2.8.0:
  • KOKORO: ARREGLO DE LA CACHÉ: las frases de siempre de varias oraciones («Entendido. Minimizando todas las
    ventanas.», «Apagando sistemas. Hasta pronto, señor.»…) se guardaban enteras pero al hablar se buscaban por
    trozos, así que NUNCA acertaban y se generaban de nuevo cada vez (12 de las 76 frases, en español e inglés). Ahora
    se guardan y se buscan por trozos: suenan al instante, también tras reiniciar Alfred (se guardan en disco)
  • KOKORO: LA HORA Y LA FECHA YA ESTÁN LISTAS: en reposo Alfred deja generada la hora (este minuto y el siguiente) y
    la fecha de hoy, en español y en inglés: «qué hora es» y «qué día es» suenan al instante (~1 generación por
    minuto; se apaga en ☰ Menú → Voz). Las respuestas largas empiezan a sonar antes: el primer trozo se corta en su
    última coma si pasa de 60 letras. alfred.log anota cuánto tarda en sonar lo que no estaba preparado
  • RECONOCIMIENTO: «pausas», «recordatorio», «volumenes»… (singular/plural) ya se entienden; en inglés se toleran
    muletillas («um what time is it»), palabras que suenan igual («paws» = pause, «moot» = mute, «a gender» = agenda)
    y pequeños errores («volum up», «skips»); si venías hablando en inglés, un empate entre las dos lecturas se
    resuelve a favor del inglés. Lo que viene tras «play», «search» o «remind me» (títulos, búsquedas, notas) no se toca
  • MENÚ: sin cambios, ya vive dentro de la ventana de Alfred (☰ no abre otra ventana ni la minimiza)

Novedades de la 2.7.0:
  • ESPAÑOL E INGLÉS A LA VEZ: Alfred oye en los dos idiomas, elige la lectura que tiene sentido (usa las 3 mejores
    interpretaciones de cada frase) y entiende las órdenes en inglés: «Alfred, what time is it», «play Numb by Linkin
    Park», «volume to 40», «open Chrome»… Si le hablas en inglés, te contesta en inglés (voz Kokoro). El modelo de
    inglés (~40 MB) se descarga con tu permiso. Se activa o desactiva en ☰ Menú → Voz
  • PALABRA DE ACTIVACIÓN MÁS FIRME: reconoce también las formas que suenan parecido («alferd», «al fret»…)
  • KOKORO SIN RETRASO: el modelo se queda cargado y calentado, las frases de siempre («Diga», «Entendido»…) se guardan ya
    generadas y suenan al instante, el audio sale por un flujo único (sin archivos ni cortes) y las frases largas
    empiezan a sonar antes. Opcional: modelo ligero de 88 MB (☰ Menú → Voz)
  • MENÚ DENTRO DE LA VENTANA: ☰ abre un panel sobre la misma ventana de Alfred (no otra ventana). La ventana ya no se
    minimiza, no cambia de tamaño (si está maximizada, sigue maximizada) y no pierde el foco

Novedades de la 2.6.3:
  • SEGUNDO PLANO: Alfred ya no pierde la escucha cuando su ventana está oculta (Windows lo ponía en «modo eficiencia»
    y le recortaba CPU y temporizadores). Además tolera mejor los tirones del micrófono
  • «Alfred muéstrate» ahora SÍ trae la ventana al frente aunque estés en otra aplicación, y entiende más formas
    de pedirlo: «desminimízate», «maximízate», «restáurate», «muestra la ventana», «sal de la bandeja»…

Novedades de la 2.6.2:
  • MICRÓFONO MÁS SENSIBLE: Alfred amplifica tu voz automáticamente (ganancia automática) antes de reconocerla,
    así ya no hace falta levantar la voz. Se ajusta en ☰ Menú → Voz → «Sensibilidad del micrófono»

Novedades de la 2.6.1:
  • Arreglo: reproductores que no leen listas .m3u8 (Harmonoid…) ya no abren «alfred_lista.m3u8» como si fuera una canción;
    ahora reciben los archivos de música directamente

Novedades de la 2.6:
  • CANCIONES POR NOMBRE: «Alfred pon Numb», «reproduce Numb de Linkin Park», «pon la canción X». Busca en tus carpetas
    de música (también FLAC), por nombre de archivo y de carpeta, entiende nombres en inglés por su sonido y sigue con el
    resto del álbum. Prefiere el FLAC si tienes la misma canción en dos formatos
  • «Abre X» (apps, webs y carpetas como Descargas) y «busca X en Google / YouTube»
  • Arreglos: detener ≠ pausa, «más bajo / más alto», «baja la música», silencio/sonido, «cerrar» ya no apaga a Alfred,
    más formas de pedir la hora y la fecha, y los comandos ya no se confunden con títulos de canciones

Novedades de la 2.5:
  • MÚSICA CON CUALQUIER REPRODUCTOR: detecta el que tengas abierto (VLC, foobar2000, MusicBee, AIMP, Spotify…) y lo
    controla (pausa, siguiente, anterior). Reproduce carpetas por su nombre: «Alfred reproduce la carpeta rock»
  • «Alfred pasa a segundo plano» (y «muéstrate» para volver); el nombre de la ventana sigue a la palabra de activación
    («Jarvis OS»); la versión ahora se ve en ☰ Menú → Mantenimiento

Novedades de la 2.4.3:
  • VOZ KOKORO (offline, gratis, sin límites): Dora (mujer) y Alex (hombre), mucho más naturales que Piper.
    Piper y la voz de Windows quedan como respaldo. Se elige en ☰ Menú → Voz

Novedades de la 2.4:
  • VOZ CON IA OFFLINE (Piper): voz neuronal natural, gratis, sin internet y sin límites de uso. Se descarga con tu
    permiso; si no está, Alfred usa la voz de Windows. Se elige en ☰ Menú → Voz
  • Interfaz nueva: indicador de estado animado, actividad ordenada por columnas con colores y filtros
  • Barras de progreso animadas (sin porcentajes) para descargas e instalaciones

Novedades de la 2.3:
  • ☰ MENÚ con las opciones que sobran en la ventana principal (General, Voz, Aplausos, Mantenimiento)
  • Todo lo que se instala pide PERMISO: componentes de Python, motor de voz y (con Iniciar_Alfred.bat) Python
  • Iniciar_Alfred.bat: si el PC no tiene Python, pregunta y lo instala; luego abre Alfred

Novedades de la 2.2:
  • PALABRA DE ACTIVACIÓN PERSONALIZABLE (campo en la ventana; admite varias separadas por coma)
  • Corrección: páginas web en navegador elegido (Opera GX) y comandos de usuario revisados de punta a punta

Novedades de la 2.1 respecto a la 2.0:
  • Voz robusta: SAPI directo → PowerShell (System.Speech) como respaldo, con avisos en la consola si falla
  • Agenda: ventana propia (ver, añadir, borrar) + comandos de voz para leerla y mostrarla
  • Ya no abre Claude ni ordena ventanas
  • Busca solo dónde están instaladas las apps (registro, PATH, Menú Inicio, carpetas de programas, tienda)
  • "Mis comandos": editor para crear comandos propios (abrir apps/webs/archivos, mover, copiar, eliminar,
    decir, esperar) sin tocar código
  • Doble aplauso rehecho: detecta transitorios de 10 ms (no confunde voz) y se puede calibrar con un botón

Archivos que crea junto al script: alfred_config.json, comandos_usuario.json, recordatorios_alfred.txt, alfred.log
"""
import os
import sys
import re
import json
import glob
import time
import queue
import ctypes
import shutil
import socket
import functools
import logging
import zipfile
import datetime
import threading
import subprocess
import webbrowser
import unicodedata
import importlib.util
import secrets
import hmac
import ipaddress
import ssl
import base64
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode, quote, quote_plus
import math
import hashlib
import tkinter as tk
from collections import deque, OrderedDict
from difflib import SequenceMatcher

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_AGENDA = os.path.join(BASE_DIR, "recordatorios_alfred.txt")
ARCHIVO_CONFIG = os.path.join(BASE_DIR, "alfred_config.json")
ARCHIVO_COMANDOS = os.path.join(BASE_DIR, "comandos_usuario.json")
RUTA_MODELO = os.path.join(BASE_DIR, "model")
URL_MODELO = "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
RUTA_MODELO_EN = os.path.join(BASE_DIR, "model_en")
URL_MODELO_EN = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
RUTA_MODELO_GRANDE = os.path.join(BASE_DIR, "model_grande")      # opcional: Vosk grande en español (~1.4 GB)
URL_MODELO_GRANDE = "https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip"
RUTA_MODELO_SPK = os.path.join(BASE_DIR, "model_spk")            # opcional: huella de voz (~13 MB)
URL_MODELO_SPK = "https://alphacephei.com/vosk/models/vosk-model-spk-0.4.zip"
RUTA_SEMANTICA = os.path.join(BASE_DIR, "modelo_semantico")      # opcional: comprensión semántica (~220 MB)
MODELO_SEMANTICO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
URL_PIPER = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
URL_VOCES = "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
URL_KOKORO = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
KOKORO_MODELO, KOKORO_MODELO_MB = "kokoro-v1.0.onnx", 310      # (kokoro-v1.0.int8.onnx pesa 88 MB: más ligera, algo menos fiel)
KOKORO_VOCES, KOKORO_VOCES_MB = "voices-v1.0.bin", 28
KOKORO_LIGERO, KOKORO_LIGERO_MB = "kokoro-v1.0.int8.onnx", 88   # modelo ligero opcional (☰ Menú → Voz)
VOCES_IA = {   # id -> datos (mb = tamaño aproximado de la descarga; motor: kokoro | piper)
    "kokoro-ef_dora": {"nombre": "Dora · Mujer (Kokoro, la más natural)", "motor": "kokoro", "voz": "ef_dora", "voz_en": "af_heart", "mb": 340},
    "kokoro-em_alex": {"nombre": "Alex · Hombre (Kokoro, la más natural)", "motor": "kokoro", "voz": "em_alex", "voz_en": "am_michael", "mb": 340},
    "es_MX-ald-medium": {"nombre": "Ald · México (Piper, ligera)", "ruta": "es/es_MX/ald/medium", "mb": 63},
    "es_MX-claude-high": {"nombre": "Claude · México (Piper, alta calidad)", "ruta": "es/es_MX/claude/high", "mb": 110},
    "es_ES-davefx-medium": {"nombre": "Davefx · España (Piper)", "ruta": "es/es_ES/davefx/medium", "mb": 63},
}
VOZ_IA_PREDETERMINADA = "kokoro-ef_dora"
KOKORO_PREDETERMINADA = "kokoro-ef_dora"
PIPER_PREDETERMINADA = "es_MX-ald-medium"
try:
    import winsound
except ImportError:          # no es Windows
    winsound = None


def _dir_voz_ia():
    r"""Carpeta de la voz IA. Piper no lee bien rutas con acentos: en ese caso usa la carpeta privada del usuario
    (datos_dir(), solo ASCII y con permisos NTFS solo para ti). Nunca C:\Users\Public: cualquiera podría cambiar
    ahí el piper.exe que Alfred ejecuta."""
    base = os.path.join(BASE_DIR, "voz_ia")
    try:
        base.encode("ascii")
        return base
    except UnicodeEncodeError:
        viejo = os.path.join(os.environ.get("PUBLIC") or os.environ.get("PROGRAMDATA") or "C:\\", "AlfredVozIA")
        if os.path.isdir(viejo):
            logging.warning("Carpeta pública antigua de la voz IA sin usar (cualquiera pudo modificarla): %s. "
                            "Puedes borrarla; Alfred descargará la voz otra vez en su carpeta privada.", viejo)
        return os.path.join(datos_dir(), "voz_ia")


PUERTO_INSTANCIA = 47653
NOMBRE_REGISTRO = "Alfred_OS"
SIN_VENTANA = 0x08000000  # CREATE_NO_WINDOW
VERSION = "3.2.2"


# ══════════════════════════════════════════════════════════════════════════════
#  SEGURIDAD: carpeta privada, secretos (DPAPI), rutas absolutas de Windows y descargas verificadas
# ══════════════════════════════════════════════════════════════════════════════
_LOCK_DATOS = threading.Lock()
_DATOS_DIR = [None]


def _es_ascii(texto):
    try:
        str(texto).encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def _raiz_windows():
    return os.environ.get("SystemRoot") or os.environ.get("windir") or r"C:\Windows"


def ruta_sistema(nombre):
    r"""Ruta ABSOLUTA de un programa de Windows. Nunca se lanza por su nombre corto: así un «shutdown.exe» plantado en
    la carpeta de trabajo o en el PATH no se ejecuta en lugar del de Windows. Busca en %SystemRoot%\System32 (y
    WindowsPowerShell\v1.0 para powershell); explorer.exe vive en %SystemRoot%, no en System32."""
    n = os.path.basename(str(nombre)).lower()
    if not n.endswith(".exe"):
        n += ".exe"
    raiz = _raiz_windows()
    cands = []
    if n == "powershell.exe":
        cands.append(os.path.join(raiz, "System32", "WindowsPowerShell", "v1.0", n))
    cands += [os.path.join(raiz, "System32", n), os.path.join(raiz, n)]
    for c in cands:
        if os.path.isfile(c):
            return c
    raise FileNotFoundError(f"No encuentro {n} en {raiz}")


def comando_sistema(cmd):
    r"""['mmc.exe', 'devmgmt.msc'] -> ['C:\\Windows\\System32\\mmc.exe', 'devmgmt.msc']: el primer elemento con ruta absoluta."""
    cmd = list(cmd)
    if cmd and not os.path.isabs(cmd[0]):
        cmd[0] = ruta_sistema(cmd[0])
    return cmd


def ejecutar_sistema(nombre, *args, **kw):
    """subprocess.run de un programa de Windows con ruta absoluta, argumentos en lista y shell=False."""
    kw.pop("shell", None)
    return subprocess.run([ruta_sistema(nombre)] + [str(a) for a in args], shell=False, **kw)


def _ruta_corta(ruta):
    """Nombre 8.3 de una carpeta existente (solo ASCII), o None."""
    if os.name != "nt":
        return None
    try:
        buf = ctypes.create_unicode_buffer(1024)
        n = ctypes.windll.kernel32.GetShortPathNameW(ruta, buf, 1024)
        return buf.value if 0 < n < 1024 else None
    except Exception:
        return None


def _restringir_acl(ruta):
    r"""Deja la carpeta solo para el usuario actual (icacls con ruta absoluta; quita los permisos heredados).
    Primero concede y solo si funcionó quita la herencia, para no dejarte sin acceso a tu propia carpeta."""
    if os.name != "nt":
        return False
    marca = os.path.join(ruta, ".acl_ok")
    if os.path.exists(marca):
        return True
    try:
        usuario = os.environ.get("USERNAME") or ""
        dominio = os.environ.get("USERDOMAIN") or ""
        if not usuario:
            return False
        quien = f"{dominio}\\{usuario}" if dominio else usuario
        r1 = ejecutar_sistema("icacls", ruta, "/grant:r", f"{quien}:(OI)(CI)F", capture_output=True,
                              creationflags=SIN_VENTANA, timeout=30)
        if r1.returncode != 0:
            logging.warning("icacls no pudo conceder permisos en la carpeta privada")
            return False
        r2 = ejecutar_sistema("icacls", ruta, "/inheritance:r", capture_output=True,
                              creationflags=SIN_VENTANA, timeout=30)
        if r2.returncode != 0:
            logging.warning("icacls no pudo quitar los permisos heredados de la carpeta privada")
            return False
        with open(marca, "w", encoding="ascii") as f:
            f.write("1")
        return True
    except Exception:
        logging.exception("No pude restringir los permisos de la carpeta privada")
        return False


def datos_dir():
    r"""Carpeta privada de Alfred: %LOCALAPPDATA%\Alfred (dentro de tu perfil, que ya es solo tuyo). Si el perfil tiene
    acentos o ñ (Vosk/Piper no abren esas rutas) usa el nombre corto 8.3 de esa misma carpeta (solo ASCII) o, si Windows
    no lo tiene, %PROGRAMDATA%\Alfred\<usuario> con los permisos NTFS limitados a ti (de forma síncrona antes de usarla).
    Nunca C:\Users\Public. Los permisos de la carpeta normal se ajustan en segundo plano (no retrasa el arranque)."""
    with _LOCK_DATOS:
        if _DATOS_DIR[0]:
            return _DATOS_DIR[0]
        local = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
        base = os.path.join(local, "Alfred")
        os.makedirs(base, exist_ok=True)
        ruta, sincrono = base, False
        if not _es_ascii(base):
            corta = _ruta_corta(base)
            if corta and _es_ascii(corta):
                ruta = corta
            else:
                pd = os.environ.get("PROGRAMDATA") or "C:\\ProgramData"
                usuario = re.sub(r"[^A-Za-z0-9_-]", "_", os.environ.get("USERNAME") or "usuario")
                usuario += "_" + hashlib.sha256(os.path.expanduser("~").encode("utf-8")).hexdigest()[:6]
                ruta = os.path.join(pd, "Alfred", usuario)
                os.makedirs(ruta, exist_ok=True)
                sincrono = True
        _DATOS_DIR[0] = ruta
    if sincrono:
        _restringir_acl(ruta)
    else:
        threading.Thread(target=_restringir_acl, args=(ruta,), daemon=True, name="acl").start()
    return ruta


# ── secretos con DPAPI (la clave la guarda Windows, ligada a tu cuenta) ──────
def _blob_clase():
    from ctypes import wintypes

    class BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]
    return BLOB


def proteger_secreto(texto):
    """'dpapi:<base64>' (CryptProtectData, solo lo abre tu cuenta de Windows). Fuera de Windows, el texto tal cual."""
    if not texto or os.name != "nt":
        return texto
    try:
        from ctypes import wintypes
        BLOB = _blob_clase()
        datos = str(texto).encode("utf-8")
        buf = ctypes.create_string_buffer(datos, len(datos))
        ent = BLOB(len(datos), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
        sal = BLOB()
        crypt32, k32 = ctypes.WinDLL("crypt32", use_last_error=True), ctypes.WinDLL("kernel32")
        crypt32.CryptProtectData.argtypes = [ctypes.POINTER(BLOB), wintypes.LPCWSTR, ctypes.POINTER(BLOB), ctypes.c_void_p,
                                             ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(BLOB)]
        crypt32.CryptProtectData.restype = wintypes.BOOL
        k32.LocalFree.argtypes = [ctypes.c_void_p]
        if not crypt32.CryptProtectData(ctypes.byref(ent), "Alfred", None, None, None, 0x1, ctypes.byref(sal)):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            cifrado = ctypes.string_at(sal.pbData, sal.cbData)
        finally:
            k32.LocalFree(ctypes.cast(sal.pbData, ctypes.c_void_p))
        return "dpapi:" + base64.b64encode(cifrado).decode("ascii")
    except Exception:
        logging.exception("DPAPI: no pude proteger un secreto")
        return texto


def revelar_secreto(valor):
    """Inverso de proteger_secreto. Un valor sin prefijo «dpapi:» (guardado por versiones anteriores) se devuelve igual."""
    if not valor or not str(valor).startswith("dpapi:"):
        return valor or ""
    if os.name != "nt":
        return ""
    try:
        from ctypes import wintypes
        BLOB = _blob_clase()
        datos = base64.b64decode(str(valor)[6:])
        buf = ctypes.create_string_buffer(datos, len(datos))
        ent = BLOB(len(datos), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
        sal = BLOB()
        crypt32, k32 = ctypes.WinDLL("crypt32", use_last_error=True), ctypes.WinDLL("kernel32")
        crypt32.CryptUnprotectData.argtypes = [ctypes.POINTER(BLOB), ctypes.c_void_p, ctypes.POINTER(BLOB), ctypes.c_void_p,
                                               ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(BLOB)]
        crypt32.CryptUnprotectData.restype = wintypes.BOOL
        k32.LocalFree.argtypes = [ctypes.c_void_p]
        if not crypt32.CryptUnprotectData(ctypes.byref(ent), None, None, None, None, 0x1, ctypes.byref(sal)):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            return ctypes.string_at(sal.pbData, sal.cbData).decode("utf-8")
        finally:
            k32.LocalFree(ctypes.cast(sal.pbData, ctypes.c_void_p))
    except Exception:
        logging.error("DPAPI: no pude abrir un secreto (¿otra cuenta de Windows?); hay que volver a crearlo")
        return ""


# ── descargas con SHA-256 ────────────────────────────────────────────────────
HASHES_SHA256 = {
    # SHA-256 oficiales «fijados»: clave = nombre del archivo de destino (o la URL completa), valor = hexadecimal.
    # Ej.: "voices-v1.0.bin": "<sha256 publicado por el autor>". Un archivo con hash fijado que no coincida se descarta.
    # Sin hash fijado se usa «confianza en el primer uso»: se guarda el de la primera descarga (alfred_hashes.json en la
    # carpeta privada) y las siguientes se comparan con él. Obtén el hash con:  certutil -hashfile ARCHIVO SHA256
}


def sha256_de(ruta, bloque=1 << 20):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(bloque), b""):
            h.update(trozo)
    return h.hexdigest()


def comprobar_hash_descarga(url, nombre, calculado, esperado=None):
    """Compara el SHA-256 de lo descargado: 'fijado' (coincide con el hash fijado), 'recordado' (coincide con el de la
    primera descarga) o 'nuevo' (primera vez, sin hash fijado: se guarda). Lanza ValueError si NO coincide."""
    esperado = (esperado or HASHES_SHA256.get(nombre) or HASHES_SHA256.get(url) or "").strip().lower()
    if esperado:
        if not hmac.compare_digest(calculado.lower(), esperado):
            raise ValueError(f"SHA-256 de {nombre} no coincide con el hash fijado (obtenido {calculado[:16]}…)")
        logging.info("SHA-256 verificado (fijado): %s", nombre)
        return "fijado"
    ruta = os.path.join(datos_dir(), "alfred_hashes.json")
    try:
        with open(ruta, encoding="utf-8") as f:
            tofu = json.load(f)
    except Exception:
        tofu = {}
    previo = tofu.get(url)
    if previo:
        if not hmac.compare_digest(calculado.lower(), str(previo).lower()):
            raise ValueError(f"{nombre} cambió desde la última vez que lo descargaste (SHA-256 distinto). Si te fías de "
                             "la nueva versión, borra su línea en alfred_hashes.json")
        logging.info("SHA-256 verificado (igual que la primera descarga): %s", nombre)
        return "recordado"
    tofu[url] = calculado.lower()
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(tofu, f, indent=2)
    except OSError:
        logging.exception("No pude guardar el SHA-256 de la descarga")
    logging.warning("%s sin SHA-256 fijado: guardo el de esta descarga (%s). Compáralo con el que publica su autor "
                    "y fíjalo en HASHES_SHA256.", nombre, calculado)
    return "nuevo"


def comprobar_zip(z, destino, max_bytes=8 << 30):
    """Antes de extraer: ningún miembro puede salir de la carpeta de destino (zip-slip) y el total descomprimido no
    puede pasar de max_bytes (zip-bomb). Lanza ValueError."""
    base = os.path.realpath(destino)
    total = 0
    for m in z.infolist():
        objetivo = os.path.realpath(os.path.join(base, m.filename))
        if os.path.commonpath([base, objetivo]) != base:
            raise ValueError(f"El zip intenta escribir fuera de su carpeta: {m.filename!r}")
        total += m.file_size
    if total > max_bytes:
        raise ValueError("El zip descomprimido es demasiado grande")


VOZ_IA_DIR = _dir_voz_ia()          # (aquí, porque puede necesitar datos_dir())
EN_ARRANQUE = "--inicio-windows" in sys.argv      # Windows abrió Alfred al iniciar sesión
T_INICIO = time.time()
EVT_ESCUCHANDO = threading.Event()                # se activa cuando el micrófono ya está escuchando
PUERTO_REMOTO = 47654                             # control remoto (API HTTP local)


def preguntar(titulo, texto):
    """Cuadro Sí/No nativo de Windows (sirve en .pyw y desde cualquier hilo). True = el usuario aceptó."""
    try:
        return ctypes.windll.user32.MessageBoxW(0, texto, titulo, 0x24 | 0x40000) == 6   # SÍ/NO + ? + al frente
    except Exception:
        return False


def avisar(titulo, texto, error=False):
    try:
        ctypes.windll.user32.MessageBoxW(0, texto, titulo, (0x10 if error else 0x40) | 0x40000)
    except Exception:
        pass


if sys.version_info < (3, 9):
    avisar("Alfred", "Alfred necesita Python 3.9 o superior y este equipo tiene la versión "
           + sys.version.split()[0] + ".\n\nAbre «Iniciar_Alfred.bat»: te ofrece instalar uno nuevo.", True)
    sys.exit(1)

logging.basicConfig(filename=os.path.join(BASE_DIR, "alfred.log"), level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8")
sys.excepthook = lambda t, v, tb: logging.critical("Excepción no controlada", exc_info=(t, v, tb))
threading.excepthook = lambda a: logging.critical("Excepción en hilo", exc_info=(a.exc_type, a.exc_value, a.exc_traceback))

# ══════════════════════════════════════════════════════════════════════════════
#  COMPONENTES DE PYTHON: si faltan, se PIDE PERMISO y se instalan (con ventana de progreso)
# ══════════════════════════════════════════════════════════════════════════════
DEPENDENCIAS = {  # módulo: paquete pip
    "vosk": "vosk", "sounddevice": "sounddevice", "numpy": "numpy", "pyautogui": "pyautogui",
    "customtkinter": "customtkinter", "requests": "requests", "pystray": "pystray", "PIL": "Pillow",
    # opcionales (si no se instalan, esa función usa una alternativa o avisa)
    "screen_brightness_control": "screen-brightness-control", "pycaw": "pycaw",
    "comtypes": "comtypes", "send2trash": "send2trash",
    "mutagen": "mutagen",                                          # 3.2.1: artista/álbum de tus canciones
    "winrt.windows.media.control": "winrt-Windows.Media.Control",  # 3.2.1: controlar Harmonoid, Spotify…
    "winrt.windows.foundation.collections": "winrt-Windows.Foundation.Collections",
    "winrt.windows.storage.streams": "winrt-Windows.Storage.Streams",
}
OPCIONALES = {"screen_brightness_control", "pycaw", "comtypes", "send2trash", "mutagen",
              "winrt.windows.media.control", "winrt.windows.foundation.collections", "winrt.windows.storage.streams"}
SIN_OPCIONALES = os.path.join(BASE_DIR, "alfred_sin_opcionales.flag")


def faltantes():
    """[(módulo, paquete)] que no están instalados."""
    def falta(m):
        try:
            return importlib.util.find_spec(m) is None
        except (ImportError, ValueError, AttributeError):         # «a.b.c» con «a» sin instalar lanza en vez de devolver None
            return True
    return [(m, p) for m, p in DEPENDENCIAS.items() if falta(m)]


def instalar_paquetes(paquetes, notificar=lambda texto: None, avance=lambda frac, techo: None):
    """Instala con pip (silencioso). Devuelve {paquete: True/False}."""
    silencio = dict(stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    creationflags=SIN_VENTANA)
    con_error = dict(stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     creationflags=SIN_VENTANA, text=True, errors="replace")
    if importlib.util.find_spec("pip") is None:
        notificar("Preparando pip…")
        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], **silencio)
    resultados = {}
    for i, (_, paquete) in enumerate(paquetes, 1):
        notificar(f"Instalando {paquete} ({i}/{len(paquetes)})…")
        avance((i - 1) / len(paquetes), (i - 0.15) / len(paquetes))
        logging.info("Instalando %s", paquete)
        orden = [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--no-input", paquete]
        # 1.º solo «ruedas» (binarios ya construidos: pip no ejecuta código del paquete al instalar); 2.º sin caché; 3.º
        # permitiendo código fuente solo si el paquete no tiene rueda (queda anotado en el log)
        r = subprocess.run(orden + ["--only-binary=:all:"], **con_error)
        if r.returncode != 0:
            r = subprocess.run(orden + ["--only-binary=:all:", "--no-cache-dir"], **con_error)
        if r.returncode != 0:
            logging.warning("%s no tiene rueda compatible: lo instalo desde su código fuente", paquete)
            r = subprocess.run(orden + ["--no-cache-dir"], **con_error)
        resultados[paquete] = r.returncode == 0
        avance(i / len(paquetes), None)
        if r.returncode != 0:
            logging.error("No se pudo instalar %s. Salida de pip:\n%s", paquete, (r.stdout or "")[-1500:])
    importlib.invalidate_caches()
    return resultados



# ══════════════════════════════════════════════════════════════════════════════
#  ASPECTO: paleta y barra de progreso animada (sirve en la ventana principal y en el instalador)
# ══════════════════════════════════════════════════════════════════════════════
PAL = {"bg": "#070b12", "bg2": "#05080d", "card": "#0d141f", "card2": "#142033", "hover": "#1c2f4a",
       "track": "#17243a", "line": "#1d3350", "text": "#e8f1fb", "muted": "#7f93ad", "acc": "#0e8fb0",
       "acc_luz": "#8be9fd", "neon": "#22d3ee", "ok": "#34d399", "warn": "#fbbf24", "err": "#fb7185",
       "voz": "#a594ff"}
F_TIT, F_CUERPO = "Segoe UI Semibold", "Segoe UI"       # elegir_fuentes() pone Bahnschrift si Windows la tiene


def mezclar(c1, c2, t):
    """Mezcla dos colores #rrggbb (t=0 -> c1, t=1 -> c2)."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(a, b))


class BarraAnimada(tk.Canvas):
    """Barra de progreso suave: sube con inercia hacia la meta, avanza despacio mientras llegan datos
    (techo) y lleva un brillo que la recorre. Sin números: se ve cuánto falta por cómo se llena."""

    def __init__(self, master, ancho=400, alto=12, bg=None, **kw):
        super().__init__(master, width=ancho, height=alto + 4, bg=bg or PAL["card"], highlightthickness=0, bd=0, **kw)
        self.alto, self._ancho = alto, ancho
        self.valor = self.meta = self.fase = 0.0
        self.techo, self.indet, self.activa = None, False, False
        self.bind("<Configure>", lambda e: setattr(self, "_ancho", e.width))

    def fijar(self, frac, techo=None):
        self.indet = False
        self.meta = max(0.0, min(1.0, frac))
        self.techo = None if techo is None else max(self.meta, min(1.0, techo))

    def indeterminado(self, si=True):
        self.indet = si

    def reiniciar(self):
        self.valor = self.meta = 0.0
        self.techo = None

    def iniciar(self):
        if not self.activa:
            self.activa = True
            self._tick()

    def detener(self):
        self.activa = False

    def _tick(self):
        if not self.activa:
            return
        try:
            if not self.indet:
                dif = self.meta - self.valor
                if dif > 0.0005:
                    self.valor += dif * 0.10 + 0.0004                 # frenado suave al acercarse a la meta
                elif self.techo is not None and self.valor < self.techo:
                    self.valor += (self.techo - self.valor) * 0.006   # sigue avanzando despacio mientras espera
            self.fase = (self.fase + 0.018) % 1.0
            self._dibujar()
            self.after(33, self._tick)
        except tk.TclError:
            self.activa = False

    def _dibujar(self):
        h = self.alto
        w = max(self._ancho, 40)
        y, r = (h + 4) // 2, h / 2
        self.delete("all")
        x0, x1 = r + 2, w - r - 2
        largo = x1 - x0
        self.create_line(x0, y, x1, y, width=h, capstyle="round", fill=PAL["track"])
        if self.indet:
            seg = largo * 0.30
            pos = (math.sin(self.fase * 2 * math.pi - math.pi / 2) + 1) / 2
            a = x0 + (largo - seg) * pos
            self.create_line(a, y, a + seg, y, width=h, capstyle="round", fill=PAL["acc"])
            return
        if self.valor <= 0.003:
            return
        fin = x0 + largo * self.valor
        self.create_line(x0, y, max(fin, x0 + 1), y, width=h, capstyle="round", fill=PAL["acc"])
        brillo = max(largo * 0.16, 24)
        a = x0 + (fin - x0 + brillo) * self.fase - brillo
        a, b = max(a, x0), min(a + brillo, fin)
        if b - a > 3:
            self.create_line(a, y, b, y, width=max(h - 5, 2), capstyle="round", fill=PAL["acc_luz"])


def instalar_con_ventana(paquetes):
    """Igual que instalar_paquetes pero mostrando una ventanita con una barra animada."""
    resultados, cola = {}, queue.Queue()

    def trabajo():
        try:
            resultados.update(instalar_paquetes(paquetes, lambda t: cola.put(("txt", t)),
                                                lambda f, tp: cola.put(("bar", f, tp))))
        finally:
            cola.put(None)

    try:
        root = tk.Tk()
    except Exception:
        return instalar_paquetes(paquetes)
    root.title("Alfred - instalando componentes")
    root.geometry("480x170")
    root.resizable(False, False)
    root.configure(bg=PAL["bg"])
    root.attributes("-topmost", True)
    root.protocol("WM_DELETE_WINDOW", lambda: None)      # no se cierra a mitad de la instalación
    tk.Label(root, text="Alfred", font=("Segoe UI Semibold", 16), bg=PAL["bg"], fg=PAL["text"]).pack(pady=(18, 0))
    etiqueta = tk.Label(root, text="Preparando…", font=("Segoe UI", 10), bg=PAL["bg"], fg=PAL["muted"], wraplength=420)
    etiqueta.pack(pady=(4, 14))
    barra = BarraAnimada(root, ancho=420, alto=12, bg=PAL["bg"])
    barra.pack(fill="x", padx=30)
    barra.indeterminado(True)
    barra.iniciar()

    def revisar():
        try:
            while True:
                msg = cola.get_nowait()
                if msg is None:
                    barra.fijar(1.0)
                    root.after(700, root.destroy)           # deja que la barra llegue al final
                    return
                if msg[0] == "txt":
                    etiqueta.config(text=msg[1])
                else:
                    barra.fijar(msg[1], msg[2])
        except queue.Empty:
            pass
        root.after(100, revisar)

    threading.Thread(target=trabajo, daemon=True).start()
    root.after(100, revisar)
    root.mainloop()
    return resultados


def instalar_dependencias(visual=True):
    faltan = faltantes()
    if not faltan:
        return
    obligatorios = [(m, p) for m, p in faltan if m not in OPCIONALES]
    if not obligatorios and os.path.exists(SIN_OPCIONALES):
        return                                            # ya dijiste que no a los opcionales
    lista = "\n".join(f"  • {p}" + ("   (opcional)" if m in OPCIONALES else "") for m, p in faltan)
    if not preguntar("Alfred - Permiso para instalar",
                     "Alfred necesita instalar estos componentes de Python, que no encontré en tu PC:\n\n" + lista +
                     "\n\nSe descargan de internet (pypi.org) y se instalan solo para tu usuario, "
                     "sin permisos de administrador.\n\n¿Instalarlos ahora?"):
        if obligatorios:
            avisar("Alfred", "Sin esos componentes Alfred no puede funcionar, así que se cerrará.\n\n"
                             "Ábrelo de nuevo cuando quieras y acepta la instalación.")
            sys.exit(0)
        with open(SIN_OPCIONALES, "w", encoding="utf-8") as f:
            f.write("El usuario rechazó los componentes opcionales. Bórrame o usa Menú > Mantenimiento para reintentar.")
        return
    if os.path.exists(SIN_OPCIONALES):
        os.remove(SIN_OPCIONALES)
    (instalar_con_ventana if visual else instalar_paquetes)(faltan)
    quedan = [p for m, p in faltantes() if m not in OPCIONALES]
    if quedan:
        avisar("Alfred", "No pude instalar: " + ", ".join(quedan) +
               ".\n\nRevisa tu conexión a internet y vuelve a abrir Alfred.\nDetalles en alfred.log.", True)
        sys.exit(1)


instalar_dependencias()

import winreg  # noqa: E402
import numpy as np  # noqa: E402
import sounddevice as sd  # noqa: E402
import pyautogui  # noqa: E402
import requests  # noqa: E402
import pystray  # noqa: E402
import customtkinter as ctk  # noqa: E402
from tkinter import filedialog, messagebox  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402
from vosk import Model, KaldiRecognizer, SetLogLevel  # noqa: E402
try:
    from vosk import SpkModel  # noqa: E402   (huella de voz; solo en versiones recientes de Vosk)
except Exception:
    SpkModel = None

try:
    import screen_brightness_control as sbc
except Exception:
    sbc = None

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0


# ══════════════════════════════════════════════════════════════════════════════
#  LÓGICA PURA (sin Windows: se puede probar aparte)
# ══════════════════════════════════════════════════════════════════════════════
def normalizar(texto):
    """Minúsculas, sin acentos ni signos: 'Buenos días' == 'buenos dias' venga como venga de Vosk."""
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


TRIGGER_RECORDAR = re.compile(r"\b(recu[eé]rdame|recuerda|anota(me)?|apunta(me)?)\b", re.I)


def hay(norm, *palabras):
    tokens = set(norm.split())
    return any(p in tokens for p in palabras)


# ── palabra de activación personalizable ─────────────────────────────────────
def parsear_activacion(texto):
    """'Jarvis, yarvis' -> ['jarvis', 'yarvis'] (normalizadas, sin repetidos, máx. 6)."""
    frases = []
    for parte in (texto or "").split(","):
        p = normalizar(parte)
        if p and p not in frases:
            frases.append(p)
    return frases[:6]


def nombre_desde_cfg(cfg):
    """Primera palabra de activación con mayúscula inicial: 'jarvis, yarvis' -> 'Jarvis'."""
    frases = parsear_activacion(cfg.get("palabra_activacion"))
    return frases[0].title() if frases else "Alfred"


def validar_activacion(frases):
    """None si es válida; si no, el mensaje de error para el usuario."""
    if not frases:
        return "Escribe al menos una palabra de activación."
    for f in frases:
        if len(f) < 3:
            return f"«{f}» es demasiado corta (mínimo 3 letras)."
        if len(f.split()) > 3:
            return f"«{f}» tiene demasiadas palabras (máximo 3)."
        if buscar_comando(f):
            return f"«{f}» coincide con un comando de Alfred; elige otra."
    return None


def _parecidas(a, b):
    """Iguales, o casi (el reconocedor a veces oye 'yarvis' por 'jarvis'). Palabras cortas: exactas."""
    if a == b:
        return True
    if len(a) < 4 or len(b) < 4:
        return False
    if SequenceMatcher(None, a, b).ratio() >= 0.8:
        return True
    fa, fb = fonetica(a), fonetica(b)                # se escriben distinto pero suenan igual («alferd» / «alfred»)
    return len(fa) >= 4 and len(fb) >= 4 and (fa == fb or SequenceMatcher(None, fa, fb).ratio() >= 0.86)


def buscar_wake(tokens, frases):
    """Primera aparición de alguna frase de activación -> (inicio, nº de palabras) o None."""
    mejor = None
    for frase in frases:
        pl = frase.split()
        k = len(pl)
        for i in range(len(tokens) - k + 1):
            if all(_parecidas(tokens[i + j], pl[j]) for j in range(k)):
                if mejor is None or i < mejor[0]:
                    mejor = (i, k)
                break
        if k == 1:                                   # 'al fred' oído en vez de 'alfred'
            for i in range(len(tokens) - 1):
                if _parecidas(tokens[i] + tokens[i + 1], pl[0]) and (mejor is None or i < mejor[0]):
                    mejor = (i, 2)
                    break
    return mejor


def quitar_wake(norm, frases):
    """(se_dijo_la_palabra, resto_de_la_orden) sobre texto normalizado."""
    tokens = norm.split()
    m = buscar_wake(tokens, frases)
    if not m:
        return False, norm
    i, k = m
    return True, " ".join(tokens[:i] + tokens[i + k:])


def quitar_wake_raw(raw, frases):
    """Quita la palabra de activación del texto original (conserva acentos y mayúsculas del resto)."""
    toks = raw.split()
    tn = [normalizar(t) for t in toks]
    idx = [i for i, t in enumerate(tn) if t]
    m = buscar_wake([tn[i] for i in idx], frases)
    if not m:
        return raw
    quitar = set(idx[m[0]:m[0] + m[1]])
    return " ".join(t for i, t in enumerate(toks) if i not in quitar)


_UNID = {"cero": 0, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8,
         "nueve": 9, "diez": 10, "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
         "dieciseis": 16, "diecisiete": 17, "dieciocho": 18, "diecinueve": 19, "veinte": 20, "veintiuno": 21,
         "veintidos": 22, "veintitres": 23, "veinticuatro": 24, "veinticinco": 25, "veintiseis": 26,
         "veintisiete": 27, "veintiocho": 28, "veintinueve": 29}
_DEC = {"treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90}


def extraer_numero(norm):
    """Primer número (0-100) dicho en la frase: 'al cincuenta', 'treinta y cinco', '80'."""
    tokens = norm.split()
    for i, t in enumerate(tokens):
        if t.isdigit():
            return max(0, min(100, int(t)))
        if t in ("cien", "ciento"):
            return 100
        if t in _DEC:
            val = _DEC[t]
            if i + 2 < len(tokens) and tokens[i + 1] == "y" and 0 < _UNID.get(tokens[i + 2], 99) < 10:
                val += _UNID[tokens[i + 2]]
            return val
        if t in _UNID:
            return _UNID[t]
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  MÚSICA: detectar el reproductor abierto, controlarlo y reproducir carpetas por su nombre
# ══════════════════════════════════════════════════════════════════════════════
REPRODUCTORES = {   # proceso (minúsculas) -> nombre
    "spotify.exe": "Spotify", "vlc.exe": "VLC", "foobar2000.exe": "foobar2000", "musicbee.exe": "MusicBee",
    "aimp.exe": "AIMP", "winamp.exe": "Winamp", "itunes.exe": "iTunes", "wmplayer.exe": "Reproductor de Windows Media",
    "microsoft.media.player.exe": "Reproductor multimedia", "music.ui.exe": "Groove Música",
    "mediamonkey.exe": "MediaMonkey", "harmonoid.exe": "Harmonoid", "harmonoid music.exe": "Harmonoid", "potplayermini64.exe": "PotPlayer", "potplayermini.exe": "PotPlayer",
    "potplayer64.exe": "PotPlayer", "mpc-hc64.exe": "MPC-HC", "mpc-hc.exe": "MPC-HC", "mpc-be64.exe": "MPC-BE",
    "mpc-be.exe": "MPC-BE", "tidal.exe": "TIDAL", "deezer.exe": "Deezer", "amazon music.exe": "Amazon Music",
    "youtube music.exe": "YouTube Music", "dopamine.exe": "Dopamine", "strawberry.exe": "Strawberry",
    "clementine.exe": "Clementine", "audacious.exe": "Audacious", "mixxx.exe": "Mixxx", "musicbee64.exe": "MusicBee",
}
ENTIENDEN_LISTAS = {"vlc.exe", "foobar2000.exe", "musicbee.exe", "musicbee64.exe", "aimp.exe", "winamp.exe", "mpc-hc.exe",
                    "mpc-hc64.exe", "mpc-be.exe", "mpc-be64.exe", "potplayer64.exe", "potplayermini.exe",
                    "potplayermini64.exe", "audacious.exe", "clementine.exe", "strawberry.exe", "mediamonkey.exe"}
STREAMING = {"spotify.exe", "tidal.exe", "deezer.exe", "amazon music.exe", "youtube music.exe"}   # no abren carpetas locales
# Reproductores que SÍ hacen caso a WM_APPCOMMAND. Harmonoid (Flutter), Spotify, las apps de la tienda y los navegadores
# no: Windows entrega el mensaje sin error y el reproductor lo ignora, por eso se controlan por SMTC / tecla multimedia.
APPCOMMAND_OK = ENTIENDEN_LISTAS | {"itunes.exe", "wmplayer.exe", "winamp.exe"}
EXT_AUDIO = (".mp3", ".flac", ".wav", ".m4a", ".ogg", ".opus", ".wma", ".aac", ".ape", ".wv", ".mka", ".aiff", ".aif")
WM_APPCOMMAND = 0x0319
APPCOMMAND = {"siguiente": 11, "anterior": 12, "detener": 13, "pausa": 14, "play": 46}
VK_MEDIA = {"siguiente": 0xB0, "anterior": 0xB1, "detener": 0xB2, "pausa": 0xB3, "play": 0xB3}
RELLENO_INICIO = {"de", "del", "la", "el", "las", "los", "llamada", "llamado", "que", "se", "llama", "carpeta", "album",
                  "playlist", "lista", "musica", "cancion", "canciones", "mi", "mis", "coleccion", "disco", "discos",
                  "por", "favor", "con", "nombre", "en", "modo"}
PALABRAS_ALEATORIO = {"aleatoria", "aleatorio", "aleatoriamente", "mezclada", "mezclado", "shuffle"}


def reproductores_activos(extra=()):
    """Reproductores de música abiertos: [{nombre, exe, ruta, hwnd, titulo}]. Solo Windows."""
    if os.name != "nt":
        return []
    from ctypes import wintypes
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                                               ctypes.POINTER(wintypes.DWORD)]
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    conocidos = dict(REPRODUCTORES)
    for nombre in extra:                              # el que el usuario eligió en el menú, aunque no esté en la lista
        n = nombre.strip().lower()
        if n:
            conocidos.setdefault(n if n.endswith(".exe") else n + ".exe", nombre.strip())
            conocidos.setdefault(n.replace(" ", "") + ".exe", nombre.strip())
    ventanas = []

    def enum(hwnd, _):
        try:
            n = user32.GetWindowTextLengthW(hwnd)
            if n > 0:
                buf = ctypes.create_unicode_buffer(n + 1)
                user32.GetWindowTextW(hwnd, buf, n + 1)
                pid = wintypes.DWORD(0)
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                ventanas.append((pid.value, hwnd, bool(user32.IsWindowVisible(hwnd)), buf.value))
        except Exception:
            pass
        return True

    proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)(enum)
    user32.EnumWindows(proc, 0)
    por_pid = {}
    for pid, hwnd, vis, tit in ventanas:
        por_pid.setdefault(pid, []).append((vis, len(tit), hwnd or 0, tit))
    mejores = {}
    for pid, vs in por_pid.items():
        h = k32.OpenProcess(0x1000, False, pid)        # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            continue
        try:
            buf = ctypes.create_unicode_buffer(1024)
            n = wintypes.DWORD(1024)
            ruta = buf.value if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)) else ""
        finally:
            k32.CloseHandle(h)
        exe = os.path.basename(ruta).lower()
        if exe in conocidos:
            vis, _, hwnd, tit = max(vs)               # ventana visible y con el título más largo
            previo = mejores.get(exe)
            if previo is None or (vis, len(tit)) > (previo["visible"], len(previo["titulo"])):
                mejores[exe] = {"nombre": conocidos[exe], "exe": exe, "ruta": ruta, "hwnd": hwnd, "titulo": tit,
                                "visible": vis}
    return list(mejores.values())


def elegir_reproductor(lista, preferido="", ultimo=""):
    """De los reproductores abiertos: el preferido, si no el último usado, si no el primero."""
    if not lista:
        return None
    for ref in (preferido, ultimo):
        r = normalizar(ref or "")
        if r:
            for p in lista:
                if r == normalizar(p["nombre"]) or r in normalizar(p["nombre"]) or r == normalizar(p["exe"][:-4]):
                    return p
    return lista[0]


def _smtc_clase():
    for mod in ("winrt.windows.media.control", "winsdk.windows.media.control"):
        try:
            return importlib.import_module(mod).GlobalSystemMediaTransportControlsSessionManager
        except Exception:
            continue
    return None


def _claves_sesion(rep):
    """Trozos (en minúsculas y sin símbolos) que identifican a un reproductor en el id de su sesión multimedia."""
    if not rep:
        return []
    claves = []
    for t in (rep.get("exe", "")[:-4], rep.get("nombre", "")):
        t = re.sub(r"[^a-z0-9]", "", t.lower())
        if len(t) >= 3 and t not in claves:
            claves.append(t)
    return claves


async def _smtc_go(accion, claves, info):
    M = _smtc_clase()
    if M is None:
        return None
    mgr = await M.request_async()
    ses = None
    if claves:
        for s in mgr.get_sessions():
            aid = re.sub(r"[^a-z0-9]", "", (s.source_app_user_model_id or "").lower())
            if any(c in aid for c in claves):
                ses = s
                break
    else:
        ses = mgr.get_current_session()            # sin reproductor conocido: lo que sea que esté sonando (p. ej. el navegador)
    if ses is None:
        return None
    if info:
        p = await ses.try_get_media_properties_async()
        return (p.title or "", p.artist or "")
    metodo = {"siguiente": ses.try_skip_next_async, "anterior": ses.try_skip_previous_async,
              "pausa": ses.try_pause_async, "play": ses.try_play_async, "detener": ses.try_stop_async,
              "alternar": ses.try_toggle_play_pause_async}[accion]
    return bool(await metodo())


def smtc(accion, claves=(), info=False, espera=4.0):
    """Manda una acción a la sesión multimedia de Windows (SMTC) del reproductor, en un hilo propio (COM).
    True/False según la aceptó; con info=True devuelve (título, artista); None si SMTC no está disponible o no hay sesión."""
    res = []

    def trabajo():
        try:
            import asyncio
            res.append(asyncio.run(_smtc_go(accion, list(claves), info)))
        except Exception:
            logging.debug("SMTC no disponible", exc_info=True)
            res.append(None)

    h = threading.Thread(target=trabajo, daemon=True)
    h.start()
    h.join(espera)
    return res[0] if res else None


def enviar_media(accion, reproductor=None):
    """accion: siguiente | anterior | pausa | play | detener. Devuelve cómo se envió: 'ventana' | 'smtc' | 'tecla'.
    1) Reproductores clásicos (VLC, foobar2000, MusicBee…): mensaje WM_APPCOMMAND a su ventana.
    2) Los demás (Harmonoid, Spotify, apps de la tienda, navegadores): la sesión multimedia de Windows (SMTC).
    3) Si no hay SMTC (falta winrt) o la rechaza: tecla multimedia global, que recibe la sesión más reciente."""
    if os.name != "nt":
        raise RuntimeError("Solo funciona en Windows")
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    if reproductor and reproductor.get("hwnd") and reproductor.get("exe") in APPCOMMAND_OK:
        from ctypes import wintypes
        user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        user32.PostMessageW.restype = wintypes.BOOL
        hwnd = reproductor["hwnd"]
        if user32.PostMessageW(hwnd, WM_APPCOMMAND, hwnd, APPCOMMAND[accion] << 16):
            return "ventana"
    if smtc(accion, _claves_sesion(reproductor)):
        return "smtc"
    vk = VK_MEDIA.get(accion, 0xB3)
    user32.keybd_event(vk, 0, 1, 0)                      # KEYEVENTF_EXTENDEDKEY
    time.sleep(0.03)
    user32.keybd_event(vk, 0, 3, 0)                      # + KEYEVENTF_KEYUP
    return "tecla"


def raices_musica(texto_cfg=""):
    """Carpetas donde buscar música: Música del usuario, las que añadió en el menú y carpetas «música» en cada disco."""
    home = os.path.expanduser("~")
    cand = [os.path.join(home, n) for n in ("Music", "Música", "Musica")]
    for var in ("OneDrive", "OneDriveConsumer", "OneDriveCommercial"):
        base = os.environ.get(var)
        if base:
            cand += [os.path.join(base, n) for n in ("Music", "Música", "Musica")]
    for t in str(texto_cfg or "").split(";"):
        t = t.strip().strip('"')
        if t:
            cand.append(expandir(t))
    try:
        k32 = ctypes.windll.kernel32
        mascara = k32.GetLogicalDrives()
        for i in range(26):
            letra = f"{chr(65 + i)}:\\"
            if mascara >> i & 1 and k32.GetDriveTypeW(letra) == 3:          # solo discos fijos
                for n in os.listdir(letra):
                    if re.search(r"music|musica|cancion|songs|mp3|audio", normalizar(n)):
                        cand.append(os.path.join(letra, n))
    except Exception:
        pass
    vistas, raices = set(), []
    for c in cand:
        try:
            clave = os.path.normcase(os.path.abspath(c))
            if clave not in vistas and os.path.isdir(c):
                vistas.add(clave)
                raices.append(c)
        except Exception:
            pass
    return raices


def indexar_musica(raices, limite_s=8.0, max_carpetas=6000, profundidad=4):
    """[(ruta, nombre normalizado)] de las carpetas dentro de las raíces."""
    inicio, res = time.time(), []
    for raiz in raices:
        base = raiz.rstrip("\\/").count(os.sep)
        for actual, dirs, _ in os.walk(raiz):
            if time.time() - inicio > limite_s or len(res) >= max_carpetas:
                return res
            if actual.count(os.sep) - base >= profundidad:
                dirs[:] = []
            dirs[:] = [d for d in dirs if not d.startswith((".", "$"))]
            nom = normalizar(os.path.basename(actual.rstrip("\\/")))
            if nom:
                res.append((actual, nom))
    return res


_FON_CACHE = {}
_FON_REGLAS = [(re.compile(a), b) for a, b in [
    (r"\be(?=s[^aeiou\s])", ""),                      # «escuelas» ~ «skulls»: el español añade una e antes de sk/st/sp
    (r"\b[gh]u(?=[aeio])", "u"),                      # «guord» / «huord» = «word»
    (r"\bwr", "r"), (r"mb\b", "m"), (r"(?:tion|sion)\b", "sion"), (r"ing\b", "in"), (r"au|aw", "o"), (r"oi|oy", "oi"),
    (r"ph", "f"), (r"tch|ch", "x"), (r"sh", "x"), (r"th", "t"), (r"ck", "k"), (r"qu", "k"), (r"\bkn", "n"),
    (r"wh", "u"), (r"w", "u"), (r"gh", ""), (r"ee|ea|ie", "i"), (r"oo|ou", "u"), (r"ai|ay|ey", "e"),
    (r"oa|ow", "o"), (r"c(?=[eiy])", "s"), (r"c", "k"), (r"z", "s"), (r"g(?=[ei])", "j"), (r"y", "i"),
    (r"v", "b"), (r"h", ""), (r"x", "ks"), (r"q", "k"), (r"(.)\1+", r"\1")]]


def fonetica(texto):
    """Aproxima cómo SUENA un texto (inglés o español) con letras españolas, para comparar lo que oyó Vosk
    (que solo sabe español: 'linkin park' lo oye como 'linquin parc') con el nombre real de la carpeta o canción."""
    f = _FON_CACHE.get(texto)
    if f is not None:
        return f
    t = normalizar(texto)
    for rx, b in _FON_REGLAS:
        t = rx.sub(b, t)
    t = t.replace(" ", "")
    if len(t) > 5:
        t = re.sub(r"[ei]\b", "", t)                          # 'e' muda final (love, stone)
    _FON_CACHE[texto] = t
    return t


def _esqueleto(f):
    """Solo consonantes: lo más estable cuando el reconocedor cambia las vocales de una palabra inglesa."""
    return re.sub(r"[aeiou]", "", f)


def _ratio(a, b, minimo=0.0):
    if not a or not b:
        return 0.0
    sm = SequenceMatcher(None, a, b)
    if sm.real_quick_ratio() < minimo or sm.quick_ratio() < minimo:
        return 0.0
    return sm.ratio()


def _puntuar(pedido, toks, fp, ep, nom, profundo=True):
    """0-1: cuánto se parece lo pedido a un nombre (letras Y sonido). Con profundo=False solo mira coincidencias
    directas (muy rápido, para miles de canciones); con True añade el parecido borroso."""
    if not nom:
        return 0.0
    if nom == pedido:
        return 1.0
    nt = nom.split()
    if all(t in nt for t in toks):
        return 0.93 - min(0.15, 0.02 * (len(nt) - len(toks)))
    if pedido in nom:
        return 0.88
    fn = fonetica(nom)
    if fp and fn and len(fp) >= 4 and fp in fn:                # 'linkin' dentro de 'linkin park'
        return 0.9 if len(fp) / len(fn) >= 0.5 else 0.8
    if not profundo:
        return 0.0
    s = _ratio(pedido, nom, 0.5)
    if nt:
        por_palabra = sum(max(_ratio(t, n, 0.5) for n in nt) for t in toks) / len(toks)
        s = max(s, por_palabra * 0.9)
    if fp and fn:
        en = _esqueleto(fn)
        se = _ratio(ep, en, 0.5) if ep and en and min(len(ep), len(en)) >= 3 else 0.0
        s = max(s, _ratio(fp, fn, 0.5) * 0.95, se * 0.88)
    return s


def mejor_carpeta(indice, pedido, minimo=0.62):
    """(ruta, puntuación) de la carpeta que más se parece a lo que se dijo, o None."""
    toks = pedido.split()
    if not toks:
        return None
    fp = fonetica(pedido)
    ep = _esqueleto(fp)
    mejor_s, mejor_r = 0.0, None
    for profundo in (False, True):
        for ruta, nom in indice:
            s = _puntuar(pedido, toks, fp, ep, nom, profundo)
            if s > mejor_s:
                mejor_s, mejor_r = s, ruta
        if mejor_s >= 0.88:
            break
    return (mejor_r, mejor_s) if mejor_s >= minimo and mejor_r else None


def mejor_etiqueta(dic, pedido, minimo=0.7):
    """(nombre, rutas, puntuación) del artista o álbum (de las etiquetas) que más se parece a lo dicho, o None."""
    toks = pedido.split()
    if not toks or not dic:
        return None
    fp = fonetica(pedido)
    ep = _esqueleto(fp)
    mejor_s, mejor_n = 0.0, None
    for profundo in (False, True):
        for nom in dic:
            s = _puntuar(pedido, toks, fp, ep, nom, profundo)
            if s > mejor_s:
                mejor_s, mejor_n = s, nom
        if mejor_s >= 0.88:
            break
    return (dic[mejor_n][0], dic[mejor_n][1], mejor_s) if mejor_n and mejor_s >= minimo else None


EXT_SIN_PERDIDA = (".flac", ".wav", ".ape", ".wv", ".aiff", ".aif", ".alac")


def indexar_canciones(raices, limite_s=25.0, maximo=80000, profundidad=8):
    """[(ruta, nombre normalizado, nombre sin nº de pista, carpetas normalizadas)] de todos los audios."""
    inicio, res, vistos = time.time(), [], set()
    for raiz in raices:
        base = raiz.rstrip("\\/").count(os.sep)
        for actual, dirs, files in os.walk(raiz):
            if time.time() - inicio > limite_s or len(res) >= maximo:
                return res
            if actual.count(os.sep) - base >= profundidad:
                dirs[:] = []
            dirs[:] = [d for d in dirs if not d.startswith((".", "$"))]
            ctx = " ".join(p for p in (normalizar(x) for x in actual.rstrip("\\/").split(os.sep)[-2:]) if p)
            for f in files:
                if f.lower().endswith(EXT_AUDIO):
                    ruta = os.path.join(actual, f)
                    clave = os.path.normcase(ruta)
                    if clave in vistos:
                        continue
                    vistos.add(clave)
                    nom = normalizar(os.path.splitext(f)[0])
                    res.append((ruta, nom, re.sub(r"^\d{1,3}\s*", "", nom) or nom, ctx))
    return res


def archivo_etiquetas():
    """alfred_etiquetas.json en la carpeta privada (si estaba junto al script de una versión anterior, se mueve)."""
    nuevo = os.path.join(datos_dir(), "alfred_etiquetas.json")
    viejo = os.path.join(BASE_DIR, "alfred_etiquetas.json")
    if os.path.exists(viejo) and not os.path.exists(nuevo):
        try:
            shutil.move(viejo, nuevo)
        except OSError:
            logging.exception("No pude mover alfred_etiquetas.json a la carpeta privada")
    return nuevo


def _etq_flac(ruta):
    """([artistas], álbum) de un FLAC leyendo su bloque Vorbis comment (sin librerías)."""
    with open(ruta, "rb") as f:
        if f.read(4) != b"fLaC":
            return None
        while True:
            h = f.read(4)
            if len(h) < 4:
                return None
            ultimo, tipo, n = h[0] & 0x80, h[0] & 0x7F, int.from_bytes(h[1:4], "big")
            if tipo != 4:
                f.seek(n, 1)
                if ultimo:
                    return None
                continue
            d = f.read(n)
            i = 4 + int.from_bytes(d[0:4], "little")                      # tras el «vendor»
            cuantos = int.from_bytes(d[i:i + 4], "little")
            i += 4
            art, alb = [], ""
            for _ in range(cuantos):
                largo = int.from_bytes(d[i:i + 4], "little")
                i += 4
                k, _, v = d[i:i + largo].decode("utf-8", "replace").partition("=")
                i += largo
                k = k.lower()
                if k in ("artist", "albumartist") and v:
                    art.append(v)
                elif k == "album" and v and not alb:
                    alb = v
            return art, alb


def _etq_id3(ruta):
    """([artistas], álbum) de un MP3 con ID3v2.3/2.4 (sin librerías)."""
    with open(ruta, "rb") as f:
        cab = f.read(10)
        if len(cab) < 10 or cab[:3] != b"ID3" or cab[3] < 3:
            return None
        ver = cab[3]
        tam = (cab[6] << 21) | (cab[7] << 14) | (cab[8] << 7) | cab[9]
        d = f.read(min(tam, 1 << 20))
    i, art, alb = 0, [], ""
    while i + 10 <= len(d):
        idf = d[i:i + 4]
        if not idf.strip(b"\x00"):
            break
        if ver == 4:
            n = (d[i + 4] << 21) | (d[i + 5] << 14) | (d[i + 6] << 7) | d[i + 7]
        else:
            n = int.from_bytes(d[i + 4:i + 8], "big")
        cuerpo = d[i + 10:i + 10 + n]
        i += 10 + n
        if idf in (b"TPE1", b"TPE2", b"TALB") and len(cuerpo) > 1:
            codec = {0: "latin-1", 1: "utf-16", 2: "utf-16-be", 3: "utf-8"}.get(cuerpo[0], "latin-1")
            try:
                txt = cuerpo[1:].decode(codec, "replace")
            except Exception:
                continue
            partes = [p.strip() for p in txt.split("\x00") if p.strip()]
            if idf == b"TALB":
                alb = alb or (partes[0] if partes else "")
            else:
                art += partes
    return art, alb


def leer_etiquetas(ruta):
    """([artistas], álbum) de un audio, o None. Usa mutagen si está instalado (cualquier formato); si no, lee
    por su cuenta FLAC y MP3."""
    try:
        import mutagen
        m = mutagen.File(ruta, easy=True)
        if m is not None and getattr(m, "tags", None):
            def g(k):
                return [str(x) for x in (m.tags.get(k) or [])]
            return g("artist") + g("albumartist"), (g("album") or [""])[0]
    except Exception:
        pass
    ext = os.path.splitext(ruta)[1].lower()
    try:
        if ext == ".flac":
            return _etq_flac(ruta)
        if ext == ".mp3":
            return _etq_id3(ruta)
    except Exception:
        pass
    return None


def _separar_artistas(vals):
    """«A feat. B; C» -> ['A feat. B; C', 'A', 'B', 'C']: el nombre completo y cada artista por separado."""
    res = []
    for v in vals:
        for p in [v] + re.split(r"\s*(?:;|/|\bfeat\.?|\bft\.?|\bfeaturing\b|\bwith\b)\s*", v, flags=re.I):
            p = p.strip()
            if len(p) >= 2 and p not in res:
                res.append(p)
    return res


def indexar_etiquetas(rutas, limite_s=12.0):
    """({'artista': {nombre normalizado: [nombre, [rutas]]}, 'album': {…}}, pendientes). Lee las etiquetas de cada
    canción una sola vez (caché en alfred_etiquetas.json, se renueva si cambia el archivo). Si tarda más que
    limite_s deja el resto para la próxima vez y lo dice en «pendientes»."""
    try:
        with open(archivo_etiquetas(), encoding="utf-8") as f:
            cache = json.load(f)
    except Exception:
        cache = {}
    inicio, nuevo, pendientes = time.time(), False, 0
    vivo, res = {}, {"artista": {}, "album": {}}
    for r in rutas:
        e = cache.get(r)
        if time.time() - inicio > limite_s:
            if not e:
                pendientes += 1
                continue
        else:
            try:
                mt = int(os.path.getmtime(r))
            except OSError:
                continue
            if not e or e[0] != mt:
                et = leer_etiquetas(r) or ([], "")
                e = [mt, _separar_artistas(et[0]), et[1]]
                nuevo = True
        vivo[r] = e
        for a in e[1]:
            n = normalizar(a)
            if n:
                res["artista"].setdefault(n, [a, []])[1].append(r)
        if e[2]:
            n = normalizar(e[2])
            if n:
                res["album"].setdefault(n, [e[2], []])[1].append(r)
    if nuevo or len(vivo) != len(cache):
        try:
            with open(archivo_etiquetas(), "w", encoding="utf-8") as f:
                json.dump(vivo, f, ensure_ascii=False)
        except Exception:
            logging.exception("No pude guardar las etiquetas")
    return res, pendientes


def _clave_natural(x):
    return [int(t) if i % 2 else t for i, t in enumerate(re.split(r"(\d+)", x.lower()))]


def _variantes_pedido(pedido):
    """'numb de linkin park' -> [título completo] + [('numb', 'linkin park')]: título solo o título + artista."""
    toks = pedido.split()
    v = [(pedido, "")]
    for i, t in enumerate(toks):
        if t in ("de", "del", "por", "by", "of") and 0 < i < len(toks) - 1:
            v.append((" ".join(toks[:i]), " ".join(toks[i + 1:])))
    return v


def mejor_cancion(indice, pedido, minimo=0.66):
    """(ruta, puntuación) de la canción que más se parece a lo pedido, o None. Entiende «título de artista»,
    «artista título» y nombres en inglés dichos en español. A igualdad prefiere los formatos sin pérdida (FLAC)."""
    prep = []
    for tit, art in _variantes_pedido(pedido):
        tt = tit.split()
        if tt:
            ft = fonetica(tit)
            prep.append((tit, tt, ft, _esqueleto(ft), art, art.split(), fonetica(art) if art else "",
                         _esqueleto(fonetica(art)) if art else ""))
    if not prep:
        return None
    sueltas = {"de", "del", "la", "el", "los", "las", "y", "the", "a", "of", "by"}
    fped = [fonetica(t) for t in pedido.split() if t not in sueltas]
    ctx_cache = {}

    def cubiertos_ctx(ctx):
        """Índices de las palabras del pedido que SUENAN como alguna palabra de las carpetas (artista / álbum)."""
        r = ctx_cache.get(ctx)
        if r is None:
            cw = [fonetica(w) for w in ctx.split()]
            r = {i for i, f in enumerate(fped) if any(f == c or (len(f) >= 4 and _ratio(f, c, 0.7) >= 0.7) for c in cw)}
            ctx_cache[ctx] = r
        return r

    mejor_s, mejor_r = 0.0, None
    for profundo in (False, True):
        for ruta, nom, limpio, ctx in indice:
            mejor_local = 0.0
            for tit, tt, ft, et, art, at, fa, ea in prep:
                base = _puntuar(tit, tt, ft, et, limpio, profundo)
                if nom != limpio:
                    base = max(base, _puntuar(tit, tt, ft, et, nom, profundo))
                if art:
                    a = 1.0 if all(t in ctx.split() or t in nom.split() for t in at) \
                        else _puntuar(art, at, fa, ea, ctx, profundo)
                    base = 0.7 * base + 0.3 * a
                mejor_local = max(mejor_local, base)
            if mejor_local < 0.88 and fped:                          # «artista título» (o «título artista») en cualquier orden
                ft = [fonetica(w) for w in limpio.split()]
                en_nombre = {i for i, f in enumerate(fped) if f in ft}
                if profundo:
                    en_nombre |= {i for i, f in enumerate(fped) if len(f) >= 4 and any(_ratio(f, c, 0.75) >= 0.75 for c in ft)}
                if en_nombre and len(en_nombre | cubiertos_ctx(ctx)) == len(fped):
                    mejor_local = max(mejor_local, 0.9 if not profundo else 0.84)
            if mejor_local >= 0.5 and ruta.lower().endswith(EXT_SIN_PERDIDA):
                mejor_local += 0.002                                 # desempata a favor del FLAC
            if mejor_local > mejor_s:
                mejor_s, mejor_r = mejor_local, ruta
        if mejor_s >= 0.88:
            break
    return (mejor_r, mejor_s) if mejor_s >= minimo else None


class SpotifyAPI:
    """Spotify por su API oficial (PKCE, sin secreto de cliente): busca la canción o el artista y lo pone en la app
    de Spotify de este PC (o de otro dispositivo tuyo). Spotify exige cuenta Premium y que crees tu propia «app» gratis
    en developer.spotify.com (de ahí sale el Client ID). Solo se guarda el token de renovación, en alfred_config.json."""
    PUERTO = 8888
    REDIRECT = f"http://127.0.0.1:{PUERTO}/callback"       # debe registrarse EXACTAMENTE así en el panel de Spotify
    SCOPES = "user-modify-playback-state user-read-playback-state"
    URL_TOKEN = "https://accounts.spotify.com/api/token"

    def __init__(self, cfg):
        self.cfg = cfg
        self._tok, self._exp = "", 0.0

    def client_id(self):
        return (self.cfg.get("spotify_client_id") or "").strip()

    def conectado(self):
        return bool(self.client_id() and self.cfg.get_secreto("spotify_refresh"))

    def conectar(self, avisar=lambda t: None, espera=150):
        """Abre el navegador para que autorices a Alfred una sola vez. True si quedó conectado."""
        cid = self.client_id()
        if not cid:
            return False
        verificador = secrets.token_urlsafe(72)[:96]
        desafio = base64.urlsafe_b64encode(hashlib.sha256(verificador.encode()).digest()).rstrip(b"=").decode()
        estado = secrets.token_urlsafe(12)
        recibido = {}

        class Manejador(BaseHTTPRequestHandler):
            def do_GET(self):
                u = urlparse(self.path)
                if u.path != "/callback":
                    self.send_response(404)
                    self.end_headers()
                    return
                recibido.update({k: v[0] for k, v in parse_qs(u.query).items() if k in ("code", "state", "error")})
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write("<html><body style='font-family:sans-serif;background:#070b12;color:#e8f1fb;"
                                 "text-align:center;padding-top:80px'><h2>Spotify conectado</h2>"
                                 "<p>Ya puedes cerrar esta pestaña y volver a hablar con tu asistente.</p>"
                                 "</body></html>".encode("utf-8"))

            def log_message(self, *a):
                pass

        try:
            srv = ThreadingHTTPServer(("127.0.0.1", self.PUERTO), Manejador)
        except OSError as e:
            avisar(f"⚠️ No pude abrir el puerto {self.PUERTO} para conectar Spotify: {e}")
            return False
        srv.timeout = 1.0
        avisar(f"🎧 Autoriza a Alfred en la página de Spotify que se abrió (el Client ID debe tener registrada la "
               f"dirección {self.REDIRECT}).")
        webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode({
            "client_id": cid, "response_type": "code", "redirect_uri": self.REDIRECT, "scope": self.SCOPES,
            "code_challenge_method": "S256", "code_challenge": desafio, "state": estado}))
        fin = time.time() + espera
        try:
            while time.time() < fin and not recibido:
                srv.handle_request()
        finally:
            srv.server_close()
        if recibido.get("state") != estado or "code" not in recibido:
            avisar("⚠️ Spotify no devolvió la autorización" + (f" ({recibido['error']})" if recibido.get("error") else "") + ".")
            return False
        try:
            r = requests.post(self.URL_TOKEN, data={"grant_type": "authorization_code", "code": recibido["code"],
                                                    "redirect_uri": self.REDIRECT, "client_id": cid,
                                                    "code_verifier": verificador}, timeout=15)
            j = r.json()
        except Exception as e:
            logging.exception("Spotify: canje del código")
            avisar(f"⚠️ No pude hablar con Spotify: {e}")
            return False
        if r.status_code != 200 or not j.get("refresh_token"):
            avisar(f"⚠️ Spotify rechazó la conexión: {j.get('error_description') or j.get('error') or r.status_code}")
            return False
        self._tok, self._exp = j["access_token"], time.time() + int(j.get("expires_in", 3600))
        self.cfg.set_secreto("spotify_refresh", j["refresh_token"])
        return True

    def _token(self):
        if self._tok and time.time() < self._exp - 30:
            return self._tok
        refresh = self.cfg.get_secreto("spotify_refresh")
        if not refresh:
            return None
        r = requests.post(self.URL_TOKEN, data={"grant_type": "refresh_token", "refresh_token": refresh,
                                                "client_id": self.client_id()}, timeout=15)
        if r.status_code != 200:
            logging.error("Spotify: no pude renovar el token (HTTP %s)", r.status_code)
            if r.status_code in (400, 401):
                self.cfg.set_secreto("spotify_refresh", "")     # caducó o la revocaste: hay que volver a conectar
            return None
        j = r.json()
        self._tok, self._exp = j["access_token"], time.time() + int(j.get("expires_in", 3600))
        if j.get("refresh_token"):
            self.cfg.set_secreto("spotify_refresh", j["refresh_token"])
        return self._tok

    def _llamar(self, metodo, ruta, **kw):
        tok = self._token()
        if not tok:
            raise RuntimeError("Spotify sin conectar")
        return requests.request(metodo, "https://api.spotify.com/v1" + ruta, headers={"Authorization": "Bearer " + tok},
                                timeout=12, **kw)

    def buscar(self, consulta, es_artista=False):
        """{'tipo': 'cancion'|'artista'|'album', 'nombre', 'artista', 'uri'} del mejor resultado, o None."""
        r = self._llamar("GET", "/search", params={"q": consulta, "limit": 5,
                                                   "type": "artist" if es_artista else "track,artist,album"})
        if r.status_code != 200:
            logging.error("Spotify: búsqueda rechazada (HTTP %s)", r.status_code)
            return None
        j = r.json()
        arts = [x for x in ((j.get("artists") or {}).get("items") or []) if x]
        pis = [x for x in ((j.get("tracks") or {}).get("items") or []) if x]
        pn = normalizar(consulta)
        if es_artista and arts:
            return {"tipo": "artista", "nombre": arts[0]["name"], "artista": "", "uri": arts[0]["uri"]}
        if pis:
            t = pis[0]
            if arts and normalizar(arts[0]["name"]) == pn and normalizar(t["name"]) != pn:
                return {"tipo": "artista", "nombre": arts[0]["name"], "artista": "", "uri": arts[0]["uri"]}
            return {"tipo": "cancion", "nombre": t["name"], "uri": t["uri"],
                    "artista": ", ".join(a["name"] for a in (t.get("artists") or [])[:2])}
        if arts:
            return {"tipo": "artista", "nombre": arts[0]["name"], "artista": "", "uri": arts[0]["uri"]}
        return None

    def dispositivo(self, abrir_app):
        """ID del dispositivo donde poner la música: el activo, si no este PC, si no el primero. Si no hay ninguno
        (Spotify cerrado) abre la app y espera a que aparezca."""
        for intento in range(15):
            r = self._llamar("GET", "/me/player/devices")
            devs = (r.json().get("devices") or []) if r.status_code == 200 else []
            if devs:
                activos = [d for d in devs if d.get("is_active")]
                pcs = [d for d in devs if d.get("type") == "Computer"]
                d = (activos or pcs or devs)[0]
                return d["id"], bool(d.get("is_active"))
            if intento == 0:
                abrir_app()
            time.sleep(1.0)
        return None, False

    def reproducir(self, hallazgo, abrir_app):
        """'ok' | 'premium' | 'sin_dispositivo' | 'error NNN'."""
        dev, activo = self.dispositivo(abrir_app)
        if not dev:
            return "sin_dispositivo"
        if not activo:                                          # despierta el dispositivo antes de pedirle música
            self._llamar("PUT", "/me/player", json={"device_ids": [dev], "play": False})
            time.sleep(0.8)
        cuerpo = {"uris": [hallazgo["uri"]]} if hallazgo["tipo"] == "cancion" else {"context_uri": hallazgo["uri"]}
        r = self._llamar("PUT", "/me/player/play", params={"device_id": dev}, json=cuerpo)
        if r.status_code in (200, 202, 204):
            return "ok"
        logging.error("Spotify: reproducir rechazado (HTTP %s)", r.status_code)
        if r.status_code == 403:
            return "premium"
        if r.status_code == 404:
            return "sin_dispositivo"
        return f"error {r.status_code}"


# ── cómo se piden las cosas por voz ──────────────────────────────────────────
VERBOS_PON = {"reproduce", "reproduceme", "reproducir", "pon", "ponme", "poner", "toca", "tocame", "tocar",
              "escuchar", "escucha", "oir"}
SALTAR_INICIO = {"por", "favor", "oye", "ahora", "puedes", "podrias", "me", "quiero", "queremos", "quisiera", "y",
                 "entonces", "ya", "mira", "pues", "a", "ver", "deseo"}
ARTICULOS = {"la", "el", "los", "las", "una", "un", "mi", "esa", "ese", "esta", "este"}
PALABRAS_TEMA = {"cancion", "canciones", "tema", "temazo", "rola", "pista"}
NO_ES_CANCION = {"volumen", "brillo", "silencio", "play", "pausa", "reproductor", "anterior", "siguiente", "proxima",
                 "previa", "spotify", "carpeta", "carpetas", "album", "disco", "playlist", "lista", "coleccion",
                 "musica", "sonido", "alarma", "temporizador", "calculadora", "bloc", "explorador", "agenda",
                 "ventana", "modo", "pantalla", "computadora", "equipo", "pc", "compu", "captura", "tema", "zoom",
                 "timer", "cronometro", "escritorio", "wifi", "bluetooth", "mouse", "raton", "cuadricula",
                 "dictado", "configuracion", "ajustes", "papelera", "portapapeles", "bateria"}


PLATAFORMAS = (   # (cómo suena, plataforma) — Vosk oye en español: «espotifai», «yutub»…
    ("youtube music", "ytmusic"), ("yutub music", "ytmusic"), ("yutube music", "ytmusic"), ("you tube music", "ytmusic"),
    ("espotifai", "spotify"), ("espoti fai", "spotify"), ("espotifay", "spotify"), ("spotifai", "spotify"),
    ("espotify", "spotify"), ("spotify", "spotify"), ("espoti", "spotify"),
    ("youtube", "youtube"), ("yutub", "youtube"), ("yutube", "youtube"), ("you tube", "youtube"), ("iutub", "youtube"),
)
_PLAT_DE = dict(PLATAFORMAS)
_PLAT_ALT = "|".join(re.escape(f) for f, _ in sorted(PLATAFORMAS, key=lambda x: -len(x[0])))
_PLAT_PRE = r"(?:la\s+|el\s+)?(?:app\s+de\s+|aplicacion\s+de\s+|plataforma\s+)?"
_RX_PLAT_FIN = re.compile(r"\s(?:en|por|desde|con|usando|mediante|a traves de)\s+" + _PLAT_PRE + "(" + _PLAT_ALT + r")$")
_RX_PLAT_INI = re.compile(r"^(?:en|por|desde|con|usando)\s+" + _PLAT_PRE + "(" + _PLAT_ALT + r")\s+")
PALABRAS_ARTISTA = {"banda", "grupo", "artista", "cantante", "cantautor", "cantautora", "agrupacion"}
DE_ARTISTA = {"canciones", "temas", "rolas", "exitos", "pistas", "musica", "algo", "cosas", "discografia"}


def separar_plataforma(toks):
    """(palabras sin la plataforma, plataforma o None): 'numb en spotify' -> (['numb'], 'spotify'). Solo la quita al
    final («… en Spotify») o al principio («en Spotify …»), para no comerse una canción que se llame así."""
    texto = " " + " ".join(toks)
    m = _RX_PLAT_FIN.search(texto)
    if m:
        return texto[:m.start()].split(), _PLAT_DE[m.group(1)]
    t = " ".join(toks) + " "
    m = _RX_PLAT_INI.match(t)
    if m:
        return t[m.end():].split(), _PLAT_DE[m.group(1)]
    return list(toks), None


def pedido_cancion_ex(norm):
    """'reproduce canciones de la banda future en spotify' -> ('future', True, 'spotify'): (lo pedido, si pide un
    artista, plataforma o None). None si no es una petición de canción (por ejemplo 'pon la carpeta rock', 'pon play',
    'pon el volumen al 30', 'pon música')."""
    toks = norm.split()
    i = 0
    while i < len(toks) and toks[i] in SALTAR_INICIO:
        i += 1
    if i >= len(toks) or toks[i] not in VERBOS_PON:
        return None
    resto = toks[i + 1:]
    while resto and resto[0] in ARTICULOS | {"me"}:
        resto.pop(0)
    while resto and resto[-1] in {"por", "favor", "gracias"}:
        resto.pop()
    resto, plataforma = separar_plataforma(resto)
    while resto and resto[0] in ARTICULOS | {"me"}:
        resto.pop(0)
    es_artista = False
    if len(resto) >= 3 and resto[0] in DE_ARTISTA and resto[1] in {"de", "del"}:      # «canciones de X», «música de X»
        es_artista = True
        resto = resto[2:]
        while resto and resto[0] in ARTICULOS:
            resto.pop(0)
    if resto and resto[0] in PALABRAS_ARTISTA:                                       # «la banda X», «el grupo X»
        es_artista = True
        resto.pop(0)
        while resto and resto[0] in ARTICULOS | {"de", "del", "llamada", "llamado", "que", "se", "llama"}:
            resto.pop(0)
    explicita = bool(resto) and resto[0] in PALABRAS_TEMA
    if explicita:
        resto.pop(0)
        while resto and resto[0] in ARTICULOS | {"de", "llamada", "llamado", "que", "se", "llama", "titulada", "titulado"}:
            resto.pop(0)
    if not resto:
        return None
    if resto[0] in {"anterior", "siguiente", "proxima", "previa"}:
        return None
    if not explicita and resto[0] in NO_ES_CANCION:
        return None
    return " ".join(resto), es_artista, plataforma


def pedido_cancion(norm):
    """'reproduce la cancion numb de linkin park' -> 'numb de linkin park'. None si no es una petición de canción."""
    r = pedido_cancion_ex(norm)
    return r[0] if r else None


_PEDIDO_SUELTAS = {"de", "del", "la", "el", "los", "las", "y", "the", "a", "an", "of", "by", "in", "on", "to", "it", "i",
                   "un", "una", "me", "mi", "mis", "en", "se", "que"}


def pedido_valido(p):
    """False para lecturas basura de otro idioma: letras sueltas o solo palabras vacías («a», «the», «de la»)."""
    toks = normalizar(p or "").split()
    return bool(toks) and len("".join(toks)) >= 3 and any(t not in _PEDIDO_SUELTAS for t in toks)


def listar_audio(carpeta, limite=3000):
    """Canciones de la carpeta y sus subcarpetas, en orden natural (pista 2 antes que pista 10)."""
    def natural(x):
        return [int(t) if i % 2 else t for i, t in enumerate(re.split(r"(\d+)", x.lower()))]
    res = []
    for actual, dirs, files in os.walk(carpeta):
        dirs.sort(key=natural)
        for f in sorted(files, key=natural):
            if f.lower().endswith(EXT_AUDIO):
                res.append(os.path.join(actual, f))
        if len(res) >= limite:
            break
    return res[:limite]


ARTICULOS_Y_ENLACES = {"de", "del", "la", "el", "las", "los", "que", "se", "llama", "llamada", "llamado", "por",
                       "favor", "con", "nombre", "en", "modo", "titulada", "titulado"}


def pedidos_musica(norm, frases, estricto=False):
    """'reproduce la carpeta rock en aleatorio' -> (['rock'], True). Devuelve las formas posibles de lo pedido, la más
    limpia primero. Si TODO lo dicho era «relleno» ('mis canciones', 'música', 'discos'), ese relleno es el nombre de la
    carpeta y se conserva (antes quedaba vacío y Alfred preguntaba «¿qué carpeta?»). Con estricto=True devuelve None
    si la orden no contiene ninguna de las frases de «reproducir carpeta»."""
    texto = f" {norm} "
    mejor = None
    for f in frases:
        i = texto.find(f" {f} ")
        if i >= 0 and (mejor is None or len(f) > len(mejor[1])):
            mejor = (i, f)
    if mejor is None and estricto:
        return None
    resto = texto[mejor[0] + len(mejor[1]) + 2:] if mejor else norm
    toks = resto.split()
    aleatorio = any(t in PALABRAS_ALEATORIO for t in toks)
    toks = [t for t in toks if t not in PALABRAS_ALEATORIO]
    while toks and toks[-1] in {"en", "modo", "por", "favor", "gracias"}:
        toks.pop()
    completo = list(toks)
    while completo and completo[0] in ARTICULOS_Y_ENLACES:
        completo.pop(0)
    limpio = list(toks)
    while limpio and limpio[0] in RELLENO_INICIO:
        limpio.pop(0)
    variantes = []
    for v in (limpio, completo):
        t = " ".join(v)
        if t and t not in variantes:
            variantes.append(t)
    return variantes, aleatorio


def pedido_musica(norm, frases):
    """'reproduce la carpeta rock en aleatorio' -> ('rock', True): lo que se pidió tras la frase y si es aleatorio."""
    variantes, aleatorio = pedidos_musica(norm, frases)
    return (variantes[0] if variantes else ""), aleatorio


VERBOS_ABRIR = {"abre", "abrir", "abreme", "ejecuta", "inicia", "lanza", "arranca"}
SITIOS = {"youtube": "youtube.com", "google": "google.com", "gmail": "mail.google.com", "correo": "mail.google.com",
          "facebook": "facebook.com", "instagram": "instagram.com", "twitter": "x.com", "whatsapp": "web.whatsapp.com",
          "netflix": "netflix.com", "github": "github.com", "chatgpt": "chatgpt.com", "claude": "claude.ai",
          "drive": "drive.google.com", "maps": "maps.google.com", "mapas": "maps.google.com",
          "traductor": "translate.google.com", "noticias": "news.google.com", "tiktok": "tiktok.com",
          "twitch": "twitch.tv", "reddit": "reddit.com", "wikipedia": "es.wikipedia.org", "amazon": "amazon.com.mx",
          "mercado libre": "mercadolibre.com.mx"}
CARPETAS_CONOCIDAS = {"descargas": "Downloads", "documentos": "Documents", "escritorio": "Desktop",
                      "imagenes": "Pictures", "fotos": "Pictures", "videos": "Videos", "musica": "Music"}
APPS_CONOCIDAS = ["chrome", "firefox", "edge", "opera", "brave", "discord", "steam", "spotify", "whatsapp", "telegram",
                  "word", "excel", "powerpoint", "outlook", "teams", "zoom", "vlc", "obs", "paint", "cursor", "code",
                  "slack", "photoshop", "premiere", "blender", "minecraft", "notion", "obsidian", "foobar2000",
                  "musicbee", "aimp", "epic games", "visual studio code", "calculadora", "terminal"]


def nombre_a_abrir(norm):
    """'abre la aplicación word por favor' -> 'word' ('' si no hay verbo de abrir o no se dijo qué abrir)."""
    toks = norm.split()
    i = next((k for k, t in enumerate(toks) if t in VERBOS_ABRIR), None)
    resto = toks[i + 1:] if i is not None else []
    while resto and resto[0] in {"el", "la", "los", "las", "mi", "mis", "un", "una", "aplicacion", "programa", "app",
                                 "pagina", "web", "de", "carpeta", "por", "favor", "me"}:
        resto.pop(0)
    while resto and resto[-1] in {"por", "favor", "gracias"}:
        resto.pop()
    return " ".join(resto)


ALIAS_APPS = {   # cómo suelen oírse (en español) las apps con nombre inglés -> la app
    "uord": "word", "guord": "word", "huord": "word", "bord": "word", "gord": "word", "uor": "word", "guor": "word",
    "ford": "word", "uart": "word", "guart": "word", "ward": "word", "uorp": "word",
    "exel": "excel", "ecsel": "excel", "eksel": "excel", "ejcel": "excel",
    "pauerpoint": "powerpoint", "pauer point": "powerpoint", "power point": "powerpoint", "paurpoint": "powerpoint",
    "autluk": "outlook", "aut luk": "outlook", "autlook": "outlook", "out luk": "outlook",
    "crom": "chrome", "cromo": "chrome", "kroum": "chrome", "fairfox": "firefox", "faierfox": "firefox",
    "tims": "teams", "timis": "teams", "zum": "zoom", "sum": "zoom", "diskor": "discord", "discor": "discord",
}


def corregir_app(nombre):
    """La app conocida que SUENA como lo que oyó Vosk ('crom' -> 'chrome', 'discor' -> 'discord'), o None."""
    n = normalizar(nombre)
    if n in APPS_CONOCIDAS:
        return n
    if n in ALIAS_APPS:
        return ALIAS_APPS[n]
    if n.replace(" ", "") in ALIAS_APPS:
        return ALIAS_APPS[n.replace(" ", "")]
    fn = fonetica(n)
    mejor, mejor_s = None, 0.0
    for a in APPS_CONOCIDAS:
        s = max(_ratio(fn, fonetica(a), 0.6), _ratio(n, a, 0.6))
        if s > mejor_s:
            mejor, mejor_s = a, s
    return mejor if mejor_s >= 0.78 else None


# ══════════════════════════════════════════════════════════════════════════════
#  3.0 · CONTROL TOTAL DEL PC POR VOZ — lógica pura (sin Windows: se puede probar aparte)
# ══════════════════════════════════════════════════════════════════════════════
ARCHIVO_ALARMAS = os.path.join(BASE_DIR, "alfred_alarmas.json")
CARPETA_CAPTURAS = os.path.join(os.path.expanduser("~"), "Pictures", "Alfred_capturas")

_CENT = {"cien": 100, "ciento": 100, "doscientos": 200, "trescientos": 300, "cuatrocientos": 400,
         "quinientos": 500, "seiscientos": 600, "setecientos": 700, "ochocientos": 800, "novecientos": 900}
_UNID_EXTRA = {"un": 1, "una": 1, "veintiun": 21, "veintiuna": 21}


def numero_en(tokens, i=0):
    """Número (cifras o palabras, hasta millones) que empieza en tokens[i]: (valor, índice siguiente) o None.
    'veinticinco' -> 25, 'ciento treinta y cinco' -> 135, 'dos mil veinte' -> 2020, '45' -> 45."""
    n = len(tokens)
    if i >= n:
        return None
    if tokens[i].isdigit():
        return int(tokens[i]), i + 1
    total, actual, j, cat = 0, 0, i, None          # cat: c = centenas, d = decenas, u = unidades, m = tras «mil»
    while j < n:
        t = tokens[j]
        if t in _CENT and cat in (None, "m"):
            actual += _CENT[t]
            cat = "c"
        elif t in _DEC and cat in (None, "m", "c"):
            actual += _DEC[t]
            cat = "d"
            if j + 2 < n and tokens[j + 1] == "y":
                u = _UNID.get(tokens[j + 2], _UNID_EXTRA.get(tokens[j + 2], 99))
                if 0 < u < 10:
                    actual += u
                    j += 2
                    cat = "u"
        elif (t in _UNID or t in _UNID_EXTRA) and cat in (None, "m", "c"):
            actual += _UNID.get(t, _UNID_EXTRA.get(t))
            cat = "u"
        elif t == "mil" and (cat is not None or j == i):
            total += (actual or 1) * 1000
            actual, cat = 0, "m"
        elif t in ("millon", "millones") and cat is not None:
            total += (actual or 1) * 1000000
            actual, cat = 0, "m"
        else:
            break
        j += 1
    if cat is None:
        return None
    return total + actual, j


# ── duraciones y horas ───────────────────────────────────────────────────────
_UNI_T = {"hora": 3600, "horas": 3600, "h": 3600, "hr": 3600, "hrs": 3600,
          "minuto": 60, "minutos": 60, "min": 60, "mins": 60,
          "segundo": 1, "segundos": 1, "seg": 1, "segs": 1}


def duracion_en(norm):
    """(segundos, índice del token donde termina la duración) de «cinco minutos», «una hora y media», «media hora»,
    «tres cuartos de hora», «90 segundos»…; None si no hay ninguna."""
    t = norm.split()
    n, total, ok, i, fin = len(t), 0.0, False, 0, 0
    while i < n:
        if t[i] in ("media", "medio") and i + 1 < n and t[i + 1] in _UNI_T:
            total += 0.5 * _UNI_T[t[i + 1]]
            ok, i, fin = True, i + 2, i + 2
            continue
        if t[i] == "cuarto" and i + 2 < n and t[i + 1] == "de" and t[i + 2] in _UNI_T:
            total += 0.25 * _UNI_T[t[i + 2]]
            ok, i, fin = True, i + 3, i + 3
            continue
        if t[i] in ("hora", "minuto") and i + 2 < n and t[i + 1] == "y" and t[i + 2] in ("media", "medio"):
            total += 1.5 * _UNI_T[t[i]]
            ok, i, fin = True, i + 3, i + 3
            continue
        r = numero_en(t, i)
        if r:
            v, j = r
            if j + 2 < n and t[j] in ("cuarto", "cuartos") and t[j + 1] == "de" and t[j + 2] in _UNI_T:
                total += v * 0.25 * _UNI_T[t[j + 2]]
                ok, i, fin = True, j + 3, j + 3
                continue
            if j < n and t[j] in _UNI_T:
                u = _UNI_T[t[j]]
                total += v * u
                j += 1
                if j + 1 < n and t[j] == "y" and t[j + 1] in ("media", "medio"):
                    total += u * 0.5
                    j += 2
                elif j + 1 < n and t[j] == "y" and t[j + 1] == "cuarto":
                    total += u * 0.25
                    j += 2
                ok, i, fin = True, j, j
                continue
        i += 1
    return (total, fin) if ok and total > 0 else None


def parse_duracion(norm):
    r = duracion_en(norm)
    return r[0] if r else None


def texto_duracion(seg):
    """90 -> '1 minuto y 30 segundos'; 3600 -> '1 hora'; 45 -> '45 segundos'."""
    seg = int(round(seg))
    h, resto = divmod(seg, 3600)
    m, s = divmod(resto, 60)
    partes = []
    if h:
        partes.append(f"{h} hora" + ("s" if h != 1 else ""))
    if m:
        partes.append(f"{m} minuto" + ("s" if m != 1 else ""))
    if s or not partes:
        partes.append(f"{s} segundo" + ("s" if s != 1 else ""))
    return " y ".join(partes) if len(partes) <= 2 else ", ".join(partes[:-1]) + " y " + partes[-1]


def hora_reloj_en(norm, ahora):
    """(datetime, índice final) de «a las siete y media de la tarde», «a las 7 30», «a la una»…: la próxima vez que el
    reloj marque esa hora. None si no hay hora."""
    t = norm.split()
    n = len(t)
    for k, tok in enumerate(t):
        if tok not in ("las", "la") or k + 1 >= n:
            continue
        r = numero_en(t, k + 1)
        if not r or not (0 <= r[0] <= 24):
            continue
        h, j = r
        minutos = 0
        if j < n and t[j] == "y" and j + 1 < n and t[j + 1] in ("media", "cuarto"):
            minutos, j = (30 if t[j + 1] == "media" else 15), j + 2
        elif j < n and t[j] == "y":
            m2 = numero_en(t, j + 1)
            if m2 and 0 <= m2[0] < 60:
                minutos, j = m2
        elif j < n and t[j] == "menos":
            m2 = numero_en(t, j + 1)
            if m2 and 0 < m2[0] < 60:
                minutos, j, h = 60 - m2[0], m2[1], h - 1
            elif j + 1 < n and t[j + 1] == "cuarto":
                minutos, j, h = 45, j + 2, h - 1
        elif j < n and t[j] == "con":
            m2 = numero_en(t, j + 1)
            if m2 and 0 <= m2[0] < 60:
                minutos, j = m2
        else:
            m2 = numero_en(t, j)
            if m2 and 0 <= m2[0] < 60 and (j >= n or t[j] not in _UNI_T) and (m2[1] >= n or t[m2[1]] not in _UNI_T):
                minutos, j = m2
        resto = t[j:j + 4]
        pm = "tarde" in resto or "noche" in resto
        am = "manana" in resto or "madrugada" in resto
        if pm and 1 <= h < 12:
            h += 12
        elif pm and h == 12 and "noche" in resto:
            h = 0
        h %= 24
        manana = any(x == "manana" and (i == 0 or t[i - 1] != "la") for i, x in enumerate(t[:k]))
        base = ahora.replace(hour=h, minute=minutos, second=0, microsecond=0)
        if manana:
            base += datetime.timedelta(days=1)
            return base, j
        opciones = [base]
        if not pm and not am and h < 12:
            opciones.append(base + datetime.timedelta(hours=12))
        opciones.append(base + datetime.timedelta(days=1))
        return next(o for o in opciones if o > ahora), j
    return None


# ── calculadora por voz ──────────────────────────────────────────────────────
def _digitos_decimales(t, j):
    """Parte decimal dicha tras «punto»/«coma» ('cero cinco' -> '05', 'veinticinco' -> '25'); (texto, índice) o None."""
    ds, k = "", j
    while k < len(t) and (t[k].isdigit() and len(t[k]) == 1 or _UNID.get(t[k], 99) < 10):
        ds += t[k] if t[k].isdigit() else str(_UNID[t[k]])
        k += 1
    if ds:
        return ds, k
    r = numero_en(t, j)
    return (str(r[0]), r[1]) if r else None


def expresion_de_voz(norm):
    """'veinte por cinco mas tres' -> '20*5+3'; None si no parece una cuenta."""
    t = norm.split()
    n, i, out = len(t), 0, []
    while i < n:
        w = t[i]
        if w == "raiz":
            k = i + 1
            while k < n and t[k] in ("cuadrada", "de"):
                k += 1
            r = numero_en(t, k)
            if r:
                out.append(f"({r[0]})**0.5")
                i = r[1]
                continue
        r = numero_en(t, i)
        if r:
            v, j = r
            txt = str(v)
            if j < n and t[j] in ("punto", "coma"):
                d = _digitos_decimales(t, j + 1)
                if d:
                    txt, j = f"{v}.{d[0]}", d[1]
            out.append(txt)
            i = j
            continue
        if w == "mas":
            out.append("+")
        elif w == "menos":
            out.append("-")
        elif w in ("x", "veces"):
            out.append("*")
        elif w in ("multiplicado", "multiplicar"):
            out.append("*")
            if i + 1 < n and t[i + 1] == "por":
                i += 1
        elif w == "por":
            if i + 1 < n and t[i + 1] == "ciento":
                out.append("*0.01*" if i + 2 < n and t[i + 2] == "de" else "*0.01")
                i += 1
            elif i + 1 < n and t[i + 1] == "favor":
                i += 1
            elif out:
                out.append("*")
        elif w in ("entre", "sobre"):
            out.append("/")
        elif w == "dividido":
            out.append("/")
            if i + 1 < n and t[i + 1] in ("entre", "por"):
                i += 1
        elif w == "elevado":
            out.append("**")
            while i + 1 < n and t[i + 1] in ("a", "la", "potencia"):
                i += 1
        elif w == "al" and i + 1 < n and t[i + 1] in ("cuadrado", "cubo"):
            out.append("**2" if t[i + 1] == "cuadrado" else "**3")
            i += 1
        i += 1                                    # lo demás («cuánto es», «de», «el»…) es relleno
    expr = "".join(out)
    if not re.search(r"\d", expr) or not re.search(r"[+\-*/]", expr):
        return None
    return expr


def evaluar_expresion(expr):
    """Evalúa una cuenta SIN eval(): solo números y + - * / **."""
    import ast
    import operator
    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
           ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}

    def ev(nodo):
        if isinstance(nodo, ast.Expression):
            return ev(nodo.body)
        if isinstance(nodo, ast.Constant) and isinstance(nodo.value, (int, float)) and not isinstance(nodo.value, bool):
            return nodo.value
        if isinstance(nodo, ast.UnaryOp) and type(nodo.op) in ops:
            return ops[type(nodo.op)](ev(nodo.operand))
        if isinstance(nodo, ast.BinOp) and type(nodo.op) in ops:
            a, b = ev(nodo.left), ev(nodo.right)
            if isinstance(nodo.op, ast.Pow) and (abs(b) > 12 or abs(a) > 1e9):
                raise ValueError("potencia demasiado grande")
            return ops[type(nodo.op)](a, b)
        raise ValueError("expresión no permitida")
    return ev(ast.parse(expr, mode="eval"))


def formatear_numero(x):
    """25.0 -> '25'; 3.5 -> '3,5' (así lo lee bien la voz en español)."""
    if isinstance(x, float) and x.is_integer():
        x = int(x)
    if isinstance(x, int):
        return str(x)
    return f"{x:.4f}".rstrip("0").rstrip(".").replace(".", ",")


# ── dictado: signos de puntuación hablados ───────────────────────────────────
# (palabras normalizadas, texto, espacio antes, espacio después, mayúscula en lo siguiente)
_DICT_SIGNOS = [
    (("punto", "y", "coma"), ";", False, True, False), (("dos", "puntos"), ":", False, True, False),
    (("puntos", "suspensivos"), "...", False, True, False), (("punto", "y", "aparte"), ".\n", False, False, True),
    (("signo", "de", "interrogacion"), "?", False, True, True), (("abre", "interrogacion"), "¿", True, False, False),
    (("cierra", "interrogacion"), "?", False, True, True), (("abre", "exclamacion"), "¡", True, False, False),
    (("cierra", "exclamacion"), "!", False, True, True), (("abre", "parentesis"), "(", True, False, False),
    (("cierra", "parentesis"), ")", False, True, False), (("abre", "comillas"), "\"", True, False, False),
    (("cierra", "comillas"), "\"", False, True, False), (("nuevo", "parrafo"), "\n\n", False, False, True),
    (("nueva", "linea"), "\n", False, False, True), (("salto", "de", "linea"), "\n", False, False, True),
    (("coma",), ",", False, True, False), (("punto",), ".", False, True, True), (("arroba",), "@", False, False, False),
    (("tabulador",), "\t", False, False, False),
    # inglés
    (("question", "mark"), "?", False, True, True), (("exclamation", "mark"), "!", False, True, True),
    (("exclamation", "point"), "!", False, True, True), (("full", "stop"), ".", False, True, True),
    (("new", "line"), "\n", False, False, True), (("new", "paragraph"), "\n\n", False, False, True),
    (("semicolon",), ";", False, True, False), (("colon",), ":", False, True, False),
    (("comma",), ",", False, True, False), (("period",), ".", False, True, True),
]
_DICT_ORDEN = sorted(_DICT_SIGNOS, key=lambda s: -len(s[0]))


def texto_dictado(raw, mayus_inicial=True):
    """Lo dicho -> texto con puntuación: 'hola coma como estas signo de interrogacion' -> 'Hola, como estas?'."""
    toks = raw.split()
    nt = [normalizar(x) for x in toks]
    out, cap, esp, i = "", mayus_inicial, False, 0
    while i < len(toks):
        for frase, txt, antes, despues, mayus in _DICT_ORDEN:
            k = len(frase)
            if tuple(nt[i:i + k]) == frase:
                if antes and out and esp:
                    out += " "
                out += txt
                esp = despues
                if mayus:
                    cap = True
                i += k
                break
        else:
            pal = toks[i]
            if cap:
                pal, cap = pal[:1].upper() + pal[1:], False
            if out and esp:
                out += " "
            out += pal
            esp = True
            i += 1
    return out


# ── atajos de teclado hablados (coincide toda la orden) ──────────────────────
# (frases, secuencia de combinaciones, sonido breve en vez de voz)
ATAJOS = [
    (("copia", "copiar", "copia esto", "copia eso", "copia la seleccion", "copia el texto"), (("ctrl", "c"),)),
    (("pega", "pegar", "pega esto", "pega aqui", "pega el texto"), (("ctrl", "v"),)),
    (("corta", "cortar", "corta esto", "corta eso", "corta la seleccion"), (("ctrl", "x"),)),
    (("selecciona todo", "seleccionar todo", "selecciona todo el texto", "marca todo"), (("ctrl", "a"),)),
    (("deshaz", "deshacer", "deshaz eso", "deshaz lo ultimo", "anula eso"), (("ctrl", "z"),)),
    (("rehaz", "rehacer", "rehaz eso"), (("ctrl", "y"),)),
    (("guarda", "guardar", "guarda esto", "guarda el archivo", "guarda el documento", "guarda los cambios"),
     (("ctrl", "s"),)),
    (("imprime", "imprimir", "imprime esto", "imprime el documento"), (("ctrl", "p"),)),
    (("busca en la pagina", "buscar en la pagina", "busca en el documento", "busca aqui"), (("ctrl", "f"),)),
    (("nueva pestana", "pestana nueva", "abre una pestana", "abre una pestana nueva", "abre una nueva pestana"),
     (("ctrl", "t"),)),
    (("cierra la pestana", "cierra pestana", "cerrar pestana", "cierra esta pestana", "cerrar la pestana"),
     (("ctrl", "w"),)),
    (("siguiente pestana", "pestana siguiente", "ve a la siguiente pestana", "cambia de pestana", "otra pestana"),
     (("ctrl", "tab"),)),
    (("pestana anterior", "anterior pestana", "ve a la pestana anterior", "regresa a la pestana anterior"),
     (("ctrl", "shift", "tab"),)),
    (("reabre la pestana", "reabre pestana", "reabrir pestana", "recupera la pestana", "abre la pestana cerrada"),
     (("ctrl", "shift", "t"),)),
    (("nueva ventana", "abre una ventana nueva", "abre una nueva ventana"), (("ctrl", "n"),)),
    (("ventana privada", "modo incognito", "abre incognito", "abre una ventana privada", "ventana de incognito"),
     (("ctrl", "shift", "n"),)),
    (("recarga", "refresca", "recarga la pagina", "actualiza la pagina", "refresca la pagina", "recargar pagina"),
     (("f5",),)),
    (("ve atras", "pagina anterior", "ir atras", "atras en el navegador"), (("alt", "left"),)),
    (("ve adelante", "pagina siguiente", "ir adelante", "adelante en el navegador"), (("alt", "right"),)),
    (("pantalla completa", "activa pantalla completa", "activa la pantalla completa", "sal de pantalla completa",
      "quita la pantalla completa", "quita pantalla completa"), (("f11",),)),
    (("acerca", "zoom", "mas zoom", "acerca la pagina", "aumenta el zoom", "amplia la pagina"), (("ctrl", "="),)),
    (("aleja", "menos zoom", "aleja la pagina", "reduce el zoom", "reduce la pagina"), (("ctrl", "-"),)),
    (("zoom normal", "restablece el zoom", "tamano normal"), (("ctrl", "0"),)),
    (("enter", "intro", "pulsa enter", "presiona enter", "da enter", "oprime enter", "aprieta enter"), (("enter",),)),
    (("escape", "pulsa escape", "presiona escape", "oprime escape"), (("esc",),)),
    (("tabulador", "pulsa tabulador", "presiona tab", "pulsa tab"), (("tab",),)),
    (("espacio", "barra espaciadora", "pulsa espacio"), (("space",),)),
    (("borra", "borrar", "borra eso", "borra lo seleccionado", "suprime", "suprimir"), (("delete",),)),
    (("retroceso", "borra una letra", "borra la ultima letra"), (("backspace",),)),
    (("borra la ultima palabra", "borra una palabra", "borra la palabra"), (("ctrl", "backspace"),)),
    (("borra todo", "borra todo el texto", "borrar todo"), (("ctrl", "a"), ("delete",))),
    (("flecha arriba",), (("up",),)), (("flecha abajo",), (("down",),)),
    (("flecha izquierda",), (("left",),)), (("flecha derecha",), (("right",),)),
    (("pagina abajo", "avanza pagina"), (("pagedown",),)), (("pagina arriba", "retrocede pagina"), (("pageup",),)),
    (("ve al inicio", "ve al inicio de la pagina", "inicio de la pagina", "ve arriba del todo"), (("ctrl", "home"),)),
    (("ve al final", "ve al final de la pagina", "final de la pagina", "ve abajo del todo"), (("ctrl", "end"),)),
    (("renombra", "renombrar", "cambia el nombre"), (("f2",),)),
    (("menu inicio", "abre el menu inicio", "abre inicio"), (("win",),)),
    (("busca en windows", "abre la busqueda", "abre el buscador"), (("win", "s"),)),
    (("centro de notificaciones", "abre las notificaciones", "abre notificaciones"), (("win", "n"),)),
    (("configuracion rapida", "panel rapido", "abre el panel rapido"), (("win", "a"),)),
    (("historial del portapapeles", "abre el portapapeles de windows"), (("win", "v"),)),
    (("abre los emojis", "emojis", "abre emojis"), (("win", "."),)),
    (("abre ejecutar", "ejecutar"), (("win", "r"),)),
    (("herramienta de recorte", "recorte de pantalla", "recorta la pantalla", "abre el recorte"),
     (("win", "shift", "s"),)),
    (("graba la pantalla", "empieza a grabar", "deja de grabar", "detener grabacion", "inicia la grabacion"),
     (("win", "alt", "r"),)),
]
_ATAJO_POR_FRASE = {f: seq for frases, seq in ATAJOS for f in frases}

# ── ventanas (coincide toda la orden): acción por frase ──────────────────────
VENTANA_ACCIONES = {
    "minimizar": ("minimiza esta ventana", "minimiza la ventana actual", "minimiza la ventana activa",
                  "minimizar esta ventana"),
    "maximizar": ("maximiza esta ventana", "maximiza la ventana actual", "maximiza la ventana activa",
                  "maximizar esta ventana"),
    "restaurar": ("restaura esta ventana", "restaura la ventana actual", "normaliza esta ventana"),
    "izquierda": ("ventana a la izquierda", "pon la ventana a la izquierda", "acomoda la ventana a la izquierda",
                  "ajusta la ventana a la izquierda", "ventana izquierda"),
    "derecha": ("ventana a la derecha", "pon la ventana a la derecha", "acomoda la ventana a la derecha",
                "ajusta la ventana a la derecha", "ventana derecha"),
    "otro_monitor": ("ventana al otro monitor", "mueve la ventana al otro monitor", "manda la ventana al otro monitor"),
    "alternar": ("cambia de ventana", "cambia de aplicacion", "siguiente ventana", "ventana siguiente",
                 "alterna ventanas", "otra ventana"),
    "vista": ("vista de tareas", "muestra las ventanas", "muestra todas las ventanas", "vista general de ventanas"),
    "escritorio_nuevo": ("escritorio nuevo", "nuevo escritorio", "crea un escritorio", "crea un escritorio nuevo"),
    "escritorio_sig": ("siguiente escritorio", "escritorio siguiente", "ve al siguiente escritorio",
                       "cambia de escritorio"),
    "escritorio_ant": ("escritorio anterior", "ve al escritorio anterior"),
    "escritorio_cerrar": ("cierra el escritorio", "cierra este escritorio"),
    "listar": ("que ventanas tengo abiertas", "que aplicaciones tengo abiertas", "que tengo abierto",
               "lista las ventanas", "dime que ventanas hay abiertas", "que programas tengo abiertos"),
}
_VENTANA_POR_FRASE = {f: a for a, frases in VENTANA_ACCIONES.items() for f in frases}

# ── ajustes de Windows por nombre ────────────────────────────────────────────
AJUSTES_WIN = [   # (palabras clave, página ms-settings:, nombre para decir)
    (("wifi", "wi", "fi", "internet", "red"), "ms-settings:network-wifi", "Wi-Fi"),
    (("bluetooth",), "ms-settings:bluetooth", "Bluetooth"),
    (("avion",), "ms-settings:network-airplanemode", "modo avión"),
    (("sonido", "audio", "volumen"), "ms-settings:sound", "sonido"),
    (("pantalla", "monitor", "resolucion"), "ms-settings:display", "pantalla"),
    (("nocturna", "noche"), "ms-settings:nightlight", "luz nocturna"),
    (("bateria", "energia"), "ms-settings:batterysaver", "batería"),
    (("actualizaciones", "actualizacion", "update"), "ms-settings:windowsupdate", "Windows Update"),
    (("aplicaciones", "programas"), "ms-settings:appsfeatures", "aplicaciones"),
    (("privacidad", "microfono", "camara"), "ms-settings:privacy-microphone", "privacidad"),
    (("fondo", "personalizacion", "tema", "temas"), "ms-settings:personalization", "personalización"),
    (("notificaciones",), "ms-settings:notifications", "notificaciones"),
    (("impresoras", "impresora"), "ms-settings:printers", "impresoras"),
    (("almacenamiento", "disco"), "ms-settings:storagesense", "almacenamiento"),
    (("teclado", "idioma"), "ms-settings:regionlanguage", "idioma y teclado"),
    (("mouse", "raton"), "ms-settings:mousetouchpad", "ratón"),
    (("accesibilidad",), "ms-settings:easeofaccess", "accesibilidad"),
    (("voz", "reconocimiento"), "ms-settings:speech", "voz"),
]

HERRAMIENTAS_WIN = [   # (frases, comando, nombre) — «abre el administrador de tareas»…
    (("administrador de tareas", "task manager", "monitor de tareas", "taskmgr"), ["taskmgr.exe"],
     "el administrador de tareas"),
    (("simbolo del sistema", "consola de comandos", "linea de comandos", "cmd"), ["cmd.exe"], "el símbolo del sistema"),
    (("powershell", "power shell"), ["powershell.exe"], "PowerShell"),
    (("panel de control",), ["control.exe"], "el panel de control"),
    (("administrador de dispositivos",), ["mmc.exe", "devmgmt.msc"], "el administrador de dispositivos"),
    (("informacion del sistema",), ["msinfo32.exe"], "la información del sistema"),
    (("visor de eventos",), ["mmc.exe", "eventvwr.msc"], "el visor de eventos"),
    (("administracion de discos", "administrador de discos"), ["mmc.exe", "diskmgmt.msc"], "la administración de discos"),
    (("papelera", "papelera de reciclaje"), ["explorer.exe", "shell:RecycleBinFolder"], "la papelera"),
    (("monitor de recursos",), ["resmon.exe"], "el monitor de recursos"),
]

# nombres que se dicen -> parte del nombre del programa (para cerrar / cambiar de ventana)
ALIAS_EXE = {"word": "winword", "powerpoint": "powerpnt", "power point": "powerpnt", "calculadora": "calculatorapp",
             "bloc de notas": "notepad", "notas": "notepad", "explorador": "explorer", "archivos": "explorer",
             "explorador de archivos": "explorer", "visual studio code": "code", "vs code": "code",
             "terminal": "windowsterminal", "paint": "mspaint", "edge": "msedge", "navegador": "",
             "teams": "teams", "opera gx": "opera", "google chrome": "chrome", "administrador de tareas": "taskmgr"}
PROTEGIDOS = {"explorer.exe", "python.exe", "pythonw.exe", "winlogon.exe", "csrss.exe", "svchost.exe", "dwm.exe",
              "services.exe", "lsass.exe", "system", "wininit.exe", "smss.exe", "taskhostw.exe", "sihost.exe"}
RELLENO_ACCION = {"el", "la", "los", "las", "mi", "mis", "un", "una", "aplicacion", "programa", "app", "ventana", "de",
                  "por", "favor", "porfa", "a", "al", "del", "en", "y", "pagina", "web", "navegador"}
CORTESIA_INI = {"por", "favor", "porfa", "oye", "ahora", "puedes", "podrias", "podria", "quiero", "entonces",
                "ya", "pues", "mira", "a", "ver", "me", "y", "deseo", "quisiera", "necesito"}
CORTESIA_FIN = {"por", "favor", "porfa", "gracias", "ahora", "ya"}


def nucleo_orden(norm):
    """La orden sin cortesías: 'por favor copia esto por favor' -> 'copia esto'."""
    t = norm.split()
    while t and t[0] in CORTESIA_INI:
        t.pop(0)
    while t and t[-1] in CORTESIA_FIN:
        t.pop()
    return " ".join(t)


def sin_relleno(norm, quitar=()):
    """Palabras 'de verdad' de una orden (sin artículos ni cortesías) para buscar un nombre: 'cierra la app de chrome'."""
    t = [w for w in norm.split() if w not in RELLENO_ACCION and w not in quitar]
    return " ".join(t)


ALIAS_EXE.update({sin_relleno(k): v for k, v in list(ALIAS_EXE.items())})   # «bloc de notas» se busca como «bloc notas»


def puntuar_ventana(clave, v):
    """Parecido (0-1) entre lo que se dijo («chrome», «youtube», «word») y una ventana {titulo, exe}."""
    k = normalizar(clave)
    if not k:
        return 0.0
    exe = normalizar(os.path.splitext(v["exe"])[0])
    tit = normalizar(v["titulo"])
    k2 = ALIAS_EXE.get(k, k)
    if not k2:
        return 0.0
    if k2 == exe:
        return 1.0
    if len(k2) >= 3 and (k2 in exe or (len(exe) >= 4 and exe in k2)):
        return 0.93
    if f" {k} " in f" {tit} ":
        return 0.9
    return _ratio(fonetica(k2), fonetica(exe), 0.6) * 0.95


def mejores_ventanas(clave, ventanas, minimo=0.8):
    """Ventanas que encajan con lo dicho, la mejor primero."""
    pts = [(puntuar_ventana(clave, v), v) for v in ventanas]
    pts = [p for p in pts if p[0] >= minimo]
    pts.sort(key=lambda p: -p[0])
    return [v for _, v in pts]


def parse_movimiento(norm):
    """'mueve el mouse un poco a la derecha' -> (dx, dy) en píxeles; None si no hay dirección."""
    t = set(norm.split())
    paso = 90
    if t & {"poco", "poquito", "ligeramente", "tantito"}:
        paso = 25
    elif t & {"mucho", "bastante", "lejos"}:
        paso = 350
    num = None
    toks = norm.split()
    for i in range(len(toks)):
        r = numero_en(toks, i) if toks[i] not in ("un", "una") else None
        if r and r[0] > 0:
            num = r[0]
            break
    if num:
        paso = min(num, 2000)
    dx = dy = 0
    if t & {"derecha"}:
        dx = paso
    elif t & {"izquierda"}:
        dx = -paso
    if t & {"arriba"}:
        dy = -paso
    elif t & {"abajo"}:
        dy = paso
    return (dx, dy) if (dx or dy) else None


def parse_desplazamiento(norm):
    """'baja la pagina un poco' -> -3 (muescas de la rueda; negativo = abajo). None si no hay dirección."""
    t = set(norm.split())
    n = 5
    if t & {"poco", "poquito", "tantito"}:
        n = 2
    elif t & {"mucho", "bastante"}:
        n = 15
    toks = norm.split()
    for i in range(len(toks)):
        r = numero_en(toks, i) if toks[i] not in ("un", "una") else None
        if r and 0 < r[0] <= 50:
            n = r[0]
            break
    if t & {"baja", "abajo", "bajar", "desciende"}:
        return -n
    if t & {"sube", "arriba", "subir", "asciende"}:
        return n
    return None


def numero_cuadricula(norm):
    """Celda 1-9 dicha en el modo cuadrícula ('cinco', 'five', '5'); None si no es un número del 1 al 9."""
    t = norm.split()
    en = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}
    if len(t) == 1:
        if t[0] in en:
            return en[t[0]]
        r = numero_en(t, 0)
        if r and 1 <= r[0] <= 9 and r[1] == 1:
            return r[0]
    return None


def celda_cuadricula(rect, n):
    """Rectángulo (x0, y0, x1, y1) de la celda n (1-9, como un teclado numérico invertido: 1 arriba-izquierda)."""
    x0, y0, x1, y1 = rect
    f, c = divmod(n - 1, 3)
    w, h = (x1 - x0) / 3.0, (y1 - y0) / 3.0
    return (int(x0 + c * w), int(y0 + f * h), int(x0 + (c + 1) * w), int(y0 + (f + 1) * h))


def ping_internet(host="1.1.1.1", puerto=53, espera=2.0):
    try:
        with socket.create_connection((host, puerto), timeout=espera):
            return True
    except OSError:
        return False


def ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.0)
        s.connect(("8.8.8.8", 80))                  # no envía nada: solo elige la interfaz de salida
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return None


def texto_uptime(seg):
    d, resto = divmod(int(seg), 86400)
    h, resto = divmod(resto, 3600)
    m = resto // 60
    partes = []
    if d:
        partes.append(f"{d} día" + ("s" if d != 1 else ""))
    if h:
        partes.append(f"{h} hora" + ("s" if h != 1 else ""))
    if m or not partes:
        partes.append(f"{m} minuto" + ("s" if m != 1 else ""))
    return " y ".join(partes) if len(partes) <= 2 else ", ".join(partes[:-1]) + " y " + partes[-1]


# Comandos integrados. El ORDEN importa (gana el primero que coincide). La ayuda se genera desde aquí.
COMANDOS = [
    # ── 3.0 · control del PC: «ventana» va PRIMERO (para ganar a «maximiza», «restaura»… de la ventana de Alfred) ──
    {"id": "ventana", "modo": "exacto", "seccion": "VENTANAS Y TECLADO",
     "frases": [f for fr in VENTANA_ACCIONES.values() for f in fr],
     "ejemplo": "Alfred maximiza esta ventana / ventana a la izquierda / cambia de ventana / qué ventanas tengo abiertas",
     "desc": "Minimiza, maximiza, acomoda o cambia de ventana y de escritorio virtual"},
    {"id": "mostrar", "frases": ["muestrate", "muestra te", "aparece", "sal del segundo plano", "sal de segundo plano",
                                 "abre tu ventana", "ventana principal", "sal a la pantalla",
                                 "desminimizate", "desminimiza te", "desminimiza", "des minimizate", "des minimiza te",
                                 "maximizate", "maximiza te", "maximiza", "restaurate", "restaura te", "restaura la ventana",
                                 "muestra la ventana", "muestra tu ventana", "muestra el panel", "sal de la bandeja",
                                 "sal de la barra", "vuelve a la pantalla", "regresa a la pantalla", "vuelve a aparecer",
                                 "levantate", "despierta"],
     "ejemplo": "Alfred muéstrate / desminimízate", "desc": "Saca la ventana del segundo plano y la trae al frente"},
    {"id": "segundo_plano", "frases": ["segundo plano", "minimizate", "minimiza te", "ocultate", "oculta te", "escondete",
                                       "esconde te", "a la bandeja", "oculta la ventana"],
     "ejemplo": "Alfred pasa a segundo plano", "desc": "Oculta la ventana (sigue escuchando desde la bandeja)"},
    {"id": "cancion", "frases": [],      # se detecta con pedido_cancion(), no por frases fijas (esto es solo la ayuda)
     "ejemplo": "Alfred pon Numb / reproduce canciones de Linkin Park / pon Numb en Spotify",
     "desc": "Reproduce una canción o a un artista de tu biblioteca (por nombre, artista o etiquetas) o en Spotify / YouTube Music"},
    {"id": "recordar", "frases": ["recuerdame", "recuerda", "anota", "anotame", "apunta", "apuntame"],
     "ejemplo": "Alfred recuérdame llamar al banco", "desc": "Guarda una nota en tu agenda"},
    {"id": "trabajo", "frases": ["vamos a trabajar", "hora de trabajar", "vamos a chambear", "hora de chambear",
                                 "trabajar", "chamba", "chambear"],
     "ejemplo": "Alfred vamos a trabajar", "desc": "Abre Explorer, tu reproductor de música, Cursor y YouTube"},
    {"id": "buenos_dias", "frases": ["buenos dias", "buen dia", "buenas tardes", "buenas noches"],
     "ejemplo": "Alfred buenos días", "desc": "Saludo, clima, noticias y recordatorios de hoy"},
    {"id": "agenda", "frases": ["agenda", "recordatorios", "pendientes", "que tengo hoy"],
     "ejemplo": "Alfred enséñame la agenda / lee mi agenda", "desc": "Muestra o lee tus recordatorios"},
    # ── 3.0 · CONTROL DEL PC POR VOZ ─────────────────────────────────────────────────────────────────────────
    {"id": "bloquear", "seccion": "ENERGÍA Y SESIÓN",
     "frases": ["bloquea la pantalla", "bloquea el equipo", "bloquea la computadora", "bloquea el pc", "bloquea la compu",
                "bloquea la sesion", "bloquear la pantalla", "bloquear el equipo", "bloquear la computadora",
                "bloquear pantalla", "bloquear equipo", "bloquea windows", "bloquea"],
     "ejemplo": "Alfred bloquea la pantalla", "desc": "Bloquea el equipo (pide tu contraseña al volver)"},
    {"id": "suspender", "seccion": "ENERGÍA Y SESIÓN",
     "frases": ["suspende", "suspender", "suspende el equipo", "suspende la computadora", "suspende el pc",
                "modo suspension", "duerme la computadora", "duerme el equipo", "duerme el pc",
                "pon la computadora a dormir", "pon el equipo a dormir", "pon el pc a dormir"],
     "ejemplo": "Alfred suspende el equipo", "desc": "Pone el equipo a dormir"},
    {"id": "hibernar", "seccion": "ENERGÍA Y SESIÓN",
     "frases": ["hiberna", "hibernar", "hiberna el equipo", "hiberna la computadora", "hiberna el pc"],
     "ejemplo": "Alfred hiberna el equipo", "desc": "Hiberna (guarda todo y apaga)"},
    {"id": "apagar_pc", "seccion": "ENERGÍA Y SESIÓN",
     "frases": ["apaga la computadora", "apaga el equipo", "apaga el pc", "apaga la compu", "apaga el ordenador",
                "apagar la computadora", "apagar el equipo", "apagar el pc", "apagar la compu", "apagar computadora",
                "apagar equipo"],
     "ejemplo": "Alfred apaga la computadora / apaga la computadora en 30 minutos",
     "desc": "Apaga el PC (pide un «sí»; da 20 s para cancelar). También programado"},
    {"id": "reiniciar_pc", "seccion": "ENERGÍA Y SESIÓN",
     "frases": ["reinicia la computadora", "reinicia el equipo", "reinicia el pc", "reinicia la compu",
                "reiniciar la computadora", "reiniciar el equipo", "reiniciar el pc", "reiniciar la compu",
                "reinicia windows", "reinicia el ordenador", "reiniciar computadora", "reiniciar equipo"],
     "ejemplo": "Alfred reinicia la computadora", "desc": "Reinicia el PC (pide un «sí»)"},
    {"id": "cerrar_sesion", "seccion": "ENERGÍA Y SESIÓN",
     "frases": ["cierra la sesion", "cierra sesion", "cerrar sesion", "cierra mi sesion", "cierra la sesion de windows"],
     "ejemplo": "Alfred cierra la sesión", "desc": "Cierra tu sesión de Windows (pide un «sí»)"},
    {"id": "cancelar_apagado", "seccion": "ENERGÍA Y SESIÓN",
     "frases": ["cancela el apagado", "cancelar el apagado", "cancela apagado", "cancela el reinicio", "cancelar reinicio",
                "no apagues", "no apagues la computadora", "aborta el apagado", "deten el apagado"],
     "ejemplo": "Alfred cancela el apagado", "desc": "Anula un apagado o reinicio en curso"},
    {"id": "pantalla", "seccion": "RATÓN Y PANTALLA",
     "frases": ["apaga la pantalla", "apaga el monitor", "apagar la pantalla", "apagar el monitor", "enciende la pantalla",
                "prende la pantalla", "enciende el monitor", "prende el monitor", "enciende pantalla", "activa la pantalla"],
     "ejemplo": "Alfred apaga la pantalla / enciende la pantalla",
     "desc": "Apaga el monitor sin suspender el PC (Alfred sigue escuchando)"},
    {"id": "temporizador", "modo": "inicio", "seccion": "TIEMPO Y CÁLCULO",
     "frases": ["pon un temporizador", "pon una alarma", "pon el temporizador", "ponme un temporizador", "ponme una alarma",
                "programa un temporizador", "programa una alarma", "crea un temporizador", "crea una alarma",
                "temporizador", "alarma", "timer", "avisame en", "avisame dentro de", "avisame a las", "despiertame a las",
                "despiertame en", "cuanto falta", "cuanto tiempo falta", "cancela el temporizador", "cancela la alarma",
                "cancela los temporizadores", "cancela las alarmas", "cancela todas las alarmas",
                "cancela todos los temporizadores", "que alarmas tengo", "que temporizadores tengo",
                "lista de alarmas", "lista de temporizadores"],
     "ejemplo": "Alfred temporizador de 10 minutos / avísame en 5 minutos de sacar la pizza / alarma a las 7 y media",
     "desc": "Temporizadores y alarmas por voz (suenan aunque reinicies Alfred)"},
    {"id": "calcular", "modo": "inicio", "seccion": "TIEMPO Y CÁLCULO",
     "frases": ["cuanto es", "cuanto son", "cuanto da", "calcula", "calcular", "cual es el resultado de",
                "dime cuanto es", "resultado de"],
     "ejemplo": "Alfred cuánto es veinticinco por cuatro / el veinte por ciento de cincuenta / raíz cuadrada de 81",
     "desc": "Resuelve cuentas dichas en voz alta"},
    {"id": "escribir", "modo": "inicio", "seccion": "DICTADO",
     "frases": ["escribe", "escribeme", "teclea", "escribir", "teclear"],
     "ejemplo": "Alfred escribe hola coma ¿cómo estás? / escribe nueva línea",
     "desc": "Escribe lo que dices en la ventana activa (acentos, ñ y signos hablados)"},
    {"id": "dictado", "seccion": "DICTADO",
     "frases": ["empieza a dictar", "comienza a dictar", "inicia el dictado", "inicia dictado", "modo dictado",
                "activa el dictado", "activa dictado", "vamos a dictar", "empieza el dictado", "comienza el dictado",
                "dictar", "dicta", "deja de dictar", "termina el dictado", "termina de dictar", "fin del dictado",
                "fin de dictado", "detener dictado", "deten el dictado", "desactiva el dictado", "sal del dictado",
                "finaliza el dictado", "para el dictado"],
     "ejemplo": "Alfred empieza a dictar … «fin del dictado»",
     "desc": "Modo dictado: todo lo que digas se escribe, sin repetir mi nombre, hasta «fin del dictado»"},
    {"id": "atajo", "modo": "exacto", "seccion": "VENTANAS Y TECLADO",
     "frases": [f for frases, _ in ATAJOS for f in frases],
     "ejemplo": "Alfred copia / pega / guarda / nueva pestaña / recarga / enter / borra todo / graba la pantalla",
     "desc": "Teclas y atajos: copiar, pegar, guardar, pestañas, zoom, flechas, Enter, Escape, Win+…"},
    {"id": "cerrar", "modo": "inicio", "seccion": "VENTANAS Y TECLADO",
     "frases": ["cierra la aplicacion", "cierra el programa", "cierra la app", "cierra la ventana de", "cierra la ventana",
                "cierra", "cerrar", "fuerza el cierre de", "fuerza el cierre", "mata el proceso de", "mata el proceso",
                "mata", "termina el proceso de", "finaliza el proceso de"],
     "ejemplo": "Alfred cierra la ventana / cierra Chrome / fuerza el cierre de Word",
     "desc": "Cierra la ventana activa o una aplicación por su nombre (con «fuerza» la mata, tras un «sí»)"},
    {"id": "cambiar_a", "modo": "inicio", "seccion": "VENTANAS Y TECLADO",
     "frases": ["cambia a la ventana de", "ve a la ventana de", "pasa a la ventana de", "muestrame la ventana de",
                "cambia a", "cambiate a", "pasa a", "ve a", "ir a", "enfoca", "trae al frente", "muestrame"],
     "ejemplo": "Alfred cambia a Chrome / ve a YouTube / enfoca Word",
     "desc": "Trae al frente una ventana abierta por el nombre del programa o de su título"},
    {"id": "raton", "modo": "inicio", "seccion": "RATÓN Y PANTALLA",
     "frases": ["clic", "click", "haz clic", "haz click", "da clic", "da click", "doble clic", "doble click",
                "haz doble clic", "haz doble click", "da doble clic", "clic derecho", "click derecho", "haz clic derecho",
                "da clic derecho", "clic izquierdo", "mueve el mouse", "mueve el raton", "mueve el cursor",
                "mueve el puntero", "baja la pagina", "sube la pagina", "desplaza", "desplazate", "scroll", "haz scroll",
                "centra el mouse", "centra el cursor", "centra el raton", "mouse al centro"],
     "ejemplo": "Alfred clic / doble clic / clic derecho / baja la página / mueve el mouse a la derecha",
     "desc": "Clics, desplazamiento y movimiento del ratón"},
    {"id": "cuadricula", "modo": "inicio", "seccion": "RATÓN Y PANTALLA",
     "frases": ["cuadricula", "muestra la cuadricula", "activa la cuadricula", "abre la cuadricula",
                "mouse por cuadricula", "raton por cuadricula", "control del mouse", "control del raton",
                "controla el mouse", "controla el raton", "controlar el mouse", "modo mouse", "modo raton"],
     "ejemplo": "Alfred cuadrícula … «cinco» … «tres» … «clic»",
     "desc": "Clic en cualquier punto de la pantalla: dices un número del 1 al 9 para afinar y luego «clic»"},
    {"id": "captura", "modo": "inicio", "seccion": "RATÓN Y PANTALLA",
     "frases": ["captura", "captura de pantalla", "captura la pantalla", "toma una captura",
                "toma una captura de pantalla", "haz una captura", "haz una captura de pantalla", "captura de ventana",
                "captura la ventana", "captura de la ventana", "screenshot", "toma un screenshot",
                "toma una foto de la pantalla"],
     "ejemplo": "Alfred captura de pantalla / captura la ventana",
     "desc": "Guarda una captura en Imágenes\\Alfred_capturas y la copia al portapapeles"},
    {"id": "configuracion", "modo": "inicio", "seccion": "SISTEMA Y HERRAMIENTAS",
     "frases": ["configuracion", "ajustes", "abre la configuracion", "abre configuracion", "abre los ajustes",
                "abre ajustes", "ve a configuracion", "configuracion de", "ajustes de", "abre la configuracion de",
                "modo avion", "activa el modo avion", "luz nocturna", "activa la luz nocturna"],
     "ejemplo": "Alfred abre la configuración de Bluetooth / sonido / pantalla / Wi-Fi / modo avión",
     "desc": "Abre la página de ajustes de Windows que pidas"},
    {"id": "herramientas", "seccion": "SISTEMA Y HERRAMIENTAS",
     "frases": [f for frases, _, _ in HERRAMIENTAS_WIN if frases[0] not in ("papelera",) for f in frases],
     "ejemplo": "Alfred abre el administrador de tareas / panel de control / símbolo del sistema / PowerShell",
     "desc": "Abre herramientas de Windows (tareas, panel de control, dispositivos, consola…)"},
    {"id": "estado_pc", "seccion": "SISTEMA Y HERRAMIENTAS",
     "frases": ["cuanta bateria", "nivel de bateria", "la bateria", "estado de la bateria", "como esta la bateria",
                "bateria", "uso del procesador", "uso de cpu", "uso del cpu", "como esta el procesador", "cuanto cpu",
                "memoria ram", "uso de memoria", "cuanta memoria", "cuanta ram", "espacio en disco", "espacio libre",
                "cuanto espacio", "que consume mas", "que esta consumiendo", "procesos pesados", "estoy conectado",
                "hay internet", "tengo internet", "estado de la red", "como esta el internet", "a que wifi",
                "nombre del wifi", "que wifi", "mi ip", "direccion ip", "cuanto tiempo lleva encendida",
                "tiempo encendida", "estado del sistema", "estado de la computadora", "como esta la computadora",
                "resumen del sistema", "estado del pc"],
     "ejemplo": "Alfred cuánta batería tengo / cómo está el procesador / espacio en disco / hay internet / estado del sistema",
     "desc": "Informa batería, procesador, memoria, disco, internet, Wi-Fi, IP y qué consume más (avisa solo si la batería baja)"},
    {"id": "wifi", "seccion": "SISTEMA Y HERRAMIENTAS",
     "frases": ["desconecta el wifi", "desconectar wifi", "desconecta wifi", "desconectar el wifi", "apaga el wifi",
                "apaga wifi", "conecta el wifi", "conecta wifi", "conectar wifi", "conectar el wifi", "reconecta el wifi",
                "reconecta wifi", "enciende el wifi", "prende el wifi", "activa el wifi", "desconecta el wi fi",
                "conecta el wi fi", "apaga el wi fi", "enciende el wi fi"],
     "ejemplo": "Alfred desconecta el Wi-Fi / conecta el Wi-Fi", "desc": "Desconecta o reconecta la red Wi-Fi"},
    {"id": "tema", "seccion": "SISTEMA Y HERRAMIENTAS",
     "frases": ["modo oscuro", "modo claro", "tema oscuro", "tema claro", "cambia el tema", "alterna el tema"],
     "ejemplo": "Alfred modo oscuro / modo claro", "desc": "Cambia Windows entre modo oscuro y claro"},
    {"id": "portapapeles", "seccion": "SISTEMA Y HERRAMIENTAS",
     "frases": ["portapapeles", "lee lo que copie", "lee el texto copiado", "que copie", "que tengo copiado"],
     "ejemplo": "Alfred lee el portapapeles / borra el portapapeles", "desc": "Lee en voz alta o vacía el portapapeles"},
    {"id": "papelera", "seccion": "SISTEMA Y HERRAMIENTAS",
     "frases": ["papelera", "abre la papelera", "vacia la papelera", "vaciar la papelera", "vacia papelera",
                "vaciar papelera", "limpia la papelera"],
     "ejemplo": "Alfred abre la papelera / vacía la papelera (pide un «sí»)", "desc": "Abre o vacía la papelera de reciclaje"},
    {"id": "silencio", "frases": ["silencio", "silencia", "mutea", "desmutea", "activa el sonido", "quita el sonido",
                                  "apaga el sonido", "pon el sonido", "enciende el sonido", "prende el sonido"],
     "ejemplo": "Alfred silencio / quita el silencio", "desc": "Silencia o reactiva el sonido"},
    {"id": "brillo", "frases": ["brillo"],
     "ejemplo": "Alfred sube el brillo / brillo al 50", "desc": "Controla el brillo de pantalla"},
    {"id": "volumen", "frases": ["volumen", "sube la musica", "baja la musica", "mas fuerte", "mas bajo", "subele",
                                  "bajale", "sube el sonido", "baja el sonido"],
     "ejemplo": "Alfred baja el volumen / volumen al 30 / sube la música", "desc": "Controla el volumen del sistema"},
    {"id": "carpeta_musica", "frases": ["reproduce la carpeta", "reproduce carpeta", "pon la carpeta", "pon carpeta",
                                       "toca la carpeta", "reproduce el album", "pon el album", "toca el album",
                                       "reproduce la playlist", "pon la playlist", "reproduce la lista", "pon la lista",
                                       "reproduce el disco", "pon el disco", "reproduce la coleccion", "pon la coleccion",
                                       "reproduce musica de", "pon musica de", "reproduce la musica de", "pon la musica de"],
     "ejemplo": "Alfred reproduce la carpeta rock (en aleatorio)", "desc": "Reproduce una carpeta de música por su nombre"},
    {"id": "que_suena", "frases": ["que suena", "que esta sonando", "que cancion es", "que cancion esta sonando",
                                   "que estoy escuchando", "como se llama esta cancion"],
     "ejemplo": "Alfred qué suena", "desc": "Dice qué canción está sonando"},
    {"id": "media", "frases": ["siguiente cancion", "cancion siguiente", "siguiente", "proxima cancion", "salta la cancion",
                              "salta", "cambia la cancion", "cambia de cancion", "cancion anterior", "anterior",
                              "pon la anterior", "pon la siguiente", "regresa la cancion", "retrocede la cancion",
                              "pasa la cancion", "otra cancion", "pausa", "pausar", "reanuda", "reanudar", "continua",
                              "dale play", "pon play", "play", "detener musica", "detener", "deten la musica",
                              "detente", "stop", "para la musica", "para la cancion", "pausa la musica"],
     "ejemplo": "Alfred siguiente canción / pausa / canción anterior / detener música",
     "desc": "Controla tu reproductor de música (el que esté abierto: VLC, foobar2000…)"},
    {"id": "spotify", "frases": ["spotify", "espotifai", "espoti fai", "espoti", "pon musica", "musica",
                                 "abre el reproductor", "pon el reproductor", "reproductor"],
     "ejemplo": "Alfred pon música", "desc": "Abre tu reproductor de música (o reanuda el que ya está abierto)"},
    {"id": "descanso", "frases": ["descanso", "hora del descanso", "despeja el escritorio", "minimiza todo"],
     "ejemplo": "Alfred descanso", "desc": "Minimiza todas las ventanas (Win + D)"},
    {"id": "calculadora", "frases": ["calculadora"], "ejemplo": "Alfred calculadora", "desc": "Abre la calculadora"},
    {"id": "bloc", "frases": ["bloc de notas", "notepad"], "ejemplo": "Alfred bloc de notas", "desc": "Abre el bloc de notas"},
    {"id": "explorador", "frases": ["explorador", "carpetas", "archivos"],
     "ejemplo": "Alfred abre el explorador", "desc": "Abre el Explorador de archivos"},
    {"id": "buscar_web", "frases": ["busca en google", "busca en youtube", "busca en internet", "busca en la web",
                                    "buscar en google", "buscar en youtube", "googlea", "busca", "buscame"],
     "ejemplo": "Alfred busca recetas de pozole en YouTube", "desc": "Busca en Google o YouTube y abre el resultado"},
    {"id": "abrir", "frases": ["abre", "abrir", "abreme", "ejecuta", "inicia", "lanza", "arranca"],
     "ejemplo": "Alfred abre Chrome / abre descargas / abre YouTube",
     "desc": "Abre una aplicación, una página web o una carpeta (Descargas, Documentos…)"},
    {"id": "hora", "frases": ["que hora es", "que horas son", "la hora", "hora actual", "dime la hora"],
     "ejemplo": "Alfred qué hora es", "desc": "Dice la hora"},
    {"id": "fecha", "frases": ["que dia es", "fecha de hoy", "que fecha es", "en que dia estamos", "a cuanto estamos"],
     "ejemplo": "Alfred qué día es", "desc": "Dice la fecha"},
    {"id": "ayuda", "frases": ["ayuda", "comandos", "que puedes hacer"],
     "ejemplo": "Alfred ayuda", "desc": "Muestra la lista de comandos"},
    {"id": "salir", "frases": ["adios", "apagate", "cierrate", "hasta luego", "cerrar asistente", "apagar asistente"],
     "ejemplo": "Alfred adiós", "desc": "Cierra el asistente"},
]


# Índice precalculado: (comando, modo, frases ya rodeadas de espacios). Modos: None = la frase aparece en cualquier
# parte de la orden; «inicio» = la orden EMPIEZA con ella (para órdenes con argumento: «escribe…», «cierra Chrome»);
# «exacto» = toda la orden es esa frase (teclas y atajos: así «busca cómo copiar un archivo» no pulsa Ctrl+C).
_INDICE_COMANDOS = [(c, c.get("modo"), tuple(f" {f} " for f in c["frases"])) for c in COMANDOS]
_CMD_CANCION = next(c for c in COMANDOS if c["id"] == "cancion")


@functools.lru_cache(maxsize=512)
def buscar_comando(norm):
    if pedido_cancion(norm):                         # «pon X» / «reproduce X»: primero, para que un título como
        return _CMD_CANCION                          # «Recuérdame» no se confunda con otro comando
    texto = f" {norm} "
    nucleo = None
    for cmd, modo, frases in _INDICE_COMANDOS:
        if modo is None:
            if any(f in texto for f in frases):
                return cmd
            continue
        if nucleo is None:
            nucleo = f" {nucleo_orden(norm)} "
        if modo == "inicio":
            if any(nucleo.startswith(f) for f in frases):
                return cmd
        elif nucleo in frases:
            return cmd
    return None


def _token_parecido(tok, ref):
    """1.0 si es el mismo token; 0.95 si solo cambia entre singular y plural («pausas» ~ «pausa», «recordatorio» ~
    «recordatorios», «volumenes» ~ «volumen»); 0 si no. Solo palabras de 5 letras o más. Se probó con parecido por
    letras y por sonido, y mezclaba palabras distintas («trabajador» no es «trabajar»): por eso solo el plural."""
    if tok == ref:
        return 1.0
    if len(tok) < 5 or len(ref) < 5:
        return 0.0
    for a, b in ((tok, ref), (ref, tok)):             # a = la corta, b = la que podría ser su plural
        if b == a + "s" or b == a + "es":
            return 0.95
    return 0.0


def buscar_comando_difuso(norm):
    """Último recurso cuando ninguna frase coincide exacta: busca la frase de comando cuyas palabras SUENAN o se
    escriben casi igual (el reconocedor a veces cambia una letra o el final de una palabra). Devuelve
    (comando, orden_corregida) con mejor parecido, o None. La orden corregida lleva las palabras tal como las espera
    el comando (así «pausas» llega como «pausa»). Se usa solo tras haber oído la palabra de activación, nunca para
    elegir entre idiomas."""
    toks = norm.split()
    if not toks:
        return None
    mejor, mejor_s, mejor_orden = None, 0.0, None
    for cmd in COMANDOS:
        if cmd.get("modo"):
            continue                                  # órdenes con argumento o teclas: exactas o nada
        for frase in cmd["frases"]:
            pl = frase.split()
            k = len(pl)
            if k > len(toks) or not any(len(w) >= 5 for w in pl):
                continue                              # frases solo de palabras cortas: exactas o nada
            for i in range(len(toks) - k + 1):
                rs = [_token_parecido(toks[i + j], pl[j]) for j in range(k)]
                if all(rs):
                    sc = sum(rs) / k + 0.01 * k
                    if sc > mejor_s:
                        mejor, mejor_s = cmd, sc
                        mejor_orden = " ".join(toks[:i] + pl + toks[i + k:])
    return (mejor, mejor_orden) if mejor else None


# ── comandos del usuario ─────────────────────────────────────────────────────
TIPOS_ACCION = {  # etiqueta: (tipo, ayuda campo 1, ayuda campo 2 o None)
    "Abrir aplicación": ("app", "Nombre o ruta (ej. Opera GX, Spotify, Discord)", None),
    "Abrir página web": ("web", "Dirección (ej. youtube.com)", "Navegador (vacío = predeterminado; ej. Opera GX)"),
    "Abrir archivo o carpeta": ("archivo", "Ruta del archivo o carpeta", None),
    "Mover archivo o carpeta": ("mover", "Qué mover (admite *, ej. C:\\Descargas\\*.pdf)", "Carpeta destino"),
    "Copiar archivo o carpeta": ("copiar", "Qué copiar (admite *)", "Carpeta destino"),
    "Eliminar (a la papelera)": ("eliminar", "Qué eliminar (admite *)", None),
    "Decir en voz alta": ("decir", "Texto que dirá Alfred", None),
    "Esperar segundos": ("esperar", "Segundos (ej. 2)", None),
    "Pulsar teclas": ("teclas", "Combinación (ej. ctrl+shift+t, alt+tab, win+d, f5)", None),
    "Escribir texto": ("escribir", "Texto que se escribirá en la ventana activa", None),
    "Ejecutar comando de Alfred": ("comando", "Frase de un comando (ej. captura de pantalla, bloquea la pantalla, cierra chrome)", None),
}
ETIQUETA_DE_TIPO = {v[0]: k for k, v in TIPOS_ACCION.items()}


def cargar_personalizados(ruta):
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
        return [c for c in datos if isinstance(c, dict) and c.get("frase") and isinstance(c.get("acciones"), list)]
    except FileNotFoundError:
        return []
    except Exception:
        logging.exception("comandos_usuario.json ilegible")
        return []


def guardar_personalizados(ruta, lista):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=2, ensure_ascii=False)


def buscar_personalizado(lista, orden_norm):
    """Comando del usuario cuya frase aparece en la orden (gana la frase más larga)."""
    mejor, largo = None, 0
    texto = f" {orden_norm} "
    for c in lista:
        f = normalizar(c.get("frase", ""))
        if f and f" {f} " in texto and len(f) > largo:
            mejor, largo = c, len(f)
    return mejor


def normalizar_url(u):
    u = u.strip()
    if re.match(r"^[a-z][a-z0-9+.-]*://", u, re.I) or u.lower().startswith(("mailto:", "spotify:")):
        return u
    return "https://" + u


# ── archivos (mover / copiar / eliminar) ─────────────────────────────────────
def expandir(p):
    return os.path.expandvars(os.path.expanduser(p.strip().strip('"')))


def coincidencias(patron):
    p = expandir(patron)
    if any(c in p for c in "*?["):
        return sorted(glob.glob(p))
    return [p] if os.path.exists(p) else []


def ruta_peligrosa(p):
    """Rutas que nunca se eliminan ni se mueven por voz: raíces, carpeta personal, carpetas del sistema y la propia
    carpeta de Alfred (y las que la contienen). Se resuelven enlaces simbólicos y uniones antes de decidir."""
    p = os.path.realpath(os.path.abspath(p))
    _, resto = os.path.splitdrive(p)
    partes = [x for x in resto.replace("/", os.sep).split(os.sep) if x]
    home = os.path.realpath(os.path.abspath(os.path.expanduser("~")))
    protegidas = {os.path.normcase(os.path.join(home, x)) for x in
                  ("Desktop", "Documents", "Downloads", "Pictures", "Music", "Videos", "AppData", "OneDrive",
                   "Escritorio", "Documentos", "Descargas", "Imágenes", "Música", "Vídeos")}
    n = os.path.normcase(p)
    if len(partes) < 3 or n == os.path.normcase(home) or n in protegidas:
        return True
    for var in ("SystemRoot", "ProgramFiles", "ProgramFiles(x86)", "ProgramData"):
        d = os.environ.get(var)
        if d and n.startswith(os.path.normcase(os.path.realpath(d))):
            return True
    propias = [BASE_DIR] + ([_DATOS_DIR[0]] if _DATOS_DIR[0] else [])
    for d in propias:
        dn = os.path.normcase(os.path.realpath(d))
        if n == dn or n.startswith(dn + os.sep) or dn.startswith(n + os.sep):     # ella, su contenido o quien la contiene
            return True
    return False


def destino_libre(carpeta, nombre):
    destino = os.path.join(carpeta, nombre)
    if not os.path.exists(destino):
        return destino
    base, ext = os.path.splitext(nombre)
    i = 1
    while os.path.exists(os.path.join(carpeta, f"{base} ({i}){ext}")):
        i += 1
    return os.path.join(carpeta, f"{base} ({i}){ext}")


def mover_patron(origen, destino):
    items = coincidencias(origen)
    if not items:
        raise FileNotFoundError(f"No encontré: {origen}")
    for it in items:      # mover = quitarlo de su sitio: mismas rutas protegidas que al eliminar
        if ruta_peligrosa(it):
            raise PermissionError(f"Ruta protegida, no la muevo: {it}")
    destino = expandir(destino)
    os.makedirs(destino, exist_ok=True)
    for it in items:
        shutil.move(it, destino_libre(destino, os.path.basename(it.rstrip("\\/"))))
    return len(items)


def copiar_patron(origen, destino):
    items = coincidencias(origen)
    if not items:
        raise FileNotFoundError(f"No encontré: {origen}")
    destino = expandir(destino)
    os.makedirs(destino, exist_ok=True)
    for it in items:
        d = destino_libre(destino, os.path.basename(it.rstrip("\\/")))
        if os.path.isdir(it):
            shutil.copytree(it, d)
        else:
            shutil.copy2(it, d)
    return len(items)


def eliminar_patron(patron, borrar_fn):
    items = coincidencias(patron)
    if not items:
        raise FileNotFoundError(f"No encontré: {patron}")
    for it in items:   # primero se revisa todo; si algo está protegido, no se borra nada
        if ruta_peligrosa(it):
            raise PermissionError(f"Ruta protegida, no la elimino: {it}")
    for it in items:
        borrar_fn(it)
    return len(items)


# ── búsqueda de aplicaciones (partes puras) ──────────────────────────────────
def coincide_nombre(clave, nombre):
    n = normalizar(nombre)
    return all(p in n for p in clave.split())


def puntuar_nombre(clave, nombre):
    n = normalizar(nombre)
    return (0 if n == clave else 1 if n.startswith(clave) else 2, len(n))


EXCLUIR_LNK = re.compile(r"uninstall|desinstal|readme|manual|ayuda|help|licen", re.I)
EXCLUIR_EXE = re.compile(r"unins|update|crash|helper|install|setup|notif|report|elevat|proxy|service|repair", re.I)


def elegir_exe(exes, clave):
    """De varios .exe dentro de la carpeta de una app, el que más probablemente la abre."""
    exes = [e for e in exes if not EXCLUIR_EXE.search(os.path.basename(e))]
    if not exes:
        return None
    compacto = clave.replace(" ", "")
    primera = clave.split()[0]

    def puntaje(e):
        stem = normalizar(os.path.splitext(os.path.basename(e))[0]).replace(" ", "")
        if stem == compacto:
            r = 0
        elif stem == "launcher":
            r = 1
        elif stem.startswith(primera):
            r = 2
        else:
            r = 3
        return (r, e.count(os.sep), len(e))
    return sorted(exes, key=puntaje)[0]


# ── agenda ───────────────────────────────────────────────────────────────────
def leer_agenda(ruta):
    items = []
    if not os.path.exists(ruta):
        return items
    with open(ruta, encoding="utf-8", errors="replace") as f:
        for linea in f:
            linea = linea.rstrip("\r\n")
            m = re.match(r"^\[(\d{4}-\d{2}-\d{2})(?: (\d{2}:\d{2}))?\]\s*(.*)$", linea)
            if m:
                items.append({"fecha": m.group(1), "hora": m.group(2) or "", "texto": m.group(3).strip()})
            elif linea.strip():
                items.append({"fecha": "", "hora": "", "texto": linea.strip()})
    return items


def guardar_agenda(ruta, items):
    with open(ruta, "w", encoding="utf-8") as f:
        for it in items:
            marca = ""
            if it["fecha"]:
                marca = f"[{it['fecha']} {it['hora']}] " if it["hora"] else f"[{it['fecha']}] "
            f.write(marca + it["texto"] + "\n")


def agregar_agenda(ruta, texto, ahora):
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(f"[{ahora:%Y-%m-%d %H:%M}] {texto}\n")


def agenda_de_hoy(items, hoy):
    return [it["texto"] for it in items if it["fecha"] == hoy]


# ── aplausos ─────────────────────────────────────────────────────────────────
def niveles_frames(data, frame=160):
    """Nivel RMS (0-1) de cada tramo de 10 ms (160 muestras a 16 kHz) del bloque de audio."""
    a = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    n = a.size // frame
    if n == 0:
        return []
    f = a[:n * frame].reshape(n, frame)
    return np.sqrt((f * f).mean(axis=1)).tolist()


class DetectorAplausos:
    """
    Detecta aplausos como TRANSITORIOS: sube de golpe desde el silencio y se apaga en < 60 ms.
    La voz (sostenida, con sonido previo) y la música no cumplen eso. Se alimenta con tramos de 10 ms.
    """

    def __init__(self, umbral=0.12, dt=0.01, ventana=1.6, separacion=0.12, decaimiento=0.4, max_frames=6):
        self.umbral, self.dt, self.ventana = umbral, dt, ventana
        self.separacion, self.decaimiento, self.max_frames = separacion, decaimiento, max_frames
        self.ruido = 0.01
        self.t = 0.0
        self.reiniciar()

    def reiniciar(self):
        self.estado, self.pico, self.t0, self.n = "espera", 0.0, 0.0, 0
        self.tiempos = []
        self.hist = deque(maxlen=5)

    def procesar(self, nivel):
        """Un tramo de 10 ms. Devuelve 0 (nada), 1 (aplauso) o 2 (doble aplauso)."""
        self.t += self.dt
        resultado = 0
        if self.estado == "espera":
            previo = max(self.hist) if self.hist else 0.0
            if nivel > self.umbral and nivel > 3 * self.ruido and previo < 0.4 * nivel:
                self.estado, self.pico, self.t0, self.n = "candidato", nivel, self.t, 0
            else:
                self.ruido = max(0.002, 0.98 * self.ruido + 0.02 * min(nivel, 3 * self.ruido + 0.005))
        elif self.estado == "candidato":
            self.n += 1
            self.pico = max(self.pico, nivel)
            if nivel < self.decaimiento * self.pico:      # se apagó rápido: es un aplauso
                resultado = self._contar()
                self.estado = "enfriar"
            elif self.n > self.max_frames:                # dura demasiado: voz o música
                self.estado = "enfriar"
        else:  # enfriar
            if nivel < self.umbral and self.t - self.t0 >= self.separacion:
                self.estado = "espera"
        self.hist.append(nivel)
        return resultado

    def _contar(self):
        t = self.t0
        self.tiempos = [x for x in self.tiempos if t - x <= self.ventana]
        if self.tiempos and t - self.tiempos[-1] < self.separacion:
            return 0
        self.tiempos.append(t)
        if len(self.tiempos) >= 2:
            self.tiempos = []
            return 2
        return 1


def calcular_umbral(muestras):
    """muestras = [(t, pico_del_bloque)] grabadas mientras el usuario aplaude. -> (umbral, ruido, picos) o None."""
    if len(muestras) < 5:
        return None
    niveles = sorted(n for _, n in muestras)
    ruido = niveles[len(niveles) // 2]
    orden = sorted(muestras, key=lambda m: -m[1])
    p1 = orden[0]
    if p1[1] < max(0.04, ruido * 4):
        return None
    p2 = next((m for m in orden[1:] if abs(m[0] - p1[0]) > 0.25), None)
    picos = [p1[1]]
    if p2 and p2[1] >= max(0.03, ruido * 3):
        picos.append(p2[1])
    umbral = min(0.6, max(0.03, ruido * 3, 0.5 * min(picos)))
    return umbral, ruido, picos


def localizar_modelo(ruta):
    """Carpeta real del modelo Vosk (acepta una subcarpeta anidada), o None."""
    if not os.path.isdir(ruta):
        return None
    if os.path.isdir(os.path.join(ruta, "am")):
        return ruta
    for nombre in os.listdir(ruta):
        sub = os.path.join(ruta, nombre)
        if os.path.isdir(os.path.join(sub, "am")):
            return sub
    return None

# ══════════════════════════════════════════════════════════════════════════════
#  DOS IDIOMAS: Alfred oye en español y en inglés a la vez, elige la lectura que tiene sentido y entiende las
#  órdenes en inglés traduciéndolas a su forma en español (así TODOS los comandos sirven en los dos idiomas).
# ══════════════════════════════════════════════════════════════════════════════
PALABRAS_SI = ("si", "confirmo", "confirmar", "adelante", "dale", "yes", "yeah", "yep", "confirm", "confirmed", "sure", "ahead")

_EN_UNID = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
            "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
            "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
_EN_DEC = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}


def numeros_en_a_digitos(norm):
    """'volume fifty five' -> 'volume 55'; 'one hundred' -> '100'. (Solo se usa en volumen y brillo.)"""
    toks, out, i = norm.split(), [], 0
    while i < len(toks):
        t = toks[i]
        if t in _EN_DEC:
            val = _EN_DEC[t]
            if i + 1 < len(toks) and 0 < _EN_UNID.get(toks[i + 1], 99) < 10:
                val += _EN_UNID[toks[i + 1]]
                i += 1
            out.append(str(val))
        elif t in _EN_UNID:
            out.append(str(_EN_UNID[t]))
        elif t == "hundred":
            if out and out[-1] == "1":
                out[-1] = "100"
            else:
                out.append("100")
        else:
            out.append(t)
        i += 1
    return " ".join(out)


_CORTESIA_INI = re.compile(r"^(?:(?:please|kindly|hey|okay|ok|so|now|then|can you|could you|would you|will you|"
                           r"i want you to|i want to|i would like you to|i would like to|go ahead and|just)\s+)+")
_CORTESIA_FIN = re.compile(r"(?:\s+(?:please|thanks|thank you|for me|now))+$")


def _en_pre(norm):
    """Quita cortesías y contracciones: 'could you please tell me what's the time' -> 'tell me what is the time'."""
    t = f" {norm} "
    t = re.sub(r" (what|that|it|here|there|who|how|where) s ", r" \1 is ", t)
    t = re.sub(r" let s ", " lets ", t)
    t = re.sub(r" today s ", " todays ", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = _CORTESIA_INI.sub("", t)
    t = _CORTESIA_FIN.sub("", t)
    return t.strip()


def _nivel_en(t, objeto_es):
    """Volumen / brillo: 'turn the volume up a little' -> 'sube el volumen un poco'; 'volume fifty' -> 'volumen al 50'."""
    t = numeros_en_a_digitos(t)
    suf = ""
    if re.search(r"\b(a little|a bit|slightly|little|bit|tiny)\b", t):
        suf = " un poco"
    elif re.search(r"\b(a lot|much|way)\b", t):
        suf = " mucho"
    if re.search(r"\b(max|maximum|full|highest|all the way)\b", t):
        return f"{objeto_es} al maximo"
    if re.search(r"\b(min|minimum|lowest)\b", t):
        return f"{objeto_es} al minimo"
    if re.search(r"\bhalf\b", t):
        return f"{objeto_es} a la mitad"
    n = re.search(r"\b(\d{1,3})\b", t)
    if n:
        return f"{objeto_es} al {n.group(1)}"
    if re.search(r"\b(up|raise|increase|higher|louder|more|brighter|boost)\b", t):
        return f"sube el {objeto_es}{suf}"
    if re.search(r"\b(down|lower|decrease|reduce|quieter|softer|less|dimmer|dim)\b", t):
        return f"baja el {objeto_es}{suf}"
    return objeto_es


_EN_OBJETOS = {"downloads": "descargas", "download": "descargas", "documents": "documentos", "desktop": "escritorio",
               "pictures": "imagenes", "photos": "fotos", "videos": "videos", "music": "musica",
               "calculator": "calculadora", "notepad": "bloc de notas", "file explorer": "explorador",
               "explorer": "explorador", "files": "explorador", "music player": "reproductor",
               "player": "reproductor", "news": "noticias", "map": "mapas", "maps": "mapas", "mail": "correo",
               "email": "correo", "translator": "traductor"}
_EN_ALEATORIO = re.compile(r"\b(?:on shuffle|in random order|shuffled|shuffle|randomly|random)\b")


def _sin_aleatorio_en(texto):
    limpio = _EN_ALEATORIO.sub(" ", texto)
    return re.sub(r"\s+", " ", limpio).strip(), limpio != texto


_EN_RELLENO = re.compile(r"^(?:(?:uh|um|uhm|umm|er|erm|ah|eh|hmm|well|like)\s+)+")
_EN_CLAVES_LARGAS = ("pause", "resume", "continue", "unmute", "volume", "brightness", "louder", "quieter", "brighter",
                     "dimmer", "previous", "minimize", "maximize", "restore", "goodbye", "calculator", "notepad",
                     "explorer", "downloads", "documents", "playlist", "agenda", "schedule", "reminders", "launch",
                     "search", "shuffle")
_EN_CLAVES_CORTAS = ("mute", "skip", "stop", "next", "play", "open", "help")


_EN_HOMOFONOS = {"paws": "pause", "pawz": "pause", "moot": "mute", "mewt": "mute", "unmoot": "unmute"}   # suenan igual


def _en_clave(tok):
    """Una palabra mal oída ('paws', 'volum', 'skips', 'brightnes') -> la palabra de comando en inglés que más se
    le parece, o la misma palabra si no se parece a ninguna."""
    if tok in _EN_HOMOFONOS:
        return _EN_HOMOFONOS[tok]
    if len(tok) < 4 or tok in _EN_CLAVES_LARGAS or tok in _EN_CLAVES_CORTAS:
        return tok
    for c in _EN_CLAVES_CORTAS:
        if tok == c + "s":
            return c
    mejor, mejor_r = tok, 0.0
    for c in _EN_CLAVES_LARGAS:
        if abs(len(c) - len(tok)) > 2:
            continue
        r = SequenceMatcher(None, tok, c).ratio()
        if r >= 0.86 and r > mejor_r:
            mejor, mejor_r = c, r
    return mejor


def _en_arreglar(t):
    """Quita muletillas ('um', 'uh') y corrige palabras de comando mal oídas. Solo toca la primera palabra o las
    órdenes de hasta 3 palabras: lo que viene detrás ('play ...', 'search ...', 'remind me ...') son títulos, notas y
    búsquedas, y se deja tal cual."""
    t = _EN_RELLENO.sub("", t).strip()
    t = re.sub(r"^(?:the |my )?a gender\b", "agenda", t)                # «a gender» es como se oye «agenda»
    toks = t.split()
    if not toks:
        return t
    if len(toks) <= 3:
        toks = [_en_clave(w) for w in toks]
    else:
        toks[0] = _en_clave(toks[0])
    return " ".join(toks)


@functools.lru_cache(maxsize=512)
def _plat_es(texto):
    """'numb on spotify' -> 'numb en spotify' (así lo entiende pedido_cancion_ex)."""
    return re.sub(r"\s(?:on|in|with|using|through|via)\s+(?:the )?(spotify|youtube music|you ?tube music|youtube|you tube)$",
                  lambda mm: " en " + mm.group(1), texto)


def traducir_orden_en(orden):
    """Orden en inglés (normalizada, sin la palabra de activación) -> la misma orden en español que entiende Alfred,
    o None si no se parece a ningún comando. Lo que no son palabras de comando (títulos, notas, búsquedas) se conserva."""
    t = _en_pre(orden)
    if not t:
        return None
    t = _en_arreglar(t)

    def r(*patrones):
        return any(re.search(p, t) for p in patrones)

    def m(patron):
        return re.match(patron, t)

    # sonido
    if r(r"^unmute\b", r"^sound on$", r"^(?:turn|switch|put)(?: the)? sound on$", r"^turn on(?: the)? sound$",
         r"^restore(?: the)? sound$", r"^bring back(?: the)? sound$"):
        return "activa el sonido"
    if r(r"^mute\b", r"^silence$", r"^sound off$", r"^(?:turn|switch|put)(?: the)? sound off$",
         r"^turn off(?: the)? sound$", r"^be quiet$", r"^shut up$"):
        return "silencio"
    # ventana
    if r(r"^(?:show yourself|show up|come back|come out|come here|wake up|appear|restore|maximi[sz]e|unminimi[sz]e|un minimi[sz]e)$",
         r"^bring (?:up|back) (?:the |your )?window$", r"^show (?:the |your |main )?(?:window|panel|screen)$",
         r"^open (?:the |your )?(?:main )?window$", r"^(?:get|come) out of (?:the )?(?:background|tray)$",
         r"^back to (?:the )?screen$"):
        return "muestrate"
    if r(r"^(?:minimi[sz]e|hide) (?:everything|all(?: the)?(?: windows)?)$", r"^show (?:the )?desktop$",
         r"^clear (?:the )?desktop$", r"^(?:take a )?break$", r"^break time$"):
        return "descanso"
    if r(r"^(?:go (?:to )?(?:the )?(?:background|tray)|minimi[sz]e(?: yourself| window)?|hide(?: yourself| the window| window)?|"
         r"run in (?:the )?background|background mode|(?:go|move) to (?:the )?system tray)$"):
        return "segundo plano"
    # brillo y volumen
    if r(r"\bbrightness\b", r"^(?:make it )?(?:brighter|dimmer)$", r"^dim the screen"):
        return _nivel_en(t, "brillo")
    if r(r"\bvolume\b", r"^(?:make it )?(?:louder|quieter|softer)(?: a little| a bit| a lot)?$",
         r"^turn (?:it |the (?:music|sound|song) )?(?:up|down)(?: a little| a bit| a lot| slightly)?$",
         r"^turn (?:up|down) the (?:music|sound|song)(?: a little| a bit| a lot| slightly)?$"):
        return _nivel_en(t, "volumen")
    # qué suena
    if r(r"^what is (?:playing|this song|that song)(?: now| right now)?$", r"^what song is (?:this|playing|that)$",
         r"^what am i listening to$", r"^which song is (?:this|playing)$", r"^name of (?:this|the) song$",
         r"^what is the song(?: name)?$"):
        return "que suena"
    # control del reproductor
    if r(r"^(?:play |go to |switch to |change to )?(?:the )?(?:next|following)(?: song| track| one| tune)?$",
         r"^skip(?: this| the| that)?(?: song| track| one| tune)?$", r"^(?:change|switch)(?: the)? (?:song|track)$",
         r"^another (?:song|one|track)$", r"^forward$"):
        return "siguiente cancion"
    if r(r"^(?:play |go |go to |switch to )?(?:the )?(?:previous|last|back)(?: song| track| one| tune)?$",
         r"^go back$", r"^rewind$"):
        return "cancion anterior"
    if r(r"^pause(?: the)?(?: music| song| track| playback| it)?$"):
        return "pausa"
    if r(r"^(?:resume|continue|unpause)(?: the)?(?: music| song| track| playback| it)?$", r"^play$", r"^play it$",
         r"^hit play$", r"^press play$"):
        return "dale play"
    if r(r"^(?:stop|halt)(?: the| playing| playback)?(?: music| song| track| playing)?$", r"^stop playing$"):
        return "detener musica"
    if r(r"^(?:play|start|put on)(?: some| the)? music$", r"^music$"):
        return "pon musica"
    if r(r"^(?:open|launch|start)(?: the| my)? (?:music )?player$"):
        return "abre el reproductor"
    # reproducir carpetas, álbumes y canciones
    mm = m(r"^(?:play|put on|start|queue)(?: the| my)? (?:folder|album|playlist|collection|record|disc)"
           r"(?: called| named| titled| of| from)? (.+)$") or m(r"^shuffle(?: the| my)?(?: folder| album| playlist)? (.+)$")
    if mm:
        pedido, alea = _sin_aleatorio_en(mm.group(1))
        if pedido:
            return f"reproduce la carpeta {pedido}" + (" aleatorio" if alea or t.startswith("shuffle") else "")
    mm = m(r"^(?:play|put on|start)(?: some| me some)? (?:music|songs|tracks|hits) (?:by|from|of) (.+)$")
    if mm:
        pedido, alea = _sin_aleatorio_en(_plat_es(mm.group(1)))
        return f"pon musica de {pedido}" + (" aleatorio" if alea else "")
    mm = m(r"^(?:play|put on)(?: me)?(?: the| some)? (?:band|artist|group|singer) (.+)$")
    if mm:
        return "reproduce la banda " + _plat_es(mm.group(1))
    mm = m(r"^(?:play|put on|listen to|queue(?: up)?)(?: me)?(?: the| a| my)?(?: (?:song|track|tune|jam))?"
           r"(?: (?:called|named|titled))? (.+)$")
    if mm and mm.group(1) not in ("song", "track", "tune", "jam", "music", "something", "it", "this"):
        return "pon " + re.sub(r"\bby\b", "de", _plat_es(mm.group(1)))
    # buscar en internet
    mm = m(r"^(?:search|look ?up|google|googling|browse)\s+(?:for\s+)?(.+)$")
    if mm:
        cuerpo, sitio = mm.group(1), ""
        s1 = re.match(r"^(youtube|google|the web|the internet)\s+(?:for\s+)?(.+)$", cuerpo)
        s2 = re.match(r"^(.+?)\s+(?:on|in|with|using)\s+(youtube|google|the web|the internet)$", cuerpo)
        if s1:
            sitio, cuerpo = s1.group(1), s1.group(2)
        elif s2:
            cuerpo, sitio = s2.group(1), s2.group(2)
        return f"busca en {'youtube' if sitio == 'youtube' else 'google'} {cuerpo}"
    if t == "google":
        return "abre google"
    pc = _traducir_pc_en(t, numeros_en_a_digitos)             # 3.0: control del PC
    if pc:
        return pc
    # abrir aplicaciones, webs y carpetas
    mm = m(r"^(?:open|launch|start|run|execute|fire up)(?: up)?(?: the| my| a| an)? (.+)$")
    if mm:
        obj = re.sub(r" (?:folder|app|application|program|website|site|page|window)$", "", mm.group(1)).strip()
        return "abre " + _EN_OBJETOS.get(obj, obj)
    if t in ("calculator", "notepad", "file explorer", "explorer", "files", "folders"):
        return _EN_OBJETOS.get(t, "explorador")
    # notas y recordatorios
    mm = m(r"^(?:remind me|remember|note down|note|write down|jot down|take (?:a )?note|make (?:a )?note|"
           r"add (?:a )?(?:reminder|note))(?: to| that| about| of| for)? (.+)$")
    if mm:
        return "recuerdame " + mm.group(1)
    # rutinas y saludos
    if r(r"^lets (?:get )?(?:to )?work$", r"^lets get started$", r"^time (?:to|for) work$", r"^work mode$",
         r"^start (?:my )?work(?:ing)?(?: day)?$"):
        return "vamos a trabajar"
    if r(r"^good (?:morning|afternoon|evening|night)(?: to you)?$", r"^(?:morning|daily) (?:report|briefing)$",
         r"^briefing$"):
        return "buenos dias"
    # agenda
    if r(r"^what (?:do i have|have i got|is on my (?:agenda|schedule|list))(?: today| for today| to do today)?$"):
        return "que tengo hoy"
    if r(r"^(?:show|open|display|bring up|let me see)(?: me)?(?: my| the)? (?:agenda|schedule|reminders|calendar|to do list|todo list|notes)$"):
        return "ensename la agenda"
    if r(r"^(?:read|tell me|say)(?: me| out)?(?: my| the)? (?:agenda|schedule|reminders|to do list|notes)(?: out loud| aloud)?$"):
        return "lee mi agenda"
    if r(r"^(?:agenda|reminders|my agenda|my reminders|schedule)$"):
        return "agenda"
    # hora y fecha
    if r(r"^(?:what (?:time|hour)(?: is it)?|what is the (?:current )?time|(?:tell|give) me the (?:current )?time|"
         r"(?:current )?time|the time)(?: now| right now)?$"):
        return "que hora es"
    if r(r"^(?:what (?:day|date)(?: is it| is today)?|what is (?:the )?(?:date|day)(?: today)?|what is todays date|"
         r"what is today|which day is(?: it| today)|todays date|(?:tell|give) me (?:the|todays) date|"
         r"(?:the )?(?:current )?date|what day of the week is it)$"):
        return "que dia es"
    # ayuda y salir
    if r(r"^(?:help|commands|help me|list(?: of)?(?: the)? commands|show(?: me)?(?: the)? commands|what can you do|"
         r"what commands do you have|what are your commands)$"):
        return "ayuda"
    if r(r"^(?:goodbye|good bye|bye|bye bye|see you(?: later| soon)?|shut down|shutdown|power off|turn off|switch off|"
         r"close (?:the )?assistant|exit|quit)$"):
        return "adios"
    return None


def extraer_candidatos(js, idioma):
    """Resultado JSON de Vosk -> [(texto, idioma, rango)]. Con varias alternativas (n-mejores) devuelve todas, la mejor primero."""
    try:
        d = json.loads(js)
    except (TypeError, ValueError):
        return []
    if not isinstance(d, dict):
        return []
    alts = d.get("alternatives")
    textos = [a.get("text", "") for a in alts if isinstance(a, dict)] if isinstance(alts, list) else [d.get("text", "")]
    return [(t.strip(), idioma, i) for i, t in enumerate(textos) if t and t.strip()]


def elegir_candidato(cands, frases_wake, es_orden, idioma_pref="es"):
    """De todas las lecturas (español + inglés, cada una con sus alternativas) elige la que tiene palabra de
    activación y una orden que Alfred entiende. es_orden(orden_normalizada, idioma) -> bool. Devuelve (texto, idioma) o None.
    A igualdad de todo gana el idioma de la conversación (idioma_pref): si venías hablando en inglés, un empate
    se resuelve a favor del inglés."""
    mejor, mejor_s = None, -1.0
    for texto, idioma, rango in cands:
        norm = normalizar(texto)
        if not norm:
            continue
        wake, orden = quitar_wake(norm, frases_wake)
        s = 0.0
        if wake:
            s += 2.0
        if orden and es_orden(orden, idioma):
            s += 1.0
        s -= 0.05 * rango                         # a igualdad, manda la alternativa que Vosk puso primero
        if idioma == idioma_pref:
            s += 0.03                             # y a igualdad de todo, el idioma en que venías hablando
        elif idioma == "es":
            s += 0.02                             # si no, el español
        if s > mejor_s:
            mejor, mejor_s = (texto, idioma), s
    return mejor


# ── respuestas en inglés (la voz Kokoro tiene voces en inglés) ───────────────
_RESP_EN = {
    "Sistemas listos.": "Systems ready.",
    "Diga": "Yes?",
    "No tengo ese comando, señor.": "I don't have that command, sir.",
    "Cancelado.": "Cancelled.",
    "Hubo un error al ejecutar esa orden.": "There was an error running that command.",
    "Este comando elimina archivos. Diga sí para confirmar.": "This command deletes files. Say yes to confirm.",
    "Excelente, señor. Desplegando herramientas de trabajo.": "Excellent, sir. Deploying your work tools.",
    "Bienvenido a casa, señor.": "Welcome home, sir.",
    "Aquí tiene su agenda.": "Here is your agenda.",
    "No tiene recordatorios para hoy.": "You have no reminders for today.",
    "No escuché qué debo anotar.": "I didn't catch what to write down.",
    "Brillo al cien por ciento.": "Brightness at one hundred percent.",
    "Brillo al mínimo.": "Brightness at minimum.",
    "Brillo a la mitad.": "Brightness at half.",
    "Subiendo brillo.": "Turning the brightness up.",
    "Bajando brillo.": "Turning the brightness down.",
    "¿Subo o bajo el brillo?": "Should I turn the brightness up or down?",
    "No pude ajustar el brillo en esta pantalla.": "I couldn't adjust the brightness on this screen.",
    "Volumen al máximo.": "Volume at maximum.",
    "Volumen al mínimo.": "Volume at minimum.",
    "Volumen a la mitad.": "Volume at half.",
    "Subiendo volumen.": "Turning the volume up.",
    "Bajando volumen.": "Turning the volume down.",
    "¿Subo o bajo el volumen?": "Should I turn the volume up or down?",
    "Sonido activado.": "Sound on.",
    "Spotify en marcha, señor.": "Spotify is on its way, sir.",
    "Abriendo tu reproductor de música, señor.": "Opening your music player, sir.",
    "No encontré ningún reproductor. Ábrelo una vez y lo recordaré, o elígelo en el menú.":
        "I couldn't find a music player. Open one once and I'll remember it, or pick it in the menu.",
    "No veo ningún reproductor de música abierto.": "I don't see any music player open.",
    "¿Qué canción quieres que ponga?": "Which song should I play?",
    "¿Qué carpeta quieres que reproduzca?": "Which folder should I play?",
    "¿Qué quieres que abra?": "What should I open?",
    "¿Qué quieres que busque?": "What should I search for?",
    "De acuerdo, paso a segundo plano. Llámame por mi nombre cuando me necesites.":
        "Alright, going to the background. Call my name when you need me.",
    "Aquí estoy, señor.": "Here I am, sir.",
    "Entendido. Minimizando todas las ventanas.": "Understood. Minimizing all windows.",
    "Aquí tiene la lista de comandos.": "Here is the list of commands.",
    "Apagando sistemas. Hasta pronto, señor.": "Shutting down. See you soon, sir.",
}
_DIAS_EN = {"lunes": "Monday", "martes": "Tuesday", "miércoles": "Wednesday", "jueves": "Thursday", "viernes": "Friday",
            "sábado": "Saturday", "domingo": "Sunday"}
_MESES_EN = {"enero": "January", "febrero": "February", "marzo": "March", "abril": "April", "mayo": "May",
             "junio": "June", "julio": "July", "agosto": "August", "septiembre": "September", "octubre": "October",
             "noviembre": "November", "diciembre": "December"}


def _hora_en(h, mi):
    return f"It's {h % 12 or 12}:{mi:02d} {'AM' if h < 12 else 'PM'}."


def _ordinal_en(n):
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def _fecha_en(dia, d, mes, anio):
    if dia not in _DIAS_EN or mes not in _MESES_EN:
        return None
    return f"Today is {_DIAS_EN[dia]}, {_MESES_EN[mes]} {_ordinal_en(int(d))}, {anio}."


_RESP_RX = [
    (re.compile(r"^Tiene (\d+) recordatorios? para hoy\.$"), lambda m: f"You have {m.group(1)} reminders for today."),
    (re.compile(r"^Son las (\d{1,2}):(\d{2})\.$"), lambda m: _hora_en(int(m.group(1)), int(m.group(2)))),
    (re.compile(r"^Hoy es (\w+) (\d+) de (\w+) de (\d{4})\.$"), lambda m: _fecha_en(*m.groups())),
    (re.compile(r"^Brillo al (\d+) por ciento\.$"), lambda m: f"Brightness at {m.group(1)} percent."),
    (re.compile(r"^Volumen al (\d+) por ciento\.$"), lambda m: f"Volume at {m.group(1)} percent."),
    (re.compile(r"^Entendido\. He anotado: (.*)$"), lambda m: f"Understood. I noted: {m.group(1)}"),
    (re.compile(r"^Reanudando (.*)\.$"), lambda m: f"Resuming {m.group(1)}."),
    (re.compile(r"^En (.+) suena: (.*)\.$"), lambda m: f"On {m.group(1)}, now playing: {m.group(2)}."),
    (re.compile(r"^No veo qué canción suena en (.*)\.$"), lambda m: f"I can't tell which song is playing in {m.group(1)}."),
    (re.compile(r"^Reproduciendo (.*) en aleatorio\.$"), lambda m: f"Playing {m.group(1)} on shuffle."),
    (re.compile(r"^Reproduciendo (.*?)\.?$"), lambda m: f"Playing {m.group(1)}."),
    (re.compile(r"^La carpeta (.*) no tiene canciones\.$"), lambda m: f"The folder {m.group(1)} has no songs."),
    (re.compile(r"^No encontré (?:una canción|una carpeta) parecida a (.*)\.$"),
     lambda m: f"I couldn't find anything similar to {m.group(1)}."),
    (re.compile(r"^No encontré (.*) en este equipo\.$"), lambda m: f"I couldn't find {m.group(1)} on this computer."),
    (re.compile(r"^Abriendo (.*)\.$"), lambda m: f"Opening {m.group(1)}."),
    (re.compile(r"^Buscando (.*)\.$"), lambda m: f"Searching for {m.group(1)}."),
    (re.compile(r"^(Buenos días|Buenas tardes|Buenas noches), señor\. Iniciando reporte\.$"),
     lambda m: {"Buenos días": "Good morning", "Buenas tardes": "Good afternoon",
                "Buenas noches": "Good evening"}[m.group(1)] + ", sir. Starting your report."),
    (re.compile(r"^Ahora me llamo (.*)\.$"), lambda m: f"My name is now {m.group(1)}."),
]


_RESP_EN.update({
    "Voy a conectar tu cuenta de Spotify. Autoriza en el navegador.": "I'll connect your Spotify account. Please authorize it in the browser.",
    "No pude conectar Spotify.": "I couldn't connect Spotify.",
    "Spotify solo me deja poner música con una cuenta Premium.": "Spotify only lets me play music with a Premium account.",
    "No encuentro Spotify abierto. Ábrelo e inténtalo otra vez.": "I can't find Spotify open. Open it and try again.",
    "Spotify no me dejó ponerla.": "Spotify wouldn't let me play it.",
    "No pude poner esa canción.": "I couldn't play that song.",
})
_RESP_RX[:0] = [
    (re.compile(r"^Reproduciendo (.+) en (Spotify|YouTube Music|YouTube)\.$"), lambda m: f"Playing {m.group(1)} on {m.group(2)}."),
    (re.compile(r"^Abrí la búsqueda de (.+?) en (Spotify|YouTube Music|YouTube)(?:\. Para que la ponga yo, conecta tu cuenta en el menú)?\.$"),
     lambda m: f"I opened the search for {m.group(1)} on {m.group(2)}."
     + (" To let me play it myself, connect your account in the menu." if "conecta" in m.string else "")),
    (re.compile(r"^No encontré (.+) en Spotify\.$"), lambda m: f"I couldn't find {m.group(1)} on Spotify."),
    (re.compile(r"^En (.+) suena: (.*), de (.+)\.$"), lambda m: f"On {m.group(1)}, now playing: {m.group(2)} by {m.group(3)}."),
]


def traducir_respuesta(texto):
    """Respuesta de Alfred en español -> en inglés, o None si no se sabe traducir."""
    t = (texto or "").strip()
    if t in _RESP_EN:
        return _RESP_EN[t]
    if t in _RESP_EN_PC:
        return _RESP_EN_PC[t]
    for rx, fn in _RESP_RX:
        m = rx.match(t)
        if m:
            res = fn(m)
            if res:
                return res
    return None


_EN_PALABRAS = {"the", "and", "to", "of", "in", "is", "for", "on", "with", "my", "your", "call", "buy", "meeting",
                "tomorrow", "today", "at", "this", "that", "you", "we", "please", "send", "email", "pay", "get",
                "take", "bring", "tonight", "morning", "friday", "monday"}
_ES_PALABRAS = {"el", "la", "los", "las", "de", "del", "que", "y", "en", "un", "una", "por", "con", "para", "es", "no",
                "se", "al", "lo", "su", "mi", "mis", "llamar", "comprar", "manana", "hoy", "reunion"}


def parece_ingles(texto):
    """True si el texto (una nota, un recordatorio) parece escrito en inglés: así se lee con la voz inglesa."""
    if re.search(r"[áéíóúñ¿¡ü]", (texto or "").lower()):
        return False
    toks = set(normalizar(texto or "").split())
    en, es = len(toks & _EN_PALABRAS), len(toks & _ES_PALABRAS)
    return en >= 1 and en > es


FRASES_FIJAS = list(_RESP_EN.keys())     # se generan una vez y quedan guardadas: la respuesta es instantánea


def limpiar_para_voz(texto):
    """Quita emojis y símbolos raros para que la voz solo lea texto."""
    t = texto.replace("%", " por ciento ")
    t = re.sub(r"[^\w\s.,;:¿?¡!()'\"-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def trocear_para_voz(texto, largo_max=90, primero_max=60):
    """Frases cortas para Kokoro: mientras suena una, ya se genera la siguiente. Una frase larga se parte por comas,
    así la voz empieza antes. El PRIMER trozo es el que se espera en silencio, así que si pasa de `primero_max`
    letras se corta en su última coma (el resto se genera mientras ya suena el principio)."""
    frases = [f.strip() for f in re.split(r"(?<=[.!?;:])\s+", texto) if f.strip()]
    res = []
    for f in frases:
        if len(f) <= largo_max:
            res.append(f)
            continue
        acum = ""
        for p in re.split(r"(?<=,)\s+", f):
            if acum and len(acum) + len(p) + 1 > largo_max:
                res.append(acum)
                acum = p
            else:
                acum = f"{acum} {p}".strip()
        if acum:
            res.append(acum)
    if res and len(res[0]) > primero_max:
        cortes = [m.end() for m in re.finditer(r",\s", res[0]) if 18 <= m.end() <= primero_max + 1]
        if cortes:
            c = cortes[-1]
            res[0:1] = [res[0][:c].strip(), res[0][c:].strip()]
    return res


def trozos_de_frase(texto):
    """Los trozos EXACTOS con los que Kokoro dice un texto (misma limpieza y mismo troceado que al hablar). La caché
    de frases de siempre se guarda con esta misma clave: así una frase de varias oraciones también suena al instante."""
    return trocear_para_voz(limpiar_para_voz(texto))


def texto_hora(ahora):
    """Lo que Alfred dice al preguntarle la hora (una sola fuente: el comando y la precarga usan este mismo texto)."""
    return f"Son las {ahora:%H:%M}."


_DIAS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
_MESES_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
             "septiembre", "octubre", "noviembre", "diciembre"]


def texto_fecha(ahora):
    """Lo que Alfred dice al preguntarle la fecha (misma fuente para el comando y la precarga)."""
    return f"Hoy es {_DIAS_ES[ahora.weekday()]} {ahora.day} de {_MESES_ES[ahora.month - 1]} de {ahora.year}."


EJEMPLOS_EN = {   # para el manual (ventana «Comandos»): cómo se piden en inglés
    "mostrar": "show yourself", "segundo_plano": "go to the background", "cancion": "play Numb by Linkin Park / play songs by Linkin Park / play Numb on Spotify",
    "recordar": "remind me to call the bank", "trabajo": "let's get to work", "buenos_dias": "good morning",
    "agenda": "show me my agenda / what do I have today", "silencio": "mute / unmute",
    "brillo": "brightness up / brightness to 50", "volumen": "turn the volume down / volume to 30",
    "carpeta_musica": "play the folder rock (on shuffle)", "que_suena": "what's playing",
    "media": "next song / pause / previous song / stop the music", "spotify": "play music",
    "descanso": "minimize everything", "calculadora": "open calculator", "bloc": "open notepad",
    "explorador": "open file explorer", "buscar_web": "search pizza recipes on YouTube",
    "abrir": "open Chrome / open downloads", "hora": "what time is it", "fecha": "what day is it",
    "ayuda": "help", "salir": "goodbye",
}


# ── 3.0 · órdenes en inglés de los comandos nuevos (se traducen a la frase en español que entiende Alfred) ──
def _dur_es(txt):
    """'ten minutes and 30 seconds' -> '10 minutos y 30 segundos' (para temporizadores dichos en inglés)."""
    txt = numeros_en_a_digitos(txt) if "numeros_en_a_digitos" in globals() else txt
    for en, es in ((r"\bhalf an hour\b", "media hora"), (r"\ban hour\b", "1 hora"), (r"\ba minute\b", "1 minuto"),
                   (r"\ba quarter of an hour\b", "un cuarto de hora"), (r"\bhours?\b", "horas"),
                   (r"\bmin(?:ute)?s?\b", "minutos"), (r"\bsec(?:ond)?s?\b", "segundos"), (r"\band a half\b", "y media"),
                   (r"\band\b", "y")):
        txt = re.sub(en, es, txt)
    return txt


_EN_AJUSTES = {"wifi": "wifi", "wi fi": "wifi", "bluetooth": "bluetooth", "sound": "sonido", "audio": "sonido",
               "display": "pantalla", "screen": "pantalla", "monitor": "pantalla", "battery": "bateria",
               "updates": "actualizaciones", "update": "actualizaciones", "windows update": "actualizaciones",
               "apps": "aplicaciones", "applications": "aplicaciones", "privacy": "privacidad",
               "background": "fondo", "theme": "fondo", "personalization": "fondo", "personalisation": "fondo",
               "notifications": "notificaciones", "printers": "impresoras", "storage": "almacenamiento",
               "keyboard": "teclado", "language": "teclado", "mouse": "mouse", "accessibility": "accesibilidad",
               "airplane mode": "modo avion", "night light": "luz nocturna", "network": "wifi", "internet": "wifi"}

_EN_PC_FIJAS = [   # (regex completa, frase en español)
    (r"^(?:copy|copy (?:this|that|it|the text|the selection))$", "copia"),
    (r"^(?:paste|paste (?:here|it|this|the text))$", "pega"),
    (r"^(?:cut|cut (?:this|that|it|the selection))$", "corta"),
    (r"^select all(?: the text)?$", "selecciona todo"),
    (r"^(?:undo|undo (?:that|it|this))$", "deshaz"),
    (r"^(?:redo|redo (?:that|it))$", "rehaz"),
    (r"^(?:save|save (?:it|this|the file|the document|changes|my changes))$", "guarda"),
    (r"^(?:print|print (?:this|it|the document))$", "imprime"),
    (r"^(?:find|search) (?:on|in) (?:the )?(?:page|document)$", "busca en la pagina"),
    (r"^(?:new tab|open (?:a )?new tab)$", "nueva pestana"),
    (r"^close (?:the |this |current )?tab$", "cierra la pestana"),
    (r"^(?:next tab|switch tab|change tab)$", "siguiente pestana"),
    (r"^(?:previous tab|last tab|prior tab)$", "pestana anterior"),
    (r"^reopen (?:the |last |closed )?tab$", "reabre la pestana"),
    (r"^(?:new window|open (?:a )?new window)$", "nueva ventana"),
    (r"^(?:(?:open )?(?:a )?(?:private|incognito)(?: window| mode)?)$", "ventana privada"),
    (r"^(?:refresh|reload)(?: the)?(?: page)?$", "recarga"),
    (r"^(?:page back|browser back|go back a page)$", "ve atras"),
    (r"^(?:page forward|browser forward|go forward)$", "ve adelante"),
    (r"^(?:(?:enter|exit|leave|toggle) )?full ?screen$", "pantalla completa"),
    (r"^zoom in$", "acerca"), (r"^zoom out$", "aleja"), (r"^(?:reset|normal) zoom$", "zoom normal"),
    (r"^(?:press |hit )?(?:enter|return)$", "enter"),
    (r"^(?:press |hit )?(?:escape|esc)$", "escape"),
    (r"^(?:press |hit )?tab(?: key)?$", "tabulador"),
    (r"^(?:press |hit )?(?:space|spacebar|space bar)$", "espacio"),
    (r"^(?:delete|erase|remove)(?: this| that| it| the selection)?$", "borra"),
    (r"^backspace$", "retroceso"),
    (r"^(?:delete|erase) (?:the )?last word$", "borra la ultima palabra"),
    (r"^(?:delete|erase|clear) (?:everything|all|all the text|the text)$", "borra todo"),
    (r"^arrow up$", "flecha arriba"), (r"^arrow down$", "flecha abajo"), (r"^arrow left$", "flecha izquierda"),
    (r"^arrow right$", "flecha derecha"), (r"^page down$", "pagina abajo"), (r"^page up$", "pagina arriba"),
    (r"^go to (?:the )?(?:top|start)(?: of the page)?$", "ve al inicio"),
    (r"^go to (?:the )?(?:bottom|end)(?: of the page)?$", "ve al final"),
    (r"^rename(?: it| this| the file)?$", "renombra"),
    (r"^(?:open )?(?:the )?start menu$", "menu inicio"),
    (r"^(?:open )?(?:windows )?search$", "busca en windows"),
    (r"^(?:open )?(?:the )?notifications$", "centro de notificaciones"),
    (r"^(?:open )?(?:the )?quick settings$", "configuracion rapida"),
    (r"^(?:open )?(?:the )?clipboard history$", "historial del portapapeles"),
    (r"^(?:open )?(?:the )?emoji(?: panel| picker)?$", "abre los emojis"),
    (r"^(?:open )?(?:the )?run(?: dialog| box)?$", "abre ejecutar"),
    (r"^(?:snipping tool|screen snip|snip(?: the screen)?)$", "herramienta de recorte"),
    (r"^(?:record the screen|start recording|stop recording|record screen)$", "graba la pantalla"),
    # ventanas
    (r"^(?:close|exit)(?: the)?(?: this| current| active)?(?: window| app| application| program)$", "cierra la ventana"),
    (r"^close (?:this|it)$", "cierra la ventana"),
    (r"^minimi[sz]e (?:this|the current|current|the active) window$", "minimiza esta ventana"),
    (r"^maximi[sz]e (?:this|the current|current|the active) window$", "maximiza esta ventana"),
    (r"^restore (?:this|the current|current) window$", "restaura esta ventana"),
    (r"^(?:snap|put|move|dock)(?: this| the)? window (?:to )?(?:the )?left$", "ventana a la izquierda"),
    (r"^(?:snap|put|move|dock)(?: this| the)? window (?:to )?(?:the )?right$", "ventana a la derecha"),
    (r"^(?:move|send)(?: this| the)? window to (?:the )?other (?:monitor|screen)$", "ventana al otro monitor"),
    (r"^(?:(?:switch|change|cycle)(?: the)? windows?|alt tab|next window|other window)$", "cambia de ventana"),
    (r"^(?:task view|show (?:all )?(?:the )?windows|window overview)$", "vista de tareas"),
    (r"^(?:new|create(?: a)? new) (?:virtual )?desktop$", "escritorio nuevo"),
    (r"^(?:next|switch to the next) (?:virtual )?desktop$", "siguiente escritorio"),
    (r"^(?:previous|last|switch to the previous) (?:virtual )?desktop$", "escritorio anterior"),
    (r"^(?:what|which) (?:windows|apps|applications|programs) (?:do i have |are )?open$", "que ventanas tengo abiertas"),
    (r"^list (?:the )?(?:open )?(?:windows|apps)$", "que ventanas tengo abiertas"),
    # energía y pantalla
    (r"^lock(?: the| my)?(?: computer| pc| screen| laptop| machine| workstation| it)?$", "bloquea la pantalla"),
    (r"^(?:put (?:the |my )?(?:computer|pc|laptop) to sleep|sleep(?: the)?(?: computer| pc| laptop)?|suspend(?: the)?(?: computer| pc)?)$",
     "suspende el equipo"),
    (r"^hibernate(?: the)?(?: computer| pc| laptop)?$", "hiberna el equipo"),
    (r"^(?:restart|reboot)(?: the| my)?(?: computer| pc| laptop| machine| system)?$", "reinicia la computadora"),
    (r"^(?:sign out|log out|logout|log off)(?: of)?(?: windows| my account)?$", "cierra la sesion"),
    (r"^(?:cancel|abort|stop|cancel the) (?:the )?(?:shutdown|restart|reboot)$", "cancela el apagado"),
    (r"^do not shut down$", "cancela el apagado"),
    (r"^(?:turn|switch|shut) off (?:the |my )?(?:screen|monitor|display)$", "apaga la pantalla"),
    (r"^(?:turn|switch) on (?:the |my )?(?:screen|monitor|display)$|^wake (?:up )?(?:the )?(?:screen|monitor|display)$",
     "enciende la pantalla"),
    # ratón
    (r"^(?:(?:left )?click|click (?:here|it)|click on it)$", "clic"),
    (r"^double ?-?click(?: here| it)?$", "doble clic"),
    (r"^right ?-?click(?: here| it)?$", "clic derecho"),
    (r"^center (?:the )?(?:mouse|cursor|pointer)$", "centra el mouse"),
    (r"^(?:(?:show|open|activate|start|turn on)(?: the)? (?:mouse )?grid|mouse grid|control (?:the )?mouse)$", "cuadricula"),
    # captura
    (r"^(?:take (?:a )?)?(?:screenshot|screen ?shot|screen capture|capture(?: the)? screen)$", "captura de pantalla"),
    (r"^(?:take (?:a )?)?(?:screenshot|screen capture|capture) of (?:the |this |current )?window$", "captura de la ventana"),
    # sistema
    (r"^(?:what is |how is )?(?:my |the )?battery(?: level| status| left| life)?$|^how much battery(?: do i have| is left)?$",
     "cuanta bateria tengo"),
    (r"^(?:cpu|processor) (?:usage|load)$|^how is the (?:cpu|processor)$", "uso de cpu"),
    (r"^(?:ram|memory) usage$|^how much (?:memory|ram)(?: do i have| is (?:free|left|used))?$", "uso de memoria"),
    (r"^(?:disk|storage|drive) space$|^how much (?:disk |storage |drive )?space(?: do i have| is left)?$",
     "espacio en disco"),
    (r"^what(?: is|s)? (?:using|consuming|eating|taking) (?:the )?(?:most )?(?:cpu|memory|ram|resources)$|^top processes$",
     "que consume mas"),
    (r"^(?:am i connected(?: to the internet)?|do i have internet|internet status|is the internet working|is there internet)$",
     "estoy conectado a internet"),
    (r"^(?:what|which) wi ?fi(?: am i (?:on|connected to))?$|^wi ?fi name$", "a que wifi estoy conectado"),
    (r"^(?:what is )?my ip(?: address)?$", "cual es mi ip"),
    (r"^uptime$|^how long has (?:the |my )?(?:computer|pc|laptop) been (?:on|running)$", "cuanto tiempo lleva encendida"),
    (r"^(?:system|computer|pc) (?:status|report|health)$|^how is (?:the|my) (?:computer|pc|system)$", "estado del sistema"),
    (r"^(?:disconnect|turn off|switch off)(?: from)?(?: the| my)? wi ?fi$", "desconecta el wifi"),
    (r"^(?:connect|reconnect|turn on|switch on)(?: to)?(?: the| my)? wi ?fi$", "conecta el wifi"),
    (r"^(?:turn on |enable |activate |switch on )?airplane mode$", "modo avion"),
    (r"^(?:turn on |enable |activate |switch on )?night light$", "luz nocturna"),
    # herramientas
    (r"^open (?:the )?(?:task manager|taskmgr)$|^task manager$", "abre el administrador de tareas"),
    (r"^(?:open )?(?:the )?(?:command prompt|cmd)$", "abre el simbolo del sistema"),
    (r"^(?:open )?power ?shell$", "abre powershell"),
    (r"^(?:open )?(?:the )?control panel$", "abre el panel de control"),
    (r"^(?:open )?(?:the )?device manager$", "abre el administrador de dispositivos"),
    (r"^(?:open )?(?:the )?system information$", "abre la informacion del sistema"),
    (r"^(?:open )?(?:the )?event viewer$", "abre el visor de eventos"),
    (r"^(?:open )?(?:the )?disk management$", "abre la administracion de discos"),
    (r"^(?:open )?(?:the )?resource monitor$", "abre el monitor de recursos"),
    (r"^(?:open )?(?:the )?(?:recycle bin|trash|trash can)$", "abre la papelera"),
    (r"^(?:empty|clear) (?:the )?(?:recycle bin|trash|trash can)$", "vacia la papelera"),
    (r"^(?:turn on |enable |switch to |activate )?dark (?:mode|theme)$", "modo oscuro"),
    (r"^(?:turn on |enable |switch to |activate )?light (?:mode|theme)$", "modo claro"),
    (r"^(?:toggle|change|switch)(?: the)? (?:theme|dark mode)$", "cambia el tema"),
    (r"^(?:read|what is in|what is on|read out|read aloud)(?: the| my)? clipboard(?: out loud| aloud)?$|^what did i copy$",
     "lee el portapapeles"),
    (r"^(?:clear|empty)(?: the| my)? clipboard$", "borra el portapapeles"),
    # temporizadores
    (r"^(?:how much time(?: is)? left|time left|how long(?: is)? left|timer status|how long until the (?:timer|alarm))$",
     "cuanto falta"),
    (r"^(?:what|which) (?:timers|alarms) do i have$|^list (?:my )?(?:timers|alarms)$", "que alarmas tengo"),
    (r"^(?:cancel|stop|delete|clear)(?: the| my)? (?:timer|alarm)$", "cancela el temporizador"),
    (r"^(?:cancel|stop|delete|clear)(?: the| my)?(?: all)?(?: of)?(?: the| my)? (?:timers|alarms|all timers|all alarms)$",
     "cancela las alarmas"),
    # dictado
    (r"^(?:start|begin|enable|turn on)(?: the)? dictation$|^dictation(?: mode)?$|^dictate$|^start dictating$",
     "empieza a dictar"),
    (r"^(?:stop|end|finish|disable|turn off)(?: the)? dictation$|^stop dictating$", "deja de dictar"),
    (r"^(?:empty|clear) clipboard$", "borra el portapapeles"),
]
_EN_PC_FIJAS = [(re.compile(p), es) for p, es in _EN_PC_FIJAS]

_EN_OP = ((r"\bsquare root of\b", "raiz cuadrada de"), (r"\bpercent of\b", "por ciento de"),
          (r"\bto the power of\b", "elevado a"), (r"\bmultiplied by\b", "por"), (r"\bdivided by\b", "entre"),
          (r"\bsquared\b", "al cuadrado"), (r"\bcubed\b", "al cubo"), (r"\bplus\b", "mas"), (r"\bminus\b", "menos"),
          (r"\btimes\b", "por"), (r"\bover\b", "entre"), (r"\bpoint\b", "punto"))


def _traducir_pc_en(t, numeros):
    """Reglas de los comandos de control del PC (inglés -> español). `t` ya viene normalizada. None si no encaja."""
    for rx, es in _EN_PC_FIJAS:
        if rx.match(t):
            return es
    # apagar el equipo (con o sin tiempo)
    mm = re.match(r"^(?:shut ?down|power off|turn off|switch off)(?: the| my)? (?:computer|pc|laptop|machine|system)"
                  r"(?: in (.+))?$", t)
    if mm:
        return "apaga la computadora" + (" en " + _dur_es(mm.group(1)) if mm.group(1) else "")
    mm = re.match(r"^(?:restart|reboot)(?: the| my)?(?: computer| pc| laptop| machine| system)? in (.+)$", t)
    if mm:
        return "reinicia la computadora en " + _dur_es(mm.group(1))
    # desplazarse y mover el ratón
    mm = re.match(r"^scroll (down|up)(?: (a little|a bit|a lot))?$", t)
    if mm:
        return ("baja" if mm.group(1) == "down" else "sube") + " la pagina" + \
               {"a little": " un poco", "a bit": " un poco", "a lot": " mucho"}.get(mm.group(2), "")
    mm = re.match(r"^(?:move|put) (?:the )?(?:mouse|cursor|pointer)(?: to the| to)? (left|right|up|down)"
                  r"(?: (a little|a bit|a lot))?$", t)
    if mm:
        return "mueve el mouse a " + {"left": "la izquierda", "right": "la derecha", "up": "arriba", "down": "abajo"}[
            mm.group(1)] + {"a little": " un poco", "a bit": " un poco", "a lot": " mucho"}.get(mm.group(2), "")
    # ajustes de Windows por tema
    mm = re.match(r"^(?:open|show|go to|launch)(?: the| my)?(?: windows)? (?:(.+?) )?settings(?: (?:for|of|page|menu))?"
                  r"(?: (.+))?$", t)
    if mm:
        tema = (mm.group(1) or mm.group(2) or "").strip()
        return "abre la configuracion" + (" de " + _EN_AJUSTES[tema] if tema in _EN_AJUSTES else "")
    # cambiar de ventana / cerrar programa
    mm = re.match(r"^(?:switch|change|go) to (?:the )?(.+?)(?: window)?$", t)
    if mm and not re.search(r"\b(?:song|track|music|next|previous|background|tray|desktop|dark|light)\b", mm.group(1)):
        return "cambia a " + mm.group(1)
    mm = re.match(r"^(?:close|quit|exit|kill) (?:the |my )?(.+?)(?: window| app| application| program)?$", t)
    if mm and mm.group(1) not in ("assistant", "alfred", "yourself", "it", "this", "tab", "window"):
        verbo = "fuerza el cierre de " if t.startswith(("kill", "force")) else "cierra "
        return verbo + mm.group(1)
    mm = re.match(r"^force (?:close|quit) (?:the |my )?(.+)$", t)
    if mm:
        return "fuerza el cierre de " + mm.group(1)
    # temporizadores y alarmas
    mm = re.match(r"^(?:set|start|create|make)(?: an?)? (?:timer|alarm)(?: for| in)? (.+)$", t)
    if mm:
        g = numeros(mm.group(1))
        hora = re.match(r"^(?:for |at )?(\d{1,2})(?: (\d{2}))?(?: ?(am|pm))?$", g)
        if "alarm" in t and hora:
            h, mi, ap = int(hora.group(1)), hora.group(2), hora.group(3)
            return f"pon una alarma a las {h}" + (f" {mi}" if mi else "") + \
                   (" de la tarde" if ap == "pm" else " de la manana" if ap == "am" else "")
        return "pon un temporizador de " + _dur_es(g)
    mm = re.match(r"^(?:remind|alert|notify|tell|wake) me in (.+?)(?: to (.+))?$", t)
    if mm:
        return "avisame en " + _dur_es(numeros(mm.group(1))) + (" de " + mm.group(2) if mm.group(2) else "")
    # escribir
    mm = re.match(r"^(?:type|write)(?: down)?(?: this| the following| the text| out)? (.+)$", t)
    if mm and not t.startswith("write down"):
        return "escribe " + mm.group(1)
    # calculadora
    mm = re.match(r"^(?:what is|how much is|calculate|compute|what is the result of)(?: the result of)? (.+)$", t)
    if mm and re.search(r"\b(?:plus|minus|times|multiplied by|divided by|over|to the power of|squared|cubed|percent of|"
                        r"square root of)\b", mm.group(1)):
        g = numeros(mm.group(1))
        for en, es in _EN_OP:
            g = re.sub(en, es, g)
        return "cuanto es " + g
    return None


EJEMPLOS_EN.update({
    "ventana": "maximize this window / snap window to the left / what windows do I have open",
    "bloquear": "lock the computer", "suspender": "put the computer to sleep", "hibernar": "hibernate",
    "apagar_pc": "shut down the computer / shut down the computer in 30 minutes", "reiniciar_pc": "restart the computer",
    "cerrar_sesion": "sign out", "cancelar_apagado": "cancel shutdown", "pantalla": "turn off the screen",
    "temporizador": "set a timer for 10 minutes / set an alarm for 7 30 am / how much time is left",
    "calcular": "what is 25 times 4 / what is 20 percent of 50", "escribir": "type hello comma how are you",
    "dictado": "start dictation … end dictation", "atajo": "copy / paste / save / new tab / refresh / press enter",
    "cerrar": "close the window / close chrome", "cambiar_a": "switch to chrome",
    "raton": "click / double click / right click / scroll down / move the mouse to the left",
    "cuadricula": "show the mouse grid … five … click", "captura": "take a screenshot",
    "configuracion": "open bluetooth settings", "herramientas": "open the task manager",
    "estado_pc": "what is my battery / cpu usage / disk space / am I connected", "wifi": "disconnect wifi",
    "tema": "dark mode", "portapapeles": "read the clipboard", "papelera": "empty the recycle bin",
})



# ══════════════════════════════════════════════════════════════════════════════
#  2.9: PUERTA DE VOZ, HUELLA DE VOZ Y COMPRENSIÓN SEMÁNTICA (partes puras)
# ══════════════════════════════════════════════════════════════════════════════
class PuertaVoz:
    """
    Puerta de voz (detector de actividad ligero): solo deja pasar al reconocedor el audio que tiene voz, con un poco
    de audio previo (para no comerse el inicio de la primera palabra) y un poco de silencio final (para que el
    reconocedor cierre la frase). Mientras no hay voz devuelve [] y el reconocedor no trabaja. Al terminar de hablar,
    o si la frase dura demasiado (ruido continuo), pide cerrar la frase.
    Cada bloque dura 0,1 s: previos=3 (0,3 s antes), cola=10 (1 s de silencio para cerrar), maximo=120 (12 s).
    """

    def __init__(self, previos=3, cola=10, maximo=120):
        self.previos_n, self.cola_n, self.maximo = previos, cola, maximo
        self.reiniciar()

    def reiniciar(self):
        self.abierta = False
        self.previos = deque(maxlen=self.previos_n)
        self.silencio = 0
        self.n = 0

    def procesar(self, hay_voz, bloque):
        """-> (bloques que deben ir al reconocedor, cerrar_frase)."""
        if not self.abierta:
            if hay_voz:
                self.abierta, self.silencio = True, 0
                feed = list(self.previos) + [bloque]
                self.previos.clear()
                self.n = len(feed)
                return feed, False
            self.previos.append(bloque)
            return [], False
        self.n += 1
        self.silencio = 0 if hay_voz else self.silencio + 1
        if self.silencio >= self.cola_n or self.n >= self.maximo:
            self.abierta = False
            self.previos.clear()
            return [bloque], True
        return [bloque], False


def distancia_coseno(a, b):
    """0 = misma voz, ~1 = nada que ver. Con huellas vacías o nulas devuelve 1."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 1.0
    return float(1.0 - np.dot(a, b) / (na * nb))


def centro_huellas(huellas):
    """Huella media (normalizada) de varias muestras de la misma voz."""
    m = [np.asarray(h, dtype=np.float64) / (float(np.linalg.norm(h)) or 1.0) for h in huellas]
    c = np.mean(m, axis=0)
    return (c / (float(np.linalg.norm(c)) or 1.0)).tolist()


def umbral_huella(huellas, centro):
    """(umbral, [distancia de cada muestra al centro]). El umbral deja margen sobre lo que varía TU voz."""
    ds = [distancia_coseno(h, centro) for h in huellas]
    return float(min(0.60, max(0.35, 1.4 * max(ds) + 0.05))), ds


def localizar_spk(ruta):
    """Carpeta real del modelo de huella de voz de Vosk (acepta una subcarpeta anidada), o None."""
    def valida(c):
        return os.path.isfile(os.path.join(c, "mfcc.conf")) and os.path.isfile(os.path.join(c, "final.ext.raw"))
    if not os.path.isdir(ruta):
        return None
    if valida(ruta):
        return ruta
    for nombre in os.listdir(ruta):
        sub = os.path.join(ruta, nombre)
        if os.path.isdir(sub) and valida(sub):
            return sub
    return None


# (id de comando, orden canónica que ese comando entiende, frases de ejemplo con otras palabras)
INTENCIONES = [
    ("volumen", "sube el volumen", ["sube el volumen", "no se escucha nada", "no oigo bien", "ponlo más fuerte",
                                     "más volumen por favor", "necesito que se escuche más", "aumenta el sonido"]),
    ("volumen", "baja el volumen", ["baja el volumen", "está muy fuerte", "está muy alto el sonido", "ponlo más bajito",
                                     "menos volumen", "me molesta el ruido", "reduce el sonido"]),
    ("brillo", "sube el brillo", ["sube el brillo", "la pantalla está muy oscura", "no veo bien la pantalla",
                                   "más luz en la pantalla", "aumenta el brillo"]),
    ("brillo", "baja el brillo", ["baja el brillo", "la pantalla está muy clara", "me lastima la luz de la pantalla",
                                   "menos brillo", "oscurece la pantalla"]),
    ("silencio", "silencio", ["silencio", "calla todo", "mutea la computadora", "que no suene nada",
                               "quita todo el sonido"]),
    ("silencio", "activa el sonido", ["activa el sonido", "devuelve el sonido", "ya puedes poner el sonido",
                                       "quita el silencio"]),
    ("media", "pausa", ["pausa la música", "detén un momento la canción", "espera un momento con la música",
                         "pon pausa"]),
    ("media", "siguiente cancion", ["siguiente canción", "cambia de canción", "esta no me gusta pon otra",
                                     "pasa a la que sigue"]),
    ("media", "cancion anterior", ["canción anterior", "regresa a la canción de antes", "pon la que sonaba antes"]),
    ("que_suena", "que suena", ["qué canción es esta", "cómo se llama lo que suena", "qué estoy escuchando"]),
    ("hora", "que hora es", ["qué hora es", "dime la hora", "me dices la hora", "tienes la hora", "qué horas son"]),
    ("fecha", "que dia es", ["qué día es hoy", "a qué fecha estamos", "dime la fecha", "en qué día vivimos"]),
    ("agenda", "que tengo hoy", ["qué tengo pendiente hoy", "qué tengo que hacer hoy", "léeme mis pendientes",
                                  "tengo algo agendado"]),
    ("descanso", "minimiza todo", ["quita todas las ventanas", "despeja la pantalla", "muéstrame el escritorio",
                                    "quiero ver el escritorio"]),
    ("calculadora", "calculadora", ["necesito hacer una cuenta", "quiero calcular algo", "abre la calculadora"]),
    ("bloc", "bloc de notas", ["quiero escribir algo rápido", "necesito tomar apuntes", "abre el bloc de notas"]),
    ("explorador", "explorador", ["quiero ver mis archivos", "abre mis carpetas", "abre el explorador de archivos"]),
    ("trabajo", "vamos a trabajar", ["es hora de ponerse a trabajar", "empecemos con el trabajo",
                                      "ya es hora de chambear"]),
    ("ayuda", "ayuda", ["qué puedes hacer", "necesito ayuda", "qué comandos tienes", "para qué sirves"]),
    ("mostrar", "muestrate", ["aparece en la pantalla", "quiero ver tu ventana", "sal de la bandeja"]),
    ("segundo_plano", "segundo plano", ["pasa a segundo plano", "ocúltate un rato", "quítate de en medio"]),
    ("bloquear", "bloquea la pantalla", ["voy a alejarme un momento", "protege mi computadora", "que nadie vea mi pantalla"]),
    ("captura", "captura de pantalla", ["guarda lo que se ve en la pantalla", "toma una foto de lo que tengo abierto"]),
    ("estado_pc", "cuanta bateria tengo", ["cuánta carga le queda a la laptop", "me estoy quedando sin batería",
                                            "cómo anda la computadora"]),
    ("pantalla", "apaga la pantalla", ["apaga el monitor un rato", "ya no necesito ver la pantalla"]),
    ("tema", "modo oscuro", ["la pantalla me deslumbra", "pon todo en negro", "quiero el tema oscuro"]),
]


class ComprensionSemantica:
    """
    Entiende órdenes dichas con OTRAS palabras comparando su significado (embeddings multilingües, offline tras la
    primera descarga) con frases de ejemplo de cada comando. Solo da respuesta si el parecido es alto Y hay margen
    sobre el comando siguiente: es preferible «no tengo ese comando» a ejecutar algo equivocado.
    """

    def __init__(self, ruta_cache, nombre_modelo=None):
        self.ruta_cache = ruta_cache
        self.nombre = nombre_modelo or MODELO_SEMANTICO
        self.modelo = None
        self.matriz = None
        self.destinos = []              # (id_comando, orden_canonica) por cada frase de ejemplo

    @property
    def listo(self):
        return self.modelo is not None and self.matriz is not None

    def cargar(self):
        from fastembed import TextEmbedding
        self.modelo = TextEmbedding(model_name=self.nombre, cache_dir=self.ruta_cache)
        frases, self.destinos = [], []
        for cmd_id, canon, ejemplos in INTENCIONES:
            for f in ejemplos:
                frases.append(f)
                self.destinos.append((cmd_id, canon))
        self.matriz = self._embed(frases)
        return len(frases)

    def _embed(self, textos):
        v = np.array(list(self.modelo.embed(list(textos))), dtype=np.float32)
        n = np.linalg.norm(v, axis=1, keepdims=True)
        n[n == 0] = 1.0
        return v / n

    def buscar(self, texto, umbral=0.74, margen=0.05):
        """(id_comando, orden_canonica o None, parecido) o None. Si dos órdenes del MISMO comando (p. ej. subir y bajar
        el volumen) quedan casi empatadas, devuelve canónica None: se usa lo que dijiste, que el comando sabe leer."""
        if not self.listo or not (texto or "").strip():
            return None
        q = self._embed([texto])[0]
        sims = self.matriz @ q
        mejor = {}
        for s, d in zip(sims.tolist(), self.destinos):
            if s > mejor.get(d, -1.0):
                mejor[d] = s
        orden = sorted(mejor.items(), key=lambda kv: -kv[1])
        (d1, s1) = orden[0]
        if s1 < umbral:
            return None
        otros = [s for (d, s) in orden[1:] if d[0] != d1[0]]
        if s1 - (max(otros) if otros else 0.0) < margen:
            return None
        mismos = [s for (d, s) in orden[1:] if d[0] == d1[0]]
        canon = d1[1] if (not mismos or s1 - max(mismos) >= 0.03) else None
        return d1[0], canon, float(s1)


# ══════════════════════════════ FIN LÓGICA PURA ═══════════════════════════════

class AmplificadorVoz:
    """
    Ganancia automática para el reconocimiento: sube el volumen de la voz suave hasta un nivel cómodo para Vosk.
    Sube rápido cuando hablas bajito, baja de inmediato si hablas fuerte (no satura) y nunca amplifica tanto
    como para convertir el ruido de fondo en voz. Solo afecta al reconocimiento; los aplausos usan el audio original.
    """

    def __init__(self, ganancia_max=8.0, objetivo=0.09):
        self.ganancia_max = max(1.0, float(ganancia_max))
        self.objetivo = objetivo          # nivel RMS al que se intenta llevar la voz (0-1)
        self.reiniciar()

    def reiniciar(self):
        self.ganancia = 1.0
        self.ruido = 0.004                # estimación del ruido de fondo (RMS)
        self.hay_voz = False              # ¿el último bloque tiene algo claramente por encima del ruido?

    def procesar(self, data):
        a = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        if a.size == 0:
            self.hay_voz = False
            return data
        rms = float(np.sqrt((a * a).mean()))
        if rms <= 1e-6:
            self.hay_voz = False
            return data
        # ruido de fondo: baja rápido, sube muy despacio (para no confundir la voz con ruido)
        if rms < self.ruido:
            self.ruido = 0.8 * self.ruido + 0.2 * rms
        else:
            self.ruido = min(self.ruido * 1.01, rms)
        self.ruido = max(self.ruido, 0.0005)
        self.hay_voz = rms > max(1.8 * self.ruido, 0.003)      # umbral de la puerta de voz (más sensible que el de la ganancia)
        if self.ganancia_max <= 1.0:
            return data
        # tope: el ruido de fondo amplificado no debe pasar de ~0.02
        tope = max(1.0, min(self.ganancia_max, 0.02 / self.ruido))
        if rms > max(2.5 * self.ruido, 0.004):                 # hay voz (o algo claramente sobre el ruido)
            deseada = min(tope, max(1.0, self.objetivo / rms))
            if deseada < self.ganancia:
                self.ganancia = deseada                                # baja al instante: evita saturar
            else:
                self.ganancia += (deseada - self.ganancia) * 0.25     # sube con suavidad
        else:
            self.ganancia = min(self.ganancia, tope)                  # en silencio se mantiene (sin pasar el tope)
        if self.ganancia <= 1.001:
            return data
        out = np.clip(a * self.ganancia, -1.0, 1.0)
        return (out * 32767.0).astype(np.int16).tobytes()


# ══════════════════════════════════════════════════════════════════════════════
#  MICRÓFONO: prueba todos los dispositivos de entrada y se recupera sola
# ══════════════════════════════════════════════════════════════════════════════
def reiniciar_portaudio():
    """Vuelve a leer los dispositivos de audio (sirve si el micrófono se activó/conectó después de abrir Alfred)."""
    try:
        sd._terminate()
        sd._initialize()
    except Exception:
        logging.exception("No pude reiniciar PortAudio")


def memoria_total_gb():
    """RAM total del equipo en GB (Windows) o None si no se puede saber."""
    try:
        class _Mem(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = _Mem()
        m.dwLength = ctypes.sizeof(_Mem)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
            return m.ullTotalPhys / float(2 ** 30)
    except Exception:
        logging.exception("No pude leer la memoria del equipo")
    return None


def candidatos_microfono(preferido):
    """[(indice|None, nombre, extra_settings)] en el orden en que conviene probarlos."""
    lista = []
    if preferido is not None:
        lista.append((preferido, f"elegido en el menú ({preferido})", None))
    lista.append((None, "predeterminado de Windows", None))
    try:
        apis = sd.query_hostapis()
        rango = {"mme": 0, "windows directsound": 1, "windows wasapi": 2}
        extra = []
        for i, d in enumerate(sd.query_devices()):
            if d["max_input_channels"] < 1:
                continue
            api = apis[d["hostapi"]]["name"].lower()
            if api not in rango:                                   # se descartan WDM-KS y similares
                continue
            nombre = d["name"]
            malo = any(x in nombre.lower() for x in ("stereo mix", "mezcla est", "loopback"))
            ajustes = None
            if api == "windows wasapi":
                try:
                    ajustes = sd.WasapiSettings(auto_convert=True)  # deja que Windows convierta a 16 kHz
                except Exception:
                    ajustes = None
            extra.append((malo, rango[api], i, f"{i}: {nombre} ({apis[d['hostapi']]['name']})", ajustes))
        for _, _, i, nombre, ajustes in sorted(extra, key=lambda e: e[:3]):
            lista.append((i, nombre, ajustes))
    except Exception:
        logging.exception("No pude listar los micrófonos")
    return lista


def ruta_ascii(ruta, nombre="AlfredModelo", marca="am"):
    """Vosk (en Windows) no abre modelos en rutas con acentos/ñ (p. ej. C:\\Users\\José). Si hace falta, usa una copia."""
    try:
        ruta.encode("ascii")
        return ruta
    except UnicodeEncodeError:
        pass
    destino = os.path.join(datos_dir(), "modelos", nombre)       # privada (permisos solo tuyos), nunca C:\Users\Public
    try:
        if not os.path.exists(os.path.join(destino, marca)):
            shutil.rmtree(destino, ignore_errors=True)
            shutil.copytree(ruta, destino)
        logging.info("Modelo copiado a una ruta sin acentos: %s", destino)
        return destino
    except Exception:
        logging.exception("No pude copiar el modelo a una ruta sin acentos")
        return ruta



# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════
CONFIG_BASE = {
    "palabra_activacion": "alfred, alfredo, al fred",   # la primera es el nombre; las demás, formas alternativas
    "ciudad": "",                # ej. "Tuxtla Gutierrez": activa el clima en "buenos días"
    "youtube": "https://www.youtube.com/watch?v=hEIexwwiKKU",
    "navegador": "Opera GX",     # navegador para abrir YouTube al trabajar (vacío = predeterminado)
    "carpeta_proyecto": "",      # carpeta que abre Cursor (opcional)
    "clap_activo": False,
    "aplauso_umbral": 0.12,      # lo ajusta el botón «Calibrar aplausos»
    "velocidad_voz": 190,
    "voz_ia": True,              # voz neuronal offline (Kokoro o Piper); si no está instalada se usa la de Windows
    "voz_ia_modelo": "kokoro-ef_dora",
    "reproductor": "",           # reproductor de música preferido (vacío = el que Alfred detecte abierto)
    "carpetas_musica": "",       # carpetas extra con música, separadas por «;»
    "plataforma_musica": "",     # 3.2.1: vacío = tu biblioteca; «spotify», «youtube music» o «youtube» = «reproduce X» usa esa plataforma
    "spotify_client_id": "",     # 3.2.1: Client ID de tu app en developer.spotify.com (cuenta Premium)
    "spotify_refresh": "",       # 3.2.1: lo rellena Alfred al conectar Spotify
    "voz_kokoro_ofrecida": False,   # se pasa una sola vez de Piper a Kokoro (con permiso)
    "voz_ia_rechazada": False,   # dijiste que no a descargarla (se puede activar en ☰ Menú → Voz)
    "voz_preferida": "",         # texto del nombre de una voz instalada, ej. "Sabina"
    "microfono": None,           # índice o nombre; None = el predeterminado
    "ganancia_mic": 8,           # ganancia máxima (×) de la amplificación automática de la voz; 1 = sin amplificar
    "ventana_espera": 7,
    "idioma_en": True,           # entiende también inglés (descarga un modelo de ~40 MB con permiso)
    "en_ofrecido": False,        # ya se te ofreció descargar el inglés (una sola vez)
    "responder_ingles": True,    # si le hablas en inglés, contesta en inglés (voz Kokoro)
    "kokoro_residente": True,    # Kokoro se queda cargado en memoria: responde sin esperas
    "kokoro_prever": True,       # en reposo deja ya generadas la hora y la fecha: «qué hora es» suena al instante
    "kokoro_ligero": False,      # modelo Kokoro de 88 MB: genera más rápido, con algo menos de fidelidad
    "rutas": {},                 # opcional, forzar una app: {"cursor": "C:\\...\\Cursor.exe"}
    "apps_encontradas": {},      # caché automática de la búsqueda de apps
    "puerta_voz": True,          # el reconocedor solo trabaja mientras hay voz (ahorra CPU y cierra bien las frases)
    "modelo_alta_precision": False,   # usa el Vosk grande en español si está descargado
    "modelo_grande_probando": False,  # marca interna: si Alfred se cerró al cargarlo, la próxima vez no lo usa
    "solo_mi_voz": False,        # solo obedece a la voz registrada
    "huella_voz": None,          # huella (x-vector) de tu voz
    "huella_umbral": 0.45,       # distancia máxima aceptada: menor = más exigente
    "huella_muestras": 0,
    "comprension_semantica": False,   # entiende órdenes con otras palabras (fastembed)
    "semantica_umbral": 0.74,    # parecido mínimo (0-1): mayor = más prudente
    "retardo_apagado": 20,       # segundos de margen para «cancela el apagado»
    "aviso_bateria": True,       # avisa por voz si la batería baja y no hay cargador
    "bateria_minima": 20,        # porcentaje a partir del cual avisa (a 10 % avisa otra vez)
    "idioma_dictado": "es",      # idioma del modo dictado: "es" o "en"
    "wifi_ultimo": "",           # última red Wi-Fi conectada (para «conecta el Wi-Fi»)
}


class Config:
    def __init__(self):
        self.datos = json.loads(json.dumps(CONFIG_BASE))
        try:
            with open(ARCHIVO_CONFIG, encoding="utf-8") as f:
                guardado = json.load(f)
            for k in ("rutas", "apps_encontradas"):
                self.datos[k].update(guardado.pop(k, {}) or {})
            self.datos.update(guardado)
        except FileNotFoundError:
            pass
        except Exception:
            logging.exception("Config ilegible, uso valores por defecto")
        self.guardar()

    def get(self, clave):
        return self.datos.get(clave)

    def set(self, clave, valor):
        self.datos[clave] = valor
        self.guardar()

    def get_secreto(self, clave):
        """Un token o clave guardado con DPAPI. Si estaba en claro (versiones anteriores) se cifra al leerlo."""
        v = self.datos.get(clave) or ""
        if v and os.name == "nt" and not str(v).startswith("dpapi:"):
            self.set_secreto(clave, v)
        return revelar_secreto(v) if str(v).startswith("dpapi:") else v

    def set_secreto(self, clave, valor):
        self.set(clave, proteger_secreto(valor) if valor else "")

    def guardar(self):
        try:
            with open(ARCHIVO_CONFIG, "w", encoding="utf-8") as f:
                json.dump(self.datos, f, indent=2, ensure_ascii=False)
        except Exception:
            logging.exception("No se pudo guardar la config")


# ══════════════════════════════════════════════════════════════════════════════
#  BUSCADOR AUTOMÁTICO DE APLICACIONES
# ══════════════════════════════════════════════════════════════════════════════
class BuscadorApps:
    """Encuentra solo dónde está una app por su nombre. Resultado: ('exe', ruta) | ('lnk', ruta) | ('shell', AppID)."""

    def __init__(self, cfg, log):
        self.cfg, self.log = cfg, log
        self._lock = threading.RLock()
        self._startapps = None

    def _ps(self, script, timeout=25):
        try:
            r = subprocess.run([ruta_sistema("powershell"), "-NoProfile", "-NonInteractive", "-Command",
                                "[Console]::OutputEncoding=[Text.Encoding]::UTF8; " + script],
                               stdin=subprocess.DEVNULL, capture_output=True, timeout=timeout,
                               creationflags=SIN_VENTANA)
            return r.stdout.decode("utf-8", "replace").strip()
        except Exception:
            logging.exception("PowerShell falló")
            return ""

    def resolver(self, nombre):
        clave = normalizar(nombre)
        if not clave:
            return None
        with self._lock:
            directa = expandir(nombre)
            if os.path.exists(directa):
                return ("exe" if directa.lower().endswith(".exe") else "lnk", directa)
            manual = {normalizar(k): v for k, v in self.cfg.get("rutas").items() if v}.get(clave)
            if manual and os.path.exists(expandir(manual)):
                return ("exe", expandir(manual))
            guardada = self.cfg.get("apps_encontradas").get(clave)
            if guardada and (guardada[0] == "shell" or os.path.exists(guardada[1])):
                return tuple(guardada)
            for metodo in (self._registro, self._path, self._menu_inicio, self._escanear, self._start_apps):
                try:
                    res = metodo(clave)
                except Exception:
                    logging.exception("Búsqueda de app (%s)", metodo.__name__)
                    res = None
                if res:
                    self.cfg.get("apps_encontradas")[clave] = list(res)
                    self.cfg.guardar()
                    return res
            return None

    def lanzar(self, nombre, *args):
        res = self.resolver(nombre)
        if not res:
            return False
        tipo, ruta = res
        if tipo == "exe":
            subprocess.Popen([ruta, *args], cwd=os.path.dirname(ruta) or None)
        elif tipo == "lnk":
            os.startfile(ruta)
        else:
            subprocess.Popen([ruta_sistema("explorer"), "shell:AppsFolder\\" + ruta])
        return True

    def _registro(self, clave):
        exe = clave.replace(" ", "") + ".exe"
        for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            try:
                with winreg.OpenKey(hive, rf"Software\Microsoft\Windows\CurrentVersion\App Paths\{exe}") as k:
                    ruta = winreg.QueryValue(k, None).strip('"')
                    if os.path.exists(ruta):
                        return ("exe", ruta)
            except OSError:
                pass
        return None

    def _path(self, clave):
        p = shutil.which(clave.replace(" ", "") + ".exe")
        return ("exe", p) if p else None

    def _menu_inicio(self, clave):
        bases = [os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
                 os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs")]
        hallados = []
        for base in bases:
            for raiz, _, archivos in os.walk(base):
                for a in archivos:
                    if a.lower().endswith(".lnk"):
                        nombre = a[:-4]
                        if coincide_nombre(clave, nombre) and not EXCLUIR_LNK.search(nombre):
                            hallados.append((puntuar_nombre(clave, nombre), os.path.join(raiz, a)))
        if not hallados:
            return None
        lnk = sorted(hallados)[0][1]
        destino = self._ps("(New-Object -ComObject WScript.Shell).CreateShortcut('"
                           + lnk.replace("'", "''") + "').TargetPath")
        if destino.lower().endswith(".exe") and os.path.exists(destino):
            return ("exe", destino)
        return ("lnk", lnk)

    def _exes(self, carpeta, profundidad=2):
        salida, base = [], carpeta.rstrip("\\/").count(os.sep)
        for raiz, dirs, archivos in os.walk(carpeta):
            if raiz.count(os.sep) - base >= profundidad:
                dirs[:] = []
            salida += [os.path.join(raiz, a) for a in archivos if a.lower().endswith(".exe")]
        return salida

    def _escanear(self, clave):
        e = os.environ
        local = e.get("LOCALAPPDATA", "")
        raices = [local + r"\Programs", local, e.get("APPDATA", ""), e.get("ProgramFiles", ""),
                  e.get("ProgramFiles(x86)", "")]
        for raiz in raices:
            if not raiz or not os.path.isdir(raiz):
                continue
            try:
                entradas = list(os.scandir(raiz))
            except OSError:
                continue
            for ent in entradas:
                if ent.is_dir() and coincide_nombre(clave, ent.name):
                    elegido = elegir_exe(self._exes(ent.path), clave)
                    if elegido:
                        return ("exe", elegido)
        return None

    def _start_apps(self, clave):
        if self._startapps is None:
            txt = self._ps("Get-StartApps | Select-Object Name,AppID | ConvertTo-Json -Compress")
            try:
                datos = json.loads(txt) if txt else []
            except ValueError:
                datos = []
            self._startapps = [datos] if isinstance(datos, dict) else datos
        cands = sorted((puntuar_nombre(clave, d["Name"]), d["AppID"]) for d in self._startapps
                       if coincide_nombre(clave, d["Name"]))
        return ("shell", cands[0][1]) if cands else None


# ══════════════════════════════════════════════════════════════════════════════
#  INICIO CON WINDOWS E INSTANCIA ÚNICA
# ══════════════════════════════════════════════════════════════════════════════
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APROBADO_KEY = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"


def _pythonw():
    """pythonw.exe con el que Windows abrirá Alfred al iniciar sesión (sin consola). Evita rutas que Windows no deja
    lanzar desde el registro, como la carpeta interna de la Microsoft Store (Program Files\\WindowsApps): ahí usa el
    alias que la Store crea en %LOCALAPPDATA%\\Microsoft\\WindowsApps."""
    candidatos = []
    for exe in (sys.executable, getattr(sys, "_base_executable", None) or ""):
        bajo = exe.lower()
        if bajo.endswith("pythonw.exe"):
            candidatos.append(exe)
        elif bajo.endswith("python.exe"):
            candidatos.append(exe[:-10] + "pythonw.exe")
    local = os.environ.get("LOCALAPPDATA")
    for c in candidatos:
        if "\\program files\\windowsapps\\" in c.lower() and local:
            alias = os.path.join(local, "Microsoft", "WindowsApps", "pythonw.exe")
            if os.path.exists(alias):
                return alias
    for c in candidatos:
        if os.path.exists(c):
            return c
    return sys.executable


def comando_autostart():
    """Orden que Windows ejecuta al iniciar sesión. --inicio-windows hace que Alfred espere a que el escritorio y el
    micrófono estén listos (al iniciar sesión tardan) y que avise en la bandeja cuando ya escucha."""
    return f'"{_pythonw()}" "{os.path.abspath(__file__)}" --oculto --inicio-windows'


def _valores_run():
    res = {}
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            i = 0
            while True:
                try:
                    nombre, valor, _ = winreg.EnumValue(k, i)
                except OSError:
                    break
                res[nombre] = valor
                i += 1
    except OSError:
        pass
    return res


def _rutas_de_comando(cmd):
    """'"C:\\Python\\pythonw.exe" "D:\\Alfred\\alfred.pyw" --oculto' -> (programa, script)."""
    m = re.match(r'^\s*"([^"]+)"\s*(?:"([^"]+)")?', cmd or "")
    return (m.group(1), m.group(2)) if m else (None, None)


def desactivado_por_windows():
    """El Administrador de tareas (pestaña Inicio) puede desactivar una entrada SIN borrarla del registro: sigue
    «existiendo» pero Windows no la ejecuta. Es una causa típica de «el inicio automático no funciona»."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, APROBADO_KEY) as k:
            datos = bytes(winreg.QueryValueEx(k, NOMBRE_REGISTRO)[0])
        return bool(datos) and datos[0] & 1 == 1
    except (OSError, TypeError):
        return False


def estado_autostart():
    cmd = _valores_run().get(NOMBRE_REGISTRO)
    est = {"registrado": cmd is not None, "comando": cmd, "problema": "", "reparable": False}
    if cmd is None:
        return est
    exe, script = _rutas_de_comando(cmd)
    yo = os.path.normcase(os.path.abspath(__file__))
    if not exe or not os.path.exists(exe):
        est["problema"], est["reparable"] = f"Python ya no está en «{exe}»", True
    elif "\\program files\\windowsapps\\" in exe.lower() and os.path.normcase(_pythonw()) != os.path.normcase(exe):
        est["problema"], est["reparable"] = "usaba la ruta interna de Python de la Microsoft Store (Windows no la abre)", True
    elif not script or not os.path.exists(script):
        est["problema"], est["reparable"] = (
            f"apuntaba a un archivo que ya no existe ({os.path.basename(script or '?')})", True)
    elif os.path.normcase(os.path.abspath(script)) != yo:
        if (os.path.dirname(os.path.normcase(os.path.abspath(script))) == os.path.dirname(yo)
                and os.path.basename(script).lower().startswith("alfred")):
            est["problema"], est["reparable"] = f"apuntaba a otra versión ({os.path.basename(script)})", True
    elif "--inicio-windows" not in cmd:
        est["problema"], est["reparable"] = "usaba la orden de arranque antigua", True
    if not est["problema"] and desactivado_por_windows():
        est["problema"] = "Windows lo tiene desactivado (Administrador de tareas → Inicio)"
    return est


def autostart_activo():
    return estado_autostart()["registrado"]


def _quitar_desactivado():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, APROBADO_KEY, 0, winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, NOMBRE_REGISTRO)
    except OSError:
        pass


def configurar_autostart(activar):
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        if activar:
            winreg.SetValueEx(k, NOMBRE_REGISTRO, 0, winreg.REG_SZ, comando_autostart())
        else:
            try:
                winreg.DeleteValue(k, NOMBRE_REGISTRO)
            except FileNotFoundError:
                pass
    if activar:
        _quitar_desactivado()                  # si Windows la tenía desactivada, vuelve a quedar activa
    else:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, APROBADO_KEY, 0, winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, NOMBRE_REGISTRO)
        except OSError:
            pass


def limpiar_inicios_antiguos():
    """Borra entradas de versiones anteriores (con otro nombre en el registro) que arrancan un Alfred que ya no existe."""
    n = 0
    for nombre, valor in _valores_run().items():
        if nombre == NOMBRE_REGISTRO:
            continue
        _, script = _rutas_de_comando(valor)
        if (script and script.lower().endswith((".pyw", ".py")) and os.path.basename(script).lower().startswith("alfred")
                and not os.path.exists(script)):
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
                    winreg.DeleteValue(k, nombre)
                n += 1
            except OSError:
                logging.exception("No pude borrar la entrada de inicio antigua %s", nombre)
    return n


def arreglar_inicio_con_windows():
    """Al abrir Alfred: si el inicio con Windows quedó roto (archivo renombrado, Python movido…) lo repara. Devuelve el
    aviso para mostrar en el registro ('' si todo está bien o no estaba activado)."""
    try:
        viejos = limpiar_inicios_antiguos()
        est = estado_autostart()
        if (est["registrado"] and est["reparable"]) or (viejos and not est["registrado"]):
            configurar_autostart(True)
            logging.info("Inicio con Windows reparado: %s", est["problema"] or "entrada antigua")
            return "🚀 Reparé el inicio automático con Windows (" + (est["problema"] or "había una entrada antigua") + ")."
        if est["registrado"] and est["problema"]:
            return "⚠️ Inicio automático: " + est["problema"] + ". Actívalo de nuevo en ☰ Menú → General."
    except Exception:
        logging.exception("Revisión del inicio con Windows")
    return ""


def esperar_barra_tareas(maximo=240):
    """Al iniciar sesión Windows tarda en tener barra de tareas. El icono de la bandeja necesita esperarla, pero ya NO
    bloquea el arranque: se espera en un hilo aparte."""
    t0 = time.time()
    try:
        u = ctypes.windll.user32
        while time.time() - t0 < maximo and not u.FindWindowW("Shell_TrayWnd", None):
            time.sleep(1)
    except Exception:
        logging.exception("Espera de la barra de tareas")
    logging.info("⏱️ Arranque: barra de tareas lista a los %.0f s", time.time() - T_INICIO)


def esperar_audio_listo(activo, estado=lambda t: None, libre=lambda: True, maximo=240):
    """Espera (en el hilo de audio, con la ventana ya visible) a que Windows entregue algún micrófono: al iniciar
    sesión el servicio de audio tarda. Reintenta cada 2 s volviendo a leer los dispositivos. True si apareció."""
    t0, avisado = time.time(), False
    while activo() and time.time() - t0 < maximo:
        try:
            if any(d["max_input_channels"] > 0 for d in sd.query_devices()):
                logging.info("⏱️ Arranque: micrófono visible a los %.0f s", time.time() - T_INICIO)
                return True
        except Exception:
            pass
        if not avisado:
            avisado = True
            estado("🟡 Esperando al micrófono de Windows…")
        if libre():
            reiniciar_portaudio()
        time.sleep(2)
    return False


def esperar_escucha(extra=0.0, maximo=420):
    """Al arrancar con Windows, las cargas pesadas que no hacen falta para escuchar (voz Kokoro, inglés, semántica…)
    esperan a que el micrófono ya esté escuchando: así Alfred queda listo antes y no compite con Windows por disco y CPU."""
    if EN_ARRANQUE and not EVT_ESCUCHANDO.is_set():
        EVT_ESCUCHANDO.wait(maximo)
    if extra:
        time.sleep(extra)


_TOKEN_INSTANCIA = [None]


def _archivo_token_instancia():
    return os.path.join(datos_dir(), "instancia.tok")


def instancia_unica():
    """Socket-candado, o None si ya hay otro Alfred (se le pide mostrarse). Tras «Reiniciar» espera al anterior.
    Quien pide «mostrar» debe presentar un token efímero guardado en la carpeta privada del usuario: otro programa o
    usuario del equipo que solo vea el puerto 47653 no puede manejar la ventana."""
    intentos = 20 if "--reiniciado" in sys.argv else 1
    for i in range(intentos):
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", PUERTO_INSTANCIA))
            s.listen(2)
            try:
                tok = secrets.token_hex(16)
                with open(_archivo_token_instancia(), "w", encoding="ascii") as f:
                    f.write(tok)
                _TOKEN_INSTANCIA[0] = tok
            except OSError:
                logging.exception("No pude guardar el token de instancia única")
            return s
        except OSError:
            s.close()
            if i < intentos - 1:
                time.sleep(0.25)
    if EN_ARRANQUE:                                  # arrancó con Windows y ya hay otro Alfred: no molestar con la ventana
        logging.info("Inicio con Windows: ya hay otro Alfred abierto, me cierro sin mostrar nada")
        return None
    try:
        try:
            with open(_archivo_token_instancia(), encoding="ascii") as f:
                tok = f.read().strip()
        except OSError:
            tok = ""
        c = socket.create_connection(("127.0.0.1", PUERTO_INSTANCIA), timeout=1)
        c.sendall(b"mostrar:" + tok.encode("ascii", "ignore"))
        c.close()
    except OSError:
        pass
    return None


def servidor_instancia(srv, gui):
    while True:
        try:
            conn, _ = srv.accept()
        except OSError:
            return
        try:
            conn.settimeout(2.0)                     # un cliente mudo no puede dejar el servidor colgado
            dato = conn.recv(64)
            esperado = b"mostrar:" + (_TOKEN_INSTANCIA[0] or "").encode("ascii")
            if _TOKEN_INSTANCIA[0] and hmac.compare_digest(dato, esperado):
                gui.ui(gui.mostrar)
            else:
                logging.warning("Instancia única: petición rechazada (token ausente o incorrecto)")
        except OSError:
            pass
        finally:
            conn.close()


# ══════════════════════════════════════════════════════════════════════════════
#  VOZ: SAPI directo → PowerShell. Hilo propio; el micrófono se ignora mientras habla.
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
#  VOZ CON IA OFFLINE (Piper, https://github.com/rhasspy/piper): proceso residente, gratis y sin límites
# ══════════════════════════════════════════════════════════════════════════════
def bajar_archivo(url, destino, progreso=None, sha256=None):
    """Descarga por HTTPS con requests y comprueba su SHA-256 ANTES de dejarla en su sitio: el .part se verifica y solo
    entonces se mueve; si el hash (o el tamaño) no cuadra se borra el temporal, se registra el error y se lanza
    ValueError. progreso(hecho, total) como máximo ~8 veces por segundo. Devuelve 'fijado' | 'recordado' | 'nuevo'."""
    if not str(url).lower().startswith("https://"):
        raise ValueError("Solo se descarga por HTTPS")
    parcial = destino + ".part"
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    ultimo, hecho, total, h = 0.0, 0, 0, hashlib.sha256()
    try:
        with requests.get(url, stream=True, timeout=30, headers={"User-Agent": "Alfred"}) as r:
            r.raise_for_status()
            if not str(r.url).lower().startswith("https://"):
                raise ValueError("La descarga se redirigió a una dirección sin cifrar")
            comprimido = bool(r.headers.get("content-encoding"))
            total = int(r.headers.get("content-length", 0))
            with open(parcial, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    f.write(chunk)
                    h.update(chunk)
                    hecho += len(chunk)
                    if progreso and time.time() - ultimo > 0.12:
                        ultimo = time.time()
                        progreso(hecho, total)
        if total and not comprimido and hecho != total:
            raise ValueError(f"Descarga incompleta ({hecho} de {total} bytes)")
        estado = comprobar_hash_descarga(url, os.path.basename(destino), h.hexdigest(), sha256)
    except BaseException as e:
        try:
            os.remove(parcial)                     # nunca queda un temporal dudoso
        except OSError:
            pass
        logging.error("Descarga descartada (%s): %s", os.path.basename(destino), e)
        raise
    if progreso:
        progreso(hecho, total or hecho)
    os.replace(parcial, destino)
    return estado


class MotorPiper:
    """Mantiene piper.exe cargado (habla rápido) y lo cierra tras 2 min sin usarse (no gasta RAM en reposo)."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.p = None
        self.lock = threading.Lock()
        self.activa = None
        self.ultimo = time.time()
        self.tmp = os.path.join(VOZ_IA_DIR, "tmp")

    @staticmethod
    def ruta_exe():
        return os.path.join(VOZ_IA_DIR, "piper", "piper.exe")

    def modelo_id(self):
        m = self.cfg.get("voz_ia_modelo")
        return m if m in VOCES_IA and VOCES_IA[m].get("motor", "piper") == "piper" else PIPER_PREDETERMINADA

    def ruta_modelo(self, mid=None):
        return os.path.join(VOZ_IA_DIR, "voces", (mid or self.modelo_id()) + ".onnx")

    def instalado(self, mid=None):
        m = self.ruta_modelo(mid)
        return all(os.path.exists(x) for x in (self.ruta_exe(), m, m + ".json"))

    def _escala(self):
        try:
            vel = int(self.cfg.get("velocidad_voz") or 190)
        except (TypeError, ValueError):
            vel = 190
        return round(max(0.7, min(1.5, 190.0 / max(vel, 1))), 2)    # 190 = velocidad natural

    def _comando(self, mid, escala):
        return [self.ruta_exe(), "--model", self.ruta_modelo(mid), "--output_dir", self.tmp,
                "--length_scale", str(escala), "--sentence_silence", "0.1", "--quiet"]

    def _arrancar(self):
        self.cerrar()
        os.makedirs(self.tmp, exist_ok=True)
        for f in glob.glob(os.path.join(self.tmp, "*.wav")):
            try:
                os.remove(f)
            except OSError:
                pass
        mid, esc = self.modelo_id(), self._escala()
        self.p = subprocess.Popen(self._comando(mid, esc), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, cwd=os.path.dirname(self.ruta_exe()),
                                  creationflags=SIN_VENTANA)
        threading.Thread(target=self._drenar, args=(self.p,), daemon=True).start()
        self.activa = (mid, esc)

    @staticmethod
    def _drenar(p):
        try:
            for _ in p.stdout:        # que el pipe de salida nunca se llene
                pass
        except Exception:
            pass

    def _esperar_wav(self, antes, limite):
        fin, ultimo_tam = time.time() + limite, -1
        while time.time() < fin:
            if self.p.poll() is not None:
                raise RuntimeError("Piper se cerró inesperadamente")
            nuevos = set(glob.glob(os.path.join(self.tmp, "*.wav"))) - antes
            if nuevos:
                ruta = max(nuevos, key=os.path.getmtime)
                tam = os.path.getsize(ruta)
                if tam > 44 and tam == ultimo_tam:      # el archivo ya terminó de escribirse
                    return ruta
                ultimo_tam = tam
            time.sleep(0.05)
        raise TimeoutError("Piper no generó audio a tiempo")

    def hablar(self, texto, idioma="es"):
        texto = limpiar_para_voz(texto)
        if not texto:
            return
        with self.lock:
            if self.p is None or self.p.poll() is not None or self.activa != (self.modelo_id(), self._escala()):
                self._arrancar()
            antes = set(glob.glob(os.path.join(self.tmp, "*.wav")))
            self.p.stdin.write((texto + "\n").encode("utf-8"))
            self.p.stdin.flush()
            ruta = self._esperar_wav(antes, 40)           # la 1.ª vez incluye cargar el modelo
            self.ultimo = time.time()
        try:
            self.reproducir(ruta)
        finally:
            try:
                os.remove(ruta)
            except OSError:
                pass

    def reproducir(self, ruta):
        if winsound is None:
            raise RuntimeError("winsound no disponible")
        winsound.PlaySound(ruta, winsound.SND_FILENAME)    # síncrono

    def cerrar(self):
        p, self.p = self.p, None
        if p is None:
            return
        try:
            p.stdin.close()
        except Exception:
            pass
        try:
            p.terminate()
        except Exception:
            pass

    def cerrar_si_inactivo(self, segundos=120):
        if self.p is not None and time.time() - self.ultimo > segundos and self.lock.acquire(blocking=False):
            try:
                self.cerrar()
            finally:
                self.lock.release()


class MotorKokoro:
    """Kokoro-82M (ONNX Runtime, https://github.com/thewh1teagle/kokoro-onnx): voz neuronal offline, gratis y sin
    límites, bastante más natural que Piper. Habla español e inglés.
    Sin retraso: el modelo se queda cargado y calentado, las frases de siempre («Diga», «Entendido»…) se generan una
    vez y quedan guardadas (suenan al instante), el audio sale por un único flujo (sin archivos temporales ni cortes)
    y mientras suena un trozo ya se está generando el siguiente (la primera frase larga se parte por comas)."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.k = None
        self._ruta_cargada = None
        self.lock = threading.Lock()
        self.ultimo = time.time()
        self.acento = "es-419"          # español latino (la «c» y la «z» suenan como «s»); si no existe, usa «es»
        self.tmp = os.path.join(VOZ_IA_DIR, "tmp_kokoro")
        self.cache_dir = os.path.join(VOZ_IA_DIR, "cache_kokoro")
        self.cache = OrderedDict()      # clave -> (muestras float32, frecuencia)
        self._cache_lock = threading.Lock()
        self.fijas = set()              # frases que se guardan también en disco (las de siempre)

    def ruta_modelo(self, mid=None):
        ligero = os.path.join(VOZ_IA_DIR, "kokoro", KOKORO_LIGERO)
        if self.cfg.get("kokoro_ligero") and os.path.exists(ligero):
            return ligero
        return os.path.join(VOZ_IA_DIR, "kokoro", KOKORO_MODELO)

    @staticmethod
    def ruta_voces():
        return os.path.join(VOZ_IA_DIR, "kokoro", KOKORO_VOCES)

    def modelo_id(self):
        m = self.cfg.get("voz_ia_modelo")
        return m if m in VOCES_IA and VOCES_IA[m].get("motor") == "kokoro" else KOKORO_PREDETERMINADA

    def instalado(self, mid=None):
        return (importlib.util.find_spec("kokoro_onnx") is not None
                and os.path.exists(self.ruta_modelo()) and os.path.exists(self.ruta_voces()))

    def _velocidad(self):
        try:
            vel = int(self.cfg.get("velocidad_voz") or 190)
        except (TypeError, ValueError):
            vel = 190
        return round(max(0.7, min(1.4, vel / 190.0)), 2)         # 190 = velocidad natural

    def cargar(self):
        """Carga el modelo (tarda 1-3 s la primera vez). Llamar con self.lock tomado."""
        if self.k is None:
            from kokoro_onnx import Kokoro
            self._ruta_cargada = self.ruta_modelo()
            self.k = Kokoro(self._ruta_cargada, self.ruta_voces())
        return self.k

    def recargar_si_cambio(self):
        """Si cambió el modelo (normal <-> ligero) lo suelta para cargar el nuevo. Cambiar de voz no hace falta."""
        if self.k is not None and self._ruta_cargada != self.ruta_modelo():
            self.k = None

    def _voz_idioma(self, idioma):
        """(voz, acento) según el idioma en que se habla."""
        datos = VOCES_IA[self.modelo_id()]
        if idioma == "en":
            return datos.get("voz_en", "af_heart"), "en-us"
        return datos["voz"], self.acento

    def _sintetizar(self, texto, voz, vel, lang):
        k = self.cargar()
        try:
            return k.create(texto, voice=voz, speed=vel, lang=lang)
        except Exception:
            if lang != self.acento or self.acento == "es":
                raise
            logging.exception("Kokoro: el acento %s no funcionó, uso «es»", self.acento)
            self.acento = "es"
            return k.create(texto, voice=voz, speed=vel, lang="es")

    def _clave(self, texto, voz, vel, lang):
        base = f"{os.path.basename(self.ruta_modelo())}|{voz}|{vel}|{lang}|{texto}"
        return hashlib.sha1(base.encode("utf-8")).hexdigest()[:24]

    def _recordar(self, clave, res):
        with self._cache_lock:
            self.cache[clave] = res
            self.cache.move_to_end(clave)
            while len(self.cache) > 160:
                self.cache.popitem(last=False)

    def _audio(self, texto, voz, vel, lang):
        """(muestras, frecuencia) de un trozo de texto: de la memoria, del disco (frases de siempre) o generado ahora."""
        clave = self._clave(texto, voz, vel, lang)
        with self._cache_lock:
            hit = self.cache.get(clave)
            if hit is not None:
                self.cache.move_to_end(clave)
        if hit is not None:
            return hit
        ruta = os.path.join(self.cache_dir, clave + ".npz")
        if os.path.exists(ruta):
            try:
                d = np.load(ruta)
                res = (d["m"].astype(np.float32) / 32767.0, int(d["sr"]))
                self._recordar(clave, res)
                return res
            except Exception:
                logging.exception("Kokoro: caché ilegible, la regenero")
        t0 = time.perf_counter()
        with self.lock:
            muestras, sr = self._sintetizar(texto, voz, vel, lang)
        res = (np.asarray(muestras, dtype=np.float32), int(sr))
        logging.info("Kokoro: frase de %d caracteres generada en %.2f s (no estaba en la caché)", len(texto), time.perf_counter() - t0)
        self._recordar(clave, res)
        if texto in self.fijas:
            try:
                os.makedirs(self.cache_dir, exist_ok=True)
                np.savez(ruta, m=(np.clip(res[0], -1.0, 1.0) * 32767).astype(np.int16), sr=res[1])
            except Exception:
                logging.exception("Kokoro: no pude guardar la frase en la caché")
        return res

    def precalentar(self, frases, parar=lambda: False):
        """Carga y calienta el modelo y deja listas las frases de siempre [(texto, idioma)]. Cede el paso si Alfred habla."""
        with self.lock:
            self.cargar()
        preparados = 0
        for texto, idioma in frases:
            for trozo in trozos_de_frase(texto):         # la clave de la caché es el TROZO (como al hablar)
                while parar():
                    time.sleep(0.5)
                try:
                    voz, lang = self._voz_idioma(idioma)
                    self._audio(trozo, voz, self._velocidad(), lang)
                    preparados += 1
                except Exception:
                    logging.exception("Kokoro: no pude preparar «%s»", trozo)
                    return
                time.sleep(0.1)
        logging.info("Kokoro listo: modelo cargado y %d trozos de frases preparados", preparados)

    def asegurar(self, texto, idioma="es"):
        """Deja en memoria (no en disco) el audio de un texto que se dirá pronto (la hora, la fecha). True si hubo que
        generarlo. Cede el paso: si Alfred habla o piensa, no estorba."""
        voz, lang = self._voz_idioma(idioma)
        vel = self._velocidad()
        hecho = False
        for trozo in trozos_de_frase(texto):
            clave = self._clave(trozo, voz, vel, lang)
            with self._cache_lock:
                if clave in self.cache:
                    continue
            self._audio(trozo, voz, vel, lang)
            hecho = True
        return hecho

    @staticmethod
    def _guardar_wav(muestras, sr, ruta):
        import wave
        pcm = (np.clip(muestras, -1.0, 1.0) * 32767).astype(np.int16)
        with wave.open(ruta, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(int(sr))
            w.writeframes(pcm.tobytes())

    def hablar(self, texto, idioma="es"):
        texto = limpiar_para_voz(texto)
        if not texto:
            return
        trozos = trocear_para_voz(texto)
        voz, lang = self._voz_idioma(idioma)
        vel = self._velocidad()
        cola = queue.Queue(maxsize=3)

        def productor():
            try:
                for tr in trozos:
                    cola.put(self._audio(tr, voz, vel, lang))
            except Exception as e:
                cola.put(e)
            finally:
                cola.put(None)

        threading.Thread(target=productor, daemon=True).start()
        estado = {"st": None, "sr": None, "fallo": False}
        t_ini = time.perf_counter()
        self._abrir_salida(estado)                      # mientras se genera el primer trozo, el audio ya se va abriendo
        error, dichas = None, 0
        try:
            while True:                                 # siempre se vacía la cola hasta el final
                try:
                    item = cola.get(timeout=30)
                except queue.Empty:
                    error = RuntimeError("Kokoro no respondió en 30 s")
                    break
                if item is None:
                    break
                if isinstance(item, Exception):
                    error = item
                    continue
                if error is not None:
                    continue
                if dichas == 0:
                    logging.info("Kokoro: primer sonido a los %.2f s", time.perf_counter() - t_ini)
                try:
                    self._tocar(estado, item[0], item[1])
                    dichas += 1
                except Exception as e:
                    error = e
        finally:
            self._cerrar_salida(estado)
        self.ultimo = time.time()
        if error is not None:
            if dichas == 0:
                raise error                             # no sonó nada: que Voz use el respaldo
            logging.error("Kokoro se interrumpió a mitad del mensaje: %s", error)

    # ── salida de audio: un solo flujo para todo el mensaje (sin archivos ni huecos entre trozos) ──
    @staticmethod
    def _abrir_salida(estado, sr=24000):
        try:
            st = sd.OutputStream(samplerate=sr, channels=1, dtype="float32", latency="low")
            st.start()
            estado["st"], estado["sr"] = st, sr
        except Exception:
            logging.exception("No pude abrir la salida de audio directa; uso winsound")
            estado["fallo"] = True

    @staticmethod
    def _cerrar_salida(estado):
        st, estado["st"] = estado.get("st"), None
        if st is None:
            return
        try:
            if estado.get("sr"):
                st.write(np.zeros((int(estado["sr"] * 0.12), 1), dtype=np.float32))   # respiro final: no se corta la última sílaba
            st.stop()                                   # espera a que termine de sonar lo que quede
            st.close()
        except Exception:
            logging.exception("Cerrando la salida de audio")

    def _tocar(self, estado, muestras, sr):
        if not estado["fallo"]:
            try:
                if estado["st"] is not None and estado["sr"] != sr:
                    self._cerrar_salida(estado)
                if estado["st"] is None:
                    self._abrir_salida(estado, sr)
                if estado["st"] is not None:
                    estado["st"].write(np.ascontiguousarray(muestras, dtype=np.float32).reshape(-1, 1))
                    return
            except Exception:
                logging.exception("La salida de audio directa falló; uso winsound")
                estado["fallo"] = True
                self._cerrar_salida(estado)
        os.makedirs(self.tmp, exist_ok=True)               # respaldo: archivo WAV + winsound
        ruta = os.path.join(self.tmp, f"k_{time.time_ns()}.wav")
        self._guardar_wav(muestras, sr, ruta)
        try:
            self.reproducir(ruta)
        finally:
            try:
                os.remove(ruta)
            except OSError:
                pass

    @staticmethod
    def reproducir(ruta):
        if winsound is None:
            raise RuntimeError("winsound no disponible")
        winsound.PlaySound(ruta, winsound.SND_FILENAME)    # síncrono

    def cerrar(self):
        self.k = None                                      # libera la memoria del modelo

    def cerrar_si_inactivo(self, segundos=300):
        if self.cfg.get("kokoro_residente") is not False:  # por defecto se queda cargado: responde sin esperas
            return
        if self.k is not None and time.time() - self.ultimo > segundos and self.lock.acquire(blocking=False):
            try:
                self.k = None
            finally:
                self.lock.release()


class Voz:
    def __init__(self, gui, cfg):
        self.gui, self.cfg = gui, cfg
        self.q = queue.Queue()
        self._lock = threading.Lock()
        self._pend = 0
        self._fin = 0.0
        self._desde = 0.0
        self._usar_ps = False
        self.voces = []
        self._pref_aplicada = None
        self.idioma, self.idioma_hasta = "es", 0.0     # idioma en que se te contesta (el último que usaste)
        self.piper = MotorPiper(cfg)
        self.kokoro = MotorKokoro(cfg)
        self.kokoro.fijas = {tr for t, _ in self.frases_fijas(True) for tr in trozos_de_frase(t)}
        self._pre_lock = threading.Lock()
        self._ia_fallos = 0
        self._ia_off = False
        self._privados = set()                       # textos que se dicen sin dejar rastro en los registros
        threading.Thread(target=self._run, daemon=True).start()
        threading.Thread(target=self._precalentar_kokoro, daemon=True).start()
        threading.Thread(target=self._bucle_prever, daemon=True).start()

    def motor_ia(self, mid=None):
        """Motor (Kokoro o Piper) que corresponde a la voz IA elegida."""
        mid = mid or self.cfg.get("voz_ia_modelo")
        return self.kokoro if VOCES_IA.get(mid, {}).get("motor") == "kokoro" else self.piper

    def frases_fijas(self, todas=False):
        """[(texto, idioma)] de las frases que Alfred dice siempre: se generan una vez y suenan al instante."""
        res = [(t, "es") for t in FRASES_FIJAS]
        if todas or (self.cfg.get("idioma_en") and self.cfg.get("responder_ingles") is not False):
            res += [(_RESP_EN[t], "en") for t in FRASES_FIJAS]
        return res

    def fijar_idioma(self, idioma):
        """Alfred contesta en el idioma en que le hablaste, durante 90 s; después vuelve al español."""
        self.idioma = idioma
        self.idioma_hasta = time.time() + (90 if idioma == "en" else 0)

    def idioma_actual(self):
        return "en" if self.idioma == "en" and time.time() < self.idioma_hasta else "es"

    def _precalentar_kokoro(self):
        """Carga Kokoro al arrancar, lo calienta y deja listas las frases de siempre: la primera respuesta no tarda."""
        esperar_escucha(6)                                # con Windows: primero el micrófono, luego la voz bonita
        if not self._pre_lock.acquire(blocking=False):
            return
        try:
            if self.cfg.get("voz_ia") and self.motor_ia() is self.kokoro and self.kokoro.instalado():
                self.kokoro.precalentar(self.frases_fijas(), self.ocupada)
        except Exception:
            logging.exception("No se pudo precargar Kokoro")
        finally:
            self._pre_lock.release()

    def _bucle_prever(self):
        """En reposo deja ya generadas la hora (este minuto y el siguiente) y la fecha de hoy: «Alfred, qué hora es» suena
        al instante en vez de esperar a que Kokoro la genere. Gasta ~1 generación por minuto; se apaga con
        «kokoro_prever»: false en alfred_config.json."""
        esperar_escucha(25)                               # que antes termine de calentar las frases de siempre
        while True:
            time.sleep(20)
            try:
                self._prever_una_vez()
            except Exception:
                logging.exception("Precarga de la hora")

    def _prever_una_vez(self):
        if (self.cfg.get("kokoro_prever") is False or not self.cfg.get("voz_ia") or self._ia_off
                or self.motor_ia() is not self.kokoro or not self.kokoro.instalado()
                or self._pre_lock.locked() or self.kokoro.k is None):
            return
        ahora = datetime.datetime.now()
        textos = [texto_hora(ahora), texto_hora(ahora + datetime.timedelta(minutes=1)), texto_fecha(ahora)]
        idiomas = ["es"]
        if self.cfg.get("idioma_en") and self.cfg.get("responder_ingles") is not False:
            idiomas.append("en")
        for texto in textos:
            for idioma in idiomas:
                if self.ocupada():                        # Alfred va a hablar o está hablando: no estorbar
                    return
                dicho = texto if idioma == "es" else traducir_respuesta(texto)
                if dicho:
                    self.kokoro.asegurar(dicho, idioma)

    def reactivar_ia(self):
        """Tras cambiar de voz IA, instalarla o activar el interruptor: vuelve a intentarlo."""
        self._ia_off = False
        self._ia_fallos = 0
        self.piper.cerrar()
        self.kokoro.recargar_si_cambio()
        threading.Thread(target=self._precalentar_kokoro, daemon=True).start()

    def decir(self, texto, esperar=False, privado=False):
        """privado=True: el texto (portapapeles, notas) se dice pero no se escribe en alfred.log ni en el bus remoto."""
        ev = threading.Event()
        with self._lock:
            if privado:
                self._privados.add(texto)
            if self._pend == 0:
                self._desde = time.time()
            self._pend += 1
        self.q.put((texto, ev, self.idioma_actual()))
        if esperar:
            ev.wait(timeout=45)

    def ocupada(self):
        with self._lock:
            atascada = self._pend > 0 and (time.time() - self._desde) > 45
            if atascada:
                self._pend = 0
                self._fin = 0.0
                self._desde = time.time()
        if atascada:
            logging.error("La voz llevaba más de 45 s sin terminar: la doy por atascada y arranco otra")
            self.gui.log("⚠️ La voz se quedó atascada; la reinicio para que Alfred vuelva a escuchar.")
            threading.Thread(target=self._run, daemon=True).start()
            return False
        with self._lock:
            return self._pend > 0 or (time.time() - self._fin) < 0.8

    def _rate(self):
        return max(-10, min(10, (int(self.cfg.get("velocidad_voz")) - 170) // 10))

    def _crear_sapi(self):
        import comtypes
        import comtypes.client
        try:
            comtypes.CoInitialize()
        except OSError:
            pass
        sp = comtypes.client.CreateObject("SAPI.SpVoice")
        self._elegir_voz(sp)
        sp.Volume = 100
        return sp

    def _elegir_voz(self, sp):
        """Voz preferida (Menú → Voz) o, si no hay, la primera en español. Guarda la lista para el menú."""
        pref = (self.cfg.get("voz_preferida") or "").lower()
        self._pref_aplicada = pref
        por_pref = por_idioma = None
        nombres = []
        voces = sp.GetVoices()
        for i in range(voces.Count):
            v = voces.Item(i)
            desc = v.GetDescription()
            nombres.append(desc)
            try:
                langs = v.GetAttribute("Language")
            except Exception:
                langs = ""
            es_espanol = any(c and int(c, 16) & 0xFF == 0x0A for c in re.findall(r"[0-9A-Fa-f]+", langs))
            if pref and pref in desc.lower() and por_pref is None:
                por_pref = (v, desc)
            if es_espanol and por_idioma is None:
                por_idioma = (v, desc)
        self.voces = nombres
        elegida = por_pref or por_idioma
        if elegida:
            sp.Voice = elegida[0]
            self.gui.log(f"🔊 Voz: {elegida[1]}")
        else:
            self.gui.log("⚠️ No hay voz en español instalada (Configuración → Hora e idioma → Voz). Usaré la predeterminada.")
        sp.Rate = self._rate()

    def _hablar_ps(self, texto):
        # El texto NO se pega dentro del script: PowerShell trata también las comillas tipográficas (‘ ’ ‚ ‛) como comilla
        # simple, así que un portapapeles o una nota con «’» podía cerrar la cadena y ejecutar código. Va en una variable.
        script = ("Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                  "try { $s.SelectVoiceByHints('NotSet','NotSet',0,[Globalization.CultureInfo]'es-ES') } catch {}; "
                  f"$s.Rate = {int(self._rate())}; $s.Speak($env:ALFRED_TTS)")
        entorno = dict(os.environ, ALFRED_TTS=str(texto).replace("\x00", "")[:8000])
        subprocess.run([ruta_sistema("powershell"), "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", script],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=entorno,
                       creationflags=SIN_VENTANA, timeout=90, check=True)

    def _run(self):
        sapi = None
        try:                              # se prepara ANTES del primer mensaje: sin retraso ni silencio inicial
            sapi = self._crear_sapi()
        except Exception:
            logging.exception("SAPI no disponible")
            self._usar_ps = True
        while True:
            try:
                texto, ev, idioma = self.q.get(timeout=30)
            except queue.Empty:
                self.piper.cerrar_si_inactivo(120)       # libera la memoria de la voz IA en reposo
                self.kokoro.cerrar_si_inactivo(300)
                continue
            with self._lock:
                self._desde = time.time()            # cuenta el atasco desde que ESTE mensaje empieza a sonar
            try:
                motor = self.motor_ia()
                usa_ia = bool(self.cfg.get("voz_ia")) and not self._ia_off and motor.instalado()
                dicho, idioma_voz = texto, "es"
                if idioma == "en" and usa_ia and motor is self.kokoro and self.cfg.get("responder_ingles") is not False:
                    traducido = traducir_respuesta(texto)        # le hablaste en inglés: contesta en inglés
                    if traducido:
                        dicho, idioma_voz = traducido, "en"
                    elif parece_ingles(texto):                   # una nota o respuesta tuya escrita en inglés
                        idioma_voz = "en"
                with self._lock:
                    priv = texto in self._privados
                    self._privados.discard(texto)
                self.gui.estado(f"🗣️ {dicho}")
                self.gui.log(f"🗣️ {dicho}", privado=f"🗣️ [texto privado: {len(dicho)} caracteres]" if priv else None)
                hablado = False
                if usa_ia:
                    try:
                        motor.hablar(dicho, idioma_voz)
                        hablado = True
                        self._ia_fallos = 0
                    except Exception:
                        logging.exception("La voz IA falló")
                        self._ia_fallos += 1
                        if self._ia_fallos >= 2:
                            self._ia_off = True
                            self.gui.log("⚠️ La voz con IA no responde; uso la voz de Windows. "
                                         "Puedes reintentar en ☰ Menú → Voz.")
                if not hablado and not self._usar_ps:
                    try:
                        if (self.cfg.get("voz_preferida") or "").lower() != self._pref_aplicada:
                            self._elegir_voz(sapi)   # cambiada desde el menú
                        sapi.Rate = self._rate()
                        sapi.Speak(texto, 0)       # 0 = síncrono
                    except Exception:
                        logging.exception("SAPI falló al hablar; paso a PowerShell")
                        self._usar_ps = True
                if not hablado and self._usar_ps:
                    self._hablar_ps(texto)
            except Exception as e:
                logging.exception("No pude hablar")
                self.gui.log(f"⚠️ No pude hablar: {e}")
            finally:
                with self._lock:
                    self._pend = max(0, self._pend - 1)
                    self._fin = time.time()
                    self._desde = time.time()
                self.gui.estado("🟢 Escuchando…")
                ev.set()


# ══════════════════════════════════════════════════════════════════════════════
#  MOTOR DE ALFRED
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
#  3.0 · CONTROL TOTAL DEL PC POR VOZ — acceso a Windows (ventanas, teclado, energía, sistema)
# ══════════════════════════════════════════════════════════════════════════════
from ctypes import wintypes  # noqa: E402


@functools.lru_cache(maxsize=1)
def _u32():
    u = ctypes.WinDLL("user32", use_last_error=True)
    H = wintypes.HWND
    u.GetForegroundWindow.restype = H
    u.ShowWindow.argtypes = [H, ctypes.c_int]
    u.IsIconic.argtypes = [H]
    u.IsWindowVisible.argtypes = [H]
    u.GetWindow.argtypes = [H, wintypes.UINT]
    u.GetWindow.restype = H
    u.GetWindowTextLengthW.argtypes = [H]
    u.GetWindowTextW.argtypes = [H, wintypes.LPWSTR, ctypes.c_int]
    u.GetWindowThreadProcessId.argtypes = [H, ctypes.POINTER(wintypes.DWORD)]
    u.GetWindowThreadProcessId.restype = wintypes.DWORD
    u.PostMessageW.argtypes = [H, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    u.SetForegroundWindow.argtypes = [H]
    u.BringWindowToTop.argtypes = [H]
    u.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
    u.GetWindowRect.argtypes = [H, ctypes.POINTER(wintypes.RECT)]
    u.SendInput.argtypes = [wintypes.UINT, ctypes.c_void_p, ctypes.c_int]
    u.SendInput.restype = wintypes.UINT
    u.OpenClipboard.argtypes = [H]
    u.OpenClipboard.restype = wintypes.BOOL
    u.GetClipboardData.argtypes = [wintypes.UINT]
    u.GetClipboardData.restype = ctypes.c_void_p
    u.SetClipboardData.argtypes = [wintypes.UINT, ctypes.c_void_p]
    u.SetClipboardData.restype = ctypes.c_void_p
    return u


@functools.lru_cache(maxsize=1)
def _k32():
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.GetCurrentThreadId.restype = wintypes.DWORD
    k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k.OpenProcess.restype = wintypes.HANDLE
    k.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                                             ctypes.POINTER(wintypes.DWORD)]
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    k.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    k.GlobalAlloc.restype = ctypes.c_void_p
    k.GlobalLock.argtypes = [ctypes.c_void_p]
    k.GlobalLock.restype = ctypes.c_void_p
    k.GlobalUnlock.argtypes = [ctypes.c_void_p]
    k.GetTickCount64.restype = ctypes.c_ulonglong
    return k


def exe_de_pid(pid):
    try:
        k = _k32()
        h = k.OpenProcess(0x1000, False, pid)                  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return ""
        try:
            buf = ctypes.create_unicode_buffer(1024)
            n = wintypes.DWORD(1024)
            ok = k.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n))
            return os.path.basename(buf.value).lower() if ok else ""
        finally:
            k.CloseHandle(h)
    except Exception:
        return ""


def ventanas_abiertas():
    """Ventanas de aplicación que ves en pantalla (de la más reciente a la más antigua): [{hwnd, titulo, exe, pid}].
    Sin las ocultas, las «fantasma» de las apps de la tienda, los diálogos con dueño ni las de Alfred."""
    if os.name != "nt":
        return []
    u = _u32()
    try:
        dwm = ctypes.WinDLL("dwmapi")
    except OSError:
        dwm = None
    yo, res, exes = os.getpid(), [], {}

    def enum(hwnd, _):
        try:
            if not u.IsWindowVisible(hwnd) or u.GetWindow(hwnd, 4):       # 4 = GW_OWNER
                return True
            n = u.GetWindowTextLengthW(hwnd)
            if n <= 0:
                return True
            if dwm is not None:
                oculta = wintypes.DWORD(0)
                try:
                    dwm.DwmGetWindowAttribute(hwnd, 14, ctypes.byref(oculta), 4)   # 14 = DWMWA_CLOAKED
                except Exception:
                    pass
                if oculta.value:
                    return True
            buf = ctypes.create_unicode_buffer(n + 1)
            u.GetWindowTextW(hwnd, buf, n + 1)
            if buf.value == "Program Manager":
                return True
            pid = wintypes.DWORD(0)
            u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value == yo:
                return True
            if pid.value not in exes:
                exes[pid.value] = exe_de_pid(pid.value)
            res.append({"hwnd": hwnd, "titulo": buf.value, "exe": exes[pid.value], "pid": pid.value})
        except Exception:
            pass
        return True

    proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)(enum)
    ctypes.WinDLL("user32").EnumWindows(proc, 0)
    return res


def enfocar_ventana(hwnd):
    """Trae una ventana cualquiera al frente (Windows no deja robar el foco: se une al hilo de la ventana activa)."""
    u, k = _u32(), _k32()
    if u.IsIconic(hwnd):
        u.ShowWindow(hwnd, 9)                                            # SW_RESTORE
    actual = u.GetForegroundWindow()
    t_act = u.GetWindowThreadProcessId(actual, None) if actual else 0
    t_dst = u.GetWindowThreadProcessId(hwnd, None)
    yo, unidos = k.GetCurrentThreadId(), []
    for t in {t_act, t_dst}:
        if t and t != yo and u.AttachThreadInput(yo, t, True):
            unidos.append(t)
    try:
        u.BringWindowToTop(hwnd)
        u.SetForegroundWindow(hwnd)
        u.ShowWindow(hwnd, 5)                                            # SW_SHOW
    finally:
        for t in unidos:
            u.AttachThreadInput(yo, t, False)
    return u.GetForegroundWindow() == hwnd


def cerrar_ventana(hwnd):
    """Pide a la ventana que se cierre (WM_CLOSE): la app puede preguntar si guardas los cambios."""
    return bool(_u32().PostMessageW(hwnd, 0x0010, 0, 0))


def rect_ventana(hwnd):
    r = wintypes.RECT()
    if _u32().GetWindowRect(hwnd, ctypes.byref(r)):
        return r.left, r.top, r.right, r.bottom
    return None


# ── escribir texto con acentos, ñ y emojis (SendInput Unicode) ───────────────
class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_int32), ("dy", ctypes.c_int32), ("mouseData", ctypes.c_uint32),
                ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32), ("dwExtraInfo", ctypes.c_size_t)]


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_uint16), ("wScan", ctypes.c_uint16), ("dwFlags", ctypes.c_uint32),
                ("time", ctypes.c_uint32), ("dwExtraInfo", ctypes.c_size_t)]


class _INPUT_U(ctypes.Union):
    _fields_ = [("mi", _MOUSEINPUT), ("ki", _KEYBDINPUT)]


class _INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_uint32), ("u", _INPUT_U)]


def _evento_tecla(vk=0, scan=0, flags=0):
    e = _INPUT()
    e.type = 1                                                          # INPUT_KEYBOARD
    e.u.ki = _KEYBDINPUT(vk, scan, flags, 0, 0)
    return e


def escribir_unicode(texto, lote=120):
    """Escribe el texto en la ventana activa, letra por letra, como si lo tecleara una persona. Sirve con acentos, ñ,
    signos y emojis (pyautogui.write los ignora). \\n = Enter, \\t = Tab."""
    u = _u32()
    eventos = []
    for ch in texto:
        if ch in "\r":
            continue
        if ch == "\n":
            eventos += [_evento_tecla(0x0D), _evento_tecla(0x0D, 0, 2)]
        elif ch == "\t":
            eventos += [_evento_tecla(0x09), _evento_tecla(0x09, 0, 2)]
        else:
            b = ch.encode("utf-16-le")
            for i in range(0, len(b), 2):                               # los emojis son 2 unidades (pares sustitutos)
                cod = b[i] | (b[i + 1] << 8)
                eventos += [_evento_tecla(0, cod, 0x0004), _evento_tecla(0, cod, 0x0004 | 0x0002)]
    for i in range(0, len(eventos), lote * 2):
        trozo = eventos[i:i + lote * 2]
        arr = (_INPUT * len(trozo))(*trozo)
        if u.SendInput(len(trozo), ctypes.byref(arr), ctypes.sizeof(_INPUT)) != len(trozo):
            raise OSError("Windows no dejó escribir en esa ventana (¿está abierta como administrador?)")


# ── portapapeles ─────────────────────────────────────────────────────────────
def _abrir_portapapeles():
    u = _u32()
    for _ in range(12):
        if u.OpenClipboard(None):
            return True
        time.sleep(0.05)
    return False


def leer_portapapeles():
    u, k = _u32(), _k32()
    if not _abrir_portapapeles():
        return None
    try:
        h = u.GetClipboardData(13)                                      # CF_UNICODETEXT
        if not h:
            return None
        p = k.GlobalLock(h)
        if not p:
            return None
        try:
            return ctypes.wstring_at(p)
        finally:
            k.GlobalUnlock(h)
    finally:
        ctypes.WinDLL("user32").CloseClipboard()


def vaciar_portapapeles():
    if not _abrir_portapapeles():
        return False
    try:
        return bool(ctypes.WinDLL("user32").EmptyClipboard())
    finally:
        ctypes.WinDLL("user32").CloseClipboard()


def copiar_imagen_portapapeles(img):
    """Pone una imagen PIL en el portapapeles (formato DIB) para poder pegarla en cualquier programa."""
    import io
    b = io.BytesIO()
    img.convert("RGB").save(b, "BMP")
    datos = b.getvalue()[14:]                                           # sin la cabecera de archivo
    u, k = _u32(), _k32()
    h = k.GlobalAlloc(0x0002, len(datos))                               # GMEM_MOVEABLE
    p = k.GlobalLock(h)
    ctypes.memmove(p, datos, len(datos))
    k.GlobalUnlock(h)
    if not _abrir_portapapeles():
        return False
    try:
        ctypes.WinDLL("user32").EmptyClipboard()
        return bool(u.SetClipboardData(8, h))                           # CF_DIB
    finally:
        ctypes.WinDLL("user32").CloseClipboard()


def capturar_pantalla(carpeta, region=None):
    """Guarda una captura (pantalla completa o región (x, y, ancho, alto)) y la copia al portapapeles. -> ruta."""
    os.makedirs(carpeta, exist_ok=True)
    img = pyautogui.screenshot(region=region)
    ruta = os.path.join(carpeta, "captura_" + time.strftime("%Y%m%d_%H%M%S") + ".png")
    img.save(ruta)
    try:
        copiar_imagen_portapapeles(img)
    except Exception:
        logging.exception("No pude copiar la captura al portapapeles")
    return ruta


# ── estado del sistema ───────────────────────────────────────────────────────
def info_bateria():
    class _SPS(ctypes.Structure):
        _fields_ = [("ACLineStatus", ctypes.c_ubyte), ("BatteryFlag", ctypes.c_ubyte),
                    ("BatteryLifePercent", ctypes.c_ubyte), ("SystemStatusFlag", ctypes.c_ubyte),
                    ("BatteryLifeTime", ctypes.c_uint32), ("BatteryFullLifeTime", ctypes.c_uint32)]
    s = _SPS()
    if not ctypes.WinDLL("kernel32").GetSystemPowerStatus(ctypes.byref(s)):
        return None
    if s.BatteryFlag == 128 or s.BatteryLifePercent == 255:             # sin batería / desconocido
        return None
    return {"pct": int(s.BatteryLifePercent), "cargando": s.ACLineStatus == 1,
            "seg": None if s.BatteryLifeTime == 0xFFFFFFFF else int(s.BatteryLifeTime)}


def info_ram():
    class _MEM(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_uint32), ("dwMemoryLoad", ctypes.c_uint32), ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = _MEM()
    m.dwLength = ctypes.sizeof(_MEM)
    if not ctypes.WinDLL("kernel32").GlobalMemoryStatusEx(ctypes.byref(m)):
        return None
    return int(m.dwMemoryLoad), m.ullTotalPhys / 2 ** 30, m.ullAvailPhys / 2 ** 30


def _tiempos_cpu():
    ft = [wintypes.FILETIME() for _ in range(3)]
    ctypes.WinDLL("kernel32").GetSystemTimes(*[ctypes.byref(f) for f in ft])
    return [(f.dwHighDateTime << 32) | f.dwLowDateTime for f in ft]     # reposo, kernel (incluye reposo), usuario


def info_cpu(espera=0.5):
    a = _tiempos_cpu()
    time.sleep(espera)
    b = _tiempos_cpu()
    total = (b[1] - a[1]) + (b[2] - a[2])
    return max(0.0, min(100.0, 100.0 * (1.0 - (b[0] - a[0]) / total))) if total > 0 else 0.0


def info_disco():
    uso = shutil.disk_usage(os.environ.get("SystemDrive", "C:") + "\\")
    return 100.0 * uso.used / uso.total, uso.free / 2 ** 30, uso.total / 2 ** 30


def info_uptime():
    return _k32().GetTickCount64() / 1000.0


def procesos_pesados(n=3):
    """Los programas que más memoria usan: [(nombre, MB)] (suma todos los procesos de cada programa)."""
    import csv
    r = subprocess.run([ruta_sistema("tasklist"), "/FO", "CSV", "/NH"], capture_output=True, text=True, errors="replace",
                       creationflags=SIN_VENTANA, timeout=15)
    suma = {}
    for fila in csv.reader(r.stdout.splitlines()):
        if len(fila) < 5:
            continue
        nombre = fila[0].lower()
        if nombre in ("system idle process", "system", "registry", "memory compression"):
            continue
        kb = re.sub(r"\D", "", fila[4])
        if kb:
            suma[nombre] = suma.get(nombre, 0) + int(kb)
    top = sorted(suma.items(), key=lambda x: -x[1])[:n]
    return [(re.sub(r"\.exe$", "", nom), kb / 1024.0) for nom, kb in top]


def nombre_wifi():
    r = subprocess.run([ruta_sistema("netsh"), "wlan", "show", "interfaces"], capture_output=True, text=True, errors="replace",
                       creationflags=SIN_VENTANA, timeout=10)
    m = re.search(r"^\s*SSID\s*:\s*(.+?)\s*$", r.stdout, re.M)
    return m.group(1) if m else None


def modo_oscuro_actual():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as k:
            return winreg.QueryValueEx(k, "AppsUseLightTheme")[0] == 0
    except OSError:
        return False


def fijar_tema(oscuro):
    ruta = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, ruta, 0, winreg.KEY_SET_VALUE) as k:
        for nombre in ("AppsUseLightTheme", "SystemUsesLightTheme"):
            winreg.SetValueEx(k, nombre, 0, winreg.REG_DWORD, 0 if oscuro else 1)
    try:                                                                # avisa a Windows para que lo aplique al instante
        res = wintypes.LPARAM(0)
        ctypes.WinDLL("user32").SendMessageTimeoutW(0xFFFF, 0x001A, 0, "ImmersiveColorSet", 2, 3000, ctypes.byref(res))
    except Exception:
        pass


def vaciar_papelera():
    return ctypes.WinDLL("shell32").SHEmptyRecycleBinW(None, None, 0x7) in (0, 1)   # sin confirmación, progreso ni sonido


def energia_windows(args):
    """shutdown.exe con argumentos; antes anula cualquier apagado pendiente. -> (código, mensaje)."""
    subprocess.run([ruta_sistema("shutdown"), "/a"], capture_output=True, creationflags=SIN_VENTANA)
    r = subprocess.run([ruta_sistema("shutdown")] + list(args), capture_output=True, text=True, errors="replace",
                       creationflags=SIN_VENTANA)
    return r.returncode, (r.stderr or r.stdout or "").strip()


# ── respuestas en inglés de los comandos nuevos ──────────────────────────────
_RESP_EN_PC = {
    "Bloqueando el equipo.": "Locking the computer.", "Suspendiendo el equipo.": "Putting the computer to sleep.",
    "Hibernando el equipo.": "Hibernating the computer.", "Cerrando la sesión.": "Signing out.",
    "¿Apago la computadora? Diga sí para confirmar.": "Shall I shut down the computer? Say yes to confirm.",
    "¿Reinicio la computadora? Diga sí para confirmar.": "Shall I restart the computer? Say yes to confirm.",
    "¿Cierro la sesión? Diga sí para confirmar.": "Shall I sign out? Say yes to confirm.",
    "¿Vacío la papelera? Diga sí para confirmar.": "Shall I empty the recycle bin? Say yes to confirm.",
    "Apagando el equipo. Diga cancela el apagado si fue un error.":
        "Shutting down. Say cancel shutdown if this was a mistake.",
    "Reiniciando el equipo. Diga cancela el apagado si fue un error.":
        "Restarting. Say cancel shutdown if this was a mistake.",
    "Apagado cancelado.": "Shutdown cancelled.", "No hay ningún apagado programado.": "There is no shutdown scheduled.",
    "Apagando la pantalla.": "Turning the screen off.", "Pantalla encendida.": "Screen on.",
    "Temporizador cancelado.": "Timer cancelled.", "Temporizadores cancelados.": "Timers cancelled.",
    "No tiene temporizadores activos.": "You have no active timers.", "¿Cuánto tiempo, señor?": "How long, sir?",
    "Señor, su temporizador ha terminado.": "Sir, your timer has finished.",
    "¿Qué cuenta quiere que resuelva?": "What should I calculate?", "No entendí la cuenta, señor.":
        "I didn't understand the calculation, sir.", "No se puede dividir entre cero.": "You can't divide by zero.",
    "Dictado activado. Diga fin del dictado para terminar.": "Dictation on. Say end dictation to stop.",
    "Dictado terminado.": "Dictation finished.", "El dictado no estaba activo.": "Dictation was not on.",
    "¿Qué quiere que escriba?": "What should I type?",
    "Cuadrícula activada. Diga un número del uno al nueve.": "Grid on. Say a number from one to nine.",
    "Captura guardada. También está en el portapapeles.": "Screenshot saved. It's also on the clipboard.",
    "Modo oscuro activado.": "Dark mode on.", "Modo claro activado.": "Light mode on.",
    "El portapapeles está vacío.": "The clipboard is empty.", "Portapapeles vaciado.": "Clipboard cleared.",
    "Papelera vaciada.": "Recycle bin emptied.", "Este equipo no tiene batería.": "This computer has no battery.",
    "Wi-Fi desconectado.": "Wi-Fi disconnected.", "Conectando al Wi-Fi.": "Connecting to Wi-Fi.",
    "No sé a qué red conectarme. Conéctese una vez y la recordaré.":
        "I don't know which network to join. Connect once and I'll remember it.",
    "¿A qué ventana quiere cambiar?": "Which window do you want to switch to?", "¿Qué quiere que cierre?":
        "What should I close?", "No pude hacerlo, señor.": "I couldn't do that, sir.",
    "Hecho.": "Done.", "Cuadrícula cerrada.": "Grid closed.",
}


def _dur_en(txt):
    for es, en in (("horas", "hours"), ("hora", "hour"), ("minutos", "minutes"), ("minuto", "minute"),
                   ("segundos", "seconds"), ("segundo", "second"), (" y ", " and ")):
        txt = txt.replace(es, en)
    return txt


_RESP_RX[:0] = [
    (re.compile(r"^Temporizador de (.+?) activado(?: para (.+))?\.$"),
     lambda m: f"Timer set for {_dur_en(m.group(1))}" + (f" for {m.group(2)}." if m.group(2) else ".")),
    (re.compile(r"^Alarma programada para las (\d{1,2}:\d{2})\.$"), lambda m: f"Alarm set for {m.group(1)}."),
    (re.compile(r"^Señor, es hora de (.+)\.$"), lambda m: f"Sir, it's time to {m.group(1)}."),
    (re.compile(r"^Faltan (.+) para (.+)\.$"), lambda m: f"{_dur_en(m.group(1))} left for {m.group(2)}."),
    (re.compile(r"^El resultado es (.+)\.$"), lambda m: f"The result is {m.group(1).replace(',', '.')}."),
    (re.compile(r"^Apagaré el equipo en (.+)\. Diga cancela el apagado para detenerlo\.$"),
     lambda m: f"I'll shut the computer down in {_dur_en(m.group(1))}. Say cancel shutdown to stop it."),
    (re.compile(r"^Abriendo ajustes de (.+)\.$"), lambda m: f"Opening {m.group(1)} settings."),
    (re.compile(r"^Cambiando a (.+)\.$"), lambda m: f"Switching to {m.group(1)}."),
    (re.compile(r"^Cerrando (.+)\.$"), lambda m: f"Closing {m.group(1)}."),
    (re.compile(r"^No veo (.+) abierto\.$"), lambda m: f"I don't see {m.group(1)} open."),
    (re.compile(r"^Tiene (\d+) por ciento de batería(.*)\.$"),
     lambda m: f"You have {m.group(1)} percent battery" + (", charging" if "cargando" in m.group(2) else
                                                          ", on battery" if "desconectado" in m.group(2) else "") + "."),
    (re.compile(r"^El procesador está al (\d+) por ciento\.$"), lambda m: f"The processor is at {m.group(1)} percent."),
    (re.compile(r"^La memoria está al (\d+) por ciento\.(.*)$"), lambda m: f"Memory is at {m.group(1)} percent."),
    (re.compile(r"^Hay conexión a internet\.$"), lambda m: "You are connected to the internet."),
    (re.compile(r"^No hay conexión a internet\.$"), lambda m: "There is no internet connection."),
]


# ══════════════════════════════════════════════════════════════════════════════
#  3.0 · CLASE ControlPC: los comandos nuevos (Alfred la hereda)
# ══════════════════════════════════════════════════════════════════════════════
class ControlPC:
    """Control del PC por voz: energía, ventanas, teclado, ratón, dictado, temporizadores y estado del sistema.
    Se mezcla con Alfred: usa self.voz, self.gui, self.cfg, self.nombre, self.lanzar y self.pend_conf."""

    # ── arranque ─────────────────────────────────────────────────────────────
    def _init_pc(self):
        self.dictado = False                  # modo dictado: lo que dices se escribe sin palabra de activación
        self.grid = None                      # cuadrícula del ratón: {"rect", "hist", "win"}
        self.alarmas = {}                     # id -> {"fin", "texto", "timer"}
        self._lock_alarmas = threading.Lock()
        self._dict_ult, self._dict_len = "", 0
        self._ssid_previo = str(self.cfg.get("wifi_ultimo") or "")

    def _iniciar_pc(self):
        threading.Thread(target=self._cargar_alarmas, daemon=True).start()
        threading.Thread(target=self._vigilar_bateria, daemon=True).start()

    def _pitido(self, tipo="ok"):
        try:
            import winsound
            if tipo == "ok":
                winsound.Beep(1100, 40)
            elif tipo == "error":
                winsound.Beep(300, 170)
            elif tipo == "alarma":
                for _ in range(3):
                    winsound.Beep(1000, 200)
                    time.sleep(0.07)
        except Exception:
            pass

    def _confirmar(self, pregunta, accion):
        """Lo delicado (apagar, reiniciar, cerrar sesión, matar procesos, vaciar la papelera, borrar archivos) SIEMPRE
        pide un «sí» dicho en voz alta en este PC. Ya no existe el ajuste confirmar_energia = false: cualquier programa
        que pudiera editar alfred_config.json habría podido quitar la confirmación."""
        self.pend_conf = ({"_accion": accion}, time.time() + 12)
        self.voz.decir(pregunta)

    @staticmethod
    def _resto_tras_frase(norm, frases):
        n = nucleo_orden(norm)
        for f in sorted(frases, key=len, reverse=True):
            if n == f:
                return ""
            if n.startswith(f + " "):
                return n[len(f) + 1:]
        return n

    # ── energía ──────────────────────────────────────────────────────────────
    def cmd_bloquear(self, raw, norm):
        self.voz.decir("Bloqueando el equipo.", esperar=True)
        _u32().LockWorkStation()

    def cmd_suspender(self, raw, norm):
        self.voz.decir("Suspendiendo el equipo.", esperar=True)
        time.sleep(0.4)
        ctypes.WinDLL("powrprof").SetSuspendState(0, 1, 0)       # si Windows tiene la hibernación activa, hiberna

    def cmd_hibernar(self, raw, norm):
        self.voz.decir("Hibernando el equipo.", esperar=True)
        energia_windows(["/h"])

    def _energia_inmediata(self, flag, mensaje):
        retardo = max(5, int(self.cfg.get("retardo_apagado") or 20))
        cod, err = energia_windows([flag, "/t", str(retardo)])
        if cod:
            self.gui.log(f"⚠️ shutdown falló ({cod}): {err}")
            self.voz.decir("No pude hacerlo, señor.")
        else:
            self.gui.log(f"⏻ {mensaje} en {retardo} s (di «{self.nombre} cancela el apagado» para detenerlo)")
            self.voz.decir(mensaje + " Diga cancela el apagado si fue un error.")

    def _energia(self, flag, norm, pregunta, mensaje):
        seg = parse_duracion(norm)
        if seg:                                                  # programado: se puede cancelar, no pide confirmación
            seg = int(min(seg, 315360000))
            cod, err = energia_windows([flag, "/t", str(seg)])
            if cod:
                self.gui.log(f"⚠️ shutdown falló ({cod}): {err}")
                self.voz.decir("No pude hacerlo, señor.")
            else:
                self.voz.decir(f"Apagaré el equipo en {texto_duracion(seg)}. Diga cancela el apagado para detenerlo.")
            return
        self._confirmar(pregunta, lambda: self._energia_inmediata(flag, mensaje))

    def cmd_apagar_pc(self, raw, norm):
        self._energia("/s", norm, "¿Apago la computadora? Diga sí para confirmar.",
                      "Apagando el equipo.")

    def cmd_reiniciar_pc(self, raw, norm):
        self._energia("/r", norm, "¿Reinicio la computadora? Diga sí para confirmar.",
                      "Reiniciando el equipo.")

    def cmd_cerrar_sesion(self, raw, norm):
        def hacer():
            self.voz.decir("Cerrando la sesión.", esperar=True)
            energia_windows(["/l"])
        self._confirmar("¿Cierro la sesión? Diga sí para confirmar.", hacer)

    def cmd_cancelar_apagado(self, raw, norm):
        r = subprocess.run([ruta_sistema("shutdown"), "/a"], capture_output=True, creationflags=SIN_VENTANA)
        self.voz.decir("Apagado cancelado." if r.returncode == 0 else "No hay ningún apagado programado.")

    def cmd_pantalla(self, raw, norm):
        if hay(norm, "apaga", "apagar", "apagada"):
            self.voz.decir("Apagando la pantalla.", esperar=True)
            time.sleep(0.3)
            _u32().PostMessageW(0xFFFF, 0x0112, 0xF170, 2)       # WM_SYSCOMMAND, SC_MONITORPOWER, apagar
        else:
            pyautogui.moveRel(1, 0)
            pyautogui.moveRel(-1, 0)                             # mover el ratón enciende el monitor
            self.voz.decir("Pantalla encendida.")

    # ── temporizadores y alarmas ─────────────────────────────────────────────
    def _guardar_alarmas(self):
        try:
            with open(ARCHIVO_ALARMAS, "w", encoding="utf-8") as f:
                json.dump([{"id": i, "fin": a["fin"], "texto": a["texto"]} for i, a in self.alarmas.items()], f)
        except Exception:
            logging.exception("No pude guardar las alarmas")

    def _cargar_alarmas(self):
        try:
            with open(ARCHIVO_ALARMAS, encoding="utf-8") as f:
                datos = json.load(f)
        except (OSError, ValueError):
            return
        ahora = time.time()
        for a in datos:
            try:
                if float(a["fin"]) > ahora - 600:                 # las que vencieron hace menos de 10 min suenan al abrir
                    self._programar_alarma(max(float(a["fin"]), ahora + 4), a.get("texto", ""), a.get("id"))
            except (KeyError, TypeError, ValueError):
                continue

    def _programar_alarma(self, fin, texto="", id_=None):
        with self._lock_alarmas:
            id_ = id_ or max(int(time.time() * 1000), max(self.alarmas, default=0) + 1)   # único aunque sea el mismo ms
        t = threading.Timer(max(0.0, fin - time.time()), self._sonar_alarma, args=(id_,))
        t.daemon = True
        with self._lock_alarmas:
            self.alarmas[id_] = {"fin": fin, "texto": texto, "timer": t}
            self._guardar_alarmas()
        t.start()
        return id_

    def _sonar_alarma(self, id_):
        with self._lock_alarmas:
            a = self.alarmas.pop(id_, None)
            self._guardar_alarmas()
        if not a:
            return
        et = a.get("texto") or ""
        self.gui.log(f"⏰ {et or 'Temporizador'}: ¡es la hora!")
        self._pitido("alarma")
        self.voz.decir(f"Señor, es hora de {et}." if et else "Señor, su temporizador ha terminado.")

    def cmd_temporizador(self, raw, norm):
        n = nucleo_orden(norm)
        toks = set(n.split())
        if toks & {"cancela", "cancelar", "elimina", "quita", "borra", "deten", "detener"}:
            with self._lock_alarmas:
                if not self.alarmas:
                    self.voz.decir("No tiene temporizadores activos.")
                    return
                todos = bool(toks & {"todos", "todas", "temporizadores", "alarmas"}) or len(self.alarmas) == 1
                ids = list(self.alarmas) if todos else [min(self.alarmas, key=lambda i: self.alarmas[i]["fin"])]
                for i in ids:
                    self.alarmas.pop(i)["timer"].cancel()
                self._guardar_alarmas()
            self.voz.decir("Temporizadores cancelados." if len(ids) > 1 else "Temporizador cancelado.")
            return
        if n.startswith(("cuanto falta", "cuanto tiempo falta", "que alarmas", "que temporizadores", "lista de")):
            with self._lock_alarmas:
                items = sorted(self.alarmas.values(), key=lambda a: a["fin"])
            if not items:
                self.voz.decir("No tiene temporizadores activos.")
                return
            for a in items[:4]:
                self.voz.decir(f"Faltan {texto_duracion(a['fin'] - time.time())} para {a['texto'] or 'el temporizador'}.")
            return
        ahora = datetime.datetime.now()
        dur = duracion_en(n)
        hr = hora_reloj_en(n, ahora) if re.search(r"\ba las?\b", n) else None
        if hr:
            fin_dt, fin_idx = hr
            fin_epoch = fin_dt.timestamp()
            resumen = f"Alarma programada para las {fin_dt.hour}:{fin_dt.minute:02d}."
        elif dur:
            seg, fin_idx = dur
            fin_epoch = time.time() + seg
            resumen = None
        else:
            self.voz.decir("¿Cuánto tiempo, señor?")
            return
        resto = n.split()[fin_idx:]
        while resto and resto[0] in {"de", "para", "que", "a", "por", "y"}:
            resto.pop(0)
        etiqueta = " ".join(resto)
        self._programar_alarma(fin_epoch, etiqueta)
        if resumen:
            self.voz.decir(resumen)
        else:
            self.voz.decir(f"Temporizador de {texto_duracion(dur[0])} activado" + (f" para {etiqueta}." if etiqueta else "."))
        self.gui.log(f"⏰ Aviso programado: {texto_duracion(fin_epoch - time.time())}" + (f" · {etiqueta}" if etiqueta else ""))

    # ── calculadora ──────────────────────────────────────────────────────────
    def cmd_calcular(self, raw, norm):
        expr = expresion_de_voz(norm)
        if not expr:
            self.voz.decir("No entendí la cuenta, señor." if len(norm.split()) > 2 else "¿Qué cuenta quiere que resuelva?")
            return
        try:
            res = evaluar_expresion(expr)
        except ZeroDivisionError:
            self.voz.decir("No se puede dividir entre cero.")
            return
        except (ValueError, SyntaxError, OverflowError):
            self.voz.decir("No entendí la cuenta, señor.")
            return
        self.gui.log(f"🧮 {expr} = {formatear_numero(res)}")
        self.voz.decir(f"El resultado es {formatear_numero(res)}.")

    # ── escribir y dictar ────────────────────────────────────────────────────
    def cmd_escribir(self, raw, norm):
        toks = raw.split()
        ntoks = [normalizar(t) for t in toks]
        i = next((k for k, t in enumerate(ntoks) if t in ("escribe", "escribeme", "teclea", "escribir", "teclear")), None)
        resto = toks[i + 1:] if i is not None else []
        while resto and normalizar(resto[0]) in ("lo", "siguiente", "el", "texto", "la", "frase", "que", "esto"):
            resto.pop(0)
        if not resto:
            self.voz.decir("¿Qué quiere que escriba?")
            return
        texto = texto_dictado(" ".join(resto))
        escribir_unicode(texto)
        self.gui.log(f"⌨️ Escribí: {texto}", privado=f"⌨️ [texto escrito: {len(texto)} caracteres]")
        self._pitido("ok")

    def cmd_dictado(self, raw, norm):
        parar = hay(norm, "deja", "termina", "fin", "finaliza", "deten", "detener", "desactiva", "sal", "para")
        if parar:
            if not self.dictado:
                self.voz.decir("El dictado no estaba activo.")
                return
            self.dictado = False
            self.gui.estado("🟢 Escuchando…")
            self.voz.decir("Dictado terminado.")
        else:
            self.dictado = True
            self._dict_ult, self._dict_len = "", 0
            self.gui.estado("✍️ Dictando… (di «fin del dictado»)")
            self.voz.decir("Dictado activado. Diga fin del dictado para terminar.")

    def _atender_modo(self, raw, norm, idioma):
        """Modos que no piden la palabra de activación (cuadrícula del ratón y dictado). True si consumió lo oído."""
        if self.grid is not None:
            return self._atender_grid(norm)
        if self.dictado:
            return self._atender_dictado(raw, norm, idioma)
        return False

    def _atender_dictado(self, raw, norm, idioma):
        n = nucleo_orden(norm)
        if any(p in n for p in ("fin del dictado", "fin de dictado", "deja de dictar", "termina el dictado",
                                "termina de dictar", "deten el dictado", "desactiva el dictado", "sal del dictado",
                                "finaliza el dictado", "para el dictado", "stop dictation", "end dictation",
                                "stop dictating", "finish dictation")):
            self.dictado = False
            self.gui.estado("🟢 Escuchando…")
            self.voz.fijar_idioma(idioma)
            self.voz.decir("Dictado terminado.")
            return True
        if n in ("borra eso", "borra lo ultimo", "borra la ultima frase", "deshaz eso", "scratch that", "delete that"):
            for _ in range(min(self._dict_len, 600)):
                pyautogui.press("backspace")
            self._dict_len, self._dict_ult = 0, ""
            return True
        if n in ("borra la ultima palabra", "delete last word"):
            pyautogui.hotkey("ctrl", "backspace")
            return True
        cap = self._dict_ult in ("", ".", "?", "!", "\n")
        pieza = texto_dictado(raw, mayus_inicial=cap)
        if not pieza:
            return True
        if self._dict_ult and self._dict_ult not in "\n\t(¿¡\"" and pieza[0] not in ",.;:?!)\n":
            pieza = " " + pieza
        try:
            escribir_unicode(pieza)
        except Exception as e:
            logging.exception("Dictado")
            self.gui.log(f"⚠️ No pude escribir: {e}")
            return True
        self._dict_ult, self._dict_len = pieza[-1], len(pieza)
        self.gui.log(f"✍️ {pieza.strip()}", privado=f"✍️ [dictado: {len(pieza.strip())} caracteres]")
        return True

    # ── atajos de teclado ────────────────────────────────────────────────────
    def cmd_atajo(self, raw, norm):
        seq = _ATAJO_POR_FRASE.get(nucleo_orden(norm))
        if not seq:
            self.voz.decir("No pude hacerlo, señor.")
            return
        for combo in seq:
            pyautogui.hotkey(*combo)
            time.sleep(0.04)
        self.gui.log("⌨️ " + " + ".join(seq[0]).upper() + (" …" if len(seq) > 1 else ""))
        self._pitido("ok")

    # ── ventanas ─────────────────────────────────────────────────────────────
    def cmd_ventana(self, raw, norm):
        accion = _VENTANA_POR_FRASE.get(nucleo_orden(norm))
        if accion in ("minimizar", "maximizar", "restaurar"):
            u = _u32()
            hwnd = u.GetForegroundWindow()
            if hwnd:
                u.ShowWindow(hwnd, {"minimizar": 6, "maximizar": 3, "restaurar": 9}[accion])
        elif accion in ("izquierda", "derecha"):
            pyautogui.hotkey("win", "left" if accion == "izquierda" else "right")
        elif accion == "otro_monitor":
            pyautogui.hotkey("win", "shift", "right")
        elif accion == "alternar":
            pyautogui.hotkey("alt", "tab")
        elif accion == "vista":
            pyautogui.hotkey("win", "tab")
        elif accion == "escritorio_nuevo":
            pyautogui.hotkey("ctrl", "win", "d")
        elif accion == "escritorio_sig":
            pyautogui.hotkey("ctrl", "win", "right")
        elif accion == "escritorio_ant":
            pyautogui.hotkey("ctrl", "win", "left")
        elif accion == "escritorio_cerrar":
            pyautogui.hotkey("ctrl", "win", "f4")
        elif accion == "listar":
            nombres = []
            for v in ventanas_abiertas():
                nom = re.sub(r"\.exe$", "", v["exe"]).replace("applicationframehost", "").strip()
                if nom and nom not in nombres:
                    nombres.append(nom)
            if nombres:
                self.voz.decir("Tiene abiertos: " + ", ".join(nombres[:7]) + ".")
            else:
                self.voz.decir("No veo ninguna ventana abierta.")
            return
        self._pitido("ok")

    def cmd_cerrar(self, raw, norm):
        frases_fuerza = ("fuerza el cierre de", "fuerza el cierre", "mata el proceso de", "mata el proceso", "mata",
                         "termina el proceso de", "finaliza el proceso de")
        n = nucleo_orden(norm)
        fuerza = any(n == f or n.startswith(f + " ") for f in frases_fuerza)
        cmd_frases = frases_fuerza if fuerza else ("cierra la aplicacion", "cierra el programa", "cierra la app",
                                                   "cierra", "cerrar", "cierra la ventana de", "cierra la ventana")
        resto = sin_relleno(self._resto_tras_frase(norm, cmd_frases))
        propias = {"esto", "esta", "este", "eso", "actual", "activa", "activo"}
        if not resto or set(resto.split()) <= propias:
            if fuerza:
                self.voz.decir("¿Qué quiere que cierre?")
                return
            pyautogui.hotkey("alt", "f4")                       # la ventana activa
            self._pitido("ok")
            return
        if resto in ("asistente", "alfred", normalizar(self.nombre)):
            self.cmd_salir(raw, norm)
            return
        ventanas = ventanas_abiertas()
        cand = mejores_ventanas(resto, ventanas)
        if not cand:
            self.voz.decir(f"No veo {resto} abierto.")
            return
        exe = cand[0]["exe"]
        nombre = re.sub(r"\.exe$", "", exe)
        if fuerza:
            if exe in PROTEGIDOS or not exe:
                self.voz.decir("Ese programa es del sistema; no lo voy a forzar.")
                return
            self._confirmar(f"¿Fuerzo el cierre de {nombre}? Diga sí para confirmar.",
                            lambda: self._matar(exe, nombre))
            return
        for v in ventanas:
            if v["exe"] == exe:
                cerrar_ventana(v["hwnd"])
        self.gui.log(f"🗙 Cerrando {nombre}")
        self.voz.decir(f"Cerrando {nombre}.")

    def _matar(self, exe, nombre):
        r = subprocess.run([ruta_sistema("taskkill"), "/F", "/IM", exe], capture_output=True, creationflags=SIN_VENTANA)
        self.voz.decir(f"Cerrando {nombre}." if r.returncode == 0 else "No pude hacerlo, señor.")

    def cmd_cambiar_a(self, raw, norm):
        frases = next(c for c in COMANDOS if c["id"] == "cambiar_a")["frases"]
        resto = sin_relleno(self._resto_tras_frase(norm, frases))
        if hay(resto, "cancion", "siguiente", "anterior", "musica", "tema") or resto.startswith("modo"):
            self.cmd_media(raw, norm)                           # «cambia a la siguiente canción»
            return
        if not resto:
            self.voz.decir("¿A qué ventana quiere cambiar?")
            return
        cand = mejores_ventanas(resto, ventanas_abiertas())
        if not cand:
            self.voz.decir(f"No veo {resto} abierto.")
            return
        enfocar_ventana(cand[0]["hwnd"])
        self.gui.log(f"🪟 Cambié a «{cand[0]['titulo'][:60]}»")
        self.voz.decir(f"Cambiando a {re.sub(r'[.]exe$', '', cand[0]['exe'])}.")

    # ── ratón ────────────────────────────────────────────────────────────────
    def cmd_raton(self, raw, norm):
        n = nucleo_orden(norm)
        if self.grid is not None:
            self.gui.ui(self._grid_cerrar)
        if n.startswith(("mueve", "centra", "mouse al centro")):
            if hay(n, "centro", "centra"):
                w, h = pyautogui.size()
                pyautogui.moveTo(w // 2, h // 2)
            else:
                mov = parse_movimiento(n)
                if not mov:
                    self.voz.decir("¿Hacia dónde, señor?")
                    return
                pyautogui.moveRel(*mov)
        elif hay(n, "pagina", "desplaza", "desplazate", "scroll"):
            muescas = parse_desplazamiento(n)
            if muescas is None:
                self.voz.decir("¿Hacia arriba o hacia abajo?")
                return
            pyautogui.scroll(muescas * 120)
        elif hay(n, "doble"):
            pyautogui.doubleClick()
        elif hay(n, "derecho"):
            pyautogui.rightClick()
        else:
            pyautogui.click()
        self._pitido("ok")

    # ── cuadrícula del ratón (clic por voz en cualquier punto de la pantalla) ─
    def cmd_cuadricula(self, raw, norm):
        self.gui.ui(self._grid_abrir)
        self.voz.decir("Cuadrícula activada. Diga un número del uno al nueve.")

    def _grid_abrir(self):                                       # hilo de la interfaz
        self._grid_cerrar()
        sw, sh = self.gui.winfo_screenwidth(), self.gui.winfo_screenheight()
        g = {"rect": (0, 0, sw, sh), "hist": [], "win": None}
        self.grid = g
        self._grid_dibujar()
        self.gui.after(60000, lambda: self._grid_expirar(g))

    def _grid_expirar(self, g):
        if self.grid is g:
            self._grid_cerrar()

    def _grid_cerrar(self):
        g, self.grid = self.grid, None
        if g and g.get("win") is not None:
            try:
                g["win"].destroy()
            except tk.TclError:
                pass

    def _grid_dibujar(self):
        g = self.grid
        if g is None:
            return
        if g.get("win") is not None:
            try:
                g["win"].destroy()
            except tk.TclError:
                pass
        x0, y0, x1, y1 = g["rect"]
        w, h = max(3, x1 - x0), max(3, y1 - y0)
        try:
            top = tk.Toplevel(self.gui)
            top.overrideredirect(True)
            top.attributes("-topmost", True)
            top.attributes("-transparentcolor", "#010203")       # lo demás se ve y deja pasar los clics
            top.configure(bg="#010203")
            top.geometry(f"{w}x{h}+{x0}+{y0}")
            cv = tk.Canvas(top, width=w, height=h, bg="#010203", highlightthickness=0)
            cv.pack()
            borde, num = "#00e5ff", max(10, min(w, h) // 9)
            for k in (1, 2):
                cv.create_line(w * k / 3, 0, w * k / 3, h, fill=borde, width=2)
                cv.create_line(0, h * k / 3, w, h * k / 3, fill=borde, width=2)
            cv.create_rectangle(1, 1, w - 1, h - 1, outline=borde, width=3)
            for i in range(1, 10):
                f, c = divmod(i - 1, 3)
                cx, cy = (c + 0.5) * w / 3, (f + 0.5) * h / 3
                cv.create_text(cx + 2, cy + 2, text=str(i), fill="#000000", font=("Segoe UI", num, "bold"))
                cv.create_text(cx, cy, text=str(i), fill="#ffffff", font=("Segoe UI", num, "bold"))
            g["win"] = top
        except tk.TclError:
            logging.exception("Cuadrícula")
            self.grid = None

    def _grid_elegir(self, n):                                   # hilo de la interfaz
        g = self.grid
        if g is None:
            return
        x0, y0, x1, y1 = g["rect"]
        if (x1 - x0) < 30 or (y1 - y0) < 30:
            return                                               # ya no se puede afinar más: di «clic»
        g["hist"].append(g["rect"])
        g["rect"] = celda_cuadricula(g["rect"], n)
        x0, y0, x1, y1 = g["rect"]
        pyautogui.moveTo((x0 + x1) // 2, (y0 + y1) // 2)
        self._grid_dibujar()

    def _grid_atras(self):
        g = self.grid
        if g is not None and g["hist"]:
            g["rect"] = g["hist"].pop()
            x0, y0, x1, y1 = g["rect"]
            pyautogui.moveTo((x0 + x1) // 2, (y0 + y1) // 2)
            self._grid_dibujar()

    def _grid_reiniciar(self):
        self._grid_abrir()

    def _grid_clic(self, tipo):
        g = self.grid
        if g is None:
            return
        x0, y0, x1, y1 = g["rect"]
        self._grid_cerrar()

        def hacer():
            pyautogui.moveTo((x0 + x1) // 2, (y0 + y1) // 2)
            if tipo == "doble":
                pyautogui.doubleClick()
            elif tipo == "derecho":
                pyautogui.rightClick()
            else:
                pyautogui.click()
        self.gui.after(120, hacer)                               # deja que la cuadrícula desaparezca antes del clic

    def _atender_grid(self, norm):
        n = nucleo_orden(norm)
        t = set(n.split())
        cel = numero_cuadricula(n)
        if cel:
            self.gui.ui(self._grid_elegir, cel)
        elif t & {"doble", "double"}:
            self.gui.ui(self._grid_clic, "doble")
        elif t & {"derecho", "right"}:
            self.gui.ui(self._grid_clic, "derecho")
        elif t & {"clic", "click", "aqui", "ahi", "selecciona", "pulsa", "presiona", "toca", "aprieta"}:
            self.gui.ui(self._grid_clic, "izq")
        elif t & {"atras", "regresa", "back", "undo", "deshaz"}:
            self.gui.ui(self._grid_atras)
        elif t & {"reinicia", "reset", "empezar", "nuevo"} or n in ("otra vez", "de nuevo", "empieza de nuevo"):
            self.gui.ui(self._grid_reiniciar)
        elif t & {"cancela", "cancelar", "salir", "listo", "cancel", "exit", "close", "cierra", "termina", "basta"}:
            self.gui.ui(self._grid_cerrar)
            self.voz.decir("Cuadrícula cerrada.")
        return True                                              # en este modo, lo demás se ignora (no es una orden)

    # ── captura de pantalla ──────────────────────────────────────────────────
    def cmd_captura(self, raw, norm):
        region = None
        if hay(norm, "ventana"):
            r = rect_ventana(_u32().GetForegroundWindow())
            if r:
                region = (r[0], r[1], max(1, r[2] - r[0]), max(1, r[3] - r[1]))
        ruta = capturar_pantalla(CARPETA_CAPTURAS, region)
        self.gui.log(f"📸 Captura guardada: {ruta}")
        self.voz.decir("Captura guardada. También está en el portapapeles.")

    # ── estado del sistema ───────────────────────────────────────────────────
    @staticmethod
    def _frase_bateria(b):
        if not b:
            return "Este equipo no tiene batería."
        estado = ", cargando" if b["cargando"] else ", con el cargador desconectado"
        extra = ""
        if not b["cargando"] and b["seg"]:
            extra = f" Le quedan unos {texto_duracion(b['seg'] // 60 * 60)}."
        return f"Tiene {b['pct']} por ciento de batería{estado}.{extra}"

    def cmd_estado_pc(self, raw, norm):
        t = set(norm.split())
        if "bateria" in t:
            self.voz.decir(self._frase_bateria(info_bateria()))
        elif t & {"procesador", "cpu"}:
            self.voz.decir(f"El procesador está al {round(info_cpu())} por ciento.")
        elif t & {"memoria", "ram"}:
            pct, total, libre = info_ram()
            self.voz.decir(f"La memoria está al {pct} por ciento. Quedan {formatear_numero(round(libre, 1))} gigas libres "
                           f"de {total:.0f}.")
        elif t & {"disco", "espacio"}:
            _, libre, total = info_disco()
            self.voz.decir(f"Quedan {libre:.0f} gigas libres de {total:.0f} en el disco.")
        elif t & {"consume", "consumiendo", "procesos", "pesados"}:
            top = procesos_pesados(3)
            self.voz.decir("Lo que más memoria usa: " + ", ".join(
                f"{n}, {formatear_numero(round(mb / 1024, 1))} gigas" if mb >= 1024 else f"{n}, {mb:.0f} megas"
                for n, mb in top) + ".")
        elif t & {"wifi", "wi"}:
            ssid = nombre_wifi()
            self.voz.decir(f"Está conectado a la red {ssid}." if ssid else "No veo ninguna red Wi-Fi conectada.")
        elif t & {"internet", "conectado", "red"}:
            self.voz.decir("Hay conexión a internet." if ping_internet() else "No hay conexión a internet.")
        elif "ip" in t:
            ip = ip_local()
            self.voz.decir(f"Su dirección IP es {ip.replace('.', ' punto ')}." if ip else "No pude obtener la dirección IP.")
        elif t & {"encendida", "encendido", "uptime"}:
            self.voz.decir(f"Lleva encendida {texto_uptime(info_uptime())}.")
        else:                                                    # resumen
            partes = []
            b = info_bateria()
            if b:
                partes.append(f"batería al {b['pct']} por ciento" + (", cargando" if b["cargando"] else ""))
            partes.append(f"procesador al {round(info_cpu(0.4))} por ciento")
            ram = info_ram()
            if ram:
                partes.append(f"memoria al {ram[0]} por ciento")
            _, libre, _ = info_disco()
            partes.append(f"{libre:.0f} gigas libres en el disco")
            self.voz.decir("Estado del sistema: " + ", ".join(partes) + ".")

    def _vigilar_bateria(self):
        """Avisa por voz cuando la batería está baja y no hay cargador (aviso_bateria / bateria_minima en la config)."""
        avisado = None
        time.sleep(20)
        while self.activo:
            try:
                if self.cfg.get("aviso_bateria") is not False:
                    b = info_bateria()
                    if b is None:
                        return                                   # este equipo no tiene batería
                    minimo = int(self.cfg.get("bateria_minima") or 20)
                    nivel = None if b["cargando"] else ("critico" if b["pct"] <= 10 else "bajo" if b["pct"] <= minimo else None)
                    if nivel is None:
                        avisado = None
                    elif nivel != avisado and not self.voz.ocupada():
                        avisado = nivel
                        self.gui.log(f"🔋 Batería baja: {b['pct']} %")
                        self.voz.decir(f"Señor, la batería está al {b['pct']} por ciento. Conecte el cargador.")
            except Exception:
                logging.exception("Vigilante de batería")
            for _ in range(45):                                  # se despierta cada segundo solo para ver si hay que salir
                if not self.activo:
                    return
                time.sleep(1)

    def cmd_wifi(self, raw, norm):
        if hay(norm, "conecta", "conectar", "reconecta", "enciende", "prende", "activa"):
            ssid = self._ssid_previo
            if not ssid:
                self.voz.decir("No sé a qué red conectarme. Conéctese una vez y la recordaré.")
                return
            subprocess.run([ruta_sistema("netsh"), "wlan", "connect", f"name={ssid}"], capture_output=True, creationflags=SIN_VENTANA)
            self.voz.decir("Conectando al Wi-Fi.")
        else:
            ssid = nombre_wifi()
            if ssid:
                self._ssid_previo = ssid
                self.cfg.set("wifi_ultimo", ssid)
            subprocess.run([ruta_sistema("netsh"), "wlan", "disconnect"], capture_output=True, creationflags=SIN_VENTANA)
            self.voz.decir("Wi-Fi desconectado.")

    # ── ajustes y herramientas de Windows ────────────────────────────────────
    def cmd_configuracion(self, raw, norm):
        t = set(norm.split())
        mejor, mejor_n = None, 0
        for claves, uri, nombre in AJUSTES_WIN:
            n = len(t & set(claves))
            if n > mejor_n:
                mejor, mejor_n = (uri, nombre), n
        if hay(norm, "avion"):
            mejor = ("ms-settings:network-airplanemode", "modo avión")
        if mejor:
            os.startfile(mejor[0])
            self.voz.decir(f"Abriendo ajustes de {mejor[1]}.")
        else:
            os.startfile("ms-settings:")
            self.voz.decir("Abriendo ajustes de Windows.")

    def cmd_herramientas(self, raw, norm):
        texto = f" {norm} "
        for frases, cmd, nombre in HERRAMIENTAS_WIN:
            if any(f" {f} " in texto for f in frases):
                nueva_consola = cmd[0] in ("cmd.exe", "powershell.exe")
                try:
                    subprocess.Popen(comando_sistema(cmd), shell=False,
                                     creationflags=subprocess.CREATE_NEW_CONSOLE if nueva_consola else 0)
                except OSError:
                    logging.exception("Herramienta de Windows")
                    self.voz.decir("No pude hacerlo, señor.")
                    return
                self.voz.decir(f"Abriendo {nombre}.")
                return
        self.voz.decir("No pude hacerlo, señor.")

    def cmd_tema(self, raw, norm):
        if hay(norm, "oscuro"):
            oscuro = True
        elif hay(norm, "claro"):
            oscuro = False
        else:
            oscuro = not modo_oscuro_actual()
        fijar_tema(oscuro)
        self.voz.decir("Modo oscuro activado." if oscuro else "Modo claro activado.")

    def cmd_portapapeles(self, raw, norm):
        if hay(norm, "borra", "vacia", "limpia", "elimina", "clear", "empty"):
            vaciar_portapapeles()
            self.voz.decir("Portapapeles vaciado.")
            return
        txt = (leer_portapapeles() or "").strip()
        if not txt:
            self.voz.decir("El portapapeles está vacío.")
            return
        self.gui.log(f"📋 Portapapeles: {txt[:120]}", privado=f"📋 [portapapeles leído: {len(txt)} caracteres]")
        self.voz.decir(txt if len(txt) <= 350 else txt[:350] + "… y sigue.", privado=True)

    def cmd_papelera(self, raw, norm):
        if hay(norm, "vacia", "vaciar", "limpia", "elimina", "borra"):
            def hacer():
                self.voz.decir("Papelera vaciada." if vaciar_papelera() else "No pude hacerlo, señor.")
            self._confirmar("¿Vacío la papelera? Diga sí para confirmar.", hacer)
        else:
            subprocess.Popen([ruta_sistema("explorer"), "shell:RecycleBinFolder"])
            self.voz.decir("Abriendo la papelera.")


# ══════════════════════════════════════════════════════════════════════════════
#  3.2 · CONTROL REMOTO: API HTTP + JSON con clave, y una página para el móvil
#
#  Base para controlar Alfred desde otros dispositivos (móvil, tablet, otro PC, un atajo, Home Assistant…).
#  Desactivado por defecto. Con la opción «red» apagada solo acepta a este mismo PC; con ella encendida acepta
#  únicamente direcciones privadas (Wi-Fi de casa, Tailscale…) y siempre exige la clave. Documentación:
#  alfred_remoto_API.md
# ══════════════════════════════════════════════════════════════════════════════
API_REMOTA = 1
_RED_TAILSCALE = ipaddress.ip_network("100.64.0.0/10")


def _tipo_evento(msj):
    m = (msj or "").lstrip()
    if m.startswith(("🎤", "📱", "👂")):
        return "orden"
    if m.startswith("🗣"):
        return "voz"
    if m.startswith(("⚠", "❌", "❓")):
        return "aviso"
    return "log"


class BusEventos:
    """Lo que Alfred oye, hace y dice, numerado, para que otro dispositivo lo siga (sondeo largo). Siempre activo:
    guardar 300 líneas no cuesta nada, y así un cliente que se conecta ve lo último que pasó."""

    def __init__(self, maximo=300):
        self._ev = deque(maxlen=maximo)
        self._n = 0
        self._cv = threading.Condition()

    def publicar(self, tipo, texto):
        with self._cv:
            self._n += 1
            self._ev.append({"id": self._n, "hora": time.strftime("%H:%M:%S"), "tipo": tipo, "texto": str(texto)[:600]})
            self._cv.notify_all()

    @property
    def ultimo(self):
        return self._n

    def desde(self, n, espera=0.0, ultimos=None):
        """([eventos con id > n], último id). Con espera > 0 aguarda hasta que haya alguno. ultimos=K: solo los K
        más recientes (para la primera conexión de un cliente)."""
        fin = time.time() + espera
        with self._cv:
            while True:
                res = [e for e in self._ev if e["id"] > n]
                if res or espera <= 0:
                    return (res[-ultimos:] if ultimos else res), self._n
                resto = fin - time.time()
                if resto <= 0:
                    return [], self._n
                self._cv.wait(resto)


BUS = BusEventos()


def ip_permitida(ip):
    """Solo este PC y redes privadas (casa, oficina, Tailscale). Nunca direcciones públicas de internet."""
    try:
        a = ipaddress.ip_address(str(ip).split("%")[0])
    except ValueError:
        return False
    if a.version == 6 and a.ipv4_mapped:
        a = a.ipv4_mapped
    return bool(a.is_loopback or a.is_private or a.is_link_local or (a.version == 4 and a in _RED_TAILSCALE))


class _ServidorHTTP(ThreadingHTTPServer):
    allow_reuse_address = False          # en Windows SO_REUSEADDR deja que otro programa se cuele en el mismo puerto
    daemon_threads = True


PAGINA_REMOTA = r"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#070b12"><meta name="apple-mobile-web-app-capable" content="yes">
<title>__NOMBRE__ remoto</title>
<style>
:root{--bg:#070b12;--card:#0e1623;--line:#1d2b3f;--tx:#e6edf6;--mu:#8aa0b8;--ac:#22d3ee;--ok:#34d399;--er:#f87171;--wa:#fbbf24}
*{box-sizing:border-box}html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--tx);font:16px system-ui,-apple-system,Segoe UI,sans-serif;display:flex;flex-direction:column;
padding:env(safe-area-inset-top) 12px calc(10px + env(safe-area-inset-bottom))}
header{display:flex;align-items:center;gap:10px;padding:12px 2px}
#punto{width:12px;height:12px;border-radius:50%;background:var(--wa);box-shadow:0 0 10px currentColor;color:var(--wa)}
h1{font-size:20px;margin:0;font-weight:600;flex:1}h1 small{display:block;color:var(--mu);font-size:12px;font-weight:400}
.rejilla{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:10px}
button{font:inherit;color:var(--tx);background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 4px;cursor:pointer}
button:active{background:#13233a;border-color:var(--ac)}
#feed{flex:1;min-height:120px;overflow:auto;background:#050810;border:1px solid var(--line);border-radius:12px;padding:8px 10px;font-size:14px}
.e{padding:3px 0;border-bottom:1px solid #0c1420;word-break:break-word}.e b{color:var(--mu);font-weight:400;font-size:12px;margin-right:6px}
.orden{color:#7dd3fc;font-weight:600}.voz{color:#6ee7b7}.aviso{color:var(--wa)}.log{color:#9fb3c8}
form{display:flex;gap:8px;margin-top:10px}
input{flex:1;font:inherit;color:var(--tx);background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px}
input:focus{outline:none;border-color:var(--ac)}form button{padding:12px 18px;background:var(--ac);color:#04121a;border:0;font-weight:600}
</style></head><body>
<header><div id="punto"></div><h1><span id="nombre">__NOMBRE__</span><small id="sub">conectando…</small></h1><button id="otra" title="Cambiar de clave" style="padding:8px 10px">🔑</button></header>
<div class="rejilla" id="botones"></div>
<div id="feed"></div>
<form id="f"><input id="t" autocomplete="off" autocapitalize="none" placeholder="Escribe una orden (sin decir el nombre)…"><button>Enviar</button></form>
<script>
const $=s=>document.querySelector(s);
let ultimo=0,vivo=true;
localStorage.removeItem('alfred_t');
async function abrirSesion(t){const r=await fetch('/api/sesion',{method:'POST',headers:{'Authorization':'Bearer '+t,'X-Alfred-Req':'1'}});return r.ok}
const h=new URLSearchParams(location.hash.slice(1));
if(h.get('t')){const t=h.get('t');history.replaceState(null,'',location.pathname);abrirSesion(t).then(ok=>{if(!ok)pedirClave()})}
const BOTONES=[['⏸','pausa'],['▶️','dale play'],['⏮','canción anterior'],['⏭','siguiente canción'],['🔉','baja el volumen'],['🔊','sube el volumen'],['🔇','silencio'],['🎵','qué suena'],['🕒','qué hora es'],['📸','captura de pantalla'],['🔒','bloquea la pantalla'],['✅','sí']];
BOTONES.forEach(([ico,ord])=>{const b=document.createElement('button');b.textContent=ico;b.title=ord;b.onclick=()=>enviar(ord);$('#botones').append(b)});
async function api(ruta,cuerpo){
  const r=await fetch(ruta,{method:cuerpo?'POST':'GET',credentials:'same-origin',headers:{'X-Alfred-Req':'1','Content-Type':'application/json'},body:cuerpo?JSON.stringify(cuerpo):undefined});
  if(r.status===401){pedirClave();throw new Error('clave')}
  if(!r.ok)throw new Error('http '+r.status);return r.json()}
function pedirClave(){const c=prompt('Clave de acceso (☰ Menú → Remoto en el PC):');if(c){abrirSesion(c.trim()).then(ok=>{ultimo=0;if(!ok)alert('Clave incorrecta')})}}
$('#otra').onclick=()=>{pedirClave()};
function pintar(lista){const f=$('#feed'),abajo=f.scrollTop+f.clientHeight>=f.scrollHeight-40;
  for(const e of lista){const d=document.createElement('div');d.className='e '+e.tipo;const h=document.createElement('b');h.textContent=e.hora;d.append(h,document.createTextNode(e.texto));f.append(d);ultimo=Math.max(ultimo,e.id)}
  while(f.children.length>300)f.firstChild.remove();if(abajo)f.scrollTop=f.scrollHeight}
async function enviar(texto){texto=(texto||'').trim();if(!texto)return;
  try{const d=await api('/api/orden',{texto,espera:4});pintar(d.eventos||[])}catch(e){pintar([{id:ultimo,hora:'',tipo:'aviso',texto:'No pude enviar: '+e.message}])}}
$('#f').onsubmit=e=>{e.preventDefault();const v=$('#t').value;$('#t').value='';enviar(v)};
async function estado(){try{const s=await api('/api/estado');$('#nombre').textContent=s.nombre+' OS';
  $('#sub').textContent=(s.escuchando?'escuchando':'sin micrófono')+' · v'+s.version;$('#punto').style.color=$('#punto').style.background=s.escuchando?'var(--ok)':'var(--wa)'}
  catch(e){$('#sub').textContent='sin conexión';$('#punto').style.color=$('#punto').style.background='var(--er)'}}
async function bucle(){while(vivo){try{
  const d=await api('/api/eventos?desde='+ultimo+'&espera=20'+(ultimo?'':'&ultimos=40'));pintar(d.eventos||[]);if(!d.eventos.length)ultimo=Math.max(ultimo,d.ultimo)
  }catch(e){await new Promise(r=>setTimeout(r,3000))}}}
if(!T)pedirClave();estado();setInterval(estado,10000);bucle();
</script></body></html>"""


class _ManejadorRemoto(BaseHTTPRequestHandler):
    server_version = "AlfredRemoto/1"
    timeout = 60

    def log_message(self, formato, *args):       # silencio: las peticiones no van a la consola
        pass

    # ── utilidades ───────────────────────────────────────────────────────────
    def _enviar(self, codigo, cuerpo, tipo="application/json; charset=utf-8"):
        datos = cuerpo if isinstance(cuerpo, bytes) else json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        if getattr(self, "_cookie", None):
            self.send_header("Set-Cookie", self._cookie)
            self._cookie = None
        if tipo.startswith("text/html"):
            self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; "
                             "style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'none'")
            self.send_header("X-Frame-Options", "DENY")
        origen = self.server.ctl.cfg.get("remoto_cors")
        if origen:
            self.send_header("Access-Control-Allow-Origin", str(origen))
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Alfred-Token")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(datos)

    def _clave_cabecera(self):
        """La clave solo viaja en cabeceras (Authorization: Bearer o X-Alfred-Token), nunca en la URL: las URL quedan en
        historiales, registros y cabeceras Referer."""
        h = self.headers.get("Authorization", "")
        if h.lower().startswith("bearer "):
            return h[7:].strip()
        return self.headers.get("X-Alfred-Token") or ""

    def _cookie_sesion(self):
        for parte in (self.headers.get("Cookie") or "").split(";"):
            k, _, v = parte.strip().partition("=")
            if k == "alfred_s":
                return v
        return ""

    def _origen_ok(self):
        """Defensa CSRF para quien entra con cookie: cabecera propia (un formulario de otra web no puede ponerla) y, si
        el navegador manda Origin, que sea esta misma dirección."""
        if self.headers.get("X-Alfred-Req") != "1":
            return False
        origen = self.headers.get("Origin")
        return not origen or urlparse(origen).netloc == (self.headers.get("Host") or "")

    def _host_ok(self):
        """Contra DNS rebinding: solo se atiende por IP, localhost, el nombre del PC o nombres .local / .ts.net."""
        host = (self.headers.get("Host") or "").strip().lower()
        host = host[1:host.index("]")] if host.startswith("[") and "]" in host else host.rsplit(":", 1)[0]
        if host in ("localhost", socket.gethostname().lower()) or host.endswith((".local", ".ts.net")):
            return True
        try:
            ipaddress.ip_address(host)
            return True
        except ValueError:
            return False

    def _entrada(self):
        """IP permitida y no bloqueada. Devuelve la IP, o None tras contestar el error."""
        self._cookie = None
        ip = self.client_address[0]
        if not ip_permitida(ip):
            self._enviar(403, {"ok": False, "error": "red no permitida"})
            return None
        if not self._host_ok():
            self._enviar(403, {"ok": False, "error": "dirección no permitida"})
            return None
        if self.server.ctl.bloqueado(ip):
            self._enviar(429, {"ok": False, "error": "demasiados intentos; espera unos minutos"})
            return None
        return ip

    def _autenticar(self, ip, solo_clave=False):
        """Entra con la clave (cabecera) o con la cookie de sesión HttpOnly. Solo una clave equivocada cuenta como intento
        fallido (una cookie caducada no bloquea al navegador)."""
        ctl = self.server.ctl
        clave = self._clave_cabecera()
        if clave:
            if ctl.clave_valida(clave):
                ctl.acierto(ip)
                return True
            ctl.fallo(ip)
        elif not solo_clave and ctl.sesion_valida(self._cookie_sesion()):
            if self.command == "POST" and not self._origen_ok():
                self._enviar(403, {"ok": False, "error": "origen no permitido"})
                return False
            return True
        self._enviar(401, {"ok": False, "error": "clave incorrecta"})
        return False

    def _cuerpo(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = 0
        if n <= 0 or n > 16384:
            return {}
        crudo = self.rfile.read(n).decode("utf-8", "replace")
        try:
            d = json.loads(crudo)
        except ValueError:
            d = {k: v[0] for k, v in parse_qs(crudo).items()}
        return d if isinstance(d, dict) else {}

    @staticmethod
    def _numero(valor, defecto, minimo, maximo):
        try:
            return max(minimo, min(maximo, float(valor)))
        except (TypeError, ValueError):
            return defecto

    # ── rutas ────────────────────────────────────────────────────────────────
    def do_OPTIONS(self):
        if self._entrada():
            self._enviar(204, b"", "text/plain")

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        ip = self._entrada()
        if ip is None:
            return
        ctl, url = self.server.ctl, urlparse(self.path)
        ruta, q = url.path.rstrip("/") or "/", parse_qs(url.query)
        try:
            if ruta in ("/", "/index.html"):                 # la página no lleva secretos: la clave la pide ella
                html = PAGINA_REMOTA.replace("__NOMBRE__", ctl.alfred.gui.nombre_os().replace("<", ""))
                return self._enviar(200, html.encode("utf-8"), "text/html; charset=utf-8")
            if ruta == "/api/ping":                          # sirve para comprobar que es un Alfred (sin datos)
                return self._enviar(200, {"app": "alfred", "api": API_REMOTA})
            if not ruta.startswith("/api/"):
                return self._enviar(404, {"ok": False, "error": "no existe"})
            if not self._autenticar(ip):
                return
            if ruta == "/api/estado":
                return self._enviar(200, ctl.estado())
            if ruta == "/api/comandos":
                return self._enviar(200, {"comandos": [
                    {"id": c["id"], "ejemplo": c.get("ejemplo", ""), "descripcion": c.get("desc", ""),
                     "seccion": c.get("seccion", "")} for c in COMANDOS]})
            if ruta == "/api/eventos":
                desde = int(self._numero((q.get("desde") or ["0"])[0], 0, 0, 10 ** 12))
                espera = self._numero((q.get("espera") or ["0"])[0], 0, 0, 25)
                ultimos = int(self._numero((q.get("ultimos") or ["0"])[0], 0, 0, 300)) or None
                ev, ult = BUS.desde(desde, espera, ultimos)
                return self._enviar(200, {"ok": True, "eventos": ev, "ultimo": ult})
            return self._enviar(404, {"ok": False, "error": "no existe"})
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception as e:
            logging.exception("Remoto GET %s", ruta)
            self._enviar(500, {"ok": False, "error": "error interno"})

    def do_POST(self):
        ip = self._entrada()
        if ip is None:
            return
        ctl, ruta = self.server.ctl, urlparse(self.path).path.rstrip("/")
        try:
            if not ruta.startswith("/api/"):
                return self._enviar(404, {"ok": False, "error": "no existe"})
            if ruta == "/api/sesion":                        # clave -> cookie de sesión HttpOnly + SameSite=Strict
                if not self._autenticar(ip, solo_clave=True):
                    return
                self._cookie = (f"alfred_s={ctl.crear_sesion()}; HttpOnly; SameSite=Strict; Path=/; Max-Age=43200"
                                + ("; Secure" if ctl.https else ""))
                return self._enviar(200, {"ok": True})
            if ruta == "/api/salir":
                if not self._autenticar(ip):
                    return
                ctl.cerrar_sesion(self._cookie_sesion())
                self._cookie = "alfred_s=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0"
                return self._enviar(200, {"ok": True})
            if not self._autenticar(ip):
                return
            d = self._cuerpo()
            texto = str(d.get("texto") or "").strip()[:500]
            if ruta == "/api/orden":
                if not texto:
                    return self._enviar(400, {"ok": False, "error": "falta «texto»"})
                espera = self._numero(d.get("espera"), 4, 0, 15)
                desde = BUS.ultimo
                ctl.ejecutar(texto)
                return self._enviar(200, {"ok": True, "eventos": ctl.recoger(desde, espera), "ultimo": BUS.ultimo})
            if ruta == "/api/decir":
                if not texto:
                    return self._enviar(400, {"ok": False, "error": "falta «texto»"})
                ctl.alfred.voz.decir(texto)
                return self._enviar(200, {"ok": True})
            return self._enviar(404, {"ok": False, "error": "no existe"})
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception as e:
            logging.exception("Remoto POST %s", ruta)
            self._enviar(500, {"ok": False, "error": "error interno"})


class ServidorRemoto:
    def __init__(self, alfred, cfg):
        self.alfred, self.cfg = alfred, cfg
        self.srv, self.puerto, self.https, self._lan = None, None, False, False
        self._fallos = {}                                  # ip -> (fallos seguidos, bloqueada hasta)
        self._lock = threading.Lock()
        self._sesiones = {}                                # id de sesión (cookie) -> caduca; solo en memoria

    # ── clave ────────────────────────────────────────────────────────────────
    def token(self):
        t = self.cfg.get_secreto("remoto_token")           # guardada con DPAPI (solo tu cuenta de Windows la abre)
        if not t:
            t = secrets.token_urlsafe(24)
            self.cfg.set_secreto("remoto_token", t)
        return t

    def crear_sesion(self):
        sid = secrets.token_urlsafe(32)
        with self._lock:
            ahora = time.time()
            self._sesiones = {k: v for k, v in self._sesiones.items() if v > ahora}
            while len(self._sesiones) >= 20:                # como mucho 20 dispositivos a la vez
                self._sesiones.pop(min(self._sesiones, key=self._sesiones.get))
            self._sesiones[sid] = ahora + 43200
        return sid

    def sesion_valida(self, sid):
        if not sid:
            return False
        cand = str(sid).encode("utf-8", "ignore")
        with self._lock:
            ahora, ok = time.time(), False
            for k, exp in list(self._sesiones.items()):
                if exp <= ahora:
                    del self._sesiones[k]
                elif hmac.compare_digest(k.encode("ascii"), cand):
                    ok = True
            return ok

    def cerrar_sesion(self, sid):
        with self._lock:
            self._sesiones.pop(sid, None)

    def nueva_clave(self):
        self.cfg.set_secreto("remoto_token", secrets.token_urlsafe(24))
        with self._lock:
            self._sesiones.clear()                          # las sesiones abiertas con la clave anterior dejan de valer
        self.alfred.gui.log("🔑 Control remoto: clave nueva. Los dispositivos ya enlazados tendrán que volver a escribirla.")
        return self.token()

    def clave_valida(self, candidata):
        return bool(candidata) and hmac.compare_digest(str(candidata).encode("utf-8"), self.token().encode("utf-8"))

    def bloqueado(self, ip):
        with self._lock:
            return time.time() < self._fallos.get(ip, (0, 0.0))[1]

    def fallo(self, ip):
        with self._lock:
            n, _ = self._fallos.get(ip, (0, 0.0))
            n += 1
            hasta = time.time() + 300 if n >= 8 else 0.0     # 8 claves malas seguidas: 5 minutos de castigo
            self._fallos[ip] = (0 if hasta else n, hasta)
            if len(self._fallos) > 200:
                self._fallos.clear()
        self.alfred.gui.log(f"🔒 Control remoto: clave incorrecta desde {ip}" + (" (bloqueada 5 min)" if hasta else ""))

    def acierto(self, ip):
        with self._lock:
            self._fallos.pop(ip, None)

    # ── ciclo de vida ────────────────────────────────────────────────────────
    def activo(self):
        return self.srv is not None

    def aplicar_config(self):
        """Arranca, para o reinicia el servidor según lo que diga la configuración."""
        quiere, lan = bool(self.cfg.get("remoto_activo")), bool(self.cfg.get("remoto_lan"))
        if self.srv and (not quiere or lan != self._lan):
            self.detener()
        if quiere and not self.srv:
            self.iniciar()

    def iniciar(self):
        lan = bool(self.cfg.get("remoto_lan"))
        host, srv, ultimo_error = ("0.0.0.0" if lan else "127.0.0.1"), None, None
        for puerto in range(PUERTO_REMOTO, PUERTO_REMOTO + 6):
            try:
                srv = _ServidorHTTP((host, puerto), _ManejadorRemoto)
                break
            except OSError as e:
                ultimo_error = e
        if srv is None:
            logging.error("Control remoto: no pude abrir ningún puerto: %s", ultimo_error)
            self.alfred.gui.log(f"⚠️ Control remoto: no pude abrir el puerto {PUERTO_REMOTO} ({ultimo_error}).")
            return False
        srv.ctl = self
        self.https = False
        cert, clave = (self.cfg.get("remoto_cert") or ""), (self.cfg.get("remoto_clave_tls") or "")
        if cert and clave and os.path.exists(cert) and os.path.exists(clave):    # HTTPS opcional (certificado propio)
            try:
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ctx.load_cert_chain(cert, clave)
                srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
                self.https = True
            except Exception:
                logging.exception("Control remoto: el certificado no sirvió, sigo sin cifrar")
        self.srv, self.puerto, self._lan = srv, srv.server_address[1], lan
        threading.Thread(target=srv.serve_forever, daemon=True, name="remoto").start()
        self.token()
        self.alfred.gui.log(f"📱 Control remoto activo en el puerto {self.puerto}"
                            + (" (visible en tu red)" if lan else " (solo este PC)") + ".")
        return True

    def detener(self):
        srv, self.srv = self.srv, None
        if srv is not None:
            try:
                srv.shutdown()
                srv.server_close()
            except Exception:
                logging.exception("Control remoto: al parar")
            self.alfred.gui.log("📱 Control remoto detenido.")

    def direcciones(self):
        """Enlaces (con la clave) para abrir en el otro dispositivo."""
        if not self.srv:
            return []
        esquema, t = ("https" if self.https else "http"), self.token()
        if not self._lan:
            return [f"{esquema}://127.0.0.1:{self.puerto}/#t={t}"]
        ips = []
        principal = ip_local()
        if principal:
            ips.append(principal)
        try:
            for i in socket.gethostbyname_ex(socket.gethostname())[2]:
                if i not in ips and not i.startswith(("127.", "169.254.")):
                    ips.append(i)
        except OSError:
            pass
        return [f"{esquema}://{ip}:{self.puerto}/#t={t}" for ip in ips]      # en el # (fragmento): no viaja ni se registra

    # ── lo que hace la API ───────────────────────────────────────────────────
    def estado(self):
        a = self.alfred
        info = {"app": "alfred", "api": API_REMOTA, "nombre": a.nombre, "version": VERSION, "escuchando": bool(a.escuchando),
                "idioma": a.voz.idioma_actual(), "dictado": bool(a.dictado), "hora": time.strftime("%H:%M:%S"),
                "reproductor": None}
        try:
            p = a.reproductor_activo()
            if p:
                info["reproductor"] = p.get("nombre")
        except Exception:
            pass
        return info

    def ejecutar(self, texto):
        """Ejecuta una orden escrita como si la hubieras dicho (sin palabra de activación)."""
        self.alfred.procesar_remoto(texto)

    @staticmethod
    def recoger(desde, espera):
        """Espera la respuesta a una orden: hasta que haya algo hablado/avisado y se calme, o se acabe el tiempo."""
        t0, visto, calma = time.time(), BUS.ultimo, None
        while time.time() - t0 < espera:
            time.sleep(0.1)
            if BUS.ultimo != visto:
                visto, calma = BUS.ultimo, time.time()
            elif calma and time.time() - calma > 0.7 and any(e["tipo"] in ("voz", "aviso") for e in BUS.desde(desde)[0]):
                break
        return BUS.desde(desde)[0]


class Alfred(ControlPC):
    def __init__(self, gui, cfg):
        self.gui, self.cfg = gui, cfg
        self.voz = Voz(gui, cfg)
        self.buscador = BuscadorApps(cfg, gui.log)
        self.personalizados = cargar_personalizados(ARCHIVO_COMANDOS)
        self.cola = queue.Queue()
        self.activo = True
        self.rec = None
        self.escuchando = False
        self.espera_hasta = 0.0
        self.pend_conf = None
        self.bloqueo_aplauso = 0.0
        self.calib = None
        self.lock_cmd = threading.Lock()
        self.detector = DetectorAplausos(float(cfg.get("aplauso_umbral")))
        self.amp = AmplificadorVoz(float(cfg.get("ganancia_mic") or 8))
        self.rec_en = None                   # reconocedor de inglés (si está activo)
        self._lock_en = threading.Lock()
        self.prueba_hasta = 0.0
        self.evento_modelo = threading.Event()
        self._reabrir = False
        self._lock_ia = threading.Lock()
        self.puerta = PuertaVoz()            # 2.9: el reconocedor solo trabaja cuando hay voz
        self._buf_frase = deque(maxlen=80)   # audio de la frase en curso (para verificar la voz)
        self._spk_modelo = None              # modelo de huella de voz (se carga la primera vez que hace falta)
        self._spk_aviso = False
        self.enrol = None                    # registro de voz en curso
        self.semantica = None                # comprensión semántica (si está activada y lista)
        self._lock_spk = threading.Lock()
        self._lock_mg = threading.Lock()
        self._lock_sem = threading.Lock()
        self._est_audio = [0, 0]             # [bloques oídos, bloques entregados al reconocedor]
        self._ult_repro = ""                 # último reproductor controlado
        self.spotify = SpotifyAPI(cfg)       # 3.2.1: poner canciones en Spotify
        self._etiquetas = (0.0, {})          # 3.2.1: (cuándo, {'artista': {...}, 'album': {...}}) leídas de tus canciones
        self._indice_musica = (0.0, [])      # (cuándo, [(carpeta, nombre)]) caché de carpetas de música
        self._indice_canciones = (0.0, [])   # (cuándo, [(ruta, nombre, limpio, carpetas)]) caché de canciones
        self._lecturas_frase = []            # 3.2: todas las lecturas (español + inglés) de la última frase oída
        self._tl = threading.local()         # 3.2: las lecturas alternas que ve cada comando mientras se ejecuta
        self.remoto = ServidorRemoto(self, cfg)   # 3.2: API para controlar Alfred desde otros dispositivos
        frases = parsear_activacion(cfg.get("palabra_activacion"))
        self.frases_wake = frases if validar_activacion(frases) is None else ["alfred", "alfredo", "al fred"]
        self._init_pc()

    @property
    def nombre(self):
        return self.frases_wake[0].title()

    def cambiar_activacion(self, texto):
        """Devuelve None si se cambió, o el mensaje de error."""
        frases = parsear_activacion(texto)
        error = validar_activacion(frases)
        if error:
            return error
        self.frases_wake = frases
        self.cfg.set("palabra_activacion", ", ".join(frases))
        self.gui.log(f"🗝️ Palabra de activación: «{frases[0]}»" + (f" (también: {', '.join(frases[1:])})" if len(frases) > 1 else ""))
        self.gui.ui(self.gui.actualizar_hint)
        self.voz.decir(f"Ahora me llamo {frases[0]}.")
        return None

    def probar_activacion(self):
        self.prueba_hasta = time.time() + 15
        self.gui.log(f"👂 Prueba de 15 s: di «{self.nombre}» (y otras frases) y verás lo que entiendo.")

    def guardar_personalizados(self):
        guardar_personalizados(ARCHIVO_COMANDOS, self.personalizados)

    # ── arranque ─────────────────────────────────────────────────────────────
    def iniciar(self):
        threading.Thread(target=self.remoto.aplicar_config, daemon=True).start()
        threading.Thread(target=self._run, daemon=True).start()
        threading.Thread(target=self._precalentar_apps, daemon=True).start()
        self._iniciar_pc()
        threading.Thread(target=self._preparar_voz_ia, daemon=True).start()
        threading.Thread(target=self._preparar_ingles, daemon=True).start()
        threading.Thread(target=self.preparar_semantica, daemon=True).start()

    def _preparar_voz_ia(self):
        """Cuando el reconocimiento ya está listo, ofrece (una sola vez) descargar la voz con IA."""
        for _ in range(1200):
            if self.rec is not None or not self.activo:
                break
            time.sleep(0.5)
        if not self.cfg.get("voz_kokoro_ofrecida"):          # una sola vez: pasa de Piper a la voz nueva (con permiso)
            self.cfg.set("voz_kokoro_ofrecida", True)
            if str(self.cfg.get("voz_ia_modelo")).startswith("es_"):
                self.cfg.set("voz_ia_modelo", KOKORO_PREDETERMINADA)
                self.cfg.set("voz_ia_rechazada", False)
                self.voz.reactivar_ia()
        if self.activo and self.cfg.get("voz_ia") and not self.cfg.get("voz_ia_rechazada"):
            self.instalar_voz_ia(False)

    def instalar_voz_ia(self, forzar=False):
        """Descarga Piper + la voz elegida (con permiso y barra de progreso). True si queda lista."""
        if not self._lock_ia.acquire(blocking=False):
            return False
        gui = self.gui
        try:
            mid = self.cfg.get("voz_ia_modelo")
            if mid not in VOCES_IA:
                mid = VOZ_IA_PREDETERMINADA
            motor = self.voz.motor_ia(mid)
            datos = VOCES_IA[mid]
            es_kokoro = datos.get("motor") == "kokoro"
            if motor.instalado(mid):
                self.voz.reactivar_ia()
                return True
            if not forzar and self.cfg.get("voz_ia_rechazada"):
                return False
            if es_kokoro:
                pip_ok = importlib.util.find_spec("kokoro_onnx") is not None
                mb = datos["mb"] + (0 if pip_ok else 40)
                motor_txt, origen = "Kokoro", "github.com y pypi.org"
            else:
                exe_ok = os.path.exists(motor.ruta_exe())
                mb = datos["mb"] + (0 if exe_ok else 22)
                motor_txt, origen = "Piper", "github.com y huggingface.co"
            if not preguntar("Alfred - Permiso para descargar",
                             "Alfred puede hablar con una voz de inteligencia artificial muy natural que funciona "
                             "SIN internet, gratis y sin límites de uso.\n\n"
                             f"Descarga: unos {mb} MB (motor {motor_txt} + voz «{datos['nombre']}») desde {origen}. "
                             "Se guarda en la carpeta de Alfred.\n\n"
                             "Si dices que no, Alfred seguirá con la voz normal de Windows (puedes cambiarlo en "
                             "☰ Menú → Voz).\n\n¿Descargarla ahora?"):
                if not forzar:
                    self.cfg.set("voz_ia_rechazada", True)
                gui.log("ℹ️ Seguiré con la voz de Windows. Activa la voz con IA en ☰ Menú → Voz cuando quieras.")
                return False
            self.cfg.set("voz_ia_rechazada", False)
            self.cfg.set("voz_ia", True)
            titulo = "Descargando la voz con inteligencia artificial"
            pasos = []                                   # (peso, función(cb))
            if es_kokoro:
                if not pip_ok:
                    pasos.append((40, lambda cb: self._pip_kokoro(cb)))
                if not os.path.exists(motor.ruta_modelo()):
                    pasos.append((KOKORO_MODELO_MB, lambda cb: bajar_archivo(URL_KOKORO + KOKORO_MODELO, motor.ruta_modelo(), cb)))
                if not os.path.exists(motor.ruta_voces()):
                    pasos.append((KOKORO_VOCES_MB, lambda cb: bajar_archivo(URL_KOKORO + KOKORO_VOCES, motor.ruta_voces(), cb)))
            else:
                base_voz = f"{URL_VOCES}{datos['ruta']}/{mid}.onnx"
                if not exe_ok:
                    zip_tmp = os.path.join(VOZ_IA_DIR, "piper.zip")
                    pasos.append((22, lambda cb: bajar_archivo(URL_PIPER, zip_tmp, cb)))
                    pasos.append((3, lambda cb: self._extraer_piper(zip_tmp, cb)))
                pasos.append((datos["mb"], lambda cb: bajar_archivo(base_voz, motor.ruta_modelo(mid), cb)))
                pasos.append((1, lambda cb: bajar_archivo(base_voz + ".json", motor.ruta_modelo(mid) + ".json", cb)))
            total_peso, acum = float(sum(p for p, _ in pasos)), 0.0
            gui.progreso(titulo, 0.0, 0.01)
            for peso, fn in pasos:
                def cb(hecho, total, peso=peso, acum=acum):
                    f = (acum + peso * (hecho / total if total else 0.0)) / total_peso
                    gui.progreso(titulo, f, min(1.0, f + 0.015))
                fn(cb)
                acum += peso
                gui.progreso(titulo, acum / total_peso, min(1.0, acum / total_peso + 0.01))
            if not motor.instalado(mid):
                raise RuntimeError("faltan archivos tras la descarga")
            gui.log("✅ Voz con IA instalada.")
            self.voz.reactivar_ia()
            self.voz.decir("Voz con inteligencia artificial lista, señor.")
            return True
        except Exception as e:
            logging.exception("Instalación de la voz IA falló")
            gui.log(f"❌ No pude instalar la voz con IA: {e}. Sigo con la voz de Windows.")
            return False
        finally:
            gui.progreso(None)
            for f in (os.path.join(VOZ_IA_DIR, "piper.zip"),):
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except OSError:
                        pass
            self._lock_ia.release()

    @staticmethod
    def _pip_kokoro(cb):
        cb(0, 1)
        res = instalar_paquetes([("kokoro_onnx", "kokoro-onnx")])
        if not all(res.values()):
            raise RuntimeError("no se pudo instalar kokoro-onnx (mira alfred.log)")
        cb(1, 1)

    @staticmethod
    def _extraer_piper(zip_ruta, cb):
        with zipfile.ZipFile(zip_ruta) as z:
            comprobar_zip(z, VOZ_IA_DIR)                        # sin zip-slip ni zip-bomb (se va a ejecutar piper.exe)
            miembros = z.infolist()
            for i, m in enumerate(miembros, 1):
                z.extract(m, VOZ_IA_DIR)
                cb(i, len(miembros))

    def _precalentar_apps(self):
        """Localiza las apps de siempre al arrancar (queda en caché para que abran al instante)."""
        esperar_escucha(4)
        try:                                  # si hay un reproductor abierto y no elegiste uno, lo recuerda
            self.recordar_reproductor(elegir_reproductor(self.reproductores()))
        except Exception:
            logging.exception("Detectar reproductor")
        for nombre in ("Cursor", self.cfg.get("navegador") or "", self.cfg.get("reproductor") or ""):
            if not nombre:
                continue
            res = self.buscador.resolver(nombre)
            if res:
                self.gui.log(f"✅ {nombre}: {res[1]}")
            else:
                self.gui.log(f"⚠️ No encontré {nombre} en este PC (¿está instalado?).")
        try:                                  # 3.2.1: canciones y etiquetas listas antes de la primera orden de música
            self.indice_canciones()
        except Exception:
            logging.exception("Precalentar el índice de canciones")

    def _run(self):
        try:
            self.rec = None
            while self.activo and self.rec is None:
                modelo = self.preparar_modelo()
                if not modelo:
                    self.gui.log("⏸️ Sin motor de voz: no puedo escucharte. Descárgalo en ☰ Menú → Mantenimiento.")
                    self.evento_modelo.wait()
                    self.evento_modelo.clear()
                    continue
                self.rec = self.cargar_reconocedor(modelo)
                if self.rec is None and localizar_modelo(RUTA_MODELO):   # sigue ahí: no quiso reinstalarlo
                    self.gui.log("⏸️ El motor de voz no carga. Reinstálalo en ☰ Menú → Mantenimiento.")
                    self.evento_modelo.wait()
                    self.evento_modelo.clear()
            if not self.activo:
                return
            self.gui.log(f"🎙️ Reconocimiento offline listo. Di «{self.nombre}» + una orden.")
            logging.info("⏱️ Arranque: reconocimiento listo a los %.0f s", time.time() - T_INICIO)
            if "--oculto" not in sys.argv:
                self.voz.decir("Sistemas listos.")
            if EN_ARRANQUE:                              # arrancó con Windows: espera al micrófono SIN bloquear la ventana
                if not esperar_audio_listo(lambda: self.activo, self.gui.estado, lambda: not self.voz.ocupada()):
                    self.gui.log("⚠️ Windows todavía no entrega ningún micrófono; sigo reintentando.")
            fallos, guia_mostrada = 0, False
            while self.activo:
                try:
                    self._bucle_audio()
                    fallos = 0
                except Exception as e:
                    fallos += 1
                    logging.exception("Fallo de micrófono")
                    self.gui.estado("🔴 Micrófono no disponible")
                    if fallos == 1 or fallos % 12 == 0:         # sin saturar la consola
                        self.gui.log(f"⚠️ Micrófono no disponible: {e}")
                        self.gui.log("   Reintentando cada 5 s. Revisa Configuración → Sistema → Sonido → Entrada.")
                    if fallos >= (8 if EN_ARRANQUE else 2) and not guia_mostrada:
                        guia_mostrada = True
                        if EN_ARRANQUE:                  # al iniciar sesión nada de cuadros emergentes: un aviso en la bandeja
                            self.gui.ui(self.gui.avisar_bandeja, f"{self.nombre}: no encuentro micrófono",
                                        "Windows no entrega ninguno. Sigo reintentando; revisa Configuración → Sonido → Entrada.")
                        else:
                            self.guia_microfono()
                    time.sleep(5)
                    if not self.voz.ocupada():          # reiniciar PortAudio con la voz sonando la cuelga
                        reiniciar_portaudio()
        except Exception as e:
            logging.exception("Error crítico")
            self.gui.log(f"❌ Error crítico: {e}")

    def cargar_reconocedor(self, modelo):
        grande = self._es_grande(modelo)
        try:
            if grande:
                self.cfg.set("modelo_grande_probando", True)     # si Alfred se cierra al cargarlo, la próxima vez no lo usa
                self.gui.log("🎯 Cargando el modelo de alta precisión (puede tardar un poco)…")
            rec = self._nuevo_rec(modelo)
            if grande:
                self.cfg.set("modelo_grande_probando", False)
            return rec
        except Exception:
            logging.exception("El modelo de voz no cargó")
            if grande:
                self.cfg.set("modelo_grande_probando", False)
                self.cfg.set("modelo_alta_precision", False)
                self.gui.log("⚠️ El modelo de alta precisión no cargó (¿poca memoria?). Vuelvo al modelo normal.")
                normal = localizar_modelo(RUTA_MODELO)
                if normal:
                    try:
                        return self._nuevo_rec(normal)
                    except Exception:
                        logging.exception("El modelo normal tampoco cargó")
            self.gui.log("⚠️ El motor de voz parece dañado.")
            if preguntar("Alfred - Motor de voz dañado",
                         "El motor de reconocimiento de voz no se pudo cargar (archivos dañados o incompletos).\n\n"
                         "¿Borrarlo y descargarlo de nuevo (unos 40 MB)?"):
                shutil.rmtree(RUTA_MODELO, ignore_errors=True)
            return None

    def preparar_modelo(self):
        if self.cfg.get("modelo_grande_probando"):              # la vez anterior se cerró al cargar el grande
            self.cfg.set("modelo_grande_probando", False)
            self.cfg.set("modelo_alta_precision", False)
            self.gui.log("⚠️ Alfred se cerró al cargar el modelo de alta precisión (poca memoria): uso el normal.")
        if self.cfg.get("modelo_alta_precision"):
            grande = localizar_modelo(RUTA_MODELO_GRANDE)
            if grande:
                return grande
        ruta = localizar_modelo(RUTA_MODELO)
        if ruta:
            return ruta
        if not preguntar("Alfred - Permiso para descargar",
                         "Alfred necesita descargar su motor de reconocimiento de voz (unos 40 MB) desde alphacephei.com.\n\n"
                         "Se guarda en la carpeta de Alfred y después funciona SIN internet.\n\n¿Descargarlo ahora?"):
            return None
        return self.descargar_modelo()

    def descargar_modelo(self, url=URL_MODELO, destino=RUTA_MODELO, nombre="motor de reconocimiento de voz", mb=40,
                         localizador=None):
        """Descarga y descomprime un modelo de Vosk (español por omisión; el inglés usa otros parámetros)."""
        self.gui.log(f"🌐 Descargando el {nombre} (~{mb} MB), un momento…")
        zip_tmp = os.path.join(BASE_DIR, f"modelo_tmp_{os.path.basename(destino)}.zip")
        try:
            os.makedirs(destino, exist_ok=True)
            titulo = f"Descargando el {nombre}"
            self.gui.progreso(titulo)

            def avance(hecho, total):
                if total:
                    fr = 0.9 * hecho / total
                    self.gui.progreso(titulo, fr, fr + 0.02)
            bajar_archivo(url, zip_tmp, avance)                 # HTTPS + SHA-256; si no coincide, se descarta
            ultimo_t = 0.0
            with zipfile.ZipFile(zip_tmp) as z:
                comprobar_zip(z, destino)                       # sin zip-slip ni zip-bomb
                miembros = z.infolist()
                for i, m in enumerate(miembros, 1):
                    z.extract(m, destino)
                    if i == len(miembros) or time.time() - ultimo_t > 0.12:
                        ultimo_t = time.time()
                        self.gui.progreso(f"Instalando el {nombre}", 0.9 + 0.1 * i / len(miembros))
            self.gui.log(f"✅ {nombre[0].upper() + nombre[1:]} instalado.")
            return (localizador or localizar_modelo)(destino)
        except Exception as e:
            logging.exception("Descarga del modelo falló")
            self.gui.log(f"❌ Falló la descarga: {e}")
            shutil.rmtree(destino, ignore_errors=True)
            return None
        finally:
            self.gui.progreso(None)
            if os.path.exists(zip_tmp):
                os.remove(zip_tmp)

    @staticmethod
    def _nuevo_rec(modelo, nombre_copia="AlfredModelo"):
        """Reconocedor de Vosk que devuelve varias lecturas posibles de cada frase (3 mejores)."""
        SetLogLevel(-1)
        m = Model(ruta_ascii(modelo, nombre_copia))
        rec = KaldiRecognizer(m, 16000)
        try:
            rec._m = m                                   # se guarda el modelo: la huella de voz crea otro reconocedor con él
        except Exception:
            pass
        try:
            rec.SetMaxAlternatives(3)
        except Exception:
            logging.warning("Esta versión de Vosk no da alternativas: uso solo la mejor lectura")
        return rec

    def _preparar_ingles(self, forzar=False):
        """Carga el reconocedor de inglés (y lo descarga, con permiso, si no está). Corre en segundo plano:
        el español ya funciona mientras tanto."""
        if not self._lock_en.acquire(blocking=False):
            return
        try:
            if forzar:
                self.cfg.set("idioma_en", True)
            if not self.cfg.get("idioma_en"):
                return
            for _ in range(1200):                          # espera a que el español esté listo
                if self.rec is not None or not self.activo:
                    break
                time.sleep(0.5)
            if not self.activo or self.rec is None:
                return
            if not forzar:                                 # que no se pisen los avisos de la voz IA y del inglés
                esperar_escucha(5)
                while self.activo and self._lock_ia.locked():
                    time.sleep(1)
            ruta = localizar_modelo(RUTA_MODELO_EN)
            rec = None
            if ruta:
                try:
                    rec = self._nuevo_rec(ruta, "AlfredModeloEN")
                except Exception:
                    logging.exception("El modelo de inglés no cargó")
                    self.gui.log("⚠️ El motor de voz en inglés parece dañado.")
                    if not preguntar("Alfred - Motor de voz en inglés dañado",
                                     "El motor de reconocimiento en inglés no se pudo cargar.\n\n"
                                     "¿Borrarlo y descargarlo de nuevo (unos 40 MB)?"):
                        return
                    shutil.rmtree(RUTA_MODELO_EN, ignore_errors=True)
                    ruta = None
            if rec is None and not ruta:
                if not forzar and self.cfg.get("en_ofrecido"):
                    return
                self.cfg.set("en_ofrecido", True)
                if not preguntar("Alfred - Permiso para descargar",
                                 "Alfred puede entender también INGLÉS (órdenes, títulos de canciones, nombres de apps) "
                                 "y contestarte en inglés cuando le hablas en inglés.\n\n"
                                 "Necesita descargar un motor de reconocimiento de voz en inglés (unos 40 MB) desde "
                                 "alphacephei.com. Se guarda en la carpeta de Alfred y funciona SIN internet.\n\n"
                                 "Si dices que no, Alfred seguirá solo en español (puedes activarlo en ☰ Menú → Voz).\n\n"
                                 "¿Descargarlo ahora?"):
                    self.gui.log("ℹ️ Seguiré solo en español. Activa el inglés en ☰ Menú → Voz cuando quieras.")
                    return
                ruta = self.descargar_modelo(URL_MODELO_EN, RUTA_MODELO_EN, "motor de voz en inglés", 40)
                if not ruta:
                    return
                rec = self._nuevo_rec(ruta, "AlfredModeloEN")
            if rec is not None and self.cfg.get("idioma_en"):
                self.rec_en = rec
                threading.Thread(target=self.voz._precalentar_kokoro, daemon=True).start()   # guarda también las frases en inglés
                self.gui.log("🇬🇧 Inglés listo: ahora te entiendo en inglés y en español a la vez.")
        except Exception as e:
            logging.exception("No pude preparar el inglés")
            self.gui.log(f"⚠️ No pude activar el inglés: {e}")
        finally:
            self._lock_en.release()

    def instalar_kokoro_ligero(self):
        """Descarga el modelo ligero de Kokoro (88 MB): genera la voz más rápido, con algo menos de fidelidad."""
        if not self._lock_ia.acquire(blocking=False):
            return False
        gui = self.gui
        try:
            destino = os.path.join(VOZ_IA_DIR, "kokoro", KOKORO_LIGERO)
            if not os.path.exists(destino):
                if not preguntar("Alfred - Permiso para descargar",
                                 f"El modelo ligero de la voz Kokoro pesa unos {KOKORO_LIGERO_MB} MB (desde github.com) "
                                 "y genera la voz bastante más rápido, con una calidad algo menor.\n\n"
                                 "Se guarda en la carpeta de Alfred. Puedes volver al modelo normal cuando quieras en "
                                 "☰ Menú → Voz.\n\n¿Descargarlo ahora?"):
                    return False
                titulo = "Descargando el modelo ligero de la voz"
                gui.progreso(titulo, 0.0, 0.02)
                bajar_archivo(URL_KOKORO + KOKORO_LIGERO, destino,
                              lambda h, t: gui.progreso(titulo, (h / t) if t else 0.0, ((h / t) if t else 0.0) + 0.02))
            self.cfg.set("kokoro_ligero", True)
            self.voz.reactivar_ia()
            gui.log("⚡ Kokoro ligero activado.")
            return True
        except Exception as e:
            logging.exception("Modelo ligero de Kokoro")
            gui.log(f"❌ No pude instalar el modelo ligero: {e}")
            return False
        finally:
            gui.progreso(None)
            self._lock_ia.release()

    def reconocer(self, data):
        """Pasa el audio por el reconocedor de español y, si está activo, por el de inglés. Devuelve todas las lecturas
        cuando alguno termina una frase (None mientras siguen escuchando)."""
        en = self.rec_en
        fin_es = self.rec.AcceptWaveform(data)
        fin_en = False
        if en is not None:
            try:
                fin_en = en.AcceptWaveform(data)
            except Exception:
                logging.exception("El reconocedor de inglés falló; sigo solo en español")
                self.rec_en = en = None
        if not (fin_es or fin_en):
            return None
        lecturas = extraer_candidatos(self.rec.Result() if fin_es else self.rec.FinalResult(), "es")
        if en is not None:
            lecturas += extraer_candidatos(en.Result() if fin_en else en.FinalResult(), "en")
        return lecturas

    def cerrar_frase(self):
        """Fuerza el cierre de la frase en curso (ruido continuo: Vosk nunca la da por terminada)."""
        lect = extraer_candidatos(self.rec.FinalResult(), "es")
        en = self.rec_en
        if en is not None:
            try:
                lect += extraer_candidatos(en.FinalResult(), "en")
            except Exception:
                logging.exception("No pude cerrar la frase en inglés")
        return lect

    def _reiniciar_rec(self):
        self.rec.Reset()
        en = self.rec_en
        if en is not None:
            en.Reset()

    # ── 2.9: atender lo oído, voz registrada, modelo grande y comprensión semántica ────────────────
    def _necesita_buffer(self):
        return self.enrol is not None or bool(self.cfg.get("solo_mi_voz") and self.cfg.get("huella_voz"))

    def _atender(self, lecturas):
        """Una frase terminó: elige la mejor lectura, comprueba la voz (si está activado) y la interpreta."""
        try:
            if self.dictado:                                  # dictando: solo vale el idioma del dictado
                pref = self.cfg.get("idioma_dictado") or "es"
                lecturas = [l for l in lecturas if l[1] == pref] or lecturas
            elegida = elegir_candidato(lecturas, self.frases_wake, self._es_orden, self.voz.idioma_actual())
            if self.enrol is not None:
                self._muestra_registro()
                return
            if elegida and self._voz_autorizada(elegida[0]):
                self._lecturas_frase = list(lecturas)         # 3.2: los comandos de música/abrir prueban todas
                self.procesar(*elegida)
        except Exception as e:                    # un error en UNA orden no debe tumbar el micrófono
            logging.exception("Error interpretando la orden")
            self.gui.log(f"⚠️ Error interpretando lo que oí: {e}")
        finally:
            self._buf_frase.clear()

    def _cargar_spk(self):
        if self._spk_modelo is None:
            if SpkModel is None:
                raise RuntimeError("esta versión de Vosk no incluye SpkModel (actualiza con: pip install -U vosk)")
            ruta = localizar_spk(RUTA_MODELO_SPK)
            if not ruta:
                raise FileNotFoundError("falta el modelo de huella de voz")
            self._spk_modelo = SpkModel(ruta_ascii(ruta, "AlfredSpk", "mfcc.conf"))
        return self._spk_modelo

    def huella_de_audio(self, bloques):
        """(huella, tramas de voz) del audio dado, o (None, 0) si no se pudo. Usa un reconocedor aparte que SOLO se
        crea cuando hace falta (una orden dirigida a Alfred), así no gasta CPU en reposo."""
        try:
            modelo = getattr(self.rec, "_m", None)
            if modelo is None or not bloques:
                return None, 0
            rec = KaldiRecognizer(modelo, 16000)
            rec.SetSpkModel(self._cargar_spk())
            rec.AcceptWaveform(b"".join(bloques))
            d = json.loads(rec.FinalResult())
            alts = d.get("alternatives")
            if "spk" not in d and isinstance(alts, list) and alts and isinstance(alts[0], dict):
                d = alts[0]
            v = d.get("spk")
            return (list(v), int(d.get("spk_frames", 0))) if v else (None, 0)
        except Exception:
            logging.exception("No pude sacar la huella de voz")
            return None, 0

    def _voz_autorizada(self, texto):
        """True si la orden puede ejecutarse: el control de voz está apagado, la frase no iba dirigida a Alfred, o
        la voz se parece a la registrada. Si algo técnico falla, deja pasar (no te deja sin Alfred)."""
        if not (self.cfg.get("solo_mi_voz") and self.cfg.get("huella_voz")):
            return True
        ahora = time.time()
        if ahora < self.prueba_hasta:
            return True
        con_wake, _ = quitar_wake(normalizar(texto), self.frases_wake)
        if not (con_wake or ahora < self.espera_hasta or self.pend_conf):
            return True                           # no iba para Alfred: procesar() la ignora de todas formas
        huella, tramas = self.huella_de_audio(list(self._buf_frase))
        if huella is None or tramas < 40:
            if not self._spk_aviso:
                self._spk_aviso = True
                self.gui.log("ℹ️ No pude comprobar la voz (audio muy corto o modelo no disponible): dejo pasar la orden.")
            return True
        d = distancia_coseno(huella, self.cfg.get("huella_voz"))
        umbral = float(self.cfg.get("huella_umbral") or 0.45)
        if d <= umbral:
            self.gui.log(f"🔓 Voz reconocida (distancia {d:.2f}, máximo {umbral:.2f})")
            if d < 0.6 * umbral:                  # muy parecida: la huella aprende despacio tu voz de hoy
                nuevo = centro_huellas([self.cfg.get("huella_voz")] * 19 + [huella])
                self.cfg.datos["huella_voz"] = [round(x, 5) for x in nuevo]
                self.cfg.guardar()
            return True
        self.gui.log(f"🔒 Voz no reconocida (distancia {d:.2f}, máximo {umbral:.2f}): ignoro la orden.")
        return False

    def _asegurar_spk(self):
        if SpkModel is None:
            self.gui.log("⚠️ Tu versión de Vosk no trae el modelo de huella de voz. Actualiza: pip install -U vosk")
            return False
        if not localizar_spk(RUTA_MODELO_SPK):
            if not preguntar("Alfred - Permiso para descargar",
                             "Para reconocer tu voz Alfred necesita un modelo pequeño (unos 13 MB) de alphacephei.com.\n\n"
                             "Se guarda en la carpeta de Alfred y después funciona SIN internet.\n\n¿Descargarlo ahora?"):
                return False
            if not self.descargar_modelo(URL_MODELO_SPK, RUTA_MODELO_SPK, "modelo de huella de voz", 13, localizar_spk):
                return False
        try:
            self._cargar_spk()
            return True
        except Exception as e:
            logging.exception("Modelo de huella de voz")
            self.gui.log(f"❌ No pude cargar el modelo de huella de voz: {e}")
            return False

    def _muestra_registro(self):
        e = self.enrol
        if e is None or not e.get("esperando"):
            return
        e["ultimo"] = self.huella_de_audio(list(self._buf_frase))
        e["esperando"] = False
        if e.get("evento"):
            e["evento"].set()

    def registrar_voz(self):
        """Registra tu voz con 5 frases. True si queda registrada y activada."""
        if not self._lock_spk.acquire(blocking=False):
            return False
        try:
            if not self.escuchando:
                self.gui.log("⏳ Espera a que Alfred termine de iniciar el micrófono.")
                return False
            if not self._asegurar_spk():
                return False
            frases = ["Alfred, ¿qué hora es?", "Alfred, abre el explorador de archivos", "Alfred, pon música",
                      "Alfred, sube un poco el volumen", "Alfred, ¿qué día es hoy?"]
            self.enrol = {"esperando": False, "evento": None, "ultimo": None}
            self.voz.decir("Voy a registrar tu voz. Repite cada frase con tu voz normal, sin gritar.", esperar=True)
            huellas = []
            for i, frase in enumerate(frases, 1):
                for _ in range(3):
                    if not self.activo:
                        return False
                    ev = threading.Event()
                    self.enrol.update(esperando=True, evento=ev, ultimo=None)
                    self.gui.log(f"🎙️ Frase {i}/{len(frases)}: di «{frase}»")
                    self.voz.decir(f"Frase {i}. {frase}", esperar=True)
                    if not ev.wait(timeout=25):
                        self.gui.log("⏳ No te oí; lo intento otra vez.")
                        continue
                    huella, tramas = self.enrol["ultimo"] or (None, 0)
                    if huella is None or tramas < 80:
                        self.gui.log(f"🔁 Muy corta o poco clara ({tramas} tramas): repítela un poco más larga.")
                        continue
                    huellas.append(huella)
                    break
                else:
                    self.gui.log("❌ No pude registrar tu voz (no te oí bien). Acércate al micrófono e inténtalo de nuevo.")
                    self.voz.decir("No pude registrar tu voz.")
                    return False
            centro = centro_huellas(huellas)
            umbral, ds = umbral_huella(huellas, centro)
            self.cfg.datos["huella_voz"] = [round(x, 5) for x in centro]
            self.cfg.datos["huella_umbral"] = round(umbral, 2)
            self.cfg.datos["huella_muestras"] = len(huellas)
            self.cfg.datos["solo_mi_voz"] = True
            self.cfg.guardar()
            self.gui.log(f"✅ Voz registrada ({len(huellas)} frases). Distancias entre tus muestras: "
                         + ", ".join(f"{d:.2f}" for d in ds) + f". Exigencia: {umbral:.2f} (ajústala en ☰ Menú → Escucha).")
            self.voz.decir("Listo. Desde ahora solo obedeceré tu voz.")
            return True
        except Exception as e:
            logging.exception("Registro de voz")
            self.gui.log(f"❌ No pude registrar tu voz: {e}")
            return False
        finally:
            self.enrol = None
            self._buf_frase.clear()
            self._lock_spk.release()

    def olvidar_voz(self):
        self.cfg.datos["huella_voz"] = None
        self.cfg.datos["huella_muestras"] = 0
        self.cfg.datos["solo_mi_voz"] = False
        self.cfg.guardar()
        self.gui.log("🗑️ Voz borrada: Alfred vuelve a obedecer a cualquiera.")

    # ── modelo de alta precisión ──
    def _es_grande(self, modelo):
        try:
            return os.path.abspath(modelo).startswith(os.path.abspath(RUTA_MODELO_GRANDE))
        except Exception:
            return False

    def cambiar_modelo_es(self, ruta):
        """Carga el modelo en español de esa carpeta y lo pone en marcha sin reiniciar. True si quedó el pedido."""
        nuevo = self.cargar_reconocedor(ruta)
        if nuevo is None:
            return False
        self.rec = nuevo
        try:
            self._reiniciar_rec()
        except Exception:
            logging.exception("Reiniciar el reconocedor")
        return (not self._es_grande(ruta)) or bool(self.cfg.get("modelo_alta_precision"))

    def activar_modelo_grande(self):
        """Descarga (con permiso) y activa el Vosk grande en español. True si queda activado."""
        if not self._lock_mg.acquire(blocking=False):
            return False
        try:
            ruta = localizar_modelo(RUTA_MODELO_GRANDE)
            if not ruta:
                gb = memoria_total_gb()
                ram = f"Este equipo tiene {gb:.0f} GB de RAM. " if gb else ""
                if gb and gb < 8:
                    ram += "Con menos de 8 GB puede ir lento o fallar (Alfred volvería solo al modelo normal). "
                if not preguntar("Alfred - Permiso para descargar",
                                 "El modelo de alta precisión entiende bastante mejor el español, pero pesa unos 1.4 GB "
                                 "(más otros 1.4 GB temporales al descargar), usa mucha más memoria y tarda más en cargar.\n\n"
                                 + ram + "Se descarga de alphacephei.com, se guarda en la carpeta de Alfred y funciona SIN "
                                 "internet. Puedes volver al modelo normal cuando quieras.\n\n¿Descargarlo ahora?"):
                    return False
                ruta = self.descargar_modelo(URL_MODELO_GRANDE, RUTA_MODELO_GRANDE, "modelo de alta precisión", 1400)
                if not ruta:
                    return False
            self.cfg.set("modelo_alta_precision", True)
            if not self.cambiar_modelo_es(ruta):
                self.cfg.set("modelo_alta_precision", False)
                return False
            self.gui.log("🎯 Modelo de alta precisión activado.")
            self.voz.decir("Modelo de alta precisión activado.")
            return True
        except Exception as e:
            logging.exception("Modelo de alta precisión")
            self.gui.log(f"❌ No pude activar el modelo de alta precisión: {e}")
            self.cfg.set("modelo_alta_precision", False)
            return False
        finally:
            self._lock_mg.release()

    def desactivar_modelo_grande(self):
        self.cfg.set("modelo_alta_precision", False)
        normal = localizar_modelo(RUTA_MODELO)
        if normal and self.cambiar_modelo_es(normal):
            self.gui.log("🎯 Vuelvo al modelo normal (el grande sigue en la carpeta «model_grande»; bórrala si quieres el espacio).")

    # ── comprensión semántica ──
    def preparar_semantica(self, forzar=False):
        """Carga la comprensión semántica. Al arrancar solo si ya estaba activada; con forzar=True (interruptor del menú)
        pide permiso para instalar fastembed y descargar el modelo. True si queda lista."""
        if not self._lock_sem.acquire(blocking=False):
            return False
        try:
            if not forzar:
                if not self.cfg.get("comprension_semantica"):
                    return False
                for _ in range(1200):                      # espera a que el reconocimiento ya esté listo
                    if self.rec is not None or not self.activo:
                        break
                    time.sleep(0.5)
                esperar_escucha(10)                        # y a que terminen de cargar las demás cosas
            if not self.activo:
                return False
            falta_lib = importlib.util.find_spec("fastembed") is None
            if forzar:
                primera = not os.path.isdir(RUTA_SEMANTICA)
                if (falta_lib or primera) and not preguntar(
                        "Alfred - Permiso para instalar",
                        "La comprensión semántica deja que Alfred te entienda aunque uses otras palabras "
                        "(«no se escucha nada» → sube el volumen).\n\n"
                        + ("Se instalará el componente «fastembed» (pypi.org) y " if falta_lib else "Se descargará ")
                        + "un modelo de unos 220 MB (huggingface.co). Después funciona SIN internet.\n\n¿Continuar?"):
                    return False
            if falta_lib:
                if not forzar:
                    self.gui.log("⚠️ Falta «fastembed»: desactivo la comprensión semántica (actívala en ☰ Menú → Escucha).")
                    self.cfg.set("comprension_semantica", False)
                    return False
                self.gui.progreso("Instalando la comprensión semántica")
                res = instalar_paquetes([("fastembed", "fastembed")], self.gui.log)
                if not all(res.values()):
                    self.gui.log("❌ No pude instalar fastembed (mira alfred.log).")
                    return False
            self.gui.progreso("Preparando la comprensión semántica (la primera vez descarga el modelo)")
            s = ComprensionSemantica(RUTA_SEMANTICA)
            n = s.cargar()
            self.semantica = s
            self.cfg.set("comprension_semantica", True)
            self.gui.log(f"🧠 Comprensión semántica lista ({n} frases de ejemplo).")
            return True
        except Exception as e:
            logging.exception("Comprensión semántica")
            self.gui.log(f"❌ No pude activar la comprensión semántica: {e}")
            self.semantica = None
            self.cfg.set("comprension_semantica", False)
            return False
        finally:
            self.gui.progreso(None)
            self._lock_sem.release()

    def _entender_semantica(self, orden):
        """(comando, orden) si el significado coincide con claridad con un comando; si no, None."""
        s = self.semantica
        if s is None or not s.listo:
            return None
        try:
            r = s.buscar(orden, float(self.cfg.get("semantica_umbral") or 0.74))
        except Exception:
            logging.exception("Comprensión semántica")
            return None
        if not r:
            return None
        cmd_id, canon, score = r
        cmd = next((c for c in COMANDOS if c["id"] == cmd_id), None)
        if cmd is None:
            return None
        final = canon or orden
        self.gui.log(f"🧠 Entendí «{orden}» como «{final}» (parecido {score:.0%})")
        return cmd, final

    def _es_orden(self, orden, idioma):
        """¿Esta lectura es una orden que Alfred entiende? (para elegir entre español e inglés)"""
        if self.pend_conf and hay(orden, *PALABRAS_SI):
            return True
        if buscar_personalizado(self.personalizados, orden):
            return True
        if idioma == "en":
            es = traducir_orden_en(orden)
            return bool(es and buscar_comando(es))
        return bool(buscar_comando(orden))

    def pedir_modelo(self):
        """Botón del menú: descarga (con permiso) o reinstala el motor de voz."""
        if localizar_modelo(RUTA_MODELO) and self.rec is not None:
            self.gui.log("✅ El motor de voz ya está instalado y funcionando.")
            return
        self.evento_modelo.set()

    def reabrir_micro(self):
        self._reabrir = True

    def volver_a_buscar_apps(self):
        self.cfg.get("apps_encontradas").clear()
        self.cfg.guardar()
        self.buscador._startapps = None
        self.gui.log("🧭 Buscando de nuevo tus aplicaciones…")
        self._precalentar_apps()

    def guia_microfono(self):
        """Explica cómo arreglar el micrófono en Windows y ofrece abrir la configuración."""
        if preguntar("Alfred - No encuentro micrófono",
                     "Windows no le está entregando ningún micrófono a Alfred.\n\n"
                     "Revisa lo siguiente:\n"
                     "  1. Configuración → Sistema → Sonido → Entrada: debe haber un micrófono y estar activado.\n"
                     "  2. Configuración → Privacidad y seguridad → Micrófono: activa «Acceso al micrófono» y "
                     "«Permitir que las aplicaciones de escritorio accedan al micrófono».\n"
                     "  3. Si usas una laptop, comprueba que la tecla de silenciar micrófono (F8) no esté activa.\n"
                     "  4. Si es un micrófono USB o Bluetooth, conéctalo.\n\n"
                     "Alfred seguirá reintentando solo, no hace falta reiniciarlo.\n\n"
                     "¿Abrir ahora la configuración de privacidad del micrófono?"):
            try:
                os.startfile("ms-settings:privacy-microphone")
            except Exception:
                logging.exception("No pude abrir la configuración")

    def _abrir_stream(self, cb):
        """Prueba micrófono por micrófono hasta que uno abra. Devuelve (stream, nombre) o lanza error."""
        errores = []
        for dev, nombre, extra in candidatos_microfono(self.cfg.get("microfono")):
            try:
                st = sd.RawInputStream(samplerate=16000, blocksize=1600, dtype="int16", channels=1,
                                       device=dev, callback=cb, extra_settings=extra)
                st.start()
                return st, nombre
            except Exception as e:
                errores.append(f"{nombre}: {e}")
                logging.warning("Micrófono descartado -> %s: %s", nombre, e)
        if not errores:
            raise RuntimeError("no hay ningún dispositivo de entrada de audio")
        raise RuntimeError("ningún micrófono pudo abrirse (detalles en alfred.log). Último error: " + errores[-1])

    def _bucle_audio(self):
        def cb(indata, frames, t, status):
            self.cola.put(bytes(indata))
        stream, nombre_mic = self._abrir_stream(cb)
        self.gui.log(f"🎙️ Micrófono en uso: {nombre_mic}")
        self.gui.estado("🟢 Escuchando…")
        if not EVT_ESCUCHANDO.is_set():
            EVT_ESCUCHANDO.set()                         # a partir de aquí se cargan las cosas pesadas secundarias
            dt = time.time() - T_INICIO
            logging.info("⏱️ Arranque: escuchando a los %.0f s", dt)
            if EN_ARRANQUE:
                self.gui.log(f"⏱️ Alfred escucha {dt:.0f} s después de que Windows lo abriera.")
                self.gui.ui(self.gui.avisar_bandeja, f"{self.nombre} está activo",
                            f"Escuchando. Di «{self.nombre}» y tu orden. Estoy en la bandeja del sistema.")
        self.vaciar_cola()
        silencio_bloques, aviso_silencio, sin_datos = 0, False, 0
        try:
            self.escuchando = True
            try:
                estaba_ocupada = False
                t_frase = time.time()
                while self.activo:
                    if self._reabrir:             # cambiaste de micrófono en el menú
                        self._reabrir = False
                        return
                    try:
                        data = self.cola.get(timeout=0.5)
                        sin_datos = 0
                    except queue.Empty:
                        sin_datos += 1
                        if sin_datos >= 16 or not stream.active:   # micrófono desconectado o congelado
                            raise RuntimeError("el micrófono dejó de enviar audio")
                        continue
                    if np.any(np.frombuffer(data, dtype=np.int16)):
                        silencio_bloques = 0
                    else:
                        silencio_bloques += 1
                        if silencio_bloques == 80 and not aviso_silencio:   # ~8 s de silencio digital exacto
                            aviso_silencio = True
                            self.gui.log("⚠️ El micrófono solo envía silencio total. Revisa que no esté silenciado "
                                         "y que Windows permita el acceso (Privacidad → Micrófono).")
                    if self.voz.ocupada():              # no escucharse a sí mismo
                        estaba_ocupada = True
                        continue
                    if estaba_ocupada:
                        estaba_ocupada = False
                        self._reiniciar_rec()
                        self.vaciar_cola()
                        self.detector.reiniciar()
                        self.amp.reiniciar()
                        self.puerta.reiniciar()
                        self._buf_frase.clear()
                        continue
                    ahora = time.time()
                    niveles = niveles_frames(data) if (self.calib is not None or self.cfg.get("clap_activo")) else ()
                    if self.calib is not None:
                        if niveles:
                            self.calib.append((ahora, max(niveles)))
                    elif self.cfg.get("clap_activo") and ahora > self.bloqueo_aplauso:
                        for nv in niveles:
                            r = self.detector.procesar(nv)
                            if r:
                                self.gui.log(f"👏 Aplauso {r}/2 (nivel {nv:.2f})")
                            if r == 2:
                                self.bloqueo_aplauso = ahora + 12
                                self.detector.reiniciar()
                                self.lanzar(self.secuencia_bienvenida)
                                break
                    if self.cola.qsize() > 40:          # más de 4 s de retraso: el audio viejo ya no sirve
                        logging.warning("Audio atrasado (%d bloques): descarto lo acumulado", self.cola.qsize())
                        self.vaciar_cola()
                        self._reiniciar_rec()
                        self.puerta.reiniciar()
                        self._buf_frase.clear()
                        continue
                    bloque = self.amp.procesar(data)                         # siempre: así sigue midiendo el ruido
                    ahora = time.time()
                    if self.cfg.get("puerta_voz") is not False:
                        feed, cerrar = self.puerta.procesar(self.amp.hay_voz, bloque)
                    else:
                        feed, cerrar = [bloque], (ahora - t_frase > 20)      # sin puerta: cierre forzado cada 20 s
                    self._est_audio[0] += 1
                    self._est_audio[1] += len(feed)
                    if self._est_audio[0] >= 6000:                           # ~10 min: cuánto CPU ahorra la puerta
                        logging.info("Puerta de voz: el reconocedor trabajó con el %.0f %% del audio",
                                     100.0 * self._est_audio[1] / self._est_audio[0])
                        self._est_audio = [0, 0]
                    guardar = self._necesita_buffer()
                    for blk in feed:
                        if guardar:
                            self._buf_frase.append(blk)
                        lect = self.reconocer(blk)                           # español + inglés, con alternativas
                        if lect:
                            t_frase = ahora
                            self._atender(lect)
                    if cerrar:                                               # terminaste de hablar (o ruido continuo)
                        t_frase = ahora
                        lect = self.cerrar_frase()
                        if lect:
                            self._atender(lect)
                        else:
                            self._buf_frase.clear()
            finally:
                self.escuchando = False
        finally:
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass

    def vaciar_cola(self):
        try:
            while True:
                self.cola.get_nowait()
        except queue.Empty:
            pass

    def calibrar_aplausos(self):
        if not self.escuchando:
            self.gui.log("⏳ Espera a que Alfred termine de iniciar el micrófono.")
            return
        self.voz.decir("Calibración. Aplauda dos veces, con su fuerza normal.", esperar=True)
        time.sleep(1.0)
        self.calib = []
        self.gui.log("🎚️ Escuchando 5 segundos… ¡aplaude dos veces!")
        time.sleep(5)
        datos, self.calib = self.calib, None
        res = calcular_umbral(datos or [])
        if not res:
            self.gui.log("⚠️ No oí aplausos claros. Acércate al micrófono, aplaude más fuerte e inténtalo otra vez.")
            self.voz.decir("No escuché aplausos claros.")
            return
        umbral, ruido, picos = res
        self.cfg.set("aplauso_umbral", round(umbral, 3))
        self.detector.umbral = umbral
        self.detector.reiniciar()
        self.gui.log(f"✅ Calibrado: umbral {umbral:.3f} (ruido {ruido:.3f}, aplausos {', '.join(f'{p:.2f}' for p in picos)}).")
        self.voz.decir("Calibración lista. Active el doble aplauso en el interruptor.")

    # ── interpretación de órdenes ────────────────────────────────────────────
    def ordenes_de_lecturas(self, lecturas):
        """Todas las lecturas de una frase (español e inglés, con sus alternativas) como órdenes en español sin la
        palabra de activación, sin repetir. Los comandos con un nombre propio (canción, carpeta, app) las prueban todas
        y se quedan con la que mejor coincide: el reconocedor de español rara vez acierta con «Mystery Skulls»."""
        cands = []
        for texto, idioma, _ in lecturas:
            norm = normalizar(texto)
            if not norm:
                continue
            wake, orden = quitar_wake(norm, self.frases_wake)
            cands.append((wake, orden.strip() if wake else norm, idioma))
        if any(w for w, _, _ in cands):
            cands = [c for c in cands if c[0]]
        res = []
        for _, orden, idioma in cands:
            if not orden:
                continue
            if idioma == "en":
                try:
                    tr = traducir_orden_en(orden)
                except Exception:
                    tr = None
                if tr:
                    orden = tr
            if orden not in res:
                res.append(orden)
        return res[:8]

    def alternas_actuales(self):
        return getattr(self._tl, "alternas", None) or []

    def pedidos_alternos(self, extraer, primero=None):
        """Lo pedido según cada lectura del audio (la elegida primero), sin repetir ni basura (letras sueltas)."""
        res = [primero] if primero else []
        for orden in self.alternas_actuales():
            try:
                p = extraer(orden)
            except Exception:
                p = None
            if isinstance(p, (list, tuple)):
                cand = list(p)
            else:
                cand = [p] if p else []
            for c in cand:
                if c and c not in res and pedido_valido(c):
                    res.append(c)
        return res[:6]

    def procesar_remoto(self, texto):
        """Una orden escrita desde otro dispositivo (API remota): igual que si la hubieras dicho, sin palabra de activación."""
        idioma = "en" if (self.cfg.get("idioma_en") and parece_ingles(texto)) else "es"
        self.procesar(texto, idioma, directo=True)

    def procesar(self, texto, idioma="es", directo=False):
        """directo=True: la orden llega escrita desde otro dispositivo (control remoto): no necesita palabra de
        activación y no pasa por el modo de prueba."""
        raw = texto.lower().strip()
        norm = normalizar(raw)
        lecturas, self._lecturas_frase = (self._lecturas_frase, []) if not directo else ([], [])
        if not norm:
            return
        ahora = time.time()
        con_wake, orden = quitar_wake(norm, self.frases_wake)
        if directo:
            con_wake, orden = True, (orden if con_wake else norm)
        if ahora < self.prueba_hasta and not directo:    # modo prueba de la palabra de activación
            self.gui.log(f"👂 Oí ({'inglés' if idioma == 'en' else 'español'}): «{raw}» → "
                         + ("✅ palabra de activación detectada" if con_wake else "❌ no detecté la palabra de activación"))
            return
        if directo and self.pend_conf and hay(norm, *PALABRAS_SI):
            self.gui.log("🔒 Una orden remota no puede confirmar una acción delicada: confírmala con tu voz en el PC.")
            return
        if self.pend_conf and not directo:               # esperando un «sí» (dicho en voz alta) para algo delicado
            cmd, hasta = self.pend_conf
            self.pend_conf = None
            if ahora <= hasta:
                self.voz.fijar_idioma(idioma)
                if hay(norm, *PALABRAS_SI):
                    if isinstance(cmd, dict) and cmd.get("_accion"):         # 3.0: apagar, reiniciar, vaciar papelera…
                        self.lanzar(cmd["_accion"])
                    else:
                        self.lanzar(self.ejecutar_personalizado, cmd, True)
                else:
                    self.voz.decir("Cancelado.")
                return
        if (self.dictado or self.grid is not None) and not con_wake and ahora >= self.espera_hasta:
            if self._atender_modo(raw, norm, idioma):                        # 3.0: dictado y cuadrícula del ratón
                return
        if not (con_wake or ahora < self.espera_hasta):
            return
        self.voz.fijar_idioma(idioma)                    # te contesta en el idioma en que le hablaste
        orden = orden.strip()
        if con_wake and not orden:                       # solo dijo la palabra de activación
            self.espera_hasta = ahora + float(self.cfg.get("ventana_espera"))
            self.voz.decir("Diga")
            return
        self.espera_hasta = 0.0
        try:
            self._alternas_cmd = self.ordenes_de_lecturas(lecturas) if lecturas else []
        except Exception:
            logging.exception("Lecturas alternas")
            self._alternas_cmd = []
        propio = buscar_personalizado(self.personalizados, orden)   # los del usuario tienen prioridad
        orden_cmd, raw_cmd = orden, raw
        if not propio and idioma == "en":                # órdenes en inglés -> su forma en español
            traducida = traducir_orden_en(orden)
            if traducida and buscar_comando(traducida):
                orden_cmd, raw_cmd = traducida, traducida
        _c = None if propio else buscar_comando(orden_cmd)
        _priv = (f"{'📱' if directo else '🎤'} [orden de escribir texto: {len(raw.split())} palabras]"
                 if _c and _c["id"] == "escribir" else None)           # lo que se teclea no va a los registros
        self.gui.log(("📱 " if directo else "🎤 ") + f"{raw}" + (f"   → {orden_cmd}" if orden_cmd != orden else ""),
                     privado=_priv)
        if propio:
            self.lanzar(self.ejecutar_personalizado, propio, False)
            return
        cmd = buscar_comando(orden_cmd)
        if not cmd:
            difuso = buscar_comando_difuso(orden_cmd)        # una letra o un final mal oído: «pausas», «recordatorio»
            if difuso:
                cmd, orden_cmd = difuso
                raw_cmd = orden_cmd
                self.gui.log(f"🎯 Entendí la orden como «{orden_cmd}»")
        if not cmd:
            sem = self._entender_semantica(orden_cmd)         # otras palabras, mismo significado (si está activada)
            if sem:
                cmd, orden_cmd = sem
                raw_cmd = orden_cmd
        if not cmd:
            self.gui.log(f"❓ No tengo ese comando (di «{self.nombre} ayuda»).")
            self.voz.decir("No tengo ese comando, señor.")
            return
        self.lanzar(getattr(self, "cmd_" + cmd["id"]), raw_cmd, orden_cmd)

    def lanzar(self, fn, *args):
        alternas = list(getattr(self, "_alternas_cmd", []) or [])
        self._alternas_cmd = []

        def correr():
            self._tl.alternas = alternas
            with self.lock_cmd:
                try:
                    fn(*args)
                except Exception as e:
                    logging.exception("Error en %s", getattr(fn, "__name__", fn))
                    self.gui.log(f"⚠️ Error: {e}")
                    self.voz.decir("Hubo un error al ejecutar esa orden.")
        threading.Thread(target=correr, daemon=True).start()

    # ── comandos del usuario ─────────────────────────────────────────────────
    def ejecutar_personalizado(self, cmd, confirmado=False):
        acciones = cmd["acciones"]
        if not confirmado and any(a.get("tipo") == "eliminar" for a in acciones):
            self._confirmar("Este comando elimina archivos. Diga sí para confirmar.",
                            lambda: self.ejecutar_personalizado(cmd, True))
            return
        if cmd.get("respuesta"):
            self.voz.decir(cmd["respuesta"])
        for a in acciones:
            self.ejecutar_accion(a)

    def a_papelera(self, ruta):
        try:
            from send2trash import send2trash
        except ImportError:
            raise RuntimeError("Falta send2trash (pip install send2trash)")
        send2trash(os.path.abspath(ruta))

    def ejecutar_accion(self, a):
        t, v, d = a.get("tipo"), (a.get("valor") or "").strip(), (a.get("destino") or "").strip()
        try:
            if t == "app":
                self.abrir_app(v)
            elif t == "web":
                self.abrir_web(v, d)
            elif t == "archivo":
                os.startfile(expandir(v))
            elif t == "mover":
                self.gui.log(f"📦 Moví {mover_patron(v, d)} elemento(s) a {expandir(d)}")
            elif t == "copiar":
                self.gui.log(f"📄 Copié {copiar_patron(v, d)} elemento(s) a {expandir(d)}")
            elif t == "eliminar":
                self.gui.log(f"🗑️ Envié {eliminar_patron(v, self.a_papelera)} elemento(s) a la papelera")
            elif t == "decir":
                self.voz.decir(v)
            elif t == "esperar":
                time.sleep(max(0.0, min(120.0, float(v.replace(",", ".")))))
            elif t == "teclas":
                alias = {"control": "ctrl", "mayusculas": "shift", "mayus": "shift", "escape": "esc", "windows": "win",
                         "suprimir": "delete", "retroceso": "backspace", "intro": "enter", "tabulador": "tab",
                         "espacio": "space"}
                teclas = [alias.get(normalizar(x), x.strip().lower()) for x in v.split("+") if x.strip()]
                pyautogui.hotkey(*teclas)
            elif t == "escribir":
                escribir_unicode(v)
            elif t == "comando":
                self.ejecutar_orden_interna(v)
            else:
                self.gui.log(f"⚠️ Acción desconocida: {t}")
        except Exception as e:
            logging.exception("Acción %s", t)
            self.gui.log(f"⚠️ La acción «{t}» falló: {e}")

    def ejecutar_orden_interna(self, frase):
        """Ejecuta un comando de Alfred por su frase («captura de pantalla»): sirve para armar macros en «Mis comandos»."""
        norm = normalizar(frase)
        cmd = buscar_comando(norm)
        if cmd is None:
            self.gui.log(f"⚠️ «{frase}» no es un comando de Alfred.")
            return
        getattr(self, "cmd_" + cmd["id"])(frase, norm)

    # ── abrir apps y webs ────────────────────────────────────────────────────
    def abrir_app(self, nombre, *args):
        try:
            if self.buscador.lanzar(nombre, *args):
                return True
        except Exception as e:
            logging.exception("Abrir app")
            self.gui.log(f"⚠️ No pude abrir {nombre}: {e}")
            return False
        if normalizar(nombre) == "spotify":
            try:
                os.startfile("spotify:")
                return True
            except OSError:
                pass
        self.gui.log(f"⚠️ No encontré la aplicación «{nombre}» en este PC.")
        return False

    def abrir_web(self, url, navegador=""):
        url = normalizar_url(url)
        if navegador:
            candidatos = [navegador] + (["Opera"] if "gx" in normalizar(navegador) else [])
            for nav in candidatos:
                try:
                    res = self.buscador.resolver(nav)
                    if res and res[0] == "exe":          # solo un .exe admite recibir la dirección
                        subprocess.Popen([res[1], url], cwd=os.path.dirname(res[1]) or None)
                        return True
                except Exception:
                    logging.exception("Abrir navegador")
            self.gui.log(f"⚠️ No pude abrir {navegador} con esa página; uso el navegador predeterminado.")
        webbrowser.open(url)
        return True

    def abrir_entorno(self, completo):
        if completo:
            subprocess.Popen([ruta_sistema("explorer")])
            self.abrir_reproductor()
        carpeta = (self.cfg.get("carpeta_proyecto") or "").strip()
        if carpeta:
            os.makedirs(expandir(carpeta), exist_ok=True)
        self.abrir_app("Cursor", *([expandir(carpeta)] if carpeta else []))
        self.abrir_web(self.cfg.get("youtube"), self.cfg.get("navegador") or "")

    # ── clima / agenda ───────────────────────────────────────────────────────
    def obtener_clima(self):
        ciudad = (self.cfg.get("ciudad") or "").strip()
        if not ciudad:
            return None
        try:
            r = requests.get(f"https://wttr.in/{requests.utils.quote(ciudad)}",
                             params={"format": "%C, %t", "lang": "es"}, timeout=5)
            r.raise_for_status()
            return f"El clima en {ciudad}: {r.text.strip().replace('+', '')}"
        except Exception:
            logging.exception("Clima no disponible")
            return None

    def decir_agenda_hoy(self):
        hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        pendientes = agenda_de_hoy(leer_agenda(ARCHIVO_AGENDA), hoy)
        if pendientes:
            self.voz.decir(f"Tiene {len(pendientes)} recordatorios para hoy.")
            for p in pendientes:
                self.voz.decir(p)
        else:
            self.voz.decir("No tiene recordatorios para hoy.")

    # ── volumen / brillo ─────────────────────────────────────────────────────
    def _endpoint_volumen(self):
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL, CoInitialize
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        try:
            CoInitialize()
        except OSError:
            pass
        dev = AudioUtilities.GetSpeakers()
        if hasattr(dev, "EndpointVolume"):
            return dev.EndpointVolume
        iface = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(iface, POINTER(IAudioEndpointVolume))

    def fijar_volumen(self, pct):
        pct = max(0, min(100, int(pct)))
        try:
            ep = self._endpoint_volumen()
            ep.SetMute(0, None)
            ep.SetMasterVolumeLevelScalar(pct / 100, None)
        except Exception:
            logging.exception("pycaw falló; uso teclas")
            pyautogui.press("volumedown", presses=50)
            pyautogui.press("volumeup", presses=pct // 2)

    def cambiar_volumen(self, delta):
        try:
            ep = self._endpoint_volumen()
            actual = ep.GetMasterVolumeLevelScalar() * 100
            ep.SetMute(0, None)
            ep.SetMasterVolumeLevelScalar(max(0, min(100, actual + delta)) / 100, None)
        except Exception:
            logging.exception("pycaw falló; uso teclas")
            pyautogui.press("volumeup" if delta > 0 else "volumedown", presses=abs(delta) // 2)

    def fijar_brillo(self, pct):
        if sbc is None:
            raise RuntimeError("screen-brightness-control no está instalado")
        sbc.set_brightness(max(0, min(100, int(pct))))

    def cambiar_brillo(self, delta):
        if sbc is None:
            raise RuntimeError("screen-brightness-control no está instalado")
        actual = sbc.get_brightness()
        actual = actual[0] if isinstance(actual, (list, tuple)) else actual
        sbc.set_brightness(max(0, min(100, int(actual) + delta)))

    # ══ COMANDOS INTEGRADOS (cmd_<id>, ver tabla COMANDOS) ════════════════════
    def cmd_trabajo(self, raw, norm):
        self.voz.decir("Excelente, señor. Desplegando herramientas de trabajo.")
        self.abrir_entorno(completo=True)

    def secuencia_bienvenida(self):
        self.voz.decir("Bienvenido a casa, señor.")
        self.abrir_entorno(completo=False)

    def cmd_buenos_dias(self, raw, norm):
        h = datetime.datetime.now().hour
        saludo = "Buenos días" if h < 12 else ("Buenas tardes" if h < 19 else "Buenas noches")
        self.voz.decir(f"{saludo}, señor. Iniciando reporte.")
        clima = self.obtener_clima()
        if clima:
            self.voz.decir(clima)
        webbrowser.open("https://news.google.com")
        self.decir_agenda_hoy()

    def cmd_agenda(self, raw, norm):
        solo_leer = hay(norm, "tengo")
        mostrar = hay(norm, "ensename", "muestra", "muestrame", "abre", "abrir", "ver", "enseñame")
        leer = hay(norm, "lee", "leer", "leeme", "dime", "dictame")
        if solo_leer:
            mostrar, leer = False, True
        elif not mostrar and not leer:
            mostrar = leer = True
        if mostrar:
            self.gui.ui(self.gui.mostrar_agenda)
        if leer:
            self.decir_agenda_hoy()
        elif mostrar:
            self.voz.decir("Aquí tiene su agenda.")

    def cmd_recordar(self, raw, norm):
        tarea = quitar_wake_raw(raw, self.frases_wake)
        tarea = TRIGGER_RECORDAR.sub(" ", tarea, count=1)
        tarea = re.sub(r"\s+", " ", tarea).strip()
        tarea = re.sub(r"^(que|de)\s+", "", tarea)
        if not tarea:
            self.voz.decir("No escuché qué debo anotar.")
            return
        agregar_agenda(ARCHIVO_AGENDA, tarea, datetime.datetime.now())
        self.gui.ui(self.gui.refrescar_agenda)
        self.voz.decir(f"Entendido. He anotado: {tarea}")

    @staticmethod
    def _direccion(norm):
        """-1 bajar, +1 subir, 0 no se dijo. «más bajo» baja y «más alto» sube."""
        if hay(norm, "baja", "bajar", "bajale", "reduce", "reducir", "menos", "disminuye", "bajito", "bajo", "suave"):
            return -1
        if hay(norm, "sube", "subir", "subele", "aumenta", "aumentar", "mas", "alto", "fuerte", "fuerza"):
            return 1
        return 0

    @staticmethod
    def _paso(norm):
        if hay(norm, "poco", "poquito", "tantito", "tantito", "ligeramente", "algo"):
            return 10
        if hay(norm, "mucho", "bastante"):
            return 40
        return 20

    def cmd_brillo(self, raw, norm):
        n = extraer_numero(norm)
        d = self._direccion(norm)
        try:
            if hay(norm, "maximo", "todo", "completo"):
                self.fijar_brillo(100); self.voz.decir("Brillo al cien por ciento.")
            elif hay(norm, "minimo"):
                self.fijar_brillo(10); self.voz.decir("Brillo al mínimo.")
            elif hay(norm, "mitad"):
                self.fijar_brillo(50); self.voz.decir("Brillo a la mitad.")
            elif n is not None:
                self.fijar_brillo(n); self.voz.decir(f"Brillo al {n} por ciento.")
            elif d > 0:
                self.cambiar_brillo(self._paso(norm)); self.voz.decir("Subiendo brillo.")
            elif d < 0:
                self.cambiar_brillo(-self._paso(norm)); self.voz.decir("Bajando brillo.")
            else:
                self.voz.decir("¿Subo o bajo el brillo?")
        except Exception as e:
            logging.exception("Brillo")
            self.gui.log(f"⚠️ Brillo: {e}")
            self.voz.decir("No pude ajustar el brillo en esta pantalla.")

    def cmd_volumen(self, raw, norm):
        n = extraer_numero(norm)
        d = self._direccion(norm)
        if hay(norm, "maximo", "todo", "completo"):
            self.fijar_volumen(100); self.voz.decir("Volumen al máximo.")
        elif hay(norm, "minimo"):
            self.fijar_volumen(5); self.voz.decir("Volumen al mínimo.")
        elif hay(norm, "mitad"):
            self.fijar_volumen(50); self.voz.decir("Volumen a la mitad.")
        elif n is not None:
            self.fijar_volumen(n); self.voz.decir(f"Volumen al {n} por ciento.")
        elif d > 0:
            self.cambiar_volumen(self._paso(norm)); self.voz.decir("Subiendo volumen.")
        elif d < 0:
            self.cambiar_volumen(-self._paso(norm)); self.voz.decir("Bajando volumen.")
        else:
            self.voz.decir("¿Subo o bajo el volumen?")

    def cmd_silencio(self, raw, norm):
        if hay(norm, "sonido"):
            reactivar = hay(norm, "activa", "reactiva", "enciende", "prende", "pon", "devuelve")
        else:
            reactivar = hay(norm, "quita", "quitale", "desmutea", "activa", "reactiva", "sin")
        try:
            self._endpoint_volumen().SetMute(0 if reactivar else 1, None)
        except Exception:
            pyautogui.press("volumemute")
        if reactivar:
            self.voz.decir("Sonido activado.")

    # ── música: detecta el reproductor abierto y lo controla ─────────────────
    def reproductores(self):
        try:
            return reproductores_activos([self.cfg.get("reproductor") or ""])
        except Exception:
            logging.exception("No pude buscar reproductores")
            return []

    def recordar_reproductor(self, p):
        """Si aún no hay reproductor elegido, se queda con el primero que detecta abierto."""
        if p and p["exe"] not in STREAMING and not (self.cfg.get("reproductor") or "").strip():
            self.cfg.set("reproductor", p["nombre"])
            self.gui.log(f"🎵 Reproductor detectado: {p['nombre']} (puedes cambiarlo en ☰ Menú → General).")

    def reproductor_activo(self):
        p = elegir_reproductor(self.reproductores(), self.cfg.get("reproductor") or "", self._ult_repro)
        if p:
            self._ult_repro = p["nombre"]
            self.recordar_reproductor(p)
        return p

    def control_media(self, accion):
        p = self.reproductor_activo()
        via = "?"
        try:
            via = enviar_media(accion, p)
        except Exception:
            logging.exception("Control de música")
            pyautogui.press({"siguiente": "nexttrack", "anterior": "prevtrack"}.get(accion, "playpause"))
            via = "tecla"
        logging.info("Música: %s → %s por %s", accion, p["nombre"] if p else "sistema", via)
        icono = {"siguiente": "⏭️ Siguiente canción", "anterior": "⏮️ Canción anterior", "pausa": "⏯️ Pausa / reanudar",
                 "play": "▶️ Reproducir", "detener": "⏹️ Detener"}[accion]
        self.gui.log(f"{icono} · {p['nombre'] if p else 'reproductor del sistema'}"
                     + (" · tecla multimedia (instala winrt para controlarlo directo)" if via == "tecla" and p and p["exe"] not in APPCOMMAND_OK else ""))
        return p

    def cmd_media(self, raw, norm):
        if hay(norm, "anterior", "atras", "regresa", "retrocede", "previa"):
            self.control_media("anterior")
        elif hay(norm, "siguiente", "proxima", "salta", "cambia", "sigue", "otra", "pasa", "adelanta"):
            self.control_media("siguiente")
        elif hay(norm, "detener", "detente", "deten", "stop", "para", "parar", "alto"):
            self.control_media("detener")
        elif hay(norm, "pausa", "pausar", "pausala", "pausame"):
            self.control_media("pausa")
        else:                                              # reanuda / continúa / play
            self.control_media("play")

    def abrir_reproductor(self):
        """Abre tu reproductor (el elegido en el menú o el primero que encuentre). True si queda abierto."""
        if self.reproductores():
            return True
        pref = (self.cfg.get("reproductor") or "").strip()
        if pref:
            return self.abrir_app(pref)
        for nombre in ("MusicBee", "foobar2000", "AIMP", "VLC", "Winamp", "iTunes"):
            try:
                res = self.buscador.resolver(nombre)
            except Exception:
                res = None
            if res:
                self.cfg.set("reproductor", nombre)
                self.gui.log(f"🎵 Reproductor encontrado: {nombre} (puedes cambiarlo en ☰ Menú → General).")
                return self.abrir_app(nombre)
        return self.abrir_app("Spotify")

    def cmd_spotify(self, raw, norm):
        if hay(norm, "spotify", "espotifai", "espoti"):
            self.voz.decir("Spotify en marcha, señor.")
            self.abrir_app("Spotify")
            return
        p = self.reproductor_activo()
        if p:
            self.control_media("play")
            self.voz.decir(f"Reanudando {p['nombre']}.")
            return
        self.voz.decir("Abriendo tu reproductor de música, señor.")
        if not self.abrir_reproductor():
            self.voz.decir("No encontré ningún reproductor. Ábrelo una vez y lo recordaré, o elígelo en el menú.")

    def cmd_que_suena(self, raw, norm):
        p = self.reproductor_activo()
        datos = smtc("info", _claves_sesion(p), info=True)             # título y artista según Windows (SMTC)
        if datos and datos[0]:
            self.voz.decir(f"En {p['nombre'] if p else 'tu reproductor'} suena: {datos[0]}"
                           + (f", de {datos[1]}." if datos[1] else "."))
            return
        if not p:
            self.voz.decir("No veo ningún reproductor de música abierto.")
            return
        titulo = p["titulo"].strip()
        for sufijo in (p["nombre"], "VLC media player", "foobar2000", "AIMP", "MusicBee", "Winamp", "iTunes",
                       "MediaMonkey", "PotPlayer", "Reproductor de Windows Media"):
            titulo = re.sub(r"\s*[-–—|\[(]*\s*" + re.escape(sufijo) + r"\s*[\])]*\s*$", "", titulo, flags=re.I).strip()
        nt = normalizar(titulo)
        if not nt or nt in ("spotify", "spotify premium", "spotify free") or nt == normalizar(p["nombre"]):
            self.voz.decir(f"No veo qué canción suena en {p['nombre']}.")
        else:
            self.voz.decir(f"En {p['nombre']} suena: {titulo}.")

    def exe_reproductor_local(self):
        """Programa con el que abrir carpetas de música: uno LOCAL (nunca Spotify y similares, que no abren tus
        archivos y reproducen su propia versión en streaming)."""
        locales = [x for x in self.reproductores() if x["exe"] not in STREAMING]
        p = elegir_reproductor(locales, self.cfg.get("reproductor") or "", self._ult_repro)
        if p and p["ruta"]:
            return p["ruta"]
        pref = (self.cfg.get("reproductor") or "").strip()
        if pref and (normalizar(pref) in {normalizar(n) for n in ("Spotify", "TIDAL", "Deezer", "Amazon Music", "YouTube Music")}):
            pref = ""                                     # el preferido es de streaming: no sirve para archivos
        for nombre in ([pref] if pref else []) + ["foobar2000", "MusicBee", "AIMP", "VLC", "Winamp"]:   # el elegido y, si no sirve, uno instalado
            try:
                res = self.buscador.resolver(nombre)
            except Exception:
                res = None
            if res and res[0] == "exe" and os.path.basename(res[1]).lower() not in STREAMING:
                return res[1]
        return None

    def abrir_lista(self, pistas):
        """Abre las pistas en tu reproductor LOCAL (nunca Spotify). Solo usa una lista .m3u8 con los reproductores que
        la entienden (VLC, foobar2000, MusicBee, AIMP…); con cualquier otro (Harmonoid…) le pasa los archivos de
        música directamente, porque si no los toma por una canción llamada «alfred_lista.m3u8»."""
        exe = self.exe_reproductor_local()
        try:
            if exe and os.path.basename(exe).lower() in ENTIENDEN_LISTAS:
                lista = os.path.join(BASE_DIR, "alfred_lista.m3u8")
                with open(lista, "w", encoding="utf-8") as f:
                    f.write("#EXTM3U\n" + "\n".join(pistas) + "\n")
                extra = ["--one-instance", "--no-playlist-enqueue"] if os.path.basename(exe).lower() == "vlc.exe" else []
                subprocess.Popen([exe] + extra + [lista], cwd=os.path.dirname(exe) or None)
            elif exe:                                       # reproductor que acepta archivos como argumentos
                elegidas, largo = [], 0
                for p in pistas:
                    largo += len(p) + 3
                    if largo > 28000:                       # límite de la línea de comandos de Windows
                        break
                    elegidas.append(p)
                subprocess.Popen([exe] + elegidas, cwd=os.path.dirname(exe) or None)
                if len(elegidas) < len(pistas):
                    self.gui.log(f"ℹ️ {os.path.basename(exe)} solo admite {len(elegidas)} de las {len(pistas)} pistas en una "
                                 "orden (límite de Windows); el resto no se añadió a la cola.")
            else:                                           # sin programa localizado: reproductor predeterminado del archivo
                self.gui.log("⚠️ No localicé el programa de tu reproductor, así que abro solo la primera canción con el "
                             "predeterminado de Windows. Para que siga con el resto, abre tu reproductor una vez "
                             "(Alfred lo recuerda) o elígelo en ☰ Menú → General → Reproductor de música.")
                os.startfile(pistas[0])
        except OSError as e:
            logging.exception("Abrir pistas")
            self.gui.log(f"⚠️ No pude abrir la música: {e}")
            os.startfile(pistas[0])

    def reproducir_carpeta(self, carpeta, aleatorio=False):
        """Hace una lista con las canciones de la carpeta y la abre en tu reproductor. Devuelve cuántas canciones."""
        import random
        pistas = listar_audio(carpeta)
        if not pistas:
            return 0
        if aleatorio:
            random.shuffle(pistas)
        self.abrir_lista(pistas)
        return len(pistas)

    def reproducir_cancion(self, ruta):
        """Pone la canción y, después, el resto de las de su carpeta (como un álbum). Devuelve cuántas pistas."""
        carpeta = os.path.dirname(ruta)
        hermanas = [p for p in listar_audio(carpeta) if os.path.dirname(p) == carpeta]
        if ruta in hermanas:
            i = hermanas.index(ruta)
            pistas = hermanas[i:] + hermanas[:i]
        else:
            pistas = [ruta] + hermanas
        self.abrir_lista(pistas)
        return len(pistas)

    def indice_canciones(self):
        ahora = time.time()
        t, idx = self._indice_canciones
        if not idx and ahora - t < 30 and t:                 # ya se buscó hace nada y no había nada
            return idx
        if not idx or ahora - t > 900:
            self.gui.log("🔎 Indexando tus canciones (la primera vez puede tardar un poco)…")
            idx = indexar_canciones(raices_musica(self.cfg.get("carpetas_musica")))
            self._indice_canciones = (time.time(), idx)
            self.gui.log(f"🎼 {len(idx)} canciones indexadas.")
            try:                                             # 3.2.1: artista y álbum de las etiquetas
                etq, pend = indexar_etiquetas([x[0] for x in idx])
                self._etiquetas = (time.time(), etq)
                self.gui.log(f"🏷️ Etiquetas: {len(etq['artista'])} artistas y {len(etq['album'])} álbumes"
                             + (f" (me faltan {pend} canciones por leer; sigo en la próxima búsqueda)" if pend else "") + ".")
                if pend:
                    self._indice_canciones = (time.time() - 900 + 20, idx)      # vuelve a pasar pronto para acabar
            except Exception:
                logging.exception("Leer etiquetas")
        return idx

    def buscar_cancion(self, pedido):
        res = mejor_cancion(self.indice_canciones(), pedido)
        if not res and time.time() - self._indice_canciones[0] > 30:     # quizá es música nueva: vuelve a mirar
            self._indice_canciones = (0.0, [])
            res = mejor_cancion(self.indice_canciones(), pedido)
        return res

    @staticmethod
    def titulo_bonito(ruta):
        t = os.path.splitext(os.path.basename(ruta))[0]
        return re.sub(r"^\d{1,3}\s*[-._)]*\s*", "", t) or t

    def poner_cancion(self, ruta, pedido, puntos):
        n = self.reproducir_cancion(ruta)
        titulo = self.titulo_bonito(ruta)
        self.gui.log(f"🔎 Oí «{pedido}» → «{titulo}» (parecido {puntos:.0%})")
        self.gui.log(f"🎵 {titulo}  ·  {n} pista(s) en cola  ·  {ruta}")
        self.voz.decir(f"Reproduciendo {titulo}.")

    def poner_carpeta(self, ruta, pedido, puntos, aleatorio=False):
        nombre = os.path.basename(ruta.rstrip("\\/")) or ruta
        self.gui.log(f"🔎 Oí «{pedido}» → carpeta «{nombre}» (parecido {puntos:.0%})")
        n = self.reproducir_carpeta(ruta, aleatorio)
        if not n:
            self.voz.decir(f"La carpeta {nombre} no tiene canciones.")
            return
        self.gui.log(f"🎵 {nombre}: {n} canciones" + (" (aleatorio)" if aleatorio else "") + f"  ·  {ruta}")
        self.voz.decir(f"Reproduciendo {nombre}" + (" en aleatorio." if aleatorio else "."))

    def no_encontrado(self, pedido, que):
        cerca = []
        try:                                                     # qué es lo más parecido, para saber qué oyó y qué hay
            c = mejor_cancion(self.indice_canciones(), pedido, minimo=0.0)
            if c and c[1] >= 0.5:
                cerca.append(f"canción «{self.titulo_bonito(c[0])}» ({c[1]:.0%})")
            f = mejor_carpeta(self._indice_musica[1], pedido, minimo=0.5)
            if f:
                cerca.append(f"carpeta «{os.path.basename(f[0].rstrip(chr(92) + '/'))}» ({f[1]:.0%})")
        except Exception:
            logging.exception("Lo más parecido")
        self.gui.log(f"❓ No encontré {que} parecida a «{pedido}». Busqué en: "
                     + (", ".join(raices_musica(self.cfg.get("carpetas_musica"))) or "(ninguna carpeta de música)")
                     + ". Busco por nombre de archivo y de carpeta (no por etiquetas). "
                       "Añade más en ☰ Menú → General → Carpetas de música.")
        if cerca:
            self.gui.log("💡 Lo más parecido que hay: " + " · ".join(cerca))
        self.voz.decir(f"No encontré {que} parecida a {pedido}.")

    def buscar_etiqueta(self, pedido):
        """(tipo, nombre, rutas, puntos) del artista o álbum (según las etiquetas) que más se parece a lo pedido."""
        self.indice_canciones()
        dic = self._etiquetas[1]
        mejor = None
        for tipo in ("artista", "album"):
            h = mejor_etiqueta(dic.get(tipo, {}), pedido)
            if h and (mejor is None or h[2] > mejor[3] + 0.02):          # a igualdad, el artista
                mejor = (tipo, h[0], h[1], h[2])
        return mejor

    def poner_etiqueta(self, etq, pedido, puntos):
        tipo, nombre, rutas, _ = etq
        pistas = sorted(set(rutas), key=_clave_natural)
        self.gui.log(f"🔎 Oí «{pedido}» → {tipo} «{nombre}» (parecido {puntos:.0%})")
        self.abrir_lista(pistas)
        self.gui.log(f"🎤 {nombre}: {len(pistas)} canciones en cola")
        self.voz.decir(f"Reproduciendo {nombre}.")

    def _resolver_pedido(self, pedido, es_artista=False):
        """(tipo, dato, puntos) de lo que más se parece a un pedido: una canción, una carpeta o un artista/álbum
        de las etiquetas (tipo «etiqueta»). Si pidió «canciones de X» / «la banda X», el artista manda. None si
        no hay nada."""
        cancion = self.buscar_cancion(pedido)
        carpeta = self.buscar_carpeta_musica(pedido)
        etq = self.buscar_etiqueta(pedido)
        otro = max([x[1] for x in (cancion, carpeta) if x] or [0.0])
        if etq and ((es_artista and etq[3] >= 0.75) or (etq[3] >= 0.9 and etq[3] > otro)):
            return ("etiqueta", etq, etq[3])
        if es_artista and carpeta and carpeta[1] >= 0.8:
            return ("carpeta", carpeta[0], carpeta[1])
        if carpeta and carpeta[1] >= 0.9 and (not cancion or carpeta[1] > cancion[1]):
            return ("carpeta", carpeta[0], carpeta[1])
        if cancion:
            return ("cancion", cancion[0], cancion[1])
        if carpeta:
            return ("carpeta", carpeta[0], carpeta[1])
        return None

    # ── plataformas (Spotify, YouTube) ───────────────────────────────────────
    def plataforma_preferida(self):
        t = normalizar(self.cfg.get("plataforma_musica") or "")
        if not t:
            return None
        for frase, plat in sorted(PLATAFORMAS, key=lambda x: -len(x[0])):
            if frase in t:
                return plat
        return None

    def _abrir_spotify_app(self):
        try:
            os.startfile("spotify:")
        except OSError:
            self.abrir_web("https://open.spotify.com", self.cfg.get("navegador") or "")

    def poner_en_plataforma(self, pedido, plat, es_artista=False):
        consulta = " ".join(t for t in pedido.split() if t not in ("de", "del")) or pedido
        try:
            if plat == "spotify":
                self._poner_spotify(pedido, consulta, es_artista)
            else:
                self._poner_youtube(pedido, consulta, plat == "ytmusic")
        except Exception as e:
            logging.exception("Plataforma de música")
            self.gui.log(f"⚠️ No pude poner «{pedido}»: {e}")
            self.voz.decir("No pude poner esa canción.")

    def _poner_spotify(self, pedido, consulta, es_artista):
        sp = self.spotify
        if not sp.client_id():                                     # sin Client ID: al menos abre la búsqueda
            try:
                os.startfile("spotify:search:" + quote(consulta))
            except OSError:
                self.abrir_web("https://open.spotify.com/search/" + quote(consulta), self.cfg.get("navegador") or "")
            self.gui.log("🎧 Abrí la búsqueda en Spotify. Para que Alfred la ponga solo: crea una app gratis en "
                         "developer.spotify.com/dashboard (Redirect URI: " + sp.REDIRECT + ", API: Web API), pega su "
                         "Client ID en ☰ Menú → General → Spotify Client ID y pulsa «Conectar Spotify» (requiere Premium).")
            self.voz.decir(f"Abrí la búsqueda de {pedido} en Spotify. Para que la ponga yo, conecta tu cuenta en el menú.")
            return
        if not sp.conectado():
            self.voz.decir("Voy a conectar tu cuenta de Spotify. Autoriza en el navegador.")
            if not sp.conectar(self.gui.log):
                self.voz.decir("No pude conectar Spotify.")
                return
            self.gui.log("🎧 Spotify conectado.")
        h = sp.buscar(consulta, es_artista)
        if not h:
            self.gui.log(f"❓ Spotify no encontró nada parecido a «{pedido}».")
            self.voz.decir(f"No encontré {pedido} en Spotify.")
            return
        quien = f" · {h['artista']}" if h["artista"] else ""
        self.gui.log(f"🔎 Oí «{pedido}» → Spotify: {h['tipo']} «{h['nombre']}»{quien}")
        res = sp.reproducir(h, self._abrir_spotify_app)
        if res == "ok":
            self.gui.log(f"🎧 {h['nombre']}{quien}  ·  Spotify")
            self.voz.decir(f"Reproduciendo {h['nombre']} en Spotify.")
        elif res == "premium":
            self.gui.log("⚠️ Spotify solo deja controlar la reproducción desde otras apps a cuentas Premium "
                         "(y la app de developer.spotify.com debe ser de una cuenta Premium).")
            self.voz.decir("Spotify solo me deja poner música con una cuenta Premium.")
        elif res == "sin_dispositivo":
            self.gui.log("⚠️ No encontré ningún dispositivo de Spotify abierto. Abre la app de Spotify e inicia sesión.")
            self.voz.decir("No encuentro Spotify abierto. Ábrelo e inténtalo otra vez.")
        else:
            self.gui.log(f"⚠️ Spotify respondió: {res}")
            self.voz.decir("Spotify no me dejó ponerla.")

    def _poner_youtube(self, pedido, consulta, musica):
        vid = None
        try:                                                       # primer vídeo de los resultados (sin API ni clave)
            r = requests.get("https://www.youtube.com/results",
                             params={"search_query": consulta, "sp": "EgIQAQ=="},
                             headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
                                      "Accept-Language": "es-MX,es;q=0.9,en;q=0.6"}, timeout=8)
            ids = re.findall(r'"videoId":"([\w-]{11})"', r.text)
            vid = ids[0] if ids else None
        except Exception:
            logging.exception("YouTube: buscar")
        nombre = "YouTube Music" if musica else "YouTube"
        if vid:
            url = ("https://music.youtube.com/watch?v=" if musica else "https://www.youtube.com/watch?v=") + vid
        else:
            url = ("https://music.youtube.com/search?q=" if musica else "https://www.youtube.com/results?search_query=") + quote_plus(consulta)
        self.gui.log(f"🔎 Oí «{pedido}» → {nombre}" + ("" if vid else " (solo pude abrir la búsqueda)"))
        self.abrir_web(url, self.cfg.get("navegador") or "")
        self.voz.decir(f"Reproduciendo {pedido} en {nombre}." if vid else f"Abrí la búsqueda de {pedido} en {nombre}.")

    def cmd_cancion(self, raw, norm):
        datos = pedido_cancion_ex(norm)
        pedido, es_art, plat = datos if datos else (None, False, None)
        if not pedido:
            self.voz.decir("¿Qué canción quieres que ponga?")
            return
        plat = plat or self.plataforma_preferida()
        if plat:                                       # «pon X en Spotify» o plataforma por defecto del menú
            self.poner_en_plataforma(pedido, plat, es_art)
            return
        mejor = None                                   # (pedido, tipo, dato, puntos)
        for i, p in enumerate(self.pedidos_alternos(pedido_cancion, pedido)):
            r = self._resolver_pedido(p, es_art)
            # una lectura alterna solo gana si es claramente mejor que la elegida
            if r and (mejor is None or r[2] > mejor[3] + 0.03):
                mejor = (p, *r)
            if mejor and mejor[3] >= 0.9:
                break
        if not mejor:
            if self.spotify.conectado():
                self.gui.log("🎧 No la encontré en tu biblioteca; la busco en Spotify.")
                self.poner_en_plataforma(pedido, "spotify", es_art)
                return
            self.no_encontrado(pedido, "una canción")
            return
        p, tipo, ruta, puntos = mejor
        if p != pedido:
            self.gui.log(f"🔎 La lectura «{pedido}» no encajaba; con «{p}» sí.")
        if tipo == "carpeta":
            self.poner_carpeta(ruta, p, puntos)
        elif tipo == "etiqueta":
            self.poner_etiqueta(ruta, p, puntos)
        else:
            self.poner_cancion(ruta, p, puntos)

    def buscar_carpeta_musica(self, pedido):
        ahora = time.time()
        t, idx = self._indice_musica
        if not idx or ahora - t > 600:
            self.gui.log("🔎 Buscando tus carpetas de música…")
            idx = indexar_musica(raices_musica(self.cfg.get("carpetas_musica")))
            self._indice_musica, t = (ahora, idx), ahora
        res = mejor_carpeta(idx, pedido)
        if not res and ahora - t > 30:                 # quizá es una carpeta nueva: vuelve a mirar
            idx = indexar_musica(raices_musica(self.cfg.get("carpetas_musica")))
            self._indice_musica = (ahora, idx)
            res = mejor_carpeta(idx, pedido)
        return res

    def cmd_carpeta_musica(self, raw, norm):
        frases = next(c["frases"] for c in COMANDOS if c["id"] == "carpeta_musica")
        variantes, aleatorio = pedidos_musica(norm, frases)
        if not variantes:
            self.voz.decir("¿Qué carpeta quieres que reproduzca?")
            return
        pedidos = list(variantes)                      # «mis canciones» puede ser el nombre de la carpeta
        for orden in self.alternas_actuales():         # y lo que oyó el otro idioma / las otras alternativas
            pm = pedidos_musica(orden, frases, estricto=True)
            for v in (pm[0] if pm else []):
                if v not in pedidos and pedido_valido(v):
                    pedidos.append(v)
        pedidos = pedidos[:6]
        mejor = None                                   # (pedido, ruta, puntos)
        for p in pedidos:
            h = self.buscar_carpeta_musica(p)
            if h and (mejor is None or h[1] > mejor[2] + 0.03):
                mejor = (p, h[0], h[1])
            if mejor and mejor[2] >= 0.9:
                break
        if mejor:
            if mejor[0] != pedidos[0]:
                self.gui.log(f"🔎 La lectura «{pedidos[0]}» no encajaba; con «{mejor[0]}» sí.")
            self.poner_carpeta(mejor[1], mejor[0], mejor[2], aleatorio)
            return
        for p in pedidos:                              # no hay carpeta con ese nombre: quizá es una canción
            cancion = self.buscar_cancion(p)
            if cancion:
                self.poner_cancion(cancion[0], p, cancion[1])
                return
        self.no_encontrado(pedidos[0], "una carpeta")

    def cmd_abrir(self, raw, norm):
        nombre = nombre_a_abrir(norm)
        if not nombre:
            self.voz.decir("¿Qué quieres que abra?")
            return
        nombres = self.pedidos_alternos(nombre_a_abrir, nombre)       # lo oído en español y en inglés
        for n in nombres:
            carpeta = CARPETAS_CONOCIDAS.get(n)
            if carpeta:
                home = os.path.expanduser("~")
                bases = [home] + [os.environ.get(v) for v in ("OneDrive", "OneDriveConsumer") if os.environ.get(v)]
                for base in bases:
                    ruta = os.path.join(base, carpeta)
                    if os.path.isdir(ruta):
                        os.startfile(ruta)
                        self.voz.decir(f"Abriendo {n}.")
                        return
        for n in nombres:
            sitio = SITIOS.get(n)
            if sitio:
                self.abrir_web(sitio, self.cfg.get("navegador") or "")
                self.voz.decir(f"Abriendo {n}.")
                return
        candidatos = []
        for n in nombres:
            for c in (n, corregir_app(n)):                 # «crom» -> chrome, «guord» -> word…
                if c and c not in candidatos:
                    candidatos.append(c)
        for c in candidatos:
            try:
                if self.buscador.resolver(c):
                    self.voz.decir(f"Abriendo {c}.")
                    self.abrir_app(c)
                    return
            except Exception:
                logging.exception("Abrir app por voz")
        self.gui.log(f"⚠️ No encontré «{nombre}»" + (f" (probé también: {', '.join(candidatos[1:4])})" if len(candidatos) > 1 else "")
                     + ". Si es una app, ábrela una vez o indica su ruta en ☰ Menú.")
        self.voz.decir(f"No encontré {nombre} en este equipo.")

    def cmd_buscar_web(self, raw, norm):
        toks = norm.split()
        youtube = "youtube" in toks
        while toks and toks[0] in {"busca", "buscar", "buscame", "googlea", "googlear", "investiga", "en", "youtube",
                                   "google", "internet", "la", "web", "el", "navegador", "por", "favor", "bing"}:
            toks.pop(0)
        consulta = " ".join(toks)
        if not consulta:
            self.voz.decir("¿Qué quieres que busque?")
            return
        q = requests.utils.quote(consulta)
        url = (f"https://www.youtube.com/results?search_query={q}" if youtube
               else f"https://www.google.com/search?q={q}")
        self.abrir_web(url, self.cfg.get("navegador") or "")
        self.gui.log(f"🌐 Buscando «{consulta}» en {'YouTube' if youtube else 'Google'}")
        self.voz.decir(f"Buscando {consulta}.")

    def cmd_segundo_plano(self, raw, norm):
        self.voz.decir("De acuerdo, paso a segundo plano. Llámame por mi nombre cuando me necesites.", esperar=True)
        self.gui.ui(self.gui.ocultar)

    def cmd_mostrar(self, raw, norm):
        self.gui.ui(self.gui.mostrar)
        self.voz.decir("Aquí estoy, señor.")

    def cmd_descanso(self, raw, norm):
        self.voz.decir("Entendido. Minimizando todas las ventanas.")
        pyautogui.hotkey("win", "d")

    def cmd_calculadora(self, raw, norm):
        subprocess.Popen([ruta_sistema("calc")])

    def cmd_bloc(self, raw, norm):
        subprocess.Popen([ruta_sistema("notepad")])

    def cmd_explorador(self, raw, norm):
        subprocess.Popen([ruta_sistema("explorer")])

    def cmd_hora(self, raw, norm):
        self.voz.decir(texto_hora(datetime.datetime.now()))

    def cmd_fecha(self, raw, norm):
        self.voz.decir(texto_fecha(datetime.datetime.now()))

    def cmd_ayuda(self, raw, norm):
        self.gui.ui(self.gui.mostrar_ayuda)
        self.voz.decir("Aquí tiene la lista de comandos.")

    def cmd_salir(self, raw, norm):
        self.voz.decir("Apagando sistemas. Hasta pronto, señor.", esperar=True)
        self.activo = False
        self.gui.ui(self.gui.salir)


# ══════════════════════════════════════════════════════════════════════════════
#  INTERFAZ
# ══════════════════════════════════════════════════════════════════════════════
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def elegir_fuentes():
    """Tipografía técnica (Bahnschrift, viene con Windows 10/11) para títulos; si no está, Segoe UI."""
    global F_TIT
    try:
        import tkinter.font as tkfont
        familias = set(tkfont.families())
        if "Bahnschrift SemiBold" in familias:
            F_TIT = "Bahnschrift SemiBold"
        elif "Bahnschrift" in familias:
            F_TIT = "Bahnschrift"
    except Exception:
        logging.exception("No pude elegir la tipografía")


def aplicar_tema_futurista():
    """Cambia los colores por defecto de CustomTkinter: así TODAS las ventanas (menú, agenda, mis comandos…) comparten
    el mismo estilo sin tocar widget por widget. Solo toca claves que existan en la versión instalada."""
    try:
        T = ctk.ThemeManager.theme
        P = PAL

        def poner(widget, **kw):
            if widget not in T:
                return
            for clave, valor in kw.items():
                if clave in T[widget]:
                    T[widget][clave] = [valor, valor] if isinstance(valor, str) else valor
        poner("CTk", fg_color=P["bg"])
        poner("CTkToplevel", fg_color=P["bg"])
        poner("CTkFrame", fg_color=P["card"], top_fg_color=P["card2"], border_color=P["line"], corner_radius=12)
        poner("CTkButton", fg_color=P["card2"], hover_color=P["hover"], border_color=P["line"], text_color=P["text"],
              text_color_disabled=P["muted"], corner_radius=10, border_width=1)
        poner("CTkLabel", text_color=P["text"])
        poner("CTkEntry", fg_color=P["bg2"], border_color=P["line"], text_color=P["text"],
              placeholder_text_color=P["muted"], corner_radius=8, border_width=1)
        poner("CTkTextbox", fg_color=P["bg2"], border_color=P["line"], text_color=P["text"],
              scrollbar_button_color=P["track"], scrollbar_button_hover_color=P["hover"], corner_radius=8)
        poner("CTkScrollbar", button_color=P["track"], button_hover_color=P["hover"])
        poner("CTkScrollableFrame", label_fg_color=P["card2"])
        poner("CTkSwitch", progress_color=P["acc"], button_color=P["neon"], button_hover_color=P["acc_luz"],
              fg_color=P["track"], text_color=P["text"])
        poner("CTkCheckBox", fg_color=P["acc"], hover_color=P["neon"], border_color=P["line"], text_color=P["text"])
        poner("CTkRadioButton", fg_color=P["acc"], hover_color=P["neon"], border_color=P["line"], text_color=P["text"])
        poner("CTkSegmentedButton", selected_color=P["acc"], selected_hover_color=P["neon"], unselected_color=P["card2"],
              unselected_hover_color=P["hover"], fg_color=P["card2"], text_color=P["text"])
        poner("CTkSlider", progress_color=P["acc"], button_color=P["neon"], button_hover_color=P["acc_luz"],
              fg_color=P["track"])
        poner("CTkProgressBar", progress_color=P["acc"], fg_color=P["track"], border_color=P["line"])
        for w in ("CTkOptionMenu", "CTkComboBox"):
            poner(w, fg_color=P["card2"], button_color=P["track"], button_hover_color=P["hover"], text_color=P["text"],
                  dropdown_fg_color=P["card"], dropdown_hover_color=P["hover"], dropdown_text_color=P["text"],
                  border_color=P["line"])
        poner("CTkTabview", fg_color=P["card"], segmented_button_fg_color=P["card2"],
              segmented_button_selected_color=P["acc"], segmented_button_selected_hover_color=P["neon"],
              segmented_button_unselected_color=P["card2"], segmented_button_unselected_hover_color=P["hover"],
              border_color=P["line"], text_color=P["text"])
    except Exception:
        logging.exception("No pude aplicar el tema")


aplicar_tema_futurista()


def forzar_primer_plano(win):
    """Windows no deja que un programa en segundo plano robe el foco; se engaña uniéndose al hilo de la ventana activa."""
    try:
        u, k = ctypes.windll.user32, ctypes.windll.kernel32
        hwnd = u.GetParent(win.winfo_id()) or win.winfo_id()
        if u.IsIconic(hwnd):
            u.ShowWindow(hwnd, 9)                                   # SW_RESTORE
        else:
            u.ShowWindow(hwnd, 5)                                   # SW_SHOW
        activa = u.GetForegroundWindow()
        hilo_activo = u.GetWindowThreadProcessId(activa, None) if activa else 0
        hilo_propio = k.GetCurrentThreadId()
        unido = bool(hilo_activo and hilo_activo != hilo_propio and u.AttachThreadInput(hilo_propio, hilo_activo, True))
        try:
            u.BringWindowToTop(hwnd)
            u.SetForegroundWindow(hwnd)
        finally:
            if unido:
                u.AttachThreadInput(hilo_propio, hilo_activo, False)
    except Exception:
        logging.exception("No pude traer la ventana al frente")


def traer_al_frente(win):
    win.lift()
    win.attributes("-topmost", True)
    win.after(300, lambda: win.attributes("-topmost", False))
    win.focus_force()
    win.after(30, lambda: forzar_primer_plano(win))


class VentanaComandos(ctk.CTkToplevel):
    """Manual: se arma desde la tabla COMANDOS (así nunca queda desactualizado), agrupado por secciones y con buscador."""

    def __init__(self, master, alfred):
        super().__init__(master)
        self.alfred = alfred
        self.nombre = alfred.nombre if alfred else "Alfred"
        self.title("Manual de Alfred")
        self.geometry("580x720")
        self.configure(fg_color=PAL["bg"])
        ctk.CTkLabel(self, text="COMANDOS", font=(F_TIT, 20), text_color=PAL["neon"]).pack(anchor="w", padx=22, pady=(16, 0))
        self.lbl_cuenta = ctk.CTkLabel(self, text="", font=("Segoe UI", 12), text_color=PAL["muted"])
        self.lbl_cuenta.pack(anchor="w", padx=22)
        self.buscar = ctk.CTkEntry(self, height=38, placeholder_text="🔍  Buscar: volumen, ventana, alarma, captura, apagar…")
        self.buscar.pack(fill="x", padx=20, pady=(10, 8))
        self.buscar.bind("<KeyRelease>", lambda e: self._pintar())
        self.txt = ctk.CTkTextbox(self, font=("Segoe UI", 12), wrap="word")
        self.txt.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        tw = self.txt._textbox
        tw.tag_configure("h", foreground=PAL["neon"], font=(F_TIT, 12), spacing1=14, spacing3=4)
        tw.tag_configure("d", foreground=PAL["text"], font=("Segoe UI Semibold", 12), spacing1=6)
        tw.tag_configure("e", foreground=PAL["acc_luz"], font=("Segoe UI", 11), lmargin1=18, lmargin2=18)
        tw.tag_configure("i", foreground=PAL["muted"], font=("Segoe UI", 11), lmargin1=18, lmargin2=18)
        self._pintar()
        self.buscar.focus_set()
        traer_al_frente(self)

    def _grupos(self):
        grupos = [("BÁSICOS", [c for c in COMANDOS if not c.get("seccion")])]
        for c in COMANDOS:
            if c.get("seccion"):
                for g in grupos:
                    if g[0] == c["seccion"]:
                        g[1].append(c)
                        break
                else:
                    grupos.append((c["seccion"], [c]))
        return grupos

    def _pintar(self):
        t = normalizar(self.buscar.get())
        con_ingles = bool(self.alfred and self.alfred.cfg.get("idioma_en"))
        tb = self.txt
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        total = sum(len(g[1]) for g in self._grupos())
        mostrados = 0
        propios = [c for c in (self.alfred.personalizados if self.alfred else []) if not t or t in normalizar(c["frase"])]
        if propios:
            tb.insert("end", "TUS COMANDOS\n", "h")
            for c in propios:
                tb.insert("end", f"«{self.nombre} {c['frase']}»\n", "e")
        for titulo, lista in self._grupos():
            sel = [c for c in lista if not t or t in normalizar(c["desc"] + " " + c["ejemplo"] + " " + " ".join(c["frases"]))]
            if not sel:
                continue
            tb.insert("end", titulo + "\n", "h")
            for c in sel:
                mostrados += 1
                tb.insert("end", "• " + c["desc"] + "\n", "d")
                tb.insert("end", "«" + c["ejemplo"].replace("Alfred", self.nombre) + "»\n", "e")
                if con_ingles and c["id"] in EJEMPLOS_EN:
                    tb.insert("end", f"🇬🇧 «{self.nombre} {EJEMPLOS_EN[c['id']]}»\n", "i")
        if not mostrados and not propios:
            tb.insert("end", "\nNo hay comandos con esa palabra.", "i")
        tb.configure(state="disabled")
        self.lbl_cuenta.configure(text=f"{mostrados} de {total} comandos integrados"
                                       + (f"  ·  {len(propios)} tuyos" if propios else ""))


class VentanaAgenda(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Agenda de Alfred")
        self.geometry("540x580")
        ctk.CTkLabel(self, text="📅 AGENDA", font=("Consolas", 16, "bold")).pack(pady=(12, 4))
        self.lista = ctk.CTkScrollableFrame(self)
        self.lista.pack(fill="both", expand=True, padx=12, pady=6)
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=12, pady=(0, 12))
        self.entrada = ctk.CTkEntry(barra, placeholder_text="Nuevo recordatorio…")
        self.entrada.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entrada.bind("<Return>", lambda e: self.anadir())
        ctk.CTkButton(barra, text="➕ Añadir", width=90, command=self.anadir).pack(side="right")
        self.refrescar()
        traer_al_frente(self)

    def refrescar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        items = leer_agenda(ARCHIVO_AGENDA)
        hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        if not items:
            ctk.CTkLabel(self.lista, text="No hay recordatorios todavía.").pack(pady=20)
            return
        indexados = list(enumerate(items))
        de_hoy = [p for p in indexados if p[1]["fecha"] == hoy]
        otros = sorted([p for p in indexados if p[1]["fecha"] != hoy], key=lambda p: p[1]["fecha"], reverse=True)
        for idx, it in de_hoy + otros:
            fila = ctk.CTkFrame(self.lista)
            fila.pack(fill="x", pady=3)
            cuando = ("HOY " if it["fecha"] == hoy else it["fecha"] + " ") + it["hora"]
            ctk.CTkLabel(fila, text=cuando.strip(), width=120, anchor="w", font=("Consolas", 11, "bold"),
                         text_color="#2c73d2" if it["fecha"] == hoy else "#9a9a9a").pack(side="left", padx=6)
            ctk.CTkLabel(fila, text=it["texto"], anchor="w", justify="left", wraplength=290).pack(
                side="left", fill="x", expand=True)
            ctk.CTkButton(fila, text="✖", width=30, fg_color="#7a2020",
                          command=lambda i=idx: self.borrar(i)).pack(side="right", padx=6, pady=4)

    def anadir(self):
        texto = self.entrada.get().strip()
        if texto:
            agregar_agenda(ARCHIVO_AGENDA, texto, datetime.datetime.now())
            self.entrada.delete(0, "end")
            self.refrescar()

    def borrar(self, idx):
        items = leer_agenda(ARCHIVO_AGENDA)
        if 0 <= idx < len(items):
            del items[idx]
            guardar_agenda(ARCHIVO_AGENDA, items)
        self.refrescar()


class FilaAccion(ctk.CTkFrame):
    def __init__(self, master, quitar_cb, accion=None):
        super().__init__(master)
        self.menu = ctk.CTkOptionMenu(self, values=list(TIPOS_ACCION), width=190, command=self.cambiar_tipo)
        self.menu.grid(row=0, column=0, padx=3, pady=3)
        self.e1 = ctk.CTkEntry(self, width=260)
        self.e1.grid(row=0, column=1, padx=3)
        self.b_arch = ctk.CTkButton(self, text="📄", width=30, command=lambda: self.elegir(self.e1, "archivo"))
        self.b_arch.grid(row=0, column=2, padx=1)
        self.b_carp = ctk.CTkButton(self, text="📁", width=30, command=lambda: self.elegir(self.e1, "carpeta"))
        self.b_carp.grid(row=0, column=3, padx=1)
        self.e2 = ctk.CTkEntry(self, width=190)
        self.e2.grid(row=0, column=4, padx=3)
        self.b_dest = ctk.CTkButton(self, text="📁", width=30, command=lambda: self.elegir(self.e2, "carpeta"))
        self.b_dest.grid(row=0, column=5, padx=1)
        ctk.CTkButton(self, text="✖", width=30, fg_color="#7a2020",
                      command=lambda: quitar_cb(self)).grid(row=0, column=6, padx=3)
        if accion:
            self.menu.set(ETIQUETA_DE_TIPO.get(accion.get("tipo"), "Abrir aplicación"))
            self.e1.insert(0, accion.get("valor", ""))
            self.e2.insert(0, accion.get("destino", ""))
        self.cambiar_tipo(self.menu.get())

    def cambiar_tipo(self, etiqueta):
        tipo, ayuda1, ayuda2 = TIPOS_ACCION[etiqueta]
        self.e1.configure(placeholder_text=ayuda1)
        if ayuda2:
            self.e2.configure(placeholder_text=ayuda2)
            self.e2.grid()
            self.b_dest.grid()
        else:
            self.e2.grid_remove()
            self.b_dest.grid_remove()
        if tipo in ("app", "archivo", "mover", "copiar", "eliminar"):
            self.b_arch.grid()
            self.b_carp.grid()
        else:
            self.b_arch.grid_remove()
            self.b_carp.grid_remove()

    def elegir(self, entrada, modo):
        if modo == "archivo":
            ruta = filedialog.askopenfilename(parent=self.winfo_toplevel())
        else:
            ruta = filedialog.askdirectory(parent=self.winfo_toplevel())
        if ruta:
            entrada.delete(0, "end")
            entrada.insert(0, os.path.normpath(ruta))

    def valores(self):
        tipo = TIPOS_ACCION[self.menu.get()][0]
        return {"tipo": tipo, "valor": self.e1.get().strip(),
                "destino": self.e2.get().strip() if TIPOS_ACCION[self.menu.get()][2] else ""}


class VentanaPersonalizados(ctk.CTkToplevel):
    def __init__(self, master, alfred):
        super().__init__(master)
        self.alfred, self.indice, self.filas = alfred, None, []
        self.title("Mis comandos")
        self.geometry("1060x640")
        izq = ctk.CTkFrame(self, width=230)
        izq.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(izq, text="Mis comandos", font=("Consolas", 14, "bold")).pack(pady=8)
        self.lista = ctk.CTkScrollableFrame(izq, width=200)
        self.lista.pack(fill="both", expand=True, padx=6)
        ctk.CTkButton(izq, text="➕ Nuevo comando", command=self.nuevo).pack(pady=10)

        der = ctk.CTkFrame(self, fg_color="transparent")
        der.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        ctk.CTkLabel(der, text=f"Cuando yo diga «{alfred.nombre} …»", anchor="w").pack(fill="x")
        self.e_frase = ctk.CTkEntry(der, placeholder_text="ej. modo cine")
        self.e_frase.pack(fill="x", pady=(2, 8))
        ctk.CTkLabel(der, text="Alfred responderá (opcional)", anchor="w").pack(fill="x")
        self.e_resp = ctk.CTkEntry(der, placeholder_text="ej. Que disfrute la función, señor")
        self.e_resp.pack(fill="x", pady=(2, 8))
        ctk.CTkLabel(der, text="y hará esto, en orden:", anchor="w").pack(fill="x")
        self.contenedor = ctk.CTkScrollableFrame(der, height=330)
        self.contenedor.pack(fill="both", expand=True, pady=(2, 8))
        barra = ctk.CTkFrame(der, fg_color="transparent")
        barra.pack(fill="x")
        ctk.CTkButton(barra, text="➕ Añadir acción", command=lambda: self.anadir_fila()).pack(side="left", padx=4)
        ctk.CTkButton(barra, text="▶ Probar", fg_color="#2b7a3d", command=self.probar).pack(side="left", padx=4)
        ctk.CTkButton(barra, text="💾 Guardar", command=self.guardar).pack(side="left", padx=4)
        ctk.CTkButton(barra, text="🗑 Borrar comando", fg_color="#7a2020", command=self.borrar).pack(side="right", padx=4)
        self.refrescar_lista()
        self.nuevo()
        traer_al_frente(self)

    def refrescar_lista(self):
        for w in self.lista.winfo_children():
            w.destroy()
        for i, c in enumerate(self.alfred.personalizados):
            ctk.CTkButton(self.lista, text=c["frase"], anchor="w", fg_color="#2a2a2a",
                          command=lambda i=i: self.cargar(i)).pack(fill="x", pady=2)

    def _vaciar_filas(self):
        for f in self.filas:
            f.destroy()
        self.filas = []

    def nuevo(self):
        self.indice = None
        self.e_frase.delete(0, "end")
        self.e_resp.delete(0, "end")
        self._vaciar_filas()
        self.anadir_fila()

    def cargar(self, i):
        c = self.alfred.personalizados[i]
        self.indice = i
        self.e_frase.delete(0, "end")
        self.e_frase.insert(0, c["frase"])
        self.e_resp.delete(0, "end")
        self.e_resp.insert(0, c.get("respuesta", ""))
        self._vaciar_filas()
        for a in c["acciones"]:
            self.anadir_fila(a)

    def anadir_fila(self, accion=None):
        fila = FilaAccion(self.contenedor, self.quitar_fila, accion)
        fila.pack(fill="x", pady=2)
        self.filas.append(fila)

    def quitar_fila(self, fila):
        fila.destroy()
        if fila in self.filas:
            self.filas.remove(fila)

    def _leer(self):
        frase = self.e_frase.get().strip()
        acciones = []
        for f in self.filas:
            v = f.valores()
            if v["valor"]:
                acciones.append(v)
        return {"frase": frase, "respuesta": self.e_resp.get().strip(), "acciones": acciones}

    def _validar(self, cmd):
        if not normalizar(cmd["frase"]):
            messagebox.showwarning("Mis comandos", "Escribe la frase que activará el comando.", parent=self)
            return False
        if not cmd["acciones"]:
            messagebox.showwarning("Mis comandos", "Añade al menos una acción con su campo lleno.", parent=self)
            return False
        for a in cmd["acciones"]:
            if a["tipo"] in ("mover", "copiar") and not a["destino"]:
                messagebox.showwarning("Mis comandos", "Falta la carpeta destino en una acción de mover/copiar.", parent=self)
                return False
        return True

    def guardar(self):
        cmd = self._leer()
        if not self._validar(cmd):
            return
        if any(a["tipo"] == "eliminar" for a in cmd["acciones"]):
            if not messagebox.askyesno("Eliminar archivos",
                                       "Este comando enviará archivos a la papelera cuando lo digas "
                                       "(Alfred pedirá confirmar con un «sí»). ¿Guardar?", parent=self):
                return
        if buscar_comando(normalizar(cmd["frase"])):
            messagebox.showinfo("Mis comandos", "Esa frase coincide con un comando integrado; "
                                "tu comando tendrá prioridad.", parent=self)
        if self.indice is None:
            self.alfred.personalizados.append(cmd)
            self.indice = len(self.alfred.personalizados) - 1
        else:
            self.alfred.personalizados[self.indice] = cmd
        self.alfred.guardar_personalizados()
        self.refrescar_lista()
        self.alfred.gui.log(f"💾 Comando guardado: «Alfred {cmd['frase']}»")

    def probar(self):
        cmd = self._leer()
        if not self._validar(cmd):
            return
        confirmado = False
        if any(a["tipo"] == "eliminar" for a in cmd["acciones"]):
            if not messagebox.askyesno("Probar", "Esta prueba ELIMINARÁ (a la papelera) los archivos indicados. ¿Continuar?",
                                       parent=self):
                return
            confirmado = True
        self.alfred.lanzar(self.alfred.ejecutar_personalizado, cmd, confirmado)

    def borrar(self):
        if self.indice is None:
            return
        if messagebox.askyesno("Borrar", "¿Borrar este comando?", parent=self):
            del self.alfred.personalizados[self.indice]
            self.alfred.guardar_personalizados()
            self.refrescar_lista()
            self.nuevo()


class PanelMenu(ctk.CTkFrame):
    """Todo lo que no hace falta tener a la vista en la ventana principal.
    Vive DENTRO de la ventana de Alfred (una tarjeta sobre un fondo oscuro) y no abre otra ventana: así la ventana
    principal no se minimiza, no cambia de tamaño (maximizada sigue maximizada) y no pierde el foco."""

    def __init__(self, ventana, gui, alfred, cfg):
        super().__init__(ventana, fg_color=PAL["bg2"], corner_radius=0)
        self.ventana, self.gui, self.alfred, self.cfg = ventana, gui, alfred, cfg
        self.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Button-1>", lambda e: self.cerrar())          # tocar el fondo oscuro cierra el menú
        tarjeta = ctk.CTkFrame(self, fg_color=PAL["card"], corner_radius=14, border_width=1, border_color=PAL["line"])
        tarjeta.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.95)
        cab = ctk.CTkFrame(tarjeta, fg_color="transparent")
        cab.pack(fill="x", padx=18, pady=(14, 0))
        ctk.CTkLabel(cab, text="☰  MENÚ", font=(F_TIT, 20), text_color=PAL["neon"]).pack(side="left")
        ctk.CTkButton(cab, text="✕", width=38, height=34, corner_radius=10, fg_color=PAL["card2"],
                      hover_color=PAL["hover"], font=("Segoe UI", 15), command=self.cerrar).pack(side="right")
        tabs = ctk.CTkTabview(tarjeta)
        tabs.pack(fill="both", expand=True, padx=10, pady=(6, 10))
        marcos = {}
        for nombre in ("General", "Voz", "Escucha", "Aplausos", "Remoto", "Mantenimiento"):
            tabs.add(nombre)
            marco = ctk.CTkScrollableFrame(tabs.tab(nombre), fg_color="transparent")
            marco.pack(fill="both", expand=True)
            marcos[nombre] = marco
        self._tab_general(marcos["General"])
        self._tab_voz(marcos["Voz"])
        self._tab_escucha(marcos["Escucha"])
        self._tab_aplausos(marcos["Aplausos"])
        self._tab_remoto(marcos["Remoto"])
        self._tab_mantenimiento(marcos["Mantenimiento"])
        ventana.bind("<Escape>", lambda e: self.cerrar())          # Esc también cierra el menú
        self.lift()

    def cerrar(self):
        self.cfg.guardar()
        try:
            self.ventana.unbind("<Escape>")
        except tk.TclError:
            pass
        self.gui.v_menu = None
        self.destroy()

    @staticmethod
    def _fila(padre, etiqueta, valor="", ayuda="", ancho=250):
        fila = ctk.CTkFrame(padre, fg_color="transparent")
        fila.pack(fill="x", padx=8, pady=4)
        ctk.CTkLabel(fila, text=etiqueta, width=168, anchor="w").pack(side="left")
        entrada = ctk.CTkEntry(fila, width=ancho, placeholder_text=ayuda or None)
        entrada.pack(side="left", padx=4)
        if valor:
            entrada.insert(0, str(valor))
        return entrada, fila

    @staticmethod
    def _nota(padre, texto):
        ctk.CTkLabel(padre, text=texto, text_color="#8a8a8a", wraplength=500, justify="left").pack(anchor="w", padx=12, pady=(2, 6))

    # ── General ──────────────────────────────────────────────────────────────
    def _tab_general(self, t):
        fila_ini = ctk.CTkFrame(t, fg_color="transparent")
        fila_ini.pack(fill="x", padx=12, pady=(12, 0))
        self.sw_inicio = ctk.CTkSwitch(fila_ini, text="Iniciar Alfred con Windows", command=self.toggle_inicio)
        self.sw_inicio.pack(side="left")
        ctk.CTkButton(fila_ini, text="🔧 Comprobar", width=112, height=28, command=self.reparar_inicio).pack(side="right")
        self.lbl_inicio = ctk.CTkLabel(t, text="", anchor="w", justify="left", wraplength=500, font=("Segoe UI", 11),
                                       text_color=PAL["muted"])
        self.lbl_inicio.pack(fill="x", padx=14, pady=(2, 8))
        self._pintar_inicio()
        self.campos = {}
        for clave, etiqueta, ayuda in (("ciudad", "Ciudad (para el clima)", "ej. Tuxtla Gutierrez"),
                                       ("navegador", "Navegador para páginas", "ej. Opera GX (vacío = predeterminado)"),
                                       ("youtube", "Página del modo trabajo", "https://…"),
                                       ("reproductor", "Reproductor de música", "ej. VLC, foobar2000 (vacío = el que detecte)"),
                                       ("carpetas_musica", "Carpetas de música", "ej. D:\\Musica; E:\\Albumes"),
                                       ("plataforma_musica", "Plataforma por defecto", "vacío = tu biblioteca · spotify · youtube music"),
                                       ("spotify_client_id", "Spotify Client ID", "opcional · developer.spotify.com (Premium)")):
            self.campos[clave], _ = self._fila(t, etiqueta, self.cfg.get(clave), ayuda)
        entrada, fila = self._fila(t, "Carpeta del proyecto (Cursor)", self.cfg.get("carpeta_proyecto"), "opcional", 205)
        ctk.CTkButton(fila, text="📁", width=34, command=lambda: self._elegir_carpeta(entrada)).pack(side="left")
        self.campos["carpeta_proyecto"] = entrada
        self._nota(t, "Spotify: crea una app gratis en developer.spotify.com/dashboard (API: Web API, Redirect URI: "
                      + SpotifyAPI.REDIRECT + "), pega aquí su Client ID, guarda y pulsa «Conectar Spotify». Requiere Premium.")
        ctk.CTkButton(t, text="🎧 Conectar Spotify", command=self.conectar_spotify).pack(pady=(4, 0))
        ctk.CTkButton(t, text="💾 Guardar", command=self.guardar_general).pack(pady=16)

    def conectar_spotify(self):
        self.guardar_general()
        sp = self.alfred.spotify
        if not sp.client_id():
            self.gui.log("⚠️ Primero pega tu Client ID de Spotify (developer.spotify.com/dashboard).")
            return

        def hilo():
            ok = sp.conectar(self.gui.log)
            self.gui.log("🎧 Spotify conectado: ya puedes decir «pon Numb en Spotify»." if ok
                         else "⚠️ No se pudo conectar Spotify.")
        threading.Thread(target=hilo, daemon=True).start()

    def _elegir_carpeta(self, entrada):
        ruta = filedialog.askdirectory(parent=self.winfo_toplevel())
        if ruta:
            entrada.delete(0, "end")
            entrada.insert(0, os.path.normpath(ruta))

    def guardar_general(self):
        for clave, entrada in self.campos.items():
            self.cfg.datos[clave] = entrada.get().strip()
        self.cfg.guardar()
        self.alfred._indice_musica = (0.0, [])          # vuelve a buscar las carpetas de música
        self.alfred._indice_canciones = (0.0, [])       # y las canciones
        self.gui.log("💾 Ajustes generales guardados.")

    def _pintar_inicio(self):
        est = estado_autostart()
        if est["registrado"]:
            self.sw_inicio.select()
        else:
            self.sw_inicio.deselect()
        if not est["registrado"]:
            txt, color = "Desactivado. Actívalo para que Alfred se abra solo, oculto en la bandeja, al iniciar sesión.", PAL["muted"]
        elif est["problema"]:
            txt, color = f"⚠ {est['problema']}. Pulsa «Comprobar» para repararlo.", PAL["warn"]
        else:
            txt, color = ("✓ Activo: al iniciar sesión Alfred se abre oculto en la bandeja al instante, espera por su cuenta "
                          "al micrófono de Windows, carga lo pesado después de empezar a escuchar y te avisa cuando ya "
                          "te oye."), PAL["ok"]
        self.lbl_inicio.configure(text=txt, text_color=color)

    def toggle_inicio(self):
        try:
            configurar_autostart(bool(self.sw_inicio.get()))
            est = estado_autostart()
            if self.sw_inicio.get():
                self.gui.log("🚀 Alfred iniciará con Windows." if not est["problema"] else f"⚠️ Inicio automático: {est['problema']}")
            else:
                self.gui.log("⏹️ Inicio automático desactivado.")
        except Exception as e:
            logging.exception("Inicio con Windows")
            self.gui.log(f"⚠️ Error en el registro: {e}")
        self._pintar_inicio()

    def reparar_inicio(self):
        try:
            limpiar_inicios_antiguos()
            configurar_autostart(True)
            self.gui.log("🚀 Inicio automático comprobado y reparado: " + comando_autostart())
        except Exception as e:
            logging.exception("Reparar inicio con Windows")
            self.gui.log(f"⚠️ No pude reparar el inicio automático: {e}")
        self._pintar_inicio()

    # ── Voz ──────────────────────────────────────────────────────────────────
    def _lista_micros(self):
        opciones = {"Predeterminado": None}
        try:
            apis = sd.query_hostapis()
            for i, d in enumerate(sd.query_devices()):
                if d["max_input_channels"] > 0:
                    opciones[f"{i}: {d['name']} ({apis[d['hostapi']]['name']})"] = i
        except Exception:
            logging.exception("No pude listar los micrófonos")
        return opciones

    def _tab_voz(self, t):
        self.e_wake, fila = self._fila(t, "Palabra de activación", self.cfg.get("palabra_activacion"),
                                       "ej. jarvis, yarvis", 185)
        ctk.CTkButton(fila, text="Guardar", width=72, command=self.guardar_wake).pack(side="left", padx=2)
        ctk.CTkButton(fila, text="👂", width=36, fg_color="#2b7a3d",
                      command=self.alfred.probar_activacion).pack(side="left")
        self._nota(t, "Varias separadas por coma (la primera es el nombre). 👂 prueba durante 15 s lo que Alfred entiende.")

        self.sw_en = ctk.CTkSwitch(t, text="🇬🇧 Entender también inglés (órdenes y títulos)", command=self.toggle_ingles)
        if self.cfg.get("idioma_en"):
            self.sw_en.select()
        self.sw_en.pack(anchor="w", padx=12, pady=(4, 2))
        self.sw_resp_en = ctk.CTkSwitch(t, text="Contestar en inglés cuando te oiga en inglés", command=self.toggle_resp_en)
        if self.cfg.get("responder_ingles") is not False:
            self.sw_resp_en.select()
        self.sw_resp_en.pack(anchor="w", padx=12, pady=2)
        self._nota(t, "Alfred oye en español y en inglés a la vez y se queda con la lectura que tiene sentido. "
                      "El motor de inglés pesa ~40 MB y se descarga con tu permiso; las respuestas en inglés usan la voz Kokoro.")

        self.lbl_vel = ctk.CTkLabel(t, text=f"Velocidad de la voz: {int(self.cfg.get('velocidad_voz'))}")
        self.lbl_vel.pack(anchor="w", padx=12, pady=(8, 0))
        sl = ctk.CTkSlider(t, from_=120, to=260, number_of_steps=14, command=self.cambiar_velocidad)
        sl.set(int(self.cfg.get("velocidad_voz")))
        sl.pack(fill="x", padx=12)

        ctk.CTkLabel(t, text="🧠 Voz con inteligencia artificial (offline, gratis, sin límites)",
                     font=("Segoe UI Semibold", 13)).pack(anchor="w", padx=12, pady=(14, 2))
        self.sw_ia = ctk.CTkSwitch(t, text="Usar la voz con IA (Kokoro / Piper)", command=self.toggle_voz_ia)
        if self.cfg.get("voz_ia"):
            self.sw_ia.select()
        self.sw_ia.pack(anchor="w", padx=12, pady=4)
        self.nombres_ia = {v["nombre"]: k for k, v in VOCES_IA.items()}
        actual_ia = VOCES_IA.get(self.cfg.get("voz_ia_modelo"), VOCES_IA[VOZ_IA_PREDETERMINADA])["nombre"]
        self.menu_ia = ctk.CTkOptionMenu(t, values=list(self.nombres_ia), command=self.cambiar_voz_ia, width=400)
        self.menu_ia.set(actual_ia)
        self.menu_ia.pack(anchor="w", padx=12)
        self.lbl_ia = ctk.CTkLabel(t, text="", text_color=PAL["muted"])
        self.lbl_ia.pack(anchor="w", padx=12, pady=(2, 0))
        self._estado_ia()
        self.sw_resid = ctk.CTkSwitch(t, text="Mantener Kokoro cargado (sin esperas; usa ~300 MB de RAM)", command=self.toggle_residente)
        if self.cfg.get("kokoro_residente") is not False:
            self.sw_resid.select()
        self.sw_resid.pack(anchor="w", padx=12, pady=(8, 2))
        self.sw_prever = ctk.CTkSwitch(t, text="Preparar la hora y la fecha por adelantado (suenan al instante)",
                                       command=self.toggle_prever)
        if self.cfg.get("kokoro_prever") is not False:
            self.sw_prever.select()
        self.sw_prever.pack(anchor="w", padx=12, pady=2)
        self.sw_ligero = ctk.CTkSwitch(t, text="⚡ Kokoro ligero: responde más rápido (88 MB, voz algo menos fiel)", command=self.toggle_ligero)
        if self.cfg.get("kokoro_ligero"):
            self.sw_ligero.select()
        self.sw_ligero.pack(anchor="w", padx=12, pady=2)

        ctk.CTkLabel(t, text="Voz de Windows (respaldo)").pack(anchor="w", padx=12, pady=(10, 0))
        voces = ["Automática (español)"] + list(self.alfred.voz.voces)
        pref = (self.cfg.get("voz_preferida") or "").lower()
        actual = next((v for v in self.alfred.voz.voces if pref and pref in v.lower()), voces[0])
        self.menu_voz = ctk.CTkOptionMenu(t, values=voces, command=self.cambiar_voz, width=400)
        self.menu_voz.set(actual)
        self.menu_voz.pack(anchor="w", padx=12)
        ctk.CTkButton(t, text="🔊 Probar voz", command=self.probar_voz).pack(anchor="w", padx=12, pady=8)

        ctk.CTkLabel(t, text="Micrófono").pack(anchor="w", padx=12, pady=(6, 0))
        self.micros = self._lista_micros()
        actual_mic = next((k for k, v in self.micros.items() if v == self.cfg.get("microfono")), "Predeterminado")
        self.menu_mic = ctk.CTkOptionMenu(t, values=list(self.micros), command=self.cambiar_micro, width=400)
        self.menu_mic.set(actual_mic)
        self.menu_mic.pack(anchor="w", padx=12)

        self.lbl_ganancia = ctk.CTkLabel(t, text=self._texto_ganancia(float(self.cfg.get("ganancia_mic") or 8)))
        self.lbl_ganancia.pack(anchor="w", padx=12, pady=(10, 0))
        sl_g = ctk.CTkSlider(t, from_=1, to=20, number_of_steps=19, command=self.cambiar_ganancia)
        sl_g.set(float(self.cfg.get("ganancia_mic") or 8))
        sl_g.pack(fill="x", padx=12)
        self._nota(t, "Amplifica tu voz automáticamente: más alto = te oye aunque hables bajito. "
                      "Si se activa con ruido o se equivoca más, bájalo. 1 = sin amplificar.")

        self.lbl_espera = ctk.CTkLabel(t, text=f"Tiempo para dar la orden tras decir solo la palabra: {int(self.cfg.get('ventana_espera'))} s")
        self.lbl_espera.pack(anchor="w", padx=12, pady=(14, 0))
        sl2 = ctk.CTkSlider(t, from_=3, to=15, number_of_steps=12, command=self.cambiar_espera)
        sl2.set(int(self.cfg.get("ventana_espera")))
        sl2.pack(fill="x", padx=12)

    def _estado_ia(self):
        try:
            ok = self.alfred.voz.motor_ia().instalado()
            self.lbl_ia.configure(text="✅ Instalada y lista" if ok else
                                  "⬇ Aún no instalada: se descarga con tu permiso al activarla")
        except Exception:
            pass

    def _instalar_ia(self):
        def trabajo():
            self.alfred.instalar_voz_ia(True)
            self.gui.ui(self._estado_ia)
        threading.Thread(target=trabajo, daemon=True).start()

    def toggle_voz_ia(self):
        self.cfg.set("voz_ia", bool(self.sw_ia.get()))
        self.alfred.voz.reactivar_ia()
        if self.sw_ia.get() and not self.alfred.voz.motor_ia().instalado():
            self._instalar_ia()
        self._estado_ia()

    def cambiar_voz_ia(self, valor):
        self.cfg.set("voz_ia_modelo", self.nombres_ia[valor])
        self.alfred.voz.reactivar_ia()
        if not self.alfred.voz.motor_ia().instalado():
            self.sw_ia.select()
            self.cfg.set("voz_ia", True)
            self._instalar_ia()
        else:
            self.alfred.voz.decir("Hola, señor. Esta es mi nueva voz.")
        self._estado_ia()

    def toggle_ingles(self):
        activo = bool(self.sw_en.get())
        self.cfg.set("idioma_en", activo)
        if activo:
            threading.Thread(target=self.alfred._preparar_ingles, args=(True,), daemon=True).start()
        else:
            self.alfred.rec_en = None
            self.gui.log("🇬🇧 Inglés desactivado: Alfred solo escucha español.")

    def toggle_resp_en(self):
        self.cfg.set("responder_ingles", bool(self.sw_resp_en.get()))

    def toggle_residente(self):
        self.cfg.set("kokoro_residente", bool(self.sw_resid.get()))
        if self.sw_resid.get():
            threading.Thread(target=self.alfred.voz._precalentar_kokoro, daemon=True).start()

    def toggle_prever(self):
        self.cfg.set("kokoro_prever", bool(self.sw_prever.get()))

    def toggle_ligero(self):
        if self.sw_ligero.get():
            def trabajo():
                if not self.alfred.instalar_kokoro_ligero():
                    self.gui.ui(self.sw_ligero.deselect)          # dijiste que no (o falló): el interruptor vuelve atrás
            threading.Thread(target=trabajo, daemon=True).start()
        else:
            self.cfg.set("kokoro_ligero", False)
            self.alfred.voz.reactivar_ia()

    def guardar_wake(self):
        error = self.alfred.cambiar_activacion(self.e_wake.get())
        if error:
            messagebox.showwarning("Palabra de activación", error, parent=self.winfo_toplevel())
        else:
            self.e_wake.delete(0, "end")
            self.e_wake.insert(0, self.cfg.get("palabra_activacion"))

    def cambiar_velocidad(self, v):
        self.cfg.datos["velocidad_voz"] = int(v)
        self.lbl_vel.configure(text=f"Velocidad de la voz: {int(v)}")

    def cambiar_espera(self, v):
        self.cfg.datos["ventana_espera"] = int(v)
        self.lbl_espera.configure(text=f"Tiempo para dar la orden tras decir solo la palabra: {int(v)} s")

    def cambiar_voz(self, valor):
        self.cfg.set("voz_preferida", "" if valor.startswith("Automática") else valor.lower())
        self.gui.log(f"🔊 Voz elegida: {valor}")

    def probar_voz(self):
        self.cfg.guardar()
        self.alfred.voz.decir("Hola, señor. La voz funciona correctamente.")

    @staticmethod
    def _texto_ganancia(v):
        return "Sensibilidad del micrófono: sin amplificar" if v <= 1 else f"Sensibilidad del micrófono: hasta ×{int(v)}"

    def cambiar_ganancia(self, v):
        v = int(round(float(v)))
        self.cfg.datos["ganancia_mic"] = v
        self.alfred.amp.ganancia_max = max(1.0, float(v))
        self.lbl_ganancia.configure(text=self._texto_ganancia(v))

    def cambiar_micro(self, valor):
        self.cfg.set("microfono", self.micros.get(valor))
        self.alfred.reabrir_micro()
        self.gui.log(f"🎙️ Micrófono: {valor}")

    # ── Escucha (2.9) ────────────────────────────────────────────────────────
    def _tab_escucha(self, t):
        ctk.CTkLabel(t, text="🎧 Oír mejor y gastar menos", font=("Segoe UI Semibold", 13)).pack(anchor="w", padx=12, pady=(12, 2))
        self.sw_puerta = ctk.CTkSwitch(t, text="Puerta de voz: el reconocedor solo trabaja cuando hablas", command=self.toggle_puerta)
        if self.cfg.get("puerta_voz") is not False:
            self.sw_puerta.select()
        self.sw_puerta.pack(anchor="w", padx=12, pady=4)
        self._nota(t, "Gasta mucha menos CPU en reposo y cierra bien cada frase aunque haya ruido de fondo continuo. "
                      "Si notas que se come el inicio de tus palabras, apágala.")
        self.sw_grande = ctk.CTkSwitch(t, text="🎯 Modelo de alta precisión en español (~1.4 GB)", command=self.toggle_grande)
        if self.cfg.get("modelo_alta_precision"):
            self.sw_grande.select()
        self.sw_grande.pack(anchor="w", padx=12, pady=(10, 2))
        gb = memoria_total_gb()
        self._nota(t, "Entiende bastante mejor el español, pero usa mucha más memoria y tarda más en cargar"
                      + (f" (este equipo tiene {gb:.0f} GB de RAM)." if gb else ".")
                      + " Se descarga con tu permiso. Si no carga, Alfred vuelve solo al modelo normal.")

        ctk.CTkLabel(t, text="🔐 Reconocer mi voz", font=("Segoe UI Semibold", 13)).pack(anchor="w", padx=12, pady=(16, 2))
        self.sw_solo = ctk.CTkSwitch(t, text="Obedecer solo a mi voz", command=self.toggle_solo_voz)
        self.sw_solo.pack(anchor="w", padx=12, pady=4)
        self.lbl_huella = ctk.CTkLabel(t, text="", text_color=PAL["muted"])
        self.lbl_huella.pack(anchor="w", padx=12)
        fila = ctk.CTkFrame(t, fg_color="transparent")
        fila.pack(anchor="w", padx=8, pady=6)
        ctk.CTkButton(fila, text="🎙️ Registrar mi voz (5 frases)", command=self.registrar_voz).pack(side="left", padx=4)
        ctk.CTkButton(fila, text="🗑 Borrar", width=80, fg_color="#7a2020", command=self.borrar_voz).pack(side="left", padx=4)
        self.lbl_umbral_voz = ctk.CTkLabel(t, text="")
        self.lbl_umbral_voz.pack(anchor="w", padx=12, pady=(8, 0))
        sl = ctk.CTkSlider(t, from_=0.25, to=0.70, number_of_steps=45, command=self.cambiar_umbral_voz)
        sl.set(float(self.cfg.get("huella_umbral") or 0.45))
        sl.pack(fill="x", padx=12)
        self._nota(t, "Menor = más exigente (rechaza más voces, pero a veces también la tuya); mayor = más permisivo. "
                      "En el registro (actividad) cada orden muestra su «distancia»: ajusta el valor un poco por encima de la tuya. "
                      "Solo se comprueba la voz en las órdenes dirigidas a Alfred. Necesita un modelo de ~13 MB (con tu permiso).")
        self._estado_huella()
        self.cambiar_umbral_voz(sl.get())

        ctk.CTkLabel(t, text="🧠 Entender mejor las órdenes", font=("Segoe UI Semibold", 13)).pack(anchor="w", padx=12, pady=(16, 2))
        self.sw_sem = ctk.CTkSwitch(t, text="Comprensión semántica (entiende otras palabras)", command=self.toggle_sem)
        if self.cfg.get("comprension_semantica"):
            self.sw_sem.select()
        self.sw_sem.pack(anchor="w", padx=12, pady=4)
        self.lbl_sem = ctk.CTkLabel(t, text="")
        self.lbl_sem.pack(anchor="w", padx=12, pady=(6, 0))
        sl2 = ctk.CTkSlider(t, from_=0.60, to=0.90, number_of_steps=15, command=self.cambiar_umbral_sem)
        sl2.set(float(self.cfg.get("semantica_umbral") or 0.74))
        sl2.pack(fill="x", padx=12)
        self._nota(t, "Solo actúa cuando ninguna frase exacta coincide: «no se escucha nada» → sube el volumen. Mayor = más prudente "
                      "(prefiere decir «no tengo ese comando» a equivocarse). Instala «fastembed» y descarga ~220 MB, con tu permiso.")
        self.cambiar_umbral_sem(sl2.get())

    def toggle_puerta(self):
        self.cfg.set("puerta_voz", bool(self.sw_puerta.get()))
        self.alfred.puerta.reiniciar()

    def toggle_grande(self):
        if self.sw_grande.get():
            def trabajo():
                if not self.alfred.activar_modelo_grande():
                    self.gui.ui(self.sw_grande.deselect)          # dijiste que no (o falló): el interruptor vuelve atrás
            threading.Thread(target=trabajo, daemon=True).start()
        else:
            threading.Thread(target=self.alfred.desactivar_modelo_grande, daemon=True).start()

    def _estado_huella(self):
        try:
            n = int(self.cfg.get("huella_muestras") or 0)
            hay = bool(self.cfg.get("huella_voz"))
            self.lbl_huella.configure(text=f"✅ Voz registrada ({n} frases)" if hay else "Aún no has registrado tu voz")
            if hay and self.cfg.get("solo_mi_voz"):
                self.sw_solo.select()
            else:
                self.sw_solo.deselect()
        except tk.TclError:
            pass

    def registrar_voz(self):
        def trabajo():
            self.alfred.registrar_voz()
            self.gui.ui(self._estado_huella)
        threading.Thread(target=trabajo, daemon=True).start()

    def borrar_voz(self):
        self.alfred.olvidar_voz()
        self._estado_huella()

    def toggle_solo_voz(self):
        if self.sw_solo.get() and not self.cfg.get("huella_voz"):
            self.sw_solo.deselect()
            self.gui.log("ℹ️ Primero registra tu voz con el botón «Registrar mi voz».")
            return
        self.cfg.set("solo_mi_voz", bool(self.sw_solo.get()))
        self.gui.log("🔐 Alfred solo obedecerá a tu voz." if self.sw_solo.get() else "🔓 Alfred obedecerá a cualquier voz.")

    def cambiar_umbral_voz(self, v):
        v = round(float(v), 2)
        self.cfg.datos["huella_umbral"] = v
        self.lbl_umbral_voz.configure(text=f"Exigencia de la voz: distancia máxima {v:.2f}   · menor = más exigente")

    def toggle_sem(self):
        if self.sw_sem.get():
            def trabajo():
                if not self.alfred.preparar_semantica(True):
                    self.gui.ui(self.sw_sem.deselect)
            threading.Thread(target=trabajo, daemon=True).start()
        else:
            self.cfg.set("comprension_semantica", False)
            self.alfred.semantica = None

    def cambiar_umbral_sem(self, v):
        v = round(float(v), 2)
        self.cfg.datos["semantica_umbral"] = v
        self.lbl_sem.configure(text=f"Parecido mínimo para entender: {v:.2f}   · mayor = más prudente")

    # ── Aplausos ─────────────────────────────────────────────────────────────
    def _tab_aplausos(self, t):
        self._nota(t, "Aplaude dos veces seguidas para recibir la bienvenida (Cursor + YouTube). "
                      "Si no responde o se activa solo, calibra o ajusta la sensibilidad.")
        self.sw_clap = ctk.CTkSwitch(t, text="👏 Activar el doble aplauso", command=self.toggle_clap)
        self.sw_clap.pack(anchor="w", padx=12, pady=8)
        if self.cfg.get("clap_activo"):
            self.sw_clap.select()
        ctk.CTkButton(t, text="🎚️ Calibrar aplausos",
                      command=lambda: self.alfred.lanzar(self.alfred.calibrar_aplausos)).pack(anchor="w", padx=12, pady=8)
        self.lbl_umbral = ctk.CTkLabel(t, text=f"Sensibilidad (umbral): {float(self.cfg.get('aplauso_umbral')):.2f}   · menor = más sensible")
        self.lbl_umbral.pack(anchor="w", padx=12, pady=(12, 0))
        sl = ctk.CTkSlider(t, from_=0.03, to=0.5, number_of_steps=47, command=self.cambiar_umbral)
        sl.set(float(self.cfg.get("aplauso_umbral")))
        sl.pack(fill="x", padx=12)

    def toggle_clap(self):
        activo = bool(self.sw_clap.get())
        self.cfg.set("clap_activo", activo)
        self.gui.log("👏 Doble aplauso " + ("activado." if activo else "desactivado."))

    def cambiar_umbral(self, v):
        v = round(float(v), 3)
        self.cfg.datos["aplauso_umbral"] = v
        self.alfred.detector.umbral = v
        self.lbl_umbral.configure(text=f"Sensibilidad (umbral): {v:.2f}   · menor = más sensible")

    # ── Mantenimiento ────────────────────────────────────────────────────────
    # ── Remoto ───────────────────────────────────────────────────────────────
    def _tab_remoto(self, t):
        ctk.CTkLabel(t, text="📱 Controlar Alfred desde el móvil u otro dispositivo",
                     font=("Segoe UI Semibold", 13)).pack(anchor="w", padx=12, pady=(12, 2))
        self._nota(t, "Abre una página web (y una API) en este PC. Desde el móvil abres el enlace en el navegador y "
                      "controlas Alfred: escribes órdenes y ves lo que responde. Es la base para una app móvil.")
        self.sw_remoto = ctk.CTkSwitch(t, text="Activar el control remoto", command=self.toggle_remoto)
        if self.cfg.get("remoto_activo"):
            self.sw_remoto.select()
        self.sw_remoto.pack(anchor="w", padx=12, pady=(4, 2))
        self.sw_lan = ctk.CTkSwitch(t, text="Permitir otros dispositivos de mi red Wi-Fi", command=self.toggle_remoto)
        if self.cfg.get("remoto_lan"):
            self.sw_lan.select()
        self.sw_lan.pack(anchor="w", padx=12, pady=2)
        self.lbl_remoto = ctk.CTkLabel(t, text="", anchor="w", justify="left", wraplength=500, font=("Segoe UI", 11),
                                       text_color=PAL["muted"])
        self.lbl_remoto.pack(fill="x", padx=14, pady=(6, 4))
        self.e_remoto = ctk.CTkEntry(t, width=480, placeholder_text="El enlace aparece al activarlo")
        self.e_remoto.pack(anchor="w", padx=12, pady=4)
        fila = ctk.CTkFrame(t, fg_color="transparent")
        fila.pack(fill="x", padx=8, pady=2)
        ctk.CTkButton(fila, text="📋 Copiar enlace", width=130, command=self.copiar_enlace_remoto).pack(side="left", padx=4)
        ctk.CTkButton(fila, text="🔑 Clave nueva", width=120, command=self.clave_nueva_remoto).pack(side="left", padx=4)
        self._nota(t, "El enlace lleva tu clave: quien lo tenga controla el PC, así que no lo compartas. Con «red» apagado "
                      "solo funciona en este mismo PC; con «red» encendido acepta únicamente direcciones privadas (Wi-Fi de "
                      "casa, Tailscale), nunca de internet. La conexión no va cifrada (http): úsalo en tu Wi-Fi de confianza. "
                      "La primera vez Windows puede preguntar por el Firewall: permite solo «Redes privadas».")
        self._pintar_remoto()

    def _pintar_remoto(self):
        try:
            r = self.alfred.remoto
            dirs = r.direcciones()
            if not self.cfg.get("remoto_activo"):
                txt, color = "Desactivado.", PAL["muted"]
            elif not r.activo():
                txt, color = "⚠ No pude abrir el puerto (¿otro programa lo usa?). Mira alfred.log.", PAL["warn"]
            else:
                txt = (f"✓ Activo en el puerto {r.puerto}" + (" · visible en tu red Wi-Fi." if self.cfg.get("remoto_lan")
                                                               else " · solo este PC (para probar). Activa «red» para el móvil."))
                color = PAL["ok"]
            self.lbl_remoto.configure(text=txt, text_color=color)
            self.e_remoto.configure(state="normal")
            self.e_remoto.delete(0, "end")
            if dirs:
                self.e_remoto.insert(0, dirs[0])
            self.e_remoto.configure(state="readonly")
        except tk.TclError:
            pass                                             # el menú se cerró mientras tanto

    def toggle_remoto(self):
        self.cfg.set("remoto_activo", bool(self.sw_remoto.get()))
        self.cfg.set("remoto_lan", bool(self.sw_lan.get()))

        def aplicar():
            self.alfred.remoto.aplicar_config()
            self.gui.ui(self._pintar_remoto)
        threading.Thread(target=aplicar, daemon=True).start()

    def copiar_enlace_remoto(self):
        dirs = self.alfred.remoto.direcciones()
        if dirs:
            self.clipboard_clear()
            self.clipboard_append(dirs[0])
            self.gui.log("📋 Enlace del control remoto copiado.")
        else:
            self.gui.log("ℹ️ Activa el control remoto para obtener el enlace.")

    def clave_nueva_remoto(self):
        self.alfred.remoto.nueva_clave()
        self._pintar_remoto()

    def _tab_mantenimiento(self, t):
        ctk.CTkLabel(t, text=f"{self.gui.nombre_os()}  ·  versión {VERSION}",
                     font=("Consolas", 13, "bold")).pack(anchor="w", padx=12, pady=(12, 0))
        ctk.CTkLabel(t, text=f"Python {sys.version.split()[0]}", font=("Consolas", 12),
                     text_color="#8a8a8a").pack(anchor="w", padx=12, pady=(0, 8))
        for texto, accion in (
            ("🔍 Verificar componentes de Python (instala los que falten, con tu permiso)", self.gui.verificar_componentes),
            ("⬇ Descargar o reinstalar el motor de voz (con tu permiso)", self.alfred.pedir_modelo),
            ("🇬🇧 Descargar o reparar el motor de voz en inglés (con tu permiso)",
             lambda: threading.Thread(target=self.alfred._preparar_ingles, args=(True,), daemon=True).start()),
            ("🧠 Descargar o reparar la voz con IA (con tu permiso)",
             lambda: threading.Thread(target=self.alfred.instalar_voz_ia, args=(True,), daemon=True).start()),
            ("🧭 Volver a buscar mis aplicaciones", lambda: self.alfred.lanzar(self.alfred.volver_a_buscar_apps)),
            ("📂 Abrir la carpeta de Alfred", lambda: os.startfile(BASE_DIR)),
            ("📜 Ver el registro (alfred.log)", self.abrir_registro),
            ("🔄 Reiniciar Alfred", self.gui.reiniciar),
        ):
            ctk.CTkButton(t, text=texto, anchor="w", command=accion).pack(fill="x", padx=12, pady=4)
        self._nota(t, "Los datos (config, agenda, comandos propios y registro) viven en la carpeta de Alfred.")

    def abrir_registro(self):
        ruta = os.path.join(BASE_DIR, "alfred.log")
        if os.path.exists(ruta):
            os.startfile(ruta)
        else:
            self.gui.log("Todavía no hay registro.")


class AlfredGUI(ctk.CTk):
    def __init__(self, cfg):
        super().__init__()
        elegir_fuentes()
        self.cfg, self.alfred, self.tray, self.candado = cfg, None, None, None
        self._tray_listo = threading.Event()
        self.v_ayuda = self.v_agenda = self.v_personal = self.v_menu = None
        self.cola_ui = queue.Queue()
        self._orb_color, self._orb_fase, self._orb_vel, self._tok_prog = PAL["warn"], 0.0, 0.10, 0
        self._acento = None
        self.title(f"{nombre_desde_cfg(cfg)} OS")
        self.geometry("720x780")
        self.minsize(600, 660)
        self.configure(fg_color=PAL["bg"])

        # ── cabecera: indicador HUD + nombre + accesos rápidos
        cab = ctk.CTkFrame(self, fg_color="transparent")
        cab.pack(fill="x", padx=22, pady=(18, 4))
        self.orb = tk.Canvas(cab, width=64, height=64, bg=PAL["bg"], highlightthickness=0)
        self.orb.pack(side="left")
        tit = ctk.CTkFrame(cab, fg_color="transparent")
        tit.pack(side="left", padx=14)
        self.lbl_nombre = ctk.CTkLabel(tit, text=f"{nombre_desde_cfg(cfg)} OS", font=(F_TIT, 30), text_color=PAL["text"])
        self.lbl_nombre.pack(anchor="w")
        ctk.CTkLabel(tit, text=f"ASISTENTE DE VOZ  ·  OFFLINE  ·  v{VERSION}", font=(F_TIT.replace(" SemiBold", ""), 10),
                     text_color=PAL["neon"]).pack(anchor="w")
        for texto, accion in (("☰", self.mostrar_menu), ("⬇", self.ocultar)):
            ctk.CTkButton(cab, text=texto, width=42, height=42, corner_radius=10, fg_color=PAL["card"],
                          hover_color=PAL["hover"], border_width=1, border_color=PAL["line"], text_color=PAL["acc_luz"],
                          font=("Segoe UI", 17), command=accion).pack(side="right", padx=(8, 0))
        self.linea = tk.Canvas(self, height=2, bg=PAL["bg"], highlightthickness=0)
        self.linea.pack(fill="x", padx=22, pady=(6, 8))
        self.linea.bind("<Configure>", self._dibujar_linea)

        # ── estado: barra de color a la izquierda + texto
        est = ctk.CTkFrame(self, fg_color=PAL["card"], corner_radius=12, border_width=1, border_color=PAL["line"])
        est.pack(fill="x", padx=22, pady=8)
        self._acento = ctk.CTkFrame(est, width=4, height=10, corner_radius=2, fg_color=PAL["warn"])
        self._acento.pack(side="left", fill="y", padx=(12, 0), pady=12)
        cuerpo = ctk.CTkFrame(est, fg_color="transparent")
        cuerpo.pack(side="left", fill="both", expand=True)
        self.label_estado = ctk.CTkLabel(cuerpo, text="Iniciando…", font=(F_TIT, 17), anchor="w", text_color=PAL["text"])
        self.label_estado.pack(fill="x", padx=14, pady=(14, 0))
        self.label_hint = ctk.CTkLabel(cuerpo, text="", font=("Segoe UI", 12), anchor="w", text_color=PAL["muted"])
        self.label_hint.pack(fill="x", padx=14, pady=(0, 14))

        # ── progreso (solo aparece mientras se descarga o instala algo)
        self.tarjeta_prog = ctk.CTkFrame(self, fg_color=PAL["card"], corner_radius=12, border_width=1,
                                         border_color=PAL["line"])
        self.lbl_prog = ctk.CTkLabel(self.tarjeta_prog, text="", font=("Segoe UI Semibold", 13), anchor="w",
                                     text_color=PAL["text"])
        self.lbl_prog.pack(fill="x", padx=18, pady=(12, 6))
        self.barra = BarraAnimada(self.tarjeta_prog, alto=12, bg=PAL["card"])
        self.barra.pack(fill="x", padx=18, pady=(0, 16))

        # ── actividad: columnas hora | icono | mensaje, con colores y filtros
        self.tarjeta_feed = ctk.CTkFrame(self, fg_color=PAL["card"], corner_radius=12, border_width=1,
                                         border_color=PAL["line"])
        self.tarjeta_feed.pack(fill="both", expand=True, padx=22, pady=8)
        top = ctk.CTkFrame(self.tarjeta_feed, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(12, 6))
        ctk.CTkLabel(top, text="ACTIVIDAD", font=(F_TIT, 12), text_color=PAL["neon"]).pack(side="left")
        ctk.CTkButton(top, text="Limpiar", width=70, height=28, corner_radius=8, fg_color=PAL["card2"],
                      hover_color=PAL["hover"], font=("Segoe UI", 12), command=self.limpiar).pack(side="right")
        self.filtro = ctk.CTkSegmentedButton(top, values=["Todo", "Órdenes", "Avisos"], command=self.filtrar, height=28,
                                             font=("Segoe UI", 12), selected_color=PAL["acc"],
                                             unselected_color=PAL["card2"], fg_color=PAL["card2"])
        self.filtro.set("Todo")
        self.filtro.pack(side="right", padx=10)
        self.console = ctk.CTkTextbox(self.tarjeta_feed, fg_color=PAL["bg2"], text_color=PAL["text"],
                                      font=("Segoe UI", 12), corner_radius=8, border_width=1, border_color=PAL["line"],
                                      wrap="word")
        self.console.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self._config_tags()

        # ── accesos
        base = ctk.CTkFrame(self, fg_color="transparent")
        base.pack(fill="x", padx=22, pady=(4, 20))
        for i, (texto, accion) in enumerate((("◈  Comandos", self.mostrar_ayuda),
                                             ("✦  Mis comandos", self.mostrar_personalizados),
                                             ("◷  Agenda", self.mostrar_agenda))):
            base.grid_columnconfigure(i, weight=1, uniform="b")
            ctk.CTkButton(base, text=texto, height=44, corner_radius=10, fg_color=PAL["card"], hover_color=PAL["hover"],
                          border_width=1, border_color=PAL["line"], text_color=PAL["acc_luz"], font=(F_TIT, 13),
                          command=accion).grid(row=0, column=i, padx=5, sticky="ew")

        self.protocol("WM_DELETE_WINDOW", self.ocultar)
        self._iniciar_bandeja()
        self.after(50, self._drenar)
        self.after(100, self._animar_orb)
        if "--oculto" in sys.argv:
            self.withdraw()

    def _dibujar_linea(self, e):
        """Filete bajo la cabecera: del cian al fondo (decorativo, se redibuja solo al cambiar de tamaño)."""
        try:
            self.linea.delete("all")
            n, w = 48, max(e.width, 10)
            for i in range(n):
                self.linea.create_rectangle(w * i / n, 0, w * (i + 1) / n + 1, 2, outline="",
                                            fill=mezclar(PAL["neon"], PAL["bg"], (i / n) ** 0.7))
        except tk.TclError:
            pass

    def avisar_bandeja(self, titulo, texto):
        """Globo de aviso junto al reloj (Alfred arrancó oculto con Windows y así sabes que ya escucha). Espera, sin
        bloquear la ventana, a que el icono exista: al iniciar sesión la barra de tareas tarda en aparecer."""
        def _avisar():
            try:
                if self.tray and self._tray_listo.wait(180):
                    self.tray.notify(texto, titulo)
            except Exception:
                logging.exception("Aviso de bandeja")
        threading.Thread(target=_avisar, daemon=True).start()

    # ── actividad ────────────────────────────────────────────────────────────
    def _config_tags(self):
        tw = self.console._textbox

        def tag(nombre, **kw):
            try:
                tw.tag_configure(nombre, **kw)
            except Exception:
                logging.exception("No pude aplicar el estilo %s", nombre)
        tag("fila", tabs=("62p", "86p"), lmargin1=8, lmargin2="86p", spacing1=3, spacing3=3)
        tag("ts", foreground=PAL["muted"], font=("Consolas", 10))
        tag("ico", font=("Segoe UI Emoji", 11))
        for nombre, color, negrita in (("orden", PAL["acc_luz"], True), ("respuesta", "#6ee7b7", False), ("ok", PAL["ok"], False),
                                       ("aviso", PAL["warn"], False), ("error", PAL["err"], False),
                                       ("sistema", "#9fb3c8", False)):
            tag("t_" + nombre, foreground=color, font=("Segoe UI Semibold" if negrita else "Segoe UI", 11))
        try:
            tw.bind("<Key>", lambda e: None if (e.state & 4) else "break")      # solo lectura (Ctrl+C sí funciona)
        except Exception:
            logging.exception("No pude poner la consola en solo lectura")

    _CATEGORIAS = (("🎤", "orden", "f_orden"), ("📱", "orden", "f_orden"), ("👂", "orden", "f_orden"), ("🗣", "respuesta", "f_orden"),
                   ("✅", "ok", "f_sistema"), ("⚠", "aviso", "f_aviso"), ("❓", "aviso", "f_aviso"),
                   ("❌", "error", "f_aviso"))

    def _log(self, ts, msj):
        msj = msj.strip()
        cat, filtro, icono, texto = "sistema", "f_sistema", "•", msj
        for emoji, c, f in self._CATEGORIAS:
            if msj.startswith(emoji):
                cat, filtro, icono = c, f, emoji
                texto = msj[len(emoji):].lstrip("\ufe0f ").strip()
                break
        else:
            if msj and not msj[0].isalnum() and msj[0] not in "«¿¡(":      # otro emoji inicial: se conserva como icono
                icono, texto = msj[0], msj[1:].lstrip("\ufe0f ").strip()
        tw = self.console._textbox
        tw.insert("end", ts, ("fila", filtro, "ts"))
        tw.insert("end", f"\t{icono}\t", ("fila", filtro, "ico"))
        tw.insert("end", texto + "\n", ("fila", filtro, "t_" + cat))
        if int(tw.index("end-1c").split(".")[0]) > 600:
            tw.delete("1.0", "120.0")
        tw.see("end")

    def filtrar(self, valor):
        tw = self.console._textbox
        tw.tag_configure("f_orden", elide=(valor == "Avisos"))
        tw.tag_configure("f_aviso", elide=(valor == "Órdenes"))
        tw.tag_configure("f_sistema", elide=(valor != "Todo"))
        tw.see("end")

    def limpiar(self):
        self.console._textbox.delete("1.0", "end")

    # ── hilo-seguro ──────────────────────────────────────────────────────────
    def ui(self, fn, *args):
        self.cola_ui.put((fn, args))

    def _drenar(self):
        try:
            while True:
                fn, args = self.cola_ui.get_nowait()
                try:
                    fn(*args)
                except Exception:
                    logging.exception("Error en la interfaz")
        except queue.Empty:
            pass
        try:                                            # ventana oculta/minimizada: revisa la cola 4 veces por segundo
            oculta = self.state() in ("withdrawn", "iconic")
        except tk.TclError:
            oculta = False
        self.after(250 if oculta else 50, self._drenar)

    def log(self, msj, privado=None):
        """privado: texto neutro (solo el tipo de operación y una métrica) para alfred.log y el bus de eventos remoto.
        La ventana de este PC sí muestra el mensaje completo. Se usa con lo dictado, lo escrito y el portapapeles."""
        pub = msj if privado is None else privado
        logging.info(pub)
        BUS.publicar(_tipo_evento(pub), pub)                 # lo siguen los dispositivos remotos
        self.ui(self._log, time.strftime("%H:%M:%S"), msj)

    # ── estado e indicador animado ───────────────────────────────────────────
    def estado(self, txt):
        self.ui(self._estado, txt)

    def _estado(self, txt):
        color, limpio = PAL["muted"], txt
        for emoji, c in (("🟢", PAL["ok"]), ("🟡", PAL["warn"]), ("🔴", PAL["err"]), ("🗣", PAL["voz"])):
            if txt.startswith(emoji):
                color, limpio = c, txt[len(emoji):].lstrip("\ufe0f ").strip()
                break
        self._orb_color = color
        if self._acento is not None:
            try:
                self._acento.configure(fg_color=color)
            except Exception:
                pass
        self._orb_vel = 0.28 if txt.startswith("🗣") else 0.10
        self.label_estado.configure(text=limpio if len(limpio) <= 70 else limpio[:69] + "…")

    def _animar_orb(self):
        try:
            if self.state() not in ("withdrawn", "iconic"):
                self._orb_fase += self._orb_vel
                pulso = (math.sin(self._orb_fase) + 1) / 2
                c, bg, o = self._orb_color, PAL["bg"], self.orb
                o.delete("all")
                ang = math.degrees(self._orb_fase) * 1.4
                g = 12 + 5 * pulso                                   # halo
                o.create_oval(32 - g, 32 - g, 32 + g, 32 + g, fill=mezclar(c, bg, 0.82), outline="")
                o.create_oval(5, 5, 59, 59, outline=mezclar(c, bg, 0.72), width=1)
                for k in range(3):                                   # anillo exterior: 3 arcos que giran
                    o.create_arc(5, 5, 59, 59, start=ang + k * 120, extent=58, style="arc", outline=c, width=2)
                for k in range(2):                                   # anillo interior: gira al revés
                    o.create_arc(14, 14, 50, 50, start=-ang * 1.6 + k * 180, extent=70, style="arc",
                                 outline=mezclar(c, bg, 0.45), width=1)
                r = 6 + 3 * pulso                                    # núcleo
                o.create_oval(32 - r, 32 - r, 32 + r, 32 + r, fill=c, outline="")
        except tk.TclError:
            return
        try:
            oculta = self.state() in ("withdrawn", "iconic")
        except tk.TclError:
            return
        self.after(500 if oculta else 70, self._animar_orb)

    def nombre_os(self):
        return f"{self.alfred.nombre if self.alfred else nombre_desde_cfg(self.cfg)} OS"

    def actualizar_hint(self):
        if self.alfred:
            self.label_hint.configure(text=f"Di «{self.alfred.nombre}» y después tu orden   ·   ☰ para más opciones")
        nom = self.nombre_os()                          # el nombre de la ventana sigue a la palabra de activación
        self.title(nom)
        self.lbl_nombre.configure(text=nom)
        if self.tray:
            try:
                self.tray.title = nom
                self.tray.update_menu()
            except Exception:
                logging.exception("No pude renombrar el icono de la bandeja")

    # ── barra de progreso ────────────────────────────────────────────────────
    def progreso(self, titulo, frac=None, techo=None):
        """progreso('texto', 0.4) = barra al 40 %; progreso('texto') = barra indeterminada; progreso(None) = ocultar."""
        self.ui(self._progreso, titulo, frac, techo)

    def _progreso(self, titulo, frac, techo):
        self._tok_prog += 1
        if titulo is None:
            tok = self._tok_prog
            self.barra.fijar(1.0)                                      # que llegue al final antes de irse
            self.after(800, lambda: self._ocultar_progreso(tok))
            return
        if not self.tarjeta_prog.winfo_ismapped():
            self.barra.reiniciar()
            self.tarjeta_prog.pack(fill="x", padx=22, pady=8, before=self.tarjeta_feed)
            self.barra.iniciar()
        self.lbl_prog.configure(text=titulo)
        if frac is None:
            self.barra.indeterminado(True)
        else:
            self.barra.fijar(frac, techo)

    def _ocultar_progreso(self, tok):
        if tok == self._tok_prog:                                     # nadie empezó otro progreso mientras tanto
            self.barra.detener()
            self.tarjeta_prog.pack_forget()

    # ── ventanas ─────────────────────────────────────────────────────────────
    @staticmethod
    def _viva(v):
        return v is not None and v.winfo_exists()

    def mostrar_ayuda(self):
        self.mostrar(traer=False)
        if self._viva(self.v_ayuda):
            self.v_ayuda.destroy()
        self.v_ayuda = VentanaComandos(self, self.alfred)

    def mostrar_agenda(self):
        self.mostrar(traer=False)
        if self._viva(self.v_agenda):
            self.v_agenda.refrescar()
            traer_al_frente(self.v_agenda)
        else:
            self.v_agenda = VentanaAgenda(self)

    def refrescar_agenda(self):
        if self._viva(self.v_agenda):
            self.v_agenda.refrescar()

    def mostrar_personalizados(self):
        if self.alfred is None:
            return
        self.mostrar(traer=False)
        if self._viva(self.v_personal):
            traer_al_frente(self.v_personal)
        else:
            self.v_personal = VentanaPersonalizados(self, self.alfred)

    def mostrar_menu(self):
        if self.alfred is None:
            return
        if self._viva(self.v_menu):                    # ☰ otra vez: cierra el menú
            self.v_menu.cerrar()
            return
        self.mostrar(traer=False)                      # solo si estaba oculta; si ya se ve, no se toca (ni tamaño ni foco)
        self.v_menu = PanelMenu(self, self, self.alfred, self.cfg)

    # ── mantenimiento ────────────────────────────────────────────────────────
    def verificar_componentes(self):
        def trabajo():
            faltan = faltantes()
            if not faltan:
                self.log("✅ Todos los componentes de Python están instalados.")
                return
            lista = "\n".join(f"  • {p}" for _, p in faltan)
            if not preguntar("Alfred - Permiso para instalar",
                             "Faltan estos componentes de Python:\n\n" + lista +
                             "\n\nSe descargan de internet (pypi.org) y se instalan solo para tu usuario.\n\n¿Instalarlos ahora?"):
                self.log("Instalación cancelada.")
                return
            if os.path.exists(SIN_OPCIONALES):
                os.remove(SIN_OPCIONALES)
            self.progreso("Instalando componentes de Python", 0.0, 0.02)
            res = instalar_paquetes(faltan, self.log,
                                    lambda f, tp: self.progreso("Instalando componentes de Python", f, tp))
            self.progreso(None)
            ok = [p for p, v in res.items() if v]
            mal = [p for p, v in res.items() if not v]
            if ok:
                self.log("✅ Instalado: " + ", ".join(ok) + ". Reinicia Alfred (☰ Menú → Mantenimiento) para usarlo.")
            if mal:
                self.log("⚠️ No se pudo instalar: " + ", ".join(mal) + " (mira alfred.log).")
        threading.Thread(target=trabajo, daemon=True).start()

    def reiniciar(self):
        if not messagebox.askyesno("Reiniciar", "¿Reiniciar Alfred ahora?", parent=self):
            return
        try:
            if self.candado:
                self.candado.close()
            subprocess.Popen([sys.executable, os.path.abspath(__file__), "--reiniciado"], creationflags=SIN_VENTANA)
        except Exception as e:
            self.log(f"⚠️ No pude reiniciar: {e}")
            return
        self.salir()

    # ── ventana / bandeja ────────────────────────────────────────────────────
    def ocultar(self):
        if self.tray:
            self.withdraw()
            self.log(f"💤 {self.nombre_os()} sigue activo en la bandeja del sistema.")
        else:
            self.iconify()

    def mostrar(self, traer=True):
        """Muestra la ventana. Si estaba oculta o minimizada la restaura tal como estaba (si estaba maximizada, sigue
        maximizada: ya no se fuerza el tamaño normal). Con traer=False, si ya se ve, no se toca (ni foco ni tamaño)."""
        try:
            estado = self.state()
        except tk.TclError:
            estado = "normal"
        oculta = estado in ("withdrawn", "iconic")
        if oculta:
            self.deiconify()
        if traer or oculta:
            self.lift()
            self.attributes("-topmost", True)
            self.after(400, lambda: self.attributes("-topmost", False))
            self.focus_force()
            self.after(30, lambda: forzar_primer_plano(self))

    def salir(self):
        if self.tray:
            try:
                self.tray.stop()
            except Exception:
                pass
        self.destroy()

    def _iniciar_bandeja(self):
        try:
            img = Image.new("RGB", (64, 64), (7, 11, 18))
            dib = ImageDraw.Draw(img)
            dib.ellipse((6, 6, 58, 58), outline=(34, 211, 238), width=5)
            dib.ellipse((22, 22, 42, 42), fill=(34, 211, 238))
            menu = pystray.Menu(
                pystray.MenuItem(lambda item: f"Abrir {self.nombre_os()}", lambda i, n: self.ui(self.mostrar), default=True),
                pystray.MenuItem("Salir", lambda i, n: self.ui(self.salir)))
            self.tray = pystray.Icon("Alfred", img, self.nombre_os(), menu)
            self._tray_listo = threading.Event()

            def _preparar(icono):
                icono.visible = True
                self._tray_listo.set()

            def _correr():
                if EN_ARRANQUE:
                    esperar_barra_tareas()       # sin barra de tareas el icono se perdería
                try:
                    self.tray.run(setup=_preparar)
                except Exception:
                    logging.exception("La bandeja se cerró")
            threading.Thread(target=_correr, daemon=True).start()
        except Exception:
            logging.exception("Sin icono de bandeja")
            self.tray = None


# ══════════════════════════════════════════════════════════════════════════════
def evitar_ahorro_energia():
    """
    Windows 10/11 pone en «modo eficiencia» (menos CPU y temporizadores lentos) a los programas cuya ventana está
    oculta o minimizada. Para un asistente de voz eso significa perder palabras. Aquí Alfred pide que no lo hagan
    y sube un poco su prioridad, para que escuche igual con la ventana visible o en segundo plano.
    """
    try:
        k = ctypes.windll.kernel32
        k.GetCurrentProcess.restype = ctypes.c_void_p
        k.SetProcessInformation.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_ulong]
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_ulong]

        class _EstadoEnergia(ctypes.Structure):
            _fields_ = [("Version", ctypes.c_ulong), ("ControlMask", ctypes.c_ulong), ("StateMask", ctypes.c_ulong)]

        yo = k.GetCurrentProcess()
        estado = _EstadoEnergia(1, 0x1 | 0x4, 0)   # velocidad de ejecución + resolución de temporizador: NO limitar
        try:
            k.SetProcessInformation(yo, 4, ctypes.byref(estado), ctypes.sizeof(estado))   # 4 = ProcessPowerThrottling
        except Exception:
            logging.exception("No pude desactivar el modo eficiencia")
        k.SetPriorityClass(yo, 0x8000)              # ABOVE_NORMAL_PRIORITY_CLASS
    except Exception:
        logging.exception("evitar_ahorro_energia")


def main():
    evitar_ahorro_energia()
    candado = instancia_unica()
    if candado is None:          # ya hay un Alfred corriendo: se le pidió mostrarse
        return
    try:
        os.chdir(BASE_DIR)       # Windows lo abre desde System32 cuando arranca con la sesión
    except OSError:
        pass
    logging.info("Alfred %s arrancando · argumentos: %s · Python: %s", VERSION, sys.argv[1:], sys.executable)
    aviso_inicio = arreglar_inicio_con_windows()
    cfg = Config()
    app = AlfredGUI(cfg)              # la ventana (oculta) y la bandeja salen YA; lo demás se espera en segundo plano
    if EN_ARRANQUE:
        app.estado("🟡 Arrancando con Windows…")
    logging.info("⏱️ Arranque: ventana lista a los %.1f s", time.time() - T_INICIO)
    if aviso_inicio:
        app.log(aviso_inicio)
    app.candado = candado
    app.alfred = Alfred(app, cfg)
    app.actualizar_hint()
    threading.Thread(target=servidor_instancia, args=(candado, app), daemon=True).start()
    app.alfred.iniciar()
    app.mainloop()
    try:
        app.alfred.voz.piper.cerrar()
    except Exception:
        pass
    os._exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except BaseException:
        import traceback
        logging.exception("Alfred no pudo arrancar")
        avisar("Alfred - no pudo abrir",
               "Alfred no pudo abrir por este error:\n\n" + traceback.format_exc()[-900:] +
               "\n\nEl detalle completo está en alfred.log, junto al programa.", True)
        sys.exit(1)
