import os
import asyncio
from pyppeteer import launch
from PyPDF2 import PdfReader, PdfWriter
import nest_asyncio
import sys

# Aplicamos el parche para entornos como Jupyter o Streamlit
nest_asyncio.apply()

async def capture_sections(url, es_simulacion=False):
    browser = None
    try:
        # 1. DEFINIR RUTAS
        base_path = "/home/ubuntu/STG-fractura_cadera/2026/app"
        
        # Carpetas diferentes según el modo
        if es_simulacion:
            output_folder = os.path.join(base_path, "informes", "simulacion")
        else:
            output_folder = os.path.join(base_path, "informes", "original")
        
        # Crear la carpeta si no existe
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder, exist_ok=True)
                print(f"📂 Carpeta creada: {output_folder}")
            except Exception as e:
                print(f"❌ Error creando carpeta (Revisa permisos): {e}")
                return None
        else:
            print(f"📂 Usando carpeta existente: {output_folder}")

        # 2. INICIAR NAVEGADOR
        print("🚀 Lanzando navegador...")
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        await page.setViewport({'width': 1920, 'height': 1080})

        # 3. CARGAR PÁGINA PRIMERO
        print(f"🌐 Cargando: {url}")
        response = await page.goto(url, {'waitUntil': 'networkidle2', 'timeout': 60000})
        
        if response.status != 200:
            print(f"❌ Error HTTP: {response.status}")
            await browser.close()
            return None

        # 4. SI ES SIMULACIÓN, HACER CLIC EN EL MODO SIMULADOR
        if es_simulacion:
            print("🔬 Cambiando a modo simulador...")
            await asyncio.sleep(2)  # Esperar a que cargue
            
            # Intentar hacer clic en el radio button de simulador
            try:
                await page.evaluate("""() => {
                    const radios = document.querySelectorAll('input[type="radio"]');
                    for (let radio of radios) {
                        if (radio.value === '🔬 Simulador' || radio.nextSibling?.textContent?.includes('Simulador')) {
                            radio.click();
                            return true;
                        }
                    }
                    return false;
                }""")
                print("✅ Modo simulador activado")
                await asyncio.sleep(3)  # Esperar a que cargue el contenido de simulación
            except Exception as e:
                print(f"⚠️ No se pudo cambiar a modo simulador: {e}")

        # 5. INYECTAR CSS
        print("🎨 Cargando estilos y ocultando Sidebar...")
        await page.addStyleTag({
            'content': """
            @page { margin: 1in; }
            body { margin: 0; padding: 1em; box-sizing: border-box; }
            .no-overlap { page-break-before: always; }
            
            /* OCULTAR SIDEBAR IZQUIERDA */
            [data-testid="stSidebar"] { 
                display: none !important; 
                visibility: hidden !important;
            }
            /* Ocultar botón de colapsar sidebar */
            [data-testid="collapsedControl"] {
                display: none !important;
            }
            
            /* Ajustar margen izquierdo si queda hueco */
            .main .block-container {
                max-width: 100% !important;
                padding-left: 2rem !important;
                padding-right: 2rem !important;
            }
            
            /* Ocultar botones de descarga y nueva simulación */
            button:has-text("Descargar PDF"),
            button:has-text("Nueva simulación") {
                display: none !important;
            }
            """
        })

        print("⏳ Esperando renderizado (5s)...")
        await asyncio.sleep(5)

        # 6. DETECTAR SECCIONES
        sections = await page.evaluate("""() => {
            const sections = document.querySelectorAll('.no-overlap');
            return Array.from(sections).map((section, index) => (index + 1));
        }""")
        
        print(f"📸 Secciones detectadas: {len(sections)}")
        pdfs_raw = []
        
        # 7. GENERAR PDFs "SIN CAMBIOS" (RAW)
        for index in sections:
            filename_raw = "pdf_raw.pdf"
            if len(sections) > 1:
                filename_raw = f"pdf_raw_{index}.pdf"
                
            full_path_raw = os.path.join(output_folder, filename_raw)
            
            bounding_box = await page.evaluate(f"""() => {{
                const el = document.querySelector('.no-overlap:nth-of-type({index})');
                if (!el) return null;
                const rect = el.getBoundingClientRect();
                return {{ x: rect.x, y: rect.y, width: rect.width, height: rect.height }};
            }}""")
            
            if bounding_box:
                await page.setViewport({'width': 1920, 'height': int(bounding_box['height'] + 50)})
                
                print(f"   -> Guardando trozo: {filename_raw}")
                await page.pdf({
                    'path': full_path_raw,
                    'printBackground': True,
                    'preferCSSPageSize': True,
                    'clip': bounding_box
                })
                pdfs_raw.append(full_path_raw)

        # 8. GENERAR PDF FINAL (COMBINADO)
        if pdfs_raw:
            final_filename = "informe_final.pdf"
            full_path_final = os.path.join(output_folder, final_filename)
            
            combine_odd_pages(pdfs_raw, full_path_final)
            
            print("-" * 50)
            print("✅ PROCESO COMPLETADO")
            print(f"📂 Ruta: {output_folder}")
            print(f"📄 Archivos sueltos: {len(pdfs_raw)} (No borrados)")
            print(f"📕 Informe final: {final_filename}")
            print("-" * 50)
            
            return full_path_final
        else:
            print("⚠️ No se generaron secciones. Revisa los divs .no-overlap")
            return None

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return None
    finally:
        if browser:
            await browser.close()
        print("🏁 Navegador cerrado.")

def combine_odd_pages(pdf_paths, output_path):
    print("📚 Combinando PDF final...")
    writer = PdfWriter() 
    for pdf_path in pdf_paths:
        try:
            reader = PdfReader(pdf_path)
            for i in range(len(reader.pages)):
                if i % 2 == 0:
                    writer.add_page(reader.pages[i])
        except Exception as e:
            print(f"⚠️ Error leyendo {pdf_path}: {e}")

    with open(output_path, "wb") as f:
        writer.write(f)

# --- EJECUCIÓN ---
if __name__ == "__main__":
    # Detectar si se pasó argumento para simulación
    es_simulacion = len(sys.argv) > 1 and sys.argv[1] == "--simulacion"
    
    url = "http://localhost:8501/"
    resultado = asyncio.run(capture_sections(url, es_simulacion=es_simulacion))
    
    # Devolver el path del PDF generado
    if resultado:
        print(f"PDF_PATH:{resultado}")