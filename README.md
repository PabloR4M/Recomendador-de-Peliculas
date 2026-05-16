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

1. **Clonar o crear la estructura de carpetas** Asegúrate de tener todos los archivos organizados dentro de un mismo directorio raíz en tu computadora.

2. **Instalar las dependencias del sistema** Abre tu terminal o consola de comandos, navega hasta la carpeta del proyecto e instala las librerías necesarias ejecutando:
   ```bash
   pip install streamlit requests python-dotenv