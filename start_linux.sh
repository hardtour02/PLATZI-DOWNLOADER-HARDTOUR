#!/bin/bash
# ============================================================
# Platzi Downloader - Arranque Portable (Linux/Lubuntu)
# ============================================================

echo -e "\e[32m===================================================\e[0m"
echo -e "\e[32m     PLATZI DOWNLOADER - INICIANDO SISTEMA\e[0m"
echo -e "\e[32m===================================================\e[0m"

# Ir al directorio del script
cd "$(dirname "$0")"

# 1. Verificar si existe Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "\e[31m[ERROR] Python 3 no está instalado.\e[0m"
    if command -v lxterminal &> /dev/null; then
        # Lubuntu fallback to install graphical
        lxterminal -e "sudo apt update && sudo apt install -y python3 python3-pip python3-venv; echo 'Presiona ENTER para continuar'; read"
    else
        echo "Por favor, instala python3-venv con tu gestor de paquetes."
        exit 1
    fi
fi

# 2. Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "[INFO] Creando entorno virtual local (.venv)..."
    python3 -m venv .venv
    
    echo "[INFO] Instalando dependencias del proyecto..."
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install .
    
    echo "[INFO] Instalando navegador Playwright (Chromium)..."
    .venv/bin/python -m playwright install chromium
fi

# 3. Lanzar interfaz
echo "[INFO] Arrancando el dashboard en el navegador..."
(sleep 3 && xdg-open http://127.0.0.1:8000) &

# 4. Iniciar servidor FastAPI
.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
