import streamlit as st
import pandas as pd
from datetime import datetime
import time
import random
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Lu's Karaoke Party", 
    page_icon="🎤", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CSS: MODO OSCURO ARREGLADO (VERSIÓN CORREGIDA) ---
def local_css():
    st.markdown("""
        <style>
        /* 1. FONDO PRINCIPAL BLANCO */
        .stApp {
            background-color: #FFFFFF;
        }

        /* 2. MENÚ LATERAL (SIDEBAR) */
        section[data-testid="stSidebar"] {
            background-color: #F0F2F6; /* Gris muy clarito */
        }
        /* Texto del menú lateral en negro */
        section[data-testid="stSidebar"] * {
            color: #000000 !important;
        }

        /* 3. TEXTOS GENERALES EN NEGRO */
        h1, h2, h3, h4, h5, h6, p, li, span, label { 
            color: #000000 !important; 
        }

        /* 4. INPUTS (Cajas de texto) */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
            background-color: #FDF2F2; 
            color: #000000 !important;
            font-size: 16px !important; 
        }
        
        /* 5. BOTONES DEL MENÚ LATERAL */
        .stRadio > div {
            background-color: #F8F9FA;
            padding: 10px;
            border-radius: 10px;
        }

        /* 6. BOTONES DE ACCIÓN (ROJOS CON TEXTO BLANCO) */
        div.stButton > button {
            width: 100%;
            background-color: #C0392B !important; /* Rojo */
            border-radius: 15px;
            border: none;
            min-height: 50px;
            font-size: 18px !important;
            margin-top: 10px;
        }
        
        /* FUERZA BRUTA PARA EL TEXTO DEL BOTÓN */
        div.stButton > button p, div.stButton > button div, div.stButton > button span {
            color: #FFFFFF !important;
            font-weight: bold !important;
        }

        /* 7. AJUSTES MÓVIL */
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

# --- MENÚ LATERAL ---
menu = ["🏠 Bienvenida", "🎤 Votaciones", "🏆 Ranking", "💌 Dedicatorias", "🎲 Ruleta"]
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
    4. 🎲 Juega a la **Ruleta** si no sabes qué cantar.
    """)

# ==========================================
# 2. VOTACIONES (CON TUS CRITERIOS + FIX DE SUMA)
# ==========================================
elif choice == "🎤 Votaciones":
    st.title("Puntúa el Show 📊")
    
    with st.form("voting_form", clear_on_submit=True):
        st.write("👤 **¿Quién canta?**")
        nombre_artista = st.text_input("Nombre", placeholder="Ej: Juan...", label_visibility="collapsed")
        
        st.write("---")
        # --- TUS CRITERIOS PERSONALIZADOS ---
        c1 = st.slider("⭐ Actitud y Energía", 0, 5, 3)
        c2 = st.slider("🎭 Interpretación Dramática", 0, 5, 3)
        c3 = st.slider("🎉 Show y Escena", 0, 5, 3)
        c4 = st.slider("🔄 Originalidad en la elección de la canción", 0, 5, 3)
        c5 = st.slider("👯 Conexión con el Grupo", 0, 5, 3)
        
        if st.form_submit_button("¡ENVIAR VOTO! 🚀"):
            if nombre_artista:
                try:
                    df = conn.read("votos")
                    
                    # Sumamos los 5 criterios
                    pts = c1 + c2 + c3 + c4 + c5
                    
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
# 4. DEDICATORIAS
# ==========================================
elif choice == "💌 Dedicatorias":
    st.title("Mensajes 💌")
    
    @st.dialog("¡Mensaje Recibido! ❤️")
    def popup_agradecimiento():
        # TU MENSAJE PERSONALIZADO
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

# ==========================================
# 5. RULETA DEL PÁNICO (ACTUALIZADA 2000s)
# ==========================================
elif choice == "🎲 Ruleta":
    st.title("🎲 La Ruleta del Pánico")
    st.markdown("¿No sabes qué cantar? ¿O eres valiente? **¡Deja que el destino decida!**")
    
    # Listas actualizadas con más 2000s y desafíos interactivos
    canciones = [
        # --- CLÁSICOS ESPAÑOLES & FIESTA ---
        "Mi Gran Noche - Raphael", "Como una ola - Rocío Jurado", 
        "Sobreviviré - Mónica Naranjo", "Libre - Nino Bravo", 
        "A quién le importa - Alaska", "La Macarena - Los del Río",
        "Bailando - Enrique Iglesias", "Corazón Partío - Alejandro Sanz",
        
        # --- 2000s ESPAÑA & VERBENA ---
        "Ave María - David Bisbal", "Caminando por la vida - Melendi",
        "Zapatillas - El Canto del Loco", "Por la raja de tu falda - Estopa",
        "Marta, Sebas, Guille y los demás - Amaral", "Princesas - Pereza",
        "Aserejé - Las Ketchup", "Torero - Chayanne",
        "Yo quiero bailar - Sonia y Selena", "Colgando en tus manos - Carlos Baute",
        "Estoy Aquí - Shakira", "Clavado en un bar - Maná", "Lloraré las penas - David Bisbal",
        
        # --- DIVAS & POP INTERNACIONAL (Nostalgia 90s/00s) ---
        "Love Story - Taylor Swift", "The Best of Both Worlds - Hannah Montana", 
        "Party in the U.S.A. - Miley Cyrus", "Wannabe - Spice Girls", 
        "Baby One More Time - Britney Spears", "I Want It That Way - Backstreet Boys", 
        "It's Raining Men - The Weather Girls",
        
        # --- DISNEY & HIGH SCHOOL MUSICAL ---
        "Un Mundo Ideal - Aladdin", "Bajo del Mar - La Sirenita",
        "Breaking Free - High School Musical", "Suéltalo (Let It Go) - Frozen",
        "El Ciclo de la Vida - El Rey León",
        
        # --- HIMNOS INTERNACIONALES ---
        "Livin' on a Prayer - Bon Jovi", "Bohemian Rhapsody - Queen",
        "Mamma Mia - ABBA", "You're the One That I Want - Grease",
        "I Will Survive - Gloria Gaynor"
    ]
    
    desafios = [
        "Normal (¡Te libras!)", "Normal (¡Te libras!)", # Doble probabilidad de normal
        "🎤 Imitando a Shakira", "🤖 Estilo Robot", 
        "😫 Con mucho drama/llorando", "🕺 Bailando sin parar", 
        "👀 Sin mirar la pantalla", "👫 A dúo con el cumpleañero/a",
        "🥴 Como si estuvieras borracho/a", "🐭 Con voz de pito",
        # DESAFÍOS NUEVOS
        "🅰️ Cantar todo SOLO con la vocal 'A'", "🅾️ Cantar todo SOLO con la vocal 'O'",
        "🤝 Convence a alguien que no conozcas para que suba contigo a cantar",
        "🏋️ Cantar haciendo sentadillas", "🧘 Cantar tumbado en el suelo",
        "🤐 Cantar sin mover los labios", "👺 Estilo Ópera / Pavarotti"
    ]

    if st.button("🎰 TIRAR DE LA RULETA 🎰"):
        # 1. Creamos un contenedor vacío
        ruleta_placeholder = st.empty()
        
        # 2. Mostramos el GIF de la ruleta girando
        ruleta_placeholder.image("https://media1.tenor.com/m/K3jT73UVZhEAAAAC/dog-spinning.gif", use_container_width=True)
        
        # 3. Esperamos 3 segundos (Suspenso...)
        time.sleep(3)
        
        # 4. Borramos el GIF
        ruleta_placeholder.empty()
        
        # 5. Mostramos el resultado
        cancion_elegida = random.choice(canciones)
        desafio_elegido = random.choice(desafios)
        
        st.markdown("---")
        st.markdown(f"### 🎵 Tu canción es: **{cancion_elegida}**")
        
        if "Normal" in desafio_elegido:
            st.success(f"😅 **Modo:** {desafio_elegido}")
        else:
            st.error(f"😈 **Desafío:** {desafio_elegido}")
            st.caption("¡Si no cumples el desafío, chupito!")
