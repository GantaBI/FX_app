# Sistema de Predicción de Fractura de Cadera

Sistema de predicción para pacientes con fractura de cadera utilizando modelos de Machine Learning. Permite visualizar datos reales de pacientes y simular casos hipotéticos.

## 📁 Estructura del Proyecto

```
FX_app/2026/
├── app/
│   ├── app.py                          # Aplicación principal Streamlit
│   ├── generate_pdf.py                 # Generación de PDFs con Pyppeteer
│   ├── pdf_styles.py                   # Estilos CSS para PDFs
│   ├── custom_styles.css               # Estilos personalizados Streamlit
│   │
│   ├── extract_data_model/
│   │   ├── extract_data_model.py       # Extracción de datos desde API
│   │   ├── .env                        # Variables de entorno (API_URL, API_KEY)
│   │   └── cache_pacientes.pkl         # Caché de datos administrativos
│   │
│   ├── utils/
│   │   ├── utils_mapeo.py              # Mapeo de datos (numérico ↔ texto)
│   │   ├── componentes_visualizacion.py # Componentes UI compartidos
│   │   └── componentes_simulador.py    # Formulario y lógica del simulador
│   │
│   └── models/
│       ├── ds_pre_oper/                # Modelo predicción pre-operatorio
│       ├── ds_post_oper/               # Modelo predicción post-operatorio
│       ├── ds_estancia/                # Modelo predicción estancia total
│       └── gsitalta/                   # Modelo clasificación situación al alta
│
└── paciente_*.json                     # JSONs de pacientes extraídos
```

## 🔄 Flujo de la Aplicación

### 1. **Extracción de Datos** (`extract_data_model.py`)

```
API Externa → extract_data_model.py → paciente_XXXXX.json
```

**Funcionalidad:**
- Conecta con API externa usando credenciales en `.env`
- Descarga datos administrativos, constantes vitales, escalas, antecedentes
- Procesa y limpia los datos
- Aplica valores por defecto para datos faltantes
- Genera JSON con estructura lista para el modelo
- Guarda en `/home/ubuntu/FX_app/2026/paciente_XXXXX.json`

**Variables de entorno requeridas:**
```bash
API_URL=https://tu-api.com
API_KEY=tu_clave_api
PACIENTE_ID=PACIENTE
```

### 2. **Aplicación Principal** (`app.py`)

```
Streamlit UI → app.py → Modelos ML → Visualización/PDF
```

**Modos de operación:**

#### A) **Visualización de Paciente Real**
1. Carga `TARGET_ID` (desde variable de entorno o input manual)
2. Verifica si existe `paciente_{ID}.json`
3. Si no existe, ejecuta `extract_data_model.py`
4. Enriquece datos con `enriquecer_datos_para_ui()`
5. Ejecuta predicciones con modelos ML
6. Muestra visualización con `mostrar_visualizacion()`
7. Permite generar PDF del informe

#### B) **Simulador**
1. Usuario completa formulario con datos del paciente
2. Datos se convierten con `preparar_datos_simulacion_para_modelo()`
3. Se ejecutan predicciones
4. Muestra resultados
5. Permite generar PDF de la simulación

### 3. **Mapeo de Datos** (`utils_mapeo.py`)

**Funciones principales:**

- **`enriquecer_datos_para_ui(data)`**
  - Convierte códigos numéricos → texto legible
  - Procesa fechas, escalas, constantes vitales
  - Añade sufijo `_map` a variables para UI
  - Ejemplo: `itipsexo: 1` → `itipsexo_map: "Mujer"`

- **`preparar_datos_simulacion_para_modelo(datos_simulacion)`**
  - Convierte datos del simulador → formato del modelo
  - Inverso de `enriquecer_datos_para_ui()`
  - Copia estructura one-hot encoded del paciente base
  - Ejemplo: `itipsexo_map: 0` → `itipsexo: 0`

### 4. **Componentes de Visualización**

#### `componentes_visualizacion.py`
- **`mostrar_visualizacion()`**: Renderiza toda la interfaz del paciente/simulación
  - Datos del paciente
  - Predicciones de estancia
  - Constantes vitales
  - Alergias, comorbilidades, escalas geriátricas
  - Gráfico de situación al alta

#### `componentes_simulador.py`
- **`mostrar_formulario_simulador()`**: Formulario de entrada de datos
- **`calcular_predicciones_simulador()`**: Ejecuta modelos con datos del formulario
- **`mostrar_resultados_simulador()`**: Muestra predicciones
- **`mostrar_botones_accion_simulador()`**: Botones para nueva simulación/PDF

### 5. **Generación de PDFs** (`generate_pdf.py`)

```
Streamlit → Pyppeteer → Chromium headless → PDF
```

**Proceso:**
1. Lanza navegador Chromium headless
2. Carga Streamlit con parámetros especiales (`?modo=simulacion`)
3. Inyecta CSS para ocultar elementos de Streamlit
4. Captura secciones definidas con clase `.no-overlap`
5. Genera PDFs individuales por sección
6. Combina en `informe_final.pdf`

**Configuración:**
- Viewport: 1920x1080
- Formato: A4
- Escala: 1.1 (ajustable)
- Rutas de salida:
  - Paciente real: `app/informes/original/`
  - Simulación: `app/informes/simulacion/`

### 6. **Modelos de Machine Learning**

Cada modelo contiene:
- `modelo_*.pkl`: Modelo entrenado (ElasticNet/RandomForest)
- `scaler.pkl`: StandardScaler para normalización
- `columnas_modelo.pkl`: Orden de features esperadas
- `clases_target.pkl`: Clases para clasificación (solo gsitalta)

**Predicciones:**
- **Pre-operatorio**: Días antes de cirugía
- **Post-operatorio**: Días después de cirugía  
- **Estancia total**: Días totales de hospitalización
- **Situación al alta**: Mejora vs Empeora (clasificación)

## Instalación y Uso

### Requisitos
```bash
pip install streamlit pandas plotly pyppeteer PyPDF2 nest-asyncio requests python-dotenv joblib scikit-learn
```

### Configuración
1. Crear archivo `.env` en `app/extract_data_model/`:
```bash
API_URL=https://tu-api.com
API_KEY=tu_clave_secreta
```

2. Variables por defecto para datos faltantes:
   - Editar `VALORES_DEFECTO` en `extract_data_model.py`
   - Basados en medianas del dataset de entrenamiento

### Ejecución

**Local:**
```bash
cd ~/FX_app/2026/app
source ~/.venv/bin/activate
streamlit run app.py
```

**Acceso remoto (servidor):**
```bash
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

**Con tmux (mantener ejecutándose):**
```bash
tmux new -s streamlit
cd ~/FX_app/2026/app
source ~/.venv/bin/activate
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
# Ctrl+B, D para desconectar
# tmux attach -t streamlit para reconectar
```

**Cambiar ID de paciente:**
```bash
PACIENTE_ID=LNRV194101570 streamlit run app.py
```

### Generar PDF manualmente
```bash
cd ~/FX_app/2026/app
python generate_pdf.py                 # Paciente real
python generate_pdf.py --simulacion    # Simulación
```

## 📊 Valores por Defecto (Datos Faltantes)

Basados en medianas del dataset de 856 pacientes:

| Variable | Valor por Defecto | Justificación |
|----------|-------------------|---------------|
| Edad | 91 años | Mediana del dataset |
| Sexo | Mujer (1) | 76% de pacientes son mujeres |
| Tensión mín/máx | 70/150 mmHg | Mediana |
| Temperatura | 36.6°C | Mediana |
| Saturación O2 | 94% | Mediana |
| Barthel | 20 | Dependencia grave (mediana) |
| Braden | 14 | Riesgo moderado (mediana) |
| Riesgo caída | 7 | Alto riesgo (mediana) |
| Movilidad | 2 | Dependiente (mediana) |
| Comorbilidades | 0 (No) | Mayoría no las presenta |

## Seguridad

- API Key almacenada en variable de entorno
- Validación de inputs del usuario
- Timeouts en llamadas API (60s)
- Caché de datos administrativos (6 horas)


## 📝 Notas Técnicas

### Codificación de Variables
- **Sexo**: 0=Hombre, 1=Mujer
- **Binarias**: 0=No, 1=Sí
- **Lado fractura**: 0=No especificado, 1=Izquierda, 2=Derecha
- **Procedencia**: 0=Domicilio, 1=Otro Centro

### Formato de Fechas
- Entrada API: `YYYY-MM-DD HH:MM:SS`
- Visualización: `DD/MM/YYYY HH:MM`
- Zona horaria: Europe/Madrid

### Estructura JSON de Paciente
```json
{
  "gidenpac": "LNRV194101570",
  "itipsexo": 1,
  "ds_edad": 85,
  "ntensmin": 69,
  "barthel": 15,
  "ds_HTA": 0,
  "gdiagalt_S72.141A": 1,
  "ds_izq_der_1": 0,
  "ds_izq_der_2": 1,
  ...
}
```