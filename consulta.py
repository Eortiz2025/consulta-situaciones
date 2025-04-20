import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Función para cargar el catálogo
@st.cache_data
def cargar_catalogo():
    df = pd.read_excel('naturista.xlsx')
    return df

# Función para buscar una breve descripción en DuckDuckGo
def buscar_descripcion_producto(nombre, ean):
    try:
        query = f"{nombre} {ean} para qué sirve"
        url = f"https://duckduckgo.com/html/?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return "No se encontró descripción disponible."

        soup = BeautifulSoup(res.text, "html.parser")
        results = soup.find_all('a', class_='result__a')

        if results:
            primer_resultado = results[0].text
            return primer_resultado[:400]  # Máximo 400 caracteres
        else:
            return "No se encontró descripción disponible."
    except Exception as e:
        return "No se encontró descripción disponible."

# Cargar datos
df_productos = cargar_catalogo()

# Título principal
st.title("🔎 Consulta de Productos - Naturista (Descripción automática)")

# Tipo de búsqueda
tipo_busqueda = st.selectbox(
    "¿Cómo quieres buscar?",
    ["Por Nombre", "Por Serie"]
)

# Buscar por Nombre
if tipo_busqueda == "Por Nombre":
    busqueda_nombre = st.text_input("Escribe el nombre o parte del nombre del producto:")

    if busqueda_nombre:
        resultados = df_productos[df_productos['Nombre'].str.contains(busqueda_nombre, case=False, na=False)]

        if not resultados.empty:
            st.success(f"✅ Se encontraron {len(resultados)} productos:")

            for index, row in resultados.iterrows():
                if st.checkbox(f"{row['Código']} - {row['Nombre']} (${int(row['Precio de venta con IVA'])})", key=f"prod_{index}"):
                    descripcion = buscar_descripcion_producto(row['Nombre'], str(row['Código EAN']))
                    st.info(f"ℹ️ **{row['Nombre']}**:\n\n{descripcion}")
        else:
            st.warning("⚠️ No se encontró ningún producto que coincida con tu búsqueda.")

# Buscar por Serie
elif tipo_busqueda == "Por Serie":
    series_disponibles = df_productos['Serie de producto'].dropna().unique()
    serie_seleccionada = st.selectbox("Selecciona una serie de producto:", options=sorted(series_disponibles))

    if serie_seleccionada:
        resultados = df_productos[df_productos['Serie de producto'] == serie_seleccionada]

        if not resultados.empty:
            st.success(f"✅ Se encontraron {len(resultados)} productos en la serie seleccionada:")

            for index, row in resultados.iterrows():
                if st.checkbox(f"{row['Código']} - {row['Nombre']} (${int(row['Precio de venta con IVA'])})", key=f"serie_{index}"):
                    descripcion = buscar_descripcion_producto(row['Nombre'], str(row['Código EAN']))
                    st.info(f"ℹ️ **{row['Nombre']}**:\n\n{descripcion}")
        else:
            st.warning("⚠️ No se encontraron productos en esta serie.")
