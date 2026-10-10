import json
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_bcv():
    try:
        url = "https://www.bcv.org.ve/"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, verify=False, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        contenedor = soup.find('div', id='dolar')
        if contenedor:
            texto = contenedor.find('strong').text.strip()
            return float(texto.replace('.', '').replace(',', '.'))
    except Exception as e:
        print(f"Error BCV: {e}")
    return None

def obtener_binance(fiat):
    try:
        url = f"https://criptoya.com/api/binancep2p/usdt/{fiat.lower()}/5"
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            precios = [float(item["price"]) for item in data.get("data", [])[:5]]
            if precios:
                return round(sum(precios) / len(precios), 2)
    except Exception as e:
        print(f"Error Binance {fiat}: {e}")
    return None

def main():
    tasa_bcv = obtener_bcv()
    tasa_ves = obtener_binance("VES")
    tasa_clp = obtener_binance("CLP")

    datos = {
        "bcv": tasa_bcv,
        "binance_ves": tasa_ves,
        "binance_clp": tasa_clp
    }

    with open("tasas.json", "w") as f:
        json.dump(datos, f, indent=4)

    print("Tasas actualizadas con éxito:", datos)

if __name__ == "__main__":
    main()