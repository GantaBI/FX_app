import os
import asyncio
from pyppeteer import launch
from PyPDF2 import PdfReader, PdfWriter

async def capture_sections(url, output_pdf_path):
    try:
        # Crear el directorio de salida si no existe
        output_dir = os.path.dirname(output_pdf_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Directorio creado: {output_dir}")

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
            return Array.from(sections).map((section, index) => (index + 1));
        }""")
        
        print(f"Secciones detectadas: {len(sections)}")
        pdfs = []
        
        for index in sections:
            print(f"Procesando sección {index}...")
            pdf_path = f"{output_pdf_path}-section-{index}.pdf"
            bounding_box = await page.evaluate(f"""() => {{
                const el = document.querySelector('.no-overlap:nth-of-type({index})');
                if (!el) return null;
                const rect = el.getBoundingClientRect();
                return {{
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height
                }};
            }}""")
            if bounding_box:
                await page.setViewport({
                    'width': 1920,
                    'height': int(bounding_box['height'] + 20)
                })
                await page.pdf({
                    'path': pdf_path,
                    'printBackground': True,
                    'preferCSSPageSize': True,
                    'clip': bounding_box
                })
                pdfs.append(pdf_path)
        
        print(f"PDFs generados: {pdfs}")

        # Combinar solo las páginas impares en un nuevo PDF
        combine_odd_pages(pdfs, f"{output_pdf_path}_final.pdf")

    except Exception as e:
        print(f"Error durante la captura: {e}")
    finally:
        # Cerrar el navegador
        await browser.close()
        print("Navegador cerrado.")

def combine_odd_pages(pdf_paths, output_path):
    print("Combinando páginas impares...")
    writer = PdfWriter()

    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        for i in range(len(reader.pages)):
            # Agregar solo páginas impares (índice 0, 2, 4,...)
            if i % 2 == 0:
                writer.add_page(reader.pages[i])

    # Guardar el PDF final
    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"PDF combinado guardado en: {output_path}")

# Ejecutar la captura
url = "http://99.81.70.181:8000/"
output_pdf_path = "./streamlit_to_pdf/informe"
asyncio.run(capture_sections(url, output_pdf_path))
