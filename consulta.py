import streamlit as st
import pandas as pd
import openai
import re
import unicodedata

# Configurar API Key de OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Función para cargar el catálogo
@st.cache_data
def cargar_catalogo():
    try:
        return pd.read_excel('naturista.xlsx')
    except Exception as e:
        st.error(f"Error al cargar el catálogo: {e}")
        return pd.DataFrame()

# Función para normalizar texto (quitar acentos y minúsculas)
def normalizar(texto):
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8').lower()
    return texto

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

# Función para extraer ingredientes y presentaciones

def extraer_ingredientes_y_presentaciones(texto):
    texto = normalizar(texto)
    ingredientes_comunes = [
        "curcuma", "glucosamina", "condroitina", "omega", "manzanilla", "jengibre", "menta",
        "zinc", "vitamina", "probiotico", "espirulina", "melatonina", "colageno",
        "resveratrol", "hierba de sapo", "cuachalalate", "ginkgo", "te verde", "carbon activado"
    ]
    presentaciones_comunes = ["gotas", "colirio", "ojos", "vision", "ocular"]

    ingredientes_detectados = [i for i in ingredientes_comunes if i in texto]
    presentaciones_detectadas = [p for p in presentaciones_comunes if p in texto]
    
    return ingredientes_detectados, presentaciones_detectadas

# Cargar catálogo
catalogo = cargar_catalogo()
if not catalogo.empty:
    catalogo.columns = catalogo.columns.str.strip().str.lower()

nombre_columna_categoria = catalogo.columns[4]
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

    ingredientes, presentaciones = extraer_ingredientes_y_presentaciones(respuesta_openai + " " + consulta_usuario)

    if ingredientes or presentaciones:
        st.markdown("\n🔎 Detectamos estos criterios de búsqueda:")
        st.write(", ".join(ingredientes + presentaciones))

        buscar_productos = st.checkbox("🔍 ¿Deseas ver productos relacionados?")

        if buscar_productos:
            productos_relevantes = pd.DataFrame()
            nombre_columna_categoria = catalogo.columns[4]

            for keyword in ingredientes + presentaciones:
                coincidencias_nombre = catalogo[catalogo['nombre'].apply(normalizar).str.contains(keyword, na=False)]
                coincidencias_categoria = catalogo[catalogo[nombre_columna_categoria].apply(normalizar).str.contains(keyword, na=False)]
                productos_relevantes = pd.concat([productos_relevantes, coincidencias_nombre, coincidencias_categoria])

            productos_relevantes = productos_relevantes.drop_duplicates()

            productos_filtrados = productos_relevantes[
                ~catalogo[nombre_columna_categoria].astype(str).str.lower().isin(categorias_excluidas)
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
        st.warning("⚠️ No detectamos criterios claros para buscar productos relacionados.")
