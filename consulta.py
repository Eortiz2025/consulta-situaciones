import streamlit as st
import pandas as pd
import openai

# Configurar tu API Key de OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Función para cargar el catálogo naturista
@st.cache_data
def cargar_catalogo():
    return pd.read_excel('naturista.xlsx')

# Tabla interna: palabras clave asociadas a categorías
mapa_categorias = {
    "visión": "vision",
    "vista": "vision",
    "ojos": "vision",
    "ocular": "vision",
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
    return None  # No encontró ninguna categoría

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

# Limpiar nombres de columnas
df_productos.columns = df_productos.columns.str.strip().str.lower()

# Detectar automáticamente la columna de categoría (4ta columna)
nombre_columna_categoria = df_productos.columns[3]  # 0,1,2,3 --> cuarta columna

# Título principal
st.title("🔎 Consulta - Karolo")

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
    st.info("🔎 Analizando tu necesidad...")

    categoria_detectada = clasificar_necesidad(consulta_necesidad)

    if categoria_detectada:
        st.success(f"✅ Detectamos que buscas productos relacionados con: **{categoria_detectada.capitalize()}**")

        # Buscar productos de esa categoría usando la cuarta columna
        productos_categoria = df_productos[df_productos[nombre_columna_categoria].str.lower() == categoria_detectada.lower()]

        if not productos_categoria.empty:
            st.subheader("🎯 Productos sugeridos:")

            for index, row in productos_categoria.iterrows():
                col1, col2 = st.columns([0.1, 0.9])
                with col1:
                    ver_detalles = st.checkbox("", key=f"detalle_{row['código']}")
                with col2:
                    st.write(f"🔹 **Código: {row['código']}** - {row['nombre']} - **Precio:** ${int(row['precio de venta con iva'])}")
                if ver_detalles:
                    descripcion = obtener_descripcion_producto(row['nombre'])
                    st.info(f"ℹ️ {descripcion}")
        else:
            st.warning(f"⚠️ No encontramos productos para la categoría detectada: **{categoria_detectada.capitalize()}**.")

    else:
        st.warning("⚠️ No pudimos detectar tu necesidad en nuestro catálogo. Intenta ser más específico o usar palabras comunes.")
