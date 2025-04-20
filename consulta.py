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

# Función para consultar a ChatGPT una descripción basada en el nombre
def consultar_descripcion_chatgpt(nombre, ean):
    prompt = f"""
Eres un experto en suplementos naturistas.

Basándote únicamente en el nombre del producto "{nombre}", explica en máximo 400 caracteres qué beneficios o propiedades naturales podría tener.

No necesitas buscar información específica de la marca ni del código EAN {ean}. Solo usa tu conocimiento general sobre suplementos naturistas.

Escribe de forma breve, clara, positiva y enfocada a beneficios de salud.
"""

    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en productos naturistas y suplementos."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )

        texto = respuesta.choices[0].message['content'].strip()
        return texto
    except Exception as e:
        st.error(f"❌ Error en la conexión a OpenAI: {e}")
        return "No se pudo obtener la descripción por un error técnico."

# Cargar el catálogo
df_productos = cargar_catalogo()

# Título corregido
st.title("🔎 Consulta - Karolo")

# Búsqueda solo por Nombre
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
