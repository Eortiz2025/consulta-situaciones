import streamlit as st
import pandas as pd
import openai
import re

# Cargar API Key de OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Función para cargar el catálogo naturista
@st.cache_data
def cargar_catalogo():
    return pd.read_excel('naturista.xlsx')

# Función para preguntar a ChatGPT qué ingredientes o suplementos ayudarían
def obtener_palabras_clave(necesidad_usuario):
    prompt = f"""
Eres un experto en suplementos naturistas.

Basándote en la necesidad que describe el usuario ("{necesidad_usuario}"),
enumera de manera breve 5 a 10 ingredientes o suplementos naturales que puedan ayudar a esta necesidad.
Solo proporciona una lista separada por comas. No expliques nada adicional.

Ejemplo de formato:
ajo negro, ginkgo biloba, cúrcuma, omega 3
"""

    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=150,
            messages=[
                {"role": "system", "content": "Eres un asesor de suplementos naturistas."},
                {"role": "user", "content": prompt}
            ]
        )
        texto = respuesta.choices[0].message['content'].strip()
        palabras_clave = [palabra.strip().lower() for palabra in texto.split(',')]
        return palabras_clave
    except Exception as e:
        st.error(f"❌ Error en la conexión a OpenAI: {e}")
        return []

# Cargar catálogo
df_productos = cargar_catalogo()

# Título de la app
st.title("🔎 Consulta - Karolo (Flujo Inteligente)")

# Ingresar necesidad libre
st.header("🩺 ¿Qué necesidad tienes? (Describe libremente)")

consulta_necesidad = st.text_input("Por ejemplo: circulación, hígado, defensas, cansancio...")

if consulta_necesidad:
    st.info("🔎 Consultando al asesor experto en suplementos naturistas...")
    palabras_clave = obtener_palabras_clave(consulta_necesidad)

    if palabras_clave:
        st.success(f"✅ Basado en tu necesidad, se buscarán productos relacionados con: {', '.join(palabras_clave)}")

        # Buscar productos que contengan alguna palabra clave
        filtro = df_productos['Nombre'].str.contains('|'.join(palabras_clave), case=False, na=False)
        resultados = df_productos[filtro]

        if not resultados.empty:
            st.subheader("🎯 Productos sugeridos:")
            for index, row in resultados.iterrows():
                st.write(f"🔹 **Código: {row['Código']}** - {row['Nombre']} - **Precio:** ${int(row['Precio de venta con IVA'])}")
        else:
            st.warning("⚠️ No encontramos productos relacionados en el catálogo.")
    else:
        st.warning("⚠️ No se pudieron generar palabras clave. Intenta reformular tu necesidad.")
