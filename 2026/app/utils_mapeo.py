'''
utils_mapeo.py
--------------
Transforma los códigos numéricos del JSON en texto legible para Streamlit.
Regla: Las nuevas variables se llaman {variable_original}_map
'''
import pandas as pd

def enriquecer_datos_para_ui(data):
    """
    Recibe el diccionario de datos (data) cargado del JSON.
    Devuelve el mismo diccionario con campos extra '_map' añadidos.
    """
    if not data: return {}
    
    # 1. Diccionarios de Mapeo
    MAPPINGS = {
        "sexo": {0: "Hombre", 1: "Mujer"},
        "si_no": {0: "No", 1: "Sí"},
        "lado": {0: "No especificado", 1: "Izquierda", 2: "Derecha"},
        "procedencia": {0: "Domicilio", 1: "Otro Centro/Hospital"},
        "residencia": {1: "Urbano (León)", 0: "Rural/Afueras"},
        "turno": {0: "Mañana", 1: "Tarde", 2: "Noche", None: "Desconocido"}
    }

    # 2. Generación de Textos (Mapeo directo nombre_original -> nombre_original_map)
    
    # Demográficos
    data["itipsexo_map"] = MAPPINGS["sexo"].get(data.get("itipsexo"), "Desconocido")
    data["ds_edad_map"] = f"{data.get('ds_edad', 0)} años"
    data["iotrocen_map"] = MAPPINGS["procedencia"].get(data.get("iotrocen"), "Desconocida")
    data["ds_centro_afueras_map"] = MAPPINGS["residencia"].get(data.get("ds_centro_afueras"), "Desconocida")
    
    # -------------------------------------------------------------------------
    # FECHAS (Combinar Fecha + Hora)
    # -------------------------------------------------------------------------
    fecha = data.get("fllegada")
    hora = data.get("hllegada")
    
    if fecha and hora:
        # Si tenemos fecha y hora separadas en el JSON
        texto_completo = f"{fecha} {hora}" # Ej: "2026-01-02 17:33:20"
        try:
            # Lo convertimos a formato fecha real para formatearlo bonito
            data["fllegada_map"] = pd.to_datetime(texto_completo).strftime("%d/%m/%Y %H:%M")
        except:
            # Si falla el formato, lo mostramos tal cual viene
            data["fllegada_map"] = texto_completo
            
    elif fecha:
        # Si solo tenemos la fecha
        try:
            data["fllegada_map"] = pd.to_datetime(fecha).strftime("%d/%m/%Y")
        except:
            data["fllegada_map"] = str(fecha)
            
    else:
        # Fallback para versiones antiguas del JSON
        raw = data.get("fllegada_raw")
        if raw:
            try:
                data["fllegada_map"] = pd.to_datetime(raw).strftime("%d/%m/%Y %H:%M")
            except:
                data["fllegada_map"] = str(raw)
        else:
            data["fllegada_map"] = "Desconocida"
    # Turno
    data["turno_raw_map"] = MAPPINGS["turno"].get(data.get("turno_raw"), "Desconocido")
    
    # Diagnóstico Lado
    data["ds_izq_der_map"] = MAPPINGS["lado"].get(data.get("ds_izq_der"), "Desconocido")

    # Clínicos (Sí/No)
    listado_clinico = [
        "ds_HTA", "ds_diabetes", "ds_deterioro_cognitivo", 
        "ds_insuficiencia_respiratoria", "ds_insuficiencia_cardiaca", 
        "ds_anemia", "ds_insuficiencia_renal", 
        "ds_ITU", "ds_vitamina_d", "ds_osteoporosis","ds_alergia_medicamentosa",
        "ds_alergia_alimentaria", "ds_otra_alergias","ds_obesidad", "ds_acido_folico"
    ]
    
    for key in listado_clinico:
        data[f"{key}_map"] = MAPPINGS["si_no"].get(data.get(key), "No")

    # Escalas con descripción
    # Barthel
    try:
        b = int(float(data.get('barthel') or 0)) 
    except (ValueError, TypeError):
        b = 0
    dep = 'Total' if b<20 else 'Grave' if b<60 else 'Leve/Indep'
    data["barthel_map"] = f"{b}"
    
    # Movilidad
    try:
        m = int(float(data.get('movilidad') or 0))
    except (ValueError, TypeError):
        m = 0
    data["movilidad_map"] = f"{m} "

    # Braden
    try:
        br = int(float(data.get('braden') or 0))
    except: br = 0
    data["braden_map"] = str(br)

    # Riesgo Caida
    try:
        rc = int(float(data.get('riesgo_caida') or 0))
    except: rc = 0
    data["riesgo_caida_map"] = str(rc)

    # Códigos CIE (gdiagalt)
    codigos_activos = []
    prefix = "gdiagalt_"
    for key, value in data.items():
        if key.startswith(prefix) and (value == 1 or value == "1"):
            codigos_activos.append(key.replace(prefix, ""))
    data["gdiagalt_map"] = ", ".join(codigos_activos) if codigos_activos else "Sin códigos"

    # -------------------------------------------------------------------------
    # SITUACIÓN AL ALTA (gsitalta) -> Mejora / Empeora
    # -------------------------------------------------------------------------
    try:
        val_gsi = int(float(data.get("gsitalta") or 0))
    except: 
        val_gsi = 0
        
    if val_gsi in [1, 2]:
        data["gsitalta_map"] = "Mejora"
    elif val_gsi in [3, 4, 5]:
        data["gsitalta_map"] = "Empeora"
    else:
        data["gsitalta_map"] = "Desconocido"

    # -------------------------------------------------------------------------
    # FORMATEO DE CONSTANTES VITALES
    # -------------------------------------------------------------------------
    
    # 1. Enteros (Tensión, Saturación) - Quitar decimales
    vars_enteras = ["ntensmin", "ntensmax", "nsatuoxi"]
    
    for v in vars_enteras:
        valor_raw = data.get(v)
        try:
            if valor_raw is not None:
                data[f"{v}_map"] = str(int(float(valor_raw)))
            else:
                data[f"{v}_map"] = "N/A"
        except (ValueError, TypeError):
            data[f"{v}_map"] = str(valor_raw) if valor_raw else "N/A"

    # 2. Decimales (Temperatura) - Forzar 1 decimal
    try:
        temp = data.get("ntempera")
        if temp is not None:
            data["ntempera_map"] = f"{float(temp):.1f}" # Fuerza "36.5"
        else:
            data["ntempera_map"] = "N/A"
    except:
        data["ntempera_map"] = str(data.get("ntempera", "N/A"))

    return data