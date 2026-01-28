import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- INTENTO DE IMPORTAR PILLOW ---
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    st.warning("Pillow no instalado correctamente, el fotomaton no tendrá filtro.")

st.set_page_config(page_title="Karaoke Party", layout="centered")

# --- CONEXION ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("Error conectando a Google Sheets. Revisa secrets.toml")

# --- MENU SIN EMOJIS EN LA LOGICA ---
# Usamos nombres simples para evitar errores de caracteres ocultos
opcion = st.sidebar.radio("Menu", ["Inicio", "Fotomaton", "Votar", "Ranking", "Mensajes"])

# 1. INICIO
if opcion == "Inicio":
    st.title("Lu's 30th Birthday")
    st.write("Bienvenido a la fiesta.")
    st.write("Usa el menú de la izquierda.")

# 2. FOTOMATON
elif opcion == "Fotomaton":
    st.header("Fotomaton")
    foto = st.camera_input("Foto")
    if foto:
        try:
            img = Image.open(foto)
            st.image(img, caption="Tu foto")
        except:
            st.error("Error procesando imagen")

# 3. VOTAR
elif opcion == "Votar":
    st.header("Votar")
    with st.form("voto"):
        artista = st.text_input("Nombre del Artista")
        puntos = st.slider("Puntos", 0, 10, 5)
        if st.form_submit_button("Enviar"):
            try:
                # Leemos datos actuales
                df = conn.read(worksheet="votos")
                # Creamos nueva fila
                nuevo = pd.DataFrame([{"Artista": artista, "Puntos": puntos, "Hora": datetime.now().strftime("%H:%M")}])
                # Unimos y guardamos
                df_final = pd.concat([df, nuevo], ignore_index=True)
                conn.update(worksheet="votos", data=df_final)
                st.success("Voto guardado")
            except Exception as e:
                st.error(f"Error: {e}")

# 4. RANKING
elif opcion == "Ranking":
    st.header("Ranking")
    try:
        df = conn.read(worksheet="votos")
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No hay datos")
    except:
        st.error("No se pudo leer el Excel")

# 5. MENSAJES
elif opcion == "Mensajes":
    st.header("Dedicatorias")
    with st.form("msg"):
        txt = st.text_area("Mensaje")
        if st.form_submit_button("Enviar"):
            try:
                df = conn.read(worksheet="dedicatorias")
                nuevo = pd.DataFrame([{"Mensaje": txt}])
                df_final = pd.concat([df, nuevo], ignore_index=True)
                conn.update(worksheet="dedicatorias", data=df_final)
                st.success("Enviado")
            except:
                st.error("Error al guardar")
