import pandas as pd  
import plotly.express as px  
import streamlit as st 
import json
import joblib
import os
from datetime import datetime
from utils_mapeo import enriquecer_datos_para_ui
import subprocess
import sys
import pytz

zona_horaria = pytz.timezone('Europe/Madrid')

# --- FUNCIONES DE MODELOS ---
@st.cache_resource
def cargar_modelo_real(nombre_carpeta):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_modelo = os.path.join(base_dir, '..', 'models', nombre_carpeta)
        
        path_modelo = os.path.join(ruta_modelo, 'modelo_elasticnet.pkl')
        path_scaler = os.path.join(ruta_modelo, 'scaler.pkl')
        path_cols = os.path.join(ruta_modelo, 'columnas_modelo.pkl')
        
        if not os.path.exists(path_modelo): return None, None, None

        modelo = joblib.load(path_modelo)
        scaler = joblib.load(path_scaler)
        cols = joblib.load(path_cols)
        return modelo, scaler, cols
    except:
        return None, None, None

def predecir_dias(modelo, scaler, cols, datos_json):
    if modelo is None: return 0.0
    try:
        df_input = pd.DataFrame(columns=cols, dtype=float)
        for col in df_input.columns:
            val = datos_json.get(col, 0)
            df_input.loc[0, col] = float(val)
            
        pred = modelo.predict(scaler.transform(df_input))[0]
        return max(0, pred)
    except:
        return 0.0

@st.cache_resource
def cargar_modelo_clasificacion(nombre_carpeta):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_modelo = os.path.join(base_dir, '..', 'models', nombre_carpeta)
        
        path_modelo = os.path.join(ruta_modelo, 'modelo_clasificacion.pkl')
        path_scaler = os.path.join(ruta_modelo, 'scaler.pkl')
        path_cols = os.path.join(ruta_modelo, 'columnas_modelo.pkl')
        path_clases = os.path.join(ruta_modelo, 'clases_target.pkl')
        
        if not os.path.exists(path_modelo): return None, None, None, None

        modelo = joblib.load(path_modelo)
        scaler = joblib.load(path_scaler)
        cols = joblib.load(path_cols)
        clases = joblib.load(path_clases)
        return modelo, scaler, cols, clases
    except:
        return None, None, None, None

def predecir_probabilidades(modelo, scaler, cols, datos_json):
    if modelo is None: return []
    try:
        df_input = pd.DataFrame(columns=cols, dtype=float)
        for col in df_input.columns:
            val = datos_json.get(col, 0)
            df_input.loc[0, col] = float(val)
        
        probs = modelo.predict_proba(scaler.transform(df_input))[0]
        return probs.tolist()
    except:
        return []

def load_css(file_path):
    with open(file_path, "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def crear_tabla_y_grafico(titulo, categorias, porcentajes, orden, colores=None):
    data = {"Categoría": categorias, "Porcentaje predicción": porcentajes}
    df = pd.DataFrame(data)

    df_tabla = df.copy()
    df_tabla["Porcentaje predicción"] = df_tabla["Porcentaje predicción"].apply(lambda x: f"{x*100:.0f}%")

    st.subheader(titulo)
    st.dataframe(df_tabla)

    fig = px.pie(
        df,
        values="Porcentaje predicción",
        names="Categoría",
        title=titulo,
        color="Categoría",
        category_orders={"Categoría": orden},
        color_discrete_sequence=colores,
    )
    st.plotly_chart(fig, use_container_width=True)

def convertir_a_texto(valor, tipo):
    """Convierte valores numéricos a texto legible"""
    conversiones = {
        'sexo': {0: 'Mujer', 1: 'Hombre'},
        'binario': {0: 'No', 1: 'Sí'},
        'residencia': {0: 'Centro', 1: 'Afueras'},
        'lado': {0: 'Izquierdo', 1: 'Derecho'},
        'riesgo_caida': {0: 'Bajo', 1: 'Medio', 2: 'Alto'},
        'movilidad': {0: 'Independiente', 1: 'Ayuda', 2: 'Dependiente'}
    }
    return conversiones.get(tipo, {}).get(valor, str(valor))

def generar_pdf_simulacion():
    """
    Ejecuta el script de generación de PDF para la página de simulación
    """
    try:
        # Marcar que estamos en modo simulación
        st.session_state['generando_pdf_simulacion'] = True
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_dir, "generate_pdf.py")
        
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Limpiar flag
        st.session_state['generando_pdf_simulacion'] = False
        
        if result.returncode == 0:
            return True, "PDF generado correctamente"
        else:
            return False, f"Error: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        st.session_state['generando_pdf_simulacion'] = False
        return False, "Timeout: El proceso tardó demasiado"
    except Exception as e:
        st.session_state['generando_pdf_simulacion'] = False
        return False, f"Error al ejecutar script: {str(e)}"

# Función para mostrar la visualización (usado en ambos modos)
def mostrar_visualizacion(data, predict_preoperatorio, predict_postoperatorio, predict_estancia_total, 
                          predict_situacion_alta, situacion_alta, categorias_situacion, 
                          es_simulacion=False, gidenpac="Simulación"):
    
    diccionario_colores = { 
        "Mejora": "#09AB3B",
        "Empeora": "#FF2B2B"
    }
    
    fecha_actual = datetime.now(zona_horaria).strftime("%d/%m/%Y %H:%M")
    fecha_ingreso = data.get("fllegada_map", fecha_actual) if not es_simulacion else fecha_actual
    
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-end; align-items: center; padding-right: 10px;">
            <p style="font-size: 16px; margin: 0;">Fecha de ingreso: {fecha_ingreso}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-end; align-items: center; padding-right: 10px;">
            <p style="font-size: 16px; margin: 0;">Fecha del documento: {fecha_actual}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    titulo = "Predicción de Fractura de Cadera" if not es_simulacion else "Simulación - Predicción de Fractura de Cadera"
    st.markdown(f"<h1 style='text-align: center;'>{titulo}</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # DATOS DEL PACIENTE
    st.header("Datos del paciente")
    
    # Mostrar ID según el modo
    if es_simulacion:
        st.warning(f"**ID paciente: {gidenpac} - SIMULACIÓN**")
    else:
        st.success(f"**ID paciente: {gidenpac}**")
    
    # Extraer valores (adaptado para simulación)
    if es_simulacion:
        sexo = convertir_a_texto(data.get("itipsexo_map", 0), 'sexo')
        edad = data.get("ds_edad_map", 0)
        otro_centro = convertir_a_texto(data.get("iotrocen_map", 0), 'binario')
        lugar_residencia = convertir_a_texto(data.get("ds_centro_afueras_map", 0), 'residencia')
        tipo_fractura = data.get("gdiagalt_map", "N/A")
        lado_fractura = convertir_a_texto(data.get("ds_izq_der_map", 0), 'lado')
    else:
        sexo = data["itipsexo_map"]
        edad = data["ds_edad_map"]
        otro_centro = data["iotrocen_map"]
        lugar_residencia = data["ds_centro_afueras_map"]
        tipo_fractura = data["gdiagalt_map"]
        lado_fractura = data["ds_izq_der_map"]
    
    tabla_resumen = pd.DataFrame({
        "Variable": ["Sexo", "Edad","Procedencia", "Lugar de residencia", "Código CIE", "Lado de fractura"],
        "Valor": [sexo, edad, otro_centro, lugar_residencia, tipo_fractura, lado_fractura]
    })
    st.subheader("Resumen paciente")
    st.table(tabla_resumen)
    
    # RESUMEN PREDICCIONES
    st.header("Resumen predicciones")
    st.subheader("Estancia")
    st.info(f"**Pre-operatorio:** {predict_preoperatorio:.1f} días")
    st.info(f"**Post-operatorio:** {predict_postoperatorio:.1f} días")
    st.info(f"**Estancia total:** {predict_estancia_total:.1f} días")
    
    st.subheader("Situación al alta")
    if isinstance(predict_situacion_alta, list) and len(predict_situacion_alta) > 0:
        prob_max = max(predict_situacion_alta) * 100
    else:
        prob_max = 0
    
    mensaje_alta = f"**Pronóstico:** {situacion_alta} ({prob_max:.1f}%)"
    if situacion_alta == "Mejora":
        st.success(mensaje_alta)
    elif situacion_alta == "Empeora":
        st.warning(mensaje_alta)
    else:
        st.info(mensaje_alta)
    
    # CONSTANTES
    st.markdown("<div class='no-overlap'></div>", unsafe_allow_html=True)
    st.header("Constantes del paciente")
    
    if es_simulacion:
        ntensmin = data.get("ntensmin_map", 0)
        ntensmax = data.get("ntensmax_map", 0)
        ntempera = data.get("ntempera_map", 0)
        nsatuoxi = data.get("nsatuoxi_map", 0)
    else:
        ntensmin = data["ntensmin_map"]
        ntensmax = data["ntensmax_map"]
        ntempera = data["ntempera_map"]
        nsatuoxi = data["nsatuoxi_map"]
    
    tabla_constantes = pd.DataFrame({
        "Variable": ["Tensión mínima","Tensión máxima", "Temperatura", "Saturación Oxígeno Respiratoria"],
        "Valor": [ntensmin, ntensmax, ntempera, nsatuoxi]
    })
    st.table(tabla_constantes)
    
    # ALERGIAS
    st.header("Alergias del paciente")
    
    if es_simulacion:
        alergia_medicamentosa = convertir_a_texto(data.get("ds_alergia_medicamentosa_map", 0), 'binario')
        alergia_alimenticia = convertir_a_texto(data.get("ds_alergia_alimentaria_map", 0), 'binario')
        otras_alergias = convertir_a_texto(data.get("ds_otra_alergias_map", 0), 'binario')
    else:
        alergia_medicamentosa = data.get("ds_alergia_medicamentosa_map")
        alergia_alimenticia = data.get("ds_alergia_alimentaria_map")
        otras_alergias = data.get("ds_otra_alergias_map")
    
    tabla_alergias = pd.DataFrame({
        "Variable": ["Alergia medicamentosa", "Alergia alimentaria","Otras alergias"],
        "Valor": [alergia_medicamentosa, alergia_alimenticia, otras_alergias]
    })
    st.table(tabla_alergias)
    
    # COMORBILIDADES
    st.header("Comorbilidades del paciente")
    
    if es_simulacion:
        itu = convertir_a_texto(data.get("ds_ITU_map", 0), 'binario')
        insuficiencia_respiratoria = convertir_a_texto(data.get("ds_insuficiencia_respiratoria_map", 0), 'binario')
        insuficiencia_cardiaca = convertir_a_texto(data.get("ds_insuficiencia_cardiaca_map", 0), 'binario')
        deterioro_cognitivo = convertir_a_texto(data.get("ds_deterioro_cognitivo_map", 0), 'binario')
        insuficiencia_renal = convertir_a_texto(data.get("ds_insuficiencia_renal_map", 0), 'binario')
        hta = convertir_a_texto(data.get("ds_HTA_map", 0), 'binario')
        diabetes = convertir_a_texto(data.get("ds_diabetes_map", 0), 'binario')
        osteoporosis = convertir_a_texto(data.get("ds_osteoporosis_map", 0), 'binario')
    else:
        itu = data["ds_ITU_map"]
        insuficiencia_respiratoria = data["ds_insuficiencia_respiratoria_map"]
        insuficiencia_cardiaca = data["ds_insuficiencia_cardiaca_map"]
        deterioro_cognitivo = data["ds_deterioro_cognitivo_map"]
        insuficiencia_renal = data["ds_insuficiencia_renal_map"]
        hta = data["ds_HTA_map"]
        diabetes = data["ds_diabetes_map"]
        osteoporosis = data.get("ds_osteoporosis_map")
    
    tabla_comorbilidades = pd.DataFrame({
        "Variable": ["ITU", "Insuficiencia Respiratoria","Insuficiencia Cardíaca", "Deterioro Cognitivo", 
                     "Insuficiencia Renal", "HTA", "Diabetes","Osteoporosis"],
        "Valor": [itu, insuficiencia_respiratoria, insuficiencia_cardiaca, deterioro_cognitivo, 
                  insuficiencia_renal, hta, diabetes, osteoporosis]
    })
    st.table(tabla_comorbilidades)
    
    # NUTRICIÓN
    st.header("Nutrición del paciente")
    
    if es_simulacion:
        anemia = convertir_a_texto(data.get("ds_anemia_map", 0), 'binario')
        vitamina_d = convertir_a_texto(data.get("ds_vitamina_d_map", 0), 'binario')
        obesidad = convertir_a_texto(data.get("ds_obesidad_map", 0), 'binario')
        acido_folico = convertir_a_texto(data.get("ds_acido_folico_map", 0), 'binario')
    else:
        anemia = data["ds_anemia_map"]
        vitamina_d = data["ds_vitamina_d_map"]
        obesidad = data.get("ds_obesidad_map")
        acido_folico = data.get("ds_acido_folico_map")
    
    tabla_nutricion = pd.DataFrame({
        "Variable": ["Anemia", "Déficit Vitamina D","Obesidad","Ácido fólico"],
        "Valor": [anemia, vitamina_d, obesidad, acido_folico]
    })
    st.table(tabla_nutricion)
    
    # GERIATRÍA
    st.header("Geriatría")
    
    if es_simulacion:
        barthel = data.get("barthel_map", 0)
        braden = data.get("braden_map", 0)
        riesgo_caida = convertir_a_texto(data.get("riesgo_caida_map", 0), 'riesgo_caida')
        movilidad = convertir_a_texto(data.get("movilidad_map", 0), 'movilidad')
    else:
        barthel = data["barthel_map"]
        braden = data["braden_map"]
        riesgo_caida = data["riesgo_caida_map"]
        movilidad = data["movilidad_map"]
    
    tabla_enfermedades = pd.DataFrame({
        "Variable": ["Escala de Barthel","Escala de Braden", "Riesgo caida", "Movilidad"],
        "Valor": [barthel, braden, riesgo_caida, movilidad]
    })
    st.table(tabla_enfermedades)
    
    # GRÁFICO SITUACIÓN AL ALTA
    st.markdown("<div class='no-overlap'></div>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    colores_dinamicos = [diccionario_colores.get(cat, "gray") for cat in categorias_situacion]
    crear_tabla_y_grafico(
        titulo="Probabilidad de situación al alta",
        categorias=categorias_situacion,
        porcentajes=predict_situacion_alta,
        orden=categorias_situacion,
        colores=colores_dinamicos
    )

# Cargar CSS
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

# SELECTOR DE MODO
st.sidebar.title("⚙️ Configuración")
modo = st.sidebar.radio(
    "Selecciona el modo:",
    ["📊 Visualización paciente", "🔬 Simulador"],
    index=0
)

# ============================================
# MODO VISUALIZACIÓN PACIENTE
# ============================================
if modo == "📊 Visualización paciente":
    # Cargar datos desde JSON
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
    # MODIFICACIÓN: BOTÓN DE DESCARGA DIRECTO Y MÁS ANCHO
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Función para generar y leer el PDF en memoria (cacheada para no re-ejecutar si no cambia)
    @st.cache_data(show_spinner="Preparando archivo de descarga...")
    def obtener_binario_pdf():
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_dir, "generate_pdf.py")
        
        try:
            # Ejecutar script
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # Ruta del PDF generado
                pdf_path = "/home/ubuntu/STG-fractura_cadera/2026/app/informes/informe_final.pdf"
                
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        return f.read(), None # Retorna bytes y sin error
                else:
                    return None, "PDF generado pero no encontrado."
            else:
                return None, f"Error script: {result.stderr}"
                
        except Exception as e:
            return None, str(e)

    # Obtenemos los bytes del PDF
    pdf_bytes, error_msg = obtener_binario_pdf()

    # Diseño de columnas para hacer el botón más ancho
    # [1, 3, 1] hace que la columna central sea mucho más ancha que antes [2, 1, 2]
    col_download = st.columns([1, 3, 1])[1] 
    
    with col_download:
        if pdf_bytes:
            st.download_button(
                label="📥 Descargar Informe PDF",
                data=pdf_bytes,
                file_name=f"informe_{gidenpac}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                type="primary",           # Estilo destacado
                use_container_width=True  # Ocupa todo el ancho de la columna
            )
        else:
            st.error(f"No se pudo generar el botón de descarga: {error_msg}")

# ============================================
# MODO SIMULADOR
# ============================================
else:
    st.markdown("<h1 style='text-align: center;'>🔬 Simulador de Predicción</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Inicializar session_state
    if 'simulacion_realizada' not in st.session_state:
        st.session_state.simulacion_realizada = False
    
    # Botón para resetear simulación
    if st.session_state.simulacion_realizada:
        col_reset, col_download = st.columns([1, 1])
        with col_reset:
            if st.button("🔄 Nueva simulación", type="secondary", use_container_width=True):
                st.session_state.simulacion_realizada = False
                # Limpiar flag de PDF simulación
                if 'generando_pdf_simulacion' in st.session_state:
                    del st.session_state['generando_pdf_simulacion']
                st.rerun()
        
        with col_download:
            if st.button("📥 Descargar PDF Simulación", type="primary", use_container_width=True):
                with st.spinner("Generando PDF de simulación... Esto puede tardar unos segundos."):
                    exito, mensaje = generar_pdf_simulacion()
                    
                    if exito:
                        st.success(mensaje)
                        
                        pdf_path = "/home/ubuntu/STG-fractura_cadera/2026/app/informes/informe_final.pdf"
                        if os.path.exists(pdf_path):
                            # Cargar JSON para obtener el gidenpac
                            with open("paciente_SRRD193407690.json", "r") as file:
                                data_raw = json.load(file)
                            data_original = enriquecer_datos_para_ui(data_raw)
                            gidenpac_real = data_original["gidenpac"]
                            
                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="💾 Guardar PDF en tu ordenador",
                                    data=pdf_file,
                                    file_name=f"simulacion_{gidenpac_real}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                        else:
                            st.warning("PDF generado pero no encontrado en la ruta esperada")
                    else:
                        st.error(mensaje)
    
    # FORMULARIO DE ENTRADA
    if not st.session_state.simulacion_realizada:
        st.header("📋 Datos del paciente")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sexo_sim = st.selectbox("Sexo", [0, 1], format_func=lambda x: "Mujer" if x==0 else "Hombre")
            edad_sim = st.number_input("Edad", 0, 120, 75)
        
        with col2:
            otro_centro_sim = st.selectbox("Otro centro", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
            lugar_residencia_sim = st.selectbox("Lugar residencia", [0, 1], format_func=lambda x: "Centro" if x==0 else "Afueras")
        
        with col3:
            tipo_fractura_sim = st.text_input("Código CIE", "S72.0")
            lado_fractura_sim = st.selectbox("Lado fractura", [0, 1], format_func=lambda x: "Izquierdo" if x==0 else "Derecho")
        
        st.header("🩺 Constantes vitales")
        col4, col5, col6, col7 = st.columns(4)
        
        with col4:
            ntensmin_sim = st.number_input("Tensión mín (mmHg)", 0, 200, 70)
        with col5:
            ntensmax_sim = st.number_input("Tensión máx (mmHg)", 0, 200, 120)
        with col6:
            ntempera_sim = st.number_input("Temperatura (°C)", 35.0, 42.0, 36.5, step=0.1)
        with col7:
            nsatuoxi_sim = st.number_input("Sat O2 (%)", 0, 100, 95)
        
        st.header("💊 Comorbilidades")
        col8, col9, col10, col11 = st.columns(4)
        
        with col8:
            itu_sim = st.selectbox("ITU", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
            insuf_resp_sim = st.selectbox("Insuf. Respiratoria", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
            insuf_card_sim = st.selectbox("Insuf. Cardíaca", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
        
        with col9:
            deterioro_cog_sim = st.selectbox("Deterioro Cognitivo", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
            insuf_renal_sim = st.selectbox("Insuf. Renal", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
            hta_sim = st.selectbox("HTA", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
        
        with col10:
            diabetes_sim = st.selectbox("Diabetes", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
            obesidad_sim = st.selectbox("Obesidad", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
            osteoporosis_sim = st.selectbox("Osteoporosis", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
        
        with col11:
            anemia_sim = st.selectbox("Anemia", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
            vitamina_d_sim = st.selectbox("Déficit Vit. D", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
            acido_folico_sim = st.selectbox("Ácido fólico", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
        
        st.header("🤧 Alergias")
        col12, col13, col14 = st.columns(3)
        
        with col12:
            alergia_med_sim = st.selectbox("Alergia medicamentosa", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
        with col13:
            alergia_alim_sim = st.selectbox("Alergia alimentaria", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
        with col14:
            otras_alergias_sim = st.selectbox("Otras alergias", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
        
        st.header("👴 Escalas geriátricas")
        col15, col16, col17, col18 = st.columns(4)
        
        with col15:
            barthel_sim = st.number_input("Barthel (0-100)", 0, 100, 60, step=5)
        with col16:
            braden_sim = st.number_input("Braden (6-23)", 6, 23, 18)
        with col17:
            riesgo_caida_sim = st.selectbox("Riesgo caída", [0, 1, 2], format_func=lambda x: ["Bajo", "Medio", "Alto"][x])
        with col18:
            movilidad_sim = st.selectbox("Movilidad", [0, 1, 2], format_func=lambda x: ["Independiente", "Ayuda", "Dependiente"][x])
        
        st.markdown("---")
        
        # BOTÓN DE PREDICCIÓN
        if st.button("🔮 Calcular predicciones", type="primary", use_container_width=True):
            # Guardar datos en session_state
            st.session_state.data_simulado = {
                "itipsexo_map": sexo_sim,
                "ds_edad_map": edad_sim,
                "iotrocen_map": otro_centro_sim,
                "ds_centro_afueras_map": lugar_residencia_sim,
                "gdiagalt_map": tipo_fractura_sim,
                "ds_izq_der_map": lado_fractura_sim,
                "ntensmin_map": ntensmin_sim,
                "ntensmax_map": ntensmax_sim,
                "ntempera_map": ntempera_sim,
                "nsatuoxi_map": nsatuoxi_sim,
                "ds_ITU_map": itu_sim,
                "ds_insuficiencia_respiratoria_map": insuf_resp_sim,
                "ds_insuficiencia_cardiaca_map": insuf_card_sim,
                "ds_deterioro_cognitivo_map": deterioro_cog_sim,
                "ds_insuficiencia_renal_map": insuf_renal_sim,
                "ds_HTA_map": hta_sim,
                "ds_diabetes_map": diabetes_sim,
                "ds_obesidad_map": obesidad_sim,
                "ds_osteoporosis_map": osteoporosis_sim,
                "ds_anemia_map": anemia_sim,
                "ds_vitamina_d_map": vitamina_d_sim,
                "ds_acido_folico_map": acido_folico_sim,
                "ds_alergia_medicamentosa_map": alergia_med_sim,
                "ds_alergia_alimentaria_map": alergia_alim_sim,
                "ds_otra_alergias_map": otras_alergias_sim,
                "barthel_map": barthel_sim,
                "braden_map": braden_sim,
                "riesgo_caida_map": riesgo_caida_sim,
                "movilidad_map": movilidad_sim,
            }
            
            # CALCULAR PREDICCIONES
            with st.spinner("Calculando predicciones..."):
                st.session_state.calculo_pre_sim = predecir_dias(mod_pre, sc_pre, cols_pre, st.session_state.data_simulado)
                st.session_state.calculo_post_sim = predecir_dias(mod_post, sc_post, cols_post, st.session_state.data_simulado)
                st.session_state.calculo_estancia_sim = predecir_dias(mod_estancia, sc_estancia, cols_estancia, st.session_state.data_simulado)
                st.session_state.probs_sit_sim = predecir_probabilidades(mod_sit, sc_sit, cols_sit, st.session_state.data_simulado)
                
                if len(st.session_state.probs_sit_sim) > 0:
                    st.session_state.categorias_situacion_sim = [diccionario_nombres.get(c, str(c)) for c in clases_sit]
                    idx_max_sim = st.session_state.probs_sit_sim.index(max(st.session_state.probs_sit_sim))
                    st.session_state.situacion_alta_sim = st.session_state.categorias_situacion_sim[idx_max_sim]
                else:
                    st.session_state.categorias_situacion_sim = ["Mejora", "Empeora"]
                    st.session_state.situacion_alta_sim = "N/A"
            
            st.session_state.simulacion_realizada = True
            st.rerun()
    
    # MOSTRAR RESULTADOS
    if st.session_state.simulacion_realizada:
        # Cargar JSON para obtener el gidenpac real
        with open("paciente_SRRD193407690.json", "r") as file:
            data_raw = json.load(file)
        data_original = enriquecer_datos_para_ui(data_raw)
        gidenpac_real = data_original["gidenpac"]
        
        mostrar_visualizacion(
            st.session_state.data_simulado,
            st.session_state.calculo_pre_sim,
            st.session_state.calculo_post_sim,
            st.session_state.calculo_estancia_sim,
            st.session_state.probs_sit_sim,
            st.session_state.situacion_alta_sim,
            st.session_state.categorias_situacion_sim,
            es_simulacion=True,
            gidenpac=gidenpac_real
        )