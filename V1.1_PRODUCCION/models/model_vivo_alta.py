
#%%
import pandas as pd
import numpy as np

df = pd.read_csv('rnfc_prepro_model_v3.csv') 

#%%
df = df[['Sexo','Edad','Residencia_preFx','Pfeiffer_SPMSQ','ASA','Fx_lado','Fx_tipo',
'VitD_PreFx','Leucocitos','Glc','Urea',
'Creatinina','CKD-EPI','Colinesterasa','Albumina','Destino_Alta','Movilidad_preFx', 'Vivo_30d', 'Demora_Qx', 'ds_post_dias' ]]

#Renombrar columnas
df = df.rename(columns={
'Residencia_preFx':'Lugar de residencia', 
'Movilidad_preFx':'Movilidad PreFractura',
'Pfeiffer_SPMSQ': 'Cuestionario Pfeiffer',
'ASA' : 'Categoría ASA',
'Fx_lado':'Lado fractura',
'Fx_tipo':'Tipo de Fractura',
'VitD_PreFx': 'Vitamina D',
'Glc': 'Glucosa'
#'Mov_30d' : 'Movilidad postFractura'

})

#%%
df.head()
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
df['Vivo_30d'] = df['Vivo_30d'].apply(str)
df['Vivo_30d'] = df['Vivo_30d'].astype('category')
df['Vivo_30d'] = df['Vivo_30d'].replace('0.0','Fallece')
df['Vivo_30d'] = df['Vivo_30d'].replace('1.0','Vivo')
df['Vivo_30d'] = df['Vivo_30d'].replace('2.0','Vivo')#Eliminarlos 
df['Vivo_30d'] = df['Vivo_30d'].replace('11.0','Desconocido')#Eliminarlos 
df['Vivo_30d'] = df['Vivo_30d'].replace('nan','Fallece')#Eliminarlos 

df = df[df['Vivo_30d'] != 'Desconocido']

df.head()

#%%
df['ds_post_dias'] = df['ds_post_dias'].round(1)

df['Cuestionario Pfeiffer'] = df['Cuestionario Pfeiffer'].astype(int)

df['Categoría ASA'] = df['Categoría ASA'].astype(int)


df['Vitamina D'] = df['Vitamina D'].astype(int)

df['Glucosa'] = df['Glucosa'].astype(int)

df['Urea'] = df['Urea'].astype(int)

df['Colinesterasa'] = df['Colinesterasa'].astype(int)

df['Albumina'] = df['Albumina'].astype(int)

df['Movilidad PreFractura'] = df['Movilidad PreFractura'].astype(int)

df['CKD-EPI'] = df['CKD-EPI'].astype(str)

df['CKD-EPI'] = np.where(df['CKD-EPI'].str.contains(">90"), 91, df['CKD-EPI'])
df['CKD-EPI'] = pd.to_numeric(df['CKD-EPI'], errors='coerce')
df['CKD-EPI'] = df['CKD-EPI'].astype(int)

df['Destino_Alta'] = df['Destino_Alta'].replace(1.0,0.0)
df['Destino_Alta'] = df['Destino_Alta'].replace(2.0,0.0)
df['Destino_Alta'] = df['Destino_Alta'].replace(3.0,0.0 )
df['Destino_Alta'] = df['Destino_Alta'].replace(6.0,1.0)
df['Destino_Alta'] = df['Destino_Alta'].replace(11.0,0.0)#Eliminarlos 
df['Destino_Alta'] = df['Destino_Alta'].astype('float')

df['Movilidad PreFractura'] = np.where((df['Movilidad PreFractura'].isin([1, 2, 3])), 4,
                                       np.where((df['Movilidad PreFractura'].isin([4, 5, 6])), 3,
                                                np.where((df['Movilidad PreFractura'].isin([7, 8, 9])), 2,
                                                         np.where(df['Movilidad PreFractura'] == 10, 1, df['Movilidad PreFractura']))))
df['Movilidad PreFractura'] = df['Movilidad PreFractura'].astype('category')

"""
df['Movilidad postFractura'].fillna(-1, inplace=True)
df['Movilidad postFractura'] = df['Movilidad postFractura'].astype(int)
df['Movilidad postFractura'] = np.where((df['Movilidad postFractura'].isin([1, 2, 3])), 4,
                                       np.where((df['Movilidad postFractura'].isin([4, 5, 6])), 3,
                                                np.where((df['Movilidad postFractura'].isin([7, 8, 9])), 2,
                                                         np.where(df['Movilidad postFractura'] == 10, 1, df['Movilidad postFractura']))))
df['Movilidad postFractura'] = df['Movilidad postFractura'].astype('category')
"""
df.head()

df.dtypes

#%%%

train_data = df[['Sexo','Edad','Lugar de residencia','Cuestionario Pfeiffer','Categoría ASA','Lado fractura','Tipo de Fractura',
'Vitamina D','Leucocitos','Glucosa','Urea',
'Creatinina','CKD-EPI','Colinesterasa','Albumina', 'Movilidad PreFractura','Demora_Qx','ds_post_dias'
]].values.tolist()
train_data
#AQUI Destino_Alta
df_prueba = df[['Sexo','Edad','Lugar de residencia','Cuestionario Pfeiffer','Categoría ASA','Lado fractura','Tipo de Fractura',
'Vitamina D','Leucocitos','Glucosa','Urea',
'Creatinina','CKD-EPI','Colinesterasa','Albumina', 'Movilidad PreFractura','Demora_Qx','ds_post_dias']]
df['Destino_Alta'].unique()

#%%
eval_data = df[['Sexo','Edad','Lugar de residencia','Cuestionario Pfeiffer','Categoría ASA','Lado fractura','Tipo de Fractura',
'Vitamina D','Leucocitos','Glucosa','Urea',
'Creatinina','CKD-EPI','Colinesterasa','Albumina', 'Movilidad PreFractura','Demora_Qx','ds_post_dias'
]].values.tolist()
eval_data
#AQUI Destino_Alta

#%%

train_labels = df['Vivo_30d'][:].values.tolist()
train_labels
eval_labels = df['Vivo_30d'].values.tolist()


# %%

from catboost import CatBoostClassifier

# Initialize data

cat_features = [0, 2, 5, 6]

"""
cat_features = [df.columns.get_loc("Sexo"),                      
    df.columns.get_loc("Lugar de residencia"),
    df.columns.get_loc("Lado fractura"),
    df.columns.get_loc("Tipo de Fractura"),
    df.columns.get_loc("Vivo_30d"),
    df.columns.get_loc("Movilidad PreFractura"),
    df.columns.get_loc("Destino_Alta"),

    ]
    """
# Initialize CatBoostRegressor
"""
model = CatBoostClassifier(iterations=200,
                           learning_rate=0.3,
                           depth=5)
"""
model = CatBoostClassifier(iterations=200,
                           learning_rate=0.1,
                           max_depth=5,
                           loss_function='Logloss',
                           eval_metric='AUC',
                        )
                    
# Fit model
model.fit(train_data, train_labels,cat_features)
# Get predicted classes
preds = model.predict_proba(eval_data)
#preds_raw = model.predict(eval_data, prediction_type='RawFormulaVal')


# %%
set(train_labels)

# %%
preds

#%%
model.save_model("model_vivo_30d_5")

# %%
"""
model.predict(['Mujer',
 92,
 'Hospitalizado',
 7,
 4,
 'Izquierda',
 'Pertrocantérea',
 0,
 10.2,
 92,
 53,
 0.38,
 91,
 2751,
 25,
 0.13,
 1,
 2.4])"""
# %%
# %%