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

# --- CSS: MODO OSCURO ARREGLADO Y MÓVIL ---
def local_css():
    st.markdown("""
        <style>
        /* Fondo blanco y texto negro FORZADO */
        .stApp { background-color: #FFFFFF; color: #000000; }
        h1, h2, h3, h4, h5, h6, p, li, span, div, label { color: #000000 !important; }
        
        /* Inputs (evitar zoom en iPhone) */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
            background-color: #FDF2F2; 
            color: #000000 !important;
            font-size: 16px !important; 
        }
        
        /* Botones del menú lateral (Radio) */
        .stRadio > div {
            background-color: #F8F9FA;
            padding: 10px;
            border-radius: 10px;
        }
        
        /* Botones de acción (Enviar) */
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
        
        /* Ajustes móvil */
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
                pk = self.config["private_key"]
                self.config["private_key"] = pk.replace("\\n", "\n")

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Credenciales en líneas separadas para seguridad al copiar
            creds = Credentials.from_service_account_info(
                self.config, 
                scopes=scopes
            )
            
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
            header = data.columns.values.tolist()
            valores = data.values.tolist()
            ws.update([header] + valores)
        except Exception as e:
            st.error(f"Error guardando: {e}")

try:
    conn = ConectorManual()
except:
    pass

# --- MENÚ LATERAL (RESTAURADO A RADIO BUTTONS) ---
menu = ["🏠 Bienvenida", "🎤 Votaciones", "🏆 Ranking", "💌 Dedicatorias"]
choice = st.sidebar.radio("Navegación:", menu)

# ==========================================
# 1. BIENVENIDA
# ==========================================
if choice == "🏠 Bienvenida":
    st.markdown("<h1 style='text-align: center;'>Lu's 30th Birthday 🎂</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>🎤 Karaoke Edition 🎤</h3>", unsafe_allow_html=True)
    st.image("https://media.giphy.com/media/l4KibWpBGWchSqCRy/giphy.gif", use_container_width=True)
    
    st.info("👇 Usa el menú de la izquierda.")
    st.markdown("""
    **Instrucciones:**
    1. ⭐ Ve a **Votaciones** para puntuar.
    2. 🏆 Mira el **Ranking** en tiempo real.
    3. 💌 Deja un mensaje en **Dedicatorias**.
    """)

# ==========================================
# 2. VOTACIONES (CRITERIOS RESTAURADOS)
# ==========================================
elif choice == "🎤 Votaciones":
    st.title("Puntúa el Show 📊")
    
    with st.form("voting_form", clear_on_submit=True):
        st.write("👤 **¿Quién canta?**")
        nombre_artista = st.text_input("Nombre", placeholder="Ej: Juan...", label_visibility="collapsed")
        
        st.write("---")
        # --- LOS 5 CRITERIOS ORIGINALES ---
        c1 = st.slider("⭐ Actitud y Energía", 0, 5, 3)
        c2 = st.slider("🎭 Interpretación Dramática", 0, 5, 3)
        c3 = st.slider("🎉 Show y Escena", 0, 5, 3)
        c4 = st.slider("🔄 Originalidad en la elección de la canción", 0, 5, 3)
        c5 = st.slider("👯 Conexión con el Grupo", 0, 5, 3)
        
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
                    st.success("✅ Voto guardado correctamente")
                except:
                    st.error("Error de conexión")
            else:
                st.warning("⚠️ Escribe el nombre del cantante")

# ==========================================
# 3. RANKING
# ==========================================
elif choice == "🏆 Ranking":
    st.title("Ranking 🏆")
    try:
        df = conn.read("votos")
        if not df.empty and 'Artista' in df.columns:
            
            # Lógica segura
            agrupado = df.groupby("Artista")["Puntos"].sum()
            top = agrupado.sort_values(ascending=False).head(3)
            
            st.write("### 🥇 Podio Actual")
            colores = ["#FFD700", "#C0C0C0", "#CD7F32"]
            medallas = ["🥇 PRIMERO", "🥈 SEGUNDO", "🥉 TERCERO"]
            
            i = 0
            for artista, puntos in top.items():
                if i < 3:
                    estilo = f"background-color: {colores[i]}20; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 2px solid {colores[i]}; text-align: center;"
                    
                    html_card = f"""
                    <div style="{estilo}">
                        <h3 style="margin:0; color:black;">{medallas[i]}</h3>
                        <h2 style="margin:5px 0; font-weight:800; color:black;">{artista}</h2>
                        <p style="margin:0; font-size: 1.2em; color:black;">{int(puntos)} Puntos</p>
                    </div>
                    """
                    st.markdown(html_card, unsafe_allow_html=True)
                    i += 1
            
            st.write("---")
            st.write("📊 **Historial:**")
            st.dataframe(df.tail(5)[["Artista", "Puntos"]], use_container_width=True, hide_index=True)
        else:
            st.info("Aún no hay votos registrados.")
    except Exception as e:
        st.error(f"Error cargando ranking: {e}")

# ==========================================
# 4. DEDICATORIAS (POP-UP RESTAURADO)
# ==========================================
elif choice == "💌 Dedicatorias":
    st.title("Mensajes 💌")
    
    # --- POP-UP RESTAURADO ---
    @st.dialog("¡Mensaje Recibido! ❤️")
    def popup_agradecimiento():
        st.write("Gracias por venir a mis 30. ¡Sin ti no es lo mismo! 💛🧸")
        st.balloons()
        if st.button("Volver a la fiesta 💃"):
            st.rerun()

    with st.form("msg_form", clear_on_submit=True):
        nom = st.text_input("Tu nombre:")
        msg = st.text_area("Mensaje para Lu:")
        
        if st.form_submit_button("ENVIAR MENSAJE ❤️"):
            if msg:
                try:
                    df = conn.read("dedicatorias")
                    nuevo = pd.DataFrame([{"Nombre": nom if nom else "Anónimo", "Mensaje": msg}])
                    conn.update("dedicatorias", pd.concat([df, nuevo], ignore_index=True))
                    
                    # Lanzamos el pop-up
                    popup_agradecimiento()
                    
                except:
                    st.error("Error al enviar")

    st.write("---")
    try:
        df = conn.read("dedicatorias")
        if not df.empty:
            for _, r in df.iloc[::-1].iterrows():
                estilo_msg = "background-color:#FFF; border-left: 5px solid #C0392B; padding: 10px; margin-bottom: 10px; border-radius: 5px; box-shadow: 1px 1px 3px rgba(0,0,0,0.1);"
                
                st.markdown(f"""
                <div style="{estilo_msg}">
                    <strong>{r['Nombre']}</strong> dice:<br>
                    <span style="color:#555;">{r['Mensaje']}</span>
                </div>
                """, unsafe_allow_html=True)
    except: pass
