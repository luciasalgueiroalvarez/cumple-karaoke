import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time 

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Lu's Karaoke Party", 
    page_icon="🎤", 
    layout="centered"
)

# --- CSS: ESTILO LIMPIO (FONDO BLANCO) ---
def local_css():
    st.markdown("""
        <style>
        /* Fondo blanco puro */
        .stApp {
            background-color: #FFFFFF;
        }
        
        /* Títulos en Rojo */
        h1 {
            text-align: center;
            color: #C0392B !important;
            font-family: 'Helvetica', sans-serif;
            font-weight: 800;
        }
        h2, h3, h4 {
            text-align: center;
            color: #333;
        }

        /* Botones Rojos y Redondos */
        div.stButton > button {
            width: 100%;
            background-color: #C0392B;
            color: white;
            border-radius: 25px;
            border: none;
            font-weight: bold;
            height: 3em;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            background-color: #a93226;
            transform: scale(1.02);
            color: white;
        }
        
        /* Inputs y Cajas de Texto con fondo suave */
        .stTextInput>div>div>input {
            background-color: #FDF2F2;
        }
        
        /* Cajas de métricas (Ranking) */
        div[data-testid="metric-container"] {
            background-color: #F8F9FA;
            border: 1px solid #eee;
            padding: 10px;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

local_css()

# --- CONEXIÓN MANUAL A GOOGLE SHEETS ---
import gspread
from google.oauth2.service_account import Credentials

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
            st.error(f"Error grave conectando: {e}")

    def read(self, worksheet="votos", ttl=0):
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
            st.error(f"Error guardando datos: {e}")

# Iniciamos conexión
try:
    conn = ConectorManual()
except Exception as e:
    st.error(f"No se pudo iniciar el conector: {e}")

# --- MENÚ LATERAL ---
menu = ["🏠 Bienvenida", "🎤 Votar Actuación", "🏆 Ranking", "💌 Dedicatorias"]
choice = st.sidebar.radio("Menú", menu)

# ==========================================
# --- 1. HOME PAGE ---
# ==========================================
if choice == "🏠 Bienvenida":
    st.markdown("<h1 style='font-size: 3em;'>Lu's 30th Birthday 🎂</h1>", unsafe_allow_html=True)
    st.markdown("### 🎤 The Karaoke Edition 🎤")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://media.giphy.com/media/l4KibWpBGWchSqCRy/giphy.gif", use_container_width=True)

    st.write("---")

    st.markdown("""
    ##### ¡Bienvenidos a la fiesta del año! 
    Hoy no se juzga la afinación, se juzga el **ESPECTÁCULO**.
    Usa el menú de la izquierda (o arriba en el móvil) para:
    
    * **Votar:** ¡Sé cruel o generoso!
    * **Ranking:** Mira quién va ganando en tiempo real.
    * **Dedicatorias:** Déjale un mensaje bonito a Lu.
    
    **¡Un chupito corre a cuenta de Lu para calentar motores!** 🥃
    """)

# ==========================================
# --- 2. PÁGINA DE VOTACIONES ---
# ==========================================
elif choice == "🎤 Votar Actuación":
    st.title("Puntúa el Show 📊")
    
    with st.form("voting_form", clear_on_submit=True):
        nombre_artista = st.text_input("👤 ¿Quién está en el escenario?", placeholder="Escribe su nombre...")
        
        st.write("---")
        # Sliders
        c1 = st.slider("⭐ Actitud y Energía", 0, 5, 3)
        c2 = st.slider("🎭 Interpretación Dramática", 0, 5, 3)
        c3 = st.slider("🎉 Show y Escena", 0, 5, 3)
        c4 = st.slider("🔄 Originalidad", 0, 5, 3)
        c5 = st.slider("👯 Conexión con el Grupo", 0, 5, 3)
        
        submitted = st.form_submit_button("Enviar voto 🚀")
        
        if submitted:
            if nombre_artista:
                try:
                    df_actual = conn.read(worksheet="v
