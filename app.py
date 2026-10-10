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

# Formato venezolano: 1.234,56
def fmt_ve(val):
    if val is None or val == 0:
        return "0,00"
    return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
    }
    .brand-title {
        text-align: center;
        font-weight: 800;
        font-size: 2.2rem;
        color: #1A202C;
        margin-bottom: 2px;
    }
    .date-badge {
        text-align: center;
        font-size: 0.85rem;
        color: #2B6CB0;
        background-color: #EBF8FF;
        border: 1px solid #BEE3F8;
        border-radius: 8px;
        padding: 5px 10px;
        margin: 5px auto 15px auto;
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
    /* Estilo del selector de moneda tipo botones */
    div[data-testid="stRadio"] > div {
        justify-content: center;
        gap: 10px;
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

# Función para reiniciar campos al cambiar de moneda
def reset_campos():
    st.session_state["val_ext"] = 0.0
    st.session_state["val_bs"] = 0.0

# Selector principal de moneda
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

# Callbacks de sincronización bidireccional
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

# CAMPOS DE ENTRADA
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown(f"### {simbolo}")
with col2:
    st.number_input(
        f"Monto {simbolo}",
        min_value=0.0,
        key="val_ext",
        on_change=update_from_ext,
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
        key="val_bs",
        on_change=update_from_bs,
        format="%.2f",
        label_visibility="collapsed"
    )

col_btn, _ = st.columns([2, 3])
with col_btn:
    st.button("🧹 Limpiar", key="btn_clean", on_click=limpiar_todo)

# CAMPO COPIABLE DESTACADO
m_ext = st.session_state.get("val_ext", 0.0)
m_bs = st.session_state.get("val_bs", 0.0)

if m_bs > 0 or m_ext > 0:
    st.write("")
    st.markdown("##### 📋 Resultado para copiar:")
    texto_copiar = f"{fmt_ve(m_bs)} Bs ({simbolo}{fmt_ve(m_ext)})"
    st.code(texto_copiar, language=None)

st.write("---")

# TABLA DE CAMBIOS RÁPIDOS
st.subheader(f"📊 Tabla de Cambios Rápidos ({simbolo})")
cantidades = [1, 5, 10, 15, 20, 30, 50, 100]
df_tabla = pd.DataFrame({
    f"Monto ({simbolo})": [f"{simbolo}{c},00" for c in cantidades],
    "Equivalente en Bolívares (Bs)": [f"{fmt_ve(c * tasa_actual)} Bs" for c in cantidades]
})
st.table(df_tabla)

st.markdown("<div class='version-footer'>Versión v1.4.0</div>", unsafe_allow_html=True)