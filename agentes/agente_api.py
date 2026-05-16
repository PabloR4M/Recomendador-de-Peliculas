import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# ==== Seccion percepcion del entorno (Actividad 4.2) ====
# se extrae la informacion de la base de datos


# variables de entorno
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


# en la bd que use, cada genero tiene un codigo, aqui los defino para que el codigo se lea mejor
MAPEO_GENEROS = {
    "Acción": 28, "Aventura": 12, "Animación": 16, "Comedia": 35,
    "Crimen": 80, "Documental": 99, "Drama": 18, "Familia": 10751,
    "Fantasía": 14, "Historia": 36, "Terror": 27, "Música": 10402,
    "Misterio": 9648, "Romance": 10749, "Ciencia ficción": 878,
    "Película de TV": 10770, "Suspense": 53, "Bélica": 10752, "Western": 37
}

# se hace al reves por si se necesita despues
GENEROS_POR_ID = {v: k for k, v in MAPEO_GENEROS.items()}

# maximo de hilos
_MAX_WORKERS = 5

# filtros minimos para las peliculas y el ruido
_MIN_VOTE_COUNT = 80
_MIN_VOTE_AVERAGE = 5.5

def obtener_peliculas_avanzado(ids_generos_str, anio_inicio, anio_fin, pagina=1):
    url = "https://api.themoviedb.org/3/discover/movie"


    # parametros para las querys
    parametros_base = {
        "api_key": TMDB_API_KEY,
        "language": "es-MX",
        "page": pagina,
        "vote_count.gte": _MIN_VOTE_COUNT,
        "vote_average.gte": _MIN_VOTE_AVERAGE  # minimo confiable para la recomendacion
    }

    if ids_generos_str:
        parametros_base["with_genres"] = ids_generos_str
    if anio_inicio:
        parametros_base["primary_release_date.gte"] = f"{anio_inicio}-01-01"
    if anio_fin:
        parametros_base["primary_release_date.lte"] = f"{anio_fin}-12-31"

    # se configuran dos busquedas distintas para tener mas opciones
    params_popularidad = {**parametros_base, "sort_by": "popularity.desc"}
    params_valoracion  = {**parametros_base, "sort_by": "vote_average.desc", "page": max(1, pagina - 1)}

    resultados_fusionados = []
    ids_vistos = set()

    def _fetch(params):
        try:
            r = requests.get(url, params=params, timeout=8)
            if r.status_code == 200:
                return r.json().get("results", [])
        except requests.exceptions.RequestException as e:
            print(f"Error de red al consultar TMDB {e}")
        return []

     # Ejecucion paralela de ambas estrategias para reducir latencia
    with ThreadPoolExecutor(max_workers=2) as executor:
        futuros = [
            executor.submit(_fetch, params_popularidad),
            executor.submit(_fetch, params_valoracion),
        ]
        for futuro in as_completed(futuros):
            for peli in futuro.result():
                pid = peli.get("id")

                # si una peli se repite en las busquedas dejamos solo una para evitar repeticiones
                if pid and pid not in ids_vistos:
                    ids_vistos.add(pid)
                    resultados_fusionados.append(peli)

    return resultados_fusionados

def obtener_detalles_pelicula(id_peli):
    # query de informacion mas especifica de cada pelicula
    url = (
        f"https://api.themoviedb.org/3/movie/{id_peli}"
        f"?api_key={TMDB_API_KEY}&language=es-MX"
        f"&append_to_response=keywords"
    )
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener detalles {e}")
    return {}

def obtener_detalles_en_lote(ids_peliculas):
    # se hacen colsultas paralelas de los detalles de cada pelicula
    detalles = []

    def _fetch_detalles(pid):
        return obtener_detalles_pelicula(pid)

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futuros = {executor.submit(_fetch_detalles, pid): pid for pid in ids_peliculas}
        for futuro in as_completed(futuros):
            resultado = futuro.result()
            if resultado and resultado.get("id"):
                detalles.append(resultado)

    return detalles

def obtener_peliculas_por_genero(ids_generos_str, pagina=1):
    # se buscan peliculas solo por genero para cuando el usuario es nuevo
    return obtener_peliculas_avanzado(ids_generos_str, None, None, pagina)



# === Prueba de funcionamiento rapida ===
if __name__ == "__main__":
    print("Iniciando Agente API")
    peliculas = obtener_peliculas_avanzado("28,12", None, None, 1)
    if peliculas:
        print(f"Muestra de peliculas percibidas")
        for peli in peliculas[:5]:
            print(f" {peli.get('title')}")
    else:
        print("Error no se obtuvieron senales del entorno")