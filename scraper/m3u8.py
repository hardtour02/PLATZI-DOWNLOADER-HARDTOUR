import asyncio
import functools
import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import aiofiles
import httpx
from tqdm.asyncio import tqdm

from scraper.constants import HEADERS, SESSION_FILE
from scraper.helpers import retry, read_json

def _get_cookies():
    try:
        cookies = read_json(SESSION_FILE)
        return {cookie["name"]: cookie["value"] for cookie in cookies}
    except Exception:
        return {}


def ffmpeg_required(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if not shutil.which("ffmpeg"):
            raise Exception("ffmpeg is not installed")
        return await func(*args, **kwargs)

    return wrapper


def _hash_id(input: str) -> str:
    hash_object = hashlib.sha256(input.encode("utf-8"))
    return hash_object.hexdigest()


def _extract_streaming_urls(content: str) -> list[str] | None:
    # Stop at common delimiters like quotes, braces, etc.
    pattern = r"https?://[^\s\"'}\\]+"
    matches = re.findall(pattern, content)

    # Filter only relevant URLs (exclude subtitles if we are looking for streams)
    urls = []
    for m in matches:
        if ".m3u8" in m or ".ts" in m:
            urls.append(m)
            
    return urls or None


async def _ts_dl(url: str, path: Path, **kwargs):
    overwrite = kwargs.get("overwrite", False)

    if not overwrite and path.exists():
        return

    path.unlink(missing_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)

    headers = HEADERS.copy()
    token = kwargs.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            async with client.stream("GET", url, headers=headers, cookies=_get_cookies(), timeout=60.0) as response:
                if not response.is_success:
                    raise Exception("Error downloading from .ts url")

                async with aiofiles.open(path, "wb") as file:
                    async for chunk in response.aiter_bytes():
                        await file.write(chunk)
    except Exception:
        raise


async def _worker_ts_dl(urls: list, dir: Path, **kwargs):
    BATCH_SIZE = 5
    IDX = 1

    bar_format = "{desc} |{bar}|{percentage:3.0f}% [{n_fmt}/{total_fmt} fragments] [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
    with tqdm(
        total=len(urls),
        desc="Progress",
        colour="green",
        bar_format=bar_format,
        ascii="░█",
    ) as bar:
        progress_callback = kwargs.get("progress_callback")
        lesson_id = kwargs.get("lesson_id", "main")
        
        for i in range(0, len(urls), BATCH_SIZE):
            urls_batch = urls[i : i + BATCH_SIZE]
            tasks = []
            for ts_url in urls_batch:
                ts_path = dir / f"{IDX}.ts"
                tasks.append(_ts_dl(ts_url, ts_path, **kwargs))
                IDX += 1

            try:
                await asyncio.gather(*tasks)
            except Exception:
                raise Exception("Error downloading ts m3u8")

            bar.update(len(urls_batch))
            if progress_callback:
                percent = (bar.n / bar.total) * 100
                if asyncio.iscoroutinefunction(progress_callback):
                    asyncio.create_task(progress_callback(lesson_id, percent))
                else:
                    progress_callback(lesson_id, percent)


@retry()
async def _m3u8_dl(
    url: str,
    path: str | Path,
    **kwargs,
) -> None:
    path = path if isinstance(path, Path) else Path(path)
    overwrite = kwargs.get("overwrite", False)
    tmp_dir = kwargs.get("tmp_dir", ".tmp")
    tmp_dir = tmp_dir if isinstance(tmp_dir, Path) else Path(tmp_dir)

    if not overwrite and path.exists():
        return

    hash = _hash_id(url)

    path.unlink(missing_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    headers = HEADERS.copy()
    token = kwargs.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers, cookies=_get_cookies(), timeout=30.0)
            if not response.is_success:
                raise Exception("Error downloading m3u8 playlist")
            
            content = response.text
            ts_urls = _extract_streaming_urls(content)

            if not ts_urls:
                raise Exception("No ts urls found")

            dir = Path(tmp_dir) / _hash_id(url)
            await _worker_ts_dl(ts_urls, dir, **kwargs)
    except Exception:
        raise

    ts_files = os.listdir(dir)
    ts_files = [ts for ts in ts_files if ts.endswith(".ts")]
    ts_files = sorted(ts_files, key=lambda x: int(x.split(".")[0]))
    ts_paths = [Path(hash) / ts for ts in ts_files]

    list_file = Path(tmp_dir) / f"{hash}.txt"
    with open(list_file.as_posix(), "w") as file:
        for ts_path in ts_paths:
            file.write(f"file '{ts_path.as_posix()}'\n")

    Path(path).parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        list_file.as_posix(),
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-async",
        "1",
        "-y" if overwrite else "-n",
        path,
    ]

    try:
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        list_file.unlink(missing_ok=True)
        shutil.rmtree(dir)

    except Exception:
        raise Exception("Error converting m3u8 to mp4")


@ffmpeg_required
async def m3u8_dl(
    url: str,
    path: str | Path,
    **kwargs,
) -> None:
    """
    Download a m3u8 file and convert it to mp4.

    :param url(str): The URL of the m3u8 file to download.
    :param path(str): The path to save the converted mp4 file.
    :param tmp_dir(str | Path): The directory to save the temporary files.
    :param kwargs: Additional keyword arguments to pass to the requests client.
    :return: None
    """

    # quality selection
    quality_pref = kwargs.get("quality", "720")
    q_idx = 0 if quality_pref == "720" else 1

    overwrite = kwargs.get("overwrite", False)
    path = path if isinstance(path, Path) else Path(path)

    if not overwrite and path.exists():
        return

    headers = HEADERS.copy()
    token = kwargs.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers, cookies=_get_cookies(), timeout=30.0)
            if not response.is_success:
                raise Exception("Error downloading m3u8 master")
            
            content = response.text
        
        # We need to find only VIDEO streams (associated with EXT-X-STREAM-INF)
        # Resolutions are usually at the end of the file after the INF tags
        lines = content.splitlines()
        video_urls = []
        for i, line in enumerate(lines):
            if line.startswith("#EXT-X-STREAM-INF"):
                # The next non-empty line should be the URL
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith("#"):
                        video_urls.append(lines[j].strip())
                        break
        
        if not video_urls:
            # Fallback to general extraction if no INF tags found (legacy?)
            video_urls = _extract_streaming_urls(content) or []
            # Exclude subtitles from fallback
            video_urls = [u for u in video_urls if "subtitle" not in u.lower()]

        if not video_urls:
            raise Exception("No video m3u8 urls found")

        # quality selection
        # quality "720" is usually the 1st or 2nd resolution. 
        # Platzi usually has 2 or 3 resolutions.
        # We'll take the first one available if quality index is out of range.
        if q_idx >= len(video_urls):
            q_idx = 0
            
        await _m3u8_dl(
            video_urls[q_idx], path, **kwargs
        )

    except Exception:
        raise
