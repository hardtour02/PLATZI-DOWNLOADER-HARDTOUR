# Implementation Plan - Platzi Downloader

## Cambios Recientes

### 2026-03-28 - Vista de Detalle de Curso por URL

**Objetivo:** Reemplazar el modal popup del syllabus por una vista completa navegable por URL.

**Tareas:**
- [x] Crear nueva vista `#curso/:slug` en el frontend
- [x] Modificar `openSyllabus()` para navegar en lugar de abrir modal
- [x] Agregar sidebar dinámico con botón "Volver al catálogo"
- [x] Manejar hash routing en el frontend

**Archivos modificados:**
- `frontend/index.html` - Vista de curso y navegación

**Cambios realizados:**
1. Nueva sección `#view-curso` con header (logo, título, metadata) y botón "Volver"
2. Función `cargarVistaCurso(slug)` que carga el syllabus desde API
3. Función `handleHashRoute()` para manejar rutas `#curso/:slug`
4. Event listener `hashchange` para navegación SPA
5. `renderSyllabusDetails()` actualizado para usar nuevo contenedor
6. Modal `syllabusModal` permanece como fallback

### 2026-03-28 - Verificación de Syllabus Completos

**Resultado:**
- Total cursos (con duplicados): 1946
- Cursos únicos: 1094
- Duplicados: 852
- Con syllabus: 1094 (100%)
- Faltantes: 0

**Archivos creados:**
- `scripts/syllabus_crawler_faltantes.py` - Script para scrapear solo cursos sin syllabus
- `scripts/check_faltantes.py` - Script de verificación

### 2026-03-28 - Re-crawleo de Cursos Vacíos (Escuela Ciberseguridad)

**Problema detectado:** Curso "Ciberseguridad Preventiva" mostraba "Syllabus no disponible" aunque existía en la BD.

**Causa:** 324 cursos tenían `total_lessons = 0` o `error = True` (scraping fallido originalmente).

**Solución:**
- Script `syllabus_crawler_rerun.py` para re-crawlear solo cursos vacíos/error
- Ejecutando en segundo plano (324 cursos por procesar)

**Archivos creados:**
- `scripts/syllabus_crawler_rerun.py` - Re-crawleo selectivo
- `scripts/check_ciber.py` - Verificador de escuela específica
- `scripts/check_ciber_curso.py` - Verificador de curso específico

---

## Plan Original

### Fase 1: Catálogo de Cursos
- [x] Scraping del catálogo de Platzi
- [x] Visualización de escuelas y rutas
- [x] Búsqueda y filtrado de cursos
- [x] Vista de detalle de curso (syllabus completo)

### Fase 2: Descarga de Contenido
- [x] Descarga de videos desde Platzi
- [x] Progreso en tiempo real
- [x] Historial de descargas
- [ ] Reanudación de descargas interrumpidas

### Fase 3: Sincronización Cloud
- [x] Integración con Google Drive
- [x] Subida de cursos descargados
- [x] Compartición de cursos vía email
- [ ] Sincronización automática

### Fase 4: Mejoras UX/UI
- [x] Navegación mejorada
- [ ] Responsive design
- [ ] Accesibilidad
