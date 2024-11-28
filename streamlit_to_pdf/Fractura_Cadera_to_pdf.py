import pickle
from pathlib import Path
import pandas as pd  
import plotly.express as px  
import plotly.figure_factory as ff
import streamlit as st 
import streamlit_authenticator as stauth  # pip install streamlit-authenticator==0.1.5
import streamlit as st
import numpy as np
from catboost import CatBoostRegressor
from sklearn import preprocessing
from catboost import CatBoostClassifier

# Cargar el archivo CSS
def load_css(file_path):
    with open(file_path, "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Llamar a la función para cargar estilos personalizados
load_css("custom_styles.css")
# CSS para evitar superposición y ajustar espaciado
st.markdown("""
    <style>
    /* Contenedores con margen para evitar superposición */
    .container {
        margin-bottom: 50px;
    }
    /* Evitar corte de contenido */
    .no-overlap {
        page-break-inside: avoid;
        overflow-wrap: break-word;
    }
    /* Ajustes para gráficos */
    .plot-container {
        page-break-inside: avoid;
        margin-bottom: 50px;
    }
    </style>
    """, unsafe_allow_html=True)



le = preprocessing.LabelEncoder()

st.markdown("<h1 style='text-align: center;'>Proyecto Fractura Cadera</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Modelos Predictivos y Simulador de Escenarios con Inteligencia Artificial para la Mejora del Proceso de Gestión de Pacientes Hospital San Juan de Dios-León</h2>", unsafe_allow_html=True)
st.markdown("""---""")

# # --- USER AUTHENTICATION ---
# names = ["Peter Parker", "Rebecca Miller", "demosjd@gantabi.com"]
# usernames = ["pparker", "rmiller", "demosjd@gantabi.com"]
# #passwords = ["XXX", "XXX", "demoFxCadera"]

# # load hashed passwords
# file_path = Path(__file__).parent / "hashed_pw.pkl"
# with file_path.open("rb") as file:
#     hashed_passwords = pickle.load(file)

# authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
#     "sales_dashboard", "abcdef", cookie_expiry_days=0)

# name, authentication_status, username = authenticator.login("Login", "main")

# if authentication_status == False:
#     st.error("Username/password is incorrect")

# if authentication_status == None:
#     st.warning("Please enter your username and password")

# if authentication_status:


        
    #--------------------------------SIDEBAR-------------------------------------
    #----------------------------------------------------------------------------
    
#________________ Funciones________________
def obtener_dia_semana(numero):
    dias_semana = {
        0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    return dias_semana[numero]

    
# Configuración fija de las variables con valores de ejemplo
sexo = "Mujer"  # Puede ser "Mujer" o "Hombre"
edad = 85  # Edad del paciente
fecha_llegada = "2024-11-27"  # Fecha fija de llegada
dia_llegada = "Lunes"  # Día de la semana calculado
lugar_residencia = "Domicilio"  # Puede ser "Domicilio" o "Residencia"
lugar_residencia_normal = lugar_residencia
movilidad_pre = 3  # Nivel de movilidad pre-fractura (1 a 4)
asa = 2  # Categoría ASA (1 a 4)
riesgo_caida = 7  # Riesgo de caída (1 a 10)
barthel = 60  # Índice de Barthel (0 a 100)
braden = 18  # Escala de Braden (8 a 23)
anticoagulantes = True  # Uso de anticoagulantes
polimedicamento = True  # Uso de múltiples medicamentos
pfeiffer = 5  # Cuestionario Pfeiffer (1 a 10)
deterioro_cognitivo = False  # Si hay deterioro cognitivo
alzheimer = False  # Si el paciente tiene Alzheimer
leucocitos = 12.0  # Leucocitos en 10³/µL
glucosa = 150  # Nivel de glucosa en mg/dL
urea = 70  # Nivel de urea en mg/dL
creatinina = 1.2  # Creatinina en mg/dL
ckd = 25  # Filtrado glomerular en mL/min/1.73 m²
colinesterasa = 3500  # Colinesterasa en U/L
albumina = 35  # Albúmina en g/L
vitD = 20  # Vitamina D en ng/mL
sentarse = True  # Si el paciente puede sentarse al día siguiente
sentarse_transformed = int(sentarse)
ulceras_presion = False  # Si hay úlceras por presión
ulceras_presion_transformed = int(ulceras_presion)
diabetes = True  # Si el paciente tiene diabetes
hta = True  # Hipertensión arterial
anemia = True  # Si el paciente tiene anemia
disfagia = False  # Si hay disfagia
epoc = False  # Enfermedad pulmonar obstructiva crónica
ins_cardiaca = False  # Insuficiencia cardiaca
ins_renal = False  # Insuficiencia renal
ins_respiratoria = False  # Insuficiencia respiratoria
infeccion_respiratoria = True  # Si hay infección respiratoria
itu = False  # Infección del tracto urinario
parkinson = False  # Enfermedad de Parkinson
tce = False  # Traumatismo craneoencefálico

# Datos de fractura
tipo_fractura = 2  # 1: Intracapsular no desplazada, 2: Intracapsular desplazada, etc.
tipo_fractura_normal = "Intracapsular desplazada"
lado_fractura = 1  # 1: Izquierda, 2: Derecha
lado_fractura_normal = "Izquierda"



# ____________________________________ VISUAL __________________________________________
# ______________________________________________________________________________________

# ------------------------------------- DEMORA -------------------------------------
# ------------------------------------- DEMORA -------------------------------------
with st.container():
    st.header("Predicción de Demora")

    resultado_demora = 2.8
    st.warning(f"**Predicción de demora:** {resultado_demora} días")

# ------------------------------------- ESTANCIA -----------------------------------
    st.header("Predicción de Estancia Hospitalaria")
    predict_estancia = 10.6  # Valor fijo para la predicción de estancia hospitalaria

    postoperatorio = predict_estancia - resultado_demora
    postoperatorio_fijo = predict_estancia - resultado_demora

    simulacion_total = resultado_demora + predict_estancia
    simulacion_total = round(simulacion_total, 1)

    st.warning(f"**Predicción de postoperatorio:** {postoperatorio_fijo} días")
    st.warning(f"**Predicción de estancia total:** {postoperatorio_fijo + resultado_demora} días")



# ------------------------------------- COSTES -------------------------------------
with st.container(): 
    st.header("Costes Propuestos")
    st.info("Nota precios: Los costes de intervención quirúrgica son de 3000 euros y el coste diario de la estancia son 550 euros.")

    # Valores fijos
    prediccion_costes = 7290.00  # Valor fijo de predicción de costes
    simulacion_costes = 8000.00  # Ejemplo de valor fijo para simulación de costes
    ahorro_costes = simulacion_costes - prediccion_costes  # Cálculo de ahorro basado en valores fijos

    # Mostrar resultados
    st.markdown(f"**Predicción de costes:** {prediccion_costes:.2f} €")
    st.markdown(f"**Simulación de costes:** {simulacion_costes:.2f} €")
    st.markdown(f"**Ahorro de costes:** {ahorro_costes:.2f} €")

    # Gráfico
    d = {
        'Coste': ["Coste demora", "Coste intervención", "Coste postoperatorio",
                  "Coste demora", "Coste intervención", "Coste postoperatorio"],
        'Euros': [2000, 3000, 2290, 2500, 3000, 2500],  # Valores ejemplo para predicción y simulación
        'Coste total': ['Predicción', 'Predicción', 'Predicción', 'Simulación', 'Simulación', 'Simulación']
    }
    df = pd.DataFrame(data=d)
    fig = px.bar(
        df, y="Coste total", x="Euros", color="Coste", orientation='h',
        title="Gráfico de Costes", color_discrete_map={
            "Coste demora": "#1f77b4", "Coste intervención": "#33BEFF", "Coste postoperatorio": "#33FF71"
        }
    )
    fig.update_layout(autosize=True, margin=dict(l=20, r=20, t=30, b=30), width=800, height=400)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<div class='no-overlap'></div>", unsafe_allow_html=True)

# ----------------------------------- DESTINO ALTA ----------------------------------
# -----------------------------------------------------------------------------------

with st.container():
    st.markdown("<div class='no-overlap'></div>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)  # Dos líneas vacías

    # Valores fijos
    destino = ['Domicilio', 'Fallecido', 'Hospitalización Agudos', 'Residencia/Institucionalizado']
    predict_destino_alta = [0.65, 0.05, 0.20, 0.10]  # Ejemplo de valores de predicción en porcentaje
    simu_destino_alta = [0.70, 0.03, 0.15, 0.12]  # Ejemplo de valores de simulación en porcentaje

    # Cálculo de diferencias
    difference = np.array(simu_destino_alta) - np.array(predict_destino_alta)
    d = {
        'Destino': destino,
        'Porcentaje predicción': predict_destino_alta,
        'Porcentaje simulación': simu_destino_alta,
        'Diferencias': difference
    }

    # DataFrame
    df = pd.DataFrame(data=d)

    # Título y tabla
    st.subheader('Probabilidad de destino al alta')
    df_tabla = df.copy()
    df_tabla['Porcentaje predicción'] = df_tabla['Porcentaje predicción'].transform(lambda x: '{:,.2%}'.format(x))
    df_tabla['Porcentaje simulación'] = df_tabla['Porcentaje simulación'].transform(lambda x: '{:,.2%}'.format(x))
    df_tabla['Diferencias'] = df_tabla['Diferencias'].transform(lambda x: '{:,.2%}'.format(x))

    st.dataframe(df_tabla)  # Mostrar la tabla en Streamlit

    # Gráfico circular
    import plotly.express as px
    fig_pie = px.pie(
        df, values='Porcentaje simulación', names='Destino', 
        title="Probabilidad de destino simulación al alta", 
        color='Destino',
        category_orders={"Destino": ['Residencia/Institucionalizado', 'Domicilio', 'Hospitalización Agudos', 'Fallecido']}
    )
    st.plotly_chart(fig_pie, use_container_width=True)



# --------------------------------------- MOVILIDAD ALTA --------------------------------------
# ---------------------------------------------------------------------------------------------

with st.container():
    # Valores fijos
    movilidad = ['Completamente inmóvil', 'Muy limitada', 'Ligeramente limitada', 'Sin limitaciones']
    predict_movilidad_alta = [0.10, 0.25, 0.40, 0.25]  # Ejemplo de valores de predicción en porcentaje
    simu_movilidad_alta = [0.08, 0.20, 0.50, 0.22]  # Ejemplo de valores de simulación en porcentaje

    # Cálculo de diferencias
    difference = np.array(simu_movilidad_alta) - np.array(predict_movilidad_alta)
    d = {
        'Movilidad': movilidad,
        'Porcentaje predicción': predict_movilidad_alta,
        'Porcentaje simulación': simu_movilidad_alta,
        'Diferencias': difference
    }

    # DataFrame
    df = pd.DataFrame(data=d)

    # Título y tabla
    st.subheader('Probabilidad de movilidad al alta')
    df_tabla = df.copy()
    df_tabla['Porcentaje predicción'] = df_tabla['Porcentaje predicción'].transform(lambda x: '{:,.2%}'.format(x))
    df_tabla['Porcentaje simulación'] = df_tabla['Porcentaje simulación'].transform(lambda x: '{:,.2%}'.format(x))
    df_tabla['Diferencias'] = df_tabla['Diferencias'].transform(lambda x: '{:,.2%}'.format(x))

    st.dataframe(df_tabla)  # Mostrar la tabla en Streamlit

    # Gráfico circular
    import plotly.express as px
    fig_pie = px.pie(
        df, values='Porcentaje simulación', names='Movilidad', 
        title="Probabilidad de Movilidad simulación al alta", 
        color='Movilidad',
        category_orders={"Movilidad": ['Ligeramente limitada', 'Sin limitaciones', 'Muy limitada', 'Completamente inmóvil']}
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Separador visual
    st.markdown("<div class='no-overlap'></div>", unsafe_allow_html=True)


# --------------------------VIVO A LOS 30 DIAS ------------------------
# ---------------------------------------------------------------------
with st.container():
    st.markdown("<div class='no-overlap'></div>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)  # Dos líneas vacías

    # Valores fijos para las probabilidades de predicción y simulación
    situacion = ['Fallece', 'Vivo a 30 días']
    predict_vivo_alta = [0.15, 0.85]  # Probabilidad fija para predicción
    simu_vivo_alta = [0.10, 0.90]    # Probabilidad fija para simulación

    # Cálculo de diferencias
    difference = np.array(simu_vivo_alta) - np.array(predict_vivo_alta)
    d = {
        'Situación': situacion,
        'Porcentaje predicción': predict_vivo_alta,
        'Porcentaje simulación': simu_vivo_alta,
        'Diferencias': difference
    }

    # DataFrame
    df = pd.DataFrame(data=d)

    # Título y tabla
    st.subheader('Probabilidad de Vivo a los 30 días')
    df_tabla = df.copy()
    df_tabla['Porcentaje predicción'] = df_tabla['Porcentaje predicción'].transform(lambda x: '{:,.2%}'.format(x))
    df_tabla['Porcentaje simulación'] = df_tabla['Porcentaje simulación'].transform(lambda x: '{:,.2%}'.format(x))
    df_tabla['Diferencias'] = df_tabla['Diferencias'].transform(lambda x: '{:,.2%}'.format(x))

    st.dataframe(df_tabla)  # Mostrar la tabla en Streamlit

    # Gráfico circular
    import plotly.express as px
    fig_pie = px.pie(
        df, values='Porcentaje simulación', names='Situación', 
        title="Probabilidad de Vivo al alta simulación", 
        color='Situación',
        category_orders={"Situación": ['Fallece', 'Vivo a 30 días']},
        color_discrete_sequence=['#ff2b2b', '#83c9ff']
    )

    st.plotly_chart(fig_pie, use_container_width=True)
