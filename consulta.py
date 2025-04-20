import streamlit as st
import pandas as pd
import wikipediaapi

# Cargar catálogo
@st.cache_data
def cargar_catalogo():
    df = pd.read_excel('naturista.xlsx')
    return df

# Función para buscar en Wikipedia
def buscar_en_wikipedia(producto):
    wiki_wiki = wikipediaapi.Wikipedia('es')  # idioma español
    page = wiki_wiki.page(producto)

    if page.exists():
        return page.summary[:500]  # Resumen de máximo 500 caracteres
    else:
        return "No se encontró información disponible en Wikipedia."

df_productos = cargar_catalogo()

# Título principal
st.title("🔎 Consulta de Productos - Naturista")

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
                    descripcion = buscar_en_wikipedia(row['Nombre'])
                    st.info(f"ℹ️ **{row['Nombre']}**: {descripcion}")
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
                    descripcion = buscar_en_wikipedia(row['Nombre'])
                    st.info(f"ℹ️ **{row['Nombre']}**: {descripcion}")
        else:
            st.warning("⚠️ No se encontraron productos en esta serie.")
