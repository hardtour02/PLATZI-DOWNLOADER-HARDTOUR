import asyncio
import json
from pathlib import Path
from scraper.api import AsyncPlatzi
from scraper.helpers import write_json

async def seed_catalog():
    print("Iniciando población de catálogo (Seeding)...")
    async with AsyncPlatzi(headless=True) as platzi:
        catalog_data = await platzi.fetch_catalog()
        if catalog_data and catalog_data.get("schools"):
            Path("data").mkdir(exist_ok=True)
            catalog_path = Path("data/catalog.json")
            write_json(catalog_path, catalog_data)
            print(f"Catálogo poblado con éxito: {len(catalog_data['schools'])} escuelas.")
        else:
            print("Error: No se obtuvieron datos del catálogo.")

if __name__ == "__main__":
    asyncio.run(seed_catalog())
