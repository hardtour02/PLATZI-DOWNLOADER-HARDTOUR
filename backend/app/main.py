import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Ensure the project root is in sys.path
ROOT_DIR = str(Path(__file__).resolve().parent.parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scraper.api import AsyncPlatzi
from scraper.helpers import write_json
from scraper.logger import Logger
from scraper.constants import SESSION_FILE

# Import Routers
from backend.app.api.auth import router as auth_router
from backend.app.api.courses import router as courses_router
from backend.app.api.catalog import router as catalog_router
from backend.app.api.drive import router as drive_router
from backend.app.api.assets import router as assets_router
from backend.app.api.progress import router as progress_router

async def preload_catalog_if_needed():
    """On startup: if catalog.json is missing but we have a Platzi session, scrape the catalog."""
    catalog_path = Path("data/catalog.json")
    if catalog_path.exists() or not SESSION_FILE.exists():
        return

    Logger.info("No catalog found — pre-loading catalog using saved Platzi session...")
    try:
        async with AsyncPlatzi(headless=True) as platzi:
            catalog_data = await platzi.fetch_catalog()
            if catalog_data and catalog_data.get("schools"):
                Path("data").mkdir(exist_ok=True)
                write_json(catalog_path, catalog_data)
                Logger.info(f"Catalog preloaded: {len(catalog_data['schools'])} schools saved.")
    except Exception as e:
        Logger.error(f"Catalog preload failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(preload_catalog_if_needed())
    yield

app = FastAPI(title="Platzi Downloader Dashboard", lifespan=lifespan)

# Static & Templates setup
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
templates = Jinja2Templates(directory=str(FRONTEND_DIR))

# Global state for WebSocket
connected_clients: List[WebSocket] = []

# Mount Courses directory for video streaming
COURSES_PATH = Path("data/courses").absolute() # Updated path
if not COURSES_PATH.exists():
    COURSES_PATH.mkdir(parents=True, exist_ok=True)
app.mount("/videos", StaticFiles(directory=str(COURSES_PATH)), name="videos")

# Mount Frontend Assets (localized)
ASSETS_DIR = FRONTEND_DIR / "assets"
if not ASSETS_DIR.exists():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# WebSockets
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        if websocket in connected_clients:
            connected_clients.remove(websocket)

async def broadcast_update(data: Dict):
    for client in connected_clients:
        try:
            await client.send_json(data)
        except Exception:
            if client in connected_clients:
                connected_clients.remove(client)

# Include Routers
app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(catalog_router)
app.include_router(drive_router)
app.include_router(assets_router)
app.include_router(progress_router)

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/ping")
async def ping():
    return {"status": "pong"}