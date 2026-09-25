import time
import requests
from bs4 import BeautifulSoup
import urllib3
import streamlit as st

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración de la página Web
st.set_page_config(page_title="Monitor de Dólar & Conversor", page_icon="💵", layout="centered")

@st.cache_data(ttl=600)  # Guarda los datos en caché por 10 minutos para ser ultrarrápida
def obtener_todas_las_tasas():
    # 1. BCV
    tasa_bcv = None
    try:
        url_bcv = "https://www.bcv.org.ve/"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url_bcv, headers=headers, verify=False, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        contenedor = soup.find('div', id='dolar')
        if contenedor:
            texto = contenedor.find('strong').text.strip()
            tasa_bcv = float(texto.replace('.', '').replace(',', '.'))
    except Exception:
        pass

    # 2. Selenium para Binance
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0")

    driver = None
    tasa_ves_binance = None
    tasa_clp_binance = None

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Consultar Binance VES (Venta)
        driver.get("https://p2p.binance.com/es/trade/SELL/USDT?fiat=VES")
        time.sleep(4)
        elem_ves = driver.find_elements(By.XPATH, '//div[contains(@class, "headline5") or contains(@class, "bn-flex")]')
        precios_ves = []
        for e in elem_ves:
            t = e.text.strip().replace('VES', '').replace(' ', '')
            t = t.replace(',', '') if (',' in t and '.' in t) else t.replace(',', '.')
            try:
                val = float(t)
                if 10 <= val <= 3000:
                    precios_ves.append(val)
                    if len(precios_ves) == 5: break
            except ValueError: continue
        if precios_ves: tasa_ves_binance = round(sum(precios_ves) / len(precios_ves), 2)

        # Consultar Binance CLP (Compra)
        driver.get("https://p2p.binance.com/es/trade/BUY/USDT?fiat=CLP")
        time.sleep(4)
        elem_clp = driver.find_elements(By.XPATH, '//div[contains(@class, "headline5") or contains(@class, "bn-flex")]')
        precios_clp = []
        for e in elem_clp:
            t = e.text.strip().replace('CLP', '').replace(' ', '')
            t = t.replace(',', '') if (',' in t and '.' in t) else t.replace(',', '.')
            try:
                val = float(t)
                if 500 <= val <= 2000:
                    precios_clp.append(val)
                    if len(precios_clp) == 5: break
            except ValueError: continue
        if precios_clp: tasa_clp_binance = round(sum(precios_clp) / len(precios_clp), 2)

    except Exception:
        pass
    finally:
        if driver: driver.quit()

    return tasa_bcv, tasa_ves_binance, tasa_clp_binance

# --- INTERFAZ WEB STREAMLIT ---
st.title("📊 Monitor Personal de Dólar & Conversor")
st.write("Consulta en vivo las tasas oficiales y de mercado para calcular tus montos personales.")

if st.button("🔄 Actualizar Tasas Ahora"):
    st.cache_data.clear()

with st.spinner("Cargando cotizaciones en tiempo real desde BCV y Binance..."):
    tasa_bcv, tasa_ves, tasa_clp = obtener_todas_las_tasas()

# Fila con tarjetas de precios
col1, col2, col3 = st.columns(3)
col1.metric("🏛️ BCV (Oficial)", f"{tasa_bcv:,.2f} VES" if tasa_bcv else "N/A")
col2.metric("🟡 Binance VES", f"{tasa_ves:,.2f} VES" if tasa_ves else "N/A")
col3.metric("🇨🇱 Binance CLP", f"${tasa_clp:,.0f} CLP" if tasa_clp else "N/A")

st.divider()

# --- SECCIÓN DE CALCULADORA ---
st.subheader("🧮 Calculadora de Montos Personal")

monto_usd = st.number_input("Ingresa el monto en Dólares/USDT ($):", min_value=1.0, value=100.0, step=10.0)

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("#### 🏛️ En Bolívares (BCV)")
    if tasa_bcv:
        total_bcv = monto_usd * tasa_bcv
        st.success(f"**{total_bcv:,.2f} VES**")
        st.caption(f"Tasa: {tasa_bcv:,.2f} VES/USD")
    else:
        st.error("Sin tasa BCV")

with col_b:
    st.markdown("#### 🟡 En Bolívares (Binance)")
    if tasa_ves:
        total_ves = monto_usd * tasa_ves
        st.info(f"**{total_ves:,.2f} VES**")
        st.caption(f"Tasa: {tasa_ves:,.2f} VES/USDT")
    else:
        st.error("Sin tasa Binance VES")

with col_c:
    st.markdown("#### 🇨🇱 En Pesos Chilenos (CLP)")
    if tasa_clp:
        total_clp = monto_usd * tasa_clp
        st.warning(f"**${total_clp:,.0f} CLP**")
        st.caption(f"Tasa: ${tasa_clp:,.2f} CLP/USDT")