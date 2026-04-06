import json

s = json.load(open('data/catalog_syllabuses.json', encoding='utf-8'))
by_slug = s.get('by_slug', {})
total = len(by_slug)
con_lecciones = sum(1 for v in by_slug.values() if v.get('total_lessons', 0) > 0)
sin_lecciones = sum(1 for v in by_slug.values() if v.get('total_lessons', 0) == 0)
con_error = sum(1 for v in by_slug.values() if v.get('error'))

print(f'Total cursos: {total}')
print(f'Con lecciones: {con_lecciones}')
print(f'Sin lecciones: {sin_lecciones}')
print(f'Con error: {con_error}')
print(f'Progreso: {total - sin_lecciones - con_error}/{total}')

# Verificar cursos de ciberseguridad
print('\n=== Ciberseguridad ===')
ciber = ['ciberseguridad', 'ciberseguridad-en-empresas', 'software-seguro', 'ingles-ciberseguridad']
for slug in ciber:
    if slug in by_slug:
        v = by_slug[slug]
        print(f'{slug}: {v.get("total_lessons", 0)} lecciones, error={v.get("error", False)}')
