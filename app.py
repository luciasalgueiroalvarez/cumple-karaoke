import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time # Importamos time aquí arriba para evitar errores

# --- MAQUILLAJE VISUAL (CSS) ---
def local_css():
    st.markdown("""
        <style>
        /* Fondo de la aplicación con un degradado suave */
        .stApp {
            background-image: linear-gradient(to top, #dfe9f3 0%, white 100%);
        }
        
        /* Títulos centrados y con color */
        h1 {
            text-align: center;
            color: #FF4B4B;
            font-family: 'Helvetica', sans-serif;
            font-weight: 800;
        }
        h2, h3 {
            text-align: center;
            color: #333;
        }

        /* Botones personalizados */
        div.stButton > button {
            width: 100%;
            background-color: #FF4B4B;
            color: white;
            border-radius: 10px;
            border: none;
            font-weight: bold;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            background-color: #ff2b2b;
            transform: scale(1.02);
        }
        
        /* Cajas de métricas (si usamos alguna) más bonitas */
        div[data-testid="metric-container"] {
            background-color: #ffffff;
            border: 1px solid #eee;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

local_css() # Llamamos a la función para pintar la web

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Lu's Karaoke Party", 
    page_icon="🎤", 
    layout="centered"
)

# --- ESTILO CSS ACTUALIZADO (Fondo Blanco y Sin Adornos) ---
st.markdown("""
    <style>
    /* Fondo blanco en toda la app */
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
        height: 3em;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
    }
    /* Ajuste de inputs para que se vean bien en fondo blanco */
    .stTextInput>div>div>input {
        background-color: #FDF2F2;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN MANUAL A GOOGLE SHEETS (COMPATIBLE CON TUS SECRETS) ---
import gspread
from google.oauth2.service_account import Credentials

class ConectorManual:
    def __init__(self):
        try:
            # 1. Cargamos todos los datos del archivo secrets
            self.config = dict(st.secrets["connections"]["gsheets"])

            # 2. Aseguramos que la clave privada tenga los saltos de línea correctos
            if "private_key" in self.config:
                self.config["private_key"] = self.config["private_key"].replace("\\n", "\n")

            # 3. Autenticación directa con Google
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Creamos las credenciales usando el diccionario limpio
            creds = Credentials.from_service_account_info(self.config, scopes=scopes)
            self.client = gspread.authorize(creds)
            
            # 4. Obtenemos la URL de la hoja
            self.url = self.config["spreadsheet"]
            
        except Exception as e:
            st.error(f"Error grave conectando: {e}")

    # Función para LEER datos
    def read(self, worksheet="votos", ttl=0):
        try:
            sh = self.client.open_by_url(self.url)
            ws = sh.worksheet(worksheet)
            return pd.DataFrame(ws.get_all_records())
        except Exception as e:
            # st.error(f"Error leyendo la hoja '{worksheet}': {e}") # Comentado para no ensuciar si está vacía
            return pd.DataFrame()

    # Función para GUARDAR datos
    def update(self, worksheet, data):
        try:
            sh = self.client.open_by_url(self.url)
            ws = sh.worksheet(worksheet)
            ws.clear()
            # gspread necesita que los datos sean una lista de listas
            ws.update([data.columns.values.tolist()] + data.values.tolist())
        except Exception as e:
            st.error(f"Error guardando datos: {e}")

# Iniciamos la conexión
try:
    conn = ConectorManual()
except Exception as e:
    st.error(f"No se pudo iniciar el conector: {e}")

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
        nombre_artista = st.text_input("👤 ¿Quién está en el escenario?", placeholder="Escribe su nombre...")
        
        st.write("---")
        c1 = st.slider("⭐ Actitud y Energía", 0, 5, 3)
        c2 = st.slider("🎭 Interpretación Dramática", 0, 5, 3)
        c3 = st.slider("🎉 Show y Escena", 0, 5, 3)
        c4 = st.slider("🔄 Originalidad", 0, 5, 3)
        c5 = st.slider("👯 Conexión con el Grupo", 0, 5, 3)
        
        submitted = st.form_submit_button("Enviar voto 🚀 🎤 🎶")
        
        if submitted:
            if nombre_artista:
                try:
                    # Leemos la pestaña 'votos'
                    df_actual = conn.read(worksheet="votos", ttl=0)
                    
                    puntos_totales = c1 + c2 + c3 + c4 + c5
                    nueva_fila = pd.DataFrame([{
                        "Artista": nombre_artista.strip().upper(),
                        "Puntos": puntos_totales,
                        "Hora": datetime.now().strftime("%H:%M:%S")
                    }])
                    
                    df_actualizado = pd.concat([df_actual, nueva_fila], ignore_index=True)
                    conn.update(worksheet="votos", data=df_actualizado)
                    
                    # --- EFECTOS VISUALES ---
                    
                    # 1. Barra de carga
                    barra_carga = st.progress(0, text="Guardando voto en la urna...")
                    for i in range(100):
                        time.sleep(0.01) # Pequeña pausa
                        barra_carga.progress(i + 1)
                    
                    # 2. Notificación y Globos
                    barra_carga.empty()
                    st.toast(f'¡Voto registrado para {nombre_artista}! 🗳️', icon='✅')
                    st.balloons()

                except Exception as e:
                    st.error("Error al conectar con la base de datos.")
                    st.info("Asegúrate de que la pestaña del Excel se llame exactamente 'votos'")
                    st.write(f"Detalle técnico: {e}")
            else:
                st.warning("Por favor, pon el nombre del artista.")

# --- 3. RANKING ---
elif choice == "🏆 Ranking":
    st.title("Podio de Estrellas (o Estrellados) 🌟")
    
    try:
        df_votos = conn.read(worksheet="votos", ttl=0)
        
        # --- SECCIÓN DE ESTADÍSTICAS (INTEGRADA AQUÍ) ---
        st.markdown("### 📊 Estadísticas en tiempo real")
        
        # Calculamos algunos datos extra solo si hay datos
        if not df_votos.empty:
            total_votos = len(df_votos)
            # Usamos "Artista" en lugar de "votado_a" porque así lo guardamos en el Excel
            lider = df_votos['Artista'].mode()[0] 
            ultimo_voto = df_votos['Hora'].iloc[-1]
        else:
            total_votos = 0
            lider = "Nadie aún"
            ultimo_voto = "---"

        # Mostramos 3 tarjetas bonitas en fila
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total Votos", total_votos, "🔥 on fire")
        col_b.metric("Líder Actual", lider, "🏆 ganando")
        col_c.metric("Último Voto", str(ultimo_voto), "🕒 hora")

        st.divider() # Una línea separadora elegante
        # -----------------------------------------------

        if not df_votos.empty:
            # Calculamos la media por artista
            ranking = df_votos.groupby("Artista")["Puntos"].mean().sort_values(ascending=False).head(3)
            
            cols = st.columns(3)
            medallas = ["🥇", "🥈", "🥉"]
            
            for i, (artista, puntos) in enumerate(ranking.items()):
                with cols[i]:
                    st.markdown(f"<h1 style='text-align: center;'>{medallas[i]}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-weight: bold;'>{artista}</p>", unsafe_allow_html=True)
                    st.metric("Media", f"{puntos:.1f}")
        else:
            st.info("Aún no hay votos registrados.")
    except Exception as e:
        st.error("No se pudo cargar el ranking.")
        st.write(f"Error: {e}")

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
        nombre_invitado = st.text_input("Tu nombre (opcional):")
        mensaje_texto = st.text_area("Tu mensaje para la cumpleañera:")
        
        if st.form_submit_button("Enviar Mensaje 💌"):
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
                    st.error("No se pudo guardar el mensaje.")
                    st.write(f"Detalle técnico: {e}")
            else:
                st.warning("Escribe algo antes de enviar.")

    st.markdown("---")
    st.write("### Muro de recuerdos:")
    try:
        mensajes_db = conn.read(worksheet="dedicatorias", ttl=0)
        if not mensajes_db.empty:
            for _, fila in mensajes_db.iloc[::-1].iterrows():
                st.info(f"**{fila['Nombre']}**: {fila['Mensaje']}")
    except:
        pass
