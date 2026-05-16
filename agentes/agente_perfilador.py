import json
import os

RUTA_DATOS = "datos/usuarios.json"

# comprobamos los usuarios ya registrados en el sistema
def cargar_usuarios():
    """Lee la memoria a largo plazo (el JSON)."""
    if not os.path.exists(RUTA_DATOS):
        with open(RUTA_DATOS, 'w') as f:
            json.dump({}, f)
    with open(RUTA_DATOS, 'r') as f:
        return json.load(f)


# si el usuario no esta en los datos se crea uno nuevo
def guardar_usuarios(datos):
    """Escribe nueva información en la memoria."""
    with open(RUTA_DATOS, 'w') as f:
        json.dump(datos, f, indent=4)


# si el usuario ya esta en los datos solo se recupera la informacion
def obtener_perfil(nombre):
    """Busca si el usuario ya existe en el sistema."""
    usuarios = cargar_usuarios()
    return usuarios.get(nombre, None)


# para usuarios nuevos crea un json base para perfilar sus gustos
# esto par despues dar recomendaciones mas acertadas al usuario
def crear_perfil(nombre, generos_favoritos, likes, dislikes):
    """Crea un perfil nuevo estructurado con las películas valoradas."""
    usuarios = cargar_usuarios()
    usuarios[nombre] = {
        "generos_favoritos": generos_favoritos,
        "peliculas_likeadas": likes,
        "peliculas_dislikeadas": dislikes
    }
    guardar_usuarios(usuarios)
    return True