import json
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from scraper.api import AsyncPlatzi
from scraper.helpers import read_json, write_json
from scraper.logger import Logger
from backend.app.core.history import history_manager

router = APIRouter(prefix="/api/catalog", tags=["catalog"])

DATA_DIR = Path("data")

def merge_catalogs(old_data: dict, new_data: dict) -> dict:
    if not old_data or not old_data.get("schools"):
        return new_data
        
    old_schools = { s.get("nombre", s.get("title", "")): s for s in old_data["schools"] }
    
    for new_school in new_data.get("schools", []):
        sname = new_school.get("nombre", new_school.get("title", ""))
        if not sname: continue
        
        if sname not in old_schools:
            old_schools[sname] = new_school
        else:
            old_school = old_schools[sname]
            for k in ["url", "emblema_local", "color"]:
                if new_school.get(k): old_school[k] = new_school[k]
                
            old_paths = { p.get("nombre_ruta", p.get("title", "")): p for p in old_school.get("rutas", old_school.get("paths", [])) }
            new_paths = new_school.get("rutas", new_school.get("paths", []))
            
            for new_p in new_paths:
                pname = new_p.get("nombre_ruta", new_p.get("title", ""))
                if pname not in old_paths:
                    old_paths[pname] = new_p
                else:
                    old_path = old_paths[pname]
                    old_courses = { c.get("slug", c.get("id", "")): c for c in old_path.get("cursos", old_path.get("courses", [])) }
                    new_courses = new_p.get("cursos", new_p.get("courses", []))
                    
                    for new_c in new_courses:
                        cslug = new_c.get("slug", new_c.get("id", ""))
                        if cslug not in old_courses:
                            old_courses[cslug] = new_c
                        else:
                            old_courses[cslug].update(new_c)
                    
                    old_path["cursos"] = list(old_courses.values())
                    old_paths[pname] = old_path
            
            old_school["rutas"] = list(old_paths.values())
            if "paths" in old_school: del old_school["paths"]
            old_schools[sname] = old_school
            
    return {"schools": list(old_schools.values())}

@router.get("")
async def get_catalog():
    catalog_file = DATA_DIR / "catalog.json"
    if catalog_file.exists():
        return read_json(catalog_file) or {"schools": []}
    return {"schools": []}

@router.post("/sync")
async def sync_catalog():
    """Trigger a full structural catalog sync with progress broadcasting."""
    from backend.app.main import broadcast_update # Lazy import to avoid circular dependency
    
    async def progress_cb(current, total, detail):
        await broadcast_update({
            "type": "catalog_progress",
            "current": current,
            "total": total,
            "detail": detail
        })

    async with AsyncPlatzi() as platzi:
        try:
            catalog = await platzi.fetch_catalog(progress_callback=progress_cb)
            history = history_manager.get_history()
            merged_catalog = merge_catalogs(catalog, history)
            
            write_json(DATA_DIR / "catalog.json", merged_catalog)
            
            await broadcast_update({
                "type": "catalog_done",
                "schools_count": len(merged_catalog.get("schools", []))
            })
            return {"status": "success", "message": "Catálogo actualizado y sincronizado"}
        except Exception as e:
            Logger.error(f"Sync error: {e}")
            await broadcast_update({"type": "catalog_error", "message": str(e)})
            return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
