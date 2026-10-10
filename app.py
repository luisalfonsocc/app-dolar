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

# Función para dar formato venezolano: 1.234,56
def fmt_ve(val):
    if val is None:
        return "0,00"
    return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
        margin: 10px auto 15px auto;
        width: fit-content;
        font-weight: 600;
    }
    .big-rates {
        text-align: center;
        font-size: 1.05rem;
        font-weight: 600;
        color: #4A5568;
        margin-bottom: 20px;
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
st.markdown(f"<div class='big-rates'>💵 USD: <b>{fmt_ve(tasa_dolar)} Bs</b> &nbsp;|&nbsp; 💶 EUR: <b>{fmt_ve(tasa_euro)} Bs</b></div>", unsafe_allow_html=True)

# Callback para limpiar campos de dólares
def limpiar_usd():
    st.session_state["val_usd"] = 0.0
    st.session_state["val_bs_u"] = 0.0

# Callback para limpiar campos de euros
def limpiar_eur():
    st.session_state["val_eur"] = 0.0
    st.session_state["val_bs_e"] = 0.0

# Callback de conversión automática
def update_u_from_usd():
    st.session_state["val_bs_u"] = round(st.session_state["val_usd"] * tasa_dolar, 2)

def update_u_from_bs():
    st.session_state["val_usd"] = round(st.session_state["val_bs_u"] / tasa_dolar, 2) if tasa_dolar else 0.0

def update_e_from_eur():
    st.session_state["val_bs_e"] = round(st.session_state["val_eur"] * tasa_euro, 2)

def update_e_from_bs():
    st.session_state["val_eur"] = round(st.session_state["val_bs_e"] / tasa_euro, 2) if tasa_euro else 0.0

# PESTAÑAS PRINCIPALES
tab_usd, tab_eur = st.tabs(["💵 Dólares ($)", "💶 Euros (€)"])

# ==================== PESTAÑA DÓLARES ====================
with tab_usd:
    st.write("")
    col_u1, col_u2 = st.columns([1, 4])
    with col_u1:
        st.markdown("### $")
    with col_u2:
        st.number_input(
            "Monto $",
            min_value=0.0,
            key="val_usd",
            on_change=update_u_from_usd,
            format="%.2f",
            label_visibility="collapsed"
        )

    col_u3, col_u4 = st.columns([1, 4])
    with col_u3:
        st.markdown("### Bs")
    with col_u4:
        st.number_input(
            "Monto Bs",
            min_value=0.0,
            key="val_bs_u",
            on_change=update_u_from_bs,
            format="%.2f",
            label_visibility="collapsed"
        )

    col_btn_u, _ = st.columns([2, 3])
    with col_btn_u:
        st.button("🧹 Limpiar", key="btn_clean_u", on_click=limpiar_usd)

    st.write("---")
    st.subheader("📊 Tabla de Cambios Rápidos ($ USD)")
    cantidades = [1, 5, 10, 15, 20, 30, 50, 100]
    df_usd = pd.DataFrame({
        "Monto ($)": [f"${c},00" for c in cantidades],
        "Equivalente en Bolívares (Bs)": [f"{fmt_ve(c * tasa_dolar)} Bs" for c in cantidades]
    })
    st.table(df_usd)

# ==================== PESTAÑA EUROS ====================
with tab_eur:
    st.write("")
    col_e1, col_e2 = st.columns([1, 4])
    with col_e1:
        st.markdown("### €")
    with col_e2:
        st.number_input(
            "Monto €",
            min_value=0.0,
            key="val_eur",
            on_change=update_e_from_eur,
            format="%.2f",
            label_visibility="collapsed"
        )

    col_e3, col_e4 = st.columns([1, 4])
    with col_e3:
        st.markdown("### Bs")
    with col_e4:
        st.number_input(
            "Monto Bs",
            min_value=0.0,
            key="val_bs_e",
            on_change=update_e_from_bs,
            format="%.2f",
            label_visibility="collapsed"
        )

    col_btn_e, _ = st.columns([2, 3])
    with col_btn_e:
        st.button("🧹 Limpiar", key="btn_clean_e", on_click=limpiar_eur)

    st.write("---")
    st.subheader("📊 Tabla de Cambios Rápidos (€ EUR)")
    cantidades = [1, 5, 10, 15, 20, 30, 50, 100]
    df_eur = pd.DataFrame({
        "Monto (€)": [f"€{c},00" for c in cantidades],
        "Equivalente en Bolívares (Bs)": [f"{fmt_ve(c * tasa_euro)} Bs" for c in cantidades]
    })
    st.table(df_eur)

st.markdown("<div class='version-footer'>Versión v1.3.0</div>", unsafe_allow_html=True)