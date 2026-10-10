import requests
from bs4 import BeautifulSoup
import urllib3

# Desactivamos advertencias de certificados SSL si la web del BCV da fallos
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_tasa_y_fecha_bcv():
    url = "https://www.bcv.org.ve/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        respuesta = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        # 1. Extraer la Tasa del Dólar
        contenedor_dolar = soup.find('div', id='dolar')
        tasa_dolar = None
        
        if contenedor_dolar:
            valor_texto = contenedor_dolar.find('strong').text.strip()
            valor_limpio = valor_texto.replace('.', '').replace(',', '.')
            tasa_dolar = float(valor_limpio)
            
        # 2. Extraer la Fecha de la Tasa
        contenedor_fecha = soup.find('span', class_='date-display-single')
        fecha_texto = "No encontrada"
        
        if contenedor_fecha:
            # El atributo 'content' guarda la fecha formateada o leemos el texto directo
            fecha_texto = contenedor_fecha.text.strip()

        return tasa_dolar, fecha_texto

    except Exception as e:
        print(f"Error de conexión con el BCV: {e}")
        return None, None

# --- PRUEBA DEL SCRIPT ---
if __name__ == "__main__":
    tasa, fecha = obtener_tasa_y_fecha_bcv()
    if tasa:
        print("\n===================================")
        print(f"TASA OFICIAL BCV: {tasa} VES")
        print(f"FECHA VALOR: {fecha}")
        print("===================================\n")