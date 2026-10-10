import json
import os
import requests
import streamlit as st

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

    # Respaldo en vivo
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
tasa_dolar = tasas.get("bcv_dolar", 1)
tasa_euro = tasas.get("bcv_euro", 1)

# Estilos CSS
st.markdown("""
    <style>
    .brand-title {
        text-align: center;
        font-weight: 800;
        font-size: 2rem;
        margin-bottom: 0px;
    }
    .big-rate {
        font-size: 1rem;
        font-weight: 600;
        color: #4A5568;
        text-align: center;
        margin-bottom: 15px;
    }
    .version-footer {
        text-align: center;
        font-size: 0.8rem;
        color: #A0AEC0;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='brand-title'>⚡ TasaYa</div>", unsafe_allow_html=True)
st.markdown(f"<div class='big-rate'>BCV: <b>${tasa_dolar:,.2f} Bs</b> &nbsp;|&nbsp; <b>€{tasa_euro:,.2f} Bs</b></div>", unsafe_allow_html=True)

# --- PESTAÑAS PRINCIPALES ---
tab_usd, tab_eur = st.tabs(["💵 Dólares ($)", "💶 Euros (€)"])

# ==================== PESTAÑA DÓLARES ====================
with tab_usd:
    col_a, col_b = st.columns(2)
    
    with col_a:
        usd_val = st.number_input("Monto en Dólares ($):", min_value=0.0, value=0.0, step=1.0, key="usd_field", format="%.2f")
    with col_b:
        bs_from_usd = usd_val * tasa_dolar
        st.number_input("Resultado en Bolívares (Bs):", value=bs_from_usd, key="bs_field_usd", format="%.2f", disabled=False)

    st.write("---")
    st.markdown("##### ⇄ Convertir a la inversa (Bolívares ➔ Dólares)")
    monto_bs_usd = st.number_input("Monto en Bolívares (Bs):", min_value=0.0, value=0.0, step=10.0, key="bs_input_usd", format="%.2f")
    res_usd = monto_bs_usd / tasa_dolar if tasa_dolar else 0.0
    st.success(f"**Equivale a:** `${res_usd:,.2f} USD`")

# ==================== PESTAÑA EUROS ====================
with tab_eur:
    col_c, col_d = st.columns(2)
    
    with col_c:
        eur_val = st.number_input("Monto en Euros (€):", min_value=0.0, value=0.0, step=1.0, key="eur_field", format="%.2f")
    with col_d:
        bs_from_eur = eur_val * tasa_euro
        st.number_input("Resultado en Bolívares (Bs):", value=bs_from_eur, key="bs_field_eur", format="%.2f", disabled=False)

    st.write("---")
    st.markdown("##### ⇄ Convertir a la inversa (Bolívares ➔ Euros)")
    monto_bs_eur = st.number_input("Monto en Bolívares (Bs):", min_value=0.0, value=0.0, step=10.0, key="bs_input_eur", format="%.2f")
    res_eur = monto_bs_eur / tasa_euro if tasa_euro else 0.0
    st.info(f"**Equivale a:** `{res_eur:,.2f} €`")

st.markdown("<div class='version-footer'>Versión v1.1.0</div>", unsafe_allow_html=True)