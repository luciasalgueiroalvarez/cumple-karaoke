import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Lu's Karaoke Party", 
    page_icon="🎤", 
    layout="centered"
)

# --- ESTILO CSS ACTUALIZADO ---
st.markdown("""
    <style>
    /* Fondo blanco en todas las páginas */
    .stApp {
        background-color: #FFFFFF;
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
    }
    /* Sidebar blanca */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVEGACIÓN ---
menu = ["🏠 Bienvenida", "🎤 Votar Actuación", "🏆 Ranking", "💌 Dedicatorias"]
choice = st.sidebar.radio("Menú", menu)

# --- 1. HOME PAGE ---
if choice == "🏠 Bienvenida":
    st.markdown("<h1 style='text-align: center;'>Lu's Karaoke Party</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    ### Espero que hayáis cenado bien porque ahora toca cantar a pleno pulmón. 🎤✨
    
    ¡Bienvenidos a mi 30 cumpleaños! Hoy la estrella eres tú (o al menos lo vas a intentar). 
    He montado esta web para que podamos puntuar los mejores shows de la noche. 
    
    **¿Cómo funciona?**
    * Ve a la sección **Votar** cuando alguien esté en el escenario.
    * Puntúa la **actitud, el show y la energía**. ¡La voz es lo de menos!
    * Mira el **Ranking** en directo para ver quién se lleva la gloria.
    
    Lo importante es participar y pasárselo super bien. 
    **¡Un chupito corre a cuenta de Lu para calentar motores!** 🥃
    """)

# --- 2. PÁGINA DE VOTACIONES ---
elif choice == "🎤 Votar Actuación":
    st.title("Puntúa el Show 📊")
    
    with st.form("voting_form", clear_on_submit=True):
        nombre_artista = st.text_input("👤 ¿Quién está en el escenario?", placeholder="Nombre...")
        
        c1 = st.slider("⭐ Actitud y Energía", 0, 5, 3)
        c2 = st.slider("🎭 Interpretación Dramática", 0, 5, 3)
        c3 = st.slider("🎉 Show y Escena", 0, 5, 3)
        c4 = st.slider("🔄 Originalidad", 0, 5, 3)
        c5 = st.slider("👯 Conexión con el Grupo", 0, 5, 3)
        
        submitted = st.form_submit_button("Enviar voto 🚀 🎤 🎶")
        
        if submitted:
            if nombre_artista:
                try:
                    # Forzamos la lectura para asegurar conexión
                    df_actual = conn.read(worksheet="votos", ttl=0)
                    nueva_fila = pd.DataFrame([{
                        "Artista": nombre_artista.strip().upper(),
                        "Puntos": c1 + c2 + c3 + c4 + c5,
                        "Hora": datetime.now().strftime("%H:%M:%S")
                    }])
                    df_actualizado = pd.concat([df_actual, nueva_fila], ignore_index=True)
                    conn.update(worksheet="votos", data=df_actualizado)
                    st.balloons()
                    st.success(f"¡Voto registrado!")
                except Exception as e:
                    st.error(f"Error al conectar con la base de datos. ¡Avisa a Lu! Detalle: {e}")
            else:
                st.warning("Escribe el nombre del artista.")

# --- 3. RANKING ---
elif choice == "🏆 Ranking":
    st.title("Podio de Estrellas (o Estrellados) 🌟")
    
    try:
        df_votos = conn.read(worksheet="votos", ttl=0)
        if not df_votos.empty:
            ranking = df_votos.groupby("Artista")["Puntos"].mean().sort_values(ascending=False).head(3)
            cols = st.columns(3)
            medallas = ["🥇", "🥈", "🥉"]
            for i, (artista, puntos) in enumerate(ranking.items()):
                with cols[i]:
                    st.markdown(f"<h1 style='text-align: center;'>{medallas[i]}</h1>", unsafe_allow_html=True)
                    st.metric(artista, f"{puntos:.1f}")
        else:
            st.info("Aún no hay votos.")
    except:
        st.error("Error al cargar el ranking.")

# --- 4. DEDICATORIAS ---
elif choice == "💌 Dedicatorias":
    st.title("Mensajes para Lu 🎂")

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
        nombre_invitado = st.text_input("Tu nombre:")
        mensaje_texto = st.text_area("Mensaje:")
        if st.form_submit_button("Enviar Mensaje 💌"):
            if mensaje_texto:
                try:
                    df_msjs = conn.read(worksheet="dedicatorias", ttl=0)
                    nuevo_msj = pd.DataFrame([{"Nombre": nombre_invitado if nombre_invitado else "Anónimo", "Mensaje": mensaje_texto}])
                    updated_df = pd.concat([df_msjs, nuevo_msj], ignore_index=True)
                    conn.update(worksheet="dedicatorias", data=updated_df)
                    popup_agradecimiento()
                except Exception as e:
                    st.error(f"No se pudo guardar el mensaje. Detalle: {e}")

    st.markdown("---")
    try:
        mensajes_db = conn.read(worksheet="dedicatorias", ttl=0)
        for _, fila in mensajes_db.iloc[::-1].iterrows():
            st.info(f"**{fila['Nombre']}**: {fila['Mensaje']}")
    except:
        pass
