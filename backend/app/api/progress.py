import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from scraper.helpers import read_json, write_json
from scraper.logger import Logger


router = APIRouter(prefix="/api/progress", tags=["progress"])

DATA_DIR = Path("data")
PROGRESS_DIR = DATA_DIR / "progress"

# Ensure progress directory exists
if not PROGRESS_DIR.exists():
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)

class ProgressUpdate(BaseModel):
    visto: bool
    tipo_marcado: str # "manual" | "automatico"

@router.get("/dashboard")
async def get_progress_dashboard():
    """
    Lee todos los archivos en data/progress/
    Los combina con la biblioteca local (data/downloads.json)
    Agrupa por escuela usando data/catalog.json
    """
    from backend.app.core.history import history_manager
    history = history_manager.get_verified_history()
    courses_data = history.get("courses", {})
    catalog = read_json(DATA_DIR / "catalog.json") or {"schools": []}
    
    # Map courses to schools for grouping
    course_to_school = {}
    for school in catalog.get("schools", []):
        school_name = school.get("nombre") or school.get("title")
        for routine in (school.get("rutas") or school.get("paths") or []):
            for course in (routine.get("cursos") or routine.get("courses") or []):
                course_to_school[course.get("slug")] = school_name

    metrics = {
        "total": len(courses_data),
        "completados": 0,
        "en_progreso": 0,
        "gb_disco": 0 
    }
    
    by_school = {}
    by_slug = {}
    total_bytes = 0
    
    for slug, info in courses_data.items():
        # Robust existence check
        raw_path = info.get("path")
        p = Path(raw_path) if raw_path else None
        if p and not p.is_absolute():
            p = Path.cwd() / p
            
        exists = p is not None and p.exists()
        
        # Calculate per-course size
        course_bytes = 0
        if exists:
            for dirpath, dirnames, filenames in os.walk(str(p)):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        try:
                            course_bytes += os.path.getsize(fp)
                        except: pass
            total_bytes += course_bytes
        
        # Format human-readable size
        if course_bytes > 1024 * 1024 * 1024:
            total_size = f"{round(course_bytes / (1024*1024*1024), 2)} GB"
        elif course_bytes > 1024 * 1024:
            total_size = f"{round(course_bytes / (1024*1024), 1)} MB"
        elif course_bytes > 1024:
            total_size = f"{round(course_bytes / 1024, 1)} KB"
        else:
            total_size = f"{course_bytes} B"

        # Load detailed progress
        prog_file = PROGRESS_DIR / f"{slug}.json"
        prog = read_json(prog_file) if prog_file.exists() else {"porcentaje": 0, "lecciones": {}}
        
        school = course_to_school.get(slug, "Sin clasificar")
        if school not in by_school:
            by_school[school] = []
            
        vistas = len([l for l in prog.get("lecciones", {}).values() if l.get("visto")])
        porcentaje = prog.get("porcentaje", 0)
        
        # If progress file doesn't match total lessons, recalculate percentage
        total_lessons = info.get("total_lessons", 0)
        if total_lessons > 0 and porcentaje == 0 and vistas > 0:
            porcentaje = round((vistas / total_lessons) * 100)

        course_entry = {
            "slug": slug,
            "title": info.get("title"),
            "porcentaje": porcentaje,
            "total_lecciones": total_lessons,
            "total_lessons": total_lessons,
            "vistas": vistas,
            "last_active": info.get("last_active", ""),
            "last_downloaded": info.get("last_active", ""),
            "exists": exists,
            "total_size": total_size if exists else "0 B",
            "thumbnail_url": info.get("thumbnail_url"),
            "logo_url": info.get("logo_url")
        }
        
        if porcentaje >= 100: 
            metrics["completados"] += 1
        elif porcentaje > 0: 
            metrics["en_progreso"] += 1
        
        by_school[school].append(course_entry)
        by_slug[slug] = course_entry

    metrics["gb_disco"] = round(total_bytes / (1024 * 1024 * 1024), 2)

    return {
        "courses": by_slug, 
        "progress": {
            "metrics": metrics,
            "by_slug": {slug: {"porcentaje": c["porcentaje"], "completadas": c["vistas"]} for slug, c in by_slug.items()}
        }
    }



@router.get("/{curso_slug}")
async def get_course_progress(curso_slug: str):
    prog_file = PROGRESS_DIR / f"{curso_slug}.json"
    if not prog_file.exists():
        return {"porcentaje": 0, "lecciones": {}}
    return read_json(prog_file)

@router.post("/{curso_slug}/{leccion_id}")
async def update_lesson_progress(curso_slug: str, leccion_id: str, data: ProgressUpdate):
    prog_file = PROGRESS_DIR / f"{curso_slug}.json"
    prog = read_json(prog_file) if prog_file.exists() else {"porcentaje": 0, "lecciones": {}}
    
    if "lecciones" not in prog:
        prog["lecciones"] = {}

    # R001: NUNCA desmarcar automáticamente lo marcado manualmente
    current = prog["lecciones"].get(leccion_id)
    if current and current.get("tipo_marcado") == "manual" and data.tipo_marcado == "automatico" and not data.visto:
        return prog

    prog["lecciones"][leccion_id] = {
        "visto": data.visto,
        "marcado_en": datetime.now().isoformat(),
        "tipo_marcado": data.tipo_marcado
    }
    
    # Recalculate percentage
    downloads = read_json(DATA_DIR / "downloads.json") or {}
    course_info = downloads.get(curso_slug)
    
    total = 0
    if course_info:
        total = course_info.get("total_lessons", 0)
    
    if total > 0:
        vistas = len([l for l in prog["lecciones"].values() if l.get("visto")])
        prog["porcentaje"] = round((vistas / total) * 100)
    else:
        prog["porcentaje"] = 0
        
    write_json(prog_file, prog)
    return prog
