import os
import httpx
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "data" / "assetmadre" / "assetsmenu"

URLS = {
    "tailwind.min.js": "https://cdn.tailwindcss.com",
    "lucide.min.js": "https://unpkg.com/lucide@latest",
    "drive_logo.png": "https://www.gstatic.com/images/branding/product/1x/drive_2020q4_48dp.png"
}

# INTER FONT (Google Fonts)
INTER_CSS_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap"

def ensure_dirs():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url, filename, is_binary=False):
    print(f"Downloading {url} ...")
    try:
        # Using a modern User-Agent to ensure we get woff2 for fonts
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        with httpx.Client(headers=headers, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            if is_binary:
                with open(ASSETS_DIR / filename, "wb") as f:
                    f.write(resp.content)
            else:
                with open(ASSETS_DIR / filename, "w", encoding="utf-8") as f:
                    f.write(resp.text)
            print(f"  OK: {filename}")
            return resp.text if not is_binary else None
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def download_fonts():
    # 1. Download the CSS
    css_content = download_file(INTER_CSS_URL, "inter_fonts.css")
    if not css_content:
        return

    # 2. Extract font URLs (woff2)
    # Example: url(https://fonts.gstatic.com/s/inter/v13/UcCO3FwrX2bDnyZFuWQYDQ.woff2)
    font_urls = re.findall(r'url\((https://fonts\.gstatic\.com/.*?\.woff2)\)', css_content)
    
    local_css = css_content
    for url in font_urls:
        # Generate a local filename from the URL (v13/XYZ.woff2 -> inter_XYZ.woff2)
        font_name = url.split("/")[-1]
        local_name = f"font_{font_name}"
        
        # Download the woff2 file
        download_file(url, local_name, is_binary=True)
        
        # Replace the URL in the local CSS
        local_css = local_css.replace(url, f"/api/assets/assetsmenu/{local_name}")
    
    # Write the updated CSS
    with open(ASSETS_DIR / "inter.css", "w", encoding="utf-8") as f:
        f.write(local_css)
    
    print("Fonts localization completed.")

if __name__ == "__main__":
    ensure_dirs()
    
    # Download baseline scripts
    for name, url in URLS.items():
        is_bin = name.endswith(".png")
        download_file(url, name, is_binary=is_bin)
    
    # Download fonts
    download_fonts()
    
    print("\nAll assets downloaded successfully to data/assetmadre/assetsmenu/")
