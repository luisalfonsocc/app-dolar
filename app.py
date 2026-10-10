import json
import os
import requests
import streamlit as st

st.set_page_config(page_title="Al Cambio Vzla", page_icon="💸", layout="centered")

def cargar_tasas():
    if os.path.exists("tasas.json"):
        try:
            with open("tasas.json", "r") as f:
                datos = json.load(f)
                if "bcv_dolar" in datos and datos["bcv_dolar"]:
                    return datos
        except Exception:
            pass

    # Respaldo en vivo si aún no existe o falla el JSON
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
tasa_dolar = tasas.get("bcv_dolar", 0)
tasa_euro = tasas.get("bcv_euro", 0)

# Estilo personalizado
st.markdown("""
    <style>
    .big-rate {
        font-size: 1.1rem;
        font-weight: 600;
        color: #4A5568;
        text-align: center;
        margin-bottom: 10px;
    }
    .version-footer {
        text-align: center;
        font-size: 0.8rem;
        color: #A0AEC0;
        margin-top: 30px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; margin-bottom: 0px;'>💸 Al Cambio Vzla</h2>", unsafe_allow_html=True)
st.markdown(f"<div class='big-rate'>BCV: <b>${tasa_dolar:,.2f} Bs</b> | <b>€{tasa_euro:,.2f} Bs</b></div>", unsafe_allow_html=True)

st.divider()

# --- PESTAÑAS PRINCIPALES POR MONEDA ---
tab_usd, tab_eur = st.tabs(["💵 Dólares ($)", "💶 Euros (€)"])

# ==================== PESTAÑA DÓLARES ====================
with tab_usd:
    st.subheader("Calculadora USD / BS")
    
    modo_usd = st.radio(
        "¿Qué deseas ingresar?",
        ["Tengo Bolívares (Bs) ➔ Calcular $", "Tengo Dólares ($) ➔ Calcular Bs"],
        key="modo_usd"
    )
    
    if "Tengo Bolívares" in modo_usd:
        monto_bs = st.number_input("Monto en Bolívares (Bs):", min_value=0.0, value=100.0, step=50.0, key="usd_bs_input")
        resultado_usd = monto_bs / tasa_dolar if tasa_dolar else 0
        st.success(f"### 💵 Equivale a: `{resultado_usd:,.2f} USD`")
    else:
        monto_usd = st.number_input("Monto en Dólares ($):", min_value=0.0, value=10.0, step=5.0, key="usd_usd_input")
        resultado_bs = monto_usd * tasa_dolar if tasa_dolar else 0
        st.success(f"### 🇻🇪 Equivale a: `{resultado_bs:,.2f} Bs`")

# ==================== PESTAÑA EUROS ====================
with tab_eur:
    st.subheader("Calculadora EUR / BS")
    
    modo_eur = st.radio(
        "¿Qué deseas ingresar?",
        ["Tengo Bolívares (Bs) ➔ Calcular €", "Tengo Euros (€) ➔ Calcular Bs"],
        key="modo_eur"
    )
    
    if "Tengo Bolívares" in modo_eur:
        monto_bs_e = st.number_input("Monto en Bolívares (Bs):", min_value=0.0, value=100.0, step=50.0, key="eur_bs_input")
        resultado_eur = monto_bs_e / tasa_euro if tasa_euro else 0
        st.info(f"### 💶 Equivale a: `{resultado_eur:,.2f} €`")
    else:
        monto_eur = st.number_input("Monto en Euros (€):", min_value=0.0, value=10.0, step=5.0, key="eur_eur_input")
        resultado_bs_e = monto_eur * tasa_euro if tasa_euro else 0
        st.info(f"### 🇻🇪 Equivale a: `{resultado_bs_e:,.2f} Bs`")

st.caption("💡 *Puedes copiar el resultado directamente manteniendo presionado el texto sobre el recuadro verde/azul.*")

# PIE DE PÁGINA CON VERSIÓN
st.markdown("<div class='version-footer'>Versión v1.0.0</div>", unsafe_allow_html=True)