# CHANGELOG - PLATZI DOWNLOADER (HARDTOUR EDITION)

## v1.0.0 (Actual)
- Refactorización completa a arquitectura Senior Full Stack.
- Implementación de FastAPI con routers modulares.
- Soporte Offline-first: Assets (Tailwind, Lucide, Fuentes) localizados.
- Migración de base de datos de historial a rutas relativas para portabilidad.
- Organización de scripts de mantenimiento en `tools/maintenance/`.

## Historial de Versiones Anteriores (Resumen)

### v0.7.3
- Mejoras de compatibilidad en cabeceras HTTP.
- Actualización de documentación y contribuidores.

### v0.7.2
- Actualización de dependencias base.
- Mejoras en tipado estático (mypy).
- Formateo de código con Ruff.

### v0.7.1
- Corrección de selectores para mayor estabilidad ante cambios en el sitio.
- Refactorización de modelos de datos.

### v0.7.0
- Soporte para descarga de recursos adicionales y resúmenes.
- Selección de calidad de video (720p, etc.).
- Implementación de descarga de estilos remotos.

### v0.6.1
- Optimización de limpieza de strings.
- Mejoras en la gestión de nombres de archivos.

### v0.6.0
- Implementación de decorador de reintentos (retry) para descargas fallidas.
- Opción de sobreescritura de archivos existentes.

### v0.5.0
- Implementación de mecanismo de caché para respuestas de API.
- Comando CLI para limpiar caché.

### v0.4.0
- Integración de persistencia para sesiones de usuario.
- Mejoras en el modelo de Unidades.

### v0.3.0
- Soporte inicial para descarga de subtítulos (.vtt).

### v0.2.0
- Lanzamiento inicial del motor asíncrono con Playwright.
- Sistema de login/logout automatizado.
