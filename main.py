import streamlit as st
from vistas import login, onboarding, panel

# ==== Seccion configuracion ======
st.set_page_config(page_title="Recomendador de Pelis", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")

# ==== Seccion estilos ======
st.markdown("""
<style>
    .stApp { background-color: #121420; color: #FFFFFF; }
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; max-width: 100%; }
    .hero-image-right {
        background-image: url('https://www.taste.io/images/hero.jpg');
        background-size: cover; background-position: center; height: 100vh;
        margin: 0rem -5rem 0rem 0rem; border-radius: 30px 0 0 30px;
    }
    .hero-image-left {
        background-image: url('https://www.taste.io/images/hero.jpg');
        background-size: cover; background-position: center; height: 100vh;
        margin: 0rem 0rem 0rem -5rem; border-radius: 0 30px 30px 0;
    }
    .form-container { padding-top: 10vh; padding-right: 2rem; padding-left: 2rem; }
    .peli-card { background-color: #1E2130; padding: 8px; border-radius: 10px; text-align: center; margin-bottom: 10px; }
    .titulo-peli {
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        font-size: 0.85rem; font-weight: 600; margin-top: 5px; margin-bottom: 10px; color: #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# ==== Seccion memoria ======
if "fase" not in st.session_state: st.session_state.fase = "login" 
if "usuario_temp" not in st.session_state: st.session_state.usuario_temp = ""
if "generos_temp" not in st.session_state: st.session_state.generos_temp = []
if "likes_temp" not in st.session_state: st.session_state.likes_temp = []
if "dislikes_temp" not in st.session_state: st.session_state.dislikes_temp = []
if "peliculas_queue" not in st.session_state: st.session_state.peliculas_queue = []
if "api_page" not in st.session_state: st.session_state.api_page = 1 

# ==== Seccion enrutador ======
if st.session_state.fase == "login":
    login.mostrar()
elif st.session_state.fase.startswith("onboarding"):
    onboarding.mostrar()
elif st.session_state.fase == "uso_diario":
    panel.mostrar()