import asyncio
from pyppeteer import launch

async def capture_full_page(url, output_pdf_path):
    # Lanzar navegador
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    page = await browser.newPage()

    # Configurar viewport
    await page.setViewport({'width': 1920, 'height': 1080})

    # Cargar la página
    await page.goto(url, {'waitUntil': 'networkidle2'})
    await asyncio.sleep(5)  # Asegurar que todo cargue

    # Guardar la página como PDF
    await page.pdf({'path': output_pdf_path, 'format': 'A4', 'printBackground': True})
    print(f"PDF guardado en {output_pdf_path}")

    await browser.close()

# Ejecutar la captura
url = "http://99.81.70.181:8000/"
output_pdf_path = "./output/prueba16.pdf"

asyncio.run(capture_full_page(url, output_pdf_path))
