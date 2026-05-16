from agentes import agente_api
import random

# ==== Seccion probabilistica y bayesiana (Actividad 3.2) ====
def calcular_probabilidad_bayesiana(peliculas, perfil, generos_hoy, animo):
    resultados = []
    mapa_animo = {
        "Feliz / Relajado": ["Comedia", "Aventura", "Familia", "Animación"],
        "Estresado / Cansado": ["Comedia", "Romance", "Fantasía", "Acción"],
        "Triste / Melancólico": ["Drama", "Romance", "Música"],
        "Quiero pensar / Intelectual": ["Ciencia ficción", "Misterio", "Documental", "Suspense"]
    }
    generos_animo = mapa_animo.get(animo, [])
    generos_favoritos = perfil.get("generos_favoritos", [])
    
    for peli in peliculas:
        ids_peli = peli.get("genres", []) # Como extraemos detalles, la estructura cambia levemente
        nombres_generos_peli = [g["name"] for g in ids_peli] if ids_peli else []
        
        # 1. Probabilidad A Priori (Basado en memoria a largo plazo)
        p_priori = 0.50 
        coincidencias_perfil = sum(1 for g in nombres_generos_peli if g in generos_favoritos)
        if coincidencias_perfil > 0:
            p_priori = 0.85 # Alta probabilidad base si pertenece a sus favoritos
            
        # 2. Verosimilitud (Basado en el animo de hoy y seleccion manual)
        p_verosimilitud = 0.40
        coincidencias_animo = sum(1 for g in nombres_generos_peli if g in generos_animo)
        coincidencias_hoy = sum(1 for g in nombres_generos_peli if g in generos_hoy)
        
        if coincidencias_hoy > 0 or coincidencias_animo > 0:
            p_verosimilitud = 0.95
            
        # 3. Calculo Posterior
        probabilidad = (p_priori * p_verosimilitud) * 100
        
        # Ligera variacion aleatoria para desempatar peliculas con el mismo score
        probabilidad += random.uniform(1.0, 5.0) 
        
        match_score = min(99.8, round(probabilidad, 1))
        peli["match_score"] = match_score
        resultados.append(peli)
        
    resultados.sort(key=lambda x: x["match_score"], reverse=True)
    return resultados