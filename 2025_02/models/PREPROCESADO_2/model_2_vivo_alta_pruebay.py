#%% Importar librerías
import pandas as pd
import numpy as np
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTENC
from collections import Counter

#%% Cargar datos
df = pd.read_csv('/home/ubuntu/STG-fractura_cadera/2025_02/models/PREPROCESADO_2/DATOS_PREPROCESADOS_2.csv')

# Selección de columnas relevantes
columnas_relevantes = [
    'ds_vivo_alta', 'itipsexo', 'iotrocen', 
    'gdiagalt', 'ds_izq_der', 'ds_turno', 'ds_edad', 'ds_estancia', 
    'ds_pre_oper', 'ds_post_oper', 'ds_dia_semana_llegada', 
    'ds_mes_llegada', 'ds_centro_afueras', 'ds_alergia_medicamentosa', 
    'ds_alergia_alimenticia', 'ds_otras_alergias', 'ds_ITU', 'ds_anemia', 
    'ds_vitamina_d', 'ds_insuficiencia_respiratoria', 'ds_insuficiencia_cardiaca', 
    'ds_deterioro_cognitivo', 'ds_insuficiencia_renal', 'ds_HTA', 'ds_diabetes'
]
df = df[columnas_relevantes]

#%% Variables categóricas
cat_features = [
    'itipsexo', 'iotrocen', 'gdiagalt', 
    'ds_izq_der', 'ds_turno', 'ds_dia_semana_llegada', 'ds_mes_llegada', 
    'ds_centro_afueras', 'ds_alergia_medicamentosa', 'ds_alergia_alimenticia', 
    'ds_otras_alergias', 'ds_ITU', 'ds_anemia', 'ds_vitamina_d', 
    'ds_insuficiencia_respiratoria', 'ds_insuficiencia_cardiaca', 
    'ds_deterioro_cognitivo', 'ds_insuficiencia_renal', 'ds_HTA', 'ds_diabetes'
]

# Convertir variables categóricas a tipo `str`
for col in cat_features:
    df[col] = df[col].astype(str)

#%% 🔹 Filtrar clases con menos de 3 muestras antes de train_test_split
class_counts = df['ds_vivo_alta'].value_counts()
valid_classes = class_counts[class_counts >= 3].index
df_filtered = df[df['ds_vivo_alta'].isin(valid_classes)]

#%% Separar variable objetivo y predictores
X = df_filtered.drop(['ds_vivo_alta'], axis=1)  # No usamos 'gsitalta'
y = df_filtered['ds_vivo_alta']

# División de datos en entrenamiento y prueba con `stratify`
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 🔹 Verificar distribución antes del balanceo
print("Distribución antes del balanceo:", Counter(y_train))

#%% 🔹 Aplicar balanceo con SMOTENC si hay desbalance de clases
if len(set(y_train)) < 2:
    print("❌ No se puede aplicar SMOTENC porque hay menos de 2 clases.")
    X_train_balanced, y_train_balanced = X_train, y_train
else:
    # Obtener índices de variables categóricas
    cat_feature_indices = [X_train.columns.get_loc(col) for col in cat_features if col in X_train.columns]

    # Aplicar SMOTENC para balancear clases
    smote_nc = SMOTENC(categorical_features=cat_feature_indices, random_state=42, k_neighbors=1, sampling_strategy="not majority")
    X_train_balanced, y_train_balanced = smote_nc.fit_resample(X_train, y_train)

    print("Distribución balanceada de clases:", Counter(y_train_balanced))

#%% 🔹 Asegurar que las variables categóricas están bien definidas
for col in cat_features:
    X_train_balanced[col] = X_train_balanced[col].astype(str)
    X_test[col] = X_test[col].astype(str)

#%% 🔹 Calcular pesos de clase inversamente proporcionales a su frecuencia
class_weights = {cls: 1.0 / count for cls, count in Counter(y_train_balanced).items()}

# Normalizar pesos
max_weight = max(class_weights.values())
class_weights = {cls: weight / max_weight for cls, weight in class_weights.items()}

print("Pesos de clase:", class_weights)

#%% Entrenar el modelo con CrossEntropy y pesos de clase
model = CatBoostClassifier(
    iterations=500,                
    learning_rate=0.05,            
    max_depth=6,                   
    loss_function="CrossEntropy",   # CrossEntropy para clasificación binaria
    eval_metric="BalancedAccuracy", # Evalúa mejor en caso de desbalanceo
    verbose=10
)


model.fit(X_train_balanced, y_train_balanced, cat_features=cat_features, eval_set=(X_test, y_test))

#%% Predicciones y métricas
preds = model.predict(X_test)
print(classification_report(y_test, preds))

# %%
