import streamlit as st
import pandas as pd
import openai
import re

# Configurar tu API Key de OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Función para cargar el catálogo naturista
@st.cache_data
def cargar_catalogo():
    return pd.read_excel('naturista.xlsx')

# Función para consultar ChatGPT sobre palabras clave
def obtener_palabras_clave(necesidad_usuario):
    prompt = f"""
Eres un experto en suplementos naturistas.

Basándote en la necesidad que describe el usuario ("{necesidad_usuario}"),
enumera de manera breve 5 a 10 ingredientes o suplementos naturales que puedan ayudar a esta necesidad.
Proporciona solo una lista separada por comas, sin explicaciones.

Ejemplo:
ajo negro, ginkgo biloba, cúrcuma, omega 3
"""
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=150,
            messages=[
                {"role": "system", "content": "Eres un asesor experto en suplementos naturistas."},
                {"role": "user", "content": prompt}
            ]
        )
        texto = respuesta.choices[0].message['content'].strip()
        palabras_clave = [palabra.strip().lower() for palabra in texto.split(',')]
        return palabras_clave
    except Exception as e:
        st.error(f"❌ Error en la conexión a OpenAI: {e}")
        return []

# Función para obtener una breve descripción de un producto
def obtener_descripcion_producto(nombre_producto):
    prompt = f"""
Eres un asesor experto en suplementos naturistas.

Dame una breve descripción de máximo 2 líneas explicando para qué podría servir un suplemento llamado "{nombre_producto}".
No repitas el nombre ni inventes efectos médicos exagerados.
"""
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=150,
            messages=[
                {"role": "system", "content": "Eres un asesor experto en suplementos naturistas."},
                {"role": "user", "content": prompt}
            ]
        )
        descripcion = respuesta.choices[0].message['content'].strip()
        return descripcion
    except Exception as e:
        return f"❌ Error: {e}"

# Cargar catálogo
df_productos = cargar_catalogo()

# Palabras prohibidas para filtrar productos no adecuados
palabras_prohibidas = ['incienso', 'shampoo', 'jabón', 'jabon', 'loción', 'locion', 'spray', 'aroma', 'ambientador']

# Título principal
st.title("🔎 Consulta - Karolo (Flujo Inteligente Mejorado)")

# Saludo inicial
st.header("👋 Hola, ¿en qué puedo ayudarte hoy?")

# Mensaje de orientación para el usuario
st.markdown(
    """
    🧠 Puedes preguntarme libremente:
    
    - Quiero algo para la circulación
    - ¿Qué recomiendas para fortalecer defensas?
    - ¿Tienes algo para la diabetes?
    - Me siento cansado, ¿qué puedo tomar?

    ¡Estoy aquí para ayudarte! 🌟
    """
)

# Entrada del usuario
consulta_necesidad = st.text_input("Escribe tu necesidad:")

if consulta_necesidad:
    st.info("🔎 Consultando al asesor experto...")
    palabras_clave = obtener_palabras_clave(consulta_necesidad)

    if palabras_clave:
        st.success(f"✅ Basado en tu necesidad, se buscarán productos relacionados con: {', '.join(palabras_clave)}")

        # Buscar productos que contengan alguna palabra clave
        filtro = df_productos['Nombre'].str.contains('|'.join(palabras_clave), case=False, na=False)

        # Filtro adicional para evitar productos no adecuados
        def es_producto_valido(nombre):
            return not any(prohibida in nombre.lower() for prohibida in palabras_prohibidas)

        resultados = df_productos[filtro]
        resultados = resultados[resultados['Nombre'].apply(es_producto_valido)]

        if not resultados.empty:
            st.subheader("🎯 Productos sugeridos:")
            for index, row in resultados.iterrows():
                st.write(f"🔹 **Código: {row['Código']}** - {row['Nombre']} - **Precio:** ${int(row['Precio de venta con IVA'])}")

                # Botón para ver más detalles
                if st.button(f"🔎 Ver más detalles - {row['Código']}", key=f"detalle_{row['Código']}"):
                    descripcion = obtener_descripcion_producto(row['Nombre'])
                    st.info(f"ℹ️ {descripcion}")
        else:
            st.warning("⚠️ No encontramos productos relevantes en tu catálogo.")
    else:
        st.warning("⚠️ No se pudieron generar palabras clave. Intenta describir tu necesidad de otra forma.")
