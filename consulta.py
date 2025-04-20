import streamlit as st
import pandas as pd
import openai

# Configurar tu API Key de OpenAI desde secrets (opcional para futura expansión)
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

# Función para cargar el catálogo naturista
@st.cache_data
def cargar_catalogo():
    df = pd.read_excel('naturista.xlsx')
    return df

# Cargar catálogo
df_productos = cargar_catalogo()

# Título de la App
st.title("🔎 Consulta - Karolo")

# =========================================
# Búsqueda tradicional por Nombre de producto
# =========================================
st.header("🔍 Buscar Producto por Nombre")

busqueda_nombre = st.text_input("Escribe el nombre o parte del nombre del producto:")

if busqueda_nombre:
    resultados = df_productos[df_productos['Nombre'].str.contains(busqueda_nombre, case=False, na=False)]

    if not resultados.empty:
        st.success(f"✅ Se encontraron {len(resultados)} productos relacionados:")
        for index, row in resultados.iterrows():
            st.write(f"🔹 **Código: {row['Código']}** - {row['Nombre']} - **Precio:** ${int(row['Precio de venta con IVA'])}")
    else:
        st.warning("⚠️ No se encontró ningún producto que coincida con tu búsqueda.")

# =========================================
# Búsqueda por Necesidad de Salud Inteligente
# =========================================
st.header("🩺 Buscar Productos por Necesidad de Salud")

consulta_necesidad = st.text_input("¿Qué necesidad tienes? (Ejemplo: circulación, próstata, diabetes, hígado, defensas, etc.)")

if consulta_necesidad:
    necesidades = {
        'circulación': ['circulación', 'vascular', 'cardio', 'corazón', 'arterias', 'venas', 'sangre'],
        'próstata': ['próstata', 'prostata', 'prost', 'saw palmetto', 'serenoa', 'pygeum'],
        'diabetes': ['diabetes', 'glucosa', 'gluco', 'sugar', 'azúcar'],
        'hígado': ['hígado', 'higado', 'cardo mariano', 'silimarina', 'biliar', 'desintoxicación'],
        'inmunidad': ['defensas', 'inmunidad', 'inmune', 'vitamina c', 'equinácea', 'propóleo'],
        'cansancio': ['energía', 'energy', 'cansancio', 'fatiga', 'vitalidad', 'ginseng', 'guaraná'],
        'digestión': ['digestión', 'digestivo', 'probiótico', 'fibra', 'laxante', 'prebiótico'],
        'colesterol': ['colesterol', 'triglicéridos', 'cardio'],
        'control de peso': ['peso', 'obesidad', 'control de peso', 'metabolismo', 'quemador', 'slim', 'delgax'],
        'osteoporosis': ['calcio', 'huesos', 'osteoporosis', 'articulaciones', 'condroitina', 'glucosamina'],
        'piel y cabello': ['colágeno', 'biotina', 'ácido hialurónico', 'shampoo', 'piel', 'cabello'],
        'relajación y sueño': ['melatonina', 'relax', 'sueño', 'insomnio', 'calmante', 'ansiedad'],
        'vista': ['vista', 'ojos', 'visión', 'luteína'],
        'riñones': ['riñón', 'riñones', 'renal', 'urinario'],
        'menopausia': ['menopausia', 'soya', 'climaterio', 'isoflavonas'],
    }

    # Detectar la necesidad buscada (permitimos entrada libre)
    palabras_clave = []
    for necesidad, palabras in necesidades.items():
        if consulta_necesidad.lower() in necesidad:
            palabras_clave = palabras
            break

    if not palabras_clave:
        palabras_clave = [consulta_necesidad.lower()]  # Buscar como palabra suelta

    # Buscar en catálogo
    filtro_necesidad = df_productos['Nombre'].str.contains('|'.join(palabras_clave), case=False, na=False)
    resultados_necesidad = df_productos[filtro_necesidad]

    if not resultados_necesidad.empty:
        st.success(f"✅ Encontramos {len(resultados_necesidad)} productos que pueden ayudarte con {consulta_necesidad}:")
        for index, row in resultados_necesidad.iterrows():
            st.write(f"🔹 **Código: {row['Código']}** - {row['Nombre']} - **Precio:** ${int(row['Precio de venta con IVA'])}")
    else:
        st.warning("⚠️ No se encontraron productos específicos para esa necesidad en nuestro catálogo.")
