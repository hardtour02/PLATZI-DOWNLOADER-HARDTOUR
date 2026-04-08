from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import json
from pathlib import Path
from datetime import datetime
from scraper.logger import Logger

router = APIRouter(prefix="/api/progress", tags=["Progress"])

PROGRESS_DIR = Path("data/progress")
CATALOG_FILE = Path("data/catalog.json")
DOWNLOADS_FILE = Path("data/downloads.json")

class ProgressUpdate(BaseModel):
    visto: bool
    tipo_marcado: str # "manual" o "automatico"

def _read_json(path: Path) -> Dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            Logger.error(f"Error reading JSON {path}: {e}")
    return {}

def _write_json(path: Path, data: Dict):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        Logger.error(f"Error writing JSON {path}: {e}")

@router.get("/dashboard")
async def get_dashboard():
    try:
        catalog = _read_json(CATALOG_FILE)
        downloads = _read_json(DOWNLOADS_FILE)
        
        # Build mapping curso_slug -> escuela
        curso_escuela = {}
        for school in catalog.get("schools", []):
            escuela_name = school.get("title", "Otros")
            for route in school.get("routes", []):
                for course in route.get("courses", []):
                    curso_escuela[course.get("slug")] = escuela_name
                    
        # Read progress
        progress_files = list(PROGRESS_DIR.glob("*.json")) if PROGRESS_DIR.exists() else []
        
        total_courses = 0
        completados = 0
        en_progreso = 0
        por_escuela = {}
        
        for pfile in progress_files:
            slug = pfile.stem
            prog_data = _read_json(pfile)
            
            porcentaje = prog_data.get("porcentaje", 0)
            if porcentaje > 0:
                total_courses += 1
                if porcentaje == 100:
                    completados += 1
                else:
                    en_progreso += 1
                    
                escuela = curso_escuela.get(slug, "Otros")
                if escuela not in por_escuela:
                    por_escuela[escuela] = []
                por_escuela[escuela].append({"slug": slug, "progreso": prog_data})
                
        # Estimate usage from downloads.json (using simple metric if sizes exist)
        gb_disco = sum(d.get("size_bytes", 0) for d in downloads.values() if isinstance(d, dict)) / (1024**3) if isinstance(downloads, dict) else 0

        return {
            "metricas": {
                "total": total_courses,
                "completados": completados,
                "en_progreso": en_progreso,
                "gb_disco": round(gb_disco, 2)
            },
            "por_escuela": por_escuela
        }
    except Exception as e:
        Logger.error(f"Error in get_dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{curso_slug}")
async def get_course_progress(curso_slug: str):
    try:
        pfile = PROGRESS_DIR / f"{curso_slug}.json"
        if not pfile.exists():
            return {"porcentaje": 0, "lecciones": {}}
        return _read_json(pfile)
    except Exception as e:
        Logger.error(f"Error in get_course_progress: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{curso_slug}/{leccion_id}")
async def update_progress(curso_slug: str, leccion_id: str, data: ProgressUpdate):
    try:
        pfile = PROGRESS_DIR / f"{curso_slug}.json"
        prog_data = _read_json(pfile)
        
        if "lecciones" not in prog_data:
            prog_data["lecciones"] = {}
            
        current_leccion = prog_data["lecciones"].get(leccion_id, {})
        
        # R001: SI tipo_marcado=="automatico" Y leccion fue marcada manualmente -> SKIP
        if data.tipo_marcado == "automatico" and current_leccion.get("tipo_marcado") == "manual":
            Logger.info(f"R001: Skipped auto-update for {leccion_id} (already manually marked)")
            return prog_data
            
        # Update leccion
        prog_data["lecciones"][leccion_id] = {
            "visto": data.visto,
            "tipo_marcado": data.tipo_marcado,
            "updated_at": datetime.now().isoformat()
        }
        
        vistas = sum(1 for lec in prog_data["lecciones"].values() if lec.get("visto"))
        total = prog_data.get("total", max(vistas, 1)) # Default to vistas if total unknown
        
        porcentaje = round((vistas / total) * 100) if total > 0 else 0
        prog_data["porcentaje"] = porcentaje
        prog_data["vistas"] = vistas
        
        if porcentaje >= 100 and not prog_data.get("completado_en"):
            prog_data["completado_en"] = datetime.now().isoformat()
        elif porcentaje < 100:
            prog_data["completado_en"] = None
            
        _write_json(pfile, prog_data)
        Logger.info(f"Progress updated for {curso_slug} / {leccion_id} -> {porcentaje}%")
        
        return {
            "porcentaje": porcentaje,
            "vistas": vistas,
            "total": total,
            "completado_en": prog_data.get("completado_en")
        }
    except Exception as e:
        Logger.error(f"Error in update_progress: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")