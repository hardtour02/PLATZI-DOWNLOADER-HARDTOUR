import os
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from scraper.helpers import read_json, write_json
from scraper.api import AsyncPlatzi
from scraper.logger import Logger

router = APIRouter(prefix="/api/catalog", tags=["catalog"])

CATALOG_FILE = Path("data/catalog.json")

@router.get("/")
async def get_catalog():
    """Return the cached Platzi catalog."""
    if not CATALOG_FILE.exists():
        return {"schools": []}
    return read_json(CATALOG_FILE)

@router.post("/sync")
async def sync_catalog():
    """Fetch the latest catalog from Platzi and save it."""
    try:
        async with AsyncPlatzi(headless=True) as platzi:
            catalog_data = await platzi.fetch_catalog()
            if not catalog_data:
                raise HTTPException(status_code=500, detail="Failed to fetch catalog data")
            
            Path("data").mkdir(exist_ok=True)
            write_json(CATALOG_FILE, catalog_data)
            return {"status": "success", "schools_count": len(catalog_data.get("schools", []))}
    except Exception as e:
        Logger.error(f"Catalog sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_catalog(query: str):
    """Search for courses in the catalog."""
    if not CATALOG_FILE.exists():
        return []
        
    data = read_json(CATALOG_FILE)
    results = []
    query = query.lower()
    
    for school in data.get("schools", []):
        for course in school.get("courses", []):
            if query in course.get("title", "").lower() or query in course.get("slug", "").lower():
                # Avoid duplicates
                if not any(r["slug"] == course["slug"] for r in results):
                    results.append({
                        "title": course.get("title"),
                        "slug": course.get("slug"),
                        "school": school.get("title"),
                        "badge": course.get("badge")
                    })
                    
    return results
