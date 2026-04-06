import json

c = json.load(open('data/catalog.json', encoding='utf-8'))
s = json.load(open('data/catalog_syllabuses.json', encoding='utf-8'))

# Buscar curso específico
busqueda = "ciberseguridad preventiva"
print(f"=== BUSCANDO: {busqueda} ===\n")

# En catalog.json
for sc in c.get('schools',[]):
    if 'ciber' in sc.get('nombre','').lower():
        for pa in sc.get('rutas',[]):
            for cu in pa.get('cursos',[]):
                slug = cu.get('slug','')
                title = cu.get('title','')
                if 'ciber' in slug.lower() or 'ciber' in title.lower():
                    en_syllabus = slug in s.get('by_slug',{})
                    estado = "✓" if en_syllabus else "✗"
                    print(f'{estado} {title}')
                    print(f'   Slug: {slug}')
                    if en_syllabus:
                        data = s['by_slug'][slug]
                        print(f'   Lecciones: {data.get("total_lessons", 0)} | Duración: {data.get("total_duration", "N/A")}')
                    print()
