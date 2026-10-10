import json
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_tasas():
    datos = {
        "bcv_dolar": None,
        "bcv_euro": None,
        "fecha_valor": None,
        "usdt_ref": 1000.00  # Tasa de referencia USDT
    }
    try:
        url = "https://www.bcv.org.ve/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
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
    datos = obtener_tasas()

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