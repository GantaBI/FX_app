import pandas as pd  
import streamlit as st 
import json
import joblib
import os
from datetime import datetime
import subprocess
import sys

# Imports de componentes personalizados
from utils.utils_mapeo import enriquecer_datos_para_ui
from utils.componentes_visualizacion import mostrar_visualizacion
from utils.componentes_simulador import (
    mostrar_formulario_simulador,
    mostrar_resultados_simulador,
    mostrar_botones_accion_simulador
)


# ==========================================
# ID DE PACIENTE (preparado para endpoint)
# ==========================================
TARGET_ID = os.getenv("PACIENTE_ID","LNRV194101570")  # Valor por defecto para pruebas. Quitar en producción.

if not TARGET_ID:
    st.error("❌ No se ha proporcionado un ID de paciente. Setea la env var PACIENTE_ID.")
    st.stop()

def extraer_datos_paciente(target_id):
    """Ejecuta extract_data_model.py (que ya guarda en pacientes/)."""
    extract_dir = os.path.join(os.path.dirname(__file__), "extract_data_model")
    script_path = os.path.join(extract_dir, "extract_data_model.py")

    env = os.environ.copy()
    env["PACIENTE_ID"] = target_id

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True, text=True, timeout=120, env=env
    )
    print(result.stdout)
    
    if result.returncode != 0:
        print(f"❌ Error al extraer datos: {result.stderr}")
        return False
    
    # El script ya guarda en pacientes/, solo verificar que se creó
    carpeta_pacientes = os.path.join(os.path.dirname(__file__), "pacientes")
    ruta_json = os.path.join(carpeta_pacientes, f"paciente_{target_id}.json")
    return os.path.exists(ruta_json)

# ==========================================
# DETECCIÓN DE MODO DESDE URL (PARA PDF)
# ==========================================
query_params = st.query_params
modo_url = query_params.get("modo", None)

# Si viene de generación PDF, cargar datos de simulación
if modo_url == "simulacion":
    temp_data_path = os.path.join(os.path.dirname(__file__), "temp_simulacion.json")
    if os.path.exists(temp_data_path):
        with open(temp_data_path, "r") as f:
            datos_temp = json.load(f)
            
        st.session_state.simulacion_realizada = True
        st.session_state.data_simulado = {k: v for k, v in datos_temp.items() 
                                          if not k.startswith('predict') and k not in ['situacion_alta', 'categorias_situacion']}
        st.session_state.calculo_pre_sim = datos_temp.get("predict_preoperatorio", 0)
        st.session_state.calculo_post_sim = datos_temp.get("predict_postoperatorio", 0)
        st.session_state.calculo_estancia_sim = datos_temp.get("predict_estancia_total", 0)
        st.session_state.probs_sit_sim = datos_temp.get("predict_situacion_alta", [])
        st.session_state.situacion_alta_sim = datos_temp.get("situacion_alta", "N/A")
        st.session_state.categorias_situacion_sim = datos_temp.get("categorias_situacion", ["Mejora", "Empeora"])

# ==========================================
# FUNCIONES DE MODELO
# ==========================================

def manejar_generacion_descarga_pdf(clave_bytes, clave_aviso, gidenpac, generar_pdf_fn, 
                                     prefijo_archivo="informe", es_simulacion=False):
    """
    Maneja el estado y UI completo de generación/descarga de PDF.
    Muestra botón centrado para generar, y luego botones laterales para resetear/descargar.
    
    Args:
        clave_bytes: Nombre de la variable en session_state para guardar el PDF
        clave_aviso: Nombre de la variable en session_state para mostrar toast
        gidenpac: ID del paciente para el nombre del archivo
        generar_pdf_fn: Función callable que genera el PDF (debe retornar (pdf_bytes, error))
        prefijo_archivo: Prefijo del nombre del archivo ("informe" o "simulacion")
        es_simulacion: Si es True, añade "_HHMM" al nombre del archivo
    """
    # Inicializar estados si no existen
    if clave_bytes not in st.session_state:
        st.session_state[clave_bytes] = None
    
    # CASO A: PDF no generado - BOTÓN CENTRADO
    if st.session_state[clave_bytes] is None:
        _, col_centro, _ = st.columns([1, 3, 1])
        
        with col_centro:
            label = "📄 Generar PDF Simulación" if es_simulacion else "📄 Generar Informe PDF"
            if st.button(label, type="primary", width='stretch'):
                with st.spinner("Generando informe..."):
                    pdf_bytes, error = generar_pdf_fn()
                    
                    if pdf_bytes:
                        st.session_state[clave_bytes] = pdf_bytes
                        st.session_state[clave_aviso] = True
                        st.rerun()
                    else:
                        st.error(f"Error al generar: {error}")
    
    # CASO B: PDF generado - BOTONES LATERALES
    else:
        # 1. Notificación flotante (solo primera vez)
        if st.session_state.get(clave_aviso):
            mensaje = "¡Simulación generada correctamente!" if es_simulacion else "¡Informe generado correctamente!"
            st.toast(mensaje, icon="✅")
            st.session_state[clave_aviso] = False
        
        # 2. Botones lado a lado
        col_reset, col_download = st.columns(2)
        
        # Botón RESET (gris)
        with col_reset:
            label_reset = "🔄  Nuevasimulación" if es_simulacion else "🔄 Generar uno nuevo"
            if st.button(label_reset, type="secondary", width='stretch'):
                st.session_state[clave_bytes] = None
                st.rerun()
        
        # Botón DESCARGA (rojo)
        with col_download:
            # Generar nombre de archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M') if es_simulacion else datetime.now().strftime('%Y%m%d')
            nombre_archivo = f"{prefijo_archivo}_{gidenpac}_{timestamp}.pdf"
            
            st.download_button(
                label="📥 Descargar PDF" if not es_simulacion else "📥 Descargar PDF Simulación",
                data=st.session_state[clave_bytes],
                file_name=nombre_archivo,
                mime="application/pdf",
                type="primary",
                width='stretch'
            )
            
            
@st.cache_resource
def cargar_modelo_real(nombre_carpeta):
    """Carga modelo de regresión y sus componentes"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_modelo = os.path.join(base_dir, '..', 'models', nombre_carpeta)
        
        path_modelo = os.path.join(ruta_modelo, 'modelo_elasticnet.pkl')
        path_scaler = os.path.join(ruta_modelo, 'scaler.pkl')
        path_cols = os.path.join(ruta_modelo, 'columnas_modelo.pkl')
        
        if not os.path.exists(path_modelo): 
            return None, None, None

        modelo = joblib.load(path_modelo)
        scaler = joblib.load(path_scaler)
        cols = joblib.load(path_cols)
        return modelo, scaler, cols
    except:
        return None, None, None


def predecir_dias(modelo, scaler, cols, datos_json):
    """Predice días de estancia"""
    if modelo is None: 
        return 0.0
    try:
        df_input = pd.DataFrame(columns=cols, dtype=float)
        for col in df_input.columns:
            val = datos_json.get(col, 0)
            df_input.loc[0, col] = float(val)
        
        pred = modelo.predict(scaler.transform(df_input))[0]
        return max(0, pred)
    except Exception as e:
        print(f"❌ Error en predicción: {e}")
        return 0.0


@st.cache_resource
def cargar_modelo_clasificacion(nombre_carpeta):
    """Carga modelo de clasificación y sus componentes"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_modelo = os.path.join(base_dir, '..', 'models', nombre_carpeta)
        
        path_modelo = os.path.join(ruta_modelo, 'modelo_clasificacion.pkl')
        path_scaler = os.path.join(ruta_modelo, 'scaler.pkl')
        path_cols = os.path.join(ruta_modelo, 'columnas_modelo.pkl')
        path_clases = os.path.join(ruta_modelo, 'clases_target.pkl')
        
        if not os.path.exists(path_modelo): 
            return None, None, None, None

        modelo = joblib.load(path_modelo)
        scaler = joblib.load(path_scaler)
        cols = joblib.load(path_cols)
        clases = joblib.load(path_clases)
        return modelo, scaler, cols, clases
    except:
        return None, None, None, None


def predecir_probabilidades(modelo, scaler, cols, datos_json):
    """Predice probabilidades de clasificación"""
    if modelo is None: 
        return []
    try:
        df_input = pd.DataFrame(columns=cols, dtype=float)
        for col in df_input.columns:
            val = datos_json.get(col, 0)
            df_input.loc[0, col] = float(val)
        
        probs = modelo.predict_proba(scaler.transform(df_input))[0]
        return probs.tolist()
    except:
        return []

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def load_css(file_name):
    # Obtiene la ruta del directorio donde está app.py actualmente
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Luego la llamas igual que antes
load_css("custom_styles.css")


def generar_pdf_backend(es_simulacion=False, datos_simulacion=None):
    """Genera PDF llamando al script externo"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, "generate_pdf.py")
    carpeta_pacientes = os.path.join(base_dir, "pacientes")
    
    # Nombre del PDF
    if es_simulacion:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        pdf_filename = f"paciente_{TARGET_ID}_sim_{timestamp}.pdf"
        temp_data_path = os.path.join(base_dir, "temp_simulacion.json")
        with open(temp_data_path, "w") as f:
            json.dump(datos_simulacion, f)
        args = [sys.executable, script_path, "--simulacion", TARGET_ID]
    else:
        pdf_filename = f"paciente_{TARGET_ID}.pdf"
        args = [sys.executable, script_path, TARGET_ID]
    
    pdf_path = os.path.join(carpeta_pacientes, pdf_filename)
    
    # Eliminar PDF anterior si existe
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except:
            pass

    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                return f.read(), None 
        else:
            msg = result.stderr if result.stderr else "No se generó el archivo."
            return None, msg
    except Exception as e:
        return None, str(e)

# ==========================================
# CONFIGURACIÓN INICIAL
# ==========================================

load_css("custom_styles.css")

# Cargar modelos
mod_pre, sc_pre, cols_pre = cargar_modelo_real('ds_pre_oper')
mod_post, sc_post, cols_post = cargar_modelo_real('ds_post_oper')
mod_estancia, sc_estancia, cols_estancia = cargar_modelo_real('ds_estancia')
mod_sit, sc_sit, cols_sit, clases_sit = cargar_modelo_clasificacion('gsitalta')

diccionario_nombres = {
    0: "Mejora", 1: "Empeora",
    "0": "Mejora", "1": "Empeora",
    1.0: "Empeora", 0.0: "Mejora"
}

# ==========================================
# SELECTOR DE MODO
# ==========================================

st.sidebar.title("⚙️ Configuración")

if modo_url == "simulacion":
    modo = "Simulador"
else:
    modo = st.sidebar.radio(
        "Selecciona el modo:",
        ["Visualización paciente", "Simulador"],
        index=0
    )

# ==========================================
# MODO: VISUALIZACIÓN PACIENTE
# ==========================================

if modo == "Visualización paciente":
    
    directorio_actual = os.path.dirname(__file__)
    carpeta_pacientes = os.path.join(directorio_actual, "pacientes")
    os.makedirs(carpeta_pacientes, exist_ok=True)  # Crear si no existe

    TARGET_ID = os.getenv("PACIENTE_ID")
    ruta_json = os.path.join(carpeta_pacientes, f"paciente_{TARGET_ID}.json")
    
    if not os.path.exists(ruta_json):
        with st.spinner(f"Extrayendo datos del paciente {TARGET_ID}..."):
            exito = extraer_datos_paciente(TARGET_ID)
        
        if not os.path.exists(ruta_json):  # Verificar de nuevo después de extraer
            st.warning(f"⚠️ No se encontraron datos para el paciente {TARGET_ID}.")
            st.info("Por favor, verifica que el ID del paciente sea correcto.")
            st.stop()

    with open(ruta_json, "r") as file:
        data_raw = json.load(file)
    
    data = enriquecer_datos_para_ui(data_raw)
    
    # Calcular predicciones
    calculo_pre = predecir_dias(mod_pre, sc_pre, cols_pre, data)
    calculo_post = predecir_dias(mod_post, sc_post, cols_post, data)
    calculo_estancia = predecir_dias(mod_estancia, sc_estancia, cols_estancia, data)
    probs_sit = predecir_probabilidades(mod_sit, sc_sit, cols_sit, data)
    
    gidenpac = data.get("gidenpac", "Desconocido")

    # --- INICIO DEL CAMBIO ---
    # 1. Recuperamos valores del JSON de forma segura (0.0 si no existen)
    val_json_pre = data.get("predict_preoperatorio", 0.0)
    val_json_post = data.get("predict_postoperatorio", 0.0)
    
    # 2. Decidimos: ¿Usamos IA o usamos JSON?
    predict_preoperatorio = calculo_pre if mod_pre else val_json_pre
    predict_postoperatorio = calculo_post if mod_post else val_json_post
    
    # 3. Lógica para la estancia total
    if mod_estancia:
        predict_estancia_total = calculo_estancia
    else:
        # Si no hay IA, intentamos leer del JSON, y si no, sumamos los parciales
        suma_default = predict_preoperatorio + predict_postoperatorio
        predict_estancia_total = data.get("predict_estancia_total", suma_default)
    # --- FIN DEL CAMBIO ---

    # ... el if anterior ...
    if mod_sit and len(probs_sit) > 0:
        predict_situacion_alta = probs_sit
        categorias_situacion = [diccionario_nombres.get(c, str(c)) for c in clases_sit]
        idx_max = probs_sit.index(max(probs_sit))
        situacion_alta = categorias_situacion[idx_max]
    else:
        # --- CORRECCIÓN AQUÍ ---
        probs_json = data.get("predict_situacion_alta", [])
        categorias_situacion = ["Mejora", "Empeora"]
        
        # 3. VERIFICACIÓN DE SEGURIDAD:
        # Si la lista está vacía o no tiene el mismo tamaño que las categorías (2),
        # creamos una lista de ceros para que Pandas no explote.
        if len(probs_json) != len(categorias_situacion):
            predict_situacion_alta = [0.0] * len(categorias_situacion) # Crea [0.0, 0.0]
        else:
            predict_situacion_alta = probs_json
            
        situacion_alta = data.get("situacion_alta", "N/A")
    # Mostrar visualización
    mostrar_visualizacion(
        data, 
        predict_preoperatorio, 
        predict_postoperatorio, 
        predict_estancia_total,
        predict_situacion_alta, 
        situacion_alta, 
        categorias_situacion,
        es_simulacion=False,
        gidenpac=gidenpac
    )
    
# GENERACIÓN Y DESCARGA DE PDF
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    manejar_generacion_descarga_pdf(
        clave_bytes='pdf_paciente_bytes',
        clave_aviso='mostrar_aviso_exito',
        gidenpac=gidenpac,
        generar_pdf_fn=lambda: generar_pdf_backend(es_simulacion=False),
        prefijo_archivo="informe",
        es_simulacion=False
    )
# ==========================================
# MODO: SIMULADOR
# ==========================================

else:
    if 'simulacion_realizada' not in st.session_state:
        st.session_state.simulacion_realizada = False
    
    if 'pdf_simulacion_bytes' not in st.session_state:
        st.session_state.pdf_simulacion_bytes = None

    if not st.session_state.simulacion_realizada:
        mostrar_formulario_simulador(
            predecir_dias, 
            predecir_probabilidades,
            cargar_modelo_real,
            cargar_modelo_clasificacion
        )
    else:
        gidenpac_real = mostrar_resultados_simulador()
        mostrar_botones_accion_simulador(gidenpac_real, generar_pdf_backend, manejar_generacion_descarga_pdf)
