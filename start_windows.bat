@echo off
title Platzi Downloader - Arranque Portable
color 0A

echo ===================================================
echo     PLATZI DOWNLOADER - INICIANDO SISTEMA
echo ===================================================

cd /d "%~dp0"

:: 1. Verificar si existe Python en el sistema
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Por favor, instala Python 3 - asegurate de marcar "Add python.exe to PATH" en la instalacion.
    echo Abriendo pagina de descarga...
    start https://www.python.org/downloads/
    pause
    exit /b
)

:: 1.1 Verificar si existe FFmpeg (necesario para unir audio/video)
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ADVERTENCIA] FFmpeg no esta instalado o no esta en el PATH.
    echo ---------------------------------------------------
    echo Los videos descargados podrian tener audio desincronizado.
    echo Para arreglarlo automaticamente, abre una terminal de PowerShell y ejecuta:
    echo     winget install ffmpeg
    echo.
    echo O descargalo manualmente desde: https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z
    echo ---------------------------------------------------
    timeout /t 10
)

:: 2. Crear entorno virtual si no existe
if exist ".venv\Scripts\python.exe" goto skip_venv

echo [INFO] Creando entorno virtual (.venv)...
python -m venv .venv

echo [INFO] Instalando dependencias base...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install .

echo [INFO] Instalando navegador Playwright...
".venv\Scripts\python.exe" -m playwright install chromium

:skip_venv

:: 3. Abrir el navegador despues del arranque
echo [INFO] Lanzando el panel de control...
start "" "http://127.0.0.1:8000"

:: 4. Arrancar el servidor backend (nueva estructura)
".venv\Scripts\python.exe" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
pause
