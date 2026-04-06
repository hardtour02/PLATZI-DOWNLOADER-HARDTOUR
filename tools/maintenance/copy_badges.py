"""
Script para copiar los badges correctos desde la carpeta base badges
hacia la carpeta assetmadre/badges usando el catálogo de cursos.

Este script:
1. Lee catalog.json para obtener los slugs de todos los cursos
2. Busca en la carpeta *_files los badges correspondientes
3. Copia y renombra los badges a la carpeta assetmadre/badges
"""

import json
import shutil
import re
from pathlib import Path
from typing import Optional


def load_catalog(catalog_path: Path) -> list[tuple[str, str]]:
    """Carga el catálogo y extrae todos los slugs de cursos únicos con sus títulos."""
    with open(catalog_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    courses = {}  # slug -> title
    for school in data.get('schools', []):
        for ruta in school.get('rutas', []):
            for curso in ruta.get('cursos', []):
                if slug := curso.get('slug'):
                    title = curso.get('title', '')
                    courses[slug] = title

    return sorted(courses.items(), key=lambda x: x[0])  # Retorna lista de tuplas (slug, title)


def normalize_text(text: str) -> str:
    """Normaliza texto: lowercase, sin acentos, sin caracteres especiales."""
    text = text.lower().strip()
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r'\s+', ' ', text)
    return text


def find_badge_for_slug(slug: str, badges_dir: Path, course_title: str = "") -> Optional[Path]:
    """
    Busca un badge para un slug dado usando múltiples estrategias mejoradas.

    Estrategias de búsqueda:
    1. Coincidencia exacta del slug
    2. Coincidencia con variaciones (badge, piezas, etc.)
    3. Coincidencia por partes del slug
    4. Coincidencia por palabras clave del título
    5. Búsqueda difusa para casos especiales
    """
    slug_parts = slug.split('-')
    slug_normalized = slug.replace('-', '_')

    # Lista de posibles patrones a buscar (estrategias 1-3)
    patterns = [
        # Patrón directo: el slug completo en el nombre
        lambda name: slug in name.lower(),
        # Patrón con guiones bajos
        lambda name: slug_normalized in name.lower().replace('-', '_'),
        # Patrón con "badge": slug seguido o precedido por "badge"
        lambda name: f"{slug}-badge" in name.lower() or f"badge-{slug}" in name.lower(),
        # Patrón con "piezas": común en los badges de Platzi
        lambda name: f"piezas-{slug}" in name.lower(),
        # Patrón con partes del slug (al menos 2 partes consecutivas para slugs compuestos)
        lambda name: len(slug_parts) >= 2 and any(
            f"{slug_parts[i]}-{slug_parts[i+1]}" in name.lower()
            for i in range(len(slug_parts) - 1)
        ),
    ]

    # Buscar en todos los archivos de la carpeta
    for badge_file in badges_dir.glob('*.png'):
        name_lower = badge_file.name.lower()
        for pattern in patterns:
            try:
                if pattern(name_lower):
                    return badge_file
            except:
                continue

    # Estrategia 4: Búsqueda por palabras clave del título
    if course_title:
        title_normalized = normalize_text(course_title)
        # Extraer palabras clave (remover prefijos comunes)
        title_keywords = re.sub(
            r'^(curso|audiocurso|taller)\s+(de|básico|profesional|avanzado|práctico|introducción|intro)\s+',
            '',
            title_normalized
        )
        title_words = set(title_keywords.split())
        title_words -= {'curso', 'de', 'la', 'las', 'los', 'el', 'un', 'una', 'con', 'para', 'y', 'en'}

        for badge_file in badges_dir.glob('*.png'):
            name_lower = badge_file.name.lower().replace('.png', '')
            # Contar cuántas palabras clave coinciden
            matches = sum(1 for word in title_words if word in name_lower and len(word) > 3)
            if matches >= 2:  # Al menos 2 palabras coinciden
                return badge_file

    # Estrategia 5: Búsqueda difusa para casos especiales
    # Mapeo de términos comunes a patrones en nombres de archivo
    keyword_mappings = {
        'gestion-tiempo': ['gestion', 'tiempo', 'management'],
        'microsoft-teams': ['teams', 'microsoft'],
        'teletrabajo': ['teletrabajo', 'remoto', 'remote', 'trabajo'],
        'colaboracion': ['colaboracion', 'collaboration', 'corporaciones', 'startups'],
        'encontrar-evaluar-ideas': ['ideas', 'emprender', 'emprendimiento'],
    }

    for keyword, patterns in keyword_mappings.items():
        if keyword in slug or any(p in slug for p in patterns):
            for badge_file in badges_dir.glob('*.png'):
                name_lower = badge_file.name.lower()
                if any(pattern in name_lower for pattern in patterns):
                    return badge_file

    return None


def copy_badge(source: Path, dest_dir: Path, slug: str) -> bool:
    """Copia un badge a la carpeta de destino con el nombre del slug."""
    try:
        dest = dest_dir / f"{slug}.png"
        shutil.copy2(source, dest)
        return True
    except Exception as e:
        print(f"  Error copiando {source.name}: {e}")
        return False


def main():
    # Rutas base
    base_dir = Path(__file__).parent
    data_dir = base_dir / 'data'
    catalog_path = data_dir / 'catalog.json'
    base_badges_dir = data_dir / 'assetmadre' / 'base badges'
    badges_files_dir = base_badges_dir / 'Cursos Online de Programación, IA, Marketing, Inglés _ Platzi_files'
    dest_badges_dir = data_dir / 'assetmadre' / 'badges'

    # Asegurar que la carpeta de destino exista
    dest_badges_dir.mkdir(parents=True, exist_ok=True)

    print("="*60)
    print("CARGANDO CATÁLOGO DE CURSOS...")
    print("="*60)
    courses = load_catalog(catalog_path)
    print(f"Encontrados {len(courses)} cursos únicos en el catálogo\n")

    # Contadores
    copied = 0
    not_found = []
    already_exists = 0

    print("="*60)
    print("BUSCANDO Y COPIANDO BADGES...")
    print("="*60)
    print()

    for slug, title in courses:
        dest_path = dest_badges_dir / f"{slug}.png"

        # Verificar si ya existe
        if dest_path.exists():
            already_exists += 1
            continue

        # Buscar el badge usando el slug y el título para mejor precisión
        badge_source = find_badge_for_slug(slug, badges_files_dir, title)

        if badge_source:
            if copy_badge(badge_source, dest_badges_dir, slug):
                print(f"✓ {slug}")
                copied += 1
        else:
            not_found.append(slug)
            print(f"✗ {slug}")

    # Resumen
    print("\n" + "="*60)
    print("RESUMEN:")
    print(f"  - Copiados: {copied}")
    print(f"  - Ya existían: {already_exists}")
    print(f"  - No encontrados: {len(not_found)}")
    print(f"  - Total procesados: {len(courses)}")

    if not_found:
        print("\n" + "="*60)
        print("CURSOS SIN BADGE:")
        for slug in not_found:
            print(f"  - {slug}")

        # Guardar lista de no encontrados
        not_found_path = base_dir / 'badges_not_found.txt'
        with open(not_found_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(not_found))
        print(f"\nLista guardada en: {not_found_path}")


if __name__ == '__main__':
    main()
