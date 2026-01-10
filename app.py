import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Karaoke Lu - 30 Cumple", page_icon="🎤")

# Estilo CSS personalizado para imitar tu invitación
st.markdown("""
    <style>
    .main {
        background-color: #FDECEC;
    }
    h1, h2, h3 {
        color: #C0392B;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #C0392B;
        color: white;
        border-radius: 20px;
        width: 100%;
        border: none;
    }
    .stSlider > div > div > div > div {
        background-color: #C0392B;
    }
    .card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #C0392B;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎤 Karaoke Lu: The 30th Show")
st.write("¡Puntúa la actuación actual! Recuerda: valoramos el show, no solo la voz.")

# --- FORMULARIO DE VOTACIÓN ---
with st.container():
    nombre_artista = st.text_input("👤 ¿Quién está cantando?", placeholder="Escribe el nombre del artista...")
    
    st.subheader("📊 Criterios de Evaluación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        c1 = st.slider("⭐ Actitud y Energía", 0, 5, 3, help="Entrega, movimiento y confianza")
        c2 = st.slider("🎭 Interpretación", 0, 5, 3, help="Emoción y gestualidad")
        c3 = st.slider("🎉 Show y Escena", 0, 5, 3, help="Uso del espacio y creatividad")
    
    with col2:
        c4 = st.slider("🔄 Originalidad", 0, 5, 3, help="Elección de canción y estilo")
        c5 = st.slider("👯 Conexión", 0, 5, 3, help="Reacción del público")

    total = c1 + c2 + c3 + c4 + c5
    st.metric(label="Puntuación Total", value=f"{total} / 25")

    if st.button("Enviar Voto 🚀"):
        if nombre_artista:
            # Aquí simulamos el guardado. 
            # Para conectar con Google Sheets, seguiremos el Paso 2.
            nuevo_voto = {
                "Artista": nombre_artista,
                "Total": total,
                "Fecha": datetime.now().strftime("%H:%M:%S")
            }
            st.success(f"¡Voto registrado para {nombre_artista}! 🎉")
            st.balloons()
        else:
            st.error("Por favor, escribe el nombre del artista antes de votar.")

st.markdown("---")
st.caption("Hecho con ❤️ para el cumple de Lucía")
