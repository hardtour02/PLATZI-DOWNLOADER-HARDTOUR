import json

c = json.load(open('data/catalog.json', encoding='utf-8'))
s = json.load(open('data/catalog_syllabuses.json', encoding='utf-8'))

print("=== ESCUELAS DISPONIBLES ===")
for i, sc in enumerate(c.get('schools',[])):
    nombre = sc.get('nombre', sc.get('title', 'N/A'))
    slug = sc.get('slug', 'N/A')
    rutas = len(sc.get('rutas', []))
    print(f'{i+1}. {nombre} (slug: {slug}) - {rutas} rutas')

print("\n=== BUSCANDO CIBERSEGURIDAD ===")
ciber_cursos = []
for sc in c.get('schools',[]):
    nombre = sc.get('nombre', sc.get('title', '')).lower()
    if 'ciber' in nombre or 'seguridad' in nombre:
        print(f'Escuela encontrada: {sc.get("nombre")}')
        for pa in sc.get('rutas',[]):
            for cu in pa.get('cursos',[]):
                if cu.get('slug'):
                    ciber_cursos.append(cu['slug'])

unicos = list(set(ciber_cursos))
syllabus = set(s.get('by_slug',{}).keys())
sin_syllabus = [c for c in unicos if c not in syllabus]

if unicos:
    print(f'\nTotal cursos Ciberseguridad: {len(unicos)}')
    print(f'Con syllabus: {len([c for c in unicos if c in syllabus])}')
    print(f'Sin syllabus: {len(sin_syllabus)}')
    if sin_syllabus:
        print(f'\nFaltantes:')
        for slug in sin_syllabus:
            print(f'  - {slug}')
else:
    print('No se encontró escuela de Ciberseguridad')
