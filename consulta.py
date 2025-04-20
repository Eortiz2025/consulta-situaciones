import streamlit as st
import pandas as pd

# Cargar catálogo de productos desde un archivo Excel
@st.cache_data
def cargar_catalogo():
    df = pd.read_excel('naturista.xlsx')
    return df

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
            resultados_mostrar = resultados[['Código', 'Nombre', 'Serie de producto', 'Precio de venta con IVA']].copy()
            resultados_mostrar['Precio de venta con IVA'] = resultados_mostrar['Precio de venta con IVA'].astype(int)
            resultados_mostrar = resultados_mostrar.rename(columns={'Precio de venta con IVA': 'Precio'})

            st.success(f"✅ Se encontraron {len(resultados_mostrar)} productos:")
            st.dataframe(resultados_mostrar)
        else:
            st.warning("⚠️ No se encontró ningún producto que coincida con tu búsqueda.")

# Buscar por Serie
elif tipo_busqueda == "Por Serie":
    series_disponibles = df_productos['Serie de producto'].dropna().unique()
    serie_seleccionada = st.selectbox("Selecciona una serie de producto:", options=sorted(series_disponibles))

    if serie_seleccionada:
        resultados = df_productos[df_productos['Serie de producto'] == serie_seleccionada]

        if not resultados.empty:
            resultados_mostrar = resultados[['Código', 'Nombre', 'Serie de producto', 'Precio de venta con IVA']].copy()
            resultados_mostrar['Precio de venta con IVA'] = resultados_mostrar['Precio de venta con IVA'].astype(int)
            resultados_mostrar = resultados_mostrar.rename(columns={'Precio de venta con IVA': 'Precio'})

            st.success(f"✅ Se encontraron {len(resultados_mostrar)} productos en la serie seleccionada:")
            st.dataframe(resultados_mostrar)
        else:
            st.warning("⚠️ No se encontraron productos en esta serie.")
