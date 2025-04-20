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

# Función para clasificar automáticamente la necesidad del usuario
def clasificar_necesidad(texto_usuario):
    texto_usuario = texto_usuario.lower()
    for palabra, categoria in mapa_categorias.items():
        if palabra in texto_usuario:
            return categoria
    return None

# Función para obtener una breve descripción de un producto utilizando OpenAI
def obtener_descripcion_producto(nombre_producto, categoria_producto):
    prompt = f"""
Eres un asesor experto en suplementos naturistas.

Describe brevemente (máximo 2 líneas) el posible beneficio de un suplemento llamado "{nombre_producto}", perteneciente a la categoría de "{categoria_producto}".
No inventes enfermedades ni tratamientos médicos específicos. No repitas el nombre completo.
Sé claro, breve y realista basado en el contexto de suplementos naturistas.
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
        return f"❌ Error generando descripción: {e}"

# Cargar el catálogo
df_productos = cargar_catalogo()

# Normalización de nombres de columnas
df_productos.columns = df_productos.columns.str.strip().str.lower()

# Identificación de la quinta columna como categoría
nombre_columna_categoria = df_productos.columns[4]

# Configuración de la aplicación en Streamlit
st.title("🔎 Consulta - Karolo")

st.header("👋 Bienvenido. ¿En qué puedo asistirle hoy?")

st.markdown(
    """
    Puede realizar consultas como:

    - Quiero algo para la circulación
    - ¿Qué recomiendas para fortalecer defensas?
    - ¿Tienes algo para la diabetes?
    - Me siento cansado, ¿qué puedo tomar?
    - Necesito gotas para los ojos

    Estoy a su disposición para asistirlo. 🌟
    """
)

# Entrada de consulta del usuario
consulta_necesidad = st.text_input("Escriba su necesidad:")

if consulta_necesidad:
    st.info("🔎 Analizando su consulta...")

    categoria_detectada = clasificar_necesidad(consulta_necesidad)

    if categoria_detectada:
        st.success(f"✅ Necesidad detectada: **{categoria_detectada.capitalize()}**")

        # Filtrar productos por categoría detectada
        productos_categoria = df_productos[
            df_productos[nombre_columna_categoria].astype(str).str.lower() == categoria_detectada.lower()
        ]

        if not productos_categoria.empty:
            st.subheader("🎯 Productos sugeridos:")

            opciones = [
                f"{str(row['código'])} - {row['nombre']}"
                for idx, row in productos_categoria.iterrows()
            ]
            
            seleccionado = st.radio(
                "Seleccione un producto para consultar detalles:",
                opciones,
                index=None
            )

            if seleccionado:
                codigo_seleccionado = seleccionado.split(" - ")[0]

                # Asegurar que la comparación sea entre strings
                producto_seleccionado = productos_categoria[
                    productos_categoria['código'].astype(str) == codigo_seleccionado
                ].iloc[0]

                # Obtener nombre y categoría del producto seleccionado
                nombre_producto = producto_seleccionado['nombre']
                categoria_producto = producto_seleccionado[nombre_columna_categoria]

                descripcion = obtener_descripcion_producto(nombre_producto, categoria_producto)

                st.info(f"🔹 **{nombre_producto}**\n\nℹ️ {descripcion}")

        else:
            st.warning(f"⚠️ No se encontraron productos relacionados con: **{categoria_detectada.capitalize()}**.")

    else:
        st.warning("⚠️ No fue posible detectar su necesidad. Intente ser más específico o utilice términos comunes.")
