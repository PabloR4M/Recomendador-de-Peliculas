# ==== Seccion probabilistica y bayesiana (Actividad 3.2) ====

# implementa el calculo del teorema de bayes para estimar la probabilidad posterior
# de que una pelicula sea relevante para el usuario dado su perfil historico y su estado de animo actual

# P(Relevante | Evidencia) es proporcional a P(Evidencia | Relevante) x P(Relevante)
# donde P(Relevante) es la probabilidad a priori segun el perfil historico del usuario

# P(Evidencia | Relevante) es la verosimilitud cruzando generos vs animo y seleccion actual

# P(Relevante | Evidencia) es la probabilidad posterior o score de match final

# la normalizacion del score se realiza mediante una funcion sigmoide escalada

from __future__ import annotations
import math
from agentes import agente_api

# mapa de animo a generos compatibles actuando como likelihood table
# cada estado afectivo activa un prior sobre los generos
MAPA_ANIMO: dict[str, list[str]] = {
    "Feliz / Relajado":           ["Comedia", "Aventura", "Familia", "Animación", "Romance"],
    "Estresado / Cansado":        ["Comedia", "Romance", "Fantasía", "Acción", "Animación"],
    "Triste / Melancólico":       ["Drama", "Romance", "Música", "Historia"],
    "Quiero pensar / Intelectual":["Ciencia ficción", "Misterio", "Documental", "Suspense", "Historia"],
}

# pesos de evidencia evaluando cuanto contribuye cada tipo de coincidencia
_W_PERFIL_EXACTO  = 2.2   # coincidencia directa con generos favoritos historicos
_W_ANIMO_EXACTO   = 1.8   # coincidencia con generos del animo declarado
_W_HOY_EXACTO     = 2.0   # coincidencia con generos elegidos para esta sesion
_W_RATING_BONUS   = 0.6   # contribucion del rating normalizado de TMDB
_W_POPULARIDAD    = 0.3   # contribucion debil de popularidad para evitar dominancia

# prior base en log odds equivale a un 40 por ciento de probabilidad neutral
_LOG_ODDS_BASE = math.log(0.40 / 0.60)


def _sigmoide(x: float) -> float:
    # funcion de activacion sigmoide que mapea log odds a probabilidad
    # propiedad clave es estrictamente monotona garantizando que mayor evidencia produce mayor score
    return 1.0 / (1.0 + math.exp(-x))


def _calcular_log_odds_previo(
    nombres_generos_peli: list[str],
    generos_favoritos: list[str],
) -> float:
    # calcula la log odds a priori basada en el perfil historico
    # el perfil representa la memoria a largo plazo del usuario
    # se usa log odds en lugar de probabilidad directa para permitir combinacion aditiva 
    # es el equivalente al clasificador naive bayes en el espacio log lineal
    if not generos_favoritos:
        return _LOG_ODDS_BASE

    # ratio de cobertura para fraccion de generos de la pelicula que pertenecen al perfil
    coincidencias = sum(1 for g in nombres_generos_peli if g in generos_favoritos)
    total_generos = max(1, len(nombres_generos_peli))
    ratio_cobertura = coincidencias / total_generos

    return _LOG_ODDS_BASE + (_W_PERFIL_EXACTO * ratio_cobertura)


def _calcular_log_verosimilitud(
    nombres_generos_peli: list[str],
    generos_hoy: list[str],
    generos_animo: list[str],
    rating: float,
    popularidad: float,
) -> float:
    # calcula la log verosimilitud evidenciando que tan probable es observar esto dado que es relevante
    # bajo la hipotesis naive bayes la log verosimilitud conjunta es la suma de las individuales
    log_vero = 0.0
    total_generos = max(1, len(nombres_generos_peli))

    # evidencia 1 generos seleccionados manualmente en la sesion como senal intencional fuerte
    coinc_hoy = sum(1 for g in nombres_generos_peli if g in generos_hoy)
    if coinc_hoy > 0:
        log_vero += _W_HOY_EXACTO * (coinc_hoy / total_generos)

    # evidencia 2 generos compatibles con el estado afectivo declarado
    coinc_animo = sum(1 for g in nombres_generos_peli if g in generos_animo)
    if coinc_animo > 0:
        log_vero += _W_ANIMO_EXACTO * (coinc_animo / total_generos)

    # evidencia 3 contribucion del rating normalizado desde base 5 hasta 10
    if rating and rating > 5.0:
        rating_norm = min(1.0, (rating - 5.0) / 5.0)
        log_vero += _W_RATING_BONUS * rating_norm

    # evidencia 4 popularidad en escala logaritmica para suavizar efecto de outliers virales
    if popularidad and popularidad > 0:
        pop_norm = min(1.0, math.log1p(popularidad) / math.log1p(5000))
        log_vero += _W_POPULARIDAD * pop_norm

    return log_vero


def _extraer_nombres_generos(peli: dict) -> list[str]:
    # extrae nombres de generos desde el objeto soportando estructura detallada o resumida
    # utiliza el mapa invertido como fallback para la forma resumida
    raw = peli.get("genres") or peli.get("genre_ids") or []
    if not raw:
        return []
    if isinstance(raw[0], dict):
        return [g.get("name", "") for g in raw if g.get("name")]
    return [agente_api.GENEROS_POR_ID.get(gid, "") for gid in raw if gid in agente_api.GENEROS_POR_ID]


def calcular_probabilidad_bayesiana(
    peliculas: list[dict],
    perfil: dict,
    generos_hoy: list[str],
    animo: str,
) -> list[dict]:
    # interfaz principal del agente bayesiano consumida por el orquestador
    # aplica teorema de bayes en espacio log odds para cada pelicula candidata
    # scores altos requieren evidencias multiples para evitar inflacion y mantener monotonia estricta
    generos_favoritos: list[str] = perfil.get("generos_favoritos", [])
    generos_animo: list[str] = MAPA_ANIMO.get(animo, [])

    resultados: list[dict] = []

    for peli in peliculas:
        # extraccion de caracteristicas observables de la pelicula
        nombres_generos = _extraer_nombres_generos(peli)
        rating          = float(peli.get("vote_average") or 0.0)
        popularidad     = float(peli.get("popularity")   or 0.0)

        # calculo de la log odds a priori reflejando la memoria a largo plazo
        log_prior = _calcular_log_odds_previo(nombres_generos, generos_favoritos)

        # calculo de la log verosimilitud capturando la senal contextual
        log_likelihood = _calcular_log_verosimilitud(
            nombres_generos, generos_hoy, generos_animo, rating, popularidad
        )

        # combinacion aditiva en espacio log odds utilizando regla de bayes
        log_posterior = log_prior + log_likelihood

        # proyeccion a probabilidad mediante funcion sigmoide
        probabilidad_posterior = _sigmoide(log_posterior)

        # escalado a porcentaje con precision decimal
        match_score = round(probabilidad_posterior * 100, 1)

        peli["match_score"] = match_score
        
        # metadatos de diagnostico para trazabilidad y defensa academica
        peli["_bayes_debug"] = {
            "log_prior":      round(log_prior, 4),
            "log_likelihood": round(log_likelihood, 4),
            "log_posterior":  round(log_posterior, 4),
            "generos_match":  [
                g for g in nombres_generos
                if g in set(generos_favoritos + generos_animo + generos_hoy)
            ],
        }
        resultados.append(peli)

    # ordenar descendentemente por probabilidad posterior mediante decision maximum a posteriori
    resultados.sort(key=lambda x: x["match_score"], reverse=True)
    return resultados