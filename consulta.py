import streamlit as st
import pandas as pd
import openai
import re

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

# Mapeo interno: palabras clave asociadas a categorías reales
mapa_categorias = {
    "visión": "ojos",
    "vista": "ojos",
    "ojos": "ojos",
    "ocular": "ojos",
    "circulación": "circulacion",
    "sangre": "circulacion",
    "varices": "circulacion",
    "energía": "energia",
    "cansancio": "energia",
    "fatiga": "energia",
    "defensas": "vitaminas",
    "inmunidad": "vitaminas",
    "gripas": "vitaminas",
    "digestión": "digestion",
    "estómago": "digestion",
    "colon": "digestion",
    "hígado": "higado",
    "desintoxicar": "higado",
    "articulaciones": "articulaciones",
    "rodillas": "articulaciones",
    "huesos": "articulaciones",
    "diabetes": "diabetes",
    "azúcar": "diabetes",
    "ansiedad": "tranquilidad",
    "dormir": "tranquilidad",
    "nervios": "tranquilidad",
    "pulmones": "respiratorio",
    "tos": "respiratorio",
    "bronquios": "respiratorio",
    "memoria": "funcion cerebral",
    "concentración": "funcion cerebral",
}

# Función para detectar si es una pregunta sobre beneficios
def detectar_consulta_beneficio(texto):
    patrones = ["para qué sirve", "beneficio", "beneficios", "ayuda", "utilidad",
                "para que sirve", "para que es bueno", "para qué es bueno", "qué beneficios", "qué hace"]
    texto = texto.lower()
    return any(patron in texto for patron in patrones)

# Función para extraer posible ingrediente
def extraer_ingrediente(texto):
    palabras = re.findall(r'\b[a-záéíóúñ]+\b', texto.lower())
    exclusiones = {"para", "qué", "sirve", "beneficio", "beneficios", "ayuda", "utilidad", "es", "el", "la", "los", "las", "un", "una", "de", "del", "en", "con", "y", "bueno", "hace"}
    ingredientes = [palabra for palabra in palabras if palabra not in exclusiones]
    return ingredientes[0] if ingredientes else ""

# Función para consultar OpenAI sobre beneficio de un ingrediente
def consultar_openai_beneficio(ingrediente):
    mensaje_usuario = f"¿Para qué sirve el suplemento naturista {ingrediente}?"
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=150,
            messages=[
                {"role": "system", "content": "Eres un asesor experto en suplementos naturistas. Responde de forma clara, breve y sin prometer curas."},
                {"role": "user", "content": mensaje_usuario}
            ]
        )
        return respuesta.choices[0].message['content'].strip()
    except Exception as e:
        return f"❌ Error consultando OpenAI: {e}"

# Función para consultar OpenAI sobre malestar o síntoma
def consultar_openai_malestar(pregunta_usuario):
    mensaje_usuario = f"""
Eres un asesor experto en suplementos naturistas.

Un usuario te pregunta: '{pregunta_usuario}'.
Sugiere de forma breve y responsable suplementos naturistas que podrían apoyar esa situación.
Nunca hagas diagnóstico médico. Siempre sugiere consultar a un profesional de la salud si el síntoma persiste.
"""
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=200,
            messages=[
                {"role": "system", "content": "Eres un asesor experto en suplementos naturistas."},
                {"role": "user", "content": mensaje_usuario}
            ]
        )
        return respuesta.choices[0].message['content'].strip()
    except Exception as e:
        return f"❌ Error consultando OpenAI: {e}"

# Función para clasificar necesidad (por categoría)
def clasificar_necesidad(texto_usuario):
    texto_usuario = texto_usuario.lower()
    for palabra, categoria in mapa_categorias.items():
        if palabra in texto_usuario:
            return categoria
    return None

# Función para buscar productos relacionados al texto
def buscar_productos_relacionados(df, texto_usuario):
    palabras_clave = re.findall(r'\b[a-záéíóúñ]+\b', texto_usuario.lower())
    resultados = pd.DataFrame()
    for palabra in palabras_clave:
        coincidencias = df[df['nombre'].str.contains(palabra, case=False, na=False)]
        resultados = pd.concat([resultados, coincidencias])
    resultados = resultados.drop_duplicates()
    return resultados

# Cargar catálogo
df_productos = cargar_catalogo()
if not df_productos.empty:
    df_productos.columns = df_productos.columns.str.strip().str.lower()
    nombre_columna_categoria = df_productos.columns[4]

# Interfaz Streamlit
st.title("🔎 Consulta - Karolo")
st.header("👋 Hola, ¿En qué te puedo ayudar?")

st.markdown("""
Puedes preguntarme:

- Quiero algo para la circulación
- ¿Qué recomiendas para fortalecer defensas?
- ¿Tienes algo para la diabetes?
- ¿Para qué sirve el zinc?
- Tengo dolor de cabeza
- Tengo diarrea
- Tengo cólico
""")

# Selección del tipo de consulta
tipo_consulta = st.radio(
    "Selecciona el tipo de consulta:",
    ("Consulta por producto o beneficio", "Consulta por síntoma o malestar")
)

consulta_necesidad = st.text_input("✍️ Escribe tu necesidad o pregunta:")

if consulta_necesidad:
    st.info("🔎 Analizando tu consulta...")

    if tipo_consulta == "Consulta por producto o beneficio":
        if detectar_consulta_beneficio(consulta_necesidad):
            ingrediente = extraer_ingrediente(consulta_necesidad)
            if ingrediente:
                st.success(f"✅ Consulta detectada sobre ingrediente: **{ingrediente.capitalize()}**")
                with st.spinner("Consultando experto..."):
                    descripcion = consultar_openai_beneficio(ingrediente)
                st.info(f"ℹ️ {descripcion}")
            else:
                st.warning("⚠️ No se pudo identificar claramente el ingrediente.")
        else:
            categoria_detectada = clasificar_necesidad(consulta_necesidad)
            if categoria_detectada and not df_productos.empty:
                st.success(f"✅ Necesidad detectada: **{categoria_detectada.capitalize()}**")
                productos_categoria = df_productos[
                    df_productos[nombre_columna_categoria].astype(str).str.lower() == categoria_detectada.lower()
                ]

                if not productos_categoria.empty:
                    st.subheader("🎯 Productos disponibles:")
                    for idx, row in productos_categoria.iterrows():
                        codigo = str(row['código'])
                        nombre = row['nombre']
                        precio = float(row['precio de venta con iva'])
                        st.write(f"{codigo} | {nombre} | ${precio:,.2f}")
                else:
                    st.warning(f"⚠️ No se encontraron productos para: **{categoria_detectada.capitalize()}**.")
            else:
                st.warning("⚠️ No pudimos interpretar tu solicitud o no hay datos disponibles.")
    else:
        # Consulta por síntoma o malestar
        st.success("✅ Consulta tipo síntoma detectada.")
        with st.spinner("Consultando experto naturista..."):
            respuesta = consultar_openai_malestar(consulta_necesidad)
        st.info(f"ℹ️ {respuesta}")

        buscar_productos = st.checkbox("🔎 ¿Quieres ver si tenemos productos para esto?")
        if buscar_productos and not df_productos.empty:
            resultados = buscar_productos_relacionados(df_productos, consulta_necesidad)
            if not resultados.empty:
                st.subheader("🎯 Productos relacionados encontrados:")
                for idx, row in resultados.iterrows():
                    codigo = str(row['código'])
                    nombre = row['nombre']
                    precio = float(row['precio de venta con iva'])
                    st.write(f"{codigo} | {nombre} | ${precio:,.2f}")
            else:
                st.warning("⚠️ No se encontraron productos relacionados en el catálogo.")
