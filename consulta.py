import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Función para cargar el catálogo
@st.cache_data
def cargar_catalogo():
    df = pd.read_excel('naturista.xlsx')
    return df

# Función para buscar imagen en Google Images usando Código EAN
def buscar_imagen_google(ean):
    query = ean
    url = f"https://www.google.com/search?hl=es&tbm=isch&q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        images = soup.find_all("img")

        if len(images) > 1:
            imagen_url = images[1]["src"]  # La primera es el logo, la segunda ya es producto
            return imagen_url
        else:
            return None
    except Exception as e:
        return None

# Cargar datos
df_productos = cargar_catalogo()

# Título principal
st.title("🔎 Consulta de Productos - Naturista (con imágenes vía Código EAN)")

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

            # Mostrar productos con checkbox
            for index, row in resultados.iterrows():
                if st.checkbox(f"{row['Código']} - {row['Nombre']} (${int(row['Precio de venta con IVA'])})", key=f"prod_{index}"):
                    imagen_url = buscar_imagen_google(str(row['Código EAN']))

                    if imagen_url:
                        st.image(imagen_url, caption=row['Nombre'], use_column_width=True)
                    else:
                        st.warning("⚠️ Imagen no disponible para este producto.")
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

            # Mostrar productos con checkbox
            for index, row in resultados.iterrows():
                if st.checkbox(f"{row['Código']} - {row['Nombre']} (${int(row['Precio de venta con IVA'])})", key=f"serie_{index}"):
                    imagen_url = buscar_imagen_google(str(row['Código EAN']))

                    if imagen_url:
                        st.image(imagen_url, caption=row['Nombre'], use_column_width=True)
                    else:
                        st.warning("⚠️ Imagen no disponible para este producto.")
        else:
            st.warning("⚠️ No se encontraron productos en esta serie.")
