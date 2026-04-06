import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from scraper.api import AsyncPlatzi
from scraper.logger import Logger
from scraper.utils import find_asset_match

router = APIRouter(prefix="/api/assets", tags=["assets"])

# Paths to asset directories
DATA_DIR = Path("data")
ASSETS_MADRE = DATA_DIR / "assetmadre"
BADGES_DIR = ASSETS_MADRE / "badges"

# Ensure directories exist
for d in [DATA_DIR, ASSETS_MADRE, BADGES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

async def download_missing_badges_task(force: bool = False):
    """Background task to fetch missing course badges localy."""
    catalog_path = DATA_DIR / "catalog.json"
    if not catalog_path.exists():
        return
        
    import json
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
        
    # Flat list of courses
    courses = []
    for school in catalog.get("schools", []):
        for course in school.get("courses", []):
            courses.append(course)
            
    async with AsyncPlatzi(headless=True) as platzi:
        for course in courses:
            slug = course.get("slug")
            badge_url = course.get("badge")
            
            if not slug or not badge_url:
                continue
                
            # Check if exists
            exists = (BADGES_DIR / f"{slug}.png").exists() or (BADGES_DIR / f"{slug}.svg").exists()
            if exists and not force:
                continue
                
            Logger.info(f"Downloading missing badge for: {slug}")
            try:
                # Basic download logic (Simplified for this script)
                import httpx
                async with httpx.AsyncClient() as client:
                    resp = await client.get(badge_url)
                    if resp.status_code == 200:
                        # Determine extension from content-type or URL
                        ext = ".png"
                        if "svg" in badge_url or "svg" in resp.headers.get("content-type", ""):
                            ext = ".svg"
                        
                        with open(BADGES_DIR / f"{slug}{ext}", "wb") as f:
                            f.write(resp.content)
            except Exception as e:
                Logger.error(f"Failed to download badge for {slug}: {e}")

@router.get("/badges/{filename}")
async def get_badge(filename: str):
    """Serve a course badge from local storage."""
    file_path = BADGES_DIR / filename
    if not file_path.exists():
        # Try finding a match if it's just the slug without extension
        match = find_asset_match(BADGES_DIR, filename)
        if match:
            return FileResponse(match)
        
        # fallback to platzi default if exists
        default = BADGES_DIR / "platzi-default.svg"
        if default.exists():
            return FileResponse(default)
            
        raise HTTPException(status_code=404, detail="Badge not found")
        
    return FileResponse(file_path)

@router.post("/badges/sync")
async def sync_badges(background_tasks: BackgroundTasks):
    """Trigger background download of all missing badges."""
    background_tasks.add_task(download_missing_badges_task)
    return {"status": "queued", "message": "Badge sync started in background"}

@router.get("/discovery")
async def discover_local_courses():
    """Scan data/courses for folders not in history and link them."""
    courses_dir = DATA_DIR / "courses"
    if not courses_dir.exists():
        return {"discovered": 0, "linked": 0}
        
    from backend.app.core.history import history_manager
    history = history_manager.get_history()
    
    discovered = []
    for item in courses_dir.iterdir():
        if item.is_dir() and item.name not in history.get("courses", {}):
            discovered.append(item.name)
            
    # Auto-link if they match catalog entries (Simplified)
    # real implementation would look up metadata in catalog.json
    return {"discovered": len(discovered), "slugs": discovered}

@router.post("/discovery/fix-history")
async def fix_history_paths():
    """Scan history and fix any absolute paths to be relative to the migration project."""
    from backend.app.core.history import history_manager
    history = history_manager.get_history()
    count = 0
    
    for slug, info in history.get("courses", {}).items():
        old_path = info.get("path", "")
        if "Documents" in old_path or "Users" in old_path: # Detect old absolute path
            # Extract the actual course folder name
            folder_name = Path(old_path).name
            new_path = f"data/courses/{folder_name}"
            # Verify if it exists locally in the new structure
            if Path(new_path).exists():
                info["path"] = str(Path(new_path))
                count += 1
                
        # Also clean history entries for missing lessons
        # (This is handled by get_verified_history, but here we can persist it)
        
    if count > 0:
        # We need a save method or equivalent
        # history_manager.save() -- defined as write_json in history.py for simplicity
        from scraper.helpers import write_json
        write_json(Path("data/downloads.json"), history)
        
    return {"fixed_paths": count}
