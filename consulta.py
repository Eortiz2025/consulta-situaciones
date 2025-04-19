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
        st.success(f"✅ Se encontraron {len(resultados)} productos:")
        st.dataframe(resultados[['Nombre', 'Precio de venta con IVA', 'C¢digo EAN']])
    else:
        st.warning("⚠️ No se encontró ningún producto que coincida con tu búsqueda.")
else:
    st.info("👈 Escribe el nombre de un producto para buscar en el catálogo.")

# Descargar el catálogo completo
st.download_button(
    label="📥 Descargar Catálogo Completo",
    data=df_productos.to_csv(index=False).encode('utf-8'),
    file_name='catalogo_naturista.csv',
    mime='text/csv'
)
