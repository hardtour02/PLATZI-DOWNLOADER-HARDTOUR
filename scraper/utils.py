import asyncio; import re; from pathlib import Path; import aiofiles; import httpx
from playwright.async_api import Page; from unidecode import unidecode
from scraper.helpers import retry; from scraper.logger import Logger

async def progressive_scroll(page: Page, time: float = 3, delay: float = 0.1, steps: int = 250):
    await asyncio.sleep(3); delta, t = 0.0, 0.0
    while t < time: await asyncio.sleep(delay); await page.mouse.wheel(0, steps); delta += steps; t += delay

def get_course_slug(url: str) -> str:
    m = re.search(r"https://platzi\.com/cursos/([^/]+)/?", url)
    if not m: raise Exception("Invalid course url")
    return m.group(1)

def clean_string(text: str) -> str:
    res = re.sub(r"[ºª\n\r]|[^\w\s]", "", text)
    return re.sub(r"\s+", " ", res).strip()

def slugify(t: str) -> str: return unidecode(clean_string(t)).lower().replace(" ", "-")

def get_m3u8_url(content: str) -> str:
    matches = list(set(re.findall(r"https?://[^\s\"'}\\]+\.m3u8[^\s\"'}\\]*", content)))
    if not matches: raise Exception("No m3u8 urls found")
    url = matches[0]
    for m in matches:
        if "mediastream.platzi.com" in m: url = m; break
    return url.split("?")[0]

def get_m3u8_url_from_thumbnail(url: str | None) -> str | None:
    if not url: return None
    m = re.search(r"/thumb_([a-f0-9]+)_", url)
    return f"https://mdstrm.com/video/{m.group(1)}.m3u8" if m else None

def get_subtitles_url(content: str) -> list[str] | None:
    matches = list(set(re.findall(r"https?://[^\s\"'}]+\.vtt", content)))
    return matches or None

@retry()
async def download(url: str, path: Path, **kwargs):
    if not kwargs.get("overwrite", False) and path.exists(): return
    path.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(follow_redirects=True) as client:
        async with client.stream("GET", url, timeout=60.0, **kwargs) as resp:
            if not resp.is_success: raise Exception("Download failed")
            async with aiofiles.open(path, "wb") as f:
                async for chunk in resp.aiter_bytes(): await f.write(chunk)

@retry()
async def download_styles(url: str, **kwargs):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, timeout=30.0, **kwargs)
        return resp.text if resp.is_success else ""

def find_asset_match(dir: Path, slug: str):
    if not dir.exists(): return None
    norm = unidecode(slug).lower().replace("curso-de-", "").replace("curso-basico-de-", "").replace("curso-", "")
    for p in [f"{slug}.*", f"{norm}.*"]:
        for f in dir.glob(p):
            if f.is_file(): return f
    for f in dir.glob("*.*"):
        if not f.is_file(): continue
        fn = unidecode(f.stem).lower().replace("curso-de-", "").replace("curso-basico-de-", "").replace("curso-", "")
        if norm in fn or fn in norm: return f
    return None
