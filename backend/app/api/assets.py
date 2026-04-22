import mimetypes
import asyncio
import os
import base64
from pathlib import Path
from typing import Dict, Optional, Any
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse

from scraper.api import AsyncPlatzi
from backend.app.core.history import history_manager
from backend.app.core.utils import get_course_logo_url
from scraper.logger import Logger

# Ensure web assets have correct MIME types
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('font/woff2', '.woff2')
mimetypes.add_type('image/png', '.png')
mimetypes.add_type('image/svg+xml', '.svg')

router = APIRouter(prefix="/api/assets", tags=["assets"])

@router.get("/course-file/{slug}/{filename}")
async def get_course_file_asset(slug: str, filename: str):
    """Serve asset file from downloaded course folder."""
    history = history_manager.get_history()
    course = history.get("courses", {}).get(slug)
    
    if not course or not course.get("path"):
        raise HTTPException(status_code=404, detail="Course not found")
    
    course_path = Path(course["path"])
    if not course_path.exists():
        raise HTTPException(status_code=404, detail="Course folder not found")
    
    asset_file = course_path / filename
    if not asset_file.exists():
        raise HTTPException(status_code=404, detail=f"Asset not found: {filename}")
    
    return FileResponse(asset_file)

@router.get("/{asset_path:path}")
async def get_asset(asset_path: str):
    """Serve assets from the centralized repository."""
    # Remove redundant "assetmadre/" prefix and normalize slashes
    clean_path = asset_path.replace("assetmadre/", "").replace("//", "/").strip("/")
    
    # 1. NEW: Try assetmadre/{slug}/... (Per-course assets)
    madre_course_path = Path("data/assetmadre") / clean_path
    if madre_course_path.exists() and madre_course_path.is_file():
        return FileResponse(madre_course_path)

    # 2. Try legacy assetmadre folders (schools, badges, thumbnails)
    madre_legacy = Path("data") / asset_path
    if madre_legacy.exists() and madre_legacy.is_file():
        return FileResponse(madre_legacy)
    
    # 3. Try old assets folder
    old_path = Path("data/assets") / asset_path
    if old_path.exists() and old_path.is_file():
        return FileResponse(old_path)
        
    raise HTTPException(status_code=404, detail=f"Asset not found: {asset_path}")

@router.post("/fetch-assets/{slug}")
async def fetch_course_assets(slug: str):
    """Download og:image thumbnail and logo locally into assetmadre/{slug}/"""
    history = history_manager.get_history()
    course = history.get("courses", {}).get(slug)
    
    assets_dir = Path("data/assetmadre") / slug
    assets_dir.mkdir(parents=True, exist_ok=True)

    async with AsyncPlatzi(headless=True) as platzi:
        page = await platzi.page
        try:
            target_url = f"https://platzi.com/cursos/{slug}/"
            await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)

            # og:image as thumbnail
            og_image = await page.evaluate(r"""() => document.querySelector('meta[property="og:image"]')?.content""")

            # Logo / Badge
            logo_url = await page.evaluate(r"""
                () => {
                    const candidates = [
                        document.querySelector('img[src*="achievements"]'),
                        document.querySelector('img[src*="badge"]'),
                        document.querySelector('img[src*="logo"]'),
                        document.querySelector('header img')
                    ];
                    for (const c of candidates) if (c && c.src) return c.src;
                    return null;
                }""")

            async def download_image(url, dest):
                if not url: return None
                try:
                    b64 = await page.evaluate(r"""
                        async (u) => {
                            const r = await fetch(u);
                            const b = await r.blob();
                            return new Promise(res => {
                                const rd = new FileReader();
                                rd.onloadend = () => res(rd.result);
                                rd.readAsDataURL(b);
                            });
                        }
                    """, url)
                    if not b64 or ',' not in b64: return None
                    data = b64.split(',')[1]
                    dest.write_bytes(base64.b64decode(data))
                    return f"assetmadre/{slug}/{dest.name}"
                except: return None

            thumb_local = await download_image(og_image, assets_dir / "thumbnail.jpg")
            logo_local = await download_image(logo_url, assets_dir / "logo.png")

            # Authors and Category
            author = await page.evaluate(r"""
                () => {
                    const selectors = ['.CourseAuthor-name', '.Teacher-name', 'a[href*="/profes/"] span', '.Header-course-teacher'];
                    for (const s of selectors) {
                        const el = document.querySelector(s);
                        if (el && el.textContent.trim()) return el.textContent.trim();
                    }
                    return null;
                }""")

            category = await page.evaluate(r"""
                () => {
                    const selectors = ['.CourseHeader-category-link', 'a[href*="/categorias/"]', '.Breadcrumb-item:nth-child(2)'];
                    for (const s of selectors) {
                        const el = document.querySelector(s);
                        if (el && el.textContent.trim()) return el.textContent.trim().replace("Ver categoría ", "");
                    }
                    return null;
                }""")
            
            res_data = {
                "status": "ok",
                "thumbnail_url": thumb_local or og_image,
                "logo_url": logo_local or logo_url,
                "author": author,
                "category": category
            }
            
            if course:
                course["thumbnail_url"] = thumb_local or og_image
                course["logo_url"] = logo_local or logo_url
                course["author"] = author or course.get("author")
                course["category"] = category or course.get("category")
                history_manager.save()

            return res_data
        except Exception as e:
            return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
        finally:
            await page.close()
