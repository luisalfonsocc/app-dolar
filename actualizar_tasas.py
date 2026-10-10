import json
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_tasa_usdt():
    """Obtiene el precio de compra/venta promedio de USDT P2P"""
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "merchantCheck": False,
            "page": 1,
            "rows": 5,
            "tradeType": "BUY"
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        data = resp.json()
        if data.get("data"):
            precios = [float(adv["adv"]["price"]) for adv in data["data"]]
            return round(sum(precios) / len(precios), 2)
    except Exception as e:
        print(f"Error obteniendo USDT Binance: {e}")

    # Respaldos alternativos si falla Binance
    try:
        resp = requests.get("https://ve.dolarapi.com/v1/dolares/cripto", timeout=5)
        if resp.status_code == 200:
            return float(resp.json().get("promedio", 1000.0))
    except Exception:
        pass

    return 1000.00 # Tasa por defecto si no hay conexión

def obtener_tasas_bcv():
    datos = {
        "bcv_dolar": None,
        "bcv_euro": None,
        "fecha_valor": None
    }
    try:
        url = "https://www.bcv.org.ve/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Dólar BCV
        contenedor_dolar = soup.find('div', id='dolar')
        if contenedor_dolar and contenedor_dolar.find('strong'):
            texto = contenedor_dolar.find('strong').text.strip()
            datos["bcv_dolar"] = float(texto.replace('.', '').replace(',', '.'))

        # Euro BCV
        contenedor_euro = soup.find('div', id='euro')
        if contenedor_euro and contenedor_euro.find('strong'):
            texto = contenedor_euro.find('strong').text.strip()
            datos["bcv_euro"] = float(texto.replace('.', '').replace(',', '.'))

        # Fecha Valor
        contenedor_fecha = soup.find('span', class_='date-display-single')
        if contenedor_fecha:
            datos["fecha_valor"] = contenedor_fecha.text.strip()

    except Exception as e:
        print(f"Error extrayendo datos del BCV: {e}")

    return datos

def main():
    datos = obtener_tasas_bcv()
    datos["usdt_ref"] = obtener_tasa_usdt()

    if not datos["bcv_dolar"]:
        datos["bcv_dolar"] = 876.80
    if not datos["bcv_euro"]:
        datos["bcv_euro"] = 982.00
    if not datos["fecha_valor"]:
        datos["fecha_valor"] = "Fecha Oficial BCV"

    with open("tasas.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

    print("Datos actualizados exitosamente:", datos)

if __name__ == "__main__":
    main()