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
    patrones = ["para qué sirve", "beneficio", "beneficios", "ayuda", "utilidad"]
    texto = texto.lower()
    return any(patron in texto for patron in patrones)

# Función para extraer posible ingrediente
def extraer_ingrediente(texto):
    palabras = re.findall(r'\b[a-záéíóúñ]+\b', texto.lower())
    exclusiones = {"para", "qué", "sirve", "beneficio", "beneficios", "ayuda", "utilidad", "es", "el", "la", "los", "las", "un", "una", "de", "del", "en", "con", "y"}
    ingredientes = [palabra for palabra in palabras if palabra not in exclusiones]
    return ingredientes[0] if ingredientes else ""

# Función para consultar OpenAI sobre beneficios
def consultar_openai_beneficio(ingrediente):
    mensaje_usuario = f"Para qué sirve el suplemento naturista {ingrediente}."
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

# Función para clasificar necesidad
def clasificar_necesidad(texto_usuario):
    texto_usuario = texto_usuario.lower()
    for palabra, categoria in mapa_categorias.items():
        if palabra in texto_usuario:
            return categoria
    return None

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
""")

consulta_necesidad = st.text_input("Escribe tu necesidad o pregunta:")

if consulta_necesidad:
    st.info("🔎 Analizando tu consulta...")

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
