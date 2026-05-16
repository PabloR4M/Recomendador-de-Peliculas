import streamlit as st
from agentes import agente_perfilador

def mostrar():
    # ==== Seccion login ======
    col_form, col_img = st.columns([1, 1.5], gap="large")
    with col_form:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown("Temas Selectos de Sistemas Inteligentes")
        st.title("Recomendador de Pelis")
        st.markdown("Por favor ingresa tu nombre de usuario para continuar o registrarte")
        nombre = st.text_input("Username", key="input_nombre")
        
        if st.button("Ingresar", type="primary", use_container_width=True):
            if nombre:
                # ==== Se carga el perfil ======
                perfil = agente_perfilador.obtener_perfil(nombre)
                if perfil:
                    st.session_state.usuario_temp = nombre
                    st.session_state.fase = "uso_diario"
                    st.rerun()
                else:
                    st.session_state.usuario_temp = nombre
                    st.session_state.fase = "onboarding_1"
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_img:
        st.markdown('<div class="hero-image-right"></div>', unsafe_allow_html=True)