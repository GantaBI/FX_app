import pandas as pd  
import plotly.express as px  
import streamlit as st 
import streamlit as st
import json

# Cargar el archivo CSS
def load_css(file_path):
    with open(file_path, "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Llamar a la función para cargar estilos personalizados
load_css("custom_styles.css")

# ___________________________________________________ VARIABLES _________________________________________
# _______________________________________________________________________________________________________
# Cargar datos desde el archivo JSON
with open("data_paciente.json", "r") as file:
    data = json.load(file)

# Asignar variables desde el JSON
id_paciente = data["id_paciente"]
sexo = data["sexo"]
edad = data["edad"]
tipo_ingreso = data["tipo_ingreso"]
reingreso = data["reingreso"]
fecha_ingreso = data["fecha_ingreso"]
lugar_residencia = data["lugar_residencia"]
tipo_fractura = data["tipo_fractura"]
lado_fractura = data["lado_fractura"]
predict_preoperatorio = data["predict_preoperatorio"]
predict_postoperatorio = data["predict_postoperatorio"]
predict_destino_alta = data["predict_destino_alta"]
destino_alta = data["destino_alta"]
predict_movilidad_alta = data["predict_movilidad_alta"]
movilidad_alta = data["movilidad_alta"]
predict_situacion_alta = data["predict_situacion_alta"]
situacion_alta = data["situacion_alta"]
predict_vivo_alta = data["predict_vivo_alta"]
vivo_alta = data["vivo_alta"]
# Enfermedades
itu = data["itu"]
anemia = data["anemia"]
vitamina_d = data["vitamina_d"]
insuficiencia_respiratoria = data["insuficiencia_respiratoria"]
insuficiencia_cardiaca = data["insuficiencia_cardiaca"]
deterioro_cognitivo = data["deterioro_cognitivo"]
insuficiencia_renal = data["insuficiencia_renal"]
hta = data["hta"]
diabetes = data["diabetes"]

barthel = data["barthel"]
braden = data["braden"]
riesgo_caida = data["riesgo_caida"]
movilidad = data["movilidad"]



# ____________________________________ VISUAL __________________________________________
# ______________________________________________________________________________________
# Obtener la fecha actual
import streamlit as st
from datetime import datetime
fecha_actual = datetime.now().strftime("%Y-%m-%d")

# Posicionar la fecha en la esquina superior derecha
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

st.markdown("<h1 style='text-align: center;'>Predicción de Fractura de Cadera</h1>", unsafe_allow_html=True)
st.markdown("""---""")

# ----------------------------------- DATOS PACIENTE ------------------------------
st.header("Datos del paciente")
st.success(f"**ID paciente: {id_paciente}**")

tabla_resumen = pd.DataFrame({
    "Variable": ["Sexo", "Edad", "Tipo de ingreso","Reingreso", "Lugar de residencia", "Tipo de fractura", "Lado de fractura"],
    "Valor": [sexo, edad, tipo_ingreso, reingreso, lugar_residencia, tipo_fractura, lado_fractura]
})

st.subheader("Resumen paciente")
st.table(tabla_resumen)

# _____________________________________________ RESUMEN PREDICCIONES ______________________________
#__________________________________________________________________________________________________

# ------------------------------------- ESTANCIA -------------------------------------
with st.container():
    st.header("Resumen predicciones")
    st.subheader("Estancia")

    st.info(f"**Pre-operatorio:** {predict_preoperatorio} días")
    st.info(f"**Post-operatorio:** {predict_postoperatorio} días")
    st.info(f"**Estancia total:** {predict_postoperatorio + predict_preoperatorio} días")

# ------------------------------------- SITUACION AL ALTA -----------------------------------
    st.subheader("Situacion al alta")
    st.info(f"**Destino:** {destino_alta}")
    st.info(f"**Movilidad:** {movilidad_alta}")
    st.info(f"**Situación:** {situacion_alta}")
    st.info(f"**Vive/Fallece:** {vivo_alta}")


    st.markdown("<div class='no-overlap'></div>", unsafe_allow_html=True)
    
# ----------------------------------- ENFERMEDADES  ------------------------------
st.markdown("<div class='no-overlap'></div>", unsafe_allow_html=True)
st.header("Enfermedades del paciente")

tabla_enfermedades = pd.DataFrame({
    "Variable": ["ITU","Anemia", "Déficit Vitamina D", "Insuficiencia Respiratoria","Insuficiencia Cardíaca", "Deterioro Cognitivo", "Insuficiencia Renal", "HTA", "Diabetes"],
    "Valor": [itu,anemia, vitamina_d, insuficiencia_respiratoria, insuficiencia_cardiaca, deterioro_cognitivo, insuficiencia_renal, hta, diabetes]
})

st.table(tabla_enfermedades)

# ----------------------------------- GERIATRIA  ------------------------------
st.header("Geriatría")

tabla_enfermedades = pd.DataFrame({
    "Variable": ["Escala de Barthel","Escala de Braden", "Riesgo caida", "Movilidad"],
    "Valor": [barthel,braden, riesgo_caida, movilidad]
})

st.table(tabla_enfermedades)
st.markdown("<div class='no-overlap'></div>", unsafe_allow_html=True)


# _____________________________________________ GRAFICOS Y TABLAS _________________________________
#__________________________________________________________________________________________________

def crear_tabla_y_grafico(titulo, categorias, porcentajes, orden, colores=None):
    """
    Crea y muestra una tabla y un gráfico circular a partir de las categorías y porcentajes proporcionados.
    """
    # Crear DataFrame
    data = {"Categoría": categorias, "Porcentaje predicción": porcentajes}
    df = pd.DataFrame(data)

    # Formatear porcentaje en la tabla
    df_tabla = df.copy()
    df_tabla["Porcentaje predicción"] = df_tabla["Porcentaje predicción"].apply(lambda x: f"{x*100:.0f}%")

    # Mostrar tabla
    st.subheader(titulo)
    st.dataframe(df_tabla)

    # Crear gráfico circular
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

# ----------------------------------- DESTINO ALTA ----------------------------------
with st.container():
    st.markdown("<div class='no-overlap'></div>", unsafe_allow_html=True)
    st.header("Gráficos y Estadísticas")

    crear_tabla_y_grafico(
    titulo="Probabilidad de destino al alta",
    categorias=["Domicilio", "Fallecido", "Hospitalización Agudos", "Residencia/Institucionalizado"],
    porcentajes=predict_destino_alta,
    orden=["Residencia/Institucionalizado", "Domicilio", "Hospitalización Agudos", "Fallecido"],
)

# --------------------------------------- MOVILIDAD ALTA --------------------------------------
with st.container():
    crear_tabla_y_grafico(
    titulo="Probabilidad de movilidad al alta",
    categorias=["Completamente inmóvil", "Muy limitada", "Ligeramente limitada", "Sin limitaciones"],
    porcentajes=predict_movilidad_alta,
    orden=["Ligeramente limitada", "Sin limitaciones", "Muy limitada", "Completamente inmóvil"],
)

    # Separador visual
    st.markdown("<div class='no-overlap'></div>", unsafe_allow_html=True)

# -------------------------- SITUACION AL ALTA ------------------------
with st.container():
    st.markdown("<div class='no-overlap'></div>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)  # Dos líneas vacías

    crear_tabla_y_grafico(
    titulo="Probabilidad de situación al alta",
    categorias=["Curación total", "Mejoría", "Sin cambios", "Agravamiento", "In extremis", "Con secuelas", "Exitus", "Mejoria a residencia"],
    porcentajes=predict_situacion_alta,
    orden=["Curación total", "Mejoría", "Sin cambios", "Agravamiento", "In extremis", "Con secuelas", "Exitus", "Mejoria a residencia"],
)
    
    # -------------------------- VIVO AL ALTA ------------------------
with st.container():
    crear_tabla_y_grafico(
    titulo="Probabilidad de Vivo al alta",
    categorias=["Fallece", "Vivo"],
    porcentajes=predict_vivo_alta,
    orden=["Fallece", "Vivo"],
)