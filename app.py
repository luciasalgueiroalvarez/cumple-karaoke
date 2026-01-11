import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Lu's 30th Karaoke Party", 
    page_icon="🎤", 
    layout="centered"
)

# --- ESTILO CSS PERSONALIZADO (Estética Invitación) ---
st.markdown("""
    <style>
    /* Fondo rosado pálido */
    .stApp {
        background-color: #FDECEC;
    }
    /* Títulos en Rojo */
    h1, h2, h3 {
        color: #C0392B !important;
        font-family: 'Arial Black', sans-serif;
    }
    /* Botones Rojos */
    .stButton>button {
        background-color: #C0392B;
        color: white;
        border-radius: 25px;
        border: none;
        font-weight: bold;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    /* Estilo de las tarjetas de mensajes */
    .stInfo {
        background-color: white;
        border-left: 5px solid #C0392B;
        border-radius: 10px;
    }
    /* Sidebar blanca */
    [data-testid="stSidebar"] {
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
# Asegúrate de configurar 'spreadsheet' en los Secrets de Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVEGACIÓN ---
st.sidebar.image("https://img.icons8.com/color/144/star--v1.png", width=50)
menu = ["🏠 Bienvenida", "🎤 Votar Actuación", "🏆 Ranking", "💌 Dedicatorias"]
choice = st.sidebar.radio("Menú", menu)

# --- 1. HOME PAGE ---
if choice == "🏠 Bienvenida":
    st.markdown("<h1 style='text-align: center;'>¡TE INVITO A MI CUMPLE!</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    ### "Espero que hayáis cenado bien porque ahora toca cantar a pleno pulmón." 🎤✨
    
    ¡Bienvenidos a mi 30 cumpleaños! Hoy la estrella eres tú (o al menos lo vas a intentar). 
    He montado esta web para que podamos puntuar los mejores shows de la noche. 
    
    **¿Cómo funciona?**
    * Ve a la sección **Votar** cuando alguien esté en el escenario.
    * Puntúa la **actitud, el show y la energía**. ¡La voz es lo de menos!
    * Mira el **Ranking** en directo para ver quién se lleva la gloria.
    
    Lo importante es participar y pasárselo super bien. 
    **¡Un chupito corre a cuenta de Lu para calentar motores!** 🥃
    """)
    st.image("https://img.icons8.com/bubbles/200/microphone.png")

# --- 2. PÁGINA DE VOTACIONES ---
elif choice == "🎤 Votar Actuación":
    st.title("Puntúa el Show 📊")
    st.write("Recuerda: solo un voto por actuación. ¡Sé justo pero divertido!")
    
    with st.form("voting_form", clear_on_submit=True):
        nombre_artista = st.text_input("👤 ¿Quién está dándolo todo?", placeholder="Nombre del artista...")
        
        st.write("---")
        c1 = st.slider("⭐ Actitud y Energía", 0, 5, 3, help="Entrega y confianza")
        c2 = st.slider("🎭 Interpretación Dramática", 0, 5, 3, help="Emoción y gestos")
        c3 = st.slider("🎉 Show y Escena", 0, 5, 3, help="Uso del escenario")
        c4 = st.slider("🔄 Originalidad", 0, 5, 3, help="Elección de canción")
        c5 = st.slider("👯 Conexión con el Grupo", 0, 5, 3, help="Público animando")
        
        submitted = st.form_submit_button("Enviar voto 🚀 🎤 🎶")
        
        if submitted:
            if nombre_artista:
                total_puntos = c1 + c2 + c3 + c4 + c5
                # Guardar en Sheets
                try:
                    df_actual = conn.read(worksheet="votos")
                    nueva_fila = pd.DataFrame([{
                        "Artista": nombre_artista.strip().upper(),
                        "Puntos": total_puntos,
                        "Hora": datetime.now().strftime("%H:%M:%S")
                    }])
                    df_actualizado = pd.concat([df_actual, nueva_fila], ignore_index=True)
                    conn.update(worksheet="votos", data=df_actualizado)
                    
                    st.balloons()
                    st.success(f"¡Voto registrado para {nombre_artista}! Total: {total_puntos} pts.")
                except Exception as e:
                    st.error("Error al conectar con la base de datos. ¡Avisa a Lu!")
            else:
                st.warning("¡Eh! No olvides poner el nombre del artista.")

# --- 3. RANKING (PODIO) ---
elif choice == "🏆 Ranking":
    st.title("Podio de Estrellas 🌟")
    
    try:
        df_votos = conn.read(worksheet="votos")
        if not df_votos.empty:
            # Media de puntos por artista
            ranking = df_votos.groupby("Artista")["Puntos"].mean().sort_values(ascending=False).head(3)
            
            cols = st.columns(3)
            medallas = ["🥇", "🥈", "🥉"]
            
            for i, (artista, puntos) in enumerate(ranking.items()):
                with cols[i]:
                    st.markdown(f"<h1 style='text-align: center;'>{medallas[i]}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-weight: bold;'>{artista}</p>", unsafe_allow_html=True)
                    st.metric("Puntos Media", f"{puntos:.1f}")
            
            st.write("---")
            st.write("### Tabla de puntuaciones completas")
            st.dataframe(df_votos)
        else:
            st.info("El podio está esperando... ¡Nadie ha votado todavía!")
    except:
        st.error("Todavía no hay datos registrados.")

# --- 4. DEDICATORIAS CON POP-UP ---
elif choice == "💌 Dedicatorias":
    st.title("Mensajes para Lu 🎂")

    # Definición del Pop-up de agradecimiento
    @st.dialog("¡Un mensaje de Lu! ❤️")
    def popup_agradecimiento():
        st.markdown("""
        **Gracias de verdad por venir a celebrar mis 30 conmigo 🥹🫶**

        Está siendo una noche increíble: risas, canciones reventadas, momentazos y muy buena compañía.  

        Gracias por darlo todo y hacer que la fiesta fuese tan especial. Sin ti no es lo mismo 💖

        *Me quedo con un recuerdo brutal 💛🎤*
        """)
        if st.button("Cerrar"):
            st.rerun()

    with st.form("dedicatoria_form", clear_on_submit=True):
        nombre_invitado = st.text_input("Tu nombre (déjalo vacío si prefieres el anonimato):")
        mensaje_texto = st.text_area("Escríbeme algo bonito...")
        
        boton_envio = st.form_submit_button("Enviar Mensaje 💌")
        
        if boton_envio:
            if mensaje_texto:
                try:
                    # Guardar en Sheets
                    df_msjs = conn.read(worksheet="dedicatorias")
                    nuevo_msj = pd.DataFrame([{
                        "Nombre": nombre_invitado if nombre_invitado else "Anónimo",
                        "Mensaje": mensaje_texto
                    }])
                    df_msjs_total = pd.concat([df_msjs, nuevo_msj], ignore_index=True)
                    conn.update(worksheet="dedicatorias", data=df_msjs_total)
                    
                    # Mostrar Pop-up
                    popup_agradecimiento()
                except:
                    st.error("No se pudo guardar el mensaje. ¡Inténtalo de nuevo!")
            else:
                st.warning("¡No me dejes el cuadro en blanco!")

    st.write("---")
    st.subheader("Muro de Recuerdos✨")
    try:
        mensajes_db = conn.read(worksheet="dedicatorias")
        for _, fila in mensajes_db.iloc[::-1].iterrows():
            st.info(f"**{fila['Nombre']}** dice: \n\n {fila['Mensaje']}")
    except:
        st.write("¡Sé el primero en escribir una dedicatoria💌!")
