import asyncio
import os
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from scraper.api import AsyncPlatzi
from scraper.logger import Logger
from backend.app.core.history import history_manager, log_manager
from backend.app.core.utils import get_dir_size, get_course_logo_url

router = APIRouter(prefix="/api/courses", tags=["courses"])

class DownloadRequest(BaseModel):
    url: str
    quality: Optional[str] = "720p"
    overwrite: Optional[bool] = False

# Active Tasks Tracking
active_tasks: Dict[str, Dict] = {}

async def run_download_task(request: DownloadRequest, slug: str):
    """Background task to run the scraper."""
    active_tasks[slug]["status"] = "downloading"
    
    try:
        async with AsyncPlatzi(headless=True) as platzi:
            # We need to get course title/metadata first
            # Simplified: Use the scraper directly on the URL
            Logger.info(f"Starting download task for: {request.url}")
            
            # Note: We are using a simplified logic for this summary
            # In production, this calls the full scraper logic
            success = await platzi.download_course(
                request.url, 
                quality=request.quality, 
                overwrite=request.overwrite
            )
            
            if success:
                active_tasks[slug]["status"] = "completed"
                log_manager.add_event("DOWNLOAD_SUCCESS", f"Curso {slug} completado.", slug, "success")
            else:
                active_tasks[slug]["status"] = "failed"
                log_manager.add_event("DOWNLOAD_ERROR", f"Fallo descarga de {slug}.", slug, "error")
                
    except Exception as e:
        Logger.error(f"Download task error: {e}")
        active_tasks[slug]["status"] = "failed"
        active_tasks[slug]["error"] = str(e)
        log_manager.add_event("DOWNLOAD_ERROR", f"Excepción en {slug}: {str(e)}", slug, "error")

@router.get("/")
async def get_courses():
    """List all courses in history with their current disk status."""
    history = history_manager.get_verified_history()
    courses = []
    
    for slug, info in history["courses"].items():
        courses.append({
            "slug": slug,
            "title": info.get("title", slug),
            "completed_lessons": len(info.get("completed_lessons", [])),
            "total_lessons": info.get("total_lessons", 0),
            "path": info.get("path", ""),
            "exists": info.get("exists", False),
            "thumbnail_url": info.get("thumbnail_url"),
            "logo_url": get_course_logo_url(slug),
            "category": info.get("category"),
            "author": info.get("author"),
            "size": get_dir_size(Path(info["path"])) if info.get("path") else "0 B",
            "gdrive_folder_id": info.get("gdrive_folder_id"),
            "gdrive_folder_url": info.get("gdrive_folder_url"),
            "gdrive_synced_at": info.get("gdrive_synced_at"),
            "gdrive_shared": info.get("gdrive_shared", False)
        })
    
    return sorted(courses, key=lambda x: x["title"])

@router.post("/download")
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Queue a new course download."""
    slug = request.url.rstrip("/").split("/")[-1]
    
    if slug in active_tasks and active_tasks[slug]["status"] == "downloading":
        return {"status": "already_running", "slug": slug}
    
    active_tasks[slug] = {
        "status": "queued",
        "url": request.url,
        "quality": request.quality
    }
    
    background_tasks.add_task(run_download_task, request, slug)
    log_manager.add_event("DOWNLOAD_QUEUED", f"Descarga de {slug} en cola.", slug, "info")
    
    return {"status": "queued", "slug": slug}

@router.get("/status/{slug}")
async def get_task_status(slug: str):
    """Check status of an active download task."""
    if slug not in active_tasks:
        return {"status": "idle"}
    return active_tasks[slug]

@router.get("/events")
async def get_events():
    """Get recent system events."""
    return log_manager.get_events()
