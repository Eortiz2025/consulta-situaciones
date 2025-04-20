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
    "visión": "Visión",
    "vista": "Visión",
    "ojos": "Visión",
    "ocular": "Visión",
    "circulación": "Circulacion",
    "sangre": "Circulacion",
    "varices": "Circulacion",
    "energía": "Energia",
    "cansancio": "Energia",
    "fatiga": "Energia",
    "defensas": "Vitaminas",
    "inmunidad": "Vitaminas",
    "gripas": "Vitaminas",
    "digestión": "Digestion",
    "estómago": "Digestion",
    "colon": "Digestion",
    "hígado": "Higado",
    "desintoxicar": "Higado",
    "articulaciones": "Articulaciones",
    "rodillas": "Articulaciones",
    "huesos": "Articulaciones",
    "diabetes": "Diabetes",
    "azúcar": "Diabetes",
    "ansiedad": "Tranquilidad",
    "dormir": "Tranquilidad",
    "nervios": "Tranquilidad",
    "pulmones": "Respiratorio",
    "tos": "Respiratorio",
    "bronquios": "Respiratorio",
    "memoria": "Funcion cerebral",
    "concentración": "Funcion cerebral",
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
        st.success(f"✅ Detectamos que buscas productos relacionados con: **{categoria_detectada}**")

        # Buscar productos de esa categoría (tomando la cuarta columna que sabemos es Categoria)
        if "Categoria" in df_productos.columns:
            productos_categoria = df_productos[df_productos['Categoria'].str.lower() == categoria_detectada.lower()]
        else:
            st.error("❌ Error: No se encontró la columna 'Categoria' en el catálogo.")
            productos_categoria = pd.DataFrame()

        if not productos_categoria.empty:
            st.subheader("🎯 Productos sugeridos:")

            for index, row in productos_categoria.iterrows():
                col1, col2 = st.columns([0.1, 0.9])
                with col1:
                    ver_detalles = st.checkbox("", key=f"detalle_{row['Código']}")
                with col2:
                    st.write(f"🔹 **Código: {row['Código']}** - {row['Nombre']} - **Precio:** ${int(row['Precio de venta con IVA'])}")
                if ver_detalles:
                    descripcion = obtener_descripcion_producto(row['Nombre'])
                    st.info(f"ℹ️ {descripcion}")
        else:
            st.warning(f"⚠️ No encontramos productos para la categoría detectada: **{categoria_detectada}**.")

    else:
        st.warning("⚠️ No pudimos detectar tu necesidad en nuestro catálogo. Intenta ser más específico o usar palabras comunes.")
