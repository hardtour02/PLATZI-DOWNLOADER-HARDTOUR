import asyncio
import functools
import json
import os
import time
import httpx
import re
import shutil
import base64
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from urllib.parse import unquote, urljoin
from datetime import datetime

import aiofiles
from playwright.async_api import BrowserContext, Page, async_playwright
from rich import box, print
from rich.live import Live
from rich.table import Table

try:
    from scraper.logger import Logger
    from scraper.helpers import write_json, read_json
    from scraper.constants import DATA_DIR, PLATZI_BASE_URL
    from scraper.m3u8 import m3u8_dl
    from scraper.models import Course, Unit
except ImportError:
    # Fallback for direct script execution
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scraper.logger import Logger
    from scraper.helpers import write_json, read_json
    from scraper.constants import DATA_DIR, PLATZI_BASE_URL
    from scraper.m3u8 import m3u8_dl
    from scraper.models import Course, Unit
    from scraper.utils import download

from .constants import SESSION_FILE, LOGIN_DETAILS_URL, LOGIN_URL, HEADERS
from .collectors import get_course_metadata, get_course_title, get_draft_chapters, get_unit
from .m3u8 import m3u8_dl
from .models import TypeUnit, User
from .utils import clean_string, download, progressive_scroll, slugify
from backend.app.core.history import history_manager, log_manager


def login_required(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        self = args[0]
        if not isinstance(self, AsyncPlatzi):
            Logger.error(f"{login_required.__name__} can only decorate Platzi class.")
            return
        if not self.loggedin:
            Logger.error("Login first!")
            return
        return await func(*args, **kwargs)

    return wrapper


def try_except_request(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        self = args[0]
        if not isinstance(self, AsyncPlatzi):
            Logger.error(
                f"{try_except_request.__name__} can only decorate Platzi class."
            )
            return

        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if str(e):
                Logger.error(e)
        return

    return wrapper


class AsyncPlatzi:
    def __init__(self, headless=False):
        self.loggedin = False
        self.headless = headless
        self.user = None
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context(
            java_script_enabled=True,
            is_mobile=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        try:
            await self._load_state()
        except Exception:
            pass

        await self._set_profile()

        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._context.close()
        await self._browser.close()
        await self._playwright.stop()

    @property
    async def page(self) -> Page:
        if not self._page or self._page.is_closed():
            self._page = await self._context.new_page()
            # Set default timeout for all page actions
            self._page.set_default_timeout(60000)
        return self._page

    @property
    def context(self) -> BrowserContext:
        return self._context

    @try_except_request
    async def _set_profile(self) -> None:
        try:
            data = await self.get_json(LOGIN_DETAILS_URL)
            self.user = User(**data)
        except Exception:
            return

        if self.user.is_authenticated:
            self.loggedin = True
            Logger.info(f"Hi, {self.user.username}!\n")

    @try_except_request
    async def login(self, email: str = None, password: str = None) -> None:
        """Login to Platzi."""
        username = email or os.getenv("PLATZI_USERNAME")
        passwd = password or os.getenv("PLATZI_PASSWORD")

        page = await self.page
        await page.goto(LOGIN_URL)
        
        # If credentials provided, attempt auto-fill
        if username and passwd:
            try:
                await page.wait_for_selector('input[name="email"]', timeout=30000)
                await page.fill('input[name="email"]', username)
                await page.fill('input[name="password"]', passwd)
                await page.click('button[type="submit"]')
            except Exception as e:
                Logger.info(f"Auto-fill failed, please login manually. Error: {e}")

        Logger.info("Waiting for login to complete...")
        try:
            # Use polling to check for successful login instead of brittle CSS modules
            for _ in range(60):
                await page.wait_for_timeout(2000)
                # Check if URL changed away from login, or if a generic avatar/profile element is present
                avatar = await page.query_selector('img[alt*="Avatar"], img[src*="avatar"], a[href*="/mi-perfil"]')
                if "login" not in page.url or avatar:
                    self.loggedin = True
                    await self._save_state()
                    Logger.info("Logged in successfully")
                    return
            
            raise Exception("Timeout 120000ms exceeded while waiting for login.")
        except Exception as e:
            Logger.error(f"Login failed: {e}")
            raise Exception("Login failed")
        finally:
            await page.close()

    @try_except_request
    async def logout(self):
        if Path(SESSION_FILE).exists():
            os.remove(SESSION_FILE)
        Logger.info("Logged out successfully")

    async def _download_asset(self, url: str, subfolder: str, slug: str = "", course_folder: str = "") -> str:
        """Downloads an asset and returns its relative path in assetmadre."""
        if not url or not url.startswith("http"): return ""
        
        # Determine filename
        ext = ".jpg"
        if "achievements" in url or ".png" in url: ext = ".png"
        elif ".svg" in url: ext = ".svg"
        elif ".webp" in url: ext = ".webp"
        
        filename = f"{slug}{ext}" if slug else url.split("/")[-1].split("?")[0]
        if not filename: return ""
        
        # New structure: data/assetmadre/{course_folder}/{filename} if course_folder provided
        # Else: data/assetmadre/{subfolder}/{filename} (legacy)
        if course_folder:
            target_path = DATA_DIR / "assetmadre" / course_folder / filename
            rel_path = f"assetmadre/{course_folder}/{filename}"
        else:
            target_path = DATA_DIR / "assetmadre" / subfolder / filename
            rel_path = f"assetmadre/{subfolder}/{filename}"
        
        if target_path.exists():
            return rel_path
            
        try:
            (DATA_DIR / "assetmadre" / subfolder).mkdir(parents=True, exist_ok=True)
            async with httpx.AsyncClient(follow_redirects=True) as client:
                resp = await client.get(url, timeout=30.0)
                if resp.status_code == 200:
                    target_path.write_bytes(resp.content)
                    return rel_path
        except Exception as e:
            Logger.error(f"Error downloading asset {url}: {e}")
        
        return ""

    async def _safe_goto(self, page, url: str, wait_until="domcontentloaded", max_retries=3, timeout=45000):
        """Robust goto wrapper with retries to avoid Timeout exceptions on slow Platzi pages."""
        for attempt in range(max_retries):
            try:
                await page.goto(url, wait_until=wait_until, timeout=timeout)
                return True
            except Exception as e:
                Logger.warning(f"Goto timeout or error on {url} (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2)
        return False

    async def fetch_catalog(self, progress_callback: Optional[Callable] = None) -> Dict:
        """Structural Scraper (v2): Schools -> Paths -> Courses immersion."""
        page = await self.page
        catalog = {"schools": [], "updated_at": datetime.now().isoformat()}
        
        async def report_progress(current, total, detail=""):
            if progress_callback:
                if asyncio.iscoroutinefunction(progress_callback):
                    await progress_callback(current, total, detail)
                else:
                    progress_callback(current, total, detail)

        try:
            Logger.info("Starting Structural Catalog Scraper (v2)...")
            await report_progress(0, 100, "Iniciando navegación robusta...")
            
            # Phase 1: Schools from /cursos/
            try:
                await self._safe_goto(page, f"{PLATZI_BASE_URL}/cursos/", wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                Logger.error(f"Failed to load /cursos/ after retries: {e}")
                return catalog
                
            await self._scroll_page(page)
            
            # Use the selectors found by browser agent
            school_links = await page.query_selector_all("a[href^='/escuela/']")
            schools_to_process = []
            seen_schools = set()

            for link in school_links:
                try:
                    href = await link.get_attribute("href")
                    if not href or href in seen_schools: continue
                    seen_schools.add(href)
                    
                    name_el = await link.query_selector("h2") or await link.query_selector("h3")
                    name = (await name_el.inner_text()).strip() if name_el else href.split("/")[-2]
                    
                    # Find Emblem image
                    img_el = await link.query_selector("img")
                    img_src = await img_el.get_attribute("src") if img_el else ""
                    
                    schools_to_process.append({
                        "nombre": name,
                        "url": urljoin(PLATZI_BASE_URL, href),
                        "emblema_url": img_src,
                        "slug": href.strip("/").split("/")[-1]
                    })
                except Exception: continue

            await report_progress(10, 100, f"Escuelas identificadas: {len(schools_to_process)}")
            Logger.info(f"Found {len(schools_to_process)} schools. Starting deep sync...")

            # Using previous catalog data if available to not lose what we have
            catalog_file = Path("data/catalog.json")
            if catalog_file.exists():
                try:
                    from scraper.helpers import read_json
                    existing = read_json(catalog_file)
                    if existing and "schools" in existing:
                        catalog = existing
                except: pass

            for idx, s_data in enumerate(schools_to_process):
                pct = 10 + int((idx / len(schools_to_process)) * 85)
                await report_progress(pct, 100, f"Escuela: {s_data['nombre']}")
                
                # Verify if we already have it to avoid re-fetching the emblem if not needed
                existing_school = next((s for s in catalog["schools"] if s["slug"] == s_data["slug"]), None)
                
                school_obj = {
                    "nombre": s_data["nombre"],
                    "url": s_data["url"],
                    "slug": s_data["slug"],
                    # Download School Emblem (Logo)
                    "emblema_local": await self._download_asset(s_data["emblema_url"], "escuelas", s_data["slug"]),
                    "rutas": existing_school["rutas"] if existing_school and "rutas" in existing_school else []
                }
                
                # Visit School page to get routes and their courses
                try:
                    routes = await self._fetch_school_paths_v2(s_data["url"])
                    # If fetching successful, override routes
                    if routes:
                        school_obj["rutas"] = routes
                except Exception as e:
                    Logger.error(f"Error syncing school {s_data['nombre']} (Skipped, will use old routes if any): {e}")

                if existing_school:
                    # Update it in place
                    existing_idx = catalog["schools"].index(existing_school)
                    catalog["schools"][existing_idx] = school_obj
                elif school_obj.get("rutas"):
                    catalog["schools"].append(school_obj)
                    
                # Instant save after each school to avoid data loss
                write_json(DATA_DIR / "catalog.json", catalog)

            await report_progress(100, 100, "Sincronización completa.")
            return catalog
            
        except Exception as e:
            Logger.error(f"fetch_catalog critical error: {e}")
            return catalog
        finally:
            await page.close()

    async def _fetch_school_paths_v2(self, school_url: str) -> List[Dict]:
        """Scrapes paths (rutas) AND their courses inside a specific school page."""
        new_page = await self._context.new_page()
        try:
            Logger.info(f"  Fetching routes for {school_url}")
            try:
                await self._safe_goto(new_page, school_url, wait_until="domcontentloaded", timeout=45000)
            except Exception as e:
                Logger.error(f"  Failed to load school page after retries: {school_url}")
                return []
                
            await self._scroll_page(new_page)
            
            # Selector for Route containers/links
            route_links = await new_page.query_selector_all("a[href*='/ruta/']")
            seen_routes = set()
            routes = []
            
            for r_link in route_links:
                try:
                    r_href = await r_link.get_attribute("href")
                    if not r_href or r_href in seen_routes: continue
                    
                    # Ignore general/fake routes
                    if "/ruta/comunidad-" in r_href: continue
                    seen_routes.add(r_href)
                    
                    r_name_el = await r_link.query_selector("h2") or await r_link.query_selector("h3") or await r_link.query_selector("h4")
                    r_name = (await r_name_el.inner_text()).strip() if r_name_el else r_href.split("/")[-2]
                    
                    route_url = urljoin(PLATZI_BASE_URL, r_href)
                    
                    # Deep Scraping Level 3: Fetch courses for this route
                    courses = await self._fetch_route_courses_v2(route_url)
                    
                    routes.append({
                        "nombre_ruta": r_name,
                        "url_ruta": route_url,
                        "slug_ruta": r_href.strip("/").split("/")[-1],
                        "cursos": courses
                    })
                except Exception as e: 
                    Logger.warning(f"    Failed to process route {r_href}: {e}")
                    continue
            return routes
        finally:
            await new_page.close()

    async def _fetch_route_courses_v2(self, route_url: str) -> List[Dict]:
        """Scrapes courses from a specific route page."""
        course_page = await self._context.new_page()
        courses_list = []
        try:
            Logger.info(f"    Inmersión en Ruta: {route_url}")
            try:
                await self._safe_goto(course_page, route_url, wait_until="domcontentloaded", timeout=45000)
            except Exception as e:
                Logger.error(f"    Failed to load route page after retries: {route_url}")
                return []
            
            await self._scroll_page(course_page)
            
            # Selectors found by research: a[class*="Course_Course"]
            course_cards = await course_page.query_selector_all('a[class*="Course_Course"]')
            
            for card in course_cards:
                try:
                    href = await card.get_attribute("href")
                    if not href: continue
                    
                    slug = href.strip("/").split("/")[-1]
                    title_el = await card.query_selector("h2")
                    title = (await title_el.inner_text()).strip() if title_el else slug
                    
                    # Assets: Badge and Thumbnail
                    badge_el = await card.query_selector('div div:nth-child(1) img') # Circular icon
                    badge_src = await badge_el.get_attribute("src") if badge_el else ""
                    
                    thumb_el = await card.query_selector('figure img') # Cover image
                    thumb_src = await thumb_el.get_attribute("src") if thumb_el else ""
                    
                    # Level
                    level_el = await card.query_selector('div:nth-child(2) div:nth-child(1) span:last-child')
                    level = (await level_el.inner_text()).strip() if level_el else "N/A"
                    
                    # Download assets to assetmadre
                    badge_local = await self._download_asset(badge_src, "badges", f"{slug}-badge")
                    thumb_local = await self._download_asset(thumb_src, "thumbnails", slug)
                    
                    courses_list.append({
                        "title": title,
                        "url": urljoin(PLATZI_BASE_URL, href),
                        "slug": slug,
                        "level": level,
                        "badge_local": badge_local,
                        "thumbnail_local": thumb_local,
                        "downloaded": history_manager.is_downloaded(slug, "") # Mark if already local
                    })
                except Exception as e:
                    continue
            
            Logger.info(f"    Found {len(courses_list)} courses in route.")
            return courses_list
        except Exception as e:
            Logger.error(f"    Error syncing route courses {route_url}: {e}")
            return []
        finally:
            await course_page.close()


    async def _scroll_page(self, page):
        """Helper to handle lazy loading."""
        await page.evaluate("""
            async () => {
                await new Promise((resolve) => {
                    let totalHeight = 0;
                    let distance = 300;
                    let timer = setInterval(() => {
                        let scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        if(totalHeight >= scrollHeight){
                            clearInterval(timer);
                            resolve();
                        }
                    }, 100);
                });
            }
        """)
        await page.wait_for_timeout(2000)

    async def _fetch_catalog_from_dom(self, page) -> Dict:
        """Parse School cards from the Platzi categories DOM as a last resort."""
        try:
            # Scroll to trigger lazy loading if any
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            await page.wait_for_timeout(2000)
            
            links = await page.evaluate("""
                () => {
                    const results = [];
                    // Using selectors found: footer links or main list links
                    const schoolLinks = document.querySelectorAll("a[href^='/escuela/'], a.CollapsibleLink-module_CollapsibleLink__link__iFSa-");
                    
                    schoolLinks.forEach(el => {
                        const href = el.getAttribute('href') || '';
                        const slug = href.replace('/escuela/', '').replace(/\\/+$/, '');
                        const title = el.textContent.trim().split('\\n')[0].trim();
                        
                        if (slug && slug !== 'escuela' && title) {
                            results.push({
                                slug,
                                title,
                                paths: [] // We'd need to visit each to get paths, but this is a fallback
                            });
                        }
                    });
                    return results;
                }
            """)
            
            seen = set()
            schools = []
            for link in (links or []):
                slug = link.get("slug", "")
                title = link.get("title", "")
                if slug and slug not in seen and title:
                    seen.add(slug)
                    schools.append({
                        "id": slug,
                        "title": title,
                        "slug": slug,
                        "color": "#99d4ff",
                        "color_light": "#eef8ff",
                        "paths": []
                    })
            
            Logger.info(f"DOM parsing found {len(schools)} schools")
            return {"schools": schools} if schools else {}
        except Exception as e:
            Logger.error(f"DOM parsing failed: {e}")
            return {}


    @try_except_request
    @login_required
    async def download(self, url: str, progress_callback: Optional[Callable] = None, preview_callback: Optional[Callable] = None, **kwargs):
        # We'll use these from the signature now
        
        # Normalize URL: if it's a lesson URL (clases or cursos with sub-path), redirect to the base course page
        import re
        # Match platzi.com/clases/slug/... or platzi.com/cursos/slug/lesson-slug/
        lesson_match = re.search(r"platzi\.com/(?:clases|cursos)/([^/]+)/(?:[^/]+/?)", url)
        if lesson_match:
            course_slug = lesson_match.group(1)
            url = f"https://platzi.com/cursos/{course_slug}/"
            Logger.info(f"Redirection to base course page: {url}")

        page = await self.page
        
        # Robust navigation with retry
        max_retries = 2
        for attempt in range(max_retries):
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    Logger.error(f"Failed to navigate to {url} after {max_retries} attempts: {e}")
                    raise e
                Logger.warning(f"Navigation to {url} failed, retrying... (Attempt {attempt+1}/{max_retries})")
                await asyncio.sleep(2)

        # Course title and metadata
        course_title = await get_course_title(page)
        course_metadata = await get_course_metadata(page)
        
        # Course slug for assets and cross-referencing
        course_slug = slugify(course_title)

        # iterate over chapters
        draft_chapters = await get_draft_chapters(page)

        # broadcast syllabus if preview_callback is set
        if preview_callback:
            syllabus_units = []
            total_seconds = 0
            for chapter in draft_chapters:
                for unit in chapter.units:
                    # Parse "5:30" or similar to seconds
                    if unit.duration:
                        try:
                            parts = unit.duration.split(":")
                            if len(parts) == 2:
                                total_seconds += int(parts[0]) * 60 + int(parts[1])
                            elif len(parts) == 3:
                                total_seconds += int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                        except Exception:
                            pass

                    syllabus_units.append({
                        "id": slugify(unit.title),
                        "title": unit.title,
                        "url": unit.url,
                        "thumbnail_url": unit.thumbnail_url,
                        "duration": unit.duration
                    })
            
            # Format total duration: "2h 15m" or "45m"
            total_duration = ""
            if total_seconds > 0:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                if hours > 0:
                    total_duration = f"{hours}h {minutes}m"
                else:
                    total_duration = f"{minutes}m"
            
            if course_metadata:
                course_metadata["total_duration"] = total_duration
                course_metadata["total_lessons"] = len(syllabus_units)

            if asyncio.iscoroutinefunction(preview_callback):
                await preview_callback(course_title, syllabus_units, metadata=course_metadata, slug=course_slug)
            else:
                preview_callback(course_title, syllabus_units, metadata=course_metadata, slug=course_slug)

        # download directory
        # Use relative path for portability under data/courses
        DL_DIR = Path("data/courses") / clean_string(course_title)
        DL_DIR.mkdir(parents=True, exist_ok=True)

        # Save assets locally to centralized assetmadre/{slug}/
        # This will group logo, main thumbnail and lesson thumbnails together
        await self._save_course_assets(course_slug, course_metadata, page)

        # --- Course Details Table ---
        table = Table(
            title=course_title,
            caption="processing...",
            caption_style="green",
            title_style="green",
            header_style="green",
            footer_style="green",
            show_footer=True,
            box=box.SQUARE_DOUBLE_HEAD,
        )
        table.add_column("Sections", style="green", footer="Total", no_wrap=True)
        table.add_column("Lessons", style="green", footer="0", justify="center")

        total_units = 0

        with Live(table, refresh_per_second=4):  # update 4 times a second to feel fluid
            for idx, draft_chapter in enumerate(draft_chapters, 1):
                time.sleep(0.3)  # arbitrary delay
                num_units = len(draft_chapter.units)
                total_units += num_units
                table.add_row(f"{idx}-{draft_chapter.name}", str(len(draft_chapter.units)))
                table.columns[1].footer = str(total_units)  # Update footer dynamically

                Logger.info(f"Creating directory: {draft_chapter.name}")

                CHAP_DIR = DL_DIR / f"{idx:02}-{clean_string(draft_chapter.name)}"
                CHAP_DIR.mkdir(parents=True, exist_ok=True)

                # iterate over units
                for jdx, draft_unit in enumerate(draft_chapter.units, 1):
                    lesson_slug = slugify(draft_unit.title)
                    course_slug = slugify(course_title)

                    file_name = f"{jdx:02}-{clean_string(draft_unit.title)}"
                    dst = CHAP_DIR / f"{file_name}.mp4"
                    
                    # Smart Resume: Check history AND physical file
                    if history_manager.is_downloaded(course_slug, lesson_slug) and dst.exists() and dst.stat().st_size > 1024:
                        Logger.info(f"Skipping (already on disk): {draft_unit.title}")
                        continue
                    elif history_manager.is_downloaded(course_slug, lesson_slug):
                        Logger.warning(f"Lesson marked as downloaded but file missing or empty. Re-downloading: {draft_unit.title}")

                    if progress_callback:
                        await progress_callback(lesson_slug, 0, title=draft_unit.title)
                    
                    log_manager.add_event("download_start", f"Iniciando: {draft_unit.title}", slug=course_slug)
                    
                    try:
                        unit = await get_unit(self.context, draft_unit.url, thumbnail_url=draft_unit.thumbnail_url)
                    except Exception as e:
                        log_manager.add_event("download_error", f"Error al obtener unidad {draft_unit.title}: {str(e)}", slug=course_slug, status="error")
                        continue
                        
                    unit_local_path = None
                    # download video
                    if unit.video:
                        # dst is already defined above

                        Logger.print(f"[{dst.name}]", "[DOWNLOADING-VIDEO]")
                        await m3u8_dl(
                            unit.video.url,
                            dst,
                            headers=HEADERS,
                            token=unit.video.token,
                            lesson_id=lesson_slug,
                            **kwargs,
                        )
                        unit_local_path = str(dst.absolute())
                        
                        # Download lesson thumbnail if available
                        local_lesson_thumb = None
                        if draft_unit.thumbnail_url:
                            # Centralize lesson thumbnails in assetmadre/{course_slug}/lessons/
                            madre_lessons = DATA_DIR / "assetmadre" / course_slug / "lessons"
                            madre_lessons.mkdir(parents=True, exist_ok=True)
                            local_lesson_thumb = await self._fetch_and_save(
                                draft_unit.thumbnail_url, 
                                madre_lessons / f"{lesson_slug}.jpg", 
                                page
                            )

                        if progress_callback:
                            await progress_callback(lesson_slug, 50, title=unit.title)

                        # download subtitles
                        subs = unit.video.subtitles_url
                        if subs:
                            for sub in subs:
                                lang = (
                                    "_es"
                                    if "ES" in sub
                                    else "_en"
                                    if "EN" in sub
                                    else "_pt"
                                    if "PT" in sub
                                    else ""
                                )

                                dst = CHAP_DIR / f"{file_name}{lang}.vtt"
                                Logger.print(f"[{dst.name}]", "[DOWNLOADING-SUBS]")
                                await download(sub, dst, **kwargs)

                        # download resources
                        if unit.resources:
                            # download files
                            files = unit.resources.files_url
                            if files:
                                for archive in files:
                                    file_name = unquote(os.path.basename(archive))
                                    dst = CHAP_DIR / f"{jdx:02}-{file_name}"
                                    Logger.print(f"[{dst.name}]", "[DOWNLOADING-FILES]")
                                    await download(archive, dst)

                            # download readings
                            readings = unit.resources.readings_url
                            if readings:
                                dst = CHAP_DIR / f"{jdx:02}-Lecturas recomendadas.txt"
                                Logger.print(f"[{dst.name}]", "[SAVING-READINGS]")
                                with open(dst, "w", encoding="utf-8") as f:
                                    for lecture in readings:
                                        f.write(lecture + "\n")

                            # download summary
                            summary = unit.resources.summary
                            if summary:
                                dst = CHAP_DIR / f"{jdx:02}-Resumen.html"
                                Logger.print(f"[{dst.name}]", "[SAVING-SUMMARY]")
                                with open(dst, "w", encoding="utf-8") as f:
                                    f.write(summary)

                    # download lecture
                    if unit.type == TypeUnit.LECTURE:
                        dst = CHAP_DIR / f"{file_name}.mhtml"
                        Logger.print(f"[{dst.name}]", "[DOWNLOADING-LECTURE]")
                        await self.save_page(unit.url, path=dst)
                        unit_local_path = str(Path(dst).absolute())

                    # download quiz
                    if unit.type == TypeUnit.QUIZ:
                        dst = CHAP_DIR / f"{file_name}.mhtml"
                        Logger.print(f"[{dst.name}]", "[DOWNLOADING-QUIZ]")
                        await self.save_page(unit.url, path=dst)
                        unit_local_path = str(Path(dst).absolute())

                    # --- Unified History Tracking (for all types: video, lecture, quiz) ---
                    history_manager.mark_completed(
                        course_slug, 
                        lesson_slug, 
                        draft_unit.title, 
                        course_title=course_title, 
                        path=str(DL_DIR), # Relative path (data/courses/...)
                        metadata=course_metadata,
                        lesson_metadata={
                            "local_path": unit_local_path,
                            "thumbnail_url": (local_lesson_thumb if 'local_lesson_thumb' in locals() else None) or draft_unit.thumbnail_url
                        }
                    )
                    log_manager.add_event("download_success", f"Completado: {draft_unit.title}", slug=course_slug, status="success")
                    if progress_callback:
                        await progress_callback(lesson_slug, 100, title=draft_unit.title)

                print("=" * 100)

    @try_except_request
    async def save_page(
        self,
        src: str | Page,
        path: str | Path = "source.mhtml",
        **kwargs,
    ):
        overwrite: bool = kwargs.get("overwrite", False)

        if not overwrite and Path(path).exists():
            return

        if isinstance(src, str):
            page = await self.page
            await page.goto(src)
        else:
            page = src

        await progressive_scroll(page)

        try:
            client = await page.context.new_cdp_session(page)
            response = await client.send("Page.captureSnapshot")
            async with aiofiles.open(path, "w", encoding="utf-8", newline="\n") as file:
                await file.write(response["data"])
        except Exception as e:
            Logger.error(f"save_page error: {e}")

    @try_except_request
    async def get_json(self, url: str) -> Dict | None:
        async with httpx.AsyncClient(headers=HEADERS) as client:
            # Transfer cookies from playwright context to httpx
            cookies = await self.context.cookies()
            cookie_dict = {c["name"]: c["value"] for c in cookies}
            
            resp = await client.get(url, cookies=cookie_dict)
            if resp.status_code == 200:
                return resp.json()
        return None

    async def _save_state(self) -> None:
        """Saves current browser state (cookies) to session file."""
        cookies = await self._context.cookies()
        with open(SESSION_FILE, "w") as f:
            json.dump(cookies, f)

    async def _load_state(self) -> None:
        """Loads browser state (cookies) from session file."""
        if Path(SESSION_FILE).exists():
            with open(SESSION_FILE, "r") as f:
                cookies = json.load(f)
                await self._context.add_cookies(cookies)

    async def _save_course_assets(self, slug: str, metadata: Dict, page: Page):
        """Centralizes course branding assets (logo, thumbnail) in data/assetmadre/{slug}/."""
        if not metadata: return
        
        course_madre = DATA_DIR / "assetmadre" / slug
        course_madre.mkdir(parents=True, exist_ok=True)
        
        # Logo
        if metadata.get("logo_url"):
            ext = ".png" if ".png" in metadata["logo_url"] else ".jpg"
            await self._fetch_and_save(metadata["logo_url"], course_madre / f"logo{ext}", page)
            
        # Thumbnail
        if metadata.get("thumbnail_url"):
            ext = ".jpg"
            await self._fetch_and_save(metadata["thumbnail_url"], course_madre / f"thumbnail{ext}", page)

    async def _fetch_and_save(self, url: str, path: Path, page: Page) -> bool:
        """Downloads an image using the authenticated page context or httpx."""
        if not url: return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=15)
                if resp.status_code == 200:
                    path.write_bytes(resp.content)
                    return True
        except: pass
        return False
