import json
import os
import requests
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="TasaYa", page_icon="⚡", layout="centered")

def cargar_tasas():
    if os.path.exists("tasas.json"):
        try:
            with open("tasas.json", "r") as f:
                datos = json.load(f)
                if "bcv_dolar" in datos and datos["bcv_dolar"]:
                    return datos
        except Exception:
            pass

    try:
        url = "https://www.bcv.org.ve/"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, verify=False, timeout=5)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        d_elem = soup.find('div', id='dolar')
        e_elem = soup.find('div', id='euro')
        
        d_val = float(d_elem.find('strong').text.strip().replace('.', '').replace(',', '.')) if d_elem else 36.50
        e_val = float(e_elem.find('strong').text.strip().replace('.', '').replace(',', '.')) if e_elem else 39.50
        return {"bcv_dolar": d_val, "bcv_euro": e_val}
    except Exception:
        return {"bcv_dolar": 36.50, "bcv_euro": 39.50}

tasas = cargar_tasas()
tasa_dolar = tasas.get("bcv_dolar", 36.50)
tasa_euro = tasas.get("bcv_euro", 39.50)

# ESTILOS CSS ESTILO AL CAMBIO (DARK MODE)
st.markdown("""
    <style>
    /* Fondo oscuro global */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    
    /* Titulo */
    .brand-title {
        text-align: center;
        font-weight: 800;
        font-size: 2.2rem;
        color: #FFFFFF;
        margin-bottom: 20px;
    }

    /* Selector verde tipo pastilla */
    div[data-testid="stRadio"] > div {
        justify-content: center;
        background-color: #27272A;
        border-radius: 25px;
        padding: 4px;
    }
    
    /* Contenedor principal de la tarjeta */
    .calc-card {
        background-color: #1E1E1E;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #2D2D2D;
        margin-top: 10px;
    }
    
    .version-footer {
        text-align: center;
        font-size: 0.8rem;
        color: #666666;
        margin-top: 30px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='brand-title'>⚡ tasaya</div>", unsafe_allow_html=True)

# Estado de la conversión
if "monto_ext" not in st.session_state:
    st.session_state.monto_ext = 1.0
if "monto_bs" not in st.session_state:
    st.session_state.monto_bs = tasa_dolar

def actualizar_desde_ext():
    tasa = tasa_dolar if st.session_state.moneda == "Dólar BCV" else tasa_euro
    st.session_state.monto_bs = round(st.session_state.monto_ext * tasa, 2)

def actualizar_desde_bs():
    tasa = tasa_dolar if st.session_state.moneda == "Dólar BCV" else tasa_euro
    st.session_state.monto_ext = round(st.session_state.monto_bs / tasa, 2) if tasa else 0.0

def cambiar_moneda():
    tasa = tasa_dolar if st.session_state.moneda == "Dólar BCV" else tasa_euro
    st.session_state.monto_bs = round(st.session_state.monto_ext * tasa, 2)

# Selector de Moneda tipo Pastilla Verde
moneda = st.radio(
    "",
    ["Dólar BCV", "Euro BCV"],
    horizontal=True,
    key="moneda",
    on_change=cambiar_moneda,
    label_visibility="collapsed"
)

tasa_actual = tasa_dolar if moneda == "Dólar BCV" else tasa_euro
simbolo = "$" if moneda == "Dólar BCV" else "€"

# Tarjeta Oscura estilo "Al Cambio"
st.markdown("<div class='calc-card'>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 4])
with col1:
    st.markdown(f"### {simbolo}")
with col2:
    st.number_input(
        f"Monto en {simbolo}",
        min_value=0.0,
        key="monto_ext",
        on_change=actualizar_desde_ext,
        format="%.2f",
        label_visibility="collapsed"
    )

col3, col4 = st.columns([1, 4])
with col3:
    st.markdown("### Bs")
with col4:
    st.number_input(
        "Monto en Bs",
        min_value=0.0,
        key="monto_bs",
        on_change=actualizar_desde_bs,
        format="%.2f",
        label_visibility="collapsed"
    )

# Fecha y Tasa en la parte inferior de la tarjeta
fecha_hoy = datetime.now().strftime("%A, %d/%m/%Y")
st.caption(f"📅 **{fecha_hoy}** &nbsp;|&nbsp; Tasa oficial: **1 {simbolo} = {tasa_actual:,.2f} Bs**")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='version-footer'>Versión v2.0.0</div>", unsafe_allow_html=True)