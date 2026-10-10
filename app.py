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

# ESTILOS CSS (LIGHT MODE / FONDO BLANCO)
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
        color: #1A202C;
    }
    
    .brand-title {
        text-align: center;
        font-weight: 800;
        font-size: 2.2rem;
        color: #000000;
        margin-bottom: 5px;
    }

    .rates-header {
        text-align: center;
        font-size: 1rem;
        font-weight: 600;
        color: #4A5568;
        margin-bottom: 20px;
    }

    .version-footer {
        text-align: center;
        font-size: 0.8rem;
        color: #A0AEC0;
        margin-top: 30px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='brand-title'>⚡ TasaYa</div>", unsafe_allow_html=True)
st.markdown(f"<div class='rates-header'>BCV: <b>${tasa_dolar:,.2f} Bs</b> &nbsp;|&nbsp; <b>€{tasa_euro:,.2f} Bs</b></div>", unsafe_allow_html=True)

# Pestañas principales
tab_usd, tab_eur = st.tabs(["💵 Dólar BCV", "💶 Euro BCV"])

# --- FUNCIONES DE CÁLCULO EN VIVO ---
def calc_usd_ext():
    m = st.session_state.get("usd_input_ext", 0.0)
    st.session_state["usd_input_bs"] = round(m * tasa_dolar, 2)

def calc_usd_bs():
    m = st.session_state.get("usd_input_bs", 0.0)
    st.session_state["usd_input_ext"] = round(m / tasa_dolar, 2) if tasa_dolar else 0.0

def calc_eur_ext():
    m = st.session_state.get("eur_input_ext", 0.0)
    st.session_state["eur_input_bs"] = round(m * tasa_euro, 2)

def calc_eur_bs():
    m = st.session_state.get("eur_input_bs", 0.0)
    st.session_state["eur_input_ext"] = round(m / tasa_euro, 2) if tasa_euro else 0.0

# ==================== PESTAÑA DÓLAR ====================
with tab_usd:
    st.write("")
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("### $")
    with col2:
        st.number_input(
            "Monto $",
            min_value=0.0,
            key="usd_input_ext",
            on_change=calc_usd_ext,
            format="%.2f",
            label_visibility="collapsed"
        )

    col3, col4 = st.columns([1, 4])
    with col3:
        st.markdown("### Bs")
    with col4:
        st.number_input(
            "Monto Bs",
            min_value=0.0,
            key="usd_input_bs",
            on_change=calc_usd_bs,
            format="%.2f",
            label_visibility="collapsed"
        )

# ==================== PESTAÑA EURO ====================
with tab_eur:
    st.write("")
    col5, col6 = st.columns([1, 4])
    with col5:
        st.markdown("### €")
    with col6:
        st.number_input(
            "Monto €",
            min_value=0.0,
            key="eur_input_ext",
            on_change=calc_eur_ext,
            format="%.2f",
            label_visibility="collapsed"
        )

    col7, col8 = st.columns([1, 4])
    with col7:
        st.markdown("### Bs")
    with col8:
        st.number_input(
            "Monto Bs",
            min_value=0.0,
            key="eur_input_bs",
            on_change=calc_eur_bs,
            format="%.2f",
            label_visibility="collapsed"
        )

# Pie de página
fecha_hoy = datetime.now().strftime("%d/%m/%Y")
st.caption(f"📅 Actualizado: {fecha_hoy}")
st.markdown("<div class='version-footer'>Versión v2.1.0</div>", unsafe_allow_html=True)