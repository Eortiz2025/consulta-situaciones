import streamlit as st
import pandas as pd

# Cargar catálogo de productos desde un archivo Excel
@st.cache_data
def cargar_catalogo():
    df = pd.read_excel('naturista.xlsx')
    return df

df_productos = cargar_catalogo()

# MOSTRAR las columnas encontradas para diagnosticar
st.write("Columnas encontradas:", df_productos.columns.tolist())

# Título principal
st.title("🔎 Consulta de Productos - Naturista")

# Pregunta inicial: ¿Qué tipo de producto estás buscando?
st.subheader("¿Qué tipo de producto estás buscando?")

# Obtener las opciones únicas de 'Serie de producto'
series_disponibles = df_productos['Serie de producto'].dropna().unique()
serie_seleccionada = st.selectbox("Selecciona una serie de producto:", options=sorted(series_disponibles))

# Campo de búsqueda adicional
busqueda = st.text_input("Escribe el nombre o parte del nombre del producto:")

# Resultado de búsqueda
if serie_seleccionada:
    # Filtrar primero por serie
    filtro_serie = df_productos[df_productos['Serie de producto'] == serie_seleccionada]

    if busqueda:
        # Luego filtrar por nombre
        resultados = filtro_serie[filtro_serie['Nombre'].str.contains(busqueda, case=False, na=False)]
    else:
        resultados = filtro_serie

    if not resultados.empty:
        # Preparar los resultados para mostrar
        resultados_mostrar = resultados[['Código', 'Nombre', 'Serie de producto', 'Precio de venta con IVA']].copy()
        resultados_mostrar['Precio de venta con IVA'] = resultados_mostrar['Precio de venta con IVA'].astype(int)
        resultados_mostrar = resultados_mostrar.rename(columns={'Precio de venta con IVA': 'Precio'})

        st.success(f"✅ Se encontraron {len(resultados_mostrar)} productos:")
        st.dataframe(resultados_mostrar)
    else:
        st.warning("⚠️ No se encontró ningún producto que coincida con tu búsqueda en esta serie.")
