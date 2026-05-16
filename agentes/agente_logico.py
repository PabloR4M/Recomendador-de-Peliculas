# ==== Seccion logica formal ====
def extraer_hechos(peli_detalles):
    runtime = peli_detalles.get("runtime", 0)
    return {
        "es_corta": 0 < runtime <= 120,
        "es_larga": runtime > 120,
        "tiene_duracion": runtime > 0
    }

def motor_de_inferencia(hechos, premisa_tiempo):
    if premisa_tiempo == "Menos de 2 horas":
        return hechos["es_corta"]
    elif premisa_tiempo == "Más de 2 horas":
        return hechos["es_larga"]
    return True

def filtrar_por_tiempo(peliculas_con_detalles, premisa_tiempo):
    pelis_validadas = []
    for peli in peliculas_con_detalles:
        hechos = extraer_hechos(peli)
        if motor_de_inferencia(hechos, premisa_tiempo):
            pelis_validadas.append(peli)
    return pelis_validadas