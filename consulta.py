import streamlit as st
import pandas as pd
import openai
import re

# Configurar API Key de OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Función para cargar el catálogo naturista
@st.cache_data
def cargar_catalogo():
    return pd.read_excel('naturista.xlsx')

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

# Función para detectar si es una pregunta sobre beneficios de un ingrediente
def detectar_consulta_beneficio(texto):
    patrones = ["para qué sirve", "beneficio", "beneficios", "ayuda", "utilidad"]
    texto = texto.lower()
    for patron in patrones:
        if patron in texto:
            return True
    return False

# Función para extraer posible ingrediente del texto
def extraer_ingrediente(texto):
    palabras = re.findall(r'\b[a-záéíóúñ]+\b', texto.lower())
    # Buscamos la primera palabra que no sea parte de la pregunta
    exclusiones = ["para", "qué", "sirve", "beneficio", "beneficios", "ayuda", "utilidad", "es", "el", "la", "los", "las", "un", "una", "de", "del", "en", "con"]
    ingredientes = [palabra for palabra in palabras if palabra not in exclusiones]
    return " ".join(ingredientes)

# Función para consultar OpenAI sobre beneficios de un ingrediente
def consultar_openai_beneficio(ingrediente):
    prompt = f"""
Eres un asesor experto en suplementos naturistas.

Explica en máximo dos líneas para qué sirve el suplemento o ingrediente naturista "{ingrediente}".
No hagas diagnósticos médicos ni afirmaciones milagrosas. Sé realista, claro y breve.
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
        return f"❌ Error consultando OpenAI: {e}"

# Función para clasificar necesidad (por categoría)
def clasificar_necesidad(texto_usuario):
    texto_usuario = texto_usuario.lower()
    for palabra, categoria in mapa_categorias.items():
        if palabra in texto_usuario:
            return categoria
    return None

# Cargar catálogo
df_productos = cargar_catalogo()
df_productos.columns = df_productos.columns.str.strip().str.lower()
nombre_columna_categoria = df_productos.columns[4]

# Interfaz en Streamlit
st.title("🔎 Consulta - Karolo")
st.header("👋 Hola, ¿En qué te puedo ayudar?")

st.markdown(
    """
    Puedes preguntarme:

    - Quiero algo para la circulación
    - ¿Qué recomiendas para fortalecer defensas?
    - ¿Tienes algo para la diabetes?
    - ¿Para qué sirve el zinc?
    - ¿Qué beneficios tiene la cúrcuma?
    """
)

# Entrada de necesidad o pregunta
consulta_necesidad = st.text_input("Escribe tu necesidad o pregunta:")

if consulta_necesidad:
    st.info("🔎 Analizando tu consulta...")

    if detectar_consulta_beneficio(consulta_necesidad):
        # Pregunta sobre beneficio de ingrediente
        ingrediente = extraer_ingrediente(consulta_necesidad)
        if ingrediente:
            st.success(f"✅ Consulta detectada sobre ingrediente: **{ingrediente.capitalize()}**")
            descripcion = consultar_openai_beneficio(ingrediente)
            st.info(f"ℹ️ {descripcion}")
        else:
            st.warning("⚠️ No se pudo identificar claramente el ingrediente.")

    else:
        # Pregunta de necesidad clásica (categoría)
        categoria_detectada = clasificar_necesidad(consulta_necesidad)
        if categoria_detectada:
            st.success(f"✅ Necesidad detectada: **{categoria_detectada.capitalize()}**")

            productos_categoria = df_productos[
                df_productos[nombre_columna_categoria].astype(str).str.lower() == categoria_detectada.lower()
            ]

            if not productos_categoria.empty:
                st.subheader("🎯 Productos disponibles:")

                for idx, row in productos_categoria.iterrows():
                    codigo = str(row['código'])
                    nombre = row['nombre']
                    precio = int(row['precio de venta con iva'])
                    st.write(f"{codigo} | {nombre} | ${precio}")

            else:
                st.warning(f"⚠️ No se encontraron productos para: **{categoria_detectada.capitalize()}**.")
        else:
            st.warning("⚠️ No pudimos interpretar tu solicitud. Consulta con un asesor naturista.")
