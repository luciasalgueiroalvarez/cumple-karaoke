import streamlit as st
import pandas as pd
from datetime import datetime
import time
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Lu's Karaoke Party", 
    page_icon="🎤", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS: ESTILO MODO CLARO Y MÓVIL ---
def local_css():
    st.markdown("""
        <style>
        /* Forzar modo claro (letras negras sobre fondo blanco) */
        .stApp { background-color: #FFFFFF; color: #000000; }
        h1, h2, h3, h4, h5, h6, p, li, span, div { color: #000000 !important; }
        
        /* Inputs ajustados para iPhone (evita zoom) */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
            background-color: #FDF2F2; 
            color: #000000 !important;
            font-size: 16px !important; 
        }
        
        /* Botones grandes y fáciles de pulsar */
        div.stButton > button {
            width: 100%;
            background-color: #C0392B;
            color: white !important;
            border-radius: 15px;
            border: none;
            font-weight: bold;
            min-height: 50px;
            font-size: 18px !important;
            margin-top: 10px;
        }
        
        /* Cajas del ranking */
        div[data-testid="metric-container"] {
            background-color: #F8F9FA;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 12px;
            color: #000000 !important;
            text-align: center;
        }
        
        /* Ajustes para pantallas pequeñas */
        @media only screen and (max-width: 600px) {
            h1 { font-size: 2rem !important; }
            img { max-width: 100% !important; }
        }
        </style>
    """, unsafe_allow_html=True)

local_css()

# --- CONEXIÓN GOOGLE SHEETS ---
class ConectorManual:
    def __init__(self):
        try:
            self.config = dict(st.secrets["connections"]["gsheets"])
            if "private_key" in self.config:
                self.config["private_key"] = self.config["private_key"].replace("\\n", "\n")

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_info(self.config, scopes=scopes)
            self.client = gspread.authorize(creds)
            self.url = self.config["spreadsheet"]
            
        except Exception as e:
            st.error(f"Error conexión: {e}")

    def read(self, worksheet="votos"):
        try:
            sh = self.client.open_by_url(self.url)
            ws = sh.worksheet(worksheet)
            return pd.DataFrame(ws.get_all_records())
        except:
            return pd.DataFrame()

    def update(self, worksheet, data):
        try:
            sh = self.client.open_by_url(self.url)
            ws = sh.worksheet(worksheet)
            ws.clear()
            ws.update([data.columns.values.tolist()] + data.values.tolist())
        except Exception as e:
            st.error(f"Error guardando: {e}")

try:
    conn = ConectorManual()
except:
    pass

# --- MENÚ ---
menu = ["🏠 Bienvenida", "🎤 Votar", "🏆 Ranking", "💌 Dedicatorias"]
choice = st.sidebar.selectbox("¿Qué quieres hacer?", menu)

# ==========================================
# 1. BIENVENIDA
# ==========================================
if choice == "🏠 Bienvenida":
    st.markdown("<h1 style='text-align: center;'>Lu's 30th Birthday 🎂</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>🎤 Karaoke Edition 🎤</h3>", unsafe_allow_html=True)
    st.image("https://media.giphy.com/media/l4KibWpBGWchSqCRy/giphy.gif", use_container_width=True)
    st.info("👇 Usa el menú de arriba a la izquierda.")
    st.markdown("""
    **Instrucciones:**
    1. ⭐ **Vota** a los cantantes.
    2. 🏆 Mira el **Ranking**.
    3. 💌 Deja una **Dedicatoria**.
    """)

# ==========================================
# 2. VOTAR
# ==========================================
elif choice == "🎤 Votar":
    st.title("Puntúa el Show 📊")
    with st.form("voting_form", clear_on_submit=True):
        st.write("👤 **¿Quién canta?**")
        nombre_artista = st.text_input("Nombre", placeholder="Ej: Juan...", label_visibility="collapsed")
        st.write("---")
        val_energia = st.slider("⭐ Energía", 0, 5, 3)
        val_voz = st.slider("🎭 Show", 0, 5, 3)
        val_publico = st.slider("👯 Público", 0, 5, 3)
        
        if st.form_submit_button("¡ENVIAR VOTO! 🚀"):
            if nombre_artista:
                try:
                    df = conn.read("votos")
                    pts = val_energia + val_voz + val_publico
                    nuevo = pd.DataFrame([{
                        "Artista": nombre_artista.strip().upper(),
                        "Puntos": pts,
                        "Hora": datetime.now().strftime("%H:%M")
                    }])
                    conn.update("votos", pd.concat([df, nuevo], ignore_index=True))
                    st.balloons()
                    st.success("✅ Voto guardado")
                except:
                    st.error("Error de conexión")
            else:
                st.warning("⚠️ Escribe el nombre")

# ==========================================
# 3. RANKING (Corregido)
# ==========================================
elif choice == "🏆 Ranking":
    st.title("Ranking 🏆")
    try:
        df = conn.read("votos")
        if not df.empty and 'Artista' in df.columns:
            
            # --- AQUÍ ESTABA EL ERROR: LO HE DIVIDIDO EN DOS PASOS ---
            # Paso 1: Sumar puntos por artista
            agrupado = df.groupby("Artista")["Puntos"].sum()
            # Paso 2: Ordenar y coger los 3 mejores
            top = agrupado.sort_values(ascending=False).head(3)
            
            st.write("### 🥇 Podio Actual")
            medallas = ["🥇 PRIMERO", "🥈 SEGUNDO", "🥉 TERCERO"]
            colores = ["#FFD700", "#C0C0C0", "#CD7F32"]
            
            i = 0
            for artista, puntos in top.items():
                if i < 3:
                    with st.container():
                        st.markdown(f"""
                        <div style="background-color: {colores[i]}20; padding: 10px; border-radius: 10px; margin-bottom: 10px; border: 2px solid {colores[i]};">
                            <h3 style="margin:0; text-align:center;">{medallas[i]}</h3>
                            <h
