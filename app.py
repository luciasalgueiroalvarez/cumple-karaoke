import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Lu's Karaoke Party", 
    page_icon="🎤", 
    layout="centered"
)

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #C0392B !important; font-family: 'Arial Black', sans-serif; }
    .stButton>button {
        background-color: #C0392B; color: white; border-radius: 25px; border: none;
        font-weight: bold; height: 3em; width: 100%;
    }
    .stButton>button:hover { background-color: #A93226; transform: scale(1.02); }
    [data-testid="stSidebar"] { background-color: #F8F9FA; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #FDF2F2; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE DATOS (HYBRID SYSTEM) ---
# Inicializamos el estado local por si falla Sheets
if 'votos_local' not in st.session_state:
    st.session_state.votos_local = pd.DataFrame(columns=["Artista", "Puntos", "Hora"])
if 'dedicatorias_local' not in st.session_state:
    st.session_state.dedicatorias_local = pd.DataFrame(columns=["Nombre", "Mensaje"])

# Intentamos conectar a Google Sheets
conn = None
usar_sheets = False

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Hacemos una lectura de prueba rápida
    test = conn.read(worksheet="votos", ttl=0)
    usar_sheets = True
except Exception:
    usar_sheets = False
    # No mostramos error feo, simplemente usamos modo local silenciosamente

# --- SIDEBAR: GESTIÓN Y DESCARGAS ---
menu = ["🏠 Bienvenida", "🎤 Votar Actuación", "🏆 Ranking", "💌 Dedicatorias"]
choice = st.sidebar.radio("Menú", menu)

st.sidebar.markdown("---")
st.sidebar.caption("⚙️ Panel de Control")

# Indicador de estado
if usar_sheets:
    st.sidebar.success("🟢 Nube: Conectada")
else:
    st.sidebar.warning("🟠 Nube: Desconectada (Modo Local)")
    st.sidebar.info("¡No cierres la pestaña del navegador principal o descarga los datos a menudo!")

# Botones de descarga (Salvavidas)
csv_votos = st.session_state.votos_local.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Descargar Votos", csv_votos, "votos_karaoke.csv", "text/csv")

csv_dedicatorias = st.session_state.dedicatorias_local.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Descargar Mensajes", csv_dedicatorias, "mensajes_lu.csv", "text/csv")


# --- 1. HOME PAGE ---
if choice == "🏠 Bienvenida":
    st.markdown("<h1 style='text-align: center;'>Lu's Karaoke Party</h1>", unsafe_allow_html=True)
    st.markdown("""
    ### Espero que hayáis cenado bien porque ahora toca cantar a pleno pulmón. 🎤✨
    
    ¡Bienvenidos a mi 30 cumpleaños! Hoy la estrella eres tú.
    He montado esta web para que podamos puntuar los mejores shows de la noche. 
    
    **¿Cómo funciona?**
    * Ve a la sección **Votar** cuando alguien esté en el escenario.
    * Puntúa la **actitud, el show y la energía**.
    * Mira el **Ranking** en directo.
    
    **¡Un chupito corre a cuenta de Lu para calentar motores!** 🥃
    """)

# --- 2. PÁGINA DE VOTACIONES ---
elif choice == "🎤 Votar Actuación":
    st.title("Puntúa el Show 📊")
    with st.form("voting_form", clear_on_submit=True):
        nombre = st.text_input("👤 ¿Quién está en el escenario?")
        st.write("---")
        c1 = st.slider("⭐ Actitud y Energía", 0, 5, 3)
        c2 = st.slider("🎭 Interpretación Dramática", 0, 5, 3)
        c3 = st.slider("🎉 Show y Escena", 0, 5, 3)
        c4 = st.slider("🔄 Originalidad", 0, 5, 3)
        c5 = st.slider("👯 Conexión con el Grupo", 0, 5, 3)
        
        submitted = st.form_submit_button("Enviar voto 🚀")
        
        if submitted and nombre:
            puntos = c1 + c2 + c3 + c4 + c5
            nuevo_dato = {
                "Artista": nombre.strip().upper(),
                "Puntos": puntos,
                "Hora": datetime.now().strftime("%H:%M:%S")
            }
            
            # Guardar en Local (Siempre funciona)
            st.session_state.votos_local = pd.concat([st.session_state.votos_local, pd.DataFrame([nuevo_dato])], ignore_index=True)
            
            # Intentar guardar en Nube (Si hay conexión)
            saved_cloud = False
            if usar_sheets and conn:
                try:
                    df_nube = conn.read(worksheet="votos", ttl=0)
                    df_nube = pd.concat([df_nube, pd.DataFrame([nuevo_dato])], ignore_index=True)
                    conn.update(worksheet="votos", data=df_nube)
                    saved_cloud = True
                except:
                    saved_cloud = False
            
            st.balloons()
            if saved_cloud:
                st.success(f"¡Voto guardado en la nube! ({puntos} pts)")
            else:
                st.success(f"¡Voto guardado localmente! ({puntos} pts)")

# --- 3. RANKING ---
elif choice == "🏆 Ranking":
    st.title("Podio de Estrellas (o Estrellados) 🌟")
    
    # Decidimos qué datos mostrar: Nube o Local
    df_mostrar = st.session_state.votos_local
    if usar_sheets:
        try:
            df_nube = conn.read(worksheet="votos", ttl=0)
            if df_nube is not None and not df_nube.empty:
                df_mostrar = df_nube
        except:
            pass # Si falla nube, mostramos local
            
    if not df_mostrar.empty:
        ranking = df_mostrar.groupby("Artista")["Puntos"].mean().sort_values(ascending=False).head(3)
        cols = st.columns(3)
        medallas = ["🥇", "🥈", "🥉"]
        for i, (artista, puntos) in enumerate(ranking.items()):
            with cols[i]:
                st.markdown(f"<h1 style='text-align: center;'>{medallas[i]}</h1>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color:#C0392B; font-weight:bold'>{artista}</p>", unsafe_allow_html=True)
                st.metric("Media", f"{puntos:.1f}")
        
        st.write("---")
        with st.expander("Ver lista completa"):
            st.dataframe(df_mostrar)
    else:
        st.info("Aún no hay votos registrados.")

# --- 4. DEDICATORIAS ---
elif choice == "💌 Dedicatorias":
    st.title("Mensajes para Lu 🎂")
    
    @st.dialog("¡Un mensaje de Lu! ❤️")
    def popup():
        st.markdown("""
        **Gracias de verdad por venir a celebrar mis 30 conmigo 🥹🫶**
        Está siendo una noche increíble: risas, canciones reventadas y muy buena compañía.
        Gracias por hacer que la fiesta fuese tan especial. 💖
        *Me quedo con un recuerdo brutal 💛🎤*
        """)
        if st.button("Cerrar"):
            st.rerun()

    with st.form("msg_form", clear_on_submit=True):
        nombre = st.text_input("Tu nombre:")
        msj = st.text_area("Mensaje:")
        if st.form_submit_button("Enviar Mensaje 💌") and msj:
            nuevo_msj = {"Nombre": nombre if nombre else "Anónimo", "Mensaje": msj}
            
            # Guardar Local
            st.session_state.dedicatorias_local = pd.concat([st.session_state.dedicatorias_local, pd.DataFrame([nuevo_msj])], ignore_index=True)
            
            # Intentar Nube
            if usar_sheets and conn:
                try:
                    df_n = conn.read(worksheet="dedicatorias", ttl=0)
                    df_n = pd.concat([df_n, pd.DataFrame([nuevo_msj])], ignore_index=True)
                    conn.update(worksheet="dedicatorias", data=df_n)
                except:
                    pass
            popup()
            
    st.markdown("---")
    # Mostrar mensajes
    df_ver = st.session_state.dedicatorias_local
    if usar_sheets:
        try:
            df_nube_msj = conn.read(worksheet="dedicatorias", ttl=0)
            if not df_nube_msj.empty:
                df_ver = df_nube_msj
        except:
            pass
            
    for _, row in df_ver.iloc[::-1].iterrows():
        st.info(f"**{row['Nombre']}**: {row['Mensaje']}")
