import streamlit as st
from agentes import agente_perfilador, agente_api, agente_orquestador

def procesar_voto_panel(id_peli, tipo_voto):

    # Se carga la memoria actual del usuario
    perfil = agente_perfilador.obtener_perfil(st.session_state.usuario_temp)
    likes = perfil.get("peliculas_likeadas", [])
    dislikes = perfil.get("peliculas_dislikeadas", [])
    
    # Se actualizan las listas
    if tipo_voto == "like" and id_peli not in likes:
        likes.append(id_peli)
    elif tipo_voto == "dislike" and id_peli not in dislikes:
        dislikes.append(id_peli)
        
    # Se guarda el perfil actualizado
    agente_perfilador.crear_perfil(
        st.session_state.usuario_temp,
        perfil["generos_favoritos"],
        likes,
        dislikes
    )

def mostrar():
    col_titulo, col_vacia, col_logout = st.columns([5, 2, 1])
    with col_titulo:
        st.title("Panel Principal")
        st.subheader(f"Bienvenido, {st.session_state.usuario_temp}")
    with col_logout:
        st.write("") 
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    if "mostrar_filtros" not in st.session_state: st.session_state.mostrar_filtros = True
    if "buscar_trigger" not in st.session_state: st.session_state.buscar_trigger = False
    if "busqueda_page" not in st.session_state: st.session_state.busqueda_page = 1

    # ==== Seccion Filtros ====
    with st.expander("🔍 Filtros de Búsqueda", expanded=st.session_state.mostrar_filtros):
        st.markdown("¿Qué tienes ganas de ver hoy?")
        
        lista_generos = list(agente_api.MAPEO_GENEROS.keys())
        generos_hoy = st.pills("Géneros que te apetecen ahora mismo", lista_generos, selection_mode="multi")
        
        st.write("")
        tipo_anio = st.radio("Filtro de Año", ["No me importa", "Definir rango"], horizontal=True)
        anio_inicio, anio_fin = None, None
        
        if tipo_anio == "Definir rango":
            col_y1, col_y2 = st.columns(2)
            with col_y1:
                anio_inicio = st.number_input("Desde el año:", min_value=1900, max_value=2026, value=2000, step=1)
            with col_y2:
                anio_fin = st.number_input("Hasta el año:", min_value=1900, max_value=2026, value=2026, step=1)
        
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            animo = st.selectbox("¿Cómo te sientes hoy?", ["Feliz / Relajado", "Estresado / Cansado", "Triste / Melancólico", "Quiero pensar / Intelectual"])
        with col2:
            tiempo = st.selectbox("Tiempo disponible", ["Menos de 2 horas", "Más de 2 horas", "Me da igual"])
            
        if st.button("Buscar Películas", type="primary"):
            st.session_state.mostrar_filtros = False
            st.session_state.buscar_trigger = True
            st.session_state.busqueda_page = 1 
            st.session_state.last_filters = (generos_hoy, anio_inicio, anio_fin, animo, tiempo)
            st.rerun()

    # ==== Seccion Resultados ====
    if st.session_state.buscar_trigger:
        with st.expander("🎬 Tus Recomendaciones", expanded=not st.session_state.mostrar_filtros):
            with st.spinner("Los agentes están rastreando la base de datos..."):
                generos_hoy, anio_inicio, anio_fin, animo, tiempo = st.session_state.last_filters
                
                top_final = agente_orquestador.ejecutar_pipeline_recomendacion(
                    st.session_state.usuario_temp, 
                    generos_hoy, anio_inicio, anio_fin, animo, tiempo, 
                    st.session_state.busqueda_page
                )
            
            if top_final:
                espacio_izq, c1, c2, c3, espacio_der = st.columns([1, 2, 2, 2, 1])
                cols = [c1, c2, c3]
                
                for idx, peli in enumerate(top_final):
                    with cols[idx]:
                        st.markdown('<div class="peli-card" style="padding: 5px;">', unsafe_allow_html=True)
                        id_peli = peli.get("id")
                        
                        if peli.get("poster_path"):
                            st.image(f"https://image.tmdb.org/t/p/w200{peli['poster_path']}", use_container_width=True)
                        
                        st.markdown(f'<div class="titulo-peli" title="{peli["title"]}">{peli["title"]}</div>', unsafe_allow_html=True)
                        st.caption(f"📅 Fecha: {peli.get('release_date', '')[:4]} | ⏱ Duración: {peli.get('runtime', 0)} min")
                        
                        score = peli['match_score'] / 100
                        st.progress(score, text=f"Match {peli['match_score']}%")
                        
                        # Seccion interactiva para el aprendizaje del agente
                        st.markdown("<hr style='margin: 10px 0; border-color: #333;'>", unsafe_allow_html=True)
                        st.caption("Ya la viste Te gusto")
                        
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("👍", key=f"panel_like_{id_peli}", help="Me gusto", use_container_width=True):
                                procesar_voto_panel(id_peli, "like")
                                st.rerun()
                                
                        with b2:
                            if st.button("👎", key=f"panel_dislike_{id_peli}", help="No me gusto", use_container_width=True):
                                procesar_voto_panel(id_peli, "dislike")
                                st.rerun()
                                
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("El motor logico descarto las opciones Intenta refrescar o cambiar los filtros")
            
            st.divider()
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔄 Mostrar otras opciones", use_container_width=True):
                    st.session_state.busqueda_page += 1
                    st.rerun()
            with col_btn2:
                if st.button(" Cambiar Filtros", use_container_width=True):
                    st.session_state.mostrar_filtros = True
                    st.session_state.buscar_trigger = False
                    st.rerun()