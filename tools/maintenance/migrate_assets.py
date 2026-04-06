import os
import shutil
from pathlib import Path

DATA_DIR = Path("data")
OLD_ASSETS = DATA_DIR / "assets"
NEW_ASSETS = DATA_DIR / "assetmadre"

def migrate():
    if not OLD_ASSETS.exists():
        print("No old assets found at data/assets.")
        return

    NEW_ASSETS.mkdir(parents=True, exist_ok=True)
    
    for slug_folder in OLD_ASSETS.iterdir():
        if slug_folder.is_dir():
            slug = slug_folder.name
            target_folder = NEW_ASSETS / slug
            target_folder.mkdir(parents=True, exist_ok=True)
            
            print(f"Migrating assets for course: {slug}")
            
            for asset_file in slug_folder.iterdir():
                if asset_file.is_file():
                    dest_file = target_folder / asset_file.name
                    try:
                        shutil.copy2(asset_file, dest_file)
                        print(f"  - Copied: {asset_file.name}")
                    except Exception as e:
                        print(f"  - Error copying {asset_file.name}: {e}")
    
    print("\nMigration completed successfully.")

if __name__ == "__main__":
    migrate()
