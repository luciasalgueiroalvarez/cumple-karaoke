import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Lu's Karaoke Party", 
    page_icon="🎤", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ESTILO CSS RESPONSIVE ---
st.markdown("""
    <style>
    /* General */
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #C0392B !important; font-family: 'Arial Black', sans-serif; }
    
    /* Botones grandes y táctiles */
    .stButton>button {
        background-color: #C0392B; 
        color: white; 
        border-radius: 25px; 
        border: none;
        font-weight: bold; 
        height: 3.5em; 
        width: 100%;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.1s;
    }
    .stButton>button:active { transform: scale(0.95); background-color: #A93226; }
    
    /* Ajustes para móvil */
    @media only screen and (max-width: 600px) {
        h1 { font-size: 2rem !important; text-align: center; }
        .block-container { padding-top: 1.5rem !important; }
        .stButton>button { font-size: 1.1rem; }
    }
    
    /* Inputs suaves */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
        background-color: #FDF2F2; 
        font-size: 16px; /* Evita zoom en iOS */
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A LA NUBE (OBLIGATORIA) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ Error de conexión con el servidor.")
    st.stop()

# --- MENÚ ---
menu = ["🏠 Bienvenida", "🎤 Votar Actuación", "🏆 Ranking", "💌 Dedicatorias"]
choice = st.sidebar.radio("Menú", menu)

# --- 1. HOME ---
if choice == "🏠 Bienvenida":
    st.markdown("<h1 style='text-align: center;'>Lu's Karaoke Party</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h3>¡Cena bien, que toca cantar! 🎤✨</h3>
    </div>
    """, unsafe_allow_html=True)
    st.info("""
    **Instrucciones rápidas:**
    1. Escucha al artista.
    2. Ve al menú **Votar**.
    3. ¡Mira cómo cambia el **Ranking** en tiempo real!
    
    🥃 **Chupito gratis cortesía de Lu.**
    """)

# --- 2. VOTAR (Escritura en Nube) ---
elif choice == "🎤 Votar Actuación":
    st.title("Puntúa el Show 📊")
    
    with st.form("voting_form", clear_on_submit=True):
        nombre = st.text_input("👤 Nombre del artista:", placeholder="Ej: La tía Paqui")
        st.write("---")
        
        # Sliders
        c1 = st.slider("⭐ Actitud", 0, 5, 3)
        c2 = st.slider("🎭 Dramatismo", 0, 5, 3)
        c3 = st.slider("🎉 Show", 0, 5, 3)
        c4 = st.slider("🔄 Originalidad", 0, 5, 3)
        c5 = st.slider("👯 Público", 0, 5, 3)
        
        submitted = st.form_submit_button("Enviar Voto 🚀")
        
        if submitted:
            if nombre:
                try:
                    # 1. Leer datos actuales (ttl=0 fuerza lectura real)
                    df_actual = conn.read(worksheet="votos", ttl=0)
                    
                    # 2. Crear nueva fila
                    nuevo_voto = pd.DataFrame([{
                        "Artista": nombre.strip().upper(),
                        "Puntos": c1+c2+c3+c4+c5,
                        "Hora": datetime.now().strftime("%H:%M:%S")
                    }])
                    
                    # 3. Concatenar y Subir
                    # Usamos concat asegurando que las columnas coincidan
                    df_final = pd.concat([df_actual, nuevo_voto], ignore_index=True)
                    conn.update(worksheet="votos", data=df_final)
                    
                    st.balloons()
                    st.success(f"¡Voto enviado a la nube! Total: {c1+c2+c3+c4+c5}")
                except Exception as e:
                    st.error("Error al sincronizar. Inténtalo de nuevo.")
                    # st.write(e) # Descomentar solo si necesitas ver el error técnico
            else:
                st.warning("¡Falta el nombre!")

# --- 3. RANKING (Lectura en Nube) ---
elif choice == "🏆 Ranking":
    st.title("Podio en Vivo 🌟")
    
    if st.button("🔄 Actualizar Ranking ahora"):
        st.rerun()
    
    try:
        # ttl=0 es CRUCIAL para ver los votos de otros al instante
        df_votos = conn.read(worksheet="votos", ttl=0)
        
        if not df_votos.empty:
            ranking = df_votos.groupby("Artista")["Puntos"].mean().sort_values(ascending=False).head(3)
            
            cols = st.columns(3)
            medallas = ["🥇", "🥈", "🥉"]
            
            for i, (artista, puntos) in enumerate(ranking.items()):
                with cols[i]:
                    st.markdown(f"""
                    <div style='text-align:center; padding:10px; border:1px solid #ddd; border-radius:10px; margin-bottom:10px; background-color:white;'>
                        <h1 style='margin:0;'>{medallas[i]}</h1>
                        <h4 style='color:#C0392B; margin:5px 0;'>{artista}</h4>
                        <p style='font-weight:bold; font-size:1.1rem;'>{puntos:.1f} pts</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with st.expander("Ver todos los votos"):
                st.dataframe(df_votos)
        else:
            st.info("Esperando el primer valiente...")
            
    except Exception as e:
        st.error("No se pudieron cargar los datos.")

# --- 4. DEDICATORIAS ---
elif choice == "💌 Dedicatorias":
    st.title("Mensajes 🎂")
    
    @st.dialog("¡Mensaje de Lu! ❤️")
    def popup():
        st.markdown("""
        **¡Gracias por venir! 🥹🫶**
        
        Me habéis hecho muy feliz.
        *Recuerdo desbloqueado 💛🎤*
        """)
        if st.button("Cerrar"):
            st.rerun()

    with st.form("dedicatoria_form", clear_on_submit=True):
        nombre = st.text_input("Nombre:")
        msj = st.text_area("Mensaje:")
        if st.form_submit_button("Enviar 💌") and msj:
            try:
                df_msj = conn.read(worksheet="dedicatorias", ttl=0)
                nuevo = pd.DataFrame([{"Nombre": nombre if nombre else "Anónimo", "Mensaje": msj}])
                df_final = pd.concat([df_msj, nuevo], ignore_index=True)
                conn.update(worksheet="dedicatorias", data=df_final)
                popup()
            except:
                st.error("Error de conexión.")

    st.write("---")
    try:
        df_ver = conn.read(worksheet="dedicatorias", ttl=0)
        if not df_ver.empty:
            for _, row in df_ver.iloc[::-1].iterrows():
                st.info(f"**{row['Nombre']}**: {row['Mensaje']}")
    except:
        pass
