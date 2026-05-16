import requests
import os
from dotenv import load_dotenv

# carga api del env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Diccionario / Ontología para traducir texto a IDs de TMDB
MAPEO_GENEROS = {
    "Acción": 28, "Aventura": 12, "Animación": 16, "Comedia": 35, 
    "Crimen": 80, "Documental": 99, "Drama": 18, "Familia": 10751, 
    "Fantasía": 14, "Historia": 36, "Terror": 27, "Música": 10402, 
    "Misterio": 9648, "Romance": 10749, "Ciencia ficción": 878, 
    "Película de TV": 10770, "Suspense": 53, "Bélica": 10752, "Western": 37
}


def obtener_peliculas_avanzado(ids_generos_str, anio_inicio, anio_fin, pagina=1):
    """Se comunica de forma segura con el entorno usando diccionarios de parametros"""
    url = "https://api.themoviedb.org/3/discover/movie"
    
    parametros = {
        "api_key": TMDB_API_KEY,
        "language": "es-MX",
        "page": pagina,
        "sort_by": "popularity.desc" # Garantiza calidad en los resultados
    }
    
    if ids_generos_str:
        parametros["with_genres"] = ids_generos_str
    if anio_inicio:
        parametros["primary_release_date.gte"] = f"{anio_inicio}-01-01"
    if anio_fin:
        parametros["primary_release_date.lte"] = f"{anio_fin}-12-31"
        
    try:
        respuesta = requests.get(url, params=parametros)
        if respuesta.status_code == 200:
            return respuesta.json().get('results', [])
    except Exception as e:
        print(f"Error en la API: {e}")
    return []

def obtener_detalles_pelicula(id_peli):
    url = f"https://api.themoviedb.org/3/movie/{id_peli}?api_key={TMDB_API_KEY}&language=es-MX"
    try:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            return respuesta.json()
    except Exception:
        pass
    return {}


# === Jalar Peliculas por Genero PERFILADOR ===
def obtener_peliculas_por_genero(ids_generos_str, pagina=1):
    """
    Busca películas que coincidan con una lista de IDs de géneros.
    Usa el parámetro 'pagina' para traer más resultados si se acaban.
    """
    # Nota que agregamos &page={pagina} al final de la URL
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=es-MX&with_genres={ids_generos_str}&sort_by=popularity.desc&page={pagina}"
    
    try:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            return respuesta.json()['results']
    except Exception as e:
        print(f"Error al buscar por género: {e}")
    return []



# === Pruebas de la API ===
if __name__ == "__main__":
    print("Iniciando Agente API... Buscando películas en el entorno...")
    peliculas = obtener_peliculas_avanzado()
    
    if peliculas:
        print("\nTodo bien, 5 peliculas de prueba::\n")
        for peli in peliculas[:5]: # Solo muestra 5
            titulo = peli.get('title', 'Sin título')
            fecha = peli.get('release_date', 'Sin fecha')
            print(f"- {titulo} ({fecha})")
    else:
        print("\nNo se obtuvieron pelis")