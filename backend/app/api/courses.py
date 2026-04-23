import asyncio
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from backend.app.core.history import history_manager
from backend.app.core.utils import get_dir_size, get_course_logo_url
from scraper.api import AsyncPlatzi
from scraper.utils import slugify, find_asset_match
from scraper.logger import Logger

router = APIRouter(prefix="/api", tags=["courses"])

active_downloads: Dict[str, float] = {}

@router.get("/history")
async def get_history():
    """Returns verified history with live disk checks and size calculations."""
    verified = history_manager.get_verified_history()
    madre_thumbs = Path("data/assetmadre/thumbnails")

    for slug, info in verified.get("courses", {}).items():
        raw_path = info.get("path")
        if not raw_path:
            info["exists"] = False
            info["logo_url"] = get_course_logo_url(slug)
            continue

        course_path = Path(raw_path)
        if not course_path.is_absolute():
            course_path = Path.cwd() / course_path

        path_exists = course_path.exists()
        info["exists"] = path_exists

        if path_exists:
            info["total_size"] = get_dir_size(course_path)
            course_madre = Path("data/assetmadre") / slug
            
            # Logo discovery
            logo_found = False
            course_logo = course_path / "logo.png"
            if course_logo.exists():
                info["logo_url"] = f"/api/assets/course-file/{slug}/logo.png"
                logo_found = True
            
            if not logo_found and course_madre.exists():
                for ext in ["png", "jpg", "svg"]:
                    if (course_madre / f"logo.{ext}").exists():
                        info["logo_url"] = f"/api/assets/{slug}/logo.{ext}"
                        logo_found = True
                        break

            if not logo_found:
                info["logo_url"] = get_course_logo_url(slug)

            # Thumbnail discovery
            thumb_found = False
            if course_madre.exists():
                for ext in ["jpg", "png"]:
                    if (course_madre / f"thumbnail.{ext}").exists():
                        info["thumbnail_url"] = f"/api/assets/{slug}/thumbnail.{ext}"
                        thumb_found = True
                        break

            if not thumb_found:
                match = find_asset_match(madre_thumbs, slug)
                if match:
                    info["thumbnail_url"] = f"/api/assets/thumbnails/{match.name}"
                else:
                    if not info.get("thumbnail_url") or info.get("thumbnail_url", "").startswith("http"):
                        info["thumbnail_url"] = None
        else:
            info["logo_url"] = get_course_logo_url(slug)

    return verified

@router.post("/open-course-folder")
async def open_course_folder(data: Dict):
    slug = data.get("slug")
    history = history_manager.get_history()
    course = history.get("courses", {}).get(slug)
    
    if course and course.get("path"):
        path = Path(course["path"])
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        if hasattr(os, "startfile"):
            os.startfile(str(path))
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Course path not found")

@router.post("/download")
async def start_download(background_tasks: BackgroundTasks, data: Dict):
    url = data.get("url", "")
    force = data.get("force", False)
    if not url:
        raise HTTPException(status_code=400, detail="URL required")
    
    parts = [p for p in url.split("/") if p]
    slug = parts[-1] if parts else ""
    
    history = history_manager.get_history()
    course_exists = slug in history.get("courses", {})
    
    if course_exists and not force:
        # Course exists but we allow resume — the Smart Resume logic in api.py
        # will skip already-downloaded lessons and continue from where it left off
        background_tasks.add_task(run_download_task, url)
        return {
            "status": "resuming", 
            "message": f"Reanudando descarga del curso. Las lecciones ya descargadas se omitirán.",
            "slug": slug
        }

    background_tasks.add_task(run_download_task, url)
    return {"status": "success", "message": "Download task queued"}

@router.post("/open-folder")
async def open_folder():
    courses_path = Path("data/courses").absolute() # Updated to new data/courses path
    if not courses_path.exists():
        courses_path.mkdir(parents=True, exist_ok=True)
    if hasattr(os, "startfile"):
        os.startfile(str(courses_path))
    return {"status": "success"}

@router.get("/course-content/{slug}")
async def get_course_content(slug: str):
    history = history_manager.get_history()
    course = history.get("courses", {}).get(slug)
    
    if not course or not course.get("path"):
        raise HTTPException(status_code=404, detail="Course not found")
    
    course_path = Path(course["path"])
    if not course_path.exists():
        raise HTTPException(status_code=404, detail="Directory missing")
    
    chapters = []
    lessons_meta = course.get("lessons_metadata", {})
    
    for chap_dir in sorted(course_path.iterdir()):
        if chap_dir.is_dir() and not chap_dir.name.startswith("_"):
            lessons = []
            for lesson_file in sorted(chap_dir.glob("*.mp4")):
                lesson_slug = slugify(lesson_file.stem)
                meta = lessons_meta.get(lesson_slug, {})
                
                lessons.append({
                    "title": lesson_file.stem,
                    "filename": lesson_file.name,
                    "url": f"/videos/{course_path.name}/{chap_dir.name}/{lesson_file.name}",
                    "thumbnail_url": meta.get("thumbnail_url")
                })
            
            if lessons:
                chapters.append({
                    "name": chap_dir.name,
                    "lessons": lessons
                })
                
    return {"title": course.get("title", slug), "chapters": chapters}

@router.get("/syllabus/{slug}")
async def get_syllabus(slug: str):
    syllabuses_file = Path("data/catalog_syllabuses.json")
    if syllabuses_file.exists():
        try:
            with open(syllabuses_file, "r", encoding="utf-8") as f:
                db = json.load(f)
            entry = db.get("by_slug", {}).get(slug)
            if entry and not entry.get("error") and entry.get("chapters"):
                return {"status": "cached", "data": entry}
        except Exception as e:
            Logger.error(f"Error reading syllabuses file: {e}")
    
    return {"status": "not_found", "slug": slug}

@router.get("/sharing")
async def get_sharing_logs():
    from backend.app.core.history import sharing_manager
    return {"logs": sharing_manager.get_logs()}

@router.delete("/sharing/{log_id}")
async def delete_sharing_log(log_id: str):
    from backend.app.core.history import sharing_manager
    sharing_manager.delete_log(log_id)
    return {"status": "success", "message": "Registro eliminado"}

@router.put("/sharing/{log_id}")
async def update_sharing_log(log_id: str, data: Dict):
    from backend.app.core.history import sharing_manager
    new_email = data.get("email")
    if not new_email:
        raise HTTPException(status_code=400, detail="Email requerido")
    sharing_manager.update_log(log_id, new_email)
    return {"status": "success", "message": "Registro actualizado"}

@router.get("/activity")
async def get_activity_logs(limit: int = 100):
    from backend.app.core.history import log_manager
    return {"events": log_manager.get_events(limit)}


async def run_download_task(url: str):
    async with AsyncPlatzi() as platzi:
        try:
            from backend.app.main import broadcast_update # Lazy import
            
            async def report_syllabus(course_title: str, units: List[Dict], metadata: Optional[Dict] = None, slug: Optional[str] = None):
                await broadcast_update({"type": "syllabus", "title": course_title, "units": units, "metadata": metadata, "slug": slug})

            async def report_progress(lesson_id: str, progress: float, title: str = ""):
                active_downloads[lesson_id] = progress
                await broadcast_update({"type": "progress", "lesson_id": lesson_id, "title": title, "progress": progress})

            await platzi.download(url, progress_callback=report_progress, preview_callback=report_syllabus)
            
            # Notify frontend that download is fully complete
            await broadcast_update({"type": "download_complete", "url": url})
        except Exception as e:
             Logger.error(f"Download task failed: {e}")
             await broadcast_update({"type": "error", "message": f"Error de descarga: {str(e)}"})
