"""
Componentes específicos del modo simulador
"""
import streamlit as st
import json
import os
from datetime import datetime
from utils.utils_mapeo import enriquecer_datos_para_ui, preparar_datos_simulacion_para_modelo
from utils.componentes_visualizacion import mostrar_visualizacion


def mostrar_formulario_simulador(predecir_dias_fn, predecir_probabilidades_fn, 
                                  cargar_modelo_real_fn, cargar_modelo_clasificacion_fn):
    """Muestra el formulario de entrada de datos para el simulador"""
    
    # Diccionario para almacenar todos los valores del formulario
    datos_formulario = {}
    
    # ========== DATOS DEL PACIENTE ==========
    st.header("Datos del paciente")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        datos_formulario['itipsexo_map'] = st.selectbox(
            "Sexo", [0, 1], 
            format_func=lambda x: "Mujer" if x==0 else "Hombre"
        )
        datos_formulario['ds_edad_map'] = st.number_input("Edad", 0, 120, 75)
    
    with col2:
        datos_formulario['iotrocen_map'] = st.selectbox(
            "Otro centro", [0, 1], 
            format_func=lambda x: "No" if x==0 else "Sí"
        )
        datos_formulario['ds_centro_afueras_map'] = st.selectbox(
            "Lugar residencia", [0, 1], 
            format_func=lambda x: "Centro" if x==0 else "Afueras"
        )
    
    with col3:
        datos_formulario['gdiagalt_map'] = st.text_input("Código CIE", "S72.0")
        datos_formulario['ds_izq_der_map'] = st.selectbox(
            "Lado fractura", [0, 1], 
            format_func=lambda x: "Izquierdo" if x==0 else "Derecho"
        )
    
    # ========== CONSTANTES VITALES ==========
    st.header("Constantes vitales")
    col4, col5, col6, col7 = st.columns(4)
    
    with col4:
        datos_formulario['ntensmin_map'] = st.number_input("Tensión mín (mmHg)", 0, 200, 70)
    with col5:
        datos_formulario['ntensmax_map'] = st.number_input("Tensión máx (mmHg)", 0, 200, 120)
    with col6:
        datos_formulario['ntempera_map'] = st.number_input("Temperatura (°C)", 35.0, 42.0, 36.5, step=0.1)
    with col7:
        datos_formulario['nsatuoxi_map'] = st.number_input("Sat O2 (%)", 0, 100, 95)
    
    # ========== COMORBILIDADES ==========
    st.header("Comorbilidades")
    
    # Definir comorbilidades por columna (reduce código repetitivo)
    comorbilidades = {
        'col8': [
            ('ds_ITU_map', 'ITU'),
            ('ds_insuficiencia_respiratoria_map', 'Insuf. Respiratoria'),
            ('ds_insuficiencia_cardiaca_map', 'Insuf. Cardíaca')
        ],
        'col9': [
            ('ds_deterioro_cognitivo_map', 'Deterioro Cognitivo'),
            ('ds_insuficiencia_renal_map', 'Insuf. Renal'),
            ('ds_HTA_map', 'HTA')
        ],
        'col10': [
            ('ds_diabetes_map', 'Diabetes'),
            ('ds_obesidad_map', 'Obesidad'),
            ('ds_osteoporosis_map', 'Osteoporosis')
        ],
        'col11': [
            ('ds_anemia_map', 'Anemia'),
            ('ds_vitamina_d_map', 'Déficit Vit. D'),
            ('ds_acido_folico_map', 'Ácido fólico')
        ]
    }
    
    cols = st.columns(4)
    for idx, (col_name, items) in enumerate(comorbilidades.items()):
        with cols[idx]:
            for key, label in items:
                datos_formulario[key] = st.selectbox(
                    label, [0, 1], 
                    format_func=lambda x: "No" if x==0 else "Sí",
                    key=key  # Importante para evitar duplicados
                )
    
    # ========== ALERGIAS ==========
    st.header("Alergias")
    
    alergias = [
        ('ds_alergia_medicamentosa_map', 'Alergia medicamentosa'),
        ('ds_alergia_alimentaria_map', 'Alergia alimentaria'),
        ('ds_otra_alergias_map', 'Otras alergias')
    ]
    
    cols = st.columns(3)
    for idx, (key, label) in enumerate(alergias):
        with cols[idx]:
            datos_formulario[key] = st.selectbox(
                label, [0, 1], 
                format_func=lambda x: "No" if x==0 else "Sí",
                key=key
            )
    
    # ========== ESCALAS GERIÁTRICAS ==========
    st.header("Escalas geriátricas")
    col15, col16, col17, col18 = st.columns(4)
    
    with col15:
        datos_formulario['barthel_map'] = st.number_input("Barthel (0-100)", 0, 100, 60, step=5)
    with col16:
        datos_formulario['braden_map'] = st.number_input("Braden (6-23)", 6, 23, 18)
    with col17:
        datos_formulario['riesgo_caida_map'] = st.selectbox(
            "Riesgo caída", [0, 1, 2], 
            format_func=lambda x: ["Bajo", "Medio", "Alto"][x]
        )
    with col18:
        datos_formulario['movilidad_map'] = st.selectbox(
            "Movilidad", [0, 1, 2], 
            format_func=lambda x: ["Independiente", "Ayuda", "Dependiente"][x]
        )
    
    # ========== BOTÓN DE PREDICCIÓN ==========
    st.markdown("---")
    
    _, col_btn, _ = st.columns([1, 3, 1])
    
    with col_btn:
        if st.button("Calcular predicciones", type="primary", use_container_width=True):
            calcular_predicciones_simulador(
                datos_formulario, 
                predecir_dias_fn, 
                predecir_probabilidades_fn,
                cargar_modelo_real_fn,
                cargar_modelo_clasificacion_fn
            )

def calcular_predicciones_simulador(datos_formulario, predecir_dias_fn, predecir_probabilidades_fn,
                                     cargar_modelo_real_fn, cargar_modelo_clasificacion_fn):
    """Calcula las predicciones del simulador"""
    
    with st.spinner("Calculando predicciones..."):
        datos_para_modelo = preparar_datos_simulacion_para_modelo(datos_formulario)
        
        mod_pre, sc_pre, cols_pre = cargar_modelo_real_fn('ds_pre_oper')
        mod_post, sc_post, cols_post = cargar_modelo_real_fn('ds_post_oper')
        mod_estancia, sc_estancia, cols_estancia = cargar_modelo_real_fn('ds_estancia')
        mod_sit, sc_sit, cols_sit, clases_sit = cargar_modelo_clasificacion_fn('gsitalta')
        
        diccionario_nombres = {
            0: "Mejora", 1: "Empeora",
            "0": "Mejora", "1": "Empeora",
            1.0: "Empeora", 0.0: "Mejora"
        }
        
        st.session_state.data_simulado = datos_formulario
        st.session_state.calculo_pre_sim = predecir_dias_fn(mod_pre, sc_pre, cols_pre, datos_para_modelo)
        st.session_state.calculo_post_sim = predecir_dias_fn(mod_post, sc_post, cols_post, datos_para_modelo)
        st.session_state.calculo_estancia_sim = predecir_dias_fn(mod_estancia, sc_estancia, cols_estancia, datos_para_modelo)
        st.session_state.probs_sit_sim = predecir_probabilidades_fn(mod_sit, sc_sit, cols_sit, datos_para_modelo)
        
        if len(st.session_state.probs_sit_sim) > 0:
            st.session_state.categorias_situacion_sim = [diccionario_nombres.get(c, str(c)) for c in clases_sit]
            idx_max_sim = st.session_state.probs_sit_sim.index(max(st.session_state.probs_sit_sim))
            st.session_state.situacion_alta_sim = st.session_state.categorias_situacion_sim[idx_max_sim]
        else:
            st.session_state.categorias_situacion_sim = ["Mejora", "Empeora"]
            st.session_state.situacion_alta_sim = "N/A"
    
    st.session_state.simulacion_realizada = True
    st.rerun()


def mostrar_resultados_simulador():
    """Muestra los resultados de la simulación"""
    
    with open(f"paciente_{os.getenv('PACIENTE_ID')}.json", "r") as file:        data_raw = json.load(file)
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
    
    return gidenpac_real


def mostrar_botones_accion_simulador(gidenpac_real, generar_pdf_backend_fn, manejar_pdf_fn):
    """
    Muestra botones de acción del simulador.
    Botones siempre visibles: Nuevo y PDF
    """
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ← AÑADIR: Mostrar toast si se acaba de generar
    if st.session_state.get('mostrar_aviso_simulacion'):
        st.toast("¡PDF generado correctamente!", icon="✅")
        st.session_state['mostrar_aviso_simulacion'] = False
    
    col_nuevo, col_pdf = st.columns(2)
    
    # BOTÓN NUEVA SIMULACIÓN (siempre visible)
    with col_nuevo:
        if st.button("🔄 Nueva simulación", type="secondary", use_container_width=True):
            # Resetear estados
            st.session_state.simulacion_realizada = False
            st.session_state.pdf_simulacion_bytes = None
            st.rerun()
    
    # BOTÓN GENERAR/DESCARGAR PDF
    with col_pdf:
        # Si el PDF ya está generado, mostrar botón de descarga
        if st.session_state.get('pdf_simulacion_bytes'):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            nombre_archivo = f"simulacion_{gidenpac_real}_{timestamp}.pdf"
            
            st.download_button(
                label="📥 Descargar PDF",
                data=st.session_state['pdf_simulacion_bytes'],
                file_name=nombre_archivo,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        
        # Si no está generado, mostrar botón para generar
        else:
            if st.button("📄 Generar PDF", type="primary", use_container_width=True):
                with st.spinner("Generando PDF..."):
                    # Preparar datos para PDF
                    datos_para_pdf = {
                        **st.session_state.data_simulado,
                        "predict_preoperatorio": st.session_state.calculo_pre_sim,
                        "predict_postoperatorio": st.session_state.calculo_post_sim,
                        "predict_estancia_total": st.session_state.calculo_estancia_sim,
                        "predict_situacion_alta": st.session_state.probs_sit_sim,
                        "situacion_alta": st.session_state.situacion_alta_sim,
                        "categorias_situacion": st.session_state.categorias_situacion_sim
                    }
                    
                    pdf_bytes, error = generar_pdf_backend_fn(es_simulacion=True, datos_simulacion=datos_para_pdf)
                    
                    if pdf_bytes:
                        st.session_state['pdf_simulacion_bytes'] = pdf_bytes
                        st.session_state['mostrar_aviso_simulacion'] = True  # ← AÑADIR
                        st.rerun()
                    else:
                        st.error(f"Error al generar: {error}")