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

# Función para limpiar texto (eliminar acentos y pasar a minúsculas)
def limpiar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto.lower()

# Función para extraer posibles ingredientes mencionados en la respuesta de OpenAI
def extraer_ingredientes_de_respuesta(texto):
    posibles = [
        "curcuma", "glucosamina", "condroitina", "omega", "manzanilla", "jengibre", "menta",
        "zinc", "vitamina", "probiotico", "spirulina", "ginkgo", "pasiflora", "hierba de sapo",
        "cuachalalate", "colageno", "magnesio", "resveratrol", "espirulina", "melatonina", "te verde",
        "eufrasia", "carbon activado"
    ]
    encontrados = []
    texto = limpiar_texto(texto)
    for palabra in posibles:
        if palabra in texto:
            encontrados.append(palabra)
    return list(set(encontrados))

# Función para consultar OpenAI sobre suplementos
def consultar_openai_suplementos(consulta):
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=300,
            messages=[
                {"role": "system", "content": """Eres un asesor experto en suplementos naturistas.
Tu tarea es recomendar suplementos o ingredientes naturales que puedan ayudar a aliviar o apoyar de forma complementaria el malestar, síntoma o condición que te describa el usuario.
Siempre responde mencionando directamente suplementos naturistas o ingredientes activos.
Evita dar consejos médicos, diagnósticos o recomendar consultas a médicos.
No uses frases genéricas como 'consulta a un profesional'.
Limítate a sugerir suplementos o combinaciones de suplementos que sean comunes en el ámbito naturista.
Sé concreto, breve y claro en tus recomendaciones."""},
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

    ingredientes_detectados = extraer_ingredientes_de_respuesta(respuesta_openai)

    # Buscar productos relacionados si el usuario quiere
    buscar_productos = st.checkbox("🔍 ¿Deseas ver productos relacionados en catálogo?")

    if buscar_productos:
        productos_relevantes = pd.DataFrame()
        nombre_columna_categoria = df_productos.columns[4]

        if not ingredientes_detectados:
            # Si no detectamos ingredientes, usamos la consulta del usuario directamente
            ingredientes_detectados = re.findall(r'\b[a-záéíóúñ]+\b', limpiar_texto(consulta_usuario))

        # Limpiar nombres de catálogo
        df_productos['nombre_limpio'] = df_productos['nombre'].apply(limpiar_texto)
        df_productos['categoria_limpio'] = df_productos[nombre_columna_categoria].apply(limpiar_texto)

        for ingrediente in ingredientes_detectados:
            coincidencias_nombre = df_productos[df_productos['nombre_limpio'].str.contains(ingrediente, na=False)]
            coincidencias_categoria = df_productos[df_productos['categoria_limpio'].str.contains(ingrediente, na=False)]
            productos_relevantes = pd.concat([productos_relevantes, coincidencias_nombre, coincidencias_categoria])

        productos_relevantes = productos_relevantes.drop_duplicates()

        # Filtrar para excluir ciertas categorías
        productos_filtrados = productos_relevantes[
            ~productos_relevantes[nombre_columna_categoria].str.lower().isin(categorias_excluidas)
        ].sort_values(by='nombre')

        if not productos_filtrados.empty:
            st.subheader("🎯 Productos sugeridos:")
            for idx, row in productos_filtrados.iterrows():
                try:
                    codigo = str(row.iloc[0])
                    nombre = row['nombre']
                    precio = float(row['precio de venta con iva'])
                    st.write(f"{codigo} | {nombre} | ${precio:,.2f}")
                except:
                    continue
        else:
            st.warning("⚠️ No se encontraron productos relevantes en catálogo.")
