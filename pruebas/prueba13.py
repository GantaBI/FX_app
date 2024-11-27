import asyncio
from pyppeteer import launch

async def capture_sections(url, output_pdf_path):
    try:
        # Iniciar el navegador
        print("Lanzando navegador...")
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()

        # Configurar el tamaño inicial de la ventana
        await page.setViewport({'width': 1920, 'height': 1080})

        # Añadir estilos CSS personalizados
        print("Cargando CSS personalizado...")
        await page.addStyleTag({
            'content': """
            @page { margin: 1in; }
            body { margin: 0; padding: 1em; box-sizing: border-box; }
            .no-overlap { page-break-before: always; }
            """
        })

        # Cargar la página y esperar hasta que esté completamente cargada
        print(f"Cargando la página: {url}")
        response = await page.goto(url, {'waitUntil': 'networkidle2'})
        if response.status != 200:
            print(f"Error al cargar la página. Estado HTTP: {response.status}")
            await browser.close()
            return

        # Esperar contenido dinámico
        print("Esperando contenido dinámico...")
        await asyncio.sleep(3)

        # Generar PDF sección por sección
        sections = await page.evaluate("""() => {
            const sections = document.querySelectorAll('.no-overlap');
            return Array.from(sections).map((section, index) => ({
                selector: `.no-overlap:nth-of-type(${index + 1})`,
                id: `section-${index + 1}`
            }));
        }""")
        
        print(f"Secciones detectadas: {len(sections)}")
        pdfs = []
        
        for section in sections:
            print(f"Procesando sección {section['id']}...")
            element = await page.querySelector(section['selector'])
            if element:
                bounding_box = await element.boundingBox()
                if bounding_box:
                    await page.setViewport({
                        'width': 1920,
                        'height': int(bounding_box['height'] + 20)
                    })
                    pdf_path = f"{output_pdf_path}-{section['id']}.pdf"
                    await page.pdf({
                        'path': pdf_path,
                        'printBackground': True,
                        'preferCSSPageSize': True,
                        'clip': bounding_box
                    })
                    pdfs.append(pdf_path)
        
        print(f"PDFs generados: {pdfs}")
    except Exception as e:
        print(f"Error durante la captura: {e}")
    finally:
        # Cerrar el navegador
        await browser.close()
        print("Navegador cerrado.")

# Ejecutar la captura
url = "http://99.81.70.181:8000/"
output_pdf_path = "./output/mejorada_prueba13"
asyncio.run(capture_sections(url, output_pdf_path))
 