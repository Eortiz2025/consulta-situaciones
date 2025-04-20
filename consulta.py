import streamlit as st
import pandas as pd
import openai

# Cargar tu API Key de OpenAI desde Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Función para cargar el catálogo
@st.cache_data
def cargar_catalogo():
    df = pd.read_excel('naturista.xlsx')
    return df

# Función mejorada para consultar a ChatGPT una descripción
def consultar_descripcion_chatgpt(nombre, ean):
    prompt = f"""
Eres un experto en suplementos naturistas. Explica brevemente, en máximo 400 caracteres, qué es y para qué sirve el siguiente producto:

Nombre: {nombre}
Código EAN: {ean}

Si no encuentras información exacta, da una respuesta general sobre las propiedades típicas de productos similares.
"""

    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente especializado en productos naturistas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.4
        )

        texto = respuesta.choices[0].message['content'].strip()
        return texto
    except Exception as e:
        return "No se encontró descripción disponible. Consulta con tu asesor naturista."

# Cargar el catálogo
df_productos = cargar_catalogo()

# Título principal
st.title("🔎 Consulta de Productos - Naturista (Con Descripción Inteligente Mejorada)")

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
                    descripcion = consultar_descripcion_chatgpt(row['Nombre'], str(row['Código EAN']))
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
                    descripcion = consultar_descripcion_chatgpt(row['Nombre'], str(row['Código EAN']))
                    st.info(f"ℹ️ **{row['Nombre']}**:\n\n{descripcion}")
        else:
            st.warning("⚠️ No se encontraron productos en esta serie.")
