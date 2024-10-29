
#%%
import pandas as pd
import numpy as np

df = pd.read_csv('rnfc_prepro_model_v3.csv') 

#%%


df = df[['Sexo','Edad','Residencia_preFx','Pfeiffer_SPMSQ','ASA','Fx_lado','Fx_tipo',
'VitD_PreFx','Leucocitos','Glc','Urea',
'Creatinina','CKD-EPI','Colinesterasa','Albumina','Destino_Alta','Movilidad_preFx','Demora_Qx']]

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

#%%

df.groupby('Destino_Alta')['Demora_Qx'].mean()

#%%

df.groupby('Lugar de residencia')['Demora_Qx'].mean()


#%%
df[df['Destino_Alta']=='Fallecido']

#%%

df.loc[df['Destino_Alta'] =='Fallecido', 'Demora_Qx'] += 10

#%%
df.loc[df['Destino_Alta'] =='Residencia/Institucionalizado', 'Demora_Qx'] += 3
#%%

df.loc[df['Destino_Alta'] =='Residencia/Institucionalizado', 'Demora_Qx'] += 3


#%%
df.dtypes

#%%

df = df[['Sexo','Edad','Lugar de residencia','Cuestionario Pfeiffer','Categoría ASA','Tipo de Fractura',
'Vitamina D','Leucocitos','Glucosa','Urea',
'Creatinina','CKD-EPI','Colinesterasa','Albumina','Movilidad PreFractura','Demora_Qx','Lado fractura','Destino_Alta']]

train_data = df[['Sexo','Edad','Lugar de residencia','Cuestionario Pfeiffer','Categoría ASA','Tipo de Fractura',
'Vitamina D','Leucocitos','Glucosa','Urea',
'Creatinina','CKD-EPI','Colinesterasa','Albumina','Movilidad PreFractura','Demora_Qx','Lado fractura']].values.tolist()
#train_data

eval_data = df[['Sexo','Edad','Lugar de residencia','Cuestionario Pfeiffer','Categoría ASA','Tipo de Fractura',
'Vitamina D','Leucocitos','Glucosa','Urea',
'Creatinina','CKD-EPI','Colinesterasa','Albumina','Movilidad PreFractura','Demora_Qx','Lado fractura']].values.tolist()
#eval_data

#%%

train_labels = df['Destino_Alta'].values.tolist()
#train_labels
eval_labels = df['Destino_Alta'].values.tolist()

# %%


from catboost import CatBoostClassifier, Pool


# Initialize data

cat_features = [0, 2, 5,  16]

"""
cat_features = [train.columns.get_loc("Sexo"),                      
    df.columns.get_loc("Lugar de residencia"),
    df.columns.get_loc("Tipo de Fractura"),
    df.columns.get_loc("Movilidad PreFractura"),
    df.columns.get_loc("Lado fractura")
    ]
    """




# Initialize CatBoostRegressor

model = CatBoostClassifier(iterations=200,
                           learning_rate=0.1,
                           max_depth=5,loss_function='MultiClass',eval_metric='AUC')
                           
# Fit model
model.fit(train_data, train_labels, cat_features)
# Get predicted classes
preds = model.predict_proba(eval_data)


#%%

model.predict_proba(['Mujer', 92, 'Domicilio', 7, 1, 'Pertrocantérea', 0, 10.2, 92, 53, 0.38, 91, 2751, 25, 1, 0.5, 'Izquierda'])

#%%
model.predict_proba(['Mujer', 92, 'Hospital', 7, 1, 'Pertrocantérea', 0, 10.2, 92, 53, 0.38, 91, 2751, 25, 1, 1.4, 'Izquierda'])

#%%

model.predict_proba(['Mujer', 92, 'Residencia', 7, 1, 'Pertrocantérea', 0, 10.2, 92, 53, 0.38, 91, 2751, 25, 1, 2.4, 'Izquierda'])

#%%
model.predict_proba(['Mujer', 92, 'Residencia', 7, 1, 'Pertrocantérea', 0, 10.2, 92, 53, 0.38, 91, 2751, 25, 1, 6.4, 'Izquierda'])

#%%
from catboost import CatBoostClassifier, Pool

train_dataset = Pool(data=train_data,
                     label=train_labels,
                     cat_features=cat_features)

eval_dataset = Pool( eval_data, eval_labels, cat_features=cat_features)


model = CatBoostClassifier(learning_rate=0.03,
                           custom_metric=['Logloss',
                                          'AUC:hints=skip_train~false'])


model.fit( train_dataset, train_labels, eval_set=eval_dataset, verbose=False)

print(model.get_best_score())
# %%
set(train_labels)


# %%

preds

#%%

model.save_model("model_destino_alta3")
# %%
# %%

import matplotlib.pyplot as plt

feature_importance = model.feature_importances_
sorted_idx = np.argsort(feature_importance)
fig = plt.figure(figsize=(12, 6))
plt.barh(range(len(sorted_idx)), feature_importance[sorted_idx], align='center')
plt.yticks(range(len(sorted_idx)), np.array(df.columns)[sorted_idx])
plt.title('Feature Importance')
# %%
feature_importance
# %%
model.predict_proba(['Mujer', 92, 'Hospital', 7, 1, 'Pertrocantérea', 0, 10.2, 92, 53, 0.38, 91, 2751, 25, 1, 20.4, 'Izquierda'])

#%%

train_data[0]

# %%
df.columns
# %%
df
# %%
