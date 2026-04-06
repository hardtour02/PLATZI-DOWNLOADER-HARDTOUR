import asyncio
import re
from pathlib import Path

import aiofiles
import httpx
from playwright.async_api import Page
from unidecode import unidecode

from scraper.helpers import retry
from scraper.logger import Logger


async def progressive_scroll(
    page: Page, time: float = 3, delay: float = 0.1, steps: int = 250
):
    await asyncio.sleep(3)  # delay to avoid rate limiting
    delta, total_time = 0.0, 0.0
    while total_time < time:
        await asyncio.sleep(delay)
        await page.mouse.wheel(0, steps)
        delta += steps
        total_time += delay


def get_course_slug(url: str) -> str:
    """
    Extracts the course slug from a Platzi course URL.

    :param url(str): The Platzi course URL.
    :return str: The course slug.
    :raises Exception: If the URL is not a valid Platzi course URL.

    Example
    -------
    >>> get_course_slug("https://platzi.com/cursos/fastapi-2023/")
    "fastapi-2023"
    """
    pattern = r"https://platzi\.com/cursos/([^/]+)/?"
    match = re.search(pattern, url)
    if not match:
        raise Exception("Invalid course url")
    return match.group(1)


def clean_string(text: str) -> str:
    """
    Remove special characters from a string and strip it.

    :param text(str): string to clean
    :return str: cleaned string

    Example
    -------
    >>> clean_string("   Hi:;<>?{}|"")
    "Hi"
    """
    result = re.sub(r"[ºª\n\r]|[^\w\s]", "", text)
    return re.sub(r"\s+", " ", result).strip()


def slugify(text: str) -> str:
    """
    Slugify a string, removing special characters and replacing
    spaces with hyphens.

    :param text(str): string to convert
    :return str: slugified string

    Example
    -------
    >>> slugify(""Café! Frío?"")
    "cafe-frio"
    """
    return unidecode(clean_string(text)).lower().replace(" ", "-")


def get_m3u8_url(content: str) -> str:
    # Improved regex to exclude backslashes and other common JS/HTML delimiters
    pattern = r"https?://[^\s\"'}\\]+\.m3u8[^\s\"'}\\]*"
    matches = list(set(re.findall(pattern, content)))

    # Found URLs logic remains, just removing the print

    if not matches:
        raise Exception("No m3u8 urls found")

    # Prefer mediastream.platzi.com over api.platzi.com if both exist
    url = matches[0]
    for m in matches:
        if "mediastream.platzi.com" in m:
            url = m
            break

    # Strip query parameters as they can cause 500 errors and cluttered playlists
    return url.split("?")[0]


def get_m3u8_url_from_thumbnail(thumbnail_url: str | None) -> str | None:
    """
    Extracts a direct MediaStream m3u8 URL from a Platzi lesson thumbnail URL.

    Platzi exposes thumbnail URLs for ALL lessons (even premium/locked ones)
    in the course syllabus JSON. The thumbnail URL contains the MediaStream
    video ID, which can be used to construct a direct m3u8 stream URL.

    Pattern:
      thumbnail: https://thumbs.cdn.mdstrm.com/thumbs/ACCOUNT/thumb_VIDEO_ID_..._Xs.jpg
      m3u8:      https://mdstrm.com/video/VIDEO_ID.m3u8

    :param thumbnail_url: The lesson thumbnail URL from the syllabus data.
    :return: Direct m3u8 URL, or None if extraction fails.
    """
    if not thumbnail_url:
        return None
    try:
        match = re.search(r"/thumb_([a-f0-9]+)_", thumbnail_url)
        if match:
            video_id = match.group(1)
            return f"https://mdstrm.com/video/{video_id}.m3u8"
    except Exception:
        pass
    return None


def get_subtitles_url(content: str) -> list[str] | None:
    pattern = r"https?://[^\s\"'}]+\.vtt"
    matches = list(set(re.findall(pattern, content)))

    if not matches:
        return None

    return matches  # returns a list of all found subtitles without repeating


@retry()
async def download(url: str, path: Path, **kwargs):
    overwrite = kwargs.get("overwrite", False)

    if not overwrite and path.exists():
        return

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(follow_redirects=True) as client:
            async with client.stream("GET", url, timeout=60.0, **kwargs) as response:
                if not response.is_success:
                    raise Exception(f"[Bad Response: {response.status_code}]")

                async with aiofiles.open(path, "wb") as file:
                    async for chunk in response.aiter_bytes():
                        await file.write(chunk)

    except Exception as e:
        Logger.error(f"Downloading file {url} -> {path.name} | {e}")


@retry()
async def download_styles(url: str, **kwargs):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, timeout=30.0, **kwargs)
        if response.is_success:
            return response.text
    return ""


def find_asset_match(directory: Path, target_slug: str):
    """
    Finds a matching asset file in a directory using normalized slug matching.
    Handles variations in accents and 'curso-de-' prefixes.
    """
    if not directory.exists():
        return None
    
    # Normalize target slug
    target_norm = unidecode(target_slug).lower().replace("curso-de-", "").replace("curso-basico-de-", "").replace("curso-", "")
    
    # Priority 1: Exact slug match (with any common extension)
    patterns = [f"{target_slug}.*", f"{target_norm}.*"]
    for p in patterns:
        for found in directory.glob(p):
            if found.is_file(): return found
            
    # Priority 2: Loose normalized scan
    for f in directory.glob("*.*"):
        if not f.is_file(): continue
        f_norm = unidecode(f.stem).lower().replace("curso-de-", "").replace("curso-basico-de-", "").replace("curso-", "")
        # Use partial matches (keywords)
        if target_norm in f_norm or f_norm in target_norm:
            return f
            
    return None
