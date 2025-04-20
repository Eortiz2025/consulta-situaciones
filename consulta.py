import streamlit as st
import pandas as pd
import openai

# Configurar tu API Key de OpenAI desde secrets (para futuras funciones si quieres usar IA)
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

# Función para cargar el catálogo naturista
@st.cache_data
def cargar_catalogo():
    df = pd.read_excel('naturista.xlsx')
    return df

# Cargar catálogo
df_productos = cargar_catalogo()

# Título de la App
st.title("🔎 Consulta - Karolo")

# Búsqueda tradicional por nombre de producto
st.header("🔍 Buscar Producto por Nombre")

busqueda_nombre = st.text_input("Escribe el nombre o parte del nombre del producto:")

if busqueda_nombre:
    resultados = df_productos[df_productos['Nombre'].str.contains(busqueda_nombre, case=False, na=False)]

    if not resultados.empty:
        st.success(f"✅ Se encontraron {len(resultados)} productos relacionados con tu búsqueda:")
        for index, row in resultados.iterrows():
            st.write(f"🔹 **Código: {row['Código']}** - {row['Nombre']} - **Precio:** ${int(row['Precio de venta con IVA'])}")
    else:
        st.warning("⚠️ No se encontró ningún producto que coincida con tu búsqueda.")

# Búsqueda por necesidad (nuevo módulo)
st.header("🩺 Buscar Productos por Necesidad de Salud")

consulta_necesidad = st.text_input("¿Qué necesidad tienes? (Ejemplo: circulación, próstata, diabetes)")

if consulta_necesidad:
    # Palabras clave relacionadas a cada necesidad
    necesidades = {
        'circulación': ['circulación', 'vascular', 'cardio', 'corazón', 'arterias', 'venas', 'sangre'],
        'próstata': ['próstata', 'prostata', 'prost', 'saw palmetto', 'serenoa', 'pygeum'],
        'diabetes': ['diabetes', 'glucosa', 'gluco', 'sugar', 'azúcar'],
        'defensas': ['defensas', 'inmunidad', 'inmune', 'vitamina c', 'equinácea', 'propóleo']
    }

    # Buscar las palabras claves asociadas a la necesidad escrita
    palabras_clave = necesidades.get(consulta_necesidad.lower(), [consulta_necesidad.lower()])

    filtro_necesidad = df_productos['Nombre'].str.contains('|'.join(palabras_clave), case=False, na=False)

    resultados_necesidad = df_productos[filtro_necesidad]

    if not resultados_necesidad.empty:
        st.success(f"✅ Encontramos {len(resultados_necesidad)} productos que pueden ayudarte con {consulta_necesidad}:")
        for index, row in resultados_necesidad.iterrows():
            st.write(f"🔹 **Código: {row['Código']}** - {row['Nombre']} - **Precio:** ${int(row['Precio de venta con IVA'])}")
    else:
        st.warning("⚠️ No se encontraron productos específicos para esa necesidad en nuestro catálogo.")
