import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt
import numpy as np
#import plotly.express as px
import time
from pandas_profiling import ProfileReport
import pandas as pd
import pandas_profiling
import streamlit as st
from streamlit_pandas_profiling import st_profile_report
from sklearn import preprocessing

#import h2o
from catboost import CatBoostRegressor
import plotly.figure_factory as ff
import plotly.express as px

le = preprocessing.LabelEncoder()


st.title('Proyecto Fractura Cadera')
st.text('App para Predicción de Demora y Dias de estancia en Fractura de Cadera')

#-------------SIDEBAR-------------------------
st.sidebar.title("Variables de Triaje")
st.sidebar.subheader("Datos paciente")


sexo = st.sidebar.radio("Sexo", ["Hombre", "Mujer"])
edad = st.sidebar.slider("Edad",1, 140,75)
fecha_llegada = st.sidebar.date_input("Fecha de llegada")

le.fit(["Domicilio", "Residencia",'Hospitalizado'])
lugar_residencia = st.sidebar.selectbox("Lugar de residencia", ["Domicilio", "Residencia","Hospitalizado"]) 
lugar_residencia = le.transform([lugar_residencia])[0] + 1


st.sidebar.subheader("Geriatría")
movilidad_pre = st.sidebar.slider("Movilidad Pre-Fractura",1, 10)
asa = st.sidebar.slider("Categoría ASA",1, 4)
riesgo_caida = st.sidebar.slider("Riesgo caida",1, 10)

barthel = st.sidebar.slider("Barthel",0, 100)
braden = st.sidebar.slider("Braden",8, 23)
anticoagulantes = st.sidebar.checkbox("Anticoagulantes")


st.sidebar.subheader("Salud mental")
pfeiffer = st.sidebar.slider("Cuestionario Pfeiffer",1, 10)
deterioro_cognitivo = st.sidebar.checkbox("Deterioro cognitivo")
deterioro_cognitivo = int(deterioro_cognitivo)
alzheimer = st.sidebar.checkbox("Alzheimer")
alzheimer = int(alzheimer)


st.sidebar.subheader("Datos médicos")
leucocitos = st.sidebar.slider("Leucocitos",1.0, 30.0)
glucosa = st.sidebar.slider("Glucosa",70, 300)
urea = st.sidebar.slider("Urea",20, 180)
creatinina = st.sidebar.slider("Creatinina",0.2, 3.0)
ckd = st.sidebar.slider("CKD: Para >90 introducir 91",10, 91)
colinesterasa = st.sidebar.slider("Colinesterasa",2000, 10000)
albumina = st.sidebar.slider("Albúmina",20, 50)
sentarse = st.sidebar.checkbox("Se sienta al día siguiente")
sentarse_transformed = int(sentarse)
ulceras_presion = st.sidebar.checkbox("Úlceras por presión")
ulceras_presion_transformed = int(ulceras_presion)
diabetes = st.sidebar.checkbox("Diabetes")
diabetes = int(diabetes)

hta = st.sidebar.checkbox("HTA")
hta = int(hta)

anemia = st.sidebar.checkbox("Anemia")
anemia = int(anemia)

disfagia = st.sidebar.checkbox("Disfagia")
disfagia = int(disfagia)

epoc = st.sidebar.checkbox("EPOC")
epoc = int(epoc)

ins_cardiaca = st.sidebar.checkbox("Insuficiencia cardiaca")
ins_cardiaca = int(ins_cardiaca)

ins_renal = st.sidebar.checkbox("Insuficiencia renal")
ins_renal = int(ins_renal)

ins_respiratoria = st.sidebar.checkbox("Insuficiencia respiratoria")
ins_respiratoria = int(ins_respiratoria)

infeccion_respiratoria = st.sidebar.checkbox("Infección respiratoria")
infeccion_respiratoria = int(infeccion_respiratoria)

itu = st.sidebar.checkbox("ITU")
itu = int(itu)

parkinson = st.sidebar.checkbox("Parkinson")
parkinson = int(parkinson)

tce = st.sidebar.checkbox("TCE")
tce = int(tce)


st.sidebar.subheader("Datos Fractura")
tipo_fractura = st.sidebar.selectbox("Tipo de Fractura", ["Intracapsular no desplazada","Intracapuslar desplazada","Pertrocantérea","Subtrocantérea","Otra"], index=4)
tipos_fractura = [ "Intracapsular no desplazada","Intracapuslar desplazada","Pertrocantérea","Subtrocantérea","Otra"]
tipo_fractura = tipos_fractura.index(tipo_fractura) + 1

lado_fractura = st.sidebar.radio("Lado fractura", ["Izquierda", "Derecha"])
if lado_fractura == "Izquierda":
    lado_fractura = 0
else:
    lado_fractura = 1

#bt_prec = st.sidebar.button("Hacer predicción")

# MODELO

#h2o.init()

#condition





#if st.sidebar.button('Hacer predicción'):
st.header('Días en el hospital')
#DEMORA
model_demora = CatBoostRegressor()
model_demora.load_model("model_ds_intervencion_dias")

d = {'Sexo': [sexo], 'Edad': [edad], 'Lugar de residencia':[lugar_residencia], 'Movilidad PreFractura':[movilidad_pre],
'Riesgo caida': [riesgo_caida], 'Barthel':[barthel],'Braden':[braden], 'Deterioro cognitivo':[deterioro_cognitivo],'Alzheimer':[alzheimer],
'Diabetes':[diabetes],'HTA':[hta],'Anemia':[anemia],'Disfagia':[disfagia], 'EPOC':[epoc],'Insuficiencia respiratoria':[ins_respiratoria],
'Insuficiencia cardiaca':[ins_cardiaca],'Insuficiencia renal':[ins_renal], 'Infección respiratoria':[infeccion_respiratoria]
,'ITU':[itu],'Parkinson':[parkinson],'TCE':[tce]
,'Tipo de Fractura':[tipo_fractura],'Lado fractura':[lado_fractura]
 }
df = pd.DataFrame(data=d)
df_list = df.values.tolist()
input_data = np.column_stack((sexo, edad, lugar_residencia, movilidad_pre,riesgo_caida, barthel, braden,deterioro_cognitivo,
alzheimer,diabetes,hta,anemia,disfagia,epoc,ins_respiratoria,ins_cardiaca,ins_renal,infeccion_respiratoria,
itu,parkinson,tce
,tipo_fractura,lado_fractura 
))

predcit = model_demora.predict(input_data)
predcit = predcit.round(1)


resultado_demora = st.slider("Demora hasta operar", min_value=0.0, max_value=7.0, value=float(predcit[0]), step=None, format=None)




# Estancia dias
model_demora = CatBoostRegressor()
model_demora.load_model("model_ds_estancia_dias")

d = {'Sexo': [sexo], 'Edad': [edad], 'Lugar de residencia':[lugar_residencia], 'Movilidad PreFractura':[movilidad_pre],
'Riesgo caida': [riesgo_caida], 'Barthel':[barthel],'Braden':[braden], 'Deterioro cognitivo':[deterioro_cognitivo],'Alzheimer':[alzheimer],
'Diabetes':[diabetes],'HTA':[hta],'Anemia':[anemia],'Disfagia':[disfagia], 'EPOC':[epoc],'Insuficiencia respiratoria':[ins_respiratoria],
'Insuficiencia cardiaca':[ins_cardiaca],'Insuficiencia renal':[ins_renal], 'Infección respiratoria':[infeccion_respiratoria]
,'ITU':[itu],'Parkinson':[parkinson],'TCE':[tce]
,'Tipo de Fractura':[tipo_fractura],'Lado fractura':[lado_fractura]
 }
df = pd.DataFrame(data=d)
df_list = df.values.tolist()
input_data = np.column_stack((sexo, edad, lugar_residencia, movilidad_pre,riesgo_caida, barthel, braden,deterioro_cognitivo,
alzheimer,diabetes,hta,anemia,disfagia,epoc,ins_respiratoria,ins_cardiaca,ins_renal,infeccion_respiratoria,
itu,parkinson,tce
,tipo_fractura,lado_fractura 
))

predcit = model_demora.predict(input_data)
predcit = predcit.round(1)



resultado_estancia = st.slider("Estancia total días", min_value=float(predcit[0]), max_value=7.0, value=float(predcit[0]+ resultado_demora), step=None, format=None)



precio_dia = 550
coste_demora = 550 * resultado_demora
coste_estancia = 550 * (resultado_estancia - resultado_demora)
coste_intervencion = 3000

d = {'Coste': ["Coste demora", "Coste intervención","Coste postoperatorio"], 'Euros': [coste_demora ,coste_intervencion, coste_estancia]}


df = pd.DataFrame(data=d)



fig = px.bar(df, y="Coste", x="Euros", color="Coste", orientation='h')

# Plot!
st.plotly_chart(fig, use_container_width=True)



coste_demora_ahorro = 550 * predcit[0]
coste_estancia_ahorro = 550 * (resultado_estancia - predcit[0])


st.write('Coste total predicho', coste_demora + coste_estancia + coste_intervencion, "€")
st.write('Ahorro', coste_demora_ahorro + coste_estancia_ahorro + coste_intervencion, "€")
"""

"""
#------------RESULTADOS-----------------------
#Indicadores calidad de vida
# st.header("Indicadores calidad de vida al alta")

# chart_data = pd.DataFrame(
#     np.random.randn(20, 1))
# st.bar_chart(chart_data)

#st.header("Tiempo de estancia previsto")
#st.subheader("7 días")
#my_bar = st.progress(0)
#my_bar.progress(50)

# st.header("Valoración estimada de visita a un mes")
# chart_data2 = pd.DataFrame(
#     np.random.randn(20, 1))
# st.bar_chart(chart_data2)

#st.header("Datos Identificativos")
#df = pd.read_csv('datos_csv/Datos_Identificativos_y_Administrativos-_Altas_desde_01072014_a_10072019_mayores_65_y_maestros___Altas.csv')
#pr = df.profile_report()
#st_profile_report(pr)

#diagnostico = st.sidebar.multiselect("Diagnóstico",
#    ["ACV Isquémico", "Broncoaspiración", "Calcifilaxis","Carcinoma","Sindrome confusional","Celulitis MMII", "Complicación fractura cadera"," Contusión cadera",
#     "Coxalgia cadera","Coxalgia derecha", "Coxartrosis derecha","Cudaro confusional","Rambdomiolisis","Demencia", "Negativa a la ingesta", "Sobredosificación Sintrom",
#     "Deterioro cognitivo", "Diarrea", "Dolor en cadera", "EPOC Reguadizado", "Exudado inguinal a través de fístula cutanea","Fractura cadera derecha", "Fractura cadera Izquierda",
#     "Fractura cadera intervenida", "Carcinoma","Gonalgia derecha", "Úlceras"])#Añadir los más relevantes

# st.sidebar.subheader("Medidas")
# imc = st.sidebar.slider("índice de Masa Corporal", 15, 35) #No está directamente, pero se puede obtener con el peso y la altura
# temperatura = st.sidebar.slider("Temperatura", 34.0, 42.0)
# ten_maxima = st.sidebar.number_input("Tensión máxima", 60, 240 )
# ten_minima = st.sidebar.number_input("Tensión mínima", 30, 110 )

# bt_prec = st.sidebar.button("Hacer predicción")
#---------------------------------------------

#------------RESULTADOS-----------------------
#Indicadores calidad de vida
# st.header("Indicadores calidad de vida al alta")

# chart_data = pd.DataFrame(
#     np.random.randn(20, 1))
# st.bar_chart(chart_data)

# st.header("Tiempo de estancia previsto")
# st.subheader("7 días")
# my_bar = st.progress(0)
# my_bar.progress(50)

# st.header("Valoración estimada de visita a un mes")
# chart_data2 = pd.DataFrame(
#     np.random.randn(20, 1))
# st.bar_chart(chart_data2)

#st.header("Datos Identificativos")
#df = pd.read_csv('datos_csv/Datos_Identificativos_y_Administrativos-_Altas_desde_01072014_a_10072019_mayores_65_y_maestros___Altas.csv')
#pr = df.profile_report()
#st_profile_report(pr)

#----------------------------------------------------------------------------------

#-------------------------------------DUDAS---------------------------------------
#Sería lo vismo visualmente en triaje que en VGI, pero serian simulador y predictor respectivamente
#Número de registro del episodio relacionado con la prestación
#Código de la prestación
#Indicador de tipo de cirugía (quirúrgicas). Valores posibles: A-mayor, E-menor (Pocos datos)
#Hay muchos datos que están codificados, como podemos saber que significan realmente.
#Si hay información de los médicos(Prestación, Interconsultas)
#Info de motivo de consulta: Está en texto libre en Interconsultas(omoticon)

#-------------------------------------ELENA---------------------------------------
#-¿Qué información tenemos exactamente del paciente? Podriamos tener una imagen de la "servilleta"?
#-¿Qué lugares de residencia podemos encontrar?¿Y donde están? ("Domicilio", "Residencia", "Hospitalizacion aguda, Desconocido")
#-¿Qué diagnósticos podemos encontrar? (En los .csv aparecen bastantes, son todos esos, se podrían resumir, faltan, etc)
#-Normalización de los tipos de diagnósticos
#-¿Qué tipo de fracturas encontramos? ("Intracapsular no desplazada","Intracapuslar desplazada","Subtrocantérea", "Pertrocantérea", "Otra")
#-¿El IMS, temperatura, tensiones,... puden ser relevantes?
#¿Tenemos datos de la Movilidad pre-fractura?
#¿Tenemos datos de la calidad de vida como Cuestionario Pfeiffer?
#-Estado de entrada y al alta. Tienen numeros que no sabemos que significan. (gmotalta, gsitalta)
#-El lado izq y derecho en la fractura influyen?
#(odiagalt	odiaging	odiagini) necesitamos normalizarlos o tenerlos resumidos en los más importantes
#(ireingre) Reingreso: es relevante
#iotrocen() Intervenido en otro centro: Es relavante
#(gsitalta) Código de situación al alta. Necesitamos saber que significa cada número
#(gmotalta) Motivo de alta. Necesitamos saber que significa cada número
#(itraslad) Corresponde a un traslado. Es relevante?
#(gdiagalt) Diagnostico codificado. No siempre coinciden para diagnostivos en texto iguales




#----------------------------------------------------------------------------------

#----------------------------------------------------------------------------------
#---------------------------------OBJETIVOS-----------------------------
#Ver de forma visual lo del cp
#Con las fechas predecir cuando se le operará, cuando se le dará el alta

#-----------------------------DATOS--------------------------------

#Analisis exploratiorio variables



#SE PODRIA AÑADIR:

#DIAGNOSTICO
##gcodidia	diagnóstico de diagnóstico médico - 
## gtipdiag tipo de diagnóstico	
##Prioridad(0-10) -ipriorid

#DATOS IDENTIFICATIVOS
## odiaging Diagnóstico al ingreso sin codificar ******
## odiagini Texto del diagnóstico sin codificar inicial al ingreso  
###     puede servir para ver los mas comunes
## finterve	paciente intervenido quirúrgicamente  
#       podemos sacar el tiempo hasta la operación
## gdiagalt Diagnóstico principal codificado según CIE al alta
## odiagalt	Descripción del diagnóstico principal al alta sin codificar

#hc = st.sidebar.text_input("Historia clínica")
#prioridad = st.sidebar.slider("Prioridad", 0, 10) #No hay casi datos
#enfermedades = st.sidebar.multiselect("Enfermedades", ["Artrosis","Acuñamiento D12","Fractura columna lumbar",
#    "Lumbalgia", "I.Cardiaca","DLA","RAO","Estreñimiento","Ecogafo de Barret","Gastritis","H. Hiato"]) #¿Cuales son las más relevantes?
#reingreso = st.sidebar.radio("¿Reingreso?", ["Si", "No"])
#cirugia = st.sidebar.radio("Cirugia", ["Antes de 48h", "Despues d 48h", "Sin cirugia"])
#oxigeno = st.sidebar.slider("Saturación de oxigeno", 0, 100) #No hay casi datos
#frecuencia = st.sidebar.slider("Frecuencia cardiaca", 50, 150) #No hay casi datos
#----------------------------------------------------------------------


#-------------------------COMPONENTES---------------------------------
#Checkbox
#selected = st.sidebar.checkbox("I agree")
#Selectbox
#choice = st.sidebar.selectbox("Elige", ["aa","bb"])
#Multiselect
#choice = st.sidebar.multiselect("Elige varias",["aaa","bb","cc"])
#---------------------------------------------------------------------

#-------------------------REUNIÓN------------------------------------
#Lugar de residencia pre-fractura(Domicilio, residencia, Hospitalizacion aguda)
#Movilidad pre-fractura
#Cuestionario Pfeiffer
#Clase social y estudios(Obtener estos datos a través de otros)/Preguntar si existe
#Usar el código postal para obtener clase social
    # https://www.agenciatributaria.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfmunicipios/2019/jrubikf74b3dca9af01b51cabd6d5603e0e16daecd1a97c.html
#---------------------------------------------------------------------




# %%
