import json
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_tasas_bcv():
    tasas = {"dolar": None, "euro": None}
    try:
        url = "https://www.bcv.org.ve/"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Dólar
        contenedor_dolar = soup.find('div', id='dolar')
        if contenedor_dolar:
            texto = contenedor_dolar.find('strong').text.strip()
            tasas["dolar"] = float(texto.replace('.', '').replace(',', '.'))

        # Euro
        contenedor_euro = soup.find('div', id='euro')
        if contenedor_euro:
            texto = contenedor_euro.find('strong').text.strip()
            tasas["euro"] = float(texto.replace('.', '').replace(',', '.'))

    except Exception as e:
        print(f"Error extrayendo tasas del BCV: {e}")

    return tasas

def main():
    tasas = obtener_tasas_bcv()

    datos = {
        "bcv_dolar": tasas["dolar"],
        "bcv_euro": tasas["euro"]
    }

    with open("tasas.json", "w") as f:
        json.dump(datos, f, indent=4)

    print("Tasas del BCV actualizadas exitosamente:", datos)

if __name__ == "__main__":
    main()