import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

# Cargar datos preprocesados
df = pd.read_csv('/home/ubuntu/STG-fractura_cadera/2026/DATOS_PREPROCESADOS.csv')

# Separar features y target
X = df.drop(['gsitalta', 'gidenpac','gmotalta','ds_izq_der','ds_estancia','ds_pre_oper', 'ds_post_oper',
             'ds_vivo_alta', 'lugar_residencia','lugar_procedencia',  'destino_alta', ], axis=1) # Eliminar columnas no predictoras
y = df['gsitalta']  # Variable objetivo

print("="*60)
print("DATASET INFO")
print("="*60)
print(f"Samples: {len(X)}")
print(f"Features: {len(X.columns)}")
print(f"\nDistribución clases:\n{y.value_counts()}")
print(f"Porcentajes:\n{y.value_counts(normalize=True)*100}")

# Normalizar features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Definir modelos
models = {
    'Logistic Regression (L2)': LogisticRegression(
        max_iter=1000, 
        class_weight='balanced',
        random_state=42,
        multi_class='multinomial'
    ),
    'Logistic Regression (L1)': LogisticRegression(
        max_iter=1000, 
        class_weight='balanced',
        penalty='l1',
        solver='saga',
        random_state=42,
        multi_class='multinomial'
    ),
    'Random Forest': RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        class_weight='balanced',
        random_state=42,
        min_samples_leaf=2
    )
}

# Métricas
scoring = {
    'accuracy': 'accuracy',
    'f1_macro': 'f1_macro',
    'f1_weighted': 'f1_weighted'
}

# Validación cruzada estratificada
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print("\n" + "="*60)
print("CROSS-VALIDATION RESULTS (5-Fold Stratified)")
print("="*60)

results = {}
for name, model in models.items():
    print(f"\n{name}:")
    print("-" * 40)
    
    cv_results = cross_validate(
        model, X_scaled, y, 
        cv=cv, 
        scoring=scoring,
        return_train_score=True
    )
    
    results[name] = cv_results
    
    print(f"  Train Accuracy: {cv_results['train_accuracy'].mean():.3f} (+/- {cv_results['train_accuracy'].std():.3f})")
    print(f"  Test Accuracy:  {cv_results['test_accuracy'].mean():.3f} (+/- {cv_results['test_accuracy'].std():.3f})")
    print(f"  F1 Macro:       {cv_results['test_f1_macro'].mean():.3f} (+/- {cv_results['test_f1_macro'].std():.3f})")
    print(f"  F1 Weighted:    {cv_results['test_f1_weighted'].mean():.3f} (+/- {cv_results['test_f1_weighted'].std():.3f})")

# Train/Test Split (80/20)
from sklearn.model_selection import train_test_split

# Eliminar clases con muy pocos casos (< 3 para poder estratificar)
print("\n" + "="*60)
print("LIMPIEZA DE CLASES MINORITARIAS")
print("="*60)
class_counts = y.value_counts()
print("Distribución original:")
print(class_counts)

min_samples = 3
valid_classes = class_counts[class_counts >= min_samples].index
mask = y.isin(valid_classes)

X_clean = X_scaled[mask]
y_clean = y[mask]

print(f"\nClases eliminadas: {set(y.unique()) - set(y_clean.unique())}")
print(f"Muestras restantes: {len(y_clean)} de {len(y)}")
print(f"\nDistribución limpia:")
print(y_clean.value_counts())

# Ahora sí podemos hacer split estratificado
X_train, X_test, y_train, y_test = train_test_split(
    X_clean, y_clean, 
    test_size=0.2, 
    random_state=42, 
    stratify=y_clean
)

print("\n" + "="*60)
print("TRAIN/TEST SPLIT")
print("="*60)
print(f"Train: {len(X_train)} samples")
print(f"Test:  {len(X_test)} samples")
print(f"\nTrain distribution:\n{y_train.value_counts()}")
print(f"\nTest distribution:\n{y_test.value_counts()}")

# Entrenar modelo final
print("\n" + "="*60)
print("MODELO FINAL (Random Forest)")
print("="*60)

best_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    class_weight='balanced',
    random_state=42,
    min_samples_leaf=2
)
best_model.fit(X_train, y_train)

# Predicciones
y_train_pred = best_model.predict(X_train)
y_test_pred = best_model.predict(X_test)

print("\n--- TRAIN PERFORMANCE ---")
print(f"Accuracy: {(y_train_pred == y_train).mean():.3f}")
print("\n--- TEST PERFORMANCE ---")
print(f"Accuracy: {(y_test_pred == y_test).mean():.3f}")

print("\nTest Classification Report:")
print(classification_report(y_test, y_test_pred, zero_division=0))

print("\nTest Confusion Matrix:")
print(confusion_matrix(y_test, y_test_pred))

# Feature importance
print("\n" + "="*60)
print("TOP 15 FEATURES MÁS IMPORTANTES")
print("="*60)
feature_importance = best_model.feature_importances_
feature_names = X.columns
top_indices = np.argsort(feature_importance)[-15:][::-1]

for idx in top_indices:
    print(f"{feature_names[idx]:40s}: {feature_importance[idx]:.4f}")
