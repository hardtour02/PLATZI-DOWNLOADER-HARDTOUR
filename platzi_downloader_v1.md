# Documento de Contexto: Platzi Downloader (HARDTOUR Edition)

Este documento detalla el estado actual, arquitectura y funcionalidades del proyecto Platzi Downloader, sirviendo como base técnica para la reconstrucción y mejora del producto (PRD Maestro).

---

## 1. Propósito del Producto
*   **Propósito:** Herramienta profesional "Offline-first" para la descarga, gestión y respaldo de cursos de Platzi.
*   **Problema que resuelve:** Falta de acceso offline fluido y gestión centralizada de contenidos educativos en entornos de baja conectividad o para preservación de activos digitales.
*   **Público objetivo:** Estudiantes de Platzi que requieren portabilidad total, empresas que respaldan capacitación y usuarios avanzados que desean integrar sus cursos con clouds personales (Google Drive).

## 2. Pantallas y Vistas (Arquitectura SPA)
1.  **Catálogo:** Explorador jerárquico (Escuelas -> Rutas -> Cursos) basado en un scraping estructural v2. Permite búsqueda global e inmersión en la oferta educativa local/remota.
2.  **Descargar:** Interfaz operativa para pegar URLs directas y monitorear el progreso de descarga en tiempo real (m3u8, lecturas, recursos y subtítulos).
3.  **Detalle de Curso:** Vista del syllabus completo con metadatos (duración, autor, nivel) y estado de descarga de cada lección.
4.  **Mis Cursos (Biblioteca):** Galería local de cursos descargados. Incluye filtros por categoría, búsqueda local y acciones rápidas (reproducir, abrir carpeta).
5.  **Sincronización Cloud (Drive):** Panel de gestión para espejar la biblioteca local en Google Drive, con control de permisos y estados de subida.
6.  **Actividad / Registro:** Bitácora detallada de eventos del sistema (éxitos, errores, advertencias) e historial de correos con los que se ha compartido contenido en Drive.
7.  **Mi Cuenta:** Gestión de credenciales para Platzi (Scraper) y Google (OAuth2).
8.  **Reproductor Integrado:** Modal con soporte para video local, selección de lecciones y visualización de recursos adjuntos.

## 3. Flujos del Usuario
*   **Descarga por URL:** Pegar URL -> Scraping de Metadatos -> Generación de Carpeta -> Descarga Secuencial (Video + Subs + Assets) -> Registro en Historial.
*   **Exploración de Catálogo:** Navegar Escuelas -> Seleccionar Ruta -> Ver Syllabus -> Iniciar Descarga desde el catálogo.
*   **Respaldo Cloud:** Seleccionar curso -> Elegir "Sincronizar con Drive" -> Subida Resumible -> (Opcional) Compartir carpeta vía email.
*   **Uso Offline:** Abrir biblioteca -> Buscar curso -> Lanzar reproductor local (totalmente offline).

## 4. Lógica de Negocio y Reglas Críticas
*   **Asset Madre:** Centralización de logos y thumbnails en `data/assetmadre` para evitar redundancias y garantizar estética premium offline.
*   **Integridad Dual:** Verificación constante de concordancia entre el disco físico y los registros JSON (`data/downloads.json`).
*   **Smart Resume:** Omisión automática de segmentos o archivos ya existentes/completos para optimizar tiempo y ancho de banda.
*   **Portabilidad Estricta:** Uso de rutas relativas y normalización de nombres (slugify) para compatibilidad multiplataforma.
*   **Captura de Contenido:** Diferenciación inteligente entre formatos de video (m3u8) y contenido de texto/clases (snapshots .mhtml).

## 5. Stack Tecnológico
*   **Backend:** Python 3.10+ con **FastAPI** (routers modulares).
*   **Scraper:** **Playwright** (Chromium) + **FFmpeg** (Procesamiento de video).
*   **Frontend:** HTML/JS Nativo + **Jinja2** + **Tailwind CSS** + **Lucide Icons**.
*   **Almacenamiento:** Sistema de archivos JSON (NoSQL local) en la carpeta `data/`.
*   **Integraciones:** Google Drive API v3 (con OAuth2 resumible).

## 6. Identidad Visual
*   **Estética:** Modern Dark Mode (Carbon Slate).
*   **Paleta:** Fondo `#121212`, Tarjetas `#1a1a1a`, Acentos Verde Platzi (`#00f2a1`) y Sky Blue (`sky-400`).
*   **UX:** Uso extensivo de glassmorphism, micro-animaciones (hover, pulses) y bordes redondeados (3xl).

## 7. Análisis de Estado (Diagnóstico)
### ✅ Lo que funciona (Conservar)
*   **Portabilidad:** Estructura de carpetas modular y autocontenida.
*   **Identidad Visual:** Diseño robusto y profesional (PlatziPVP Style).
*   **Sincronización Drive:** Lógica de permisos y mirroring de folders estable.
*   **Estructura de Rutas Unificada:** Estandarización de `data/courses/` para todas las operaciones del sistema, eliminando duplicidad.


### ❌ Lo que está roto/incompleto
*   **Resunción de Video:** Fragmentación de segmentos si falla FFmpeg a mitad del proceso.
*   **Responsive Design:** La interfaz se rompe en resoluciones móviles/tablet.


### 🚀 Oportunidades (Faltantes)
*   **Auto-Sync Nube:** Automatización de respaldos sin intervención del usuario.
*   **Virtual Scrolling:** Optimización del DOM para catálogos masivos (+1000 cursos).
*   **Gestor de Almacenamiento:** Estadísticas de espacio en disco y limpieza automática.
*   **Soporte Multicuenta:** Perfiles de usuario para el scraper.

---
**Fecha de Análisis:** 06 de Abril, 2026
**Autor:** Antigravity AI Project Manager
