import json
import os
import requests
import streamlit as st
import pandas as pd

st.set_page_config(page_title="CuentasClaras", page_icon="🤝", layout="centered")

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
        return {
            "bcv_dolar": d_val, 
            "bcv_euro": e_val, 
            "fecha_valor": f_val, 
            "usdt_ref": 1016.45,
            "usdt_fecha_hora": "Reciente"
        }
    except Exception:
        return {
            "bcv_dolar": 876.80, 
            "bcv_euro": 982.00, 
            "fecha_valor": "Fecha Oficial BCV", 
            "usdt_ref": 1016.45,
            "usdt_fecha_hora": "Reciente"
        }

datos = cargar_tasas()
tasa_dolar = datos.get("bcv_dolar", 876.80)
tasa_euro = datos.get("bcv_euro", 982.00)
fecha_valor = datos.get("fecha_valor", "Fecha Oficial BCV")
tasa_usdt = datos.get("usdt_ref", 1016.45)
usdt_fecha_hora = datos.get("usdt_fecha_hora", "Hoy")

def fmt_ve(val):
    if val is None or val == 0:
        return "0,00"
    return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- ESTILOS CSS LIMPIOS ANTI-DARK MODE (SIN CAJAS FANTASMA) ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #FFFFFF !important;
        color: #1A202C !important;
    }

    /* Ocultar elementos vacios o contenedores HTML residuales */
    .element-container:empty {
        display: none !important;
    }

    .brand-title {
        text-align: center;
        font-weight: 900;
        font-size: 2.3rem;
        color: #0F172A !important;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
    }
    .brand-title span {
        color: #2563EB !important;
    }
    .brand-tagline {
        text-align: center;
        font-size: 0.8rem;
        color: #64748B !important;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .date-badge {
        text-align: center;
        font-size: 0.85rem;
        color: #1E40AF !important;
        background-color: #EFF6FF !important;
        border: 1px solid #BFDBFE !important;
        border-radius: 8px;
        padding: 5px 12px;
        margin: 4px auto 10px auto;
        width: fit-content;
        font-weight: 700;
    }
    .big-rates {
        text-align: center;
        font-size: 0.95rem;
        font-weight: 700;
        color: #334155 !important;
        margin-bottom: 2px;
    }
    .usdt-time-header {
        text-align: center;
        font-size: 0.78rem;
        color: #047857 !important;
        font-weight: 600;
        margin-bottom: 18px;
    }
    .card-label {
        font-size: 0.95rem;
        font-weight: 800;
        color: #1E293B !important;
        margin-bottom: 4px;
        margin-top: 10px;
    }
    .preview-box {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        font-size: 1.15rem;
        font-weight: 800;
        padding: 8px 14px;
        border-radius: 8px;
        margin-top: 6px;
        margin-bottom: 12px;
        display: inline-block;
    }
    .usdt-ref-box {
        font-size: 0.88rem;
        color: #047857 !important;
        background-color: #ECFDF5 !important;
        border: 1px solid #A7F3D0 !important;
        border-radius: 8px;
        padding: 8px 12px;
        margin-top: 6px;
        margin-bottom: 12px;
        font-weight: 600;
    }

    /* Estilos para Tablas */
    div[data-testid="stTable"] table {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
    }
    div[data-testid="stTable"] th {
        color: #0F172A !important;
        background-color: #F1F5F9 !important;
        font-weight: 800 !important;
    }
    div[data-testid="stTable"] td {
        color: #1E293B !important;
    }
    div[data-testid="stRadio"] label p {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    .version-footer {
        text-align: center;
        font-size: 0.8rem;
        color: #94A3B8 !important;
        margin-top: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# ENCABEZADO "CUENTAS CLARAS"
st.markdown("<div class='brand-title'>🤝 Cuentas<span>Claras</span> ⚡</div>", unsafe_allow_html=True)
st.markdown("<div class='brand-tagline'>Calculadora Rápida • Sin Publicidad</div>", unsafe_allow_html=True)
st.markdown(f"<div class='date-badge'>📅 Fecha Tasa BCV: <b>{fecha_valor}</b></div>", unsafe_allow_html=True)

# TASAS SUPERIORES DESTACADAS CON HORA DE USDT PERMANENTE
st.markdown(
    f"<div class='big-rates'>"
    f"💵 USD: <b>{fmt_ve(tasa_dolar)} Bs</b> &nbsp;|&nbsp; "
    f"💶 EUR: <b>{fmt_ve(tasa_euro)} Bs</b> &nbsp;|&nbsp; "
    f"🪙 USDT: <b>{fmt_ve(tasa_usdt)} Bs</b>"
    f"</div>", 
    unsafe_allow_html=True
)
st.markdown(f"<div class='usdt-time-header'>🕒 Tasa USDT actualizada: <b>{usdt_fecha_hora}</b></div>", unsafe_allow_html=True)

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

val_ext_actual = st.session_state.get("val_ext", 0.0)
val_bs_actual = st.session_state.get("val_bs", 0.0)

# BLOQUE MONEDA EXTRANJERA ($ / €)
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

# BLOQUE BOLÍVARES (Bs)
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
    
    # REFERENCIA EN USDT
    usdt_equiv = val_bs_actual / tasa_usdt if tasa_usdt else 0.0
    st.markdown(
        f"<div class='usdt-ref-box'>"
        f"🪙 Equivale a: <b>~{fmt_ve(usdt_equiv)} USDT</b> (Ref: {fmt_ve(tasa_usdt)} Bs/USDT)"
        f"</div>", 
        unsafe_allow_html=True
    )

st.write("")

# BOTÓN LIMPIAR
st.button("🧹 Limpiar calculadora", key="btn_clean", on_click=limpiar_todo, use_container_width=True)

st.write("---")

# CHULETA RÁPIDA
st.markdown(f"### 📝 Chuleta Rápida ({simbolo})")
cantidades = [1, 5, 10, 15, 20, 30, 35, 40, 45, 50, 100]

monto_col = [f"{simbolo}{c},00" for c in cantidades]
bs_col = [f"{fmt_ve(c * tasa_actual)} Bs" for c in cantidades]
usdt_col = [f"~{fmt_ve((c * tasa_actual) / tasa_usdt)} USDT" for c in cantidades]

df_tabla = pd.DataFrame({
    f"Monto ({simbolo})": monto_col,
    "En Bolívares (Bs)": bs_col,
    "En USDT 🪙": usdt_col
})

st.table(df_tabla)

st.markdown("<div class='version-footer'>Versión v3.0.0</div>", unsafe_allow_html=True)