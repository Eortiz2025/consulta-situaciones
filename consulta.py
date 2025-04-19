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

# Campo de búsqueda
busqueda = st.text_input("Escribe el nombre o parte del nombre del producto:")

# Resultado de búsqueda
if busqueda:
    resultados = df_productos[df_productos['Nombre'].str.contains(busqueda, case=False, na=False)]

    if not resultados.empty:
        # Preparar los resultados para mostrar
        resultados_mostrar = resultados[['Código', 'Nombre', 'Precio de venta con IVA']].copy()
        resultados_mostrar['Precio de venta con IVA'] = resultados_mostrar['Precio de venta con IVA'].astype(int)  # Convertir precio a entero
        resultados_mostrar = resultados_mostrar.rename(columns={'Precio de venta con IVA': 'Precio'})  # Renombrar columna
        
        st.success(f"✅ Se encontraron {len(resultados_mostrar)} productos:")
        st.dataframe(resultados_mostrar)
    else:
        st.warning("⚠️ No se encontró ningún producto que coincida con tu búsqueda.")
else:
    st.info("👈 Escribe el nombre de un producto para buscar en el catálogo.")
