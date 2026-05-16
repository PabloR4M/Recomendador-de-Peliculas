from agentes import agente_api, agente_logico, agente_bayes, agente_perfilador

def ejecutar_pipeline_recomendacion(nombre_usuario, generos_hoy, anio_inicio, anio_fin, animo, tiempo, pagina):
    perfil = agente_perfilador.obtener_perfil(nombre_usuario)
    if not perfil: return []
        
    # Se aplica logica AND u OR dependiendo de la interaccion del usuario
    if generos_hoy:
        ids_buscar = [str(agente_api.MAPEO_GENEROS[g]) for g in generos_hoy if g in agente_api.MAPEO_GENEROS]
        ids_str = ",".join(ids_buscar) 
    else:
        ids_buscar = [str(agente_api.MAPEO_GENEROS[g]) for g in perfil["generos_favoritos"] if g in agente_api.MAPEO_GENEROS]
        ids_str = "|".join(ids_buscar) 
    
    # Se extraen opciones del entorno
    pelis_entorno = agente_api.obtener_peliculas_avanzado(ids_str, anio_inicio, anio_fin, pagina)
    
    # Se filtran las peliculas ya vistas en la memoria historica
    vistas = set(perfil["peliculas_likeadas"] + perfil["peliculas_dislikeadas"])
    pelis_no_vistas = [p for p in pelis_entorno if p.get("id") not in vistas]
    
    # Se forzara otra busqueda si el filtro elimino demasiadas opciones
    if len(pelis_no_vistas) < 5:
        pelis_extra = agente_api.obtener_peliculas_avanzado(ids_str, anio_inicio, anio_fin, pagina + 1)
        pelis_no_vistas.extend([p for p in pelis_extra if p.get("id") not in vistas])
        
    # Se obtienen los hechos concretos para el motor de inferencia
    pelis_detalladas = []
    for p in pelis_no_vistas[:15]: 
        detalles = agente_api.obtener_detalles_pelicula(p['id'])
        if detalles: pelis_detalladas.append(detalles)
        
    # Se aplica inferencia logica estricta
    pelis_filtradas = agente_logico.filtrar_por_tiempo(pelis_detalladas, tiempo)
    
    # Se aplica probabilidad bayesiana para ordenar los resultados
    pelis_puntuadas = agente_bayes.calcular_probabilidad_bayesiana(pelis_filtradas, perfil, generos_hoy, animo)
    
    return pelis_puntuadas[:3]