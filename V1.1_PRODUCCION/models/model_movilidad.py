
#%%
import pandas as pd
import numpy as np

df = pd.read_csv(r'C:\Users\Rodrigo\Desktop\cadera\rnfc_prepro_model_v3.csv', encoding = 'utf-8') 

#%%


df = df[['Sexo','Edad','Residencia_preFx','Pfeiffer_SPMSQ','ASA','Fx_lado','Fx_tipo',
'VitD_PreFx','Leucocitos','Glc','Urea',
'Creatinina','CKD-EPI','Colinesterasa','Albumina','Destino_Alta','Movilidad_preFx', 'Mov_30d', 'Demora_Qx' ]]

#Renombrar columnas
df = df.rename(columns={
'Residencia_preFx':'Lugar de residencia', 
'Movilidad_preFx':'Movilidad PreFractura',
'Pfeiffer_SPMSQ': 'Cuestionario Pfeiffer',
'ASA' : 'Categoría ASA',
'Fx_lado':'Lado fractura',
'Fx_tipo':'Tipo de Fractura',
'VitD_PreFx': 'Vitamina D',
'Glc': 'Glucosa',
'Mov_30d' : 'Movilidad postFractura',

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



df['Movilidad PreFractura'] = np.where((df['Movilidad PreFractura'].isin([1])), 4,
                                       np.where((df['Movilidad PreFractura'].isin([2, 3, 4])), 3,
                                                np.where((df['Movilidad PreFractura'].isin([5, 6, 7, 8, 9])), 2,
                                                         np.where(df['Movilidad PreFractura'] == 10, 1, df['Movilidad PreFractura']))))
df['Movilidad PreFractura'] = df['Movilidad PreFractura'].astype('category')


df['Movilidad postFractura'].fillna(-1, inplace=True)
df['Movilidad postFractura'] = df['Movilidad postFractura'].astype(int)
df['Movilidad postFractura'] = np.where((df['Movilidad postFractura'].isin([1, 2, 3])), 4,
                                       np.where((df['Movilidad postFractura'].isin([4, 5, 6])), 3,
                                                np.where((df['Movilidad postFractura'].isin([7, 8, 9])), 2,
                                                         np.where(df['Movilidad postFractura'] == 10, 1, df['Movilidad postFractura']))))
df['Movilidad postFractura'] = df['Movilidad postFractura'].astype('category')
df = df[df['Movilidad postFractura'] != -1]



df.head()

df.dtypes



#%%%

train_data = df[['Sexo','Edad','Lugar de residencia','Cuestionario Pfeiffer','Categoría ASA','Lado fractura','Tipo de Fractura',
'Vitamina D','Leucocitos','Glucosa','Urea',
'Creatinina','CKD-EPI','Colinesterasa','Albumina','Movilidad PreFractura', 'Demora_Qx'
]].values.tolist()

eval_data = df[['Sexo','Edad','Lugar de residencia','Cuestionario Pfeiffer','Categoría ASA','Lado fractura','Tipo de Fractura',
'Vitamina D','Leucocitos','Glucosa','Urea',
'Creatinina','CKD-EPI','Colinesterasa','Albumina','Movilidad PreFractura', 'Demora_Qx'
]].values.tolist()

train_labels = df['Movilidad postFractura'][:].values.tolist()



# %%


from catboost import CatBoostClassifier


# Initialize data

cat_features = [0, 2, 5, 6, 15]

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
                           learning_rate=0.3,
                           depth=5)
                           
# Fit model
model.fit(train_data, train_labels, cat_features)
# Get predicted classes
preds = model.predict_proba(eval_data)

# %%
set(train_labels)


# %%

preds

#%%

#model.save_model("model_movilidad")
# %%
# %%
import matplotlib.pyplot as plt

feature_importance = model.feature_importances_
sorted_idx = np.argsort(feature_importance)
fig = plt.figure(figsize=(12, 6))
plt.barh(range(len(sorted_idx)), feature_importance[sorted_idx], align='center')
plt.yticks(range(len(sorted_idx)), np.array(['Sexo','Edad','Lugar de residencia','Cuestionario Pfeiffer','Categoría ASA','Lado fractura','Tipo de Fractura',
'Vitamina D','Leucocitos','Glucosa','Urea',
'Creatinina','CKD-EPI','Colinesterasa','Albumina','Movilidad PreFractura', 'Demora_Qx'
])[sorted_idx])
plt.title('Feature Importance')
# %%
train_data[0]

# %%


model.predict_proba(['Mujer', 92, 'Hospitalizado', 7, 4, 'Izquierda', 'Pertrocantérea', 0,
 10.2, 92, 53, 0.38, 91, 2751, 25, 4, 2.4])

# %%
model.predict_proba(['Mujer', 92, 'Hospitalizado', 7, 4, 'Izquierda', 'Pertrocantérea', 0,
 10.2, 92, 53, 0.38, 91, 2751, 25, 4, 3.4])

# %%
model.predict_proba(['Mujer', 92, 'Hospitalizado', 7, 4, 'Izquierda', 'Pertrocantérea', 0,
 10.2, 92, 53, 0.38, 91, 2751, 25, 4, 1.4])
# %%


X = df[['Sexo','Edad','Lugar de residencia','Cuestionario Pfeiffer','Categoría ASA','Lado fractura','Tipo de Fractura',
'Vitamina D','Leucocitos','Glucosa','Urea',
'Creatinina','CKD-EPI','Colinesterasa','Albumina','Movilidad PreFractura', 'Demora_Qx']]

y = df['Movilidad postFractura']



#%%
from sklearn.model_selection import cross_validate, train_test_split
X_train, X_eval, y_train, y_eval = train_test_split(X, y, test_size=0.20, shuffle=False)

#%%



from catboost import Pool, CatBoostClassifier

cat_features = [0, 2, 5, 6, 15]


train_dataset = Pool(data=X_train,
                     label=y_train,
                     cat_features=cat_features)

eval_dataset = Pool(data=X_eval,
                    label=y_eval,
                    cat_features=cat_features)

# Initialize CatBoostClassifier
model = CatBoostClassifier(iterations=10,
                           learning_rate=1,
                           depth=2, eval_metric= 'AUC')
# Fit model
model.fit(train_dataset,train_labels,
          eval_set=eval_dataset,
          verbose=True)
        
# Get predicted classes
preds_class = model.predict(eval_dataset)
# Get predicted probabilities for each class
preds_proba = model.predict_proba(eval_dataset)

# %%
preds_proba
# %%

eval_dataset = Pool(data=X_eval,
                    label=y_eval,
                    cat_features=cat_features)

# Initialize CatBoostClassifier

model = CatBoostClassifier(iterations=100, learning_rate=0.03,
                           eval_metric='AUC', l2_leaf_reg=0.8)

model.fit(train_data,
          train_labels,
          eval_set=eval_dataset,
          verbose=True, cat_features=cat_features)

print(model.get_best_iteration())

#%%
model.predict_proba(['Mujer', 92, 'Hospitalizado', 7, 4, 'Izquierda', 'Pertrocantérea', 0, 10.2, 92, 53, 0.38,
 91, 2751, 25, 1, 10.4])


# %%
train_data[0]
# %%
