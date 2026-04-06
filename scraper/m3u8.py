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
    except: return {}

def ffmpeg_required(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if not shutil.which("ffmpeg"): raise Exception("ffmpeg not installed")
        return await func(*args, **kwargs)
    return wrapper

def _hash_id(input: str) -> str: return hashlib.sha256(input.encode("utf-8")).hexdigest()

def _extract_streaming_urls(content: str) -> list[str] | None:
    pattern = r"https?://[^\s\"'}\\]+"
    matches = re.findall(pattern, content)
    urls = [m for m in matches if ".m3u8" in m or ".ts" in m]
    return urls or None

async def _ts_dl(url: str, path: Path, **kwargs):
    if not kwargs.get("overwrite", False) and path.exists(): return
    path.unlink(missing_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = HEADERS.copy()
    if kwargs.get("token"): headers["Authorization"] = f"Bearer {kwargs.get('token')}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        async with client.stream("GET", url, headers=headers, cookies=_get_cookies(), timeout=60.0) as resp:
            if not resp.is_success: raise Exception("TS download error")
            async with aiofiles.open(path, "wb") as f:
                async for chunk in resp.aiter_bytes(): await f.write(chunk)

async def _worker_ts_dl(urls: list, dir: Path, **kwargs):
    BATCH_SIZE, IDX = 5, 1
    with tqdm(total=len(urls), desc="Progress", colour="green", ascii="░█") as bar:
        for i in range(0, len(urls), BATCH_SIZE):
            batch = urls[i : i + BATCH_SIZE]
            tasks = []
            for u in batch:
                tasks.append(_ts_dl(u, dir / f"{IDX}.ts", **kwargs))
                IDX += 1
            await asyncio.gather(*tasks)
            bar.update(len(batch))

@retry()
async def _m3u8_dl(url: str, path: Path, **kwargs) -> None:
    overwrite, tmp_dir = kwargs.get("overwrite", False), Path(kwargs.get("tmp_dir", ".tmp"))
    if not overwrite and path.exists(): return
    hash_val = _hash_id(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    headers = HEADERS.copy()
    if kwargs.get("token"): headers["Authorization"] = f"Bearer {kwargs.get('token')}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, headers=headers, cookies=_get_cookies(), timeout=30.0)
        if not resp.is_success: raise Exception("m3u8 playlist error")
        ts_urls = _extract_streaming_urls(resp.text)
        if not ts_urls: raise Exception("No TS URLs")
        work_dir = tmp_dir / hash_val
        await _worker_ts_dl(ts_urls, work_dir, **kwargs)
    ts_files = sorted([f for f in os.listdir(work_dir) if f.endswith(".ts")], key=lambda x: int(x.split(".")[0]))
    list_file = tmp_dir / f"{hash_val}.txt"
    with open(list_file, "w") as f:
        for ts in ts_files: f.write(f"file '{hash_val}/{ts}'\n")
    cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-y" if overwrite else "-n", str(path)]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    list_file.unlink(missing_ok=True)
    shutil.rmtree(work_dir)

@ffmpeg_required
async def m3u8_dl(url: str, path: Path, **kwargs) -> None:
    qual = kwargs.get("quality", "720")
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, headers=HEADERS, cookies=_get_cookies(), timeout=30.0)
        if not resp.is_success: raise Exception("m3u8 master error")
        lines = resp.text.splitlines()
        video_urls = []
        for i, line in enumerate(lines):
            if line.startswith("#EXT-X-STREAM-INF"):
                for j in range(i+1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith("#"):
                        video_urls.append(lines[j].strip()); break
        if not video_urls: video_urls = [u for u in (_extract_streaming_urls(resp.text) or []) if "subtitle" not in u.lower()]
        if not video_urls: raise Exception("No video URLs")
        idx = 0 if qual == "720" else (1 if len(video_urls) > 1 else 0)
        await _m3u8_dl(video_urls[idx], path, **kwargs)
