from pathlib import Path
import platformdirs

APP_NAME = "Platzi"
SESSION_DIR = Path(platformdirs.user_data_dir(APP_NAME))
SESSION_FILE = SESSION_DIR / "state.json"
LOGIN_URL = "https://platzi.com/login"
LOGIN_DETAILS_URL = "https://api.platzi.com/api/v1/components/headerv2/user/"
PLATZI_URL = "https://platzi.com"
PLATZI_BASE_URL = "https://platzi.com"
REFERER = "https://platzi.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Referer": REFERER,
    "Origin": "https://platzi.com",
    "Accept": "*/*",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}
SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
CACHE_DIR = SESSION_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
