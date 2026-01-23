'''
Para extarer los datos de los pacientes desde la API y procesarlos para que estén listos para el modelo de predicción.
'''

import os, requests, datetime, pickle
import pandas as pd
import json
from pathlib import Path
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
load_dotenv(Path(__file__).parent / '.env')
API_URL = os.getenv("API_URL").rstrip('/')
HEADERS = {'XApiKey': os.getenv("API_KEY")}
TARGET_ID = "SRRD193407690"
CACHE_FILE = Path(__file__).parent / "cache_pacientes.pkl"
OUTPUT_FILE = Path(__file__).parent / f"paciente_{TARGET_ID}.json"
CACHE_HORAS = 6
DIAS_MAXIMO_BUSQUEDA = 30
hoy = datetime.date.today()

# --- HELPERS ---
def cargar_cache():
    try:
        with open(CACHE_FILE, 'rb') as f:
            cache = pickle.load(f)
            if datetime.datetime.now() - cache['timestamp'] < datetime.timedelta(hours=CACHE_HORAS):
                print("⚡ Usando caché")
                return cache['data']
    except:
        pass
    return None

def api_get(endpoint, params=None):
    try:
        response = requests.get(f"{API_URL}/{endpoint}", headers=HEADERS, params=params, timeout=60)
        response.raise_for_status()
        
        if not response.text.strip():
            print(f"⚠️ {endpoint}: Respuesta vacía")
            return []
            
        return response.json()
        
    except requests.exceptions.Timeout:
        print(f"❌ {endpoint}: Timeout después de 60s")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint}: Error de red - {e}")
        return []
    except json.JSONDecodeError:
        print(f"❌ {endpoint}: Respuesta no es JSON")
        print(f"   Contenido: {response.text[:100]}")
        return []
    


# --- DESCARGA DATOS ---
params_fechas = {
    "FechaInicio": (hoy - datetime.timedelta(days=DIAS_MAXIMO_BUSQUEDA)).strftime("%Y/%m/%d"),
    "FechaFin": hoy.strftime("%Y/%m/%d")
}
'''
# Test
print("Test vitals:", len(api_get("ApuntesPaciente/ConstantesVitales", params_fechas)))
print("Test antecedentes:", len(api_get("Valoraciones/ValoracionesAntecedentesPersonales", params_fechas)))
print("Test escalas:", len(api_get("Valoraciones/ValoracionesEnfermeria", params_fechas)))
print("Test valoraciones SIN fechas:", len(api_get("Valoraciones/ValoracionesMedicas",params_fechas)))
'''

data_admin = cargar_cache()
if not data_admin:
    print("📡 Descargando datos administrativos...")
    data_admin = api_get("DatosAdministrativos/DatosIdentificativosAdministrativos", params_fechas)
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump({'timestamp': datetime.datetime.now(), 'data': data_admin}, f)

row = next((r for r in data_admin if str(r.get('gidenpac')) == TARGET_ID), None)
if not row:
    print(f"❌ Paciente {TARGET_ID} no encontrado en datos administrativos")
    exit(1)

print("📡 Descargando datos clínicos...")
vitals = api_get("ApuntesPaciente/ConstantesVitales", params_fechas)
antecedentes = api_get("Valoraciones/ValoracionesAntecedentesPersonales", params_fechas)
escalas = api_get("Valoraciones/ValoracionesEnfermeria", params_fechas)
valoraciones = api_get("Valoraciones/ValoracionesMedicas")

# --- VALIDACIÓN: Filtrar por paciente ---
vitals_paciente = [v for v in vitals if str(v.get('gidenpac')) == TARGET_ID]
antecedentes_paciente = [a for a in antecedentes if str(a.get('gidenpac')) == TARGET_ID]
escalas_paciente = [e for e in escalas if str(e.get('gidenpac')) == TARGET_ID]
valoraciones_paciente = [val for val in valoraciones if str(val.get('gidenpac')) == TARGET_ID]

# --- CONTROL: Verificar que hay datos del paciente ---
if not vitals_paciente:
    print(f"⚠️ ADVERTENCIA: No hay constantes vitales para {TARGET_ID}")
if not escalas_paciente:
    print(f"⚠️ ADVERTENCIA: No hay escalas de enfermería para {TARGET_ID}")
if not antecedentes_paciente:
    print(f"⚠️ ADVERTENCIA: No hay antecedentes personales para {TARGET_ID}")
if not valoraciones_paciente:
    print(f"⚠️ ADVERTENCIA: No hay valoraciones médicas para {TARGET_ID}")

# --- VITALES (más reciente con valores válidos) ---
vitals_paciente = sorted(
    vitals_paciente, 
    key=lambda x: pd.to_datetime(x.get('fapuntes'), errors='coerce') or pd.Timestamp.min,
    reverse=True
)

ntensmin = ntensmax = ntempera = nsatuoxi = None

for v in vitals_paciente:
    if ntensmin is None:
        val = pd.to_numeric(v.get('ntensmin'), errors='coerce')
        if pd.notna(val):
            ntensmin = int(val)
    
    if ntensmax is None:
        val = pd.to_numeric(v.get('ntensmax'), errors='coerce')
        if pd.notna(val):
            ntensmax = int(val)
    
    if ntempera is None:
        val = pd.to_numeric(v.get('ntempera'), errors='coerce')
        if pd.notna(val):
            ntempera = float(val)
    
    if nsatuoxi is None:
        val = pd.to_numeric(v.get('nsatuoxi'), errors='coerce')
        if pd.notna(val):
            nsatuoxi = int(val)
    
    # Si ya tenemos todos, salir
    if all(x is not None for x in [ntensmin, ntensmax, ntempera, nsatuoxi]):
        break

# --- ANTECEDENTES (agregación: si aparece alguna vez = 1) ---
ant_flags = {'alergia_med': 0, 'alergia_ali': 0, 'otras_alergias': 0, 'hta_ant': 0, 'diabetes_ant': 0}
ant_map = {
    'Alergia medicamentosa': 'alergia_med',
    'Alergia alimenticia': 'alergia_ali',
    'Otras alergias': 'otras_alergias',
    'HTA': 'hta_ant',
    'Diabetes Mellitus': 'diabetes_ant'
}

for ant in antecedentes_paciente:
    dconclin = str(ant.get('dconclin', ''))
    for keyword, flag in ant_map.items():
        if keyword in dconclin:
            ant_flags[flag] = 1

for ant in antecedentes_paciente:
    dconclin = str(ant.get('dconclin', ''))
    vbivalor = ant.get('vbivalor')
    if pd.notnull(vbivalor):
        vbivalor = 1 if str(vbivalor).upper() in ['S', 'A'] else (0 if isinstance(vbivalor, str) else int(vbivalor))
        for keyword, flag in ant_map.items():
            if keyword in dconclin and ant_flags[flag] == 1:
                ant_flags[flag] = vbivalor

# --- ESCALAS (valor máximo de cada escala) ---
patterns = {
    'movilidad': ["_Movilidad", "Movilidad"],
    'barthel': ["Resultado Indice de Barthel"],
    'braden': ["Resultado Escala de Braden"],
    'riesgo_caida': ["Resultado Escala Riesgo Caidas"]
}
valores = {k: [] for k in patterns}

for e in escalas_paciente:
    dconclin = str(e.get('dconclin', ''))
    max_val = pd.Series([pd.to_numeric(e.get(f), errors='coerce') for f in ['ncodtabu', 'nvalncon', 'ovallcon', 'vbivalor']]).max()
    for key, keywords in patterns.items():
        if any(kw in dconclin for kw in keywords) and pd.notna(max_val):
            valores[key].append(max_val)

movilidad = int(max(valores['movilidad'])) if valores['movilidad'] and max(valores['movilidad']) <= 4 else None
barthel = int(max(valores['barthel'])) if valores['barthel'] else None
braden = int(max(valores['braden'])) if valores['braden'] else None
riesgo_caida = int(max(valores['riesgo_caida'])) if valores['riesgo_caida'] else None

# --- CONDICIONES MÉDICAS (si aparece alguna vez = 1) ---
medical_patterns = {
    'ds_HTA': ['HTA'],
    'ds_ITU': ['ITU'],
    'ds_anemia': ['ANEMIA'],
    'ds_vitamina_d': ['VITAMINA D'],
    'ds_obesidad': ['OBESIDAD'],
    'ds_osteoporosis': ['OSTEOPOROSIS'],
    'ds_acido_folico': ['ACIDO FOLICO'],
    'ds_insuficiencia_respiratoria': [
        'INSUFICIENCIA RESPIRATORIA AGUDA', 'INSUFICIENCIA RESPIRATORIA',
        'INSUFICIENCIA RESPIRATORIA AGUDA PARCIAL', 'INSUFICIENCIA RESPIRATORIA CRÓNICA AGUDIZADA',
        'INSUFICIENCIA RESPIRATORIA PARCIAL', 'INSUFICIENCIA RESPIRATORIA 2RIA',
        'INSUFICIENCIA RESPIRATORIA GLOBAL', 'INSUFICIENCIA RESPIRATORIA AGUDA SECUNDARIA',
        'INSUFICIENCIA RESPIRATORIA PARCIAL CRÓNICA AGUDIZADA',
        'INSUFICIENCIA RESPIRATORIA AGUDA PARCIAL RESUELTA', 'EPOC AGUDIZADO', 'EPOC', 'EPOC REAGUDIZADO'
    ],
    'ds_diabetes': [
        'DM TIPO 2 ', 'DM TIPO II', 'DIABETES MELLITUS', 'DM-II', 'DIABETES MELLITUS TIPO II', 'DIABETES'
    ],
    'ds_insuficiencia_cardiaca': [
        'INSUFICIENCIA CARDIACA', 'INSUFICIENCIA CARDIACA DESCOMPENSADA', 'INSUFICIENCIA RESPIRATORIA CRÓNICA',
        'INSUFICIENCIA CARDIACA CONGESTIVA', 'I. CARDIACA', 'INSUFICIENCIA CARDIACA CONGESTIVA DESCOMPENSADA',
        'INSUFICIENCIA CARDÍACA', 'INSUFICIENCIA CARDIACA CRÓNICA DESCOMPENSADA',
        'INSUFICIENCIA CARDIACA CONGESTIVA AGUDA', 'ICC AGUDA', 'CARDIOPATIA ISQUEMICA',
        'CARDIOPATÍA ISQUÉMICA', 'ICC', 'ICC DESCOMPENSADA'
    ],
    'ds_deterioro_cognitivo': ['DETERIORO COGNITIVO', 'DEMENCIA'],
    'ds_exitus': ['EXITUS', 'ÉXITUS'],
    'ds_insuficiencia_renal': [
        'I. RENAL', 'INSUFICIENCIA RENAL', 'ENFERMEDAD RENAL CRÓNICA', 'INSUFICIENCIA RENAL AGUDA',
        'INSUFICIENCIA RENAL CRÓNICA AGUDIZADA', 'INSUFICIENCIA RENAL CRONICA', 'IRC',
        'ERC REAGUDIZADA', 'ERC AGUDIZADA', 'ERC'
    ]
}

conditions = {k: 0 for k in medical_patterns}

for val in valoraciones_paciente:
    ovallcon = str(val.get('ovallcon', '')).upper()
    for condition, keywords in medical_patterns.items():
        if any(kw.upper() in ovallcon for kw in keywords):
            conditions[condition] = 1

# --- DIAGNÓSTICO ---
gdiagalt = str(row.get('gdiagalt', ''))
derecho_codes = ["M66.151","M80.051A","M97.01XA","M97.01XD","M97.01XS","S72.001A","S72.011A","S72.091A","S72.101A","S72.141A","S73.031A","S79.811A","T84.010","T84.010A","T84.010D","T84.010S","T84.040","T84.040A","T84.040D","T84.040S","T84.090A"]
izquierdo_codes = ["M66.152","M97.02XA","M97.02XD","M97.02XS","S70.02XA","S72.002A","S72.012A","S72.102A","S72.112A","S72.142A","S72.142D","S72.22XA","T84.011","T84.011A","T84.011D","T84.011S","T84.021A","T84.031A","T84.041","T84.041A","T84.041D","T84.041S"]
no_especificado = ["M66.15","M66.159","M84.359","M84.359A","M84.359D","M84.359G","M84.359K","M84.359P","M84.359S","M84.459","M84.459A","M84.459D","M84.459G","M84.459K","M84.459P","M84.459S","M84.559","M84.559A","M84.559D","M84.559G","M84.559K","M84.559P","M84.559S","M84.659","M84.659A","M84.659D","M84.659G","M84.659K","M84.659P","M84.659S","T84.84XA","Z51.89"]
all_codes = derecho_codes + izquierdo_codes + no_especificado

ds_izq_der = None
if any(code in gdiagalt for code in no_especificado):
    ds_izq_der = 0
elif any(code in gdiagalt for code in izquierdo_codes):
    ds_izq_der = 1
elif any(code in gdiagalt for code in derecho_codes):
    ds_izq_der = 2

gdiagalt_onehot = {f'gdiagalt_{code}': int(code in gdiagalt) for code in all_codes}
izq_der_onehot = {
    'ds_izq_der_0': int(ds_izq_der == 0),
    'ds_izq_der_1': int(ds_izq_der == 1),
    'ds_izq_der_2': int(ds_izq_der == 2)
}

# --- TEMPORALES ---
fl = pd.to_datetime(row.get('fllegada'), errors='coerce')
dia_semana = fl.weekday() + 1 if pd.notna(fl) else None
mes_llegada = fl.month if pd.notna(fl) else None

hora = fl.hour if pd.notna(fl) else None
if hora is not None:
    turno = 0 if 8 <= hora < 15 else (1 if 15 <= hora < 22 else 2)
else:
    turno = None

dia_semana_onehot = {f'ds_dia_semana_llegada_{i}': int(dia_semana == i) for i in range(1, 8)}
mes_onehot = {f'ds_mes_llegada_{i}': int(mes_llegada == i) for i in range(1, 13)}
turno_onehot = {
    'ds_turno_0': int(turno == 0),
    'ds_turno_1': int(turno == 1),
    'ds_turno_2': int(turno == 2)
}

# --- RESULTADO ---
fn = pd.to_datetime(row.get('fnacipac'), errors='coerce')

resultado = {
    "gidenpac": TARGET_ID,
    "itipsexo": {'H': 0, 'M': 1}.get(row.get('itipsexo')),
    "iotrocen": {'N': 0, 'S': 1}.get(row.get('iotrocen')),
    "ds_edad": (hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))) if pd.notna(fn) else None,
    "ds_centro_afueras": int(pd.to_numeric(row.get('gcodipos'), errors='coerce') in {24001,24002,24003,24004,24005,24006,24007,24008,24009,24010,24012,24070,24071,24080}),
    "ntensmin": ntensmin,
    "ntensmax": ntensmax,
    "ntempera": ntempera,
    "nsatuoxi": nsatuoxi,
    "ds_alergia_medicamentosa": ant_flags['alergia_med'],
    "ds_alergia_alimenticia": ant_flags['alergia_ali'],
    "ds_otras_alergias": ant_flags['otras_alergias'],
    "movilidad": movilidad,
    "barthel": barthel,
    "braden": braden,
    "riesgo_caida": riesgo_caida,
    "ds_izq_der": ds_izq_der
}

resultado.update(conditions)
resultado.update(gdiagalt_onehot)
resultado.update(izq_der_onehot)      
resultado.update(dia_semana_onehot)   
resultado.update(mes_onehot)          
resultado.update(turno_onehot)
resultado['ds_HTA'] = max(ant_flags['hta_ant'], resultado.get('ds_HTA', 0))
resultado['ds_diabetes'] = max(ant_flags['diabetes_ant'], resultado.get('ds_diabetes', 0))

# --- GUARDAR ---
excluir = ['ds_pre_oper', 'ds_post_oper'] + [k for k in resultado.keys() if k.startswith(('gdiagalt_', 'ds_izq_der_', 'ds_dia_', 'ds_mes_', 'ds_turno_'))]
faltantes = [k for k in resultado.keys() if k not in excluir and resultado[k] is None]

if faltantes:
    print(f"⚠️ Campos críticos faltantes ({len(faltantes)}): {faltantes}")

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)

print(f"✅ Datos guardados en: {OUTPUT_FILE}")
print(f"📊 Total de campos: {len(resultado)}")


