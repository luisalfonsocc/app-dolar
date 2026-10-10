import json
import os
import requests
import streamlit as st
import pandas as pd

st.set_page_config(page_title="TasaYa", page_icon="⚡", layout="centered")

def cargar_tasas():
    if os.path.exists("tasas.json"):
        try:
            with open("tasas.json", "r", encoding="utf-8") as f:
                datos = json.load(f)
                if "bcv_dolar" in datos and datos["bcv_dolar"]:
                    return datos
        except Exception:
            pass

    # Respaldo directo en vivo
    try:
        url = "https://www.bcv.org.ve/"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, verify=False, timeout=5)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        d_elem = soup.find('div', id='dolar')
        e_elem = soup.find('div', id='euro')
        f_elem = soup.find('span', class_='date-display-single')
        
        d_val = float(d_elem.find('strong').text.strip().replace('.', '').replace(',', '.')) if d_elem else 876.80
        e_val = float(e_elem.find('strong').text.strip().replace('.', '').replace(',', '.')) if e_elem else 982.00
        f_val = f_elem.text.strip() if f_elem else "Fecha Oficial BCV"
        return {"bcv_dolar": d_val, "bcv_euro": e_val, "fecha_valor": f_val}
    except Exception:
        return {"bcv_dolar": 876.80, "bcv_euro": 982.00, "fecha_valor": "Fecha Oficial BCV"}

datos = cargar_tasas()
tasa_dolar = datos.get("bcv_dolar", 876.80)
tasa_euro = datos.get("bcv_euro", 982.00)
fecha_valor = datos.get("fecha_valor", "Fecha Oficial BCV")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .brand-title {
        text-align: center;
        font-weight: 800;
        font-size: 2.2rem;
        color: #1A202C;
        margin-bottom: 2px;
    }
    .date-badge {
        text-align: center;
        font-size: 0.9rem;
        color: #2B6CB0;
        background-color: #EBF8FF;
        border: 1px solid #BEE3F8;
        border-radius: 8px;
        padding: 6px 12px;
        margin: 10px auto 20px auto;
        width: fit-content;
        font-weight: 600;
    }
    .big-rates {
        text-align: center;
        font-size: 1.05rem;
        font-weight: 600;
        color: #4A5568;
        margin-bottom: 15px;
    }
    .version-footer {
        text-align: center;
        font-size: 0.8rem;
        color: #A0AEC0;
        margin-top: 35px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='brand-title'>⚡ TasaYa</div>", unsafe_allow_html=True)
st.markdown(f"<div class='date-badge'>📅 {fecha_valor}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='big-rates'>💵 USD: <b>{tasa_dolar:,.2f} Bs</b> &nbsp;|&nbsp; 💶 EUR: <b>{tasa_euro:,.2f} Bs</b></div>", unsafe_allow_html=True)

# --- PESTAÑAS Y RESET DE ESTADO ---
tab_usd, tab_eur = st.tabs(["💵 Dólares ($)", "💶 Euros (€)"])

# ==================== PESTAÑA DÓLARES ====================
with tab_usd:
    st.write("")
    
    modo_u = st.radio(
        "Convertir:",
        ["Dólares ($) ➔ Bolívares (Bs)", "Bolívares (Bs) ➔ Dólares ($)"],
        key="modo_u_radio",
        horizontal=True
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if "Dólares ($)" in modo_u:
            monto_u = st.number_input("Monto en Dólares ($):", min_value=0.0, value=0.0, step=5.0, key="in_usd", format="%.2f")
            res_u = monto_u * tasa_dolar
            st.success(f"### 🇻🇪 Equivale a: `{res_u:,.2f} Bs`")
        else:
            monto_bs_u = st.number_input("Monto en Bolívares (Bs):", min_value=0.0, value=0.0, step=50.0, key="in_bs_u", format="%.2f")
            res_u = monto_bs_u / tasa_dolar if tasa_dolar else 0.0
            st.success(f"### 💵 Equivale a: `${res_u:,.2f} USD`")

    with col2:
        st.write("")
        st.write("")
        if st.button("🧹 Limpiar", key="clean_usd", use_container_width=True):
            st.session_state["in_usd"] = 0.0
            st.session_state["in_bs_u"] = 0.0
            st.rerun()

    st.write("---")
    st.subheader("📊 Tabla de Cambios Rápidos ($ USD)")
    cantidades = [1, 5, 10, 15, 20, 30, 50, 100]
    df_usd = pd.DataFrame({
        "Monto ($)": [f"${c}.00" for c in cantidades],
        "Equivalente en Bolívares (Bs)": [f"{c * tasa_dolar:,.2f} Bs" for c in cantidades]
    })
    st.table(df_usd)

# ==================== PESTAÑA EUROS ====================
with tab_eur:
    st.write("")
    
    modo_e = st.radio(
        "Convertir:",
        ["Euros (€) ➔ Bolívares (Bs)", "Bolívares (Bs) ➔ Euros (€)"],
        key="modo_e_radio",
        horizontal=True
    )
    
    col3, col4 = st.columns([3, 1])
    with col3:
        if "Euros (€)" in modo_e:
            monto_e = st.number_input("Monto en Euros (€):", min_value=0.0, value=0.0, step=5.0, key="in_eur", format="%.2f")
            res_e = monto_e * tasa_euro
            st.info(f"### 🇻🇪 Equivale a: `{res_e:,.2f} Bs`")
        else:
            monto_bs_e = st.number_input("Monto en Bolívares (Bs):", min_value=0.0, value=0.0, step=50.0, key="in_bs_e", format="%.2f")
            res_e = monto_bs_e / tasa_euro if tasa_euro else 0.0
            st.info(f"### 💶 Equivale a: `{res_e:,.2f} €`")

    with col4:
        st.write("")
        st.write("")
        if st.button("🧹 Limpiar", key="clean_eur", use_container_width=True):
            st.session_state["in_eur"] = 0.0
            st.session_state["in_bs_e"] = 0.0
            st.rerun()

    st.write("---")
    st.subheader("📊 Tabla de Cambios Rápidos (€ EUR)")
    cantidades = [1, 5, 10, 15, 20, 30, 50, 100]
    df_eur = pd.DataFrame({
        "Monto (€)": [f"€{c}.00" for c in cantidades],
        "Equivalente en Bolívares (Bs)": [f"{c * tasa_euro:,.2f} Bs" for c in cantidades]
    })
    st.table(df_eur)

st.markdown("<div class='version-footer'>Versión v1.2.0</div>", unsafe_allow_html=True)