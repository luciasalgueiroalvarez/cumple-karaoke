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
        /* Forzar modo claro */
        .stApp { background-color: #FFFFFF; color: #000000; }
        h1, h2, h3, h4, h5, h6, p, li, span, div { color: #000000 !important; }
        
        /* Inputs ajustados para iPhone */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
            background-color: #FDF2F2; 
            color: #000000 !important;
            font-size: 16px !important; 
        }
        
        /* Botones grandes */
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
                self.config["private_key"] = self.config["private_key"].replace("\\n", "\n")

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.
