import json
import os
import requests
import streamlit as st

st.set_page_config(page_title="Al Cambio Vzla", page_icon="💸", layout="centered")

def cargar_tasas():
    if os.path.exists("tasas.json"):
        try:
            with open("tasas.json", "r") as f:
                return json.load(f)
        except Exception:
            pass

    # Respaldo en vivo si aún no existe el JSON
    try:
        url = "https://www.bcv.org.ve/"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, verify=False, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        d_elem = soup.find('div', id='dolar')
        e_elem = soup.find('div', id='euro')
        
        d_val = float(d_elem.find('strong').text.strip().replace('.', '').replace(',', '.')) if d_elem else None
        e_val = float(e_elem.find('strong').text.strip().replace('.', '').replace(',', '.')) if e_elem else None
        return {"bcv_dolar": d_val, "bcv_euro": e_val}
    except Exception:
        return {"bcv_dolar": None, "bcv_euro": None}

tasas = cargar_tasas()
tasa_dolar = tasas.get("bcv_dolar")
tasa_euro = tasas.get("bcv_euro")

# --- CABECERA ---
st.markdown("<h2 style='text-align: center;'>💸 Al Cambio Vzla</h2>", unsafe_allow_html=True)

# Tarjetas de Tasas
col1, col2 = st.columns(2)
with col1:
    st.metric("💵 Dólar BCV", f"{tasa_dolar:,.2f} Bs" if tasa_dolar else "N/A")
with col2:
    st.metric("💶 Euro BCV", f"{tasa_euro:,.2f} Bs" if tasa_euro else "N/A")

st.divider()

# --- CALCULADORA ---
st.subheader("🧮 Calculadora Rápida")

if "monto_input" not in st.session_state:
    st.session_state.monto_input = 10.0

def limpiar():
    st.session_state.monto_input = 0.0

opcion = st.radio(
    "Convertir desde:",
    ["Dólares ($)", "Euros (€)", "Bolívares (Bs)"],
    horizontal=True
)

col_input, col_btn = st.columns([3, 1])
with col_input:
    monto = st.number_input(
        "Monto a calcular:",
        min_value=0.0,
        key="monto_input",
        step=5.0,
        format="%.2f"
    )

with col_btn:
    st.write("") # Espaciador para alinear con el input
    st.write("")
    st.button("🧹 Limpiar", on_click=limpiar, use_container_width=True)

st.write("---")

# Lógica de conversión
if opcion == "Dólares ($)":
    bs_val = monto * tasa_dolar if tasa_dolar else 0
    eur_val = (monto * tasa_dolar / tasa_euro) if (tasa_dolar and tasa_euro) else 0
    
    st.success(f"**🇻🇪 En Bolívares:** `{bs_val:,.2f} Bs`")
    st.info(f"**💶 Equivalente en Euros:** `{eur_val:,.2f} €`")

elif opcion == "Euros (€)":
    bs_val = monto * tasa_euro if tasa_euro else 0
    usd_val = (monto * tasa_euro / tasa_dolar) if (tasa_dolar and tasa_euro) else 0
    
    st.success(f"**🇻🇪 En Bolívares:** `{bs_val:,.2f} Bs`")
    st.info(f"**💵 Equivalente en Dólares:** `{usd_val:,.2f} $`")

else: # Bolívares (Bs)
    usd_val = monto / tasa_dolar if tasa_dolar else 0
    eur_val = monto / tasa_euro if tasa_euro else 0
    
    st.success(f"**💵 En Dólares ($):** `{usd_val:,.2f} $`")
    st.info(f"**💶 En Euros (€):** `{eur_val:,.2f} €`")

st.caption("💡 *Tip: Puedes presionar o mantener pulsado sobre el cuadro con borde de color para copiar el resultado directo al portapapeles.*")