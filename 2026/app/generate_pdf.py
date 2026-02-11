from datetime import datetime
import os
import asyncio
from pyppeteer import launch
from PyPDF2 import PdfReader, PdfWriter
import nest_asyncio
import sys
from pdf_styles import CSS_OCULTAR_STREAMLIT  

# Aplicamos el parche para entornos como Jupyter o Streamlit
nest_asyncio.apply()

# ========== CONFIGURACIÓN ==========
BASE_PATH_APP = "/home/ubuntu/FX_app/2026/app"
URL_STREAMLIT = "http://localhost:8501/"

# Configuración del navegador
BROWSER_VIEWPORT = {'width': 1920, 'height': 1080}
BROWSER_ARGS = ['--no-sandbox', '--disable-setuid-sandbox']

# Timeouts
PAGE_LOAD_TIMEOUT = 60000  # 60 segundos
SIMULATION_WAIT_TIME = 5   # 5 segundos extra para procesar datos

async def capture_sections(url, es_simulacion=False, paciente_id=None):
    browser = None
    try:
        # 1. DEFINIR RUTAS
        base_path = BASE_PATH_APP
        output_folder = os.path.join(base_path, "pacientes")
        
        # Crear carpeta si no existe
        os.makedirs(output_folder, exist_ok=True)
        
        # Nombre del archivo final
        if es_simulacion:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            final_filename = f"paciente_{paciente_id}_sim_{timestamp}.pdf"
        else:
            final_filename = f"paciente_{paciente_id}.pdf"

        # 2. INICIAR NAVEGADOR
        print("🚀 Lanzando navegador...")
        browser_args_with_tz = BROWSER_ARGS + ['--lang=es-ES', '--timezone-id=Europe/Madrid']
        browser = await launch(headless=True, args=browser_args_with_tz)
        page = await browser.newPage()
        await page.setViewport(BROWSER_VIEWPORT)

        # 3. CARGAR PÁGINA CON PARÁMETROS
        print(f"🌐 Cargando: {url}")
        
        # Si es simulación, agregar parámetro a la URL
        if es_simulacion:
            url_con_params = f"{url}?modo=simulacion"
        else:
            url_con_params = url
            
        response = await page.goto(url_con_params, {'waitUntil': 'networkidle2', 'timeout': PAGE_LOAD_TIMEOUT})
                
        if response.status != 200:
            print(f"❌ Error HTTP: {response.status}")
            await browser.close()
            return None

        # ESPERAR EXTRA SI ES SIMULACIÓN (para que procese el JSON)
        if es_simulacion:
            print("⏳ Esperando carga de datos de simulación...")
            await asyncio.sleep(SIMULATION_WAIT_TIME)

       # 4. INYECTAR CSS PARA OCULTAR ELEMENTOS
        print("🎨 Cargando estilos y ocultando elementos...")
        await page.addStyleTag({'content': CSS_OCULTAR_STREAMLIT})

        # 5. DETECTAR SECCIONES
        sections = await page.evaluate("""() => {
            const sections = document.querySelectorAll('.no-overlap');
            return Array.from(sections).map((section, index) => (index + 1));
        }""")
        
        print(f"📸 Secciones detectadas: {len(sections)}")
        pdfs_raw = []
        
        # 6. GENERAR PDFs "SIN CAMBIOS" (RAW)
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
                # ← CAMBIO: Ajustar viewport ANTES de generar PDF
                await page.setViewport({'width': 1920, 'height': int(bounding_box['height'] + 50)})
                
                # ← AÑADIR: Esperar a que se reajuste el layout
                await asyncio.sleep(0.5)
                
                # ← AÑADIR: Re-evaluar bounding_box después del ajuste
                bounding_box = await page.evaluate(f"""() => {{
                    const el = document.querySelector('.no-overlap:nth-of-type({index})');
                    if (!el) return null;
                    const rect = el.getBoundingClientRect();
                    return {{ x: rect.x, y: rect.y, width: rect.width, height: rect.height }};
                }}""")
                
                print(f"   -> Guardando trozo: {filename_raw}")
                await page.pdf({
                    'path': full_path_raw,
                    'printBackground': True,
                    'format': 'A4',  # ← CAMBIAR
                    'scale': 1.24,    # ← AÑADIR (ajusta entre 1.0-1.5)
                    'margin': {'top': '5mm', 'right': '5mm', 'bottom': '5mm', 'left': '5mm'}  # ← AÑADIR
                })
                pdfs_raw.append(full_path_raw)

        # 7. GENERAR PDF FINAL (COMBINADO)
        if pdfs_raw:
            full_path_final = os.path.join(output_folder, final_filename)
            
            combine_odd_pages(pdfs_raw, full_path_final)
            
            # ELIMINAR ARCHIVOS RAW TEMPORALES
            for pdf_raw in pdfs_raw:
                try:
                    os.remove(pdf_raw)
                except Exception as e:
                    print(f"⚠️ No se pudo borrar {pdf_raw}: {e}")
            
            print("-" * 50)
            print("✅ PROCESO COMPLETADO")
            print(f"📂 Ruta: {output_folder}")
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
    es_simulacion = "--simulacion" in sys.argv
    paciente_id = sys.argv[-1]  # Último argumento es siempre el ID
    
    url = URL_STREAMLIT
    resultado = asyncio.run(capture_sections(url, es_simulacion, paciente_id))
    
    # Devolver el path del PDF generado
    if resultado:
        print(f"PDF_PATH:{resultado}")