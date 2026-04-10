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
ASSETMADRE_DIR = DATA_DIR / "assetmadre"

# ===== In-Memory Cache =====
_catalog_cache: Optional[dict] = None

def _auto_wire_assets(catalog: dict) -> dict:
    """Auto-wire local asset paths for schools, badges, and thumbnails.
    
    Uses the slug-based naming convention:
    - School icons: assetmadre/escuelas/{slug}.jpg
    - Course badges: assetmadre/badges/{slug}.png
    - Course thumbnails: assetmadre/thumbnails/{slug}.jpg
    """
    schools = catalog.get("schools", [])
    
    for school in schools:
        slug = school.get("slug", "")
        
        # Auto-wire school emblem if missing
        if not school.get("emblema_local") and slug:
            icon_path = ASSETMADRE_DIR / "escuelas" / f"{slug}.jpg"
            if icon_path.exists():
                school["emblema_local"] = f"assetmadre/escuelas/{slug}.jpg"
        
        # Process courses within routes
        for ruta in school.get("rutas", []):
            for curso in ruta.get("cursos", []):
                c_slug = curso.get("slug", "")
                if not c_slug:
                    continue
                
                # Auto-wire badge if missing
                if not curso.get("badge_local"):
                    badge_path = ASSETMADRE_DIR / "badges" / f"{c_slug}.png"
                    if badge_path.exists():
                        curso["badge_local"] = f"assetmadre/badges/{c_slug}.png"
                
                # Auto-wire thumbnail if missing
                if not curso.get("thumbnail_local"):
                    thumb_path = ASSETMADRE_DIR / "thumbnails" / f"{c_slug}.jpg"
                    if thumb_path.exists():
                        curso["thumbnail_local"] = f"assetmadre/thumbnails/{c_slug}.jpg"
    
    return catalog

def load_catalog_into_memory() -> dict:
    """Load catalog.json into memory cache with auto-wired assets.
    Self-heals if the catalog is flat or empty by using local assets."""
    global _catalog_cache
    catalog_file = DATA_DIR / "catalog.json"
    raw = {}
    
    if catalog_file.exists():
        raw = read_json(catalog_file)
        
    # Enforce standard structure if it's missing the schools array but keep whatever else there is
    if raw and "schools" not in raw:
        Logger.info("Missing 'schools' in catalog.json. Seeding from local school assets to avoid empty catalog...")
        schools = []
        escuelas_dir = ASSETMADRE_DIR / "escuelas"
        if escuelas_dir.exists():
            for img in escuelas_dir.glob("*.jpg"):
                slug = img.stem
                schools.append({
                    "nombre": slug.replace("-", " ").title(),
                    "slug": slug,
                    "emblema_local": f"assetmadre/escuelas/{slug}.jpg",
                    "rutas": []
                })
        raw["schools"] = schools
    elif not raw:
        raw = {"schools": []}
    
    _catalog_cache = _auto_wire_assets(raw)
    school_count = len(_catalog_cache.get("schools", []))
    total_courses = sum(
        len(c.get("cursos", []))
        for s in _catalog_cache.get("schools", [])
        for c in s.get("rutas", [])
    )
    Logger.info(f"Catalog loaded: {school_count} schools, {total_courses} courses (Local-First)")
    return _catalog_cache


def get_cached_catalog() -> dict:
    """Return the in-memory catalog. Load from disk if not yet cached."""
    global _catalog_cache
    if _catalog_cache is None:
        load_catalog_into_memory()
    return _catalog_cache


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
    """Serve catalog from in-memory cache (instant response)."""
    return get_cached_catalog()

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
            
            # The scraper (fetch_catalog) already merges with old catalog.json internally.
            # We just need to save the result.
            write_json(DATA_DIR / "catalog.json", catalog)
            
            # Reload into memory cache with auto-wired assets
            load_catalog_into_memory()
            
            await broadcast_update({
                "type": "catalog_done",
                "schools_count": len(catalog.get("schools", []))
            })
            return {"status": "success", "message": "Catálogo actualizado y sincronizado"}
        except Exception as e:
            Logger.error(f"Sync error: {e}")
            await broadcast_update({"type": "catalog_error", "message": str(e)})
            return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
