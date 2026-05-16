import streamlit as st
from agentes import agente_perfilador, agente_api

def procesar_voto(id_peli, tipo_voto):
    # ==== Se guardan los votos ======
    if tipo_voto == "like": st.session_state.likes_temp.append(id_peli)
    elif tipo_voto == "dislike": st.session_state.dislikes_temp.append(id_peli)
    st.session_state.peliculas_queue = [p for p in st.session_state.peliculas_queue if p.get('id') != id_peli]

def mostrar():
    col_img, col_form = st.columns([1, 2], gap="large")
    with col_img: 
        st.markdown('<div class="hero-image-left"></div>', unsafe_allow_html=True)
        
    with col_form:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        # ==== Seccion generos ======
        if st.session_state.fase == "onboarding_1":
            if st.button("⬅️ Volver"):
                st.session_state.fase = "login"
                st.rerun()
                
            st.title("Bienvenido, notamos que eres nuevo")
            st.subheader("Vamos a crear tu perfil")
            st.markdown("Selecciona MINIMO 3 generos que te gusten para afinar nuestros agentes")
            
            lista_generos = list(agente_api.MAPEO_GENEROS.keys())
            st.pills("Tus generos favoritos", lista_generos, selection_mode="multi", key="pills_generos")
            
            st.write("")
            if st.button("Continuar", type="primary", use_container_width=True):
                seleccion = st.session_state.pills_generos
                if seleccion and len(seleccion) >= 3:
                    st.session_state.generos_temp = seleccion
                    st.session_state.fase = "onboarding_2"
                    st.rerun()
                else:
                    llevas = len(seleccion) if seleccion else 0
                    st.error(f"Llevas {llevas} Faltan {3 - llevas} generos mas")
        
        # ==== Seccion valoracion peliculas ======
        elif st.session_state.fase == "onboarding_2":
            if st.button("⬅️ Volver"):
                st.session_state.fase = "onboarding_1"
                st.rerun()
                
            st.title("De estas peliculas cuales te gustan")
            st.markdown("Presiona \n 👍 SI te gusta | 👎 SI NO es para ti | 👁️ Si aun no la ves")
            
            # ==== Se obtienen peliculas ======
            if len(st.session_state.peliculas_queue) < 5:
                ids_generos = [str(agente_api.MAPEO_GENEROS[g]) for g in st.session_state.generos_temp]
                ids_str = "|".join(ids_generos) 
                
                nuevas_pelis = agente_api.obtener_peliculas_por_genero(ids_str, st.session_state.api_page)
                vistas = set(st.session_state.likes_temp + st.session_state.dislikes_temp)
                filtradas = [p for p in nuevas_pelis if p.get('id') not in vistas]
                
                st.session_state.peliculas_queue.extend(filtradas)
                st.session_state.api_page += 1 
            
            top_5 = st.session_state.peliculas_queue[:5]
            
            if top_5:
                cols = st.columns(5)
                for idx, peli in enumerate(top_5):
                    titulo = peli.get('title', 'Sin Titulo')
                    id_peli = peli.get('id')
                    poster_path = peli.get('poster_path')
                    
                    with cols[idx]:
                        st.markdown('<div class="peli-card">', unsafe_allow_html=True)
                        if poster_path:
                            url_imagen = f"https://image.tmdb.org/t/p/w200{poster_path}"
                            st.image(url_imagen, use_container_width=True)
                        
                        st.markdown(f'<div class="titulo-peli" title="{titulo}">{titulo}</div>', unsafe_allow_html=True)
                        
                        b1, b2, b3 = st.columns(3)
                        with b1:
                            if st.button("👍", key=f"l_{id_peli}", help="Me gusta"):
                                procesar_voto(id_peli, "like")
                                st.rerun()
                        with b2:
                            if st.button("👎", key=f"d_{id_peli}", help="No me gusta"):
                                procesar_voto(id_peli, "dislike")
                                st.rerun()
                        with b3:
                            if st.button("👁️", key=f"s_{id_peli}", help="Ignorar"):
                                procesar_voto(id_peli, "skip")
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Buscando mas peliculas")
            
            st.write("")
            votos_totales = len(st.session_state.likes_temp) + len(st.session_state.dislikes_temp)
            st.caption(f"Peliculas valoradas {votos_totales}")
            
            if st.button("Terminar y Guardar Perfil", type="primary", use_container_width=True):
                # ==== Se guarda la informacion ======
                agente_perfilador.crear_perfil(
                    st.session_state.usuario_temp, 
                    st.session_state.generos_temp,
                    st.session_state.likes_temp,
                    st.session_state.dislikes_temp
                )
                st.success("Perfil guardado permanentemente")
                st.session_state.peliculas_queue = []
                st.session_state.api_page = 1
                st.session_state.fase = "uso_diario"
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)