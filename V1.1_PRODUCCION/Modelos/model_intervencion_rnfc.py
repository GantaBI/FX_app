
#%%
import pandas as pd
import numpy as np

df = pd.read_csv(r'C:\Users\Rodrigo\Desktop\cadera\rnfc_prepro_model_v3.csv', encoding = 'utf-8') 

#%%
df.head()

df.columns


#%%

df = df.dropna(subset=['Dias_Estancia'])

#%%

df = df[['Sexo', 'Edad', 'Residencia_preFx', 'Movilidad_preFx', 'Pfeiffer_SPMSQ',
       'ASA', 'Fx_lado', 'Fx_tipo',  'Demora_Qx',
       'Destino_Alta', 'Dias_Estancia', 'Sedest_postQx',
        'UPP.intrahosp', 
       'Leucocitos', 'Glc', 'Urea', 'Creatinina', 'CKD-EPI', 'Colinesterasa',
       'Albumina', 'Vitamina_D',
       'ds_dia_semana_llegada_Urg']]


#%%


#Renombrar columnas
df = df.rename(columns={
'Residencia_preFx':'Lugar de residencia', 
'Movilidad_preFx':'Movilidad PreFractura',
'Pfeiffer_SPMSQ': 'Cuestionario Pfeiffer',
'ASA' : 'Categoría ASA',
'Fx_lado':'Lado fractura',
'Fx_tipo':'Tipo de Fractura',
'Vitamina_D': 'Vitamina D',
'Glc': 'Glucosa'
#'Mov_30d' : 'Movilidad postFractura'

})


#%%
df['Sexo'] = df['Sexo'].apply(str)
df['Sexo'] = df['Sexo'].replace('F','Mujer')
df['Sexo'] = df['Sexo'].replace('H','Hombre')
df['Sexo'] = df['Sexo'].astype('category')



df['Lado fractura'] = df['Lado fractura'].apply(str)
df['Lado fractura'] = df['Lado fractura'].astype('category')
df['Lado fractura'] = df['Lado fractura'].replace('1.0','Izquierda')
df['Lado fractura'] = df['Lado fractura'].replace('2.0','Derecha')

df['Lugar de residencia'] = df['Lugar de residencia'].apply(str)
df['Lugar de residencia'] = df['Lugar de residencia'].astype('category')
df['Lugar de residencia'] = df['Lugar de residencia'].replace('0.0','Domicilio')
df['Lugar de residencia'] = df['Lugar de residencia'].replace('1.0','Residencia')
df['Lugar de residencia'] = df['Lugar de residencia'].replace('2.0','Hospitalizado')

df['Tipo de Fractura'] = df['Tipo de Fractura'].apply(str)
df['Tipo de Fractura'] = df['Tipo de Fractura'].astype('category')
df['Tipo de Fractura'] = df['Tipo de Fractura'].replace('1.0','Intracapsular no desplazada')
df['Tipo de Fractura'] = df['Tipo de Fractura'].replace('2.0','Intracapsular desplazada')
df['Tipo de Fractura'] = df['Tipo de Fractura'].replace('3.0','Pertrocantérea')
df['Tipo de Fractura'] = df['Tipo de Fractura'].replace('4.0','Subtrocantérea')
df['Tipo de Fractura'] = df['Tipo de Fractura'].replace('5.0','Otra')

####
df['Destino_Alta'] = df['Destino_Alta'].apply(str)
df['Destino_Alta'] = df['Destino_Alta'].astype('category')
df['Destino_Alta'] = df['Destino_Alta'].replace('1.0','Domicilio')
df['Destino_Alta'] = df['Destino_Alta'].replace('2.0','Residencia/Institucionalizado')
df['Destino_Alta'] = df['Destino_Alta'].replace('3.0','Hospitalización Agudos')
df['Destino_Alta'] = df['Destino_Alta'].replace('6.0','Fallecido')
df['Destino_Alta'] = df['Destino_Alta'].replace('11.0','Desconocido')#Eliminarlos 
df = df[df['Destino_Alta'] != 'Desconocido']


df.head()



#%%

df['Cuestionario Pfeiffer'] = df['Cuestionario Pfeiffer'].astype(int)

df['Categoría ASA'] = df['Categoría ASA'].astype(int)


#df['Vitamina D'] = df['Vitamina D'].astype(int)

df['Glucosa'] = df['Glucosa'].astype(int)

df['Urea'] = df['Urea'].astype(int)

df['Colinesterasa'] = df['Colinesterasa'].astype(int)

df['Albumina'] = df['Albumina'].astype(int)



df['Movilidad PreFractura'] = df['Movilidad PreFractura'].astype(int)

df['CKD-EPI'] = df['CKD-EPI'].astype(str)

df['CKD-EPI'] = np.where(df['CKD-EPI'].str.contains(">90"), 91, df['CKD-EPI'])
df['CKD-EPI'] = pd.to_numeric(df['CKD-EPI'], errors='coerce')
df['CKD-EPI'] = df['CKD-EPI'].astype(int)



df['Movilidad PreFractura'] = np.where((df['Movilidad PreFractura'].isin([1, 2, 3])), 4,
                                       np.where((df['Movilidad PreFractura'].isin([4, 5, 6])), 3,
                                                np.where((df['Movilidad PreFractura'].isin([7, 8, 9])), 2,
                                                         np.where(df['Movilidad PreFractura'] == 10, 1, df['Movilidad PreFractura']))))
df['Movilidad PreFractura'] = df['Movilidad PreFractura'].astype('category')


#%%

df.dtypes

#%%
df['Sedest_postQx'] = df['Sedest_postQx'].astype(str)
#df['Sit_Vital'] = df['Sit_Vital'].astype(str)
df['UPP.intrahosp'] = df['UPP.intrahosp'].astype(str)
#df['Fx_patol'] = df['Fx_patol'].astype(str)


#%%%

train_data = df[['Sexo', 'Edad', 'Lugar de residencia', 'Movilidad PreFractura',
       'Cuestionario Pfeiffer', 'Categoría ASA', 'Lado fractura',
       'Tipo de Fractura',   
       'Demora_Qx',  'Sedest_postQx', 'UPP.intrahosp', 'Leucocitos', 'Glucosa',
       'Urea', 'Creatinina', 'CKD-EPI', 'Colinesterasa', 'Albumina',
       'Vitamina D',  'ds_dia_semana_llegada_Urg']].values.tolist()

eval_data = df[['Sexo', 'Edad', 'Lugar de residencia', 'Movilidad PreFractura',
       'Cuestionario Pfeiffer', 'Categoría ASA', 'Lado fractura',
       'Tipo de Fractura', 
       'Demora_Qx', 'Sedest_postQx', 'UPP.intrahosp', 'Leucocitos', 'Glucosa',
       'Urea', 'Creatinina', 'CKD-EPI', 'Colinesterasa', 'Albumina',
       'Vitamina D',  'ds_dia_semana_llegada_Urg']].values.tolist()


train_labels = df['Dias_Estancia'][:].values.tolist()


#%%

from catboost import CatBoostRegressor
# Initialize data

cat_features = [ 0, 2, 3, 6, 7, 9, 10, 19]




# Initialize CatBoostRegressor
model = CatBoostRegressor(iterations=300, 
                           learning_rate=0.03,
                           depth=5, custom_metric = 'MAPE', loss_function='RMSE', l2_leaf_reg=0.8, early_stopping_rounds=10)
# Fit model
model.fit(train_data, train_labels, cat_features)
# Get predictions
preds = model.predict(eval_data)

# %%
train_data[4]


# %%
model.predict(['Mujer', 89, 'Residencia', 3, 5, 3, 'Izquierda', 'Pertrocantérea', 4.9, '1.0', '0.0',
 11.1, 107, 125, 1.29, 37, 7103, 34, 9.9, 'Lunes'])
# %%
model.predict(['Mujer', 89, 'Residencia', 3, 5, 3, 'Izquierda', 'Pertrocantérea', 4.9, '1.0', '0.0',
 11.1, 107, 125, 1.29, 37, 7103, 34, 9.9, 'Miércoles'])

# %%
model.predict(['Mujer', 89, 'Residencia', 3, 5, 3, 'Izquierda', 'Pertrocantérea', 4.9, '1.0', '0.0',
 11.1, 107, 125, 1.29, 37, 7103, 34, 9.9, 'Jueves'])

# %%
model.predict(['Mujer', 89, 'Residencia', 3, 5, 3, 'Izquierda', 'Pertrocantérea', 4.9, '1.0', '0.0',
 11.1, 107, 125, 1.29, 37, 7103, 34, 9.9, 'Viernes'])
# %%
model.predict(['Mujer', 89, 'Residencia', 3, 5, 3, 'Izquierda', 'Pertrocantérea', 4.9, '1.0', '0.0',
 11.1, 107, 125, 1.29, 37, 7103, 34, 9.9, 'Domingo'])
# %%
#%%

model.save_model("model_ds_estancia_dias_rnfc_4")
# %%
