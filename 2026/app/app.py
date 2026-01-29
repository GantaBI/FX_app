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

def load_css(file_path):
    """Carga estilos CSS personalizados"""
    with open(file_path, "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def generar_pdf_backend(es_simulacion=False, datos_simulacion=None):
    """Genera PDF llamando al script externo"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, "generate_pdf.py")
    base_path_app = "/home/ubuntu/STG-fractura_cadera/2026/app"
    
    if es_simulacion:
        pdf_path = os.path.join(base_path_app, "informes", "simulacion", "informe_final.pdf")
        temp_data_path = os.path.join(base_dir, "temp_simulacion.json")
        with open(temp_data_path, "w") as f:
            json.dump(datos_simulacion, f)
        args = [sys.executable, script_path, "--simulacion"]
    else:
        pdf_path = os.path.join(base_path_app, "informes", "original", "informe_final.pdf")
        args = [sys.executable, script_path]

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
    with open("paciente_SRRD193407690.json", "r") as file:
        data_raw = json.load(file)
    
    data = enriquecer_datos_para_ui(data_raw)
    
    # Calcular predicciones
    calculo_pre = predecir_dias(mod_pre, sc_pre, cols_pre, data)
    calculo_post = predecir_dias(mod_post, sc_post, cols_post, data)
    calculo_estancia = predecir_dias(mod_estancia, sc_estancia, cols_estancia, data)
    probs_sit = predecir_probabilidades(mod_sit, sc_sit, cols_sit, data)
    
    gidenpac = data["gidenpac"]
    
    predict_preoperatorio = calculo_pre if mod_pre else data["predict_preoperatorio"]
    predict_postoperatorio = calculo_post if mod_post else data["predict_postoperatorio"]
    predict_estancia_total = calculo_estancia if mod_estancia else (predict_preoperatorio + predict_postoperatorio)
    
    if mod_sit and len(probs_sit) > 0:
        predict_situacion_alta = probs_sit
        categorias_situacion = [diccionario_nombres.get(c, str(c)) for c in clases_sit]
        idx_max = probs_sit.index(max(probs_sit))
        situacion_alta = categorias_situacion[idx_max]
    else:
        predict_situacion_alta = data.get("predict_situacion_alta", [])
        situacion_alta = data.get("situacion_alta", "N/A")
        categorias_situacion = ["Mejora", "Empeora"]
    
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
    
# -------------------------------------------------------------------------
    # BOTONES DE DESCARGA - DISEÑO DINÁMICO (Centro -> Lados)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Inicializar estado
    if 'pdf_paciente_bytes' not in st.session_state:
        st.session_state.pdf_paciente_bytes = None

    # CASO A: Aún no generado (BOTÓN CENTRADO)
    if st.session_state.pdf_paciente_bytes is None:
        # Truco para centrar: Creamos 3 columnas y usamos la del medio.
        # [1, 2, 1] hace que el botón ocupe el 50% del ancho central.
        c_izq, c_centro, c_der = st.columns([1, 3, 1])
        
        with c_centro:
            if st.button("📄 Generar Informe PDF", type="primary", use_container_width=True):
                with st.spinner("Generando informe..."):
                    pdf_bytes, error = generar_pdf_backend(es_simulacion=False)
                    
                    if pdf_bytes:
                        st.session_state.pdf_paciente_bytes = pdf_bytes
                        st.session_state.mostrar_aviso_exito = True 
                        st.rerun()
                    else:
                        st.error(f"Error al generar: {error}")

    # CASO B: Generado (BOTONES A LOS LADOS)
    else:
        # 1. Notificación flotante (Toast)
        if st.session_state.get("mostrar_aviso_exito"):
            st.toast("¡Informe generado correctamente!", icon="✅")
            st.session_state.mostrar_aviso_exito = False 

        # 3. Columnas divididas 50/50
        col_reset, col_download = st.columns([1, 1])
        
        # --- IZQUIERDA: Botón Nuevo (Gris) ---
        with col_reset:
            if st.button("🔄 Generar uno nuevo", type="secondary", use_container_width=True):
                st.session_state.pdf_paciente_bytes = None
                st.rerun()

        # --- DERECHA: Botón Descargar (Rojo) ---
        with col_download:
            st.download_button(
                label="📥 Descargar PDF",
                data=st.session_state.pdf_paciente_bytes,
                file_name=f"informe_{gidenpac}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
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
        mostrar_botones_accion_simulador(gidenpac_real, generar_pdf_backend)