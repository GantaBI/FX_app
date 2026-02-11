'''
Transforma los códigos numéricos del JSON en texto legible para Streamlit.
Regla: Las nuevas variables se llaman {variable_original}_map

También hace la inversa: convierte datos del simulador (con sufijo _map) al formato que espera el modelo (sin sufijo).
'''
import pandas as pd
import json
import os


def enriquecer_datos_para_ui(data):
    """
    Recibe el diccionario de datos (data) cargado del JSON.
    Devuelve el mismo diccionario con campos extra '_map' añadidos.
    """
    if not data: 
        return {}
    
    # Diccionarios de Mapeo
    MAPPINGS = {
        "sexo": {0: "Hombre", 1: "Mujer"},
        "si_no": {0: "No", 1: "Sí"},
        "lado": {0: "No especificado", 1: "Izquierda", 2: "Derecha"},
        "procedencia": {0: "Domicilio", 1: "Otro Centro/Hospital"},
        "residencia": {1: "Urbano (León)", 0: "Rural/Afueras"},
        "turno": {0: "Mañana", 1: "Tarde", 2: "Noche", None: "Desconocido"}
    }
    
    # Mapeo automático de variables clínicas (Sí/No)
    vars_si_no = [
        "ds_HTA", "ds_diabetes", "ds_deterioro_cognitivo", 
        "ds_insuficiencia_respiratoria", "ds_insuficiencia_cardiaca", 
        "ds_anemia", "ds_insuficiencia_renal", "ds_ITU", "ds_vitamina_d", 
        "ds_osteoporosis", "ds_alergia_medicamentosa", "ds_alergia_alimentaria", 
        "ds_otra_alergias", "ds_obesidad", "ds_acido_folico"
    ]
    
    for var in vars_si_no:
        data[f"{var}_map"] = MAPPINGS["si_no"].get(data.get(var), "No")
    
    # Variables simples con mapeo directo
    data["itipsexo_map"] = MAPPINGS["sexo"].get(data.get("itipsexo"), "Desconocido")
    data["ds_edad_map"] = f"{data.get('ds_edad', 0)} años"
    data["iotrocen_map"] = MAPPINGS["procedencia"].get(data.get("iotrocen"), "Desconocida")
    data["ds_centro_afueras_map"] = MAPPINGS["residencia"].get(data.get("ds_centro_afueras"), "Desconocida")
    data["ds_izq_der_map"] = MAPPINGS["lado"].get(data.get("ds_izq_der"), "Desconocido")
    data["turno_raw_map"] = MAPPINGS["turno"].get(data.get("turno_raw"), "Desconocido")
    
    # Procesamiento de secciones específicas
    _procesar_fecha_llegada(data)
    _procesar_escalas(data)
    _procesar_constantes(data)
    _procesar_codigos_cie(data)
    _procesar_situacion_alta(data)
    
    return data


def _procesar_fecha_llegada(data):
    """Procesa y formatea la fecha de llegada"""
    fecha, hora = data.get("fllegada"), data.get("hllegada")
    
    if fecha and hora:
        try:
            data["fllegada_map"] = pd.to_datetime(f"{fecha} {hora}").strftime("%d/%m/%Y %H:%M")
            return
        except:
            pass
    
    if fecha:
        try:
            data["fllegada_map"] = pd.to_datetime(fecha).strftime("%d/%m/%Y")
            return
        except:
            pass
    
    # Fallback
    raw = data.get("fllegada_raw")
    if raw:
        try:
            data["fllegada_map"] = pd.to_datetime(raw).strftime("%d/%m/%Y %H:%M")
        except:
            data["fllegada_map"] = str(raw)
    else:
        data["fllegada_map"] = "Desconocida"


def _procesar_escalas(data):
    """Procesa las escalas geriátricas"""
    try:
        data["barthel_map"] = str(int(float(data.get('barthel', 0))))
    except:
        data["barthel_map"] = "0"
    
    try:
        data["movilidad_map"] = str(int(float(data.get('movilidad', 0))))
    except:
        data["movilidad_map"] = "0"
    
    try:
        data["braden_map"] = str(int(float(data.get('braden', 0))))
    except:
        data["braden_map"] = "0"
    
    try:
        data["riesgo_caida_map"] = str(int(float(data.get('riesgo_caida', 0))))
    except:
        data["riesgo_caida_map"] = "0"


def _procesar_constantes(data):
    """Procesa las constantes vitales"""
    # Variables enteras (tensión, saturación)
    for var in ["ntensmin", "ntensmax", "nsatuoxi"]:
        try:
            valor = data.get(var)
            if valor is not None:
                data[f"{var}_map"] = str(int(float(valor)))
            else:
                data[f"{var}_map"] = "N/A"
        except (ValueError, TypeError):
            data[f"{var}_map"] = "N/A"
    
    # Temperatura (1 decimal)
    try:
        temp = data.get("ntempera")
        if temp is not None:
            data["ntempera_map"] = f"{float(temp):.1f}"
        else:
            data["ntempera_map"] = "N/A"
    except:
        data["ntempera_map"] = "N/A"


def _procesar_codigos_cie(data):
    """Procesa los códigos CIE de diagnóstico"""
    codigos_activos = [
        key.replace("gdiagalt_", "") 
        for key, value in data.items() 
        if key.startswith("gdiagalt_") and value in [1, "1"]
    ]
    data["gdiagalt_map"] = ", ".join(codigos_activos) if codigos_activos else "Sin códigos"


def _procesar_situacion_alta(data):
    """Procesa la situación al alta"""
    try:
        val_gsi = int(float(data.get("gsitalta", 0)))
    except:
        val_gsi = 0
    
    if val_gsi in [1, 2]:
        data["gsitalta_map"] = "Mejora"
    elif val_gsi in [3, 4, 5]:
        data["gsitalta_map"] = "Empeora"
    else:
        data["gsitalta_map"] = "Desconocido"


def preparar_datos_simulacion_para_modelo(datos_simulacion, ruta_json_base=None):
    """
    Convierte datos del simulador (con sufijo _map) al formato que espera el modelo (sin sufijo).
    También copia las columnas one-hot encoded del paciente base.
    
    Args:
        datos_simulacion: Diccionario con datos del formulario del simulador (con sufijo _map)
        ruta_json_base: Ruta al JSON del paciente real para copiar estructura one-hot
    
    Returns:
        Diccionario con datos en formato del modelo
    """
    # Cargar datos base del paciente real
    data_base = _cargar_datos_base(ruta_json_base)
    
    # Mapeo de nombres: simulador (_map) -> modelo (sin _map)
    MAPEO_CAMPOS = {
        'itipsexo_map': 'itipsexo',
        'ds_edad_map': 'ds_edad',
        'iotrocen_map': 'iotrocen',
        'ds_centro_afueras_map': 'ds_centro_afueras',
        'ntensmin_map': 'ntensmin',
        'ntensmax_map': 'ntensmax',
        'ntempera_map': 'ntempera',
        'nsatuoxi_map': 'nsatuoxi',
        'ds_ITU_map': 'ds_ITU',
        'ds_insuficiencia_respiratoria_map': 'ds_insuficiencia_respiratoria',
        'ds_insuficiencia_cardiaca_map': 'ds_insuficiencia_cardiaca',
        'ds_deterioro_cognitivo_map': 'ds_deterioro_cognitivo',
        'ds_insuficiencia_renal_map': 'ds_insuficiencia_renal',
        'ds_HTA_map': 'ds_HTA',
        'ds_diabetes_map': 'ds_diabetes',
        'ds_obesidad_map': 'ds_obesidad',
        'ds_osteoporosis_map': 'ds_osteoporosis',
        'ds_anemia_map': 'ds_anemia',
        'ds_vitamina_d_map': 'ds_vitamina_d',
        'ds_acido_folico_map': 'ds_acido_folico',
        'ds_alergia_medicamentosa_map': 'ds_alergia_medicamentosa',
        'ds_alergia_alimentaria_map': 'ds_alergia_alimenticia',  # OJO: cambio de nombre
        'ds_otra_alergias_map': 'ds_otras_alergias',  # OJO: cambio de nombre
        'barthel_map': 'Barthel',  # OJO: mayúscula
        'braden_map': 'braden',
        'riesgo_caida_map': 'riesgo_caida',
        'movilidad_map': 'movilidad',
        'ds_izq_der_map': 'ds_izq_der',
        'gdiagalt_map': 'gdiagalt'
    }
    
    # Aplicar mapeo básico
    datos_modelo = {}
    for key_simulador, key_modelo in MAPEO_CAMPOS.items():
        if key_simulador in datos_simulacion:
            datos_modelo[key_modelo] = datos_simulacion[key_simulador]
    
    # Copiar columnas one-hot encoded del paciente base
    PREFIJOS_ONE_HOT = ['gdiagalt_', 'ds_izq_der_', 'ds_dia_semana_', 'ds_mes_', 'ds_turno_']
    
    for key, value in data_base.items():
        if any(key.startswith(prefix) for prefix in PREFIJOS_ONE_HOT):
            datos_modelo[key] = value
    
    return datos_modelo


def _cargar_datos_base(ruta_json_base):
    """Carga el JSON del paciente base desde la carpeta pacientes/"""
    # Si no se especifica ruta, usar el PACIENTE_ID del entorno
    if ruta_json_base is None:
        TARGET_ID = os.getenv("PACIENTE_ID", "LNRV194101570")
        ruta_json_base = f"paciente_{TARGET_ID}.json"
    
    # Construir ruta a la carpeta pacientes/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    carpeta_pacientes = os.path.join(base_dir, '..', 'pacientes')
    ruta_completa = os.path.join(carpeta_pacientes, ruta_json_base)
    
    if not os.path.exists(ruta_completa):
        raise FileNotFoundError(f"No se encontró el archivo {ruta_completa}")
    
    with open(ruta_completa, "r") as file:
        return json.load(file)