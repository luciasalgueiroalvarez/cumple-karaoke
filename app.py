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

# --- ESTILO CSS (Fondo Blanco, Sin Comillas, Estilo Limpio) ---
st.markdown("""
    <style>
    /* Fondo blanco total */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Títulos en Rojo */
    h1, h2, h3 {
        color: #C0392B !important;
        font-family: 'Arial Black', sans-serif;
    }
    
    /* Botones Rojos y Redondos */
    .stButton>button {
        background-color: #C0392B;
        color: white;
        border-radius: 25px;
        border: none;
        font-weight: bold;
        height: 3em;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #A93226;
        transform: scale(1.02);
    }

    /* Sidebar gris muy claro */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
    }
    
    /* Inputs con fondo suave para contraste */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #FDF2F2;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Error en la configuración de Secrets.")

# --- NAVEGACIÓN ---
menu = ["🏠 Bienvenida", "🎤 Votar actuación", "🏆 Ranking", "💌 Dedicatorias"]
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
    **¡Un chupito corre a cuenta de Lu para calentar motores!** 🥂
    """)

# --- 2. PÁGINA DE VOTACIONES ---
elif choice == "🎤 Votar Actuación":
    st.title("Puntúa el show 📊")
    
    with st.form("voting_form", clear_on_submit=True):
        nombre_artista = st.text_input("👤 ¿Quién está en el escenario?", placeholder="Escribe el nombre...")
        
        st.write("---")
        # Sliders
        c1 = st.slider("⭐ Actitud y Energía", 0, 5, 3)
        c2 = st.slider("🎭 Interpretación Dramática", 0, 5, 3)
        c3 = st.slider("🎉 Show y Escena", 0, 5, 3)
        c4 = st.slider("🔄 Originalidad", 0, 5, 3)
        c5 = st.slider("👯 Conexión con el Grupo", 0, 5, 3)
        
        submitted = st.form_submit_button("Enviar voto 🚀 🎤 🎶")
        
        if submitted:
            if nombre_artista:
                try:
                    # 1. Intentamos leer la hoja. Usamos ttl=0 para no usar caché vieja.
                    try:
                        df_actual = conn.read(worksheet="votos", ttl=0)
                    except:
                        # Si falla al leer (porque está vacía), creamos un DF vacío
                        df_actual = pd.DataFrame(columns=["Artista", "Puntos", "Hora"])

                    # 2. Si el dataframe viene vacío o nulo, lo forzamos
                    if df_actual is None or df_actual.empty:
                        df_actual = pd.DataFrame(columns=["Artista", "Puntos", "Hora"])

                    # 3. Crear nueva fila
                    total_puntos = c1 + c2 + c3 + c4 + c5
                    nueva_fila = pd.DataFrame([{
                        "Artista": nombre_artista.strip().upper(),
                        "Puntos": total_puntos,
                        "Hora": datetime.now().strftime("%H:%M:%S")
                    }])
                    
                    # 4. Concatenar y guardar
                    # Importante: reset_index evita problemas de índices duplicados
                    df_actualizado = pd.concat([df_actual, nueva_fila], ignore_index=True)
                    
                    conn.update(worksheet="votos", data=df_actualizado)
                    
                    st.balloons()
                    st.success(f"¡Voto registrado para {nombre_artista}!")
                    
                except Exception as e:
                    st.error("⚠️ Error de conexión (Error 400)")
                    st.warning("Posible causa: El Google Sheet no tiene permisos de 'Editor' para cualquiera con el enlace.")
                    st.code(f"Detalle: {e}")
            else:
                st.warning("¡Falta el nombre del artista!")

# --- 3. RANKING ---
elif choice == "🏆 Ranking":
    st.title("Podio de Estrellas (o Estrellados) 🌟")
    
    try:
        # Leemos forzando actualización
        df_votos = conn.read(worksheet="votos", ttl=0)
        
        if df_votos is not None and not df_votos.empty:
            # Agrupar y calcular media
            ranking = df_votos.groupby("Artista")["Puntos"].mean().sort_values(ascending=False).head(3)
            
            cols = st.columns(3)
            medallas = ["🥇", "🥈", "🥉"]
            
            for i, (artista, puntos) in enumerate(ranking.items()):
                with cols[i]:
                    st.markdown(f"<h1 style='text-align: center;'>{medallas[i]}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-weight: bold; font-size: 1.2em; color: #C0392B;'>{artista}</p>", unsafe_allow_html=True)
                    st.metric("Puntos", f"{puntos:.1f}")
            
            st.write("---")
            with st.expander("Ver tabla completa"):
                st.dataframe(df_votos)
        else:
            st.info("Aún no hay votos registrados. ¡Sé el primero!")
            
    except Exception as e:
        st.info("El ranking está vacío o cargando...")

# --- 4. DEDICATORIAS ---
elif choice == "💌 Dedicatorias":
    st.title("Mensajes para Lu 🎂")

    # Definimos el Pop-up (Dialog)
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
        nombre_invitado = st.text_input("Tu nombre (opcional):")
        mensaje_texto = st.text_area("Tu mensaje para la cumpleañera:")
        
        if st.form_submit_button("Enviar Mensaje 💌"):
            if mensaje_texto:
                try:
                    # Lectura segura
                    try:
                        df_msjs = conn.read(worksheet="dedicatorias", ttl=0)
                    except:
                        df_msjs = pd.DataFrame(columns=["Nombre", "Mensaje"])
                        
                    if df_msjs is None or df_msjs.empty:
                        df_msjs = pd.DataFrame(columns=["Nombre", "Mensaje"])

                    nuevo_msj = pd.DataFrame([{
                        "Nombre": nombre_invitado if nombre_invitado else "Anónimo", 
                        "Mensaje": mensaje_texto
                    }])
                    
                    df_final = pd.concat([df_msjs, nuevo_msj], ignore_index=True)
                    conn.update(worksheet="dedicatorias", data=df_final)
                    
                    popup_agradecimiento()
                    
                except Exception as e:
                    st.error("No se pudo guardar. Revisa los permisos del Sheet.")
            else:
                st.warning("¡Escribe algo bonito!")

    st.markdown("---")
    st.subheader("Muro de Recuerdos ✨")
    try:
        mensajes_db = conn.read(worksheet="dedicatorias", ttl=0)
        if mensajes_db is not None and not mensajes_db.empty:
            for _, fila in mensajes_db.iloc[::-1].iterrows():
                st.info(f"**{fila['Nombre']}**: {fila['Mensaje']}")
    except:
        pass
