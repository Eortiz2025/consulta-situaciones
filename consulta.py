import streamlit as st
import pandas as pd
import openai
import re
import unicodedata

# Configurar API Key de OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Función para cargar el catálogo naturista
@st.cache_data
def cargar_catalogo():
    try:
        return pd.read_excel('naturista.xlsx')
    except Exception as e:
        st.error(f"Error al cargar el catálogo: {e}")
        return pd.DataFrame()

# Función para normalizar texto (sin acentos)
def normalizar(texto):
    if isinstance(texto, str):
        return ''.join(
            c for c in unicodedata.normalize('NFKD', texto)
            if not unicodedata.combining(c)
        ).lower()
    return texto

# Función para consultar OpenAI sobre suplementos
def consultar_openai_suplementos(consulta):
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=400,
            messages=[
                {"role": "system", "content": """
Eres un asesor experto en suplementos naturistas.
Tu tarea es recomendar suplementos o ingredientes naturales que puedan ayudar a aliviar o apoyar de forma complementaria el malestar, síntoma o condición que te describa el usuario.
Siempre responde mencionando directamente suplementos naturistas o ingredientes activos principales y, si aplica, también algunos complementarios relevantes de forma breve.
Evita dar consejos médicos, diagnósticos o recomendar consultas a médicos.
No uses frases genéricas como 'consulta a un profesional'.
Limítate a sugerir suplementos o combinaciones de suplementos que sean comunes en el ámbito naturista.
Sé concreto, breve y claro en tus recomendaciones, enfocándote en suplementos que apoyen de manera natural el bienestar de la persona.
"""},  
                {"role": "user", "content": consulta}
            ]
        )
        return respuesta.choices[0].message['content'].strip()
    except Exception as e:
        return f"❌ Error consultando OpenAI: {e}"

# Cargar catálogo
df_productos = cargar_catalogo()
if not df_productos.empty:
    df_productos.columns = df_productos.columns.str.strip().str.lower()

# Categorías que no deben mostrarse
categorias_excluidas = ["abarrote", "bebidas", "belleza", "snacks"]

# Interfaz
st.title("🔎 Consulta - Karolo")
st.header("👋 Hola, ¿En qué te puedo ayudar?")

consulta_usuario = st.text_input("✍️ Escribe tu necesidad o pregunta:")

if consulta_usuario:
    st.info("🔎 Procesando tu consulta...")

    with st.spinner("Consultando asesor experto..."):
        respuesta_openai = consultar_openai_suplementos(consulta_usuario)
    st.success(f"ℹ️ {respuesta_openai}")

    buscar_productos = st.checkbox("🔍 ¿Deseas ver productos relacionados en catálogo?")

    if buscar_productos and not df_productos.empty:
        productos_relevantes = pd.DataFrame()
        nombre_columna_categoria = df_productos.columns[4]

        consulta_normalizada = normalizar(consulta_usuario)

        for idx, row in df_productos.iterrows():
            nombre_producto = normalizar(str(row['nombre']))
            categoria_producto = normalizar(str(row[nombre_columna_categoria]))
            
            if (
                any(palabra in nombre_producto for palabra in consulta_normalizada.split())
                or any(palabra in categoria_producto for palabra in consulta_normalizada.split())
            ) and categoria_producto not in categorias_excluidas:
                productos_relevantes = pd.concat([productos_relevantes, pd.DataFrame([row])])

        productos_relevantes = productos_relevantes.drop_duplicates().sort_values(by='nombre')

        if not productos_relevantes.empty:
            st.subheader("🎯 Productos sugeridos:")
            for idx, row in productos_relevantes.iterrows():
                try:
                    codigo = str(row.iloc[0])
                    nombre = row['nombre']
                    precio = float(row['precio de venta con iva'])
                    st.write(f"{codigo} | {nombre} | ${precio:,.2f}")
                except:
                    continue
        else:
            st.warning("⚠️ No se encontraron productos relevantes en catálogo.")
