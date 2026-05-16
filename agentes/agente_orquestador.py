# ==== Seccion sistemas multiagente (Actividad 4.3) ====

# coordina el flujo de control entre los agentes

from __future__ import annotations
from agentes import agente_api, agente_logico, agente_bayes, agente_perfilador

# numero minimo de candidatas que deben pasar el filtro antes del remuestreo
_MIN_CANDIDATAS_LOGICAS = 4

# candidatas a solicitar a la API en cada lote antes del filtrado
_LOTE_API = 20

# maximo de paginas adicionales a consultar durante el remuestreo
_MAX_PAGINAS_EXTRA = 3


def _construir_ids_generos(generos_hoy: list[str], perfil: dict) -> tuple[str, str]:

    # construye los strings de ids de generos para el entorno segun la sesion actual
    # usa operador AND cuando se busca que las pelis tengan varios generos especificos
    # usa operador OR para generos del perfil donde no se busca un filtro estrictop
    ids_sesion = ",".join(
        str(agente_api.MAPEO_GENEROS[g])
        for g in generos_hoy
        if g in agente_api.MAPEO_GENEROS
    )
    ids_perfil = "|".join(
        str(agente_api.MAPEO_GENEROS[g])
        for g in perfil.get("generos_favoritos", [])
        if g in agente_api.MAPEO_GENEROS
    )
    return ids_sesion, ids_perfil


def _filtrar_vistas(peliculas: list[dict], vistas: set[int]) -> list[dict]:
    # aplica razonamiento no monotono retractando del espacio de busqueda las peliculas ya vistas
    # una conclusion previa se revisa cuando llega nueva evidencia de interaccion del usuario
    # digamos que recomienda una pelicula que el usuario ya vio, bueno lo guarda en el registro 
    # y regenera la recomendacion
    return [p for p in peliculas if p.get("id") not in vistas]


def ejecutar_pipeline_recomendacion(
    nombre_usuario: str,
    generos_hoy: list[str],
    anio_inicio: int | None,
    anio_fin: int | None,
    animo: str,
    tiempo: str,
    pagina: int,
) -> list[dict]:
    
    # recomendacion que orquesta los cuatro agentes especializados
    
    # se recupera la memoria a largo plazo del usuario
    perfil = agente_perfilador.obtener_perfil(nombre_usuario)
    if not perfil:
        return []

    # se construye el espacio de busqueda inicial consultando al agente logico
    ids_sesion, ids_perfil = _construir_ids_generos(generos_hoy, perfil)
    ids_buscar = ids_sesion if ids_sesion else ids_perfil

    pelis_entorno = agente_api.obtener_peliculas_avanzado(ids_buscar, anio_inicio, anio_fin, pagina)

    # se aplica razonamiento no monotono retractando las peliculas ya vistas
    vistas: set[int] = set(
        perfil.get("peliculas_likeadas", []) + perfil.get("peliculas_dislikeadas", [])
    )
    pelis_no_vistas = _filtrar_vistas(pelis_entorno, vistas)

    # se aplica remuestreo si el retractor agoto la muestra inicial
    pagina_extra = pagina + 1
    intentos_extra = 0
    while len(pelis_no_vistas) < _MIN_CANDIDATAS_LOGICAS and intentos_extra < _MAX_PAGINAS_EXTRA:
        pelis_extra = agente_api.obtener_peliculas_avanzado(ids_buscar, anio_inicio, anio_fin, pagina_extra)
        pelis_no_vistas.extend(_filtrar_vistas(pelis_extra, vistas))
        
        # se eliminan duplicados tras la extension del muestreo
        seen_ids: set[int] = set()
        pelis_no_vistas = [
            p for p in pelis_no_vistas
            if not (p.get("id") in seen_ids or seen_ids.add(p.get("id")))  # type: ignore[func-returns-value]
        ]
        pagina_extra += 1
        intentos_extra += 1

    # el agente sensor realiza fetching concurrente para obtener hechos concretos en lote
    ids_candidatas = [p["id"] for p in pelis_no_vistas[:_LOTE_API] if p.get("id")]
    pelis_detalladas = agente_api.obtener_detalles_en_lote(ids_candidatas)

    if not pelis_detalladas:
        return []

    # el motor de inferencia evalua la premisa usando encadenamiento hacia adelante
    pelis_filtradas = agente_logico.filtrar_por_tiempo(pelis_detalladas, tiempo)

    if not pelis_filtradas:
        # si ninguna supera el filtro estricto se relaja usando todo el lote para evitar un retorno vacio
        pelis_filtradas = pelis_detalladas


    # el agente bayesiano evalua las opciones restantes calculando la probabilidad posterior
    pelis_puntuadas = agente_bayes.calcular_probabilidad_bayesiana(
        pelis_filtradas, perfil, generos_hoy, animo
    )

    # se retorna el top con mayor probabilidad posterior al usuario
    return pelis_puntuadas[:3]