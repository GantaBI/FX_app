"""
Componentes específicos del modo simulador
"""
import streamlit as st
import json
from datetime import datetime
from utils.utils_mapeo import enriquecer_datos_para_ui, preparar_datos_simulacion_para_modelo
from utils.componentes_visualizacion import mostrar_visualizacion


def mostrar_formulario_simulador(predecir_dias_fn, predecir_probabilidades_fn, 
                                  cargar_modelo_real_fn, cargar_modelo_clasificacion_fn):
    """Muestra el formulario de entrada de datos para el simulador"""
    
    st.header("Datos del paciente")
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
    
    st.header("Constantes vitales")
    col4, col5, col6, col7 = st.columns(4)
    
    with col4:
        ntensmin_sim = st.number_input("Tensión mín (mmHg)", 0, 200, 70)
    with col5:
        ntensmax_sim = st.number_input("Tensión máx (mmHg)", 0, 200, 120)
    with col6:
        ntempera_sim = st.number_input("Temperatura (°C)", 35.0, 42.0, 36.5, step=0.1)
    with col7:
        nsatuoxi_sim = st.number_input("Sat O2 (%)", 0, 100, 95)
    
    st.header("Comorbilidades")
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
    
    st.header("Alergias")
    col12, col13, col14 = st.columns(3)
    
    with col12:
        alergia_med_sim = st.selectbox("Alergia medicamentosa", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
    with col13:
        alergia_alim_sim = st.selectbox("Alergia alimentaria", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
    with col14:
        otras_alergias_sim = st.selectbox("Otras alergias", [0, 1], format_func=lambda x: "No" if x==0 else "Sí")
    
    st.header("Escalas geriátricas")
    col15, col16, col17, col18 = st.columns(4)
    
    with col15:
        barthel_sim = st.number_input("Barthel (0-100)", 0, 100, 60, step=5)
    with col16:
        braden_sim = st.number_input("Braden (6-23)", 6, 23, 18)
    with col17:
        riesgo_caida_sim = st.selectbox("Riesgo caída", [0, 1, 2], format_func=lambda x: ["Bajo", "Medio", "Alto"][x])
    with col18:
        movilidad_sim = st.selectbox("Movilidad", [0, 1, 2], format_func=lambda x: ["Independiente", "Ayuda", "Dependiente"][x])
    
    
# BOTÓN DE PREDICCIÓN CENTRADO (1, 3, 1)
    st.markdown("---")
    
    # 1. Definimos las columnas para centrar el botón
    col_izq, col_btn, col_der = st.columns([1, 3, 1])
    
    # 2. Metemos el botón DENTRO de la columna central
    with col_btn:
        if st.button("Calcular predicciones", type="primary", use_container_width=True):
            
            # --- TU LÓGICA ORIGINAL (INTACTA) ---
            datos_formulario = {
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
    
    return gidenpac_real


def mostrar_botones_accion_simulador(gidenpac_real, generar_pdf_backend_fn):
    """Muestra botones de acción del simulador"""
    
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_reset, col_download = st.columns([1, 1])
    
    with col_reset:
        if st.button("🔄 Nueva simulación", type="secondary", use_container_width=True):
            st.session_state.simulacion_realizada = False
            st.session_state.pdf_simulacion_bytes = None
            st.rerun()
    
    with col_download:
        # CASO A: Aún no generado -> Botón Generar
        if st.session_state.pdf_simulacion_bytes is None:
            if st.button("📄 Generar PDF Simulación", type="primary", use_container_width=True):
                with st.spinner("Generando PDF de simulación..."):
                    # Preparamos los datos
                    datos_para_pdf = {
                        **st.session_state.data_simulado,
                        "predict_preoperatorio": st.session_state.calculo_pre_sim,
                        "predict_postoperatorio": st.session_state.calculo_post_sim,
                        "predict_estancia_total": st.session_state.calculo_estancia_sim,
                        "predict_situacion_alta": st.session_state.probs_sit_sim,
                        "situacion_alta": st.session_state.situacion_alta_sim,
                        "categorias_situacion": st.session_state.categorias_situacion_sim
                    }
                    
                    # Llamada a tu función backend
                    pdf_bytes, error = generar_pdf_backend_fn(es_simulacion=True, datos_simulacion=datos_para_pdf)
                    
                    if pdf_bytes:
                        st.session_state.pdf_simulacion_bytes = pdf_bytes
                        # Marcamos éxito para mostrar el aviso tras la recarga
                        st.session_state.mostrar_aviso_simulacion = True
                        st.rerun()
                    else:
                        st.error(f"Error: {error}")

        # CASO B: Generado y listo para descargar
        else:
            # 1. Notificación flotante (solo la primera vez)
            if st.session_state.get("mostrar_aviso_simulacion"):
                st.toast("¡Simulación generada correctamente!", icon="✅")
                st.session_state.mostrar_aviso_simulacion = False

            # 3. Botón de descarga
            st.download_button(
                label="📥 Descargar PDF Simulación",
                data=st.session_state.pdf_simulacion_bytes,
                file_name=f"simulacion_{gidenpac_real}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )