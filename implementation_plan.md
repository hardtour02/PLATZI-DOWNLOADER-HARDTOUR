# Implementation Plan — PlatziPVP Suite v1.0

**Última actualización:** 8 Abril 2026
**PRD de referencia:** `.prdmaster/prd-platzi.md` v1.0

---

## Estado Global del Proyecto

| Área | Progreso | Notas |
|---|---|---|
| Arquitectura y PRD | ✅ 100% | PRD Maestro aprobado, design system definido |
| Base de datos (Supabase) | ✅ 100% | 4 tablas, 11 policies, trigger, admin creado |
| Repositorios y Git | ✅ 100% | S1 + S2 repos configurados, branches, PRs integrados |
| Backend S1 (Progress API) | ✅ 100% | 3 endpoints integrados en main.py |
| Backend S2 (Sync + Cron) | ✅ 100% | API sync, cron route, vercel.json |
| Config base S2 (Tailwind/Supabase) | ✅ 100% | globals.css, tailwind tokens, types.ts |
| Middleware Auth S2 | ✅ 100% | Protección /admin/* |
| **Frontend S1 (Rediseño UI)** | ✅ 100% | **COMPLETADO — Integrado CSS y Jinja components** |
| **Frontend S2 (Componentes UI)** | ✅ 100% | **COMPLETADO — UI elements en Nextjs** |
| **Frontend S2 (Páginas)** | ✅ 100% | **COMPLETADO — Todas las páginas conectadas a supabase** |
| **Auth S2 (Google OAuth flow)** | ✅ 100% | **COMPLETADO — Callback y middleware robusto** |
| **Admin S2 (Páginas CMS)** | ✅ 100% | **COMPLETADO — Sync panel y Dashboard listos** |
| Deploy Vercel | ❌ 0% | Esperando deploy manual en Vercel |

---

## LO QUE YA ESTÁ HECHO (no tocar)

### Infraestructura Supabase (proyecto: `sqegdibogfonfnelunml`)
- [x] Tablas: `cursos`, `lecciones`, `profiles`, `sync_logs`
- [x] RLS habilitado + 11 policies (visitante activo, admin, service_role)
- [x] Trigger `on_auth_user_created` → auto-crear profile desde Google OAuth
- [x] 8 índices de performance
- [x] Usuario admin creado: `koinumamusic@gmail.com` (role=admin, activo=true)

### Repositorio S1 (`hardtour02/PLATZI-DOWNLOADER-HARDTOUR`)
- [x] `backend/app/api/progress.py` — 3 endpoints (R001 implementada)
- [x] `backend/app/main.py` — progress_router registrado
- [x] PR #1 mergeado a main

### Repositorio S2 (`hardtour02/platzipvp-web`)
- [x] `app/globals.css` — Variables CSS carbon-neon + Google Fonts
- [x] `tailwind.config.ts` — Tokens mapeados a CSS vars
- [x] `lib/supabase/client.ts` — createBrowserClient
- [x] `lib/supabase/types.ts` — Tipos TS del schema completo
- [x] `app/api/admin/sync/route.ts` — Sync Drive→Supabase con R007
- [x] `app/api/cron/sync/route.ts` — Vercel Cron con CRON_SECRET
- [x] `vercel.json` — Cron cada 30 min
- [x] `middleware.ts` — Protección /admin/* (excepto /admin/login)
- [x] `package.json` — Deps: next, supabase-js, lucide-react, clsx, tailwind-merge
- [x] PRs #1 y #2 mergeados a develop
- [x] Estructura de carpetas completa (placeholders)

---

## LO QUE FALTA (en orden de ejecución)

### FASE 1 — Frontend S2: Componentes UI Base
**Branch:** `feature/s2-public-web` (crear desde develop)
**Estimado:** 3 días | **Prioridad:** P0

#### Tarea 1.1 — Utilidades y componentes base (`components/ui/`)
- [ ] `lib/utils.ts` — función `cn()` usando clsx + tailwind-merge
- [ ] `components/ui/Badge.tsx` — variantes: success, pending, warning, error, info
- [ ] `components/ui/StatCard.tsx` — label muted + valor grande SG + sub-label colored
- [ ] `components/ui/ProgressBar.tsx` — linear h prop, color dinámico (0%→transparent, 1-99%→secondary, 100%→primary)
- [ ] `components/ui/Spinner.tsx` — centrado, color primary, tamaño prop
- [ ] `components/ui/EmptyState.tsx` — ícono Lucide + título + descripción + CTA opcional
- [ ] `components/ui/Skeleton.tsx` — shimmer 1.5s, variantes: card, row, text

#### Tarea 1.2 — Componentes de catálogo (`components/catalog/`)
- [ ] `components/catalog/EscuelaCard.tsx` — badge SVG 48px + nombre SG 600 + contador rutas + hover glow + flecha
- [ ] `components/catalog/CursoCard.tsx` — thumb 16:9 + badge nivel + nombre 2-line clamp + botón acción
- [ ] `components/catalog/LeccionRow.tsx` — h-14 + thumb 40×28 + título + duración JetBrains Mono + play icon on hover

#### Tarea 1.3 — Componentes de reproductor (`components/player/`)
- [ ] `components/player/VideoPlayer.tsx` — iframe Drive embed 16:9, loading spinner, error state AlertCircle
- [ ] `components/player/LessonPanel.tsx` — lista agrupada por sección, activa resaltada, scroll to active

#### Tarea 1.4 — Componentes admin (`components/admin/`)
- [ ] `components/admin/AdminTopBar.tsx` — nav: Dashboard, Cursos, Usuarios, Sync, Ver web, Cerrar sesión
- [ ] `components/admin/AdminToggle.tsx` — 44×24px ON(primary)/OFF(surface-3), loading state
- [ ] `components/admin/UserTable.tsx` — avatar 32px + nombre + email + fecha + estado badge + acciones

**Commit:** `feat(s2): componentes UI base carbon-neon`

---

### FASE 2 — Frontend S2: Auth (Google OAuth + Admin Login)
**Branch:** `feature/s2-public-web`
**Estimado:** 2 días | **Prioridad:** P0
**Dependencia:** Requiere configurar Google Provider en Supabase Dashboard

#### Tarea 2.1 — Supabase Server Client
- [ ] `lib/supabase/server.ts` — createServerClient usando cookies() de next/headers

#### Tarea 2.2 — Login Visitante (`app/(auth)/login/page.tsx`)
- [ ] Diseño: card centrada, logo PlatziPVP, botón "Continuar con Google"
- [ ] Lógica: `supabase.auth.signInWithOAuth({ provider: 'google' })`
- [ ] Si ya autenticado + activo → redirect `/`
- [ ] Si ya autenticado + no activo → redirect `/pending`

#### Tarea 2.3 — Callback OAuth (`app/auth/callback/route.ts`)
- [ ] Intercambiar code por session
- [ ] Verificar profile.activo
- [ ] Redirect: activo → `/` | inactivo → `/pending`

#### Tarea 2.4 — Pending Page (`app/(auth)/pending/page.tsx`)
- [ ] Diseño: ícono reloj + "Tu cuenta está pendiente de activación"
- [ ] Mostrar email registrado + avatar Google
- [ ] Botón "Cerrar sesión" → `supabase.auth.signOut()`

#### Tarea 2.5 — Admin Login (`app/admin/login/page.tsx`)
- [ ] Form: email + password, card surface-2, logo, max-w-[400px]
- [ ] `supabase.auth.signInWithPassword({ email, password })`
- [ ] Verificar rol admin en profiles → si no admin → signOut + error
- [ ] Si ok → redirect `/admin/dashboard`

#### Tarea 2.6 — Middleware completo (`middleware.ts`)
- [ ] Actualizar para proteger rutas públicas `(public)/*` → requiere auth + activo (R010)
- [ ] Mantener protección admin existente (R002)
- [ ] Excepciones: `/login`, `/pending`, `/auth/callback`

**Commit:** `feat(s2): flujo auth completo — Google OAuth + admin login`

---

### FASE 3 — Frontend S2: Páginas Públicas
**Branch:** `feature/s2-public-web`
**Estimado:** 4 días | **Prioridad:** P0

#### Tarea 3.1 — Layout público (`app/(public)/layout.tsx`)
- [ ] TopBar sticky 64px: logo PlatziPVP + nav + badge BETA + avatar usuario + logout
- [ ] Backdrop-blur 12px, responsive → hamburger en mobile

#### Tarea 3.2 — Home (`app/(public)/page.tsx`)
- [ ] Hero: gradient radial primary-dim, H1 "Tu biblioteca Platzi, desde cualquier pantalla"
- [ ] Stats row: COUNT escuelas, cursos publicados, lecciones (query Supabase server component)
- [ ] Grid escuelas: `SELECT DISTINCT escuela, COUNT(*) FROM cursos WHERE estado='publicado' GROUP BY escuela`
- [ ] Responsive: 4 cols desktop, 2 tablet, 1 mobile, gap 16px
- [ ] Loading: Suspense + Skeleton cards

#### Tarea 3.3 — Vista Curso (`app/(public)/escuelas/[escuela]/[ruta]/[curso]/page.tsx`)
- [ ] Query: `SELECT * FROM cursos WHERE slug=$curso AND estado='publicado'`
- [ ] Query: `SELECT * FROM lecciones WHERE curso_id=$id ORDER BY seccion_orden, leccion_orden`
- [ ] Header: thumbnail + título + escuela badge + nivel + total lecciones
- [ ] Acordeón de secciones colapsables por `seccion_nombre`
- [ ] LeccionRow con link a `/watch/[curso]/[leccion]`
- [ ] Error/Empty states

#### Tarea 3.4 — Reproductor (`app/(public)/watch/[curso]/[leccion]/page.tsx`)
- [ ] Query: `SELECT drive_file_id FROM lecciones WHERE slug=$leccion AND estado='activa'`
- [ ] Layout split (lg:flex-row, flex-col mobile):
  - Video área flex-1: iframe `drive.google.com/file/d/[id]/preview`, ratio 16:9, radius xl
  - Loading: spinner centrado
  - Error: AlertCircle + "Video no disponible" + enlace Drive
- [ ] Panel lateral 320px (drawer en mobile): lista lecciones por sección, activa resaltada
- [ ] Footer: título lección + [← Anterior] [Siguiente →] calculados por orden
- [ ] Responsive complete

**Commit:** `feat(s2): páginas públicas — home, curso, reproductor`

---

### FASE 4 — Frontend S2: Admin CMS
**Branch:** `feature/s2-admin-cms` (crear desde develop)
**Estimado:** 4 días | **Prioridad:** P1

#### Tarea 4.1 — Layout Admin (`app/admin/layout.tsx`)
- [ ] AdminTopBar con navegación: Dashboard, Cursos, Usuarios, Sync
- [ ] Sidebar o top nav responsive

#### Tarea 4.2 — Dashboard Admin (`app/admin/dashboard/page.tsx`)
- [ ] Stats: total cursos, publicados, borrador, total lecciones, total usuarios, users activos
- [ ] Último sync log
- [ ] Links rápidos a cada sección

#### Tarea 4.3 — Gestión Cursos (`app/admin/cursos/page.tsx`)
- [ ] Tabla: thumb + nombre + escuela + lecciones + estado + acciones
- [ ] Tabs: Todos | Publicados | Borrador | Ocultos
- [ ] Acciones: toggle publicar/despublicar (AdminToggle), editar metadatos
- [ ] SearchBar + filtro por escuela

#### Tarea 4.4 — Gestión Usuarios (`app/admin/usuarios/page.tsx`) ⭐
- [ ] Stats row: total, activos, pendientes, desactivados
- [ ] Filtros: Todos | Activos | Pendientes | Desactivados
- [ ] Tabla: avatar Google 32px + nombre + email + fecha + estado badge + acciones
- [ ] Acciones: Activar (btn primary) / Desactivar (btn error)
- [ ] R011: No desactivar a otro admin
- [ ] `app/admin/usuarios/actions.ts` — Server actions para activar/desactivar

#### Tarea 4.5 — Panel Sync (`app/admin/sync/page.tsx`)
- [ ] Botón Sync manual → POST /api/admin/sync
- [ ] SyncButton: idle/loading/success/error states
- [ ] Tabla sync_logs: fecha + cursos nuevos + lecciones + errores
- [ ] Indicador auto-sync cada 30 min

**Commit:** `feat(s2): admin CMS — dashboard, cursos, usuarios, sync`

---

### FASE 5 — Frontend S1: Rediseño UI Carbon-Neon
**Branch:** `feature/s1-catalog-redesign`
**Estimado:** 5 días | **Prioridad:** P0

#### Tarea 5.1 — Design System CSS
- [ ] `frontend/assets/carbon-neon.css` — Todas las CSS variables del PRD §3
- [ ] Importar Google Fonts: Space Grotesk 600,700 + Inter 400,500,600 + JetBrains Mono 400
- [ ] Actualizar `<head>` de `index.html` para cargar el nuevo CSS

#### Tarea 5.2 — Sidebar (180px)
- [ ] Reducir ancho de 240px a 180px
- [ ] Logo: "PLATZI" en primary bold + "PVP" en text-primary + "VIDEO DOWNLOADER" 10px muted
- [ ] Nav items gap 4px, padding 12px con Lucide 18px stroke 1.5:
  - Catálogo (LayoutGrid), Descargar (Download), Cursos (BookOpen), Drive (Cloud), Actividad (Activity)
- [ ] Activo: bg primary-dim + text primary + border-left 2px primary + radius md
- [ ] Inactivo: text secondary, hover bg surface-2
- [ ] Zona inferior: Mi Cuenta (User) + Carpeta Local (FolderOpen)
- [ ] Actualizar `margin-left` de `.main-content` a 180px

#### Tarea 5.3 — Catálogo Escuelas
- [ ] Header: H1 "Catálogo Platzi" SG 700 24px primary + SearchBar 380px + Btn "Actualizar" secondary outline
- [ ] Grid: 4 cols, gap 20px, padding 32px
- [ ] EscuelaCard: bg surface-1, border, radius 2xl, padding 24px
  - Hover: border primary-dim + glow-primary + translateY(-2px) transition 200ms
  - Badge SVG 48px + nombre SG 600 16px + "X RUTAS" Inter 400 13px muted
  - Hover: flecha → esquina superior derecha primary

#### Tarea 5.4 — Dashboard Mis Cursos
- [ ] Stats Row: 4 cards (Total | Completados | En Progreso | GB disco) bg surface-1
- [ ] Filtros rápidos pills: Activo(bg primary-dim text primary) / Inactivo(bg surface-1 text muted)
- [ ] Acordeón por escuela: ChevronDown animado + ícono + nombre SG 600 + pill nº cursos
- [ ] CursoCardPro: radius xl, thumb 16:9, overlay ProgressBar bottom 4px, badge escuela pill
  - Nombre SG 600 14px 2-line clamp + "X/Y lecciones" + ProgressBar + footer GB + Drive icon
- [ ] LeccionRow (h 56px): checkbox circular 18px + thumb 40×28 + título truncado + duración mono 12px
  - VISTO: border-left 3px primary + opacity 0.75
  - ACTIVO: bg primary-dim + border-left 3px primary

#### Tarea 5.5 — Reproductor con Auto-mark
- [ ] Integrar JS que detecta 80% reproducido → POST /api/progress con tipo_marcado="automatico"
- [ ] Respetar R001: no sobreescribir marcado manual

**Commit por módulo:**
- `feat(s1): design system carbon-neon CSS + sidebar`
- `feat(s1): catálogo escuelas rediseño`
- `feat(s1): dashboard mis cursos con progress tracking`

---

### FASE 6 — QA Final e Integración
**Estimado:** 1 día | **Prioridad:** P0

- [ ] Verificar todos los componentes S2 renderizan correctamente
- [ ] Confirmar que middleware protege rutas públicas (auth+activo) y admin (role=admin)
- [ ] Verificar responsive en 3 breakpoints (mobile, tablet, desktop)
- [ ] Confirmar que queries Supabase tienen manejo de error
- [ ] Verificar que endpoints S1 funcionan con servidor FastAPI encendido
- [ ] Merge feature branches → develop → main
- [ ] Deploy S2 a Vercel: `npx vercel --prod`

---

### FASE 7 — Acciones Manuales del Usuario
**Estas NO las ejecuta el agente — requieren acción humana:**

- [ ] Configurar Google Provider en [Supabase Dashboard → Authentication → Providers → Google](https://supabase.com/dashboard/project/sqegdibogfonfnelunml/auth/providers) con Client ID y Client Secret de Google Cloud Console
- [ ] Crear archivo `.env.local` en platzipvp-web local con todas las variables
- [ ] Conectar repo `platzipvp-web` en [Vercel Dashboard](https://vercel.com) y setear env vars
- [ ] Configurar `CRON_SECRET` en Vercel Environment Variables

---

## Notas Históricas

### 2026-03-28 — Vista Detalle Curso por URL (S1)
- [x] Vista `#curso/:slug` + hash routing + SPA navigation

### 2026-03-28 — Syllabus 100% completos (S1)
- [x] 1094 cursos únicos, todos con syllabus verificado

### 2026-04-07 — Arquitectura Completa
- [x] PRD Maestro escrito y aprobado
- [x] Schema Supabase creado (4 tablas, 11 policies, trigger)
- [x] Admin creado en Supabase Auth
- [x] Repo platzipvp-web creado (privado) + estructura scaffolded
- [x] Progress tracking API (S1) con R001
- [x] Sync CMS API (S2) con R007
- [x] Cron auto-sync configurado
- [x] Middleware auth S2 implementado
- [x] Tailwind config + globals.css + types.ts
- [x] Branches integrados a develop/main
