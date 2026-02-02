"""
Componentes de visualización compartidos entre el modo paciente y simulador
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

# Configurar zona horaria
zona_horaria = pytz.timezone('Europe/Madrid')


def crear_tabla_y_grafico(titulo, categorias, porcentajes, orden, colores=None):
    """Crea tabla y gráfico de pastel para probabilidades"""
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


def mostrar_visualizacion(data, predict_preoperatorio, predict_postoperatorio, predict_estancia_total, 
                          predict_situacion_alta, situacion_alta, categorias_situacion, 
                          es_simulacion=False, gidenpac="Simulación"):
    """Muestra la visualización completa del paciente o simulación"""
    
    diccionario_colores = { 
        "Mejora": "#09AB3B",
        "Empeora": "#FF2B2B"
    }
    
    # Fecha/Hora actual (Madrid)
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
    
    if es_simulacion:
        st.warning(f"**ID paciente: {gidenpac} - SIMULACIÓN**")
    else:
        st.success(f"**ID paciente: {gidenpac}**")
    
    # Extraer valores
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
    st.caption("ℹ️ Cada predicción proviene de un modelo independiente. La estancia total no es necesariamente la suma de pre y post-operatorio, ya que considera patrones globales del proceso completo de hospitalización.")

    
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

    ntensmin_fmt = f"{ntensmin:.0f}" if isinstance(ntensmin, (int, float)) else ntensmin
    ntensmax_fmt = f"{ntensmax:.0f}" if isinstance(ntensmax, (int, float)) else ntensmax
    ntempera_fmt = f"{ntempera:.1f}" if isinstance(ntempera, (int, float)) else ntempera
    nsatuoxi_fmt = f"{nsatuoxi:.0f}" if isinstance(nsatuoxi, (int, float)) else nsatuoxi

    tabla_constantes = pd.DataFrame({
        "Variable": ["Tensión mínima","Tensión máxima", "Temperatura", "Saturación Oxígeno Respiratoria"],
        "Valor": [ntensmin_fmt, ntensmax_fmt, ntempera_fmt, nsatuoxi_fmt]
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