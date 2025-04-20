import streamlit as st
import pandas as pd
import openai

# Configurar tu API Key de OpenAI desde secrets (opcional, futuro uso)
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

# Función para cargar el catálogo naturista
@st.cache_data
def cargar_catalogo():
    df = pd.read_excel('naturista.xlsx')
    return df

# Cargar catálogo
df_productos = cargar_catalogo()

# Título principal
st.title("🔎 Consulta - Karolo")

# =========================================
# 🔍 Buscar Producto por Nombre
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
# 🩺 Buscar Productos por Necesidad de Salud (Detección Automática)
# =========================================
st.header("🩺 Buscar Productos por Necesidad de Salud (Describe Libremente)")

consulta_necesidad = st.text_input("Describe tu necesidad o problema de salud:")

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

    # Detección automática de necesidad
    consulta_detectada = None
    consulta_texto = consulta_necesidad.lower()

    for necesidad, palabras in necesidades.items():
        for palabra in palabras:
            if palabra in consulta_texto:
                consulta_detectada = necesidad
                break
        if consulta_detectada:
            break

    if consulta_detectada:
        palabras_clave = necesidades[consulta_detectada]
        filtro_necesidad = df_productos['Nombre'].str.contains('|'.join(palabras_clave), case=False, na=False)
        resultados_necesidad = df_productos[filtro_necesidad]

        if not resultados_necesidad.empty:
            st.success(f"✅ Basado en tu necesidad relacionada con **{consulta_detectada}**, encontramos estos productos:")
            for index, row in resultados_necesidad.iterrows():
                st.write(f"🔹 **Código: {row['Código']}** - {row['Nombre']} - **Precio:** ${int(row['Precio de venta con IVA'])}")
        else:
            st.warning(f"⚠️ No encontramos productos en el catálogo para '{consulta_detectada}'.")
    else:
        st.warning("⚠️ No detectamos un área de consulta relacionada. Intenta describir tu necesidad de otra forma.")
