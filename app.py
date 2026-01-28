import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- IMPORTANTE: LIBRERÍA DE IMÁGENES ---
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    st.error("⚠️ Error: No se encuentra la librería 'Pillow'. Verifica requirements.txt")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Lu's Karaoke Party", 
    page_icon="🎤", 
    layout="centered"
)

# --- CSS: ESTILO LIMPIO ---
def local_css():
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF; }
        
        h1 { text-align: center; color: #C0392B !important; font-family: 'Helvetica', sans-serif; font-weight: 800; }
        h2, h3, h4 { text-align: center; color: #333; }

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
        
        .stTextInput>div>div>input { background-color: #FDF2F2; }
        
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
menu = ["🏠 Bienvenida", "📸 Fotomatón", "🎤 Votar Actuación", "🏆 Ranking", "💌 Dedicatorias"]
choice = st.sidebar.radio("Menú", menu)

# ==========================================
# --- 1. HOME PAGE ---
# ==========================================
if choice == "🏠 Bienvenida":
    st.markdown("<h1 style='font-size: 3em;'>Lu's 30th Birthday 🎂</h1>", unsafe_allow_html=True)
    st.markdown("### 🎤 Karaoke Edition 🎤")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://media.giphy.com/media/l4KibWpBGWchSqCRy/giphy.gif", use_container_width=True)

    st.write("---")

    st.markdown("""
    ##### ¡Bienvenidos a la fiesta del año! 
    Hoy no se juzga la voz, se juzga el **ESPECTÁCULO**.
    Usa el menú de la izquierda para:
    
    * **Fotomatón:** Hazte un selfie y súbelo a Instagram 😘
    * **Votar:** ¡Sé cruel o generoso! Tú sabrás si quieres ganarte algún enemigo más.
    * **Ranking:** Mira quién va ganando en tiempo real.
    * **Dedicatorias:** Déjale un mensaje bonito a Lu.
    
    **¡Un chupito corre a cuenta de Lu para calentar motores!** 🍹
    """)

# ==========================================
# --- 2. FOTOMATÓN (CON FILTRO TIPO INSTAGRAM) ---
# ==========================================
elif choice == "📸 Fotomatón":
    st.title("📸 El Espejo Mágico")
    st.markdown("¡Hazte un selfie! Le pondremos un marco de la fiesta automáticamente.")
    
    # Input de cámara
    imagen_input = st.camera_input("Sonríe... 3, 2, 1 📸")
    
    if imagen_input:
        # --- PROCESO DE EDICIÓN DE IMAGEN (FILTRO) ---
        with st.spinner("Aplicando filtro de fiesta... ✨"):
            try:
                # 1. Abrimos la imagen con Pillow
                img = Image.open(imagen_input)
                width, height = img.size
                
                # 2. Preparamos el "lienzo"
                img = img.convert("RGBA")
                overlay = Image.new("RGBA", img.size, (0,0,0,0))
                draw = ImageDraw.Draw(overlay)
                
                # Configuración del banner
                banner_height = 80
                banner_color = (0, 0, 0, 180) # Negro transparente
                
                # 3. Dibujamos la franja negra abajo
                draw.rectangle(
                    [(0, height - banner_height), (width, height)],
                    fill=banner_color
                )
                
                # 4. Configuramos el texto
                texto_filtro = "LU'S 30TH BIRTHDAY PARTY 🎤"
                
                # Intentamos cargar fuentes
                try:
                    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
                except:
                    font = ImageFont.load_default()

                # Calcular posición texto
                try:
                    text_bbox = draw.textbbox((0, 0), texto_filtro, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                except:
                    text_width, text_height = width / 2, 20
                    
                text_x = (width - text_width) / 2
                text_y = height - (banner_height / 2) - (text_height / 2) - 5

                # 5. Dibujamos el texto
                draw.text((text_x, text_y), texto_filtro, font=font, fill="white")
                
                # 6. Fusionamos
                img_final = Image.alpha_composite(img, overlay)
                
                st.success("¡Fotaza! ✨")
                st.image(img_final, use_container_width=True)
                st.info("💡 **Tip:** Mantén pulsada la foto para guardarla.")
                
            except Exception as e:
                st.error(f"Error aplicando el filtro: {e}")
                st.image(imagen_input)    

# ==========================================
# --- 3. PÁGINA DE VOTACIONES ---
# ==========================================
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
        
        submitted = st.form_submit_button("Enviar voto 🚀")
        
        if submitted:
            if nombre_artista:
                try:
                    df_actual = conn.read(worksheet="votos", ttl=0)
                    
                    puntos_totales = c1 + c2 + c3 + c4 + c5
                    nueva_fila = pd.DataFrame([{
                        "Artista": nombre_artista.strip().upper(),
                        "Puntos": puntos_totales,
                        "Hora": datetime.now().strftime("%H:%M:%S")
                    }])
                    
                    df_actualizado = pd.concat([df_actual, nueva_fila], ignore_index=True)
                    conn.update(worksheet="votos", data=df_actualizado)
                    
                    st.balloons()
                    st.success(f"¡Voto registrado para {nombre_artista}!")

                except Exception as e:
                    st.error("Error conectando.")
                    st.write(e)
            else:
                st.warning("⚠️ ¡Falta el nombre del artista!")

# ==========================================
# --- 4. RANKING ---
# ==========================================
elif choice == "🏆 Ranking":
    st.title("Podio de Estrellas 🌟")
    
    try:
        df_votos = conn.read(worksheet="votos", ttl=0)
        
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
        st.error(f"Error cargando ranking: {e}")

# ==========================================
# --- 5. DEDICATORIAS ---
# ==========================================
elif choice == "💌 Dedicatorias":
    st.title("Mensajes para Lu 🎂")

    @st.dialog("¡Gracias! ❤️")
    def popup_agradecimiento():
        st.markdown("""
        **Gracias de corazón por venir a celebrar los 30 conmigo 🧸💖**
        Está siendo una noche increíble. Gracias por darlo todo. 
        Sin ti no es lo mismo 💖🎤
        """)
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
    st.write("### Muro de amor 💛:")
    try:
        mensajes_db = conn.read(worksheet="dedicatorias", ttl=0)
        if not mensajes_db.empty:
            for _, fila in mensajes_db.iloc[::-1].iterrows():
                st.info(f"**{fila['Nombre']}**: {fila['Mensaje']}")
    except:
        pass
