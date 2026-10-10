import requests

def obtener_tasa_binance(moneda="VES"):
    moneda = moneda.upper()
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/trade-offer/search"
    
    payload = {
        "asset": "USDT",
        "fiat": moneda,
        "merchantCheck": False,
        "page": 1,
        "rows": 5,
        "tradeType": "BUY",
        "publisherType": None,
        "payTypes": []
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        respuesta = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            ofertas = datos.get("data", [])
            
            if ofertas:
                precios = []
                print(f"\n--- OFERTAS DESTACADAS BINANCE P2P ({moneda}) ---")
                for i, oferta in enumerate(ofertas, 1):
                    precio = float(oferta["adv"]["price"])
                    comerciante = oferta["advertiser"]["nickName"]
                    precios.append(precio)
                    print(f"{i}. {comerciante} -> {precio:,.2f} {moneda}")

                promedio = sum(precios) / len(precios)
                return round(promedio, 2)
            else:
                print(f"Binance respondió 200 pero la lista de ofertas vino vacía para {moneda}.")
        else:
            print(f"Binance devolvió código HTTP {respuesta.status_code} para {moneda}.")

    except Exception as e:
        print(f"Error en la conexión con Binance ({moneda}): {e}")

    return None

# --- PRUEBA DEL SCRIPT ---
if __name__ == "__main__":
    tasa_ves = obtener_tasa_binance("VES")
    tasa_clp = obtener_tasa_binance("CLP")

    print("\n===================================")
    print(f"PROMEDIO BINANCE P2P (VES): {tasa_ves if tasa_ves else 'Sin datos'} VES/USDT")
    print(f"PROMEDIO BINANCE P2P (CLP): {tasa_clp if tasa_clp else 'Sin datos'} CLP/USDT")
    print("===================================\n")