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
        return respuesta.choices[0].message['content'].strip()
    except Exception as e:
        return f"❌ Error: {e}"

# Función para filtrar productos no adecuados
def es_producto_valido(nombre):
    palabras_prohibidas = ['incienso', 'shampoo', 'jabón', 'jabon', 'loción', 'locion', 'spray', 'aroma', 'ambientador']
    return not any(p in nombre.lower() for p in palabras_prohibidas)

# Cargar catálogo
df_productos = cargar_catalogo()

# Interfaz
st.title("🔎 Consulta - Karolo")
st.header("👋 Hola, ¿en qué puedo ayudarte hoy?")

st.markdown("""
🧠 Puedes preguntarme libremente:

- Quiero algo para la circulación  
- ¿Qué recomiendas para fortalecer defensas?  
- ¿Tienes algo para la diabetes?  
- Me siento cansado, ¿qué puedo tomar?

¡Estoy aquí para ayudarte! 🌟
""")

consulta_necesidad = st.text_input("Escribe tu necesidad:")

if consulta_necesidad:
    st.info("🔎 Buscando coincidencias por palabras clave...")

    # Convertir la consulta a palabras clave individuales
    palabras_usuario = re.findall(r'\b\w+\b', consulta_necesidad.lower())
    filtro_directo = df_productos['Nombre'].str.contains('|'.join(palabras_usuario), case=False, na=False)
    resultados_directos = df_productos[filtro_directo]
    resultados_directos = resultados_directos[resultados_directos['Nombre'].apply(es_producto_valido)]

    if not resultados_directos.empty:
        st.success("✅ Encontramos productos directamente relacionados con tu consulta:")
        for _, row in resultados_directos.iterrows():
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                ver = st.checkbox("", key=f"directo_{row['Código']}")
            with col2:
                st.write(f"🔹 **Código: {row['Código']}** - {row['Nombre']} - **Precio:** ${int(row['Precio de venta con IVA'])}")
            if ver:
                descripcion = obtener_descripcion_producto(row['Nombre'])
                st.info(f"ℹ️ {descripcion}")
    else:
        st.info("🤖 No hubo coincidencias directas. Consultando al asesor experto...")
        palabras_clave = obtener_palabras_clave(consulta_necesidad)

        if palabras_clave:
            st.success(f"🔍 Buscando con las palabras sugeridas por el asesor: {', '.join(palabras_clave)}")

            filtro = df_productos['Nombre'].str.contains('|'.join(palabras_clave), case=False, na=False)
            resultados = df_productos[filtro]
            resultados = resultados[resultados['Nombre'].apply(es_producto_valido)]

            if not resultados.empty:
                st.subheader("🎯 Productos sugeridos:")
                for _, row in resultados.iterrows():
                    col1, col2 = st.columns([0.1, 0.9])
                    with col1:
                        ver = st.checkbox("", key=f"detalle_{row['Código']}")
                    with col2:
                        st.write(f"🔹 **Código: {row['Código']}** - {row['Nombre']} - **Precio:** ${int(row['Precio de venta con IVA'])}")
                    if ver:
                        descripcion = obtener_descripcion_producto(row['Nombre'])
                        st.info(f"ℹ️ {descripcion}")
            else:
                st.warning("⚠️ No se encontraron productos con las palabras sugeridas.")
        else:
            st.warning("⚠️ No se pudieron generar sugerencias. Reformula tu pregunta si deseas.")
