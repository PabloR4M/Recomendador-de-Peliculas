# ==== Seccion logica formal (Actividad 3.1) ====

# implementa un motor de inferencia basico usando encadenamiento hacia adelante
# evalua reglas de produccion sobre una base de hechos derivada de los metadatos

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

# definimos los rangos de tiempo que se pueden seleccionar en la pantalla
_RANGOS_TIEMPO: dict[str, tuple[int, int]] = {
    "Menos de 2 horas":     (1,   119),
    "Exactamente 2 horas":  (100, 130),   # mas menos 15 min de tolerancia
    "Más de 2 horas":       (120, 9999),
    "Sin importar duración":(1,   9999),
}

# umbral minimo de votos para que el rating de la peli sea un hecho confiable
_MIN_VOTOS_CONFIABLES = 50

# runtime estimado cuando TMDB no reporta el dato
_RUNTIME_ESTIMADO_DEFAULT = 100


@dataclass
class WorkingMemory:
    # memoria de trabajo del motor de inferencia con proposiciones verdaderas o falsas
    # hechos de duracion
    runtime: int = 0
    tiene_runtime_real: bool = False     # distingue 0 real de dato ausente
    runtime_efectivo: int = 0            # runtime usado ya sea real o estimado

    # hechos de calidad y credibilidad
    votos_suficientes: bool = False
    rating_confiable: float = 0.0

    # hechos derivados de duracion
    es_cortometraje: bool = False        # menor a 40 min
    es_pelicula_corta: bool = False      # entre 40 y 119 min
    es_pelicula_estandar: bool = False   # entre 100 y 130 min
    es_pelicula_larga: bool = False      # mayor a 120 min

    # adicionales 
    generos_ids: list[int] = field(default_factory=list)
    idioma_original: str = ""

    # estado 
    decision: str = "PENDIENTE"         # puede ser ACEPTAR RECHAZAR o PENDIENTE
    razones_rechazo: list[str] = field(default_factory=list)


def _extraer_hechos(peli_detalles: dict[str, Any]) -> WorkingMemory:

    # si el dato esta ausente se infiere un valor por defecto 
    wm = WorkingMemory()

    # duracion
    runtime_raw = peli_detalles.get("runtime")
    if runtime_raw and isinstance(runtime_raw, int) and runtime_raw > 0:
        wm.runtime = runtime_raw
        wm.tiene_runtime_real = True
        wm.runtime_efectivo = runtime_raw
    else:
        # runtime estimado para evitar falsos negativos si falta el dato
        wm.runtime = 0
        wm.tiene_runtime_real = False
        wm.runtime_efectivo = _RUNTIME_ESTIMADO_DEFAULT

    # inferencia de categorias de duracion usando reglas de produccion
    r = wm.runtime_efectivo
    wm.es_cortometraje    = r < 40
    wm.es_pelicula_corta  = 40 <= r < 120
    wm.es_pelicula_estandar = 100 <= r <= 130
    wm.es_pelicula_larga  = r >= 120

    # calidad
    votos = peli_detalles.get("vote_count", 0) or 0
    rating = peli_detalles.get("vote_average", 0.0) or 0.0
    wm.votos_suficientes = votos >= _MIN_VOTOS_CONFIABLES
    wm.rating_confiable  = float(rating) if wm.votos_suficientes else 0.0

    # datos
    wm.generos_ids    = [g["id"] for g in (peli_detalles.get("genres") or [])]
    wm.idioma_original = peli_detalles.get("original_language", "")

    return wm


def _aplicar_reglas_tiempo(wm: WorkingMemory, premisa_tiempo: str) -> WorkingMemory:
    # Aplicacion de reglas usando encadenamiento hacia adelante
    # el motor evalua las reglas y la primera que se dispara determina la decision
    
    # regla nula toda pelicula es aceptada si no importa el tiempo
    if premisa_tiempo not in _RANGOS_TIEMPO or premisa_tiempo == "Sin importar duración":
        wm.decision = "ACEPTAR"
        return wm

    # si el dato esta ausente se acepta con advertencia para no descartar a ciegas
    if not wm.tiene_runtime_real:
        wm.decision = "ACEPTAR"
        return wm

    # regla de cortometraje 
    if wm.es_cortometraje:
        wm.decision = "RECHAZAR"
        wm.razones_rechazo.append(f"Cortometraje fuera del rango")
        return wm

    # verificar si el runtime cae dentro de lo que pide el usuario
    rango_min, rango_max = _RANGOS_TIEMPO[premisa_tiempo]
    if rango_min <= wm.runtime_efectivo <= rango_max:
        wm.decision = "ACEPTAR"
    else:
        wm.decision = "RECHAZAR"
        wm.razones_rechazo.append("Fuera de rango")

    return wm


def evaluar_pelicula(peli_detalles: dict[str, Any], premisa_tiempo: str) -> WorkingMemory:

    # buca y evalua la peli y retorna la decision
    wm = _extraer_hechos(peli_detalles)
    wm = _aplicar_reglas_tiempo(wm, premisa_tiempo)
    return wm


def filtrar_por_tiempo(peliculas_con_detalles: list[dict], premisa_tiempo: str) -> list[dict]:

    pelis_validadas: list[dict] = []

    for peli in peliculas_con_detalles:
        wm = evaluar_pelicula(peli, premisa_tiempo)

        if wm.decision == "ACEPTAR":
            # se adjuntan hechos derivados a la pelicula para el agente de bayes
            peli["_wm"] = wm
            pelis_validadas.append(peli)

    return pelis_validadas



def extraer_hechos(peli_detalles: dict) -> dict:
    wm = _extraer_hechos(peli_detalles)
    return {
        "es_corta":        wm.es_pelicula_corta,
        "es_larga":        wm.es_pelicula_larga,
        "tiene_duracion":  wm.tiene_runtime_real,
        "runtime_efectivo": wm.runtime_efectivo,
    }


def motor_de_inferencia(hechos: dict, premisa_tiempo: str) -> bool:
    wm = WorkingMemory(
        runtime=hechos.get("runtime_efectivo", 0),
        tiene_runtime_real=hechos.get("tiene_duracion", False),
        runtime_efectivo=hechos.get("runtime_efectivo", _RUNTIME_ESTIMADO_DEFAULT),
    )
    wm = _aplicar_reglas_tiempo(wm, premisa_tiempo)
    return wm.decision == "ACEPTAR"