@echo off
setlocal

echo PLATZI-DOWNLOADER-HARDTOUR - Launcher Initializing...

:: Get the directory of the batch file
set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

:: Check for virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
call .venv\Scripts\activate

:: Ensure dependencies are updated
echo Checking dependencies...
pip install -e . --quiet

:: Launch Backend (FastAPI) via Uvicorn with the new entry point
echo Starting Backend Server (Uvicorn)...
echo.
echo Open: http://localhost:8000
echo.
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --log-level info

pause
