import json
import os
import urllib.request
from pathlib import Path

# Mapping exact school names to their provided URLs
school_emblems = {
    "Desarrollo Web": "https://static.platzi.com/media/learningpath/emblems/80b010b7-adb8-4274-965d-113d97cb0d5b.jpg",
    "English Academy": "https://static.platzi.com/media/learningpath/emblems/1091fc90-8f1e-41f8-8b71-236b9004c992.jpg",
    "Marketing Digital": "https://static.platzi.com/media/learningpath/emblems/ab53fae1-8f04-40de-923b-393f30ac1eea.jpg",
    "Inteligencia Artificial y Data Science": "https://static.platzi.com/media/learningpath/emblems/e1f9ffbf-0fbc-4a5e-a07c-143f82c1a850.jpg",
    "Ciberseguridad": "https://static.platzi.com/media/learningpath/emblems/e4b3237a-7cf4-46dc-8611-cd3fed1a7774.jpg",
    "Liderazgo y Habilidades Blandas": "https://static.platzi.com/media/learningpath/emblems/28efe215-abbe-421e-be01-e97e50641652.jpg",
    "Diseño de Producto y UX": "https://static.platzi.com/media/learningpath/emblems/d7a6f6fb-9afc-451f-b21a-723c2beaa2ef.jpg",
    "Desarrollo Móvil": "https://static.platzi.com/media/learningpath/emblems/9932021b-404b-4415-a6ea-f3a93855f08e.jpg",
    "Contenido Audiovisual": "https://static.platzi.com/media/learningpath/emblems/2b1e9410-8650-45b8-99c7-7bbbf25576fc.jpg",
    "Finanzas e Inversiones": "https://static.platzi.com/media/learningpath/emblems/0ee14a84-15d1-40bf-9a83-1307b71d32f3.jpg",
    "Cloud Computing y DevOps": "https://static.platzi.com/media/learningpath/emblems/2935507d-bb87-4661-b17c-dff68b4c0aab.jpg",
    "Programación": "https://static.platzi.com/media/learningpath/emblems/2e48edd1-0888-445a-a022-93de8743d965.jpg",
    "Diseño Gráfico y Arte Digital": "https://static.platzi.com/media/learningpath/emblems/2a30633f-3473-443d-b665-0f8512a79e59.jpg",
    "Blockchain y Web3": "https://static.platzi.com/media/learningpath/emblems/f106aa88-12d8-437b-a72b-e8f30df49d81.jpg",
    "Recursos Humanos": "https://static.platzi.com/media/learningpath/emblems/8af138ab-6106-4ed6-9a3f-9db71e3e6a4c.jpg",
    "Startups": "https://static.platzi.com/media/learningpath/emblems/569972d1-c9c5-4b43-bb9f-8383394756f4.jpg",
    "Negocios": "https://static.platzi.com/media/learningpath/emblems/63b5a5d0-b1ab-49e9-a367-06f773aa01ab.jpg"
}

def main():
    cat_path = Path("data/catalog.json")
    if not cat_path.exists():
        print("Catalog JSON not found")
        return

    with open(cat_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    emblems_dir = Path("data/assetmadre/escuelas")
    emblems_dir.mkdir(parents=True, exist_ok=True)

    for school in catalog.get("schools", []):
        name = school.get("nombre") or school.get("title")
        slug = school.get("slug", name.lower().replace(" ", "-").replace(",", "") if name else "unknown")
        
        # We try to find a URL based on the name or standard Platzi equivalents.
        url = school_emblems.get(name)
        if not url:
            # Maybe slight mismatch in name, try partial matching or fallback
            for k, v in school_emblems.items():
                if k.lower() in name.lower() or name.lower() in k.lower():
                    url = v
                    break

        if url:
            dest_path = emblems_dir / f"{slug}.jpg"
            print(f"Downloading {name} from {url} to {dest_path}")
            try:
                # Add headers to avoid 403 Forbidden
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
                    out_file.write(response.read())
                
                # Assign the relative path
                school["emblema_local"] = f"assetmadre/escuelas/{slug}.jpg"
            except Exception as e:
                print(f"Error downloading {url}: {e}")
        else:
            print(f"No custom url mapping found for: {name}")

    # Write back to JSON
    with open(cat_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=4)
        print("catalog.json updated perfectly.")

if __name__ == "__main__":
    main()
