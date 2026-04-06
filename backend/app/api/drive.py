import asyncio
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.app.core.drive_service import GDriveManager
from backend.app.core.history import history_manager, sharing_manager, log_manager

router = APIRouter(prefix="/api/gdrive", tags=["drive"])
gdrive_manager = GDriveManager()

class ShareRequest(BaseModel):
    course_slug: str
    email: str

class SyncRequest(BaseModel):
    course_slug: str

active_syncs: Dict[str, Dict] = {}

# background task for course syncing
async def run_sync_task(slug: str, path: str):
    active_syncs[slug]["status"] = "syncing"
    try:
        def progress_cb(filename, uploaded, total, current_idx, total_count):
            active_syncs[slug]["current_file"] = filename
            active_syncs[slug]["progress"] = {
                "uploaded": uploaded,
                "total": total,
                "file_index": current_idx,
                "total_files": total_count
            }

        result = gdrive_manager.upload_course_folder(Path(path), progress_callback=progress_cb)
        
        # update history
        history_manager.update_gdrive_info(
            slug, 
            result["folder_id"], 
            f"https://drive.google.com/drive/folders/{result['folder_id']}"
        )
        
        active_syncs[slug]["status"] = "completed"
        active_syncs[slug]["result"] = result
        log_manager.add_event("DRIVE_SYNC_SUCCESS", f"Sincronización de {slug} finalizada.", slug, "success")
        
    except Exception as e:
        active_syncs[slug]["status"] = "failed"
        active_syncs[slug]["error"] = str(e)
        log_manager.add_event("DRIVE_SYNC_ERROR", f"Sincronización de {slug} falló: {str(e)}", slug, "error")

@router.get("/status")
async def get_gdrive_status():
    auth = gdrive_manager.is_authenticated()
    email = gdrive_manager.get_account_email() if auth else None
    return {"authenticated": auth, "email": email}

@router.get("/auth-url")
async def get_auth_url():
    url = gdrive_manager.get_auth_url()
    if not url:
        raise HTTPException(status_code=400, detail="credentials.json not found in /data")
    return {"url": url}

@router.get("/auth-callback")
async def auth_callback(code: str):
    success = gdrive_manager.exchange_code(code)
    if success:
        return "Authentication successful! You can close this window."
    raise HTTPException(status_code=400, detail="Authentication failed")

@router.post("/sync")
async def sync_course(request: SyncRequest, background_tasks: BackgroundTasks):
    if not gdrive_manager.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated with Google Drive")
        
    history = history_manager.get_history()
    course = history.get("courses", {}).get(request.course_slug)
    
    if not course or not course.get("path"):
        raise HTTPException(status_code=404, detail="Course not found locally")
        
    slug = request.course_slug
    if slug in active_syncs and active_syncs[slug]["status"] == "syncing":
        return {"status": "already_running"}
        
    active_syncs[slug] = {"status": "queued", "progress": {}}
    background_tasks.add_task(run_sync_task, slug, course["path"])
    log_manager.add_event("DRIVE_SYNC_QUEUED", f"Sincronización de {slug} en cola.", slug, "info")
    
    return {"status": "queued"}

@router.get("/sync/status/{slug}")
async def get_sync_status(slug: str):
    return active_syncs.get(slug, {"status": "idle"})

@router.post("/share")
async def share_course(request: ShareRequest):
    if not gdrive_manager.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated with Google Drive")
        
    history = history_manager.get_history()
    course = history.get("courses", {}).get(request.course_slug)
    
    if not course or not course.get("gdrive_folder_id"):
        raise HTTPException(status_code=400, detail="Course must be synced to Google Drive first")
        
    try:
        gdrive_manager.set_permission_user(course["gdrive_folder_id"], request.email, "reader")
        
        # log it
        log = sharing_manager.add_log(
            request.course_slug, 
            course.get("title", request.course_slug),
            request.email,
            course["gdrive_folder_url"]
        )
        
        # update history sharing flag
        history_manager.update_gdrive_info(
            request.course_slug,
            course["gdrive_folder_id"],
            course["gdrive_folder_url"],
            shared=True
        )
        
        log_manager.add_event("DRIVE_SHARE", f"Curso {request.course_slug} compartido con {request.email}.", request.course_slug, "success")
        
        return {"status": "success", "log": log}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shares")
async def get_sharing_logs():
    return sharing_manager.get_logs()

@router.delete("/shares/{log_id}")
async def delete_sharing_log(log_id: str):
    sharing_manager.delete_log(log_id)
    return {"status": "success"}
