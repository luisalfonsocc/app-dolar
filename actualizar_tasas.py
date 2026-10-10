import json
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_tasas_bcv():
    tasas = {"bcv_dolar": None, "bcv_euro": None}
    try:
        url = "https://www.bcv.org.ve/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Dólar
        contenedor_dolar = soup.find('div', id='dolar')
        if contenedor_dolar and contenedor_dolar.find('strong'):
            texto = contenedor_dolar.find('strong').text.strip()
            tasas["bcv_dolar"] = float(texto.replace('.', '').replace(',', '.'))

        # Euro
        contenedor_euro = soup.find('div', id='euro')
        if contenedor_euro and contenedor_euro.find('strong'):
            texto = contenedor_euro.find('strong').text.strip()
            tasas["bcv_euro"] = float(texto.replace('.', '').replace(',', '.'))

    except Exception as e:
        print(f"Error extrayendo tasas del BCV: {e}")

    return tasas

def main():
    tasas = obtener_tasas_bcv()

    # Si por alguna razón no extrae alguna tasa, poner valores por defecto de seguridad
    if not tasas["bcv_dolar"]:
        tasas["bcv_dolar"] = 36.50
    if not tasas["bcv_euro"]:
        tasas["bcv_euro"] = 39.50

    with open("tasas.json", "w") as f:
        json.dump(tasas, f, indent=4)

    print("Tasas del BCV guardadas exitosamente:", tasas)

if __name__ == "__main__":
    main()