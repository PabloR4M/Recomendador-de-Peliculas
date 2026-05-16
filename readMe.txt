# 🎬 Recomendador de Pelis - Sistema Multiagente

Este proyecto es una aplicación avanzada de recomendación cinematográfica desarrollada como Proyecto Integrador de Aprendizaje (PIA) para la materia **Temas Selectos de Sistemas Inteligentes** de la **Facultad de Ingeniería Mecánica y Eléctrica (FIME - UANL)**.

La aplicación va más allá de los sistemas de recomendación tradicionales basados en filtros fijos, implementando un **Sistema Multiagente Complejo** que combina percepción profunda del entorno, motores de inferencia lógica formal (Forward Chaining) y razonamiento probabilístico bayesiano para gestionar la incertidumbre de los gustos humanos.

---

## 🚀 Propósito del Proyecto

El propósito de este sistema es actuar como un asesor cinematográfico inteligente capaz de modelar el perfil cognitivo de un usuario en dos niveles:
1. **Memoria a Largo Plazo:** Almacena el historial permanente de preferencias básicas (géneros favoritos) e interacciones pasadas (películas con "Me gusta" o "No me gusta").
2. **Memoria a Corto Plazo / Contextual:** Evalúa el estado afectivo inmediato del usuario (ánimo actual), la disponibilidad de tiempo de la sesión y las intenciones específicas del día.

Con esta información, una red de agentes independientes colabora bajo una arquitectura de orquestación para interrogar el entorno dinámico de la base de datos global de **The Movie Database (TMDB)**, depurar el espacio de soluciones mediante lógica estricta y calcular la probabilidad a posteriori para entregar un Top 3 altamente personalizado con su respectivo porcentaje de coincidencia exacta.

---

## 💻 Instrucciones de Instalación y Ejecución
Sigue estos pasos detallados para configurar y correr el sistema inteligente en tu entorno local:

1. **Clonar o crear la estructura de carpetas**
Asegúrate de tener todos los archivos organizados dentro de un mismo directorio raíz en tu computadora.

2. **Instalar las dependencias del sistema**
Abre tu terminal o consola de comandos, navega hasta la carpeta del proyecto e instala las librerías necesarias ejecutando:

```text
pip install streamlit requests python-dotenv


3. **Configurar las credenciales del entorno**
En la raíz de la carpeta del proyecto, crea un archivo llamado exactamente .env y añade tu clave de acceso privada de The Movie Database (TMDB):

```text
TMDB_API_KEY=clave

4. **Ejecutar la aplicación**
Para iniciar el orquestador gráfico y lanzar el servidor local de la interfaz, ejecuta el siguiente comando infalible en tu terminal:

```text
python -m streamlit run main.py


Una vez ejecutado, el sistema abrirá de forma automática una pestaña en tu navegador web predeterminado (normalmente en la dirección http://localhost:8501) mostrando la pantalla de bienvenida lista para operar.

---

## 🛠️ Justificación Académica (Temas Vistos en Clase)

El backend de la aplicación está diseñado de forma modular para reflejar y justificar las competencias desarrolladas durante el semestre:

* **Sistemas Multiagente (Actividad 4.2 y 4.3):** El control no está centralizado en la interfaz. El sistema delega tareas a agentes autónomos especializados que interactúan entre sí compartiendo una ontología estandarizada (mapeo semántico de géneros).
* **Arquitectura de Orquestación (Actividad 4.3):** Implementada en el Agente Orquestador, encargado de coordinar de manera lineal y eficiente el flujo de datos desde los sensores hasta el motor probabilístico.
* **Razonamiento Lógico Formal / Forward Chaining (Actividad 3.1):** El Agente Lógico opera como un motor de inferencia clásica de producción (*IF condición THEN acción*), transformando metadatos duros en proposiciones lógicas de una *Working Memory* para descartar opciones no viables.
* **Manejo de Incertidumbre y Teorema de Bayes (Actividad 3.2):** El Agente Bayesiano modela las preferencias difusas calculando la probabilidad *A Priori* (perfil histórico) y la *Verosimilitud* (ánimo contextual) para resolver la probabilidad *A Posteriori* utilizando una función de activación sigmoide.
* **Razonamiento No Monótono (Actividad 3.1):** El sistema adapta sus creencias en tiempo real. Cuando el usuario califica una recomendación en el panel principal, el orquestador retracta inmediatamente esa película del espacio de búsqueda e infiere una nueva solución sin reiniciar el pipeline completo.
* **Asunción de Mundo Abierto / Open World Assumption (Actividad 3.1):** Gestión avanzada de fallas del entorno; si faltan metadatos en la API (hechos ausentes), el sistema aplica reglas heurísticas permisivas por defecto en lugar de asumir falsedades lógicas.

---

## 📂 Estructura del Proyecto

El diseño de archivos sigue un patrón altamente escalable separando por completo la capa de presentación visual (vistas) de los cerebros algorítmicos (agentes):

Salida de código
File written successfully.

```text
PIA_SistemasInteligentes/
│
├── .streamlit/
│   └── config.toml         # Personalización estética de la interfaz (Tema Morado)
│
├── datos/
│   └── usuarios.json       # Base de conocimientos permanente (Memoria a largo plazo)
│
├── agentes/                # Capa del Sistema Multiagente
│   ├── __init__.py         
│   ├── agente_api.py       # Agente Sensor (Extracción paralela y ontología de TMDB)
│   ├── agente_perfilador.py# Agente de Memoria (Estructura y persistencia de perfiles)
│   ├── agente_logico.py    # Agente de Inferencia (Forward Chaining y Working Memory)
│   ├── agente_bayes.py     # Agente Probabilístico (Teorema de Bayes y Naive Bayes)
│   └── agente_orquestador.py# Agente de Control (Gestión de pipeline y remuestreo)
│
├── vistas/                 # Capa de Presentación (Frontend)
│   ├── __init__.py         
│   ├── login.py            # Pantalla de enrutamiento e inicio de sesión
│   ├── onboarding.py       # Pantalla de creación interactiva de perfiles (Pills y Carrucel)
│   └── panel.py            # Pantalla principal (Filtros condicionales y feedback en vivo)
│
├── main.py                 # Enrutador e inicializador general de Streamlit
├── .env                    # Variables de entorno seguras (Credenciales de API)
└── requirements.txt        # Índice de dependencias del proyecto