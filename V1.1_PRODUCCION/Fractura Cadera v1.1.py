import pickle
from pathlib import Path
import pandas as pd  
import plotly.express as px  
import plotly.figure_factory as ff
import streamlit as st 
import streamlit_authenticator as stauth  # pip install streamlit-authenticator==0.1.5
import streamlit as st
import numpy as np
import time
from catboost import CatBoostRegressor
from sklearn import preprocessing
import datetime
from catboost import CatBoostClassifier


#import matplotlib.pyplot as plt
#import plotly.express as px
#from pandas_profiling import ProfileReport
#import pandas_profiling
#from streamlit_pandas_profiling import st_profile_report
#import h2o
#from streamlit_pandas_profiling import st_profile_report


VERSION = "v1.1"
le = preprocessing.LabelEncoder()

st.markdown("<h1 style='text-align: center;'>Proyecto Fractura Cadera</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Modelos Predictivos y Simulador de Escenarios con Inteligencia Artificial para la Mejora del Proceso de Gestión de Pacientes Hospital San Juan de Dios-León</h2>", unsafe_allow_html=True)
st.markdown("""---""")

# --- USER AUTHENTICATION ---
names = ["Peter Parker", "Rebecca Miller", "demosjd@gantabi.com"]
usernames = ["pparker", "rmiller", "demosjd@gantabi.com"]
#passwords = ["XXX", "XXX", "demoFxCadera"]

# load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "sales_dashboard", "abcdef", cookie_expiry_days=0)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:


        
    #--------------------------------SIDEBAR-------------------------------------
    #----------------------------------------------------------------------------
    
    #________________ Funciones________________
    def obtener_dia_semana(numero):
        dias_semana = {
            0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
        return dias_semana[numero]
    
    
    st.sidebar.title("Variables de Triaje")
    st.sidebar.subheader("Datos paciente")

    sexo = st.sidebar.radio("Sexo", [ "Mujer", "Hombre"])
    edad = st.sidebar.slider("Edad",70, 110,92)
    fecha_llegada = st.sidebar.date_input("Fecha de llegada a urgencias")
    dia_llegada = fecha_llegada.weekday()
    dia_llegada = obtener_dia_semana(dia_llegada)
    le.fit(["Domicilio", "Residencia",'Hospitalizado'])
    lugar_residencia = st.sidebar.selectbox("Lugar de residencia", ["Domicilio", "Residencia"])
    lugar_residencia_normal = lugar_residencia
    lugar_residencia = le.transform([lugar_residencia])[0] + 1

    st.sidebar.subheader("Geriatría")
    movilidad_pre = st.sidebar.slider("Movilidad Pre-Fractura",1, 4, 3)
    st.sidebar.markdown("<span style='color:gray;font-size:90%'>Menor movilidad(1) - Mayor movilidad(4)</span>", unsafe_allow_html=True)
    asa = st.sidebar.slider("Categoría ASA",1, 4, 3)
    st.sidebar.markdown("<span style='color:gray;font-size:90%'>Sano(1) - Enf. Incapacitante(4)</span>", unsafe_allow_html=True)
    riesgo_caida = st.sidebar.slider("Riesgo caida",1, 10)
    if "riesgo_caida_anterior" in st.session_state and st.session_state.riesgo_caida_anterior != riesgo_caida:
        st.sidebar.warning("Dato no disponible")
    st.session_state.riesgo_caida_anterior = riesgo_caida

    barthel = st.sidebar.slider("Barthel",0, 100)
    if "barthel_anterior" in st.session_state and st.session_state.barthel_anterior != barthel:
        st.sidebar.warning("Dato no disponible")
    st.session_state.barthel_anterior = barthel

    braden = st.sidebar.slider("Braden",8, 23)
    if "braden_anterior" in st.session_state and st.session_state.braden_anterior != braden:
        st.sidebar.warning("Dato no disponible")
    st.session_state.braden_anterior = braden

    anticoagulantes = st.sidebar.checkbox("Anticoagulantes")
    if "Anticoagulantes_anterior" in st.session_state and st.session_state.Anticoagulantes_anterior != anticoagulantes:
        st.sidebar.warning("Dato no disponible")
    st.session_state.Anticoagulantes_anterior = anticoagulantes
    
    polimedicamento = st.sidebar.checkbox("Polimedicamento")
    polimedicamento = int(polimedicamento)
    if "polimedicamento_anterior" in st.session_state and st.session_state.polimedicamento_anterior != polimedicamento:
        st.sidebar.warning("Dato no disponible")
    st.session_state.polimedicamento_anterior = polimedicamento


    st.sidebar.subheader("Salud mental")
    pfeiffer = st.sidebar.slider("Cuestionario Pfeiffer",1, 10,7)
    deterioro_cognitivo = st.sidebar.checkbox("Deterioro cognitivo")
    deterioro_cognitivo = int(deterioro_cognitivo)
    if "deterioro_cognitivo_anterior" in st.session_state and st.session_state.deterioro_cognitivo_anterior != deterioro_cognitivo:
        st.sidebar.warning("Dato no disponible")
    st.session_state.deterioro_cognitivo_anterior = deterioro_cognitivo
    alzheimer = st.sidebar.checkbox("Alzheimer")
    alzheimer = int(alzheimer)
    if "alzheimer_anterior" in st.session_state and st.session_state.alzheimer_anterior != alzheimer:
        st.sidebar.warning("Dato no disponible")
    st.session_state.alzheimer_anterior = alzheimer

    st.sidebar.subheader("Datos médicos")
    leucocitos = st.sidebar.slider("Leucocitos (10³/µL)",1.0, 30.0, 10.2)
    glucosa = st.sidebar.slider("Glucosa (mg/dL)",70, 300, 92)
    urea = st.sidebar.slider("Urea (mg/dL)",17, 180, 53)
    creatinina = st.sidebar.slider("Creatinina (mg/dL)",0.2, 3.0, 0.38)
    ckd = st.sidebar.slider("CKD (mL/min/1.73 m²)",10, 91,20)
    st.sidebar.markdown("<span style='color:gray;font-size:90%'>Para &gt;90 introducir 91</span>", unsafe_allow_html=True)

    colinesterasa = st.sidebar.slider("Colinesterasa (U/L)",2000, 10000, 2751)
    albumina = st.sidebar.slider("Albúmina (g/L)",20, 60, 25)
    vitD = st.sidebar.slider("Vitamina D (ng/mL)",0, 55,15)

    sentarse = st.sidebar.checkbox("Se sienta al día siguiente")
    sentarse_transformed = int(sentarse)
    if "sentarse_anterior" in st.session_state and st.session_state.sentarse_anterior != sentarse:
        st.sidebar.warning("Dato no disponible")
    st.session_state.sentarse_anterior = sentarse

    ulceras_presion = st.sidebar.checkbox("Úlceras por presión")
    ulceras_presion_transformed = int(ulceras_presion)
    if "ulceras_presion_anterior" in st.session_state and st.session_state.ulceras_presion_anterior != ulceras_presion:
        st.sidebar.warning("Dato no disponible")
    st.session_state.ulceras_presion_anterior = ulceras_presion

    diabetes = st.sidebar.checkbox("Diabetes")
    diabetes = int(diabetes)
    if "diabetes_anterior" in st.session_state and st.session_state.diabetes_anterior != diabetes:
        st.sidebar.warning("Dato no disponible")
    st.session_state.diabetes_anterior = alzheimer

    hta = st.sidebar.checkbox("HTA")
    hta = int(hta)
    if "hta_anterior" in st.session_state and st.session_state.alzheimer_anterior != hta:
        st.sidebar.warning("Dato no disponible")
    st.session_state.hta_anterior = hta

    anemia = st.sidebar.checkbox("Anemia")
    anemia = int(anemia)
    if "anemia_anterior" in st.session_state and st.session_state.alzheimer_anterior != anemia:
        st.sidebar.warning("Dato no disponible")
    st.session_state.anemia_anterior = anemia

    disfagia = st.sidebar.checkbox("Disfagia")
    disfagia = int(disfagia)
    if "disfagia_anterior" in st.session_state and st.session_state.alzheimer_anterior != disfagia:
        st.sidebar.warning("Dato no disponible")
    st.session_state.disfagia_anterior = disfagia

    epoc = st.sidebar.checkbox("EPOC")
    epoc = int(epoc)
    if "epoc_anterior" in st.session_state and st.session_state.alzheimer_anterior != epoc:
        st.sidebar.warning("Dato no disponible")
    st.session_state.epoc_anterior = epoc

    ins_cardiaca = st.sidebar.checkbox("Insuficiencia cardiaca")
    ins_cardiaca = int(ins_cardiaca)
    if "ins_cardiaca_anterior" in st.session_state and st.session_state.alzheimer_anterior != ins_cardiaca:
        st.sidebar.warning("Dato no disponible")
    st.session_state.ins_cardiaca_anterior = ins_cardiaca

    ins_renal = st.sidebar.checkbox("Insuficiencia renal")
    ins_renal = int(ins_renal)
    if "ins_renal_anterior" in st.session_state and st.session_state.alzheimer_anterior != ins_renal:
        st.sidebar.warning("Dato no disponible")
    st.session_state.ins_renal_anterior = ins_renal

    ins_respiratoria = st.sidebar.checkbox("Insuficiencia respiratoria")
    ins_respiratoria = int(ins_respiratoria)
    if "ins_respiratoria_anterior" in st.session_state and st.session_state.alzheimer_anterior != ins_respiratoria:
        st.sidebar.warning("Dato no disponible")
    st.session_state.ins_respiratoria_anterior = ins_respiratoria

    infeccion_respiratoria = st.sidebar.checkbox("Infección respiratoria")
    infeccion_respiratoria = int(infeccion_respiratoria)
    if "infeccion_respiratoria_anterior" in st.session_state and st.session_state.alzheimer_anterior != infeccion_respiratoria:
        st.sidebar.warning("Dato no disponible")
    st.session_state.infeccion_respiratoria_anterior = infeccion_respiratoria

    itu = st.sidebar.checkbox("ITU")
    itu = int(itu)
    if "itu_anterior" in st.session_state and st.session_state.alzheimer_anterior != itu:
        st.sidebar.warning("Dato no disponible")
    st.session_state.itu_anterior = itu

    parkinson = st.sidebar.checkbox("Parkinson")
    parkinson = int(parkinson)
    if "parkinson_anterior" in st.session_state and st.session_state.alzheimer_anterior != parkinson:
        st.sidebar.warning("Dato no disponible")
    st.session_state.parkinson_anterior = parkinson

    tce = st.sidebar.checkbox("TCE")
    tce = int(tce)
    if "tce_anterior" in st.session_state and st.session_state.alzheimer_anterior != tce:
        st.sidebar.warning("Dato no disponible")
    st.session_state.tce_anterior = tce

    st.sidebar.subheader("Datos Fractura")
    tipo_fractura = st.sidebar.selectbox("Tipo de Fractura", ["Intracapsular no desplazada","Intracapuslar desplazada","Pertrocantérea","Subtrocantérea","Otra"], index=2)
    tipo_fractura_normal = tipo_fractura

    tipos_fractura = [ "Intracapsular no desplazada","Intracapuslar desplazada","Pertrocantérea","Subtrocantérea","Otra"]
    tipo_fractura = tipos_fractura.index(tipo_fractura) + 1

    lado_fractura = st.sidebar.radio("Lado fractura", ["Izquierda", "Derecha"], index=0)
    lado_fractura_normal = lado_fractura
    if lado_fractura == "Izquierda":
        lado_fractura = 1
    else:
        lado_fractura = 2

    st.sidebar.markdown(f"Versión: {VERSION}")




    #------------------------------------------------------------------ PREDICCIONES --------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------------------------
    # %%
    st.markdown("<span style='color:gray;font-size:90%'>Nota uso: Las predicciones se obtienen de las variables que aparecen en el lateral izquierdo. Las simulaciones surgen de los cambios que realizas en las variables de Demora y Postoperatorio</span>", unsafe_allow_html=True)
    st.header('Días en el hospital')


    #____________________________DEMORA___________________________________
    model_demora = CatBoostRegressor()


    #if modelo == "Datos RNFC":

    #model_demora.load_model("model")
    #predcit = model_demora.predict([sexo, edad])
    #predcit = predcit.round(1)
    model_demora.load_model("models/model_ds_demora_dias_rnfc")
    predcit = model_demora.predict([sexo, edad, lugar_residencia_normal, movilidad_pre,  pfeiffer, asa, lado_fractura_normal, \
    tipo_fractura_normal, sentarse_transformed, ulceras_presion_transformed ,leucocitos, glucosa,urea, creatinina, \
        ckd ,colinesterasa ,albumina, vitD,dia_llegada])
    predcit = predcit.round(1)

    #else:
    #    # carga tu modelo de demora
    #    #model_demora.load_model("model_ds_intervencion_dias")
    #    model_demora.load_model("model_ds_intervencion_dias_date2")
    #
    #
    #    predcit = model_demora.predict([sexo, edad, lugar_residencia_normal, movilidad_pre,riesgo_caida, barthel, braden,deterioro_cognitivo,
    #    alzheimer,diabetes,hta,anemia,disfagia,epoc,ins_respiratoria,ins_cardiaca,ins_renal,infeccion_respiratoria,
    #    itu,parkinson,tce,tipo_fractura_normal,lado_fractura_normal,dia_llegada])
    #    predcit = predcit.round(1)


    resultado_demora = st.slider("Demora hasta operar", min_value=0.0, max_value=10.0, value=float(predcit), step=None, format=None)

    st.write('###### Predicción de demora:', predcit, "días")


    # Estancia dias
    model_estancia_dias = CatBoostRegressor()

    #if modelo == "Datos RNFC":
    #model_estancia_dias.load_model("model_estancia_dias")
    #predict_estancia = model_estancia_dias.predict([ sexo, movilidad_pre,  edad, pfeiffer, asa, lado_fractura_normal, \
    #tipo_fractura_normal, sentarse_transformed, ulceras_presion_transformed ,leucocitos, glucosa,urea, creatinina, \
    #    ckd ,colinesterasa ,albumina, vitD, resultado_demora])
    #predict_estancia = predict_estancia.round(1)
    #predict_estancia_fijo = model_estancia_dias.predict([sexo, movilidad_pre,  edad, pfeiffer, asa, lado_fractura_normal, \
    #tipo_fractura_normal, sentarse_transformed, ulceras_presion_transformed ,leucocitos, glucosa,urea, creatinina, \
    #    ckd ,colinesterasa ,albumina, vitD, predcit])
    #predict_estancia_fijo = predict_estancia_fijo.round(1)
    
    model_estancia_dias.load_model("models/model_ds_estancia_dias_rnfc")
    predict_estancia = model_estancia_dias.predict([sexo, edad, lugar_residencia_normal, movilidad_pre,  pfeiffer, asa, lado_fractura_normal, \
    tipo_fractura_normal, resultado_demora, sentarse_transformed, ulceras_presion_transformed ,leucocitos, glucosa,urea, creatinina, \
        ckd ,colinesterasa ,albumina, vitD,dia_llegada])

    predict_estancia +=2

    predict_estancia = predict_estancia.round(1)
    predict_estancia_fijo = model_estancia_dias.predict([sexo, edad, lugar_residencia_normal, movilidad_pre,  pfeiffer, asa, lado_fractura_normal, \
    tipo_fractura_normal, predcit, sentarse_transformed, ulceras_presion_transformed ,leucocitos, glucosa,urea, creatinina, \
        ckd ,colinesterasa ,albumina, vitD,dia_llegada])

    predict_estancia_fijo +=2

    predict_estancia_fijo = predict_estancia_fijo.round(1)

    #else:
    #    #pon aqui tu modelo 2 veces con los nombres predict_estancia(con la demora "resultado_demora") y  predict_estancia_fijo con la demora predicha desde el modelo
    #    #model_estancia_dias.load_model("model_ds_estancia_dias")
    #    model_estancia_dias.load_model("model_ds_estancia_dias_date2")
    #
    #
    #    predict_estancia = model_estancia_dias.predict([sexo, edad, lugar_residencia_normal, movilidad_pre,riesgo_caida, barthel, braden,deterioro_cognitivo,
    #    alzheimer,diabetes,hta,anemia,disfagia,epoc,ins_respiratoria,ins_cardiaca,ins_renal,infeccion_respiratoria,itu,parkinson,tce,
    #    tipo_fractura_normal,lado_fractura_normal, dia_llegada,resultado_demora])
    #
    #
    #
    #    predict_estancia_fijo = model_estancia_dias.predict([sexo, edad, lugar_residencia_normal, movilidad_pre,riesgo_caida, barthel, braden,deterioro_cognitivo,
    #    alzheimer,diabetes,hta,anemia,disfagia,epoc,ins_respiratoria,ins_cardiaca,ins_renal,infeccion_respiratoria,itu,parkinson,tce,
    #    tipo_fractura_normal,lado_fractura_normal, dia_llegada, predcit])
    #    predict_estancia_fijo = predict_estancia_fijo.round(1)
    #
    #    #pon aqui tu modelo 2 veces con los nombres predict_estancia(con la demora "resultado_demora") y  predict_estancia_fijo con la demora predicha desde el modelo
    #    pass


    postoperatorio = predict_estancia - predcit
    postoperatorio = postoperatorio.round(1)

    postoperatorio_fijo = predict_estancia_fijo - predcit
    postoperatorio_fijo = postoperatorio_fijo.round(1)


    resultado_post = st.slider("Postoperatorio", min_value=0.0, max_value=20.0, value=float(postoperatorio), step=None, format=None)

    st.write('###### Predicción de postoperatorio:', postoperatorio_fijo, "días")
    st.write(' ')
    st.write('##### Predicción de estancia total:', postoperatorio_fijo+predcit, "días")
    simulacion_total = resultado_demora + resultado_post
    simulacion_total = round(simulacion_total,1)
    st.write('##### Simulación de estancia total: ',simulacion_total, "días")

    # ------------------------------------- COSTES ----------------------------------
    # -------------------------------------------------------------------------------
    # metricas
    precio_dia = 550
    coste_intervencion = 3000

    # GASTOS
    coste_postoperatorio_simu = precio_dia * resultado_post
    coste_postoperatorio_predict = precio_dia * postoperatorio_fijo

    coste_demora_simu = precio_dia * resultado_demora
    coste_demora_predict = precio_dia * predcit

    st.header('Costes propuestos')
    st.markdown("<span style='color:gray;font-size:90%'>Nota precios: Los costes de intervención quirúrgica son de 3000 euros y el coste diario de la estancia son 550 euros</span>", unsafe_allow_html=True)    
    st.markdown("<span style='color:gray;font-size:90%'>Nota Predicción: es lo obtenido en base a las variables seleccionadas</span>", unsafe_allow_html=True)    
    st.markdown("<span style='color:gray;font-size:90%'>Nota Simulación: es lo obtenido en base a los cambios realizados en las variables de Demora y Postoperatorio</span>", unsafe_allow_html=True)    


    st.write('###### Predicción de costes', coste_demora_predict + coste_intervencion + coste_postoperatorio_predict, "€")
    st.write('###### Simulación de costes', coste_demora_simu + coste_intervencion + coste_postoperatorio_simu, "€")
    st.write('###### Ahorro de costes',((coste_demora_simu + coste_intervencion + coste_postoperatorio_simu) - (coste_demora_predict + coste_intervencion + coste_postoperatorio_predict))* -1, "€")


    # GRAFICO
    d = {'Coste': ["Coste demora", "Coste intervención", "Coste postoperatorio", "Coste demora", "Coste intervención", "Coste postoperatorio"], 
    'Euros': [ coste_demora_predict, coste_intervencion, coste_postoperatorio_predict, coste_demora_simu, coste_intervencion, coste_postoperatorio_simu], 
    'Coste total': ['Predición','Predición','Predición','Simulación','Simulación','Simulación']}
    df = pd.DataFrame(data=d)

    fig = px.bar(df, y="Coste total", x="Euros", color="Coste", orientation='h',
                color_discrete_map={
                    "Coste demora": "#1f77b4",
                    "Coste intervención": "#33BEFF",
                    "Coste postoperatorio": "#33FF71"},
                title="Gráfico de costes")

    fig.update_layout(xaxis_range=[0,15000])
    fig.update_traces(width=0.5)
    fig.update_layout(bargap=0.2)

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------- DESTINO ALTA ----------------------------------
    # -----------------------------------------------------------------------------------

    model_destino_alta = CatBoostClassifier()
    model_destino_alta.load_model("models/model_destino_alta")

    predict_destino_alta = model_destino_alta.predict_proba([ sexo, edad, lugar_residencia_normal,  pfeiffer, asa,tipo_fractura_normal, \
        vitD, leucocitos ,glucosa,urea, creatinina, ckd ,colinesterasa ,albumina, movilidad_pre, predcit, lado_fractura_normal])
    predict_destino_alta = predict_destino_alta.round(2)

    predict_destino_alta_final = model_destino_alta.predict([ sexo, edad, lugar_residencia_normal,  pfeiffer, asa,tipo_fractura_normal, \
        vitD, leucocitos ,glucosa,urea, creatinina, ckd ,colinesterasa ,albumina, movilidad_pre, predcit, lado_fractura_normal])

    simu_destino_alta = model_destino_alta.predict_proba([ sexo, edad, lugar_residencia_normal,  pfeiffer, asa,tipo_fractura_normal, \
        vitD, leucocitos ,glucosa,urea, creatinina, ckd ,colinesterasa ,albumina, movilidad_pre, resultado_demora, lado_fractura_normal,
        predcit])
    simu_destino_alta = simu_destino_alta.round(2)

    simu_destino_alta_final = model_destino_alta.predict([ sexo, edad, lugar_residencia_normal,  pfeiffer, asa,tipo_fractura_normal, \
        vitD, leucocitos ,glucosa,urea, creatinina, ckd ,colinesterasa ,albumina, movilidad_pre, resultado_demora, lado_fractura_normal,
        predcit])

    destino = ['Domicilio', 'Fallecido', 'Hospitalización Agudos', 'Residencia/Institucionalizado']

    predict_destino_alta = list(predict_destino_alta)
    simu_destino_alta = list(simu_destino_alta)

    difference = np.array(simu_destino_alta)- np.array(predict_destino_alta)
    d = {'Destino': ['Domicilio', 'Fallecido', 'Hospitalización Agudos', 'Residencia/Institucionalizado'],
        'Porcentaje predicción': predict_destino_alta,
        'Porcentaje simulación': simu_destino_alta,
        'Diferencias': difference}
        #'Porcentaje simulación': lista_simu_destino}

    df = pd.DataFrame(data=d)

    st.subheader('Probabilidad de destino al alta')
    #st.write('###### Probabilidad de destino al alta')
    df_tabla = df.copy()
    df_tabla['Porcentaje predicción'] = df_tabla['Porcentaje predicción'].transform(lambda x: '{:,.2%}'.format(x))
    df_tabla['Porcentaje simulación'] = df_tabla['Porcentaje simulación'].transform(lambda x: '{:,.2%}'.format(x))
    df_tabla['Diferencias'] = df_tabla['Diferencias'].transform(lambda x: '{:,.2%}'.format(x))

    df_tabla

    import plotly.express as px
    fig_pie = px.pie(df, values='Porcentaje simulación', names='Destino', title="Probabilidad de destino simulación al alta", color = 'Destino',category_orders={ 
                    "Destino": [ 'Residencia/Institucionalizado','Domicilio',  'Hospitalización Agudos','Fallecido']})

    st.plotly_chart(fig_pie, use_container_width=True)


    # --------------------------------------- MOVILIDAD ALTA --------------------------------------
    # ---------------------------------------------------------------------------------------------
    
    model_movilidad_alta = CatBoostClassifier()

    model_movilidad_alta.load_model("models/model_movilidad")

    predict_movilidad_alta = model_movilidad_alta.predict_proba([sexo, edad, lugar_residencia_normal,  pfeiffer, asa,lado_fractura_normal, tipo_fractura_normal, \
        vitD, leucocitos ,glucosa,urea, creatinina, ckd ,colinesterasa ,albumina, movilidad_pre, predcit, simu_destino_alta_final[0]])
    predict_movilidad_alta = predict_movilidad_alta.round(2)

    simu_movilidad_alta = model_movilidad_alta.predict_proba([ sexo, edad, lugar_residencia_normal,  pfeiffer, asa,lado_fractura_normal, tipo_fractura_normal, \
        vitD, leucocitos ,glucosa,urea, creatinina, ckd ,colinesterasa ,albumina, movilidad_pre, resultado_demora, simu_destino_alta_final[0]])
    simu_movilidad_alta = simu_movilidad_alta.round(2)

    predict_movilidad_alta = list(predict_movilidad_alta)
    simu_movilidad_alta = list(simu_movilidad_alta)

    difference = np.array(simu_movilidad_alta)- np.array(predict_movilidad_alta)
    d = {'Movilidad': ['Completamente inmovil', 'Muy limitada','Ligeramente limitada', 'Sin limitaciones'],
    'Descripción': ['Completamente inmovil', 'Muy limitada','Ligeramente limitada', 'Sin limitaciones'],
        'Porcentaje predicción': predict_movilidad_alta,
        'Porcentaje simulación': simu_movilidad_alta,
        'Diferencias': difference}
        #'Porcentaje simulación': lista_simu_destino}

    df = pd.DataFrame(data=d)

    st.subheader('Probabilidad de movilidad al alta')
    #st.write('###### Probabilidad de movilidad al alta')

    df_tabla = df.copy()
    df_tabla['Porcentaje predicción'] = df_tabla['Porcentaje predicción'].transform(lambda x: '{:,.2%}'.format(x))
    df_tabla['Porcentaje simulación'] = df_tabla['Porcentaje simulación'].transform(lambda x: '{:,.2%}'.format(x))
    df_tabla['Diferencias'] = df_tabla['Diferencias'].transform(lambda x: '{:,.2%}'.format(x))

    df_tabla

    # custom function to change labels    
    def newLegend(fig, newNames):
        newLabels = []
        for item in newNames:
            for i, elem in enumerate(fig.data[0].labels):
                if elem == item:
                    #fig.data[0].labels[i] = newNames[item]
                    newLabels.append(newNames[item])
        fig.data[0].labels = np.array(newLabels)
        return(fig)
    import plotly.express as px
    fig_pie = px.pie(df, values='Porcentaje simulación', names='Movilidad', title="Probabilidad de Movilidad simulación al alta", color = 'Movilidad',category_orders={ 
                    "Movilidad": [ 'Ligeramente limitada', 'Sin limitaciones', 'Muy limitada', 'Completamente inmovil']})

    st.plotly_chart(fig_pie, use_container_width=True)


    # --------------------------VIVO A LOS 30 DIAS ------------------------
    # ---------------------------------------------------------------------

    model_vivo_30d = CatBoostClassifier()
    model_vivo_30d.load_model("models/model_vivo_30d")

    predict_vivo_alta = model_vivo_30d.predict_proba([sexo, edad, lugar_residencia_normal, pfeiffer, asa, lado_fractura_normal, tipo_fractura_normal, \
        vitD, leucocitos ,glucosa,urea, creatinina, ckd ,colinesterasa ,albumina,simu_destino_alta[1], movilidad_pre, predcit,postoperatorio ])
    predict_vivo_alta = predict_vivo_alta.round(2)
    #simu_destino_alta_final[0]

    simu_vivo_alta = model_vivo_30d.predict_proba([ sexo, edad, lugar_residencia_normal,  pfeiffer, asa,lado_fractura_normal, tipo_fractura_normal, \
        vitD, leucocitos ,glucosa,urea, creatinina, ckd ,colinesterasa ,albumina,simu_destino_alta[1], movilidad_pre, resultado_demora, resultado_post])
    simu_vivo_alta = simu_vivo_alta.round(2)
    #AQUI

    predict_vivo_alta = list(predict_vivo_alta)
    simu_vivo_alta = list(simu_vivo_alta)

    difference = np.array(simu_vivo_alta)- np.array(predict_vivo_alta)
    d = {'Situación': ['Fallece', 'Vivo a 30 días'],
        'Porcentaje predicción': predict_vivo_alta,
        'Porcentaje simulación': simu_vivo_alta,
        'Diferencias': difference}
        #'Porcentaje simulación': lista_simu_destino}

    df = pd.DataFrame(data=d)

    st.subheader('Probabilidad de Vivo a los 30 dias')
    #st.write('###### Probabilidad de vivo al alta')

    df_tabla = df.copy()
    df_tabla['Porcentaje predicción'] = df_tabla['Porcentaje predicción'].transform(lambda x: '{:,.2%}'.format(x))
    df_tabla['Porcentaje simulación'] = df_tabla['Porcentaje simulación'].transform(lambda x: '{:,.2%}'.format(x))
    df_tabla['Diferencias'] = df_tabla['Diferencias'].transform(lambda x: '{:,.2%}'.format(x))

    df_tabla

    # custom function to change labels    
    def newLegend(fig, newNames):
        newLabels = []
        for item in newNames:
            for i, elem in enumerate(fig.data[0].labels):
                if elem == item:
                    #fig.data[0].labels[i] = newNames[item]
                    newLabels.append(newNames[item])
        fig.data[0].labels = np.array(newLabels)
        return(fig)
    import plotly.express as px
    fig_pie = px.pie(df, values='Porcentaje simulación', names='Situación', title="Probabilidad de Vivo al alta simulación", color = 'Situación',category_orders={ 
                    "Situación": [ 'Fallece','Vivo a 30 días']},
                    color_discrete_sequence=['#ff2b2b', '#83c9ff'])
    
    st.plotly_chart(fig_pie, use_container_width=True)