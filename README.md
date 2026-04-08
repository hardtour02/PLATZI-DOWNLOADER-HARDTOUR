<!-- markdownlint-disable MD033 MD036 MD041 MD045 MD046 -->

![Repo Banner](https://i.imgur.com/aJVikYa.png)

<div align="center">

<h1 style="border-bottom: none">
    <b><a href="#">PLATZI DOWNLOADER - HARDTOUR</a></b>
</h1>

Herramienta profesional para la descarga y gestión de cursos de Platzi, optimizada con una arquitectura **Senior Full Stack** modular. Funciona de manera **Offline-first**, localizando todos los activos críticos para su ejecución sin depender de internet una vez descargados los cursos.

![GitHub repo size](https://img.shields.io/github/repo-size/hardtour02/PLATZI-DOWNLOADER-HARDTOUR?style=social)
![GitHub stars](https://img.shields.io/github/stars/hardtour02/PLATZI-DOWNLOADER-HARDTOUR)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=social)](https://opensource.org/licenses/MIT)

</div>

---

## 🎯 Características Core - HARDTOUR Edition

Diseñado íntegramente desde cero bajo una arquitectura **Senior Full Stack**, este sistema ha sido concebido para ofrecer una robustez y eficiencia superiores:

- **Arquitectura Modular Nativa (FastAPI)**: Orquestación completa del backend mediante routers especializados para una escalabilidad sin precedentes.
- **Ecosistema 100% Offline-First**: Implementación nativa de recursos críticos (fuentes, iconos y librerías) para una operatividad total sin dependencia de conexiones externas.
- **Portabilidad Universal Inteligente**: Sistema de gestión de rutas internas diseñado para garantizar un funcionamiento inmediato en cualquier hardware.
- **Estándares de Desarrollo Senior**: Flujos de trabajo, limpieza de código y procesos de mantenimiento centralizados bajo los más altos estándares profesionales.

---

## 🚀 Instalación y Uso

### 1. Requisitos Previos

Asegúrate de tener instalado **Python 3.10+** y **FFmpeg**.

```console
# En Windows (via PowerShell)
winget install ffmpeg
```

### 2. Preparación

Instala las dependencias y el navegador automatizado:

```console
pip install -e .
playwright install chromium
```

### 3. Ejecución

Utiliza los lanzadores directos incluidos:

- **Windows**: `start_windows.bat`
- **Linux**: `bash start_linux.sh`

---

## 💡 Guía Rápida

- **Iniciar Sesión**: Accede desde el panel lateral para vincular tu cuenta de Platzi.
- **Explorar Catálogo**: Navega por escuelas y rutas en la pestaña **"Catálogo"** para encontrar tus cursos favoritos.
- **Sincronización Inteligente**: Al hacer clic en el botón **Descargar** de cualquier curso en el catálogo, el sistema capturará automáticamente el enlace y lo transferirá al módulo de descarga sin intervención manual.
- **Modo Offline**: Una vez completado, disfruta de tus clases en la pestaña **"Mis Cursos"** sin necesidad de conexión externa.

---

## **Aviso de Uso**

Este proyecto se realiza con fines exclusivamente educativos. El código se ofrece "tal cual". Utilízalo de manera responsable y dentro de los términos de servicio de las plataformas educativas.

Este repositorio es una evolución personalizada y refinada basada en trabajos iniciales de la comunidad.
