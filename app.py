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

st.set_page_config(page_title="Monitor de Dólar & Conversor", page_icon="📊", layout="centered")

def obtener_tasa_bcv():
    try:
        url = "https://www.bcv.org.ve/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, verify=False, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        contenedor = soup.find('div', id='dolar')
        if contenedor:
            texto = contenedor.find('strong').text.strip()
            return float(texto.replace('.', '').replace(',', '.'))
    except Exception:
        pass
    return None


def obtener_tasa_criptoya(fiat):
    # Respaldo ultrarrápido vía API para evitar bloqueos en servidores en la nube
    try:
        url = f"https://criptoya.com/api/binancep2p/usdt/{fiat.lower()}/5"
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            precios = [float(item["price"]) for item in data.get("data", [])[:5]]
            if precios:
                return round(sum(precios) / len(precios), 2)
    except Exception:
        pass
    return None


def obtener_tasa_selenium(moneda="VES", tipo="SELL", rango_min=10, rango_max=3000):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = None
    try:
        # Intentar inicialización automática
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception:
            # Ruta directa para el paquete chromium en Streamlit Cloud / Linux
            options.binary_location = "/usr/bin/chromium"
            driver = webdriver.Chrome(options=options)

        url = f"https://p2p.binance.com/es/trade/{tipo}/USDT?fiat={moneda.upper()}"
        driver.get(url)
        time.sleep(5)

        elementos = driver.find_elements(By.XPATH, '//div[contains(@class, "headline5") or contains(@class, "bn-flex")]')
        precios = []
        for elem in elementos:
            texto = elem.text.strip().replace(moneda.upper(), '').replace(' ', '')
            texto = texto.replace(',', '') if (',' in texto and '.' in texto) else texto.replace(',', '.')
            try:
                val = float(texto)
                if rango_min <= val <= rango_max:
                    precios.append(val)
                    if len(precios) == 5:
                        break
            except ValueError:
                continue

        if precios:
            return round(sum(precios) / len(precios), 2)
    except Exception:
        pass
    finally:
        if driver:
            driver.quit()

    return None


@st.cache_data(ttl=600)
def cargar_datos_completos():
    tasa_bcv = obtener_tasa_bcv()
    
    # 1. Intentar Selenium
    tasa_ves = obtener_tasa_selenium("VES", "SELL", 10, 3000)
    tasa_clp = obtener_tasa_selenium("CLP", "BUY", 500, 2000)

    # 2. Respaldo vía API si Selenium es bloqueado en la IP del servidor de la nube
    if not tasa_ves:
        tasa_ves = obtener_tasa_criptoya("VES")
    if not tasa_clp:
        tasa_clp = obtener_tasa_criptoya("CLP")

    return tasa_bcv, tasa_ves, tasa_clp


# --- INTERFAZ STREAMLIT ---
st.title("📊 Monitor Personal de Dólar & Conversor")
st.write("Consulta en vivo las tasas oficiales y de mercado para calcular tus montos personales.")

if st.button("🔄 Actualizar Tasas Ahora"):
    st.cache_data.clear()

with st.spinner("Obteniendo cotizaciones en vivo..."):
    tasa_bcv, tasa_ves, tasa_clp = cargar_datos_completos()

col1, col2, col3 = st.columns(3)
col1.metric("🏛️ BCV (Oficial)", f"{tasa_bcv:,.2f} VES" if tasa_bcv else "N/A")
col2.metric("🟡 Binance VES", f"{tasa_ves:,.2f} VES" if tasa_ves else "N/A")
col3.metric("🇨🇱 Binance CLP", f"${tasa_clp:,.0f} CLP" if tasa_clp else "N/A")

st.divider()

st.subheader("🧮 Calculadora de Montos Personal")
monto_usd = st.number_input("Ingresa el monto en Dólares/USDT ($):", min_value=1.0, value=100.0, step=10.0)

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("#### 🏛️ Bolívares (BCV)")
    if tasa_bcv:
        st.success(f"**{monto_usd * tasa_bcv:,.2f} VES**")
        st.caption(f"Tasa: {tasa_bcv:,.2f}")
    else:
        st.error("Sin datos")

with col_b:
    st.markdown("#### 🟡 Bolívares (Binance)")
    if tasa_ves:
        st.info(f"**{monto_usd * tasa_ves:,.2f} VES**")
        st.caption(f"Tasa: {tasa_ves:,.2f}")
    else:
        st.error("Sin datos")

with col_c:
    st.markdown("#### 🇨🇱 Pesos Chilenos (CLP)")
    if tasa_clp:
        st.warning(f"**${monto_usd * tasa_clp:,.0f} CLP**")
        st.caption(f"Tasa: ${tasa_clp:,.2f}")
    else:
        st.error("Sin datos")

