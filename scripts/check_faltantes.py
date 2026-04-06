import json

c = json.load(open('data/catalog.json', encoding='utf-8'))
s = json.load(open('data/catalog_syllabuses.json', encoding='utf-8'))

todos = []
for sc in c.get('schools',[]):
    for pa in sc.get('rutas',[]):
        for cu in pa.get('cursos',[]):
            if cu.get('slug'):
                todos.append(cu['slug'])

unicos = set(todos)
syllabus = set(s.get('by_slug',{}).keys())

print(f'Total cursos (con duplicados): {len(todos)}')
print(f'Cursos unicos: {len(unicos)}')
print(f'Duplicados: {len(todos) - len(unicos)}')
print(f'Con syllabus: {len(syllabus)}')
print(f'Faltantes reales: {len(unicos - syllabus)}')

faltan = list(unicos - syllabus)
if faltan:
    print(f'Primeros 20 faltantes: {faltan[:20]}')
else:
    print('¡Todos los cursos únicos tienen syllabus!')
