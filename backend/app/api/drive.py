import asyncio
import datetime
import re
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse

from backend.app.core.history import history_manager, sharing_manager
from backend.app.core.drive_service import GDriveManager
from scraper.logger import Logger

router = APIRouter(prefix="/api/gdrive", tags=["gdrive"])

gdrive = GDriveManager()

@router.get("/status")
async def gdrive_status():
    if gdrive.is_authenticated():
        return {"authenticated": True, "email": gdrive.get_account_email(), "auth_url": None}
    auth_url = gdrive.get_auth_url()
    return {"authenticated": False, "email": None, "auth_url": auth_url}

@router.get("/auth-callback", response_class=HTMLResponse)
async def gdrive_auth_callback(code: str = ""):
    if not code:
        return HTMLResponse(
            '<html><body style="background:#121212;color:#f44;font-family:sans-serif;padding:40px;">'
            '<h2>❌ Error de autenticación</h2><p>No se recibió código de autorización.</p></body></html>',
            status_code=400,
        )
    ok = gdrive.exchange_code(code)
    if ok:
        return HTMLResponse(
            '<html><body style="background:#121212;color:#00f2a1;font-family:sans-serif;padding:40px;">'
            '<script>'
            'if(window.opener){window.opener.postMessage("gdrive_auth_success","*");window.close();}'
            'else{window.location.href="/";}'
            '</script>'
            '<h2>✅ Cuenta de Google conectada</h2>'
            '<p>Puedes cerrar esta ventana.</p></body></html>'
        )
    return HTMLResponse(
        '<html><body style="background:#121212;color:#f44;font-family:sans-serif;padding:40px;">'
        '<h2>❌ Error al conectar</h2>'
        '<p>No se pudo completar la autorización. Intenta de nuevo.</p></body></html>',
        status_code=500,
    )

@router.post("/logout")
async def gdrive_logout():
    gdrive.revoke()
    return {"status": "success"}

@router.get("/course-status")
async def gdrive_course_status():
    """Retorna el estado de sincronización de cursos con Drive, incluyendo logos."""
    from backend.app.core.utils import get_course_logo_url
    history = history_manager.get_history()
    result = {}
    
    for slug, info in history.get("courses", {}).items():
        in_drive = bool(info.get("gdrive_folder_id"))
        in_local = bool(info.get("path") and Path(info["path"]).exists())
        
        result[slug] = {
            "synced": in_drive,
            "in_local": in_local,
            "folder_id": info.get("gdrive_folder_id"),
            "folder_url": info.get("gdrive_folder_url"),
            "gdrive_synced_at": info.get("gdrive_synced_at"),
            "shared": info.get("gdrive_shared", False),
            "logo_url": get_course_logo_url(slug),
            "title": info.get("title", slug),
        }
    return result

@router.post("/sync")
async def gdrive_sync(background_tasks: BackgroundTasks, data: Dict):
    if not gdrive.is_authenticated():
        raise HTTPException(status_code=401, detail="No autenticado con Google Drive")

    slugs = data.get("slugs", [])
    share = data.get("share", False)
    history = history_manager.get_history()

    valid_slugs = []
    skipped = []
    for s in slugs:
        course = history.get("courses", {}).get(s)
        if course and course.get("path") and Path(course["path"]).exists():
            valid_slugs.append(s)
        else:
            skipped.append(s)

    if valid_slugs:
        background_tasks.add_task(run_gdrive_sync_task, valid_slugs, share)

    return {"status": "queued", "total": len(valid_slugs), "skipped": skipped}

@router.delete("/folder/{slug}")
async def gdrive_delete_folder(slug: str):
    if not gdrive.is_authenticated():
        raise HTTPException(status_code=401, detail="No autenticado")
    
    history = history_manager.get_history()
    course = history.get("courses", {}).get(slug)
    if not course or not course.get("gdrive_folder_id"):
        raise HTTPException(status_code=404, detail="Curso no encontrado en Drive")
    
    try:
        folder_id = course["gdrive_folder_id"]
        await asyncio.to_thread(gdrive.delete_file, folder_id)
        history_manager.remove_gdrive_info(slug)
        return {"status": "success", "message": "Carpeta eliminada de Google Drive"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/share-email")
async def gdrive_share_email(data: Dict):
    if not gdrive.is_authenticated():
        raise HTTPException(status_code=401, detail="No autenticado")
    
    slug = data.get("slug")
    emails = data.get("emails", [])
    if not slug or not emails:
        raise HTTPException(status_code=400, detail="Faltan datos (slug o emails)")
    
    history = history_manager.get_history()
    course = history.get("courses", {}).get(slug)
    if not course or not course.get("gdrive_folder_id"):
        raise HTTPException(status_code=404, detail="Curso no encontrado en Drive")
    
    folder_id = course["gdrive_folder_id"]
    folder_url = course["gdrive_folder_url"]
    title = course.get("title", slug)
    
    success_count = 0
    errors = []
    for email in emails:
        try:
            await asyncio.to_thread(gdrive.set_permission_user, folder_id, email, "reader")
            sharing_manager.add_log(slug, title, email, folder_url)
            success_count += 1
        except Exception as e:
            errors.append(f"{email}: {str(e)}")
            
    if success_count == 0:
        return JSONResponse({"error": "No se pudo compartir con ningún correo", "details": errors}, status_code=500)
    return {"status": "success", "message": f"Compartido con {success_count} correo(s) correctamente.", "errors": errors if errors else None}

@router.post("/sync-remote")
async def gdrive_sync_remote():
    if not gdrive.is_authenticated():
        raise HTTPException(status_code=401, detail="No autenticado")
    
    try:
        courses_fid = await asyncio.to_thread(gdrive.find_folder, "COURSES")
        if not courses_fid:
            return {"status": "info", "message": "No se encontró la carpeta 'COURSES' en Drive.", "count": 0}
        
        remote_folders = await asyncio.to_thread(gdrive.list_files, courses_fid)
        history = history_manager.get_history()
        courses = history.get("courses", {})
        added_count = 0
        
        for folder in remote_folders:
            if folder.get("mimeType") != "application/vnd.google-apps.folder":
                continue
            name = folder["name"]
            fid = folder["id"]
            found = False
            for slug, info in courses.items():
                if info.get("gdrive_folder_id") == fid:
                    found = True
                    break
            
            if not found:
                slug_match = None
                for slug, info in courses.items():
                    if info["title"] == name:
                        slug_match = slug
                        break
                
                if slug_match:
                    history_manager.update_gdrive_info(slug_match, fid, f"https://drive.google.com/drive/folders/{fid}")
                    added_count += 1
                else:
                    new_slug = re.sub(r'[^a-z0-9-]', '-', name.lower()).strip('-')
                    if not new_slug: new_slug = fid[:10]
                    history_manager.add_course(new_slug, {
                        "title": name,
                        "path": None,
                        "gdrive_folder_id": fid,
                        "gdrive_folder_url": f"https://drive.google.com/drive/folders/{fid}",
                        "gdrive_synced_at": datetime.datetime.utcnow().isoformat(),
                        "author": "Cloud (Sync)",
                        "category": "Drive Sync"
                    })
                    added_count += 1
        return {"status": "success", "message": f"Sincronización completada. {added_count} cursos actualizados/añadidos.", "count": added_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_gdrive_sync_task(slugs: List[str], share: bool):
    """Background task: upload selected courses to Google Drive."""
    from backend.app.main import broadcast_update # Lazy import
    from backend.app.core.history import log_manager # Lazy import
    history = history_manager.get_history()
    loop = asyncio.get_event_loop()

    badges_dir = Path("data/assetmadre/badges")
    default_badge = badges_dir / "platzi-default.svg"

    for slug in slugs:
        course = history.get("courses", {}).get(slug)
        if not course: continue
        course_path = Path(course["path"])
        title = course.get("title", slug)
        
        log_manager.add_event("gdrive", f"Iniciando subida de curso: {title}", slug=slug, status="info")
        course_path = Path(course["path"])
        title = course.get("title", slug)

        badge_source = None
        if (badges_dir / f"{slug}.png").exists():
            badge_source = badges_dir / f"{slug}.png"
        elif (badges_dir / f"{slug}.svg").exists():
            badge_source = badges_dir / f"{slug}.svg"
        elif default_badge.exists():
            badge_source = default_badge
        
        if badge_source and badge_source.exists():
            badge_dest = course_path / "logo.png"
            if not badge_dest.exists():
                try:
                    import shutil
                    shutil.copy2(badge_source, badge_dest)
                except Exception as e:
                    Logger.warning(f"No se pudo copiar el badge para {slug}: {e}")

        try:
            def progress_cb(filename, uploaded, total, file_idx, total_files):
                pct = int((uploaded / total) * 100) if total > 0 else 100
                asyncio.run_coroutine_threadsafe(
                    broadcast_update({
                        "type": "gdrive_progress",
                        "slug": slug,
                        "title": title,
                        "filename": filename,
                        "uploaded": uploaded,
                        "total": total,
                        "pct": pct,
                        "file_idx": file_idx,
                        "total_files": total_files,
                    }),
                    loop,
                )

            result = await asyncio.to_thread(gdrive.upload_course_folder, course_path, progress_cb)
            folder_id = result["folder_id"]
            folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

            if share:
                await asyncio.to_thread(gdrive.set_permission_public, folder_id)

            history_manager.update_gdrive_info(slug, folder_id, folder_url, shared=share)
            
            msg_type = "gdrive_already_synced" if result["uploaded"] == 0 and result["skipped"] == result["total"] else "gdrive_done"
            
            if msg_type == "gdrive_done":
                log_manager.add_event("gdrive", f"Subida completada con éxito: {title} ({result['uploaded']} archivos)", slug=slug, status="success")
            else:
                log_manager.add_event("gdrive", f"Curso ya estaba sincronizado: {title}", slug=slug, status="info")

            await broadcast_update({
                "type": msg_type,
                "slug": slug,
                "title": title,
                "folder_url": folder_url,
                "total_files": result["total"],
                "uploaded": result.get("uploaded", 0),
                "skipped": result.get("skipped", 0),
            })
        except Exception as exc:
            Logger.error(f"GDrive sync failed for {slug}: {exc}")
            log_manager.add_event("gdrive", f"Error al subir curso: {title}. Motivo: {str(exc)}", slug=slug, status="error")
            await broadcast_update({"type": "gdrive_error", "slug": slug, "title": title, "message": str(exc)})
