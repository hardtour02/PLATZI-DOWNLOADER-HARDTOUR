import asyncio

from playwright.async_api import BrowserContext, Page

from scraper.cache import Cache
from scraper.constants import PLATZI_URL
from scraper.helpers import read_json, write_json
from scraper.models import Chapter, Resource, TypeUnit, Unit, Video
from scraper.utils import download_styles, get_m3u8_url, get_m3u8_url_from_thumbnail, get_subtitles_url, slugify


@Cache.cache_async
async def get_course_title(page: Page) -> str:
    SELECTOR = "h1[class*='CourseHeader']"
    EXCEPTION = Exception("No course title found")
    try:
        title = await page.locator(SELECTOR).first.text_content()
        if not title:
            raise EXCEPTION
    except Exception:
        await page.close()
        raise EXCEPTION

    return title


@Cache.cache_async
async def get_course_metadata(page: Page) -> dict:
    """Extrae metadatos premium del curso para la interfaz gráfica."""
    # Esperar a que el header esté listo
    try:
        await page.wait_for_selector("h1[class*='CourseHeader'], [class*='CourseClass__Image']", timeout=10000)
    except:
        pass
    
    # Intentar extraer todo via JS para ser más robusto
    metadata = await page.evaluate(r"""
        () => {
            const findSrc = (sel) => {
                const el = document.querySelector(sel);
                if (!el) return null;
                let src = el.getAttribute('src') || el.getAttribute('data-src');
                if (src) return src;
                const style = window.getComputedStyle(el).backgroundImage;
                if (style && style !== 'none') {
                    const match = style.match(/url\(["']?([^"']+)["']?\)/);
                    if (match) return match[1];
                }
                return null;
            };
            const findText = (sel) => {
                const el = document.querySelector(sel);
                return el ? el.innerText.trim() : null;
            };
            
            return {
                thumbnail_url: findSrc("[class*='CourseClass__Image'] div, img[class*='Hero'], .Hero-image img, [class*='CourseHeader'] img[src*='background'], meta[property='og:image']"),
                logo_url: findSrc("img[src*='achievements'], img[src*='achievement'], img[class*='Logo'], .Badge-icon, [class*='CourseHeader-badge'] img"),
                category: findText(".CourseHeader-category, a[href*='/categorias/'], [class*='Badge-category']"),
                author: findText(".CourseHeader-teacher-name, a[href*='/profesores/'], [class*='Teacher-name']")
            };
        }
    """)
    
    # Fallback si JS falló en algo
    if not metadata["thumbnail_url"]:
        hero = page.locator("img[src*='banner'], img[src*='hero'], .Hero img").first
        if await hero.count() > 0:
            metadata["thumbnail_url"] = await hero.get_attribute("src")

    return metadata

@Cache.cache_async
async def get_draft_chapters(page: Page) -> list[Chapter]:
    EXCEPTION = Exception("No sections found")
    try:
        # Esperar a que aparezca la sección de contenido
        try:
            await page.wait_for_selector("a[href*='/clases/'], a[href*='/quiz/'], a[class*='ItemLink']", timeout=15000)
        except Exception:
            pass

        # Extraer syllabus completo via JS hiper-robusto sin depender de clases CSS
        syllabus_data = await page.evaluate(r"""
            () => {
                const chapters = [];
                let currentChapter = { name: "Módulo Principal", units: [] };
                
                // All possible module titles and lesson links in document order
                const elements = document.querySelectorAll("h2, h3, a[href*='/clases/'], a[href*='/quiz/'], a[class*='ItemLink']");
                
                elements.forEach(el => {
                    const isLink = el.tagName === 'A';
                    
                    if (!isLink) {
                        // It's a heading
                        const text = el.innerText.trim();
                        // Ignore general headings like "Acerca de", "Comentarios", etc.
                        if (text && text.length > 3 && !['comentarios', 'acerca de', 'archivos', 'profesor'].includes(text.toLowerCase())) {
                            if (currentChapter.units.length > 0) {
                                chapters.push(currentChapter);
                            }
                            currentChapter = { name: text, units: [] };
                        }
                    } else {
                        // It's a lesson link
                        const unitTitleEl = el.querySelector("h3, strong, p, [class*='title']") || el;
                        const unitTitle = (unitTitleEl.innerText || '').trim().split('\n')[0];
                        if (!unitTitle) return;
                        
                        const url = el.getAttribute('href');
                        
                        // Buscar duración
                        let duration = null;
                        const durEl = el.querySelector("span[class*='Duration'], .Duration") || 
                                      Array.from(el.querySelectorAll('span, p')).find(s => s.innerText.includes('min') || /\d+:\d+/.test(s.innerText));
                        
                        if (durEl) {
                            duration = durEl.innerText.replace('min', '').trim();
                        }
                        
                        // Buscar miniatura
                        const img = el.querySelector('img[src]');
                        let thumb = img ? img.getAttribute('src') : null;
                        
                        if (!thumb) {
                            const bg = el.querySelector('[style*="background"]');
                            if (bg) {
                                const m = bg.style.backgroundImage.match(/url\((["']?)([^"']+)["']?\)/);
                                if (m) thumb = m[2];
                            }
                        }
                        
                        currentChapter.units.push({
                            title: unitTitle,
                            url: url,
                            duration: duration,
                            thumbnail_url: thumb
                        });
                    }
                });
                
                if (currentChapter.units.length > 0) {
                    chapters.push(currentChapter);
                }
                
                return chapters;
            }
        """)
        
        # Si falló el JS selectivo, intentar un barrido más genérico
        if not syllabus_data:
             # Fallback logic here if needed, but JS above is usually better
             pass

        chapters: list[Chapter] = []
        for ch in syllabus_data:
            units: list[Unit] = []
            for u in ch['units']:
                units.append(
                    Unit(
                        type=TypeUnit.VIDEO if "/quiz/" not in u['url'] else TypeUnit.QUIZ,
                        title=u['title'],
                        url=PLATZI_URL + u['url'] if u['url'].startswith("/") else u['url'],
                        slug=slugify(u['title']),
                        thumbnail_url=u['thumbnail_url'],
                        duration=u['duration'],
                    )
                )
            
            chapters.append(
                Chapter(
                    name=ch['name'],
                    slug=slugify(ch['name']),
                    units=units,
                )
            )

    except Exception as e:
        await page.close()
        raise EXCEPTION from e

    return chapters


@Cache.cache_async
async def get_unit(context: BrowserContext, url: str, thumbnail_url: str | None = None) -> Unit:
    TYPE_SELECTOR = ".VideoPlayer"
    TITLE_SELECTOR = "h1[class*='MaterialHeading'], h1, .Material-title, .CourseHeader-title"
    EXCEPTION = Exception("Could not collect unit data")

    # --- NEW CONSTANTS ----
    SECTION_FILES = "//h4[normalize-space(text())='Archivos de la clase']"
    SECTION_READING = "//h4[normalize-space(text())='Lecturas recomendadas']"
    SECTION_LINKS = "a[class*='FilesAndLinks_Item']"
    BUTTON_DOWNLOAD_ALL = "a[class*='FilesTree__Download'][href][download]"
    SUMMARY_CONTENT_SELECTOR = "div[class*='Resources_Resources__Articlass--expanded']"
    SIBLINGS = "//following-sibling::ul[1]"
    LAYOUT_CONTAINER = "div[class*='Layout_Layout__']"
    MAIN_LAYOUT = "main[class*='Layout_Layout-main']"

    if "/quiz/" in url:
        return Unit(
            url=url,
            title="Quiz",
            type=TypeUnit.QUIZ,
            slug="Quiz",
        )

    page = None
    try:
        page = await context.new_page()
        
        # Catch ALL requests for deep debugging
        all_requests = []
        captured_headers = {}
        async def handle_request(request):
            all_requests.append(f"{request.method} {request.url}")
            if ".m3u8" in request.url:
                nonlocal captured_headers
                captured_headers = request.headers
                pass
                print(f"INFO: Captured m3u8 request: {request.url}")

        page.on("request", handle_request)
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Try to bypass "Subscribe" banner and force video load
            await page.evaluate("""() => {
                const banner = document.querySelector('div[class*="Banner_Banner__"]');
                if (banner) {
                    console.log("Removing subscription banner...");
                    banner.remove();
                }
                const video = document.querySelector('video');
                if (video) {
                    console.log("Found video element, trying to play...");
                    video.play().catch(e => console.log("Play failed: ", e));
                }
            }""")
            
            # Additional wait for title to appear
            try:
                await page.wait_for_selector(TITLE_SELECTOR, timeout=10000)
            except Exception:
                 pass

            await page.wait_for_load_state("load", timeout=15000)
            await asyncio.sleep(2) # Wait for network requests
        except Exception:
            pass
        
        # all_requests and requests_debug.log removed for production
        pass

        title_element = page.locator(TITLE_SELECTOR).first
        if await title_element.count() == 0:
             # Last resort: try any H1
             title_element = page.locator("h1").first
             if await title_element.count() == 0:
                raise EXCEPTION
        title = await title_element.text_content()

        if not title:
            raise EXCEPTION

        # Detect locked/premium content indicators
        is_locked = await page.locator("[class*='Paywall'], [class*='Banner_Banner__'], [class*='LockIcon']").count() > 0
        video_player_visible = await page.locator(TYPE_SELECTOR).is_visible()

        if is_locked or not video_player_visible:
            # Check if we have a thumbnail_url → can bypass paywall via MediaStream
            m3u8_from_thumb = get_m3u8_url_from_thumbnail(thumbnail_url)
            if m3u8_from_thumb:
                from scraper.logger import Logger
                Logger.info(f"[BYPASS] Locked/Hidden lesson ({url}) → using thumbnail m3u8")
                video = Video(url=m3u8_from_thumb, token=None, subtitles_url=None)
                return Unit(
                    url=url,
                    title=title,
                    type=TypeUnit.VIDEO,
                    video=video,
                    slug=slugify(title),
                )
            
            if not video_player_visible:
                # No thumbnail bypass available → treat as lecture/text
                return Unit(
                    url=url,
                    title=title,
                    type=TypeUnit.LECTURE,
                    slug=slugify(title),
                )

        # It's a video unit with a visible player
        content = await page.content()

        # Extract credentials_token from localStorage
        try:
            import json
            localStorage = await page.evaluate("() => JSON.stringify(localStorage)")
            ls_dict = json.loads(localStorage)
            token = ls_dict.get("credentials_token")
        except Exception:
            token = None

        unit_type = TypeUnit.VIDEO

        # Extract m3u8_url and subtitles_url
        # First try to extract from HTML (works for open/free lessons)
        try:
            m3u8_url = get_m3u8_url(content)
        except Exception:
            # Fallback: extract Video ID from lesson thumbnail URL
            m3u8_url_from_thumb = get_m3u8_url_from_thumbnail(thumbnail_url)
            if m3u8_url_from_thumb:
                from scraper.logger import Logger
                Logger.info(f"[BYPASS] Using thumbnail m3u8 for locked lesson: {url}")
                m3u8_url = m3u8_url_from_thumb
            else:
                raise
        subtitles_url = get_subtitles_url(content)

        # and requires undefined variables (directory, title_formatted) and an
        # unimported function (m3u8_dl).
        # To make the code syntactically correct and fulfill the intent of
        # passing the token, we'll assume m3u8_dl is meant to be called
        # separately if needed, or that the Video model should be updated.
        # For now, we'll keep the Video model initialization as it was,
        # but if m3u8_dl were to be called, it would be here,
        # using the 'token' variable.
        # Example of how it *might* be called if m3u8_dl, directory,
        # and title_formatted were defined and imported:
        # if m3u8_url:
        #     from pathlib import Path # Needs to be imported
        #     from scraper.utils import m3u8_dl # Needs to be imported
        #     directory = "some_directory" # Needs to be defined
        #     title_formatted = "some_title" # Needs to be defined
        #     await m3u8_dl(
        #         m3u8_url,
        #         Path(f"{directory}/{title_formatted}.mp4"),
        #         token=token,
        #     )

        video = Video(
            url=m3u8_url,
            token=token,
            subtitles_url=subtitles_url,
        )

        # --- Get resources and summary ---
        html_summary = None

        files_section = page.locator(SECTION_FILES)
        next_sibling_files = files_section.locator(SIBLINGS)

        reading_section = page.locator(SECTION_READING)
        next_sibling_reading = reading_section.locator(SIBLINGS)

        download_all_button = page.locator(BUTTON_DOWNLOAD_ALL)

        file_links: list[str] = []
        readings_links: list[str] = []

        # Get "Archivos de la clase" if the section exists
        if await next_sibling_files.count() > 0:
            enlaces = next_sibling_files.locator(SECTION_LINKS)
            for i in range(await enlaces.count()):
                link = await enlaces.nth(i).get_attribute("href")
                if link:
                    file_links.append(link)

        # Get link of the download all button if it exists
        if await download_all_button.count() > 0:
            link = await download_all_button.get_attribute("href")
            if link:
                file_links.append(link)

        # Get "Lecturas recomendadas" if the section exists
        if await next_sibling_reading.count() > 0:
            enlaces = next_sibling_reading.locator(SECTION_LINKS)
            for i in range(await enlaces.count()):
                link = await enlaces.nth(i).get_attribute("href")
                if link:
                    readings_links.append(link)

        # Get summary if it exists
        summary = page.locator(SUMMARY_CONTENT_SELECTOR)
        if await summary.count() > 0:
            all_css_styles: list[str] = []

            layout_container = await page.query_selector(LAYOUT_CONTAINER)
            class_container = ""
            if layout_container:
                class_container = await layout_container.get_attribute("class") or ""

            main_layout = await page.query_selector(MAIN_LAYOUT)
            class_main = ""
            if main_layout:
                class_main = await main_layout.get_attribute("class") or ""

            # Get the HTML structure of the summary
            summary_section = await summary.evaluate("el => el.outerHTML")

            # Find all CSS selectors to include in the html_summary template
            stylesheet_links = page.locator("link[rel=stylesheet]")
            count = await stylesheet_links.count()
            for i in range(count):
                href = await stylesheet_links.nth(i).get_attribute("href")
                if href:
                    stylesheet = await download_styles(href)
                    all_css_styles.append(stylesheet)

            # Get the content of the <style>
            style_blocks = await page.query_selector_all("style")
            for style in style_blocks:
                style_content = await style.inner_text()
                all_css_styles.append(style_content)

            # Combine all styles
            styles = "\n".join(filter(None, all_css_styles))

            # HTML template for the summary
            html_summary = f"""
           <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{title}</title>
                <style>{styles}</style>
            </head>
            <body>
                <div class="{class_container}">
                    <main class="{class_main}">
                        {summary_section}
                    </main>
                </div>
            </body>
            </html>"""

        return Unit(
            url=url,
            title=title,
            type=unit_type,
            video=video,
            slug=slugify(title),
            resources=Resource(
                files_url=file_links,
                readings_url=readings_links,
                summary=html_summary,
            ),
        )

    except Exception as e:
        raise EXCEPTION from e

    finally:
        if page:
            await page.close()
