@echo off
rem ============================================================================
rem  Iniciar_Alfred.bat
rem  - Busca Python en este equipo (3.9 o superior, con tkinter).
rem  - Si NO lo encuentra, te PREGUNTA y, solo si aceptas, descarga e instala
rem    Python 3.12 desde python.org (solo para tu usuario, sin administrador).
rem  - Despues abre Alfred. Alfred te pedira permiso para cualquier otra cosa
rem    que necesite instalar (librerias de Python y motor de voz).
rem  Deja este archivo en la MISMA carpeta que alfred_X_Y_Z.pyw
rem ============================================================================
setlocal EnableExtensions
cd /d "%~dp0"
title Alfred - Iniciando

rem --- Busca el script mas reciente (alfred_2_3_0.pyw, etc.)
set "SCRIPT="
for /f "delims=" %%F in ('dir /b /o-n "%~dp0alfred_*.pyw" 2^>nul') do if not defined SCRIPT set "SCRIPT=%~dp0%%F"
if not defined SCRIPT (
  call :aviso "No encontre el archivo alfred_X_Y_Z.pyw junto a este iniciador."
  exit /b 1
)

rem --- Hay Python?
call :buscar_python
if defined PYW goto :lanzar

rem --- No hay Python: pedir permiso
powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; $nl=[Environment]::NewLine; $r=[System.Windows.MessageBox]::Show('Alfred necesita Python para funcionar y no lo encontre en este equipo.' + $nl + $nl + 'Puedo descargar e instalar Python 3.12 desde python.org, solo para tu usuario, sin permisos de administrador y sin tocar otros programas. Son unos 27 MB.' + $nl + $nl + 'Quieres instalarlo ahora?','Alfred - Permiso para instalar Python','YesNo','Question'); if ($r -eq 'Yes') { exit 0 } else { exit 1 }"
if errorlevel 1 (
  echo Instalacion cancelada. Alfred no puede iniciar sin Python.
  timeout /t 4 >nul
  exit /b 1
)

echo.
echo Descargando Python 3.12 desde python.org ^(unos 27 MB^)...
set "INSTALADOR=%TEMP%\python-3.12.10-amd64.exe"
if exist "%INSTALADOR%" del /q "%INSTALADOR%"
powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing -Uri 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe' -OutFile '%INSTALADOR%'"
if not exist "%INSTALADOR%" (
  call :aviso "No pude descargar Python. Revisa tu conexion a internet y vuelve a abrir el iniciador."
  exit /b 1
)

echo Instalando Python, puede tardar un par de minutos. No cierres esta ventana...
start /wait "" "%INSTALADOR%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=0 Include_test=0 Include_tcltk=1 Include_pip=1 SimpleInstall=1
del /q "%INSTALADOR%" >nul 2>&1

call :buscar_python
if not defined PYW (
  call :aviso "La instalacion de Python no se completo. Puedes instalarlo a mano desde python.org y volver a abrir este iniciador."
  exit /b 1
)

:lanzar
start "" "%PYW%" "%SCRIPT%" %*
exit /b 0


rem ============================================================================
rem  Subrutinas
rem ============================================================================
:buscar_python
set "PYW="
rem a) En el PATH (se descarta el atajo vacio de la Tienda de Windows)
for /f "delims=" %%P in ('where pythonw 2^>nul') do (
  echo %%P | find /I "WindowsApps" >nul || call :probar "%%~dpP"
)
if defined PYW exit /b 0
rem b) Instalaciones tipicas
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do if not defined PYW call :probar "%%D\"
for /d %%D in ("%ProgramFiles%\Python3*") do if not defined PYW call :probar "%%D\"
exit /b 0

:probar
rem %~1 = carpeta que contiene python.exe y pythonw.exe
if defined PYW exit /b 0
if not exist "%~1python.exe" exit /b 0
if not exist "%~1pythonw.exe" exit /b 0
"%~1python.exe" -c "import sys, tkinter; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
if not errorlevel 1 set "PYW=%~1pythonw.exe"
exit /b 0

:aviso
powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [void][System.Windows.MessageBox]::Show('%~1','Alfred','OK','Warning')"
exit /b 0
