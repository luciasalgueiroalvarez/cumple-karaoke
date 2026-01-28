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
                    # AQUÍ ESTABA EL ERROR ANTES, AHORA ESTÁ CORREGIDO:
                    df_actual = conn.read(worksheet="votos", ttl=0)
                    
                    puntos_totales = c1 + c2 + c3 + c4 + c5
                    nueva_fila = pd.DataFrame([{
                        "Artista": nombre_artista.strip().upper(),
                        "Puntos": puntos_totales,
                        "Hora": datetime.now().strftime("%H:%M:%S")
                    }])
                    
                    df_actualizado = pd.concat([df_actual, nueva_fila], ignore_index=True)
                    conn.update(worksheet="votos", data=df_actualizado)
                    
                    # Efectos visuales
                    barra_carga = st.progress(0, text="Guardando voto...")
                    for i in range(100):
                        time.sleep(0.005) # Rápido
                        barra_carga.progress(i + 1)
                    
                    barra_carga.empty()
                    st.toast(f'¡Voto registrado para {nombre_artista}! 🗳️', icon='✅')
                    st.balloons()

                except Exception as e:
                    st.error("Error conectando.")
                    st.write(e)
            else:
                st.warning("⚠️ ¡Falta el nombre del artista!")

# ==========================================
# --- 3. RANKING ---
# ==========================================
elif choice == "🏆 Ranking":
    st.title("Podio de Estrellas 🌟")
    
    try:
        df_votos = conn.read(worksheet="votos", ttl=0)
        
        # Estadísticas Rápidas
        st.markdown("### 📊 En tiempo real")
        if not df_votos.empty:
            total_votos = len(df_votos)
            lider = df_votos['Artista'].mode()[0] 
            ultimo_voto = df_votos['Hora'].iloc[-1]
        else:
            total_votos = 0; lider = "---"; ultimo_voto = "---"

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total Votos", total_votos, "🔥")
        col_b.metric("Líder", lider, "🏆")
        col_c.metric("Última Hora", str(ultimo_voto)[:5], "🕒")

        st.divider()

        # Tabla de Ganadores con Medallas
        if not df_votos.empty:
            ranking = df_votos.groupby("Artista")["Puntos"].mean().sort_values(ascending=False).head(3)
            cols = st.columns(3)
            medallas = ["🥇", "🥈", "🥉"]
            
            for i, (artista, puntos) in enumerate(ranking.items()):
                with cols[i]:
                    st.markdown(f"<h1 style='text-align: center; margin-bottom:0;'>{medallas[i]}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='margin-top:0;'>{artista}</h4>", unsafe_allow_html=True)
                    st.metric("Puntos Media", f"{puntos:.1f}")
        else:
            st.info("Aún no hay cantantes... ¡Sé el primero!")
            
    except Exception as e:
        st.error("Error cargando ranking.")

# ==========================================
# --- 4. DEDICATORIAS ---
# ==========================================
elif choice == "💌 Dedicatorias":
    st.title("Mensajes para Lu 🎂")

    @st.dialog("¡Gracias! ❤️")
    def popup_agradecimiento():
        st.markdown("Gracias por venir y por tus palabras. ¡A seguir con la fiesta!")
        if st.button("Cerrar"):
            st.rerun()

    with st.form("dedicatoria_form", clear_on_submit=True):
        nombre_invitado = st.text_input("Tu nombre (opcional):")
        mensaje_texto = st.text_area("Tu mensaje para la cumpleañera:")
        
        if st.form_submit_button("Enviar 💌"):
            if mensaje_texto:
                try:
                    df_msjs = conn.read(worksheet="dedicatorias", ttl=0)
                    nuevo_msj = pd.DataFrame([{
                        "Nombre": nombre_invitado if nombre_invitado else "Anónimo", 
                        "Mensaje": mensaje_texto
                    }])
                    df_final = pd.concat([df_msjs, nuevo_msj], ignore_index=True)
                    conn.update(worksheet="dedicatorias", data=df_final)
                    popup_agradecimiento()
                except Exception as e:
                    st.error("Error guardando mensaje.")
            else:
                st.warning("El mensaje está vacío.")

    st.markdown("---")
    st.write("### Muro de Love 💛:")
    try:
        mensajes_db = conn.read(worksheet="dedicatorias", ttl=0)
        if not mensajes_db.empty:
            for _, fila in mensajes_db.iloc[::-1].iterrows():
                st.info(f"**{fila['Nombre']}**: {fila['Mensaje']}")
    except:
        pass
