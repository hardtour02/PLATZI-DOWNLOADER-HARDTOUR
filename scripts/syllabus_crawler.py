"""
syllabus_crawler.py — Crawleo Masivo de Syllabus de Platzi

Recorre TODOS los cursos del catalog.json, extrae sus capítulos y lecciones
usando el scraper autenticado, y guarda todo en data/catalog_syllabuses.json.

Uso:
    python scripts/syllabus_crawler.py [--limit N] [--concurrency N] [--reset]

Opciones:
    --limit N        Solo crawlear los primeros N cursos (útil para pruebas).
    --concurrency N  Cuántas pestañas abrir en paralelo (default: 3).
    --reset          Borrar el archivo de salida y empezar desde cero.

El proceso es INCREMENTAL: los cursos ya guardados se saltan automáticamente.
Puedes interrumpir con Ctrl+C y reiniciarlo cuando quieras — siempre continuará.
"""

import sys
import os
import json
import asyncio
import argparse
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to sys.path so we can import the scraper
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from scraper.api import AsyncPlatzi, get_draft_chapters, get_course_title, get_course_metadata
from scraper.utils import Logger, slugify

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
CATALOG_PATH    = ROOT / "data" / "catalog.json"
SYLLABUSES_PATH = ROOT / "data" / "catalog_syllabuses.json"

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def load_json(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(path: Path, data: dict):
    """Thread-safe atomic write."""
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)

def extract_all_courses(catalog: dict) -> list[dict]:
    """Flatten catalog.json → list of {slug, url, title, level} dicts."""
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

# ──────────────────────────────────────────────────────────────────────────────
# Core crawler: fetch one course's syllabus
# ──────────────────────────────────────────────────────────────────────────────
async def crawl_course(platzi: AsyncPlatzi, slug: str, url: str, sem: asyncio.Semaphore) -> dict | None:
    """Open a new page, navigate to the course, extract chapters & lessons."""
    async with sem:
        page = None
        try:
            page = await platzi.context.new_page()
            page.set_default_timeout(60_000)

            Logger.info(f"  → Navigating: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            await asyncio.sleep(2)  # Let JS render

            chapters_raw = await get_draft_chapters(page)
            if not chapters_raw:
                Logger.warning(f"  ⚠ No chapters found for {slug}")
                return None

            total_seconds = 0
            chapters_out = []
            for ch in chapters_raw:
                units_out = []
                for unit in ch.units:
                    # Parse duration "mm:ss" or "hh:mm:ss" → seconds
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
                    "title": ch.name,   # Chapter model uses 'name', not 'title'
                    "units": units_out,
                })

            # Human-readable total duration
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


# ──────────────────────────────────────────────────────────────────────────────
# Main orchestrator
# ──────────────────────────────────────────────────────────────────────────────
async def main(limit: int, concurrency: int, reset: bool):
    # 0. Setup
    if reset and SYLLABUSES_PATH.exists():
        SYLLABUSES_PATH.unlink()
        Logger.info("Existing syllabuses file deleted (reset mode).")

    catalog    = load_json(CATALOG_PATH)
    syllabuses = load_json(SYLLABUSES_PATH)   # {"by_slug": {...}}
    if "by_slug" not in syllabuses:
        syllabuses["by_slug"] = {}

    all_courses = extract_all_courses(catalog)
    Logger.info(f"Catalog has {len(all_courses)} unique courses.")

    # 1. Filter out already-crawled courses
    pending = [c for c in all_courses if c["slug"] not in syllabuses["by_slug"]]
    if limit:
        pending = pending[:limit]

    Logger.info(f"To crawl: {len(pending)} courses. Already done: {len(all_courses) - len(pending)}")
    if not pending:
        Logger.info("Nothing to crawl. All done!")
        return

    # 2. Launch browser (headless) once, reuse for all courses
    lock = asyncio.Lock()
    sem  = asyncio.Semaphore(concurrency)
    done = 0
    errors = 0
    start_time = time.time()

    async with AsyncPlatzi(headless=True) as platzi:
        Logger.info(f"Browser ready. Crawling {len(pending)} courses with concurrency={concurrency}…")

        async def process(course: dict):
            nonlocal done, errors
            result = await crawl_course(platzi, course["slug"], course["url"], sem)
            async with lock:
                if result:
                    syllabuses["by_slug"][course["slug"]] = result
                    done += 1
                else:
                    # Save a stub so we don't retry endlessly
                    syllabuses["by_slug"][course["slug"]] = {
                        "slug": course["slug"],
                        "title": course["title"],
                        "chapters": [],
                        "total_lessons": 0,
                        "error": True,
                        "crawled_at": datetime.utcnow().isoformat(),
                    }
                    errors += 1

                # Save incrementally every 5 courses
                if (done + errors) % 5 == 0:
                    save_json(SYLLABUSES_PATH, syllabuses)
                    elapsed = time.time() - start_time
                    total_done = done + errors
                    eta_s = (elapsed / total_done) * (len(pending) - total_done) if total_done else 0
                    eta_m = int(eta_s // 60)
                    Logger.info(
                        f"  Progress: {total_done}/{len(pending)} "
                        f"({done} OK, {errors} err) | ETA ~{eta_m} min"
                    )

        # Run all tasks concurrently (semaphore limits parallelism)
        await asyncio.gather(*[process(c) for c in pending])

    # 3. Final save
    syllabuses["last_updated"] = datetime.utcnow().isoformat()
    syllabuses["total_courses"] = len(syllabuses["by_slug"])
    save_json(SYLLABUSES_PATH, syllabuses)

    elapsed = int(time.time() - start_time)
    Logger.info(f"\n{'='*60}")
    Logger.info(f"CRAWLEO COMPLETO en {elapsed//60}m {elapsed%60}s.")
    Logger.info(f"  ✓ Exitosos: {done}")
    Logger.info(f"  ✗ Errores:  {errors}")
    Logger.info(f"  Archivo guardado en: {SYLLABUSES_PATH}")
    Logger.info(f"{'='*60}")


if __name__ == "__main__":
    # Force UTF-8 output so special chars don't crash on Windows terminals
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Crawleo masivo de syllabus de Platzi")
    parser.add_argument("--limit",       type=int, default=0,   help="Solo crawlear los primeros N cursos (0 = todos)")
    parser.add_argument("--concurrency", type=int, default=3,   help="Pestanas paralelas (default: 3)")
    parser.add_argument("--reset",       action="store_true",    help="Borrar archivo existente y empezar de cero")
    args = parser.parse_args()

    limit_str = "Sin limite (TODOS)" if not args.limit else f"Primeros {args.limit} cursos"
    reset_str = "Si - empieza desde cero" if args.reset else "No - reanuda donde lo dejo"

    print("=" * 60)
    print("   PLATZI SYLLABUS CRAWLER - Modo Masivo")
    print("=" * 60)
    print(f"  Concurrencia : {args.concurrency} pestanas paralelas")
    print(f"  Limite       : {limit_str}")
    print(f"  Reset        : {reset_str}")
    print("=" * 60)
    print()

    try:
        asyncio.run(main(args.limit, args.concurrency, args.reset))
    except KeyboardInterrupt:
        print("\n[!] Interrumpido por el usuario. El progreso ya fue guardado.")
