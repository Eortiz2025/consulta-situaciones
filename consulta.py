import streamlit as st
import pandas as pd
import openai

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

# Función para clasificar automáticamente la necesidad
def clasificar_necesidad(texto_usuario):
    texto_usuario = texto_usuario.lower()
    for palabra, categoria in mapa_categorias.items():
        if palabra in texto_usuario:
            return categoria
    return None

# Cargar catálogo
df_productos = cargar_catalogo()

# Normalizar nombres de columnas
df_productos.columns = df_productos.columns.str.strip().str.lower()

# Detectar nombre de la columna categoría
nombre_columna_categoria = df_productos.columns[4]

# Configuración de la aplicación
st.title("🔎 Consulta - Karolo")

st.header("👋 Bienvenido. ¿En qué puedo asistirle hoy?")

st.markdown(
    """
    Puede realizar consultas como:

    - Quiero algo para la circulación
    - ¿Qué recomiendas para fortalecer defensas?
    - ¿Tienes algo para la diabetes?
    """
)

# Entrada de necesidad del usuario
consulta_necesidad = st.text_input("Escriba su necesidad:")

if consulta_necesidad:
    st.info("🔎 Analizando su consulta...")

    categoria_detectada = clasificar_necesidad(consulta_necesidad)

    if categoria_detectada:
        st.success(f"✅ Necesidad detectada: **{categoria_detectada.capitalize()}**")

        # Filtrar productos de esa categoría
        productos_categoria = df_productos[
            df_productos[nombre_columna_categoria].astype(str).str.lower() == categoria_detectada.lower()
        ]

        if not productos_categoria.empty:
            st.subheader("🎯 Productos disponibles:")

            # Mostrar listado limpio de productos
            for idx, row in productos_categoria.iterrows():
                codigo = str(row['código'])
                nombre = row['nombre']
                precio = int(row['precio de venta con iva'])

                st.write(f"🔹 **Código:** {codigo} | **Nombre:** {nombre} | **Precio:** ${precio}")

        else:
            st.warning(f"⚠️ No se encontraron productos relacionados con: **{categoria_detectada.capitalize()}**.")

    else:
        st.warning("⚠️ No fue posible detectar su necesidad. Intente ser más específico o utilice términos comunes.")
