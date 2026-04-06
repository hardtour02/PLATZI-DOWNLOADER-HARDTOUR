import json
from pathlib import Path

HISTORY_FILE = Path("data/history.json")

def migrate_paths():
    if not HISTORY_FILE.exists():
        print("No history file found.")
        return

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)

    updated = False
    for course_slug, data in history.items():
        # Update course-level paths
        if "path" in data and "Platzi Downloader" in data["path"]:
            data["path"] = data["path"].replace("Platzi Downloader", "PLATZI-DOWNLOADER-HARDTOUR")
            updated = True
        
        # Update metadata asset paths (logo, thumbnail)
        if "metadata" in data:
            meta = data["metadata"]
            for key in ["logo_url", "thumbnail_url"]:
                if key in meta and meta[key] and meta[key].startswith("assets/"):
                    meta[key] = meta[key].replace("assets/", "assetmadre/", 1)
                    updated = True

        # Update lesson-level paths
        if "lessons" in data:
            for lesson_slug, lesson_data in data["lessons"].items():
                if "local_path" in lesson_data and lesson_data["local_path"]:
                    if "Platzi Downloader" in lesson_data["local_path"]:
                        lesson_data["local_path"] = lesson_data["local_path"].replace("Platzi Downloader", "PLATZI-DOWNLOADER-HARDTOUR")
                        updated = True

    if updated:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        print("History paths migrated successfully.")
    else:
        print("No paths needed migration.")

if __name__ == "__main__":
    migrate_paths()
