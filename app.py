import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Lu's Karaoke Party", 
    page_icon="🎤", 
    layout="centered",
    initial_sidebar_state="collapsed" # En móvil oculta el menú para ganar espacio
)

# --- ESTILO CSS RESPONSIVE ---
st.markdown("""
    <style>
    /* ESTILOS GENERALES (PC y Móvil) */
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { 
        color: #C0392B !important; 
        font-family: 'Arial Black', sans-serif; 
    }
    .stButton>button {
        background-color: #C0392B; 
        color: white; 
        border-radius: 25px; 
        border: none;
        font-weight: bold; 
        height: 3.5em; 
        width: 100%;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:active {
        background-color: #A93226;
        transform: scale(0.98);
    }
    [data-testid="stSidebar"] { background-color: #F8F9FA; }
    
    /* Inputs más amigables al tacto */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
        background-color: #FDF2F2; 
        font-size: 16px; /* Evita zoom automático en iPhone */
    }

    /* --- MODO MÓVIL (PANTALLAS PEQUEÑAS) --- */
    @media only screen and (max-width: 600px) {
        /* Títulos más pequeños para que no ocupen toda la pantalla */
        h1 { font-size: 2rem !important; text-align: center; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.2rem !important; }
        
        /* Ajuste de márgenes para ganar espacio */
        .block-container {
            padding-top: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* Botones más grandes para dedos */
        .stButton>button {
            height: 4em;
            font-size: 1.1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE DATOS (SISTEMA HÍBRIDO) ---
if 'votos_local' not in st.session_state:
    st.session_state.votos_local = pd.DataFrame(columns=["Artista", "Puntos", "Hora"])
if 'dedicatorias_local' not in st.session_state:
    st.session_state.dedicatorias_local = pd.DataFrame(columns=["Nombre", "Mensaje"])

# Conexión a Sheets (Intento silencioso)
conn = None
usar_sheets = False
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    test = conn.read(worksheet="votos", ttl=0) # Prueba de lectura
    usar_sheets = True
except:
    usar_sheets = False

# --- MENÚ SIDEBAR ---
menu = ["🏠 Bienvenida", "🎤 Votar Actuación", "🏆 Ranking", "💌 Dedicatorias"]
choice = st.sidebar.radio("Menú", menu)

st.sidebar.markdown("---")
# Estado de conexión discreto
if usar_sheets:
    st.sidebar.caption("🟢 Conexión Nube: OK")
else:
    st.sidebar.caption("🟠 Modo Local (Descarga los datos antes de cerrar)")

# Botones de descarga (Backup)
csv_votos = st.session_state.votos_local.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Descargar CSV Votos", csv_votos, "votos.csv", "text/csv")

csv_dedicatorias = st.session_state.dedicatorias_local.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Descargar CSV Mensajes", csv_dedicatorias, "mensajes.csv", "text/csv")


# --- 1. HOME PAGE ---
if choice == "🏠 Bienvenida":
    st.markdown("<h1>Lu's Karaoke Party</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h3>Espero que hayáis cenado bien porque ahora toca cantar a pleno pulmón. 🎤✨</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("""
    **¡Bienvenidos a los 30!** Hoy la estrella eres tú.
    
    1. **Vota** al artista en escena.
    2. Puntúa su **energía y show**.
    3. Revisa el **Ranking** en vivo.
    
    🥃 **¡Un chupito corre a cuenta de Lu!**
    """)

# --- 2. PÁGINA DE VOTACIONES ---
elif choice == "🎤 Votar Actuación":
    st.title("Puntúa el Show 📊")
    
    with st.form("voting_form", clear_on_submit=True):
        nombre = st.text_input("👤 ¿Quién canta?", placeholder="Nombre del artista...")
        
        st.write("---")
        # Sliders simplificados visualmente
        c1 = st.slider("⭐ Actitud", 0, 5, 3)
        c2 = st.slider("🎭 Dramatismo", 0, 5, 3)
        c3 = st.slider("🎉 Show", 0, 5, 3)
        c4 = st.slider("🔄 Originalidad", 0, 5, 3)
        c5 = st.slider("👯 Público", 0, 5, 3)
        
        submitted = st.form_submit_button("Enviar voto 🚀")
        
        if submitted and nombre:
            total = c1 + c2 + c3 + c4 + c5
            nuevo_dato = {
                "Artista": nombre.strip().upper(),
                "Puntos": total,
                "Hora": datetime.now().strftime("%H:%M:%S")
            }
            
            # Guardar Local
            st.session_state.votos_local = pd.concat([st.session_state.votos_local, pd.DataFrame([nuevo_dato])], ignore_index=True)
            
            # Guardar Nube (si hay)
            if usar_sheets and conn:
                try:
                    df_nube = conn.read(worksheet="votos", ttl=0)
                    df_nube = pd.concat([df_nube, pd.DataFrame([nuevo_dato])], ignore_index=True)
                    conn.update(worksheet="votos", data=df_nube)
                except:
                    pass
            
            st.balloons()
            st.success(f"¡Voto enviado! ({total} pts)")

# --- 3. RANKING ---
elif choice == "🏆 Ranking":
    st.title("Podio 🌟")
    
    # Lógica de datos (Híbrida)
    df_final = st.session_state.votos_local
    if usar_sheets:
        try:
            df_cloud = conn.read(worksheet="votos", ttl=0)
            if df_cloud is not None and not df_cloud.empty:
                df_final = df_cloud
        except:
            pass

    if not df_final.empty:
        # Ranking
        ranking = df_final.groupby("Artista")["Puntos"].mean().sort_values(ascending=False).head(3)
        
        # En móvil, las columnas se apilan verticalmente automáticamente
        cols = st.columns(3)
        medallas = ["🥇", "🥈", "🥉"]
        
        for i, (artista, puntos) in enumerate(ranking.items()):
            with cols[i]:
                st.markdown(f"<div style='text-align:center; padding:10px; border: 1px solid #eee; border-radius:10px; margin-bottom:10px;'><h1>{medallas[i]}</h1><h3 style='color:#C0392B; margin:0;'>{artista}</h3><p style='font-size:1.2rem; font-weight:bold;'>{puntos:.1f} pts</p></div>", unsafe_allow_html=True)
        
        with st.expander("Ver lista completa"):
            st.dataframe(df_final)
    else:
        st.info("¡Esperando votos!")

# --- 4. DEDICATORIAS ---
elif choice == "💌 Dedicatorias":
    st.title("Mensajes 🎂")
    
    @st.dialog("¡Mensaje de Lu! ❤️")
    def popup():
        st.markdown("""
        **¡Gracias por venir a mis 30! 🥹🫶**
        
        Risas, canciones y momentazos.
        Gracias por hacerlo especial.
        
        *Recuerdo desbloqueado 💛🎤*
        """)
        if st.button("Cerrar"):
            st.rerun()

    with st.form("msg_form", clear_on_submit=True):
        nombre = st.text_input("Tu nombre:")
        msj = st.text_area("Mensaje:")
        if st.form_submit_button("Enviar 💌") and msj:
            nuevo = {"Nombre": nombre if nombre else "Anónimo", "Mensaje": msj}
            
            # Guardar
            st.session_state.dedicatorias_local = pd.concat([st.session_state.dedicatorias_local, pd.DataFrame([nuevo])], ignore_index=True)
            if usar_sheets and conn:
                try:
                    df_n = conn.read(worksheet="dedicatorias", ttl=0)
                    df_n = pd.concat([df_n, pd.DataFrame([nuevo])], ignore_index=True)
                    conn.update(worksheet="dedicatorias", data=df_n)
                except:
                    pass
            popup()

    st.write("---")
    # Mostrar mensajes
    df_ver = st.session_state.dedicatorias_local
    if usar_sheets:
        try:
            df_c = conn.read(worksheet="dedicatorias", ttl=0)
            if not df_c.empty: df_ver = df_c
        except: pass
            
    for _, row in df_ver.iloc[::-1].iterrows():
        st.info(f"**{row['Nombre']}**: {row['Mensaje']}")
