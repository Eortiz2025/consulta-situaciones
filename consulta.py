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

# Función para normalizar texto (quita acentos y convierte a minúsculas)
def normalizar_texto(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()

# Función para extraer posibles ingredientes naturales desde la respuesta
def extraer_ingredientes(texto):
    palabras_clave = [
        "cúrcuma", "glucosamina", "condroitina", "omega", "manzanilla", "jengibre", "menta",
        "zinc", "vitamina", "probiótico", "probiotico", "espirulina", "ginkgo", "pasiflora",
        "hierba de sapo", "cuachalalate", "colágeno", "magnesio", "resveratrol", "melatonina",
        "té verde", "carbon activado", "carbón activado"
    ]
    texto_normalizado = normalizar_texto(texto)
    encontrados = []
    for palabra in palabras_clave:
        palabra_normalizada = normalizar_texto(palabra)
        if palabra_normalizada in texto_normalizado:
            encontrados.append(palabra_normalizada)
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

    # Buscar ingredientes naturales detectados
    ingredientes_detectados = extraer_ingredientes(respuesta_openai)

    if ingredientes_detectados:
        st.markdown("🔎 Detectamos estos ingredientes relevantes:")
        st.write(", ".join(ingredientes_detectados))

        buscar_productos = st.checkbox("🔍 ¿Deseas ver productos relacionados en catálogo?")

        if buscar_productos:
            productos_relevantes = pd.DataFrame()
            nombre_columna_categoria = df_productos.columns[4]

            for ingrediente in ingredientes_detectados:
                # Buscar en nombre normalizado
                coincidencias_nombre = df_productos[
                    df_productos['nombre'].apply(lambda x: ingrediente in normalizar_texto(x))
                ]

                # Buscar en categoría normalizada
                coincidencias_categoria = df_productos[
                    df_productos[nombre_columna_categoria].apply(lambda x: ingrediente in normalizar_texto(x))
                ]

                productos_relevantes = pd.concat([productos_relevantes, coincidencias_nombre, coincidencias_categoria])

            productos_relevantes = productos_relevantes.drop_duplicates()

            # Filtrar para excluir ciertas categorías
            productos_filtrados = productos_relevantes[
                ~df_productos[nombre_columna_categoria].astype(str).str.lower().isin(categorias_excluidas)
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
    else:
        st.warning("⚠️ No detectamos ingredientes específicos para buscar productos relacionados.")
