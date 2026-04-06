import os
import math
from pathlib import Path
from typing import Dict, List, Optional
from scraper.logger import Logger
from scraper.utils import find_asset_match

def get_dir_size(path: Path) -> str:
    """Calculate total size of a directory in a human-readable format."""
    try:
        if not path.is_absolute():
            path = Path.cwd() / path
            
        if not path.exists():
            return "0 B"
            
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(str(path)):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    except Exception as e:
        Logger.error(f"Error calculating size for {path}: {e}")
        return "0 B"
        
    if total_size <= 0:
        return "0 B"
    
    units = ("B", "KB", "MB", "GB", "TB")
    try:
        i = int(math.floor(math.log(float(total_size), 1024)))
        p = math.pow(1024, i)
        s = "{:.2f}".format(float(total_size) / p)
        return f"{s} {units[i]}"
    except Exception:
        return f"{total_size} B"

def get_course_logo_url(slug: str) -> str:
    """Get the logo URL for a course based on its slug."""
    # Note: We'll keep the paths relative to the API /api/assets/
    badges_dir = Path("data/assetmadre/badges")
    
    badge_path = badges_dir / f"{slug}.png"
    if badge_path.exists():
        return f"/api/assets/badges/{slug}.png"
    
    badge_svg = badges_dir / f"{slug}.svg"
    if badge_svg.exists():
        return f"/api/assets/badges/{slug}.svg"
    
    default_badge = badges_dir / "platzi-default.svg"
    if default_badge.exists():
        return "/api/assets/badges/platzi-default.svg"
    
    return "FALLBACK_LOGO_SVG"
