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

# --- CSS: ESTILO RESPONSIVE Y MODO CLARO FORZADO ---
def local_css():
    st.markdown("""
        <style>
        /* =========================================
           1. ESTILOS GLOBALES (Modo Claro Forzado)
           ========================================= */
        .stApp { background-color: #FFFFFF; color: #000000; }
        h1, h2, h3, h4, h5, h6, p, li, span, div { color: #000000 !important; }
        
        /* Inputs y Cajas de texto */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
            background-color: #FDF2F2; 
            color: #000000 !important;
            font-size: 16px !important; /* Evita zoom automático en iPhone */
        }
        
        /* Botones Generales */
        div.stButton > button {
            width: 100%;
            background-color: #C0392B;
            color: white !important;
            border-radius: 15px;
            border: none;
            font-weight: bold;
            min-height: 50px; /* Botón más alto para dedos */
            font-size: 18px !important;
            margin-top: 10px;
        }
        div.stButton > button:hover {
            background-color: #a93226;
            color: white !important;
        }

        /* Contenedores de Métricas (Ranking) */
        div[data-testid="metric-container"] {
            background-color: #F8F9FA;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            color: #000000 !important;
            text-align: center;
        }
        div[data-testid="metric-container"] > label { color: #555 !important; }

        /* =========================================
           2. ESTILOS SOLO PARA MÓVIL (PANTALLAS PEQUEÑAS)
           ========================================= */
        @media only screen and (max-width: 600px) {
            h1 { font-size: 2rem !important; }
            h2 { font-size: 1.5rem !important; }
            img { max-width: 100% !important; }
            .block-container {
                padding-top: 2rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
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

# --- MENÚ LATERAL ---
menu = ["🏠 Bienvenida", "🎤 Votar", "🏆 Ranking", "💌 Dedicatorias"]
choice = st.sidebar.selectbox("¿Qué quieres hacer?", menu)

# ==========================================
# --- 1. HOME PAGE ---
# ==========================================
if choice == "🏠 Bienvenida":
    st.markdown("<h1 style='text-align: center;'>Lu's 30th Birthday 🎂</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>🎤 Karaoke Edition 🎤</h3>", unsafe_allow_html=True)
    
    st.image("https://media.giphy.com/media/l4KibWpBGWchSqCRy/giphy.gif", use_container_width=True)

    st.info("👇 Abre el menú arriba a la izquierda para empezar.")
    st.markdown("""
    **Instrucciones rápidas:**
    1. 🎤 Escucha al artista.
    2. ⭐ Ve a **'Votar'** y puntúalo.
    3. 🏆 Mira el **'Ranking'** para ver quién gana.
    4. 💌 Deja un mensaje en **'Dedicatorias'**.
    """)

# ==========================================
# --- 2. VOTAR ---
# ==========================================
elif choice == "🎤 Votar":
    st.title("Puntúa el Show 📊")
    
    with st.form("voting_form", clear_on_submit=True):
        st.write("👤 **¿Quién canta?**")
        nombre_artista = st.text_input("Nombre", placeholder="Ej: Juan...", label_visibility="collapsed")
        
        st.write("---")
        val_energia = st.slider("⭐ Actitud / Energía", 0, 5, 3)
        val_voz = st.slider("🎭 Show / Drama", 0, 5, 3)
        val_publico = st.slider("👯 Conexión Público", 0, 5, 3)
        
        submitted = st.form_submit_button("¡ENVIAR VOTO! 🚀")
        
        if submitted:
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
                st.warning("⚠️ Escribe el nombre del cantante")

# ==========================================
# --- 3. RANKING ---
# ==========================================
elif choice == "🏆 Ranking":
    st.title("Ranking 🏆")
    try:
        df = conn.read("votos")
        if not df.empty and 'Artista' in df.columns:
            top = df.groupby("Artista")["Puntos"].sum().
