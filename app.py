import json
import os
import requests
import streamlit as st

st.set_page_config(page_title="Al Cambio Vzla", page_icon="💸", layout="centered")

def cargar_tasas_desde_json():
    # Intentar leer el archivo json generado en el servidor
    if os.path.exists("tasas.json"):
        try:
            with open("tasas.json", "r") as f:
                return json.load(f)
        except Exception:
            pass
    
    # Respaldo en vivo directo si por alguna razón no existe el json
    try:
        url_bcv = "https://www.bcv.org.ve/"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url_bcv, headers=headers, verify=False, timeout=5)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, 'html.parser')
        contenedor = soup.find('div', id='dolar')
        bcv_val = float(contenedor.find('strong').text.strip().replace('.', '').replace(',', '.')) if contenedor else None
    except Exception:
        bcv_val = None

    try:
        resp_c = requests.get("https://criptoya.com/api/binancep2p/usdt/ves/5", timeout=5).json()
        precios = [float(item["price"]) for item in resp_c.get("data", [])[:5]]
        ves_val = round(sum(precios) / len(precios), 2) if precios else None
    except Exception:
        ves_val = None

    try:
        resp_clp = requests.get("https://criptoya.com/api/binancep2p/usdt/clp/5", timeout=5).json()
        precios_clp = [float(item["price"]) for item in resp_clp.get("data", [])[:5]]
        clp_val = round(sum(precios_clp) / len(precios_clp), 2) if precios_clp else None
    except Exception:
        clp_val = None

    return {"bcv": bcv_val, "binance_ves": ves_val, "binance_clp": clp_val}

tasas = cargar_tasas_desde_json()
tasa_bcv = tasas.get("bcv")
tasa_usdt = tasas.get("binance_ves")
tasa_clp = tasas.get("binance_clp")

# --- INTERFAZ TIPO APP ---
st.markdown("<h2 style='text-align: center;'>💸 Al Cambio Vzla</h2>", unsafe_allow_html=True)

# Tarjetas de Tasas
col1, col2 = st.columns(2)
with col1:
    st.metric("🏛️ BCV (Oficial)", f"{tasa_bcv:,.2f} Bs" if tasa_bcv else "N/A")
with col2:
    st.metric("🟡 USDT (Paralelo)", f"{tasa_usdt:,.2f} Bs" if tasa_usdt else "N/A")

if tasa_clp:
    st.caption(f"🇨🇱 Binance CLP: ${tasa_clp:,.0f} CLP/USDT")

st.divider()

# --- CALCULADORA DE UN SOLO CAMPO ---
st.subheader("🧮 Calculadora Rápida")

modo = st.radio("Convertir desde:", ["Dólares ($)", "Bolívares (Bs)"], horizontal=True)

if modo == "Dólares ($)":
    monto_usd = st.number_input("Monto en Dólares ($):", min_value=0.0, value=10.0, step=5.0)
    
    bs_bcv = monto_usd * tasa_bcv if tasa_bcv else 0
    bs_usdt = monto_usd * tasa_usdt if tasa_usdt else 0
    
    st.success(f"**🏛️ BCV:** {bs_bcv:,.2f} Bs")
    st.info(f"**🟡 Paralelo:** {bs_usdt:,.2f} Bs")

else:
    monto_bs = st.number_input("Monto en Bolívares (Bs):", min_value=0.0, value=500.0, step=50.0)
    
    usd_bcv = monto_bs / tasa_bcv if tasa_bcv else 0
    usd_usdt = monto_bs / tasa_usdt if tasa_usdt else 0
    
    st.success(f"**🏛️ BCV:** ${usd_bcv:,.2f} USD")
    st.info(f"**🟡 Paralelo:** ${usd_usdt:,.2f} USDT")