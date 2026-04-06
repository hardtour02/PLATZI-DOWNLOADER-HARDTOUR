"""
syllabus_crawler_faltantes.py — Crawleo de Syllabus Faltantes

Identifica cursos en catalog.json que no tienen syllabus en catalog_syllabuses.json
y ejecuta el crawleo solo para esos cursos faltantes.

Uso:
    python scripts/syllabus_crawler_faltantes.py [--concurrency N]

Opciones:
    --concurrency N  Cuántas pestañas abrir en paralelo (default: 3).
"""

import sys
import os
import json
import asyncio
import argparse
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from scraper.api import AsyncPlatzi, get_draft_chapters, get_course_title
from scraper.utils import Logger, slugify

CATALOG_PATH    = ROOT / "data" / "catalog.json"
SYLLABUSES_PATH = ROOT / "data" / "catalog_syllabuses.json"

def load_json(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(path: Path, data: dict):
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)

def extract_all_courses(catalog: dict) -> list[dict]:
    courses = []
    seen = set()
    for school in catalog.get("schools", []):
        for path in school.get("rutas", []):
            for course in path.get("cursos", []):
                slug = course.get("slug") or course.get("id")
                if not slug or slug in seen:
                    continue
                seen.add(slug)
                courses.append({
                    "slug":  slug,
                    "url":   course.get("url") or f"https://platzi.com/cursos/{slug}/",
                    "title": course.get("title") or "",
                    "level": course.get("level") or "",
                })
    return courses

def find_missing_courses(catalog: dict, syllabuses: dict) -> list[dict]:
    all_courses = extract_all_courses(catalog)
    existing_slugs = set(syllabuses.get("by_slug", {}).keys())
    missing = [c for c in all_courses if c["slug"] not in existing_slugs]
    return missing

async def crawl_course(platzi: AsyncPlatzi, slug: str, url: str, sem: asyncio.Semaphore) -> dict | None:
    async with sem:
        page = None
        try:
            page = await platzi.context.new_page()
            page.set_default_timeout(60_000)

            Logger.info(f"  → Navigating: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            await asyncio.sleep(2)

            chapters_raw = await get_draft_chapters(page)
            if not chapters_raw:
                Logger.warning(f"  ⚠ No chapters found for {slug}")
                return None

            total_seconds = 0
            chapters_out = []
            for ch in chapters_raw:
                units_out = []
                for unit in ch.units:
                    secs = 0
                    if unit.duration:
                        try:
                            parts = [int(p) for p in unit.duration.split(":")]
                            if len(parts) == 2:   secs = parts[0] * 60 + parts[1]
                            elif len(parts) == 3: secs = parts[0] * 3600 + parts[1] * 60 + parts[2]
                        except Exception:
                            pass
                    total_seconds += secs
                    units_out.append({
                        "id":       slugify(unit.title),
                        "title":    unit.title,
                        "url":      unit.url,
                        "duration": unit.duration or "",
                    })
                chapters_out.append({
                    "title": ch.name,
                    "units": units_out,
                })

            h = total_seconds // 3600
            m = (total_seconds % 3600) // 60
            total_duration = f"{h}h {m}m" if h else f"{m}m"
            total_lessons  = sum(len(c["units"]) for c in chapters_out)

            result = {
                "slug":           slug,
                "title":          await get_course_title(page) or "",
                "chapters":       chapters_out,
                "total_lessons":  total_lessons,
                "total_duration": total_duration,
                "crawled_at":     datetime.utcnow().isoformat(),
            }
            Logger.info(f"  ✓ {slug}: {total_lessons} lessons in {len(chapters_out)} chapters ({total_duration})")
            return result

        except Exception as e:
            Logger.error(f"  ✗ Error crawling {slug}: {e}")
            return None
        finally:
            if page and not page.is_closed():
                await page.close()

async def main(concurrency: int):
    catalog    = load_json(CATALOG_PATH)
    syllabuses = load_json(SYLLABUSES_PATH)
    
    if "by_slug" not in syllabuses:
        syllabuses["by_slug"] = {}

    missing = find_missing_courses(catalog, syllabuses)
    
    Logger.info(f"Cursos en catálogo: {len(extract_all_courses(catalog))}")
    Logger.info(f"Cursos con syllabus: {len(syllabuses['by_slug'])}")
    Logger.info(f"Cursos faltantes: {len(missing)}")
    
    if not missing:
        Logger.info("¡Todos los cursos tienen syllabus! No hay nada que hacer.")
        return

    Logger.info(f"Crawleando {len(missing)} cursos faltantes con concurrencia={concurrency}...")
    
    lock = asyncio.Lock()
    sem  = asyncio.Semaphore(concurrency)
    done = 0
    errors = 0
    start_time = time.time()

    async with AsyncPlatzi(headless=True) as platzi:
        async def process(course: dict):
            nonlocal done, errors
            result = await crawl_course(platzi, course["slug"], course["url"], sem)
            async with lock:
                if result:
                    syllabuses["by_slug"][course["slug"]] = result
                    done += 1
                else:
                    syllabuses["by_slug"][course["slug"]] = {
                        "slug": course["slug"],
                        "title": course["title"],
                        "chapters": [],
                        "total_lessons": 0,
                        "error": True,
                        "crawled_at": datetime.utcnow().isoformat(),
                    }
                    errors += 1

                if (done + errors) % 5 == 0:
                    save_json(SYLLABUSES_PATH, syllabuses)
                    elapsed = time.time() - start_time
                    total_done = done + errors
                    eta_s = (elapsed / total_done) * (len(missing) - total_done) if total_done else 0
                    Logger.info(
                        f"  Progress: {total_done}/{len(missing)} "
                        f"({done} OK, {errors} err) | ETA ~{int(eta_s // 60)} min"
                    )

        await asyncio.gather(*[process(c) for c in missing])

    syllabuses["last_updated"] = datetime.utcnow().isoformat()
    syllabuses["total_courses"] = len(syllabuses["by_slug"])
    save_json(SYLLABUSES_PATH, syllabuses)

    elapsed = int(time.time() - start_time)
    Logger.info(f"\n{'='*60}")
    Logger.info(f"CRAWLEO COMPLETO en {elapsed//60}m {elapsed%60}s.")
    Logger.info(f"  ✓ Exitosos: {done}")
    Logger.info(f"  ✗ Errores:  {errors}")
    Logger.info(f"  Total cursos con syllabus: {len(syllabuses['by_slug'])}")
    Logger.info(f"{'='*60}")

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Crawleo de syllabus faltantes")
    parser.add_argument("--concurrency", type=int, default=3, help="Pestañas paralelas (default: 3)")
    args = parser.parse_args()

    print("=" * 60)
    print("   PLATZI SYLLABUS CRAWLER - Cursos Faltantes")
    print("=" * 60)
    print(f"  Concurrencia : {args.concurrency} pestañas paralelas")
    print("=" * 60)
    print()

    try:
        asyncio.run(main(args.concurrency))
    except KeyboardInterrupt:
        print("\n[!] Interrumpido por el usuario. El progreso ya fue guardado.")
