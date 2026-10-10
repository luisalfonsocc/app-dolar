import json
import os
import requests
import streamlit as st
import pandas as pd

# Configuración de página
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

def fmt_ve(val):
    if val is None or val == 0:
        return "0,00"
    return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- CSS ANTI-MODO OSCURO DEL TELÉFONO + DISEÑO MOBILE PERFECTO ---
st.markdown("""
    <style>
    /* Forzar fondo blanco y texto oscuro absoluto */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #FFFFFF !important;
        color: #1A202C !important;
    }

    /* Encabezados */
    .brand-title {
        text-align: center;
        font-weight: 900;
        font-size: 2.1rem;
        color: #111827 !important;
        margin-bottom: 2px;
    }
    .date-badge {
        text-align: center;
        font-size: 0.85rem;
        color: #1D4ED8 !important;
        background-color: #EFF6FF !important;
        border: 1px solid #BFDBFE !important;
        border-radius: 8px;
        padding: 5px 12px;
        margin: 6px auto 14px auto;
        width: fit-content;
        font-weight: 700;
    }
    .big-rates {
        text-align: center;
        font-size: 1rem;
        font-weight: 700;
        color: #374151 !important;
        margin-bottom: 20px;
    }

    /* Tarjetas de Entrada de Dinero */
    .calc-card {
        background-color: #F9FAFB !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .card-label {
        font-size: 0.9rem;
        font-weight: 800;
        color: #1F2937 !important;
        margin-bottom: 6px;
    }
    .preview-box {
        background-color: #374151 !important;
        color: #FFFFFF !important;
        font-size: 1.15rem;
        font-weight: 800;
        padding: 8px 12px;
        border-radius: 8px;
        margin-top: 8px;
        display: inline-block;
        letter-spacing: 0.5px;
    }

    /* Tablas forzadas a texto visible */
    div[data-testid="stTable"] table {
        color: #111827 !important;
        background-color: #FFFFFF !important;
    }
    div[data-testid="stTable"] th {
        color: #111827 !important;
        background-color: #F3F4F6 !important;
        font-weight: 800 !important;
    }
    div[data-testid="stTable"] td {
        color: #1F2937 !important;
    }

    /* Textos del Radio Button */
    div[data-testid="stRadio"] label p {
        color: #111827 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }

    .version-footer {
        text-align: center;
        font-size: 0.8rem;
        color: #9CA3AF !important;
        margin-top: 30px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='brand-title'>⚡ TasaYa</div>", unsafe_allow_html=True)
st.markdown(f"<div class='date-badge'>📅 {fecha_valor}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='big-rates'>💵 USD: <b>{fmt_ve(tasa_dolar)} Bs</b> &nbsp;|&nbsp; 💶 EUR: <b>{fmt_ve(tasa_euro)} Bs</b></div>", unsafe_allow_html=True)

def reset_campos():
    st.session_state["val_ext"] = 0.0
    st.session_state["val_bs"] = 0.0

moneda = st.radio(
    "",
    ["💵 Dólares ($)", "💶 Euros (€)"],
    horizontal=True,
    key="moneda_sel",
    on_change=reset_campos,
    label_visibility="collapsed"
)

tasa_actual = tasa_dolar if "Dólares" in moneda else tasa_euro
simbolo = "$" if "Dólares" in moneda else "€"

def update_from_ext():
    m = st.session_state.get("val_ext", 0.0)
    st.session_state["val_bs"] = round(m * tasa_actual, 2)

def update_from_bs():
    m = st.session_state.get("val_bs", 0.0)
    st.session_state["val_ext"] = round(m / tasa_actual, 2) if tasa_actual else 0.0

def limpiar_todo():
    st.session_state["val_ext"] = 0.0
    st.session_state["val_bs"] = 0.0

st.write("")

val_ext_actual = st.session_state.get("val_ext", 0.0)
val_bs_actual = st.session_state.get("val_bs", 0.0)

# BLOQUE MONEDA EXTRANJERA
st.markdown("<div class='calc-card'>", unsafe_allow_html=True)
st.markdown(f"<div class='card-label'>Monto en {simbolo}</div>", unsafe_allow_html=True)

col_e_in, col_e_cp = st.columns([4, 1])
with col_e_in:
    st.number_input(
        f"Monto {simbolo}",
        min_value=0.0,
        key="val_ext",
        on_change=update_from_ext,
        format="%.2f",
        label_visibility="collapsed"
    )
with col_e_cp:
    if st.button("📋", key="btn_cp_ext", help="Copiar solo números"):
        st.code(fmt_ve(val_ext_actual), language=None)

if val_ext_actual > 0:
    st.markdown(f"<div class='preview-box'>{simbolo} {fmt_ve(val_ext_actual)}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# BLOQUE BOLÍVARES
st.markdown("<div class='calc-card'>", unsafe_allow_html=True)
st.markdown("<div class='card-label'>Monto en Bolívares (Bs)</div>", unsafe_allow_html=True)

col_b_in, col_b_cp = st.columns([4, 1])
with col_b_in:
    st.number_input(
        "Monto Bs",
        min_value=0.0,
        key="val_bs",
        on_change=update_from_bs,
        format="%.2f",
        label_visibility="collapsed"
    )
with col_b_cp:
    if st.button("📋", key="btn_cp_bs", help="Copiar solo números"):
        st.code(fmt_ve(val_bs_actual), language=None)

if val_bs_actual > 0:
    st.markdown(f"<div class='preview-box'>{fmt_ve(val_bs_actual)} Bs</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# BOTÓN LIMPIAR
st.button("🧹 Limpiar calculadora", key="btn_clean", on_click=limpiar_todo, use_container_width=True)

st.write("---")

# TABLA DE CAMBIOS RÁPIDOS
st.markdown(f"### 📊 Tabla de Cambios Rápidos ({simbolo})")
cantidades = [1, 5, 10, 15, 20, 30, 35, 40, 45, 50, 100]
df_tabla = pd.DataFrame({
    f"Monto ({simbolo})": [f"{simbolo}{c},00" for c in cantidades],
    "Equivalente en Bolívares (Bs)": [f"{fmt_ve(c * tasa_actual)} Bs" for c in cantidades]
})
st.table(df_tabla)

st.markdown("<div class='version-footer'>Versión v2.0.0</div>", unsafe_allow_html=True)