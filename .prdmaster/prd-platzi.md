# PRD Maestro — PlatziPVP Suite
**Versión:** 1.0
**Fecha:** Abril 2026
**Tipo de producto:** Ecosistema Dual — App Desktop Local + Plataforma Web de Streaming
**Estado:** Aprobado

---

## RESUMEN EJECUTIVO

PlatziPVP Suite es un ecosistema dual compuesto por dos sistemas complementarios: una app de escritorio local (Sistema 1) que permite descargar, gestionar y reproducir cursos de Platzi offline con tracking de progreso, y una plataforma web independiente (Sistema 2) deployada en Vercel que permite visualizar en streaming los cursos subidos a Google Drive desde cualquier dispositivo. Ambos sistemas comparten identidad visual carbon-neon y el flujo completo es: descarga local → respaldo en Drive → acceso web universal. El Sistema 1 mejora la UI existente sin tocar el backend; el Sistema 2 es un producto nuevo con repositorio GitHub propio, CMS admin en Supabase y streaming directo desde Drive.

---

## 1. DEFINICIÓN DEL PRODUCTO

### 1.1 El Problema
Los estudiantes de Platzi que descargan contenido para uso offline carecen de una interfaz moderna que les permita gestionar su progreso de aprendizaje localmente. Paralelamente, no existe forma de acceder a ese contenido desde otros dispositivos ni compartirlo de forma organizada. El sistema actual funciona técnicamente pero presenta UI desactualizada, ausencia de tracking de progreso y ningún puente entre la biblioteca local y una experiencia web accesible desde cualquier dispositivo.

### 1.2 Usuarios Objetivo

**Perfil primario — Estudiante Descargador**
Técnico o profesional de 22–38 años, suscriptor activo de Platzi, trabaja en entornos con conectividad intermitente o quiere preservar su biblioteca de cursos. Nivel técnico medio-alto.
**Job-to-be-done:** "Cuando descargo un curso de Platzi, quiero saber exactamente qué lecciones he completado y poder retomarlo desde cualquier dispositivo para no perder mi progreso."

**Perfil secundario — Administrador / Empresa**
Responsable de capacitación que gestiona y comparte cursos descargados con su equipo.
**Job-to-be-done:** "Cuando subo cursos a Drive, quiero que aparezcan automáticamente en una web organizada para que mi equipo los consuma sin fricción."

### 1.3 Los Dos Sistemas

**SISTEMA 1 — PlatziPVP Desktop (Mejora UI)**
Rediseño de interfaz sin modificar backend ni rutas API. Dos módulos afectados:
- Módulo A: Catálogo rediseñado con UI moderna, glassmorphism, microinteracciones
- Módulo B: Dashboard "Mis Cursos" — galería plana transformada en dashboard de control con tracking de progreso, agrupación por escuela, buscador y estadísticas

**SISTEMA 2 — PlatziPVP Web (Nuevo producto)**
Plataforma web en Vercel con repositorio GitHub separado. Conectada a Google Drive. Incluye visualización de cursos por Escuela → Ruta → Curso → Lección, streaming desde Drive, CMS admin, sincronización automática Drive → Web, y **sistema de acceso controlado con registro via Google (Gmail)** donde el administrador gestiona la activación de usuarios.

### 1.4 Fuera del Scope (v1)
- No se modifican rutas de API ni lógica de scraping del Sistema 1
- No se migra la base de datos del Sistema 1 (sigue siendo JSON local)
- No hay sistema de comentarios ni foros en v1
- No se implementa DRM ni control de acceso por suscripción en v1
- El Sistema 2 no descarga contenido — solo visualiza desde Drive
- Solo un administrador en v1
- No se implementa caché de manifiestos Drive (Redis/Upstash) en v1
- No se soportan subtítulos (.vtt) en el reproductor web en v1

### 1.5 Diferencial Competitivo
PlatziPVP es el único sistema que cierra el ciclo completo: descarga local con tracking de progreso → respaldo en Drive → acceso web desde cualquier dispositivo, todo bajo una identidad visual cohesiva y sin depender de la disponibilidad de Platzi.

### 1.6 Métricas de Éxito

| Sistema | KPI | Objetivo |
|---|---|---|
| S1 — Dashboard | % lecciones con estado marcado | >80% de cursos con progreso registrado |
| S1 — Catálogo | Tiempo para encontrar y descargar | <30 segundos desde apertura |
| S2 — Web | Latencia Drive → Web | <5 minutos tras subida |
| S2 — Web | Accesibilidad multidispositivo | Funcional en móvil, tablet y desktop |

---

## 2. IDENTIDAD CORPORATIVA

### 2.1 Nombres por Sistema

| Producto | Nombre | Subtítulo |
|---|---|---|
| App Desktop | **PlatziPVP** | Video Downloader |
| Plataforma Web | **PlatziPVP Web** | Tu biblioteca online |
| Ecosistema | **PlatziPVP Suite** | Descarga. Organiza. Aprende. |

### 2.2 Taglines
- **Ecosistema:** "Descarga. Organiza. Aprende. Sin límites."
- **Sistema 1:** "Tu biblioteca Platzi, bajo tu control."
- **Sistema 2:** "Todo tu aprendizaje, desde cualquier pantalla."

### 2.3 Concepto de Marca
**Metáfora central:** PlatziPVP es la bóveda personal del conocimiento — un espacio blindado donde el estudiante es dueño absoluto de su contenido educativo, sin depender de conexiones, servidores externos ni restricciones de plataforma.

**Tres pilares:** Soberanía (el contenido descargado es tuyo) · Precisión (cada lección rastreada) · Fluidez (local → Drive → web sin fricción)

### 2.4 Archetype
**Rebelde + Experto** — Desafía la dependencia de plataformas cerradas con herramienta técnicamente impecable.

### 2.5 Personalidad
`Preciso` · `Oscuro` · `Confiable` · `Técnico` · `Fluido`

| Dimensión | Valor |
|---|---|
| Tono | Neutral con destellos técnicos |
| Energía | Sereno y eficiente |
| Carácter | Experto accesible |
| Registro | Técnico pero legible |

### 2.6 Voz de Comunicación
**✅ Sí decimos:**
- "Descargando 26 clases — 3 completadas, 23 en espera."
- "Tu biblioteca está sincronizada con Drive."
- "Catálogo actualizado — 147 nuevos cursos detectados."

**❌ No decimos:**
- "¡Genial! Tu descarga fue un éxito 🎉"
- "Estamos procesando tu solicitud, por favor espera..."
- Emojis decorativos en mensajes del sistema

### 2.7 Valores de Marca
1. **Soberanía Digital** — El contenido descargado es del usuario. Siempre.
2. **Precisión Operativa** — Cada acción produce resultado medible y rastreable.
3. **Portabilidad Total** — Local → Drive → web sin fricción entre entornos.

---

## 3. SISTEMA DE DISEÑO

### 3.1 Estilo Visual
**`carbon-neon`** — Dark mode profundo con acentos neón bicolor. Glassmorphism sutil. Tipografía técnica de alta legibilidad.

### 3.2 Paleta de Colores

| Token | HEX | Uso |
|---|---|---|
| `--color-bg` | `#0A0A0A` | Fondo base |
| `--color-surface-1` | `#111111` | Cards primer nivel |
| `--color-surface-2` | `#1A1A1A` | Cards segundo nivel, modales |
| `--color-surface-3` | `#222222` | Hover states, inputs |
| `--color-border` | `#2A2A2A` | Líneas divisoras |
| `--color-primary` | `#00F2A1` | CTAs, acento Platzi, activos |
| `--color-primary-dim` | `#00F2A120` | Fondos tinte primario |
| `--color-secondary` | `#38BDF8` | Sky blue, acciones secundarias |
| `--color-accent` | `#A78BFA` | Highlights, tags premium |
| `--color-success` | `#00F2A1` | Descarga completa, lección vista |
| `--color-error` | `#F87171` | Errores, fallos |
| `--color-warning` | `#FBBF24` | Advertencias, pendiente |
| `--text-primary` | `#F1F5F9` | Textos principales |
| `--text-secondary` | `#94A3B8` | Textos secundarios |
| `--text-muted` | `#475569` | Deshabilitados, placeholders |

### 3.3 Tipografía

| Uso | Fuente | Peso | Tamaño |
|---|---|---|---|
| Display / Hero | Space Grotesk | 700 | 48–64px |
| H1 | Space Grotesk | 700 | 32–40px |
| H2 | Space Grotesk | 600 | 24–28px |
| H3 | Space Grotesk | 600 | 18–20px |
| Body | Inter | 400 | 14–16px |
| Label / Button | Inter | 500–600 | 13–14px |
| Caption | Inter | 400 | 11–12px |
| Code | JetBrains Mono | 400 | 13px |

### 3.4 Espaciado (base 4px)

| Token | Valor | Uso |
|---|---|---|
| `--space-1` | 4px | Micro gaps |
| `--space-2` | 8px | Separación inline |
| `--space-4` | 16px | Padding base componentes |
| `--space-6` | 24px | Padding interno cards |
| `--space-8` | 32px | Separación entre secciones |
| `--space-12` | 48px | Secciones principales |
| `--space-16` | 64px | Hero sections |

### 3.5 Border Radius

| Token | Valor | Uso |
|---|---|---|
| `--radius-sm` | 6px | Badges, tags |
| `--radius-md` | 10px | Botones, inputs |
| `--radius-lg` | 14px | Cards, panels |
| `--radius-xl` | 20px | Modales, drawers |
| `--radius-2xl` | 28px | Cards grandes thumbnail |
| `--radius-full` | 9999px | Pills, avatares |

### 3.6 Efectos

```css
--shadow-md:      0 4px 16px rgba(0,0,0,0.5);
--glow-primary:   0 0 20px rgba(0, 242, 161, 0.25);
--glow-secondary: 0 0 20px rgba(56, 189, 248, 0.2);
--glass-bg:       rgba(255, 255, 255, 0.03);
--glass-border:   rgba(255, 255, 255, 0.06);
--glass-blur:     backdrop-filter: blur(12px);
```

### 3.7 Iconografía
**Librería:** Lucide Icons | Stroke: 1.5px | Tamaño base: 18px (nav), 16px (acciones)
**Badges de escuelas:** SVG propios del sistema — conservar como activo de identidad

### 3.8 Estados — Sistema de Badges

| Estado | Color | Fondo | Ícono |
|---|---|---|---|
| En Local & Drive | `#00F2A1` | dim green | CheckCircle2 |
| Pendiente | `#94A3B8` | dim slate | Clock |
| Descargando | `#38BDF8` | dim blue | UploadCloud |
| Solo en Nube | `#FBBF24` | dim yellow | Cloud |
| Error | `#F87171` | dim red | AlertCircle |

---

## 4. FLUJO UX

### 4.1 Roles de Usuario

| Rol | Sistema | Permisos | Entrada |
|---|---|---|---|
| `usuario_local` | S1 | Descargar, reproducir, sync Drive | `/catalogo` |
| `admin_web` | S2 | CMS completo, publicar cursos, gestionar usuarios | `/admin/login` |
| `visitante_web` | S2 | Ver catálogo, reproducir lecciones (requiere registro Gmail + cuenta activa) | `/login` |
| `visitante_pendiente` | S2 | Ninguno — pantalla de espera de activación | `/pending` |

### 4.2 SISTEMA 1 — Flujos Principales

#### Flujo 1A — Exploración y Descarga
```
[Catálogo Escuelas] → click escuela → [Rutas]
  → click ruta → [Grid Cursos]
    → click DESCARGAR → [Modal confirmación]
      → confirmar → [Pantalla Descargar]
        → progreso tiempo real → LISTO ✓ → aparece en [Mis Cursos]
    → click 👁 → [Detalle Curso / Syllabus]
```

#### Flujo 1B — Dashboard Mis Cursos
```
[Dashboard] → métricas + grid agrupado por escuela
  → click card curso → [Vista Detalle — Modo Aprendizaje]
    → listado secciones + lecciones con checkbox
    → click lección → [Reproductor Modal]
      → video se reproduce
      → al 80% duración → marcar automáticamente
      → botones Anterior | Siguiente
      → al completar curso → badge COMPLETADO
```

#### Flujo 1C — Sincronización Drive
```
[Dashboard] → click Sincronizar en card
  → SI sin credenciales → [Mi Cuenta OAuth2]
  → SI credenciales ok → subida resumible
    → PENDIENTE → SUBIENDO → EN LOCAL & DRIVE
```

### 4.3 SISTEMA 2 — Flujos Principales

#### Flujo 2A — Registro y Acceso de Visitantes
```
[/login] → click "Continuar con Google" → Google OAuth consent
  → SI primera vez → crear profile con activo=false
    → [/pending] → "Tu cuenta está pendiente de activación"
    → Esperar activación del admin
  → SI ya registrado + activo=true → redirect a [Home]
  → SI ya registrado + activo=false → [/pending]
```

#### Flujo 2B — Navegación Autenticada (requiere cuenta activa)
```
[Home] → grid escuelas → [Vista Escuela]
  → grid rutas → [Vista Ruta]
    → lista cursos → [Vista Curso]
      → syllabus colapsable → click lección → [Reproductor Web]
        → video desde Drive + panel lateral lecciones
        → Anterior | Siguiente
```

#### Flujo 2C — CMS Admin
```
[/admin/login] → Supabase Auth (email+password) → [/admin/dashboard]
  → [/admin/cursos] → tabla cursos con estados
    → toggle Publicar/Despublicar | Editar metadatos
  → [/admin/usuarios] → tabla usuarios registrados
    → toggle Activar/Desactivar | Ver perfil | Buscar por email
  → [/admin/sync] → escanear Drive → nuevos cursos como BORRADOR
    → activar auto-sync cada 30 minutos
```

#### Flujo 2D — Gestión de Usuarios (Admin)
```
[/admin/usuarios] → tabla con avatar, nombre, email, fecha, estado
  → Filtros: Todos | Activos | Pendientes | Desactivados
  → click Activar → profile.activo=true + timestamp activado_en
  → click Desactivar → profile.activo=false
  → Usuario desactivado pierde acceso inmediatamente (middleware)
```

### 4.4 Mapa de Navegación

#### Sistema 1
```
/catalogo (default)
  /catalogo/[escuela]
    /catalogo/[escuela]/[ruta]
      /catalogo/[escuela]/[ruta]/[curso]
/descargar
/cursos
  /cursos/[curso] + Modal reproductor
/drive
/actividad (tabs: bitacora | envios-drive)
/mi-cuenta
```

#### Sistema 2
```
/login                              ← Registro/login con Google (Gmail)
/pending                            ← Cuenta pendiente de activación
/auth/callback                      ← OAuth callback handler
/ (Home — requiere auth + activo)   ← Protegido
  /escuelas/[escuela]/[ruta]/[curso]
    /watch/[curso]/[leccion]
/admin/login                        ← Login admin (email+password)
/admin/dashboard
/admin/cursos
  /admin/cursos/[curso]/editar
/admin/usuarios                     ← ⭐ Gestión de usuarios registrados
/admin/sync
```

### 4.5 Estados de Pantallas Clave

| Pantalla | Vacío | Error |
|---|---|---|
| Catálogo Escuelas | "Catálogo no cargado — presiona Actualizar" | "Error de conexión al scraper" |
| Mis Cursos | "Aún no tienes cursos — ve al Catálogo" + CTA | "Error al leer biblioteca local" |
| Descargar | Input esperando URL | "URL inválida o curso no encontrado" |
| Login Web | — | "Error de autenticación — intenta de nuevo" |
| Pending Web | "Tu cuenta está pendiente de activación por el administrador" | — |
| Home Web | "Biblioteca en construcción" | "Error de conexión" |
| Reproductor Web | — | "Video no disponible en Drive" |
| Admin Cursos | "No hay cursos — sincroniza primero" + CTA | "Error al conectar con Drive" |
| Admin Usuarios | "No hay usuarios registrados todavía" | "Error al cargar usuarios" |

---

## 5. COMPONENTES UI

### 5.1 Componentes Globales S1 (Desktop)

- **Sidebar fijo 180px:** Logo + Nav items + zona inferior (Mi Cuenta, Carpeta Local)
- **SearchBar:** width 380px, debounce 300ms, dropdown de resultados
- **Toast system:** fixed bottom-right, auto-dismiss 4000ms, stack máx 3
- **Skeleton loader:** shimmer 1.5s, formas: card | row | text | avatar
- **Empty state:** ícono 48px + título + descripción + CTA opcional

### 5.2 Componentes Globales S2 (Web)

- **TopBar sticky:** height 64px, backdrop-blur 12px, responsive → hamburger, avatar Google del usuario logueado + botón cerrar sesión
- **VideoPlayer:** ratio 16:9, source Drive embed, controls nativos v1
- **AdminTopBar:** nav Dashboard | Cursos | Usuarios | Sync | Ver web | Cerrar sesión
- **LoginCard:** botón "Continuar con Google" centrado, branding carbon-neon, ícono Google
- **PendingCard:** ícono reloj + mensaje "Cuenta pendiente" + email registrado + botón cerrar sesión

### 5.3 Pantallas y Layouts

#### S1 — Catálogo Escuelas (`/catalogo`)
```
Layout: Sidebar + Content full
Header: H1 + SearchBar 380px + Btn Actualizar
Grid: 4 cols, gap 20px, padding 32px
Componente: EscuelaCard
  → badge SVG 48px + nombre (SG 600 16px) + contador rutas
  → hover: border primary-dim + glow + flecha →
```

#### S1 — Dashboard Mis Cursos (`/cursos`) ⭐
```
Layout: Sidebar + Content full
Header: H1 + SearchBar local + Filtros dropdown
Stats Row: 4x StatCard (Total | Completados | En Progreso | GB disco)
Filtros rápidos: Todos | No iniciado | En progreso | Completado | Drive Sync
Acordeón por escuela: ícono + nombre + nº cursos + GB
  → expandido: grid 4 cols de CursoCardPro
CursoCardPro:
  → thumbnail 16:9 + overlay barra progreso
  → badge escuela + nombre + "X/Y lecciones" + ProgressBar 4px
  → footer: GB disco + badge estado + ícono Drive
```

#### S1 — Modo Aprendizaje (`/cursos/[slug]`)
```
Layout: Single col centrada, max 800px
Header: ← Volver + badge ícono 48px + nombre + metadata
Lista: Sección (caps, SG 600 13px) → LeccionRow
LeccionRow (h:56px):
  → checkbox circular + thumbnail 40x28 + título + duración
  → estado: VISTO (border-left 3px primary) |
            ACTIVO (bg primary-dim) | DEFAULT
  → hover: bg surface-2 + ícono play
```

#### S1 — Drive (`/drive`)
```
Layout: Sidebar + Content
Header: H1 italic + caption + Btn Sincronizar
Tabla: checkbox | curso | estado badge | fecha | acciones (4 íconos)
```

#### S2 — Home Web (`/`)
```
TopBar sticky
Hero: gradient radial primary-dim + H1 + stats row (escuelas/cursos/lecciones)
Grid escuelas: 4 cols desktop | 2 tablet | 1 mobile
```

#### S2 — Reproductor Web (`/watch/[curso]/[leccion]`)
```
TopBar: logo + nombre curso truncado + lección X de Y
Layout split: video area (flex-1) + panel lateral 320px
Panel: lista lecciones por sección, activa resaltada
Footer video: título lección + ← Anterior | Siguiente →
Mobile: columna única, panel bajo el video
```

#### S2 — Admin Cursos (`/admin/cursos`)
```
AdminTopBar
Header: H1 + SearchBar + Filtro escuela
Tabs: Todos | Publicados | Borrador | Ocultos
Tabla: thumb | nombre+escuela | lecciones | estado | acciones
AdminToggle: ON(primary) | OFF(surface-3) | loading(opacity 0.6)
```

#### S2 — Admin Usuarios (`/admin/usuarios`) ⭐
```
AdminTopBar
Header: H1 "Gestión de Usuarios" + SearchBar (email/nombre)
Stats Row: 3x StatCard (Total | Activos | Pendientes)
Filtros: Todos | Activos | Pendientes | Desactivados
Tabla: avatar Google 32px | nombre | email | fecha registro | estado badge | acciones
  → Acciones: Activar (btn primary) | Desactivar (btn error)
  → Estado badge: Activo(primary) | Pendiente(warning) | Desactivado(error)
```

### 5.4 Componentes Críticos

#### ProgressBar de Lección
```
Linear: h:4px, radius full, bg surface-3
Fill: 0% → invisible | 1–99% → secondary | 100% → primary
Animación: width 0→valor%, 600ms ease-out
Circular: 40px SVG dasharray para header de curso
```

#### CourseGroupAccordion
```
Header: chevron animado + ícono escuela + nombre + pill nº cursos + GB
Body: grid 4 cols CursoCardPro, padding 0 24px 24px
Animación: height 0→auto, 250ms ease
Default: primera escuela expandida, resto colapsadas
```

#### SyncButton
```
idle    → "Sincronizar con Drive" | RefreshCw | secondary outline
loading → "Sincronizando..." | spin | disabled
success → "Sincronizado ✓" | CheckCircle2 | primary | 2s → idle
error   → "Error — Reintentar" | AlertCircle | error outline
```

#### VideoPlayer Web
```
Ratio 16:9 | bg #000 | radius --radius-xl
Source: Drive embed iframe
Loading: spinner centrado primary
Error: AlertCircle + "Video no disponible" + link Drive
Mobile: 100vw, sin radius
```

#### AdminToggle
```
44x24px | radius full
ON: bg primary + thumb white derecha
OFF: bg surface-3 + thumb white izquierda
Transición: 200ms | loading: thumb animado + opacity 0.6
```

---

## 6. LÓGICA DE NEGOCIO

### 6.1 Módulos del Sistema

| Módulo | Sistema | Responsabilidad |
|---|---|---|
| CATALOG | S1 | Lectura y navegación catálogo local |
| DOWNLOAD | S1 | Gestión de descargas y cola |
| PROGRESS | S1 | Tracking de lecciones y progreso |
| LIBRARY | S1 | Gestión de biblioteca local |
| SYNC_DRIVE | S1+S2 | Sincronización con Google Drive |
| AUTH | S2 | Autenticación admin via Supabase |
| CMS | S2 | Gestión de cursos publicados |
| STREAMING | S2 | Resolución de URLs de video desde Drive |
| SEARCH | S1+S2 | Búsqueda y filtrado |

### 6.2 Funciones Principales

#### MÓDULO CATALOG
```
obtener_escuelas() → Lista<Escuela>
  1. Leer data/catalog.json
  2. SI no existe → Error("CATALOG_NOT_FOUND")
  3. Parsear → extraer escuelas con id, nombre, slug, ícono, total_rutas
  4. Ordenar alfabéticamente
  RETORNA: Lista ordenada de escuelas

obtener_cursos_de_ruta(escuela_slug, ruta_slug) → Lista<Curso>
  1. Buscar escuela y ruta por slug
  2. Enriquecer cada curso con estado_descarga + has_thumbnail + lecciones_count
  RETORNA: Lista de cursos enriquecida

buscar_en_catalogo(query, filtros) → Lista<Resultado>
  1. Normalizar query (lowercase + trim + sin tildes)
  2. Calcular score por coincidencia: exacta(+100) | contiene(+50) | descripción(+20)
  3. Filtrar score > 0, ordenar desc, limitar a 20
  RETORNA: Lista de resultados por relevancia
```

#### MÓDULO DOWNLOAD
```
iniciar_descarga(url_curso) → JobDescarga
  1. Validar URL formato platzi.com/cursos/[slug]/
  2. Verificar no existe descarga activa del mismo curso
  3. Lanzar scraper Playwright → extraer metadatos + syllabus
  4. Crear estructura carpetas: data/courses/[slug]/
  5. Crear JobDescarga con UUID, emitir evento SSE
  RETORNA: JobDescarga con id y estado inicial

descargar_leccion(job_id, leccion) → ResultadoDescarga
  1. Smart resume: SI archivo existe con tamaño correcto → SKIP
  2. Detectar tipo: m3u8 → VIDEO | texto → LECTURA
  3. VIDEO: FFmpeg → fragmentar → merge → .mp4
     LECTURA: snapshot .mhtml
  4. Descargar subtítulos y materiales adjuntos
  5. Actualizar job + emitir SSE progreso
  ERROR: red falla → reintentar x3 con backoff | FFmpeg parcial → guardar punto de corte
```

#### MÓDULO PROGRESS
```
marcar_leccion(curso_slug, leccion_id, visto) → Confirmacion
  1. Leer/crear data/progress/[curso_slug].json
  2. Actualizar lecciones[leccion_id] = { visto, marcado_en, tipo_marcado }
  3. Recalcular porcentaje
  4. SI porcentaje==100 → agregar completado_en
  RETORNA: { porcentaje_nuevo, vistas, total }

marcar_automatico_por_tiempo(curso_slug, leccion_id, pct_reproducido)
  SI pct_reproducido >= 80 → marcar_leccion(visto=true, tipo="automatico")
  REGLA R001: NUNCA desmarcar automáticamente lo marcado manualmente

obtener_progreso_dashboard() → ResumenProgreso
  1. Leer todos data/progress/ + biblioteca local
  2. Calcular estado por curso: no_iniciado | en_progreso | completado
  3. Agrupar por escuela usando catálogo local
  4. Calcular métricas globales
  RETORNA: { metricas, por_escuela }
```

#### MÓDULO SYNC_DRIVE
```
sincronizar_curso_a_drive(curso_slug, credenciales) → ResultadoSync
  1. Verificar/crear estructura Drive: PlatziPVP/[Escuela]/[Ruta]/[Curso]/
  2. Por cada archivo: verificar si existe por nombre + tamaño
  3. SI no existe o tamaño diferente → subida resumible en chunks 256KB
  4. Guardar upload_uri para retomar si falla
  5. Actualizar downloads.json: drive_synced=true, folder_id, synced_at
  ERROR: token expirado → refresh | sin espacio → Error("DRIVE_QUOTA_EXCEEDED")

compartir_curso_drive(folder_id, email_destino) → Confirmacion
  1. Validar email formato
  2. Drive API: crear permiso tipo "user", rol "reader"
  3. Guardar en data/drive_shares.json
  REGLA: SI ya tiene acceso → Error("ALREADY_SHARED")
```

#### MÓDULO AUTH (S2)
```
registrar_visitante_google() → Sesion | Redirect
  1. Iniciar flujo OAuth con Supabase Auth (provider: Google)
  2. Google retorna nombre, email, avatar_url
  3. Trigger auto-crear profile con:
     role='viewer', activo=false, nombre, avatar_url
  4. SI profile.activo=false → redirect /pending
  5. SI profile.activo=true → redirect /
  REGLA R009: Nuevos registros SIEMPRE inician con activo=false

verificar_sesion_visitante(request) → Boolean
  1. Extraer token de cookie
  2. Supabase Auth: getUser(token)
  3. Verificar profile.activo=true
  SI no autenticado → redirect /login
  SI autenticado + activo=false → redirect /pending
  REGLA R010: toda ruta pública /* ejecuta esto PRIMERO

login_admin(email, password) → Sesion
  1. Supabase Auth: signInWithPassword
  2. Verificar rol "admin" en tabla profiles
  3. Guardar session en cookie httpOnly
  REGLA R002: 5 intentos fallidos → bloquear IP 15 minutos

verificar_sesion_admin(request) → Boolean
  1. Extraer token de cookie
  2. Supabase Auth: getUser(token)
  3. Verificar rol admin en profiles
  REGLA R002: toda ruta /admin/* ejecuta esto PRIMERO
```

#### MÓDULO USUARIOS (S2) ⭐
```
listar_usuarios(filtro, pagina) → Lista<Profile>
  1. Query profiles JOIN auth.users
  2. Filtrar por estado: todos | activos | pendientes | desactivados
  3. Ordenar por creado_en DESC
  4. Paginar 20 por página
  RETORNA: { usuarios, total, pagina, total_paginas }

activar_usuario(user_id) → Confirmacion
  1. Verificar sesión admin (R002)
  2. Update profiles SET activo=true, activado_en=now()
  RETORNA: { success, mensaje: "Usuario activado" }

desactivar_usuario(user_id) → Confirmacion
  1. Verificar sesión admin (R002)
  2. Update profiles SET activo=false
  3. Usuario pierde acceso inmediatamente (middleware verifica en cada request)
  REGLA: No se puede desactivar a otro admin
  RETORNA: { success, mensaje: "Usuario desactivado" }

obtener_stats_usuarios() → Stats
  1. COUNT total profiles WHERE role='viewer'
  2. COUNT activos WHERE activo=true
  3. COUNT pendientes WHERE activo=false AND activado_en IS NULL
  4. COUNT desactivados WHERE activo=false AND activado_en IS NOT NULL
  RETORNA: { total, activos, pendientes, desactivados }
```

#### MÓDULO CMS (S2)
```
sincronizar_drive_a_cms() → ResultadoSync
  1. Listar carpetas PlatziPVP/ en Drive (Escuela/Ruta/Curso/Lección)
  2. Por cada curso: verificar/crear registro en Supabase estado "borrador"
  3. Por cada lección: verificar/crear con drive_file_id
  REGLA R007: auto-sync cada 30min, mínimo 5min entre syncs

publicar_curso(curso_id) → Confirmacion
  1. Verificar curso tiene lecciones con drive_file_id
  2. Actualizar estado → "publicado", publicado_en: timestamp
  REGLA R006: estado borrador/oculto → no visible en web pública
```

#### MÓDULO STREAMING (S2)
```
resolver_url_video(leccion_id) → UrlVideo
  1. Obtener drive_file_id de Supabase
  2. Construir URL embed: drive.google.com/file/d/[id]/preview
  3. Verificar accesibilidad con HEAD request
  REGLA R003: usar SIEMPRE embed (no direct) en reproductor
  ERROR: archivo eliminado → marcar lección "no_disponible"

obtener_siguiente_leccion(curso_id, leccion_actual_id) → Leccion|Null
  1. Obtener lecciones ordenadas por seccion_orden + leccion_orden
  2. Retornar índice+1 o null si es la última
```

### 6.3 Reglas de Negocio

| ID | Nombre | Condición | Acción | Excepción |
|---|---|---|---|---|
| R001 | Protección marcado manual | Usuario marca lección manualmente | Sistema no puede desmarcar automáticamente | Usuario desmarca explícitamente |
| R002 | Protección rutas admin | Request llega a /admin/* | Verificar sesión admin PRIMERO | /admin/login es pública |
| R003 | URL embed streaming | Resolución de video en web | Usar formato embed Drive | Admin configura modo direct |
| R004 | Smart Resume | Descarga de curso parcial | Omitir archivos con tamaño correcto | Usuario fuerza re-descarga |
| R005 | Integridad disco-JSON | Descarga completada | Actualizar disco Y JSON simultáneo | Error de disco → no actualizar JSON |
| R006 | Visibilidad web | Curso en borrador/oculto | No aparece en rutas públicas | /admin siempre lo ve |
| R007 | Auto-sync cooldown | Auto-sync Drive→Web activo | Ejecutar cada 30 minutos | Última sync hace <5min → skip |
| R008 | Agrupación sin escuela | Curso sin escuela en catálogo | Agrupar en "Sin clasificar" | — |
| R009 | Registro inactivo por defecto | Nuevo visitante se registra con Gmail | profile.activo=false hasta activación admin | — |
| R010 | Verificación acceso visitante | Request llega a ruta pública /* | Verificar auth + profile.activo=true | /login y /pending son públicas |
| R011 | Protección entre admins | Admin intenta desactivar otro admin | Bloquear la acción | — |

### 6.4 Integraciones Externas

| Servicio | Sistema | Propósito | Fallback |
|---|---|---|---|
| Google Drive API v3 | S1+S2 | Subir cursos + leer para streaming | Guardar upload_uri, retomar sesión siguiente |
| Google OAuth 2.0 | S2 | Registro/login visitantes con Gmail | Mostrar error en pantalla login |
| Supabase Auth | S2 | Autenticación admin + visitantes (Google provider) | Mantener en login si no responde |
| Supabase DB (PostgreSQL) | S2 | Persistencia cursos, lecciones, usuarios, CMS | Mostrar error, no ejecutar CMS |
| Playwright + Chromium | S1 | Scraping metadatos y syllabus Platzi | Error("SCRAPER_ERROR") + no crear carpeta |
| FFmpeg | S1 | Procesar video m3u8 → mp4 | Guardar segmentos parciales + punto de corte |

### 6.5 Esquema Base de Datos Supabase (S2)

```sql
-- Tabla cursos
cursos (
  id              UUID PK DEFAULT gen_random_uuid(),
  nombre          TEXT NOT NULL,
  slug            TEXT UNIQUE NOT NULL,
  escuela         TEXT,
  ruta            TEXT,
  descripcion     TEXT,
  nivel           TEXT CHECK (nivel IN ('basico','intermedio','avanzado')),
  drive_folder_id TEXT NOT NULL,
  thumbnail_url   TEXT,
  badge_url       TEXT,
  total_lecciones INTEGER DEFAULT 0,
  estado          TEXT DEFAULT 'borrador'
                  CHECK (estado IN ('borrador','publicado','oculto')),
  creado_en       TIMESTAMPTZ DEFAULT now(),
  publicado_en    TIMESTAMPTZ,
  actualizado_en  TIMESTAMPTZ
)

-- Tabla lecciones
lecciones (
  id              UUID PK DEFAULT gen_random_uuid(),
  curso_id        UUID FK → cursos.id ON DELETE CASCADE,
  nombre          TEXT NOT NULL,
  slug            TEXT NOT NULL,
  seccion_nombre  TEXT,
  seccion_orden   INTEGER,
  leccion_orden   INTEGER,
  drive_file_id   TEXT,
  duracion_seg    INTEGER,
  tipo            TEXT CHECK (tipo IN ('video','lectura')),
  estado          TEXT DEFAULT 'activa'
                  CHECK (estado IN ('activa','no_disponible')),
  creado_en       TIMESTAMPTZ DEFAULT now()
)

-- Tabla profiles (extiende auth.users) — con gestión de acceso
profiles (
  id           UUID PK FK → auth.users.id ON DELETE CASCADE,
  email        TEXT UNIQUE NOT NULL,
  nombre       TEXT,                                 -- Nombre de Google profile
  avatar_url   TEXT,                                 -- Foto de Google profile
  role         TEXT DEFAULT 'viewer'
               CHECK (role IN ('admin','viewer')),
  activo       BOOLEAN DEFAULT false,                -- false = pendiente de activación
  creado_en    TIMESTAMPTZ DEFAULT now(),
  activado_en  TIMESTAMPTZ                           -- timestamp cuando admin activa
)
-- NOTA: activo=false por defecto (R009). Admin activa manualmente.
-- Trigger on auth.users INSERT → auto-crear profile con datos de Google.

-- Tabla sync_logs
sync_logs (
  id              UUID PK DEFAULT gen_random_uuid(),
  ejecutado_en    TIMESTAMPTZ DEFAULT now(),
  cursos_nuevos   INTEGER DEFAULT 0,
  lecciones_nuevas INTEGER DEFAULT 0,
  errores         JSONB DEFAULT '[]',
  tipo            TEXT CHECK (tipo IN ('manual','automatico'))
)
```

---

## 7. ARQUITECTURA TÉCNICA

### 7.1 Sistema 1 — Stack (sin modificar backend)

```
Frontend:   HTML/JS nativo + Jinja2 + Tailwind CSS + Lucide Icons
Backend:    Python 3.10+ + FastAPI (routers modulares) — SIN CAMBIOS
Scraper:    Playwright (Chromium) — SIN CAMBIOS
Video:      FFmpeg — SIN CAMBIOS
Storage:    Sistema de archivos JSON local en data/
Drive:      Google Drive API v3 con OAuth2 resumible — SIN CAMBIOS
```

**Cambios v2 Sistema 1:**
- Reemplazar estilos CSS actuales por nuevo design system carbon-neon
- Agregar Space Grotesk + Inter desde Google Fonts
- Nuevo componente Dashboard en `/cursos` con lógica de progreso
- Nuevos endpoints FastAPI para progress tracking:
  - `GET /api/progress/{curso_slug}` → obtener progreso
  - `POST /api/progress/{curso_slug}/{leccion_id}` → marcar lección
  - `GET /api/progress/dashboard` → resumen completo

### 7.2 Sistema 2 — Stack nuevo

```
Framework:    Next.js 14 (App Router)
Estilos:      Tailwind CSS v3
Iconos:       Lucide React
Auth:         Supabase Auth (Google OAuth para visitantes, email+password para admin)
Database:     Supabase PostgreSQL
Drive:        Google Drive API v3 (scope: drive.readonly)
Deploy:       Vercel
Repo:         GitHub privado independiente (hardtour02/platzipvp-web)
```

### 7.3 Estructura de Carpetas S2

```
platzipvp-web/
├── app/
│   ├── (auth)/                            ← Rutas de autenticación visitante
│   │   ├── login/page.tsx                 ← "Continuar con Google"
│   │   └── pending/page.tsx               ← "Cuenta pendiente de activación"
│   ├── auth/callback/route.ts             ← OAuth callback handler
│   ├── (public)/                          ← Rutas protegidas (auth + activo)
│   │   ├── page.tsx                       ← Home
│   │   ├── escuelas/[escuela]/
│   │   │   └── [ruta]/[curso]/
│   │   └── watch/[curso]/[leccion]/
│   └── admin/
│       ├── login/page.tsx                 ← Login admin (email+password)
│       ├── dashboard/page.tsx
│       ├── cursos/page.tsx
│       ├── usuarios/page.tsx              ← ⭐ Gestión usuarios registrados
│       └── sync/page.tsx
├── components/
│   ├── ui/                                ← Componentes base
│   ├── catalog/                           ← EscuelaCard, CursoCard
│   ├── player/                            ← VideoPlayer, LessonPanel
│   └── admin/                             ← AdminTable, SyncPanel, UserTable
├── lib/
│   ├── supabase/                          ← cliente + tipos
│   ├── drive/                             ← Google Drive helpers
│   └── utils/
├── middleware.ts                           ← Auth guard (visitante + admin)
└── public/
    └── assets/                            ← badges y logos de escuelas
```

### 7.4 Variables de Entorno S2

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Google Drive (OAuth2)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=

# Config
NEXT_PUBLIC_APP_URL=https://platzipvp.vercel.app
DRIVE_ROOT_FOLDER_NAME=PlatziPVP
AUTO_SYNC_INTERVAL_MINUTES=30
```

### 7.5 Servicios Externos Requeridos

| Servicio | Plan mínimo | Uso |
|---|---|---|
| Supabase | Free tier | Auth + PostgreSQL |
| Vercel | Hobby (free) | Deploy Next.js S2 |
| Google Cloud Console | Free | Drive API credentials |
| Google Drive | Personal (15GB) | Almacenamiento cursos |

---

## 8. ROADMAP v1

| Feature | Sistema | Prioridad | Estimado | Dependencias |
|---|---|---|---|---|
| Rediseño Catálogo (UI) | S1 | P0 | 3 días | Design system |
| Dashboard Mis Cursos | S1 | P0 | 5 días | Progress API |
| Progress tracking API | S1 | P0 | 2 días | — |
| Reproductor con auto-mark | S1 | P1 | 2 días | Progress API |
| Setup Next.js + Supabase | S2 | P0 | 1 día | — |
| Auth visitantes (Google OAuth) | S2 | P0 | 2 días | Supabase setup + Google Cloud |
| Auth admin (email+password) | S2 | P0 | 1 día | Supabase setup |
| Gestión de usuarios (admin) | S2 | P0 | 2 días | Auth visitantes |
| Home + catálogo web (autenticado) | S2 | P0 | 4 días | Auth + DB schema |
| CMS admin — gestión cursos | S2 | P1 | 3 días | Auth admin |
| Sync Drive → Supabase | S2 | P0 | 3 días | Drive API creds |
| Reproductor web streaming | S2 | P0 | 2 días | Sync Drive |
| Auto-sync cada 30min | S2 | P2 | 1 día | Sync manual |
| Responsive mobile S2 | S2 | P1 | 2 días | Reproductor web |

---

## APÉNDICE

### A. Glosario

| Término | Definición |
|---|---|
| Asset Madre | Carpeta `data/assetmadre` con logos y thumbnails centralizados |
| Smart Resume | Omisión automática de archivos ya descargados con tamaño correcto |
| Carbon-neon | Nombre del estilo visual del ecosistema: dark mode + acentos neón |
| Drive Scope | Permisos de Google Drive: `drive.file` (S1) y `drive.readonly` (S2) |
| Slug | Versión URL-friendly del nombre de un curso o escuela |
| SSE | Server-Sent Events — mecanismo para progreso en tiempo real en S1 |
| Borrador | Estado inicial de un curso en el CMS S2, no visible en web pública |
| Cuenta Activa | Usuario visitante con `profile.activo=true`, puede acceder al contenido |
| Cuenta Pendiente | Usuario visitante registrado pero con `profile.activo=false`, esperando activación del admin |
| Google OAuth | Protocolo de autenticación usado para registro de visitantes via Gmail |

### B. Decisiones de Diseño y Justificación

1. **No modificar backend S1:** Reduce riesgo y tiempo — el backend funciona correctamente. Solo se actualiza la capa de presentación.
2. **JSON local para progreso S1:** Consistente con la arquitectura existente. No requiere DB externa, mantiene portabilidad total.
3. **Space Grotesk como display font:** Aporta personalidad técnica única con terminaciones geométricas — diferencia visualmente de Platzi que usa fuentes más redondeadas.
4. **Drive embed sobre direct URL:** Los embeds de Drive son más estables, no requieren tokens de acceso temporal y funcionan sin configuración adicional de CORS.
5. **Supabase como backend S2:** Provee Auth + PostgreSQL + API REST generada automáticamente en un solo servicio — reduce complejidad operacional para un proyecto de este tamaño.
6. **Repositorio S2 independiente:** Permite deployar, versionar y escalar el Sistema 2 sin acoplamiento al Sistema 1. Facilita colaboración y CI/CD separados.
7. **Registro con Google (Gmail) obligatorio:** Permite control total de quién accede al contenido. El admin activa manualmente cada usuario, garantizando acceso solo a personas autorizadas.
8. **Cuenta inactiva por defecto (R009):** Modelo de seguridad opt-in — nadie accede sin autorización explícita del administrador.

### C. Preguntas Resueltas

| # | Pregunta | Resolución |
|---|---|---|
| 1 | ¿Acceso público o autenticación? | **Autenticación obligatoria** via Google OAuth (Gmail). Admin activa cuentas manualmente. |
| 2 | ¿Múltiples admins o uno solo? | **Un solo admin** en v1. |
| 3 | ¿Badges de S1 se migran a S2? | **Sí**, como assets estáticos en `public/assets/badges/`. |
| 4 | ¿Caché de manifiestos Drive? | **No** en v1. Se evaluará Redis/Upstash en v2. |
| 5 | ¿Subtítulos .vtt en reproductor web? | **No** en v1. |
