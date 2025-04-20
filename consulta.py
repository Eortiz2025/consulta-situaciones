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

# Función para detectar consulta sobre beneficio
def detectar_consulta_beneficio(texto):
    patrones = ["para qué sirve", "beneficio", "beneficios", "ayuda", "utilidad", "para que sirve", "para qué es bueno"]
    texto = texto.lower()
    return any(patron in texto for patron in patrones)

# Función para extraer ingrediente
def extraer_ingrediente(texto):
    palabras = re.findall(r'\b[a-záéíóúñ]+\b', texto.lower())
    exclusiones = {"para", "qué", "sirve", "beneficio", "beneficios", "ayuda", "utilidad", "es", "el", "la", "los", "las", "un", "una", "de", "del", "en", "con", "y", "bueno", "hace"}
    ingredientes = [palabra for palabra in palabras if palabra not in exclusiones]
    return ingredientes[0] if ingredientes else ""

# Función para preguntar a OpenAI sobre beneficios
def consultar_openai_beneficio(ingrediente):
    mensaje_usuario = f"¿Para qué sirve el suplemento naturista {ingrediente}?"
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=200,
            messages=[
                {"role": "system", "content": "Eres un asesor experto en suplementos naturistas. Responde de forma breve, clara y sin prometer curas."},
                {"role": "user", "content": mensaje_usuario}
            ]
        )
        return respuesta.choices[0].message['content'].strip()
    except Exception as e:
        return f"❌ Error consultando OpenAI: {e}"

# Función para consultar OpenAI sobre síntomas
def consultar_openai_malestar(pregunta_usuario):
    mensaje_usuario = f"""
Eres un asesor experto en suplementos naturistas.

Un usuario te pregunta: '{pregunta_usuario}'.
Sugiere de forma breve suplementos naturistas que podrían apoyar esa situación.
Nunca prometas curas. Siempre recomienda consultar a un profesional de la salud si los síntomas persisten.
"""
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=300,
            messages=[
                {"role": "system", "content": "Eres un asesor experto en suplementos naturistas."},
                {"role": "user", "content": mensaje_usuario}
            ]
        )
        return respuesta.choices[0].message['content'].strip()
    except Exception as e:
        return f"❌ Error consultando OpenAI: {e}"

# Cargar catálogo
df_productos = cargar_catalogo()
if not df_productos.empty:
    df_productos.columns = df_productos.columns.str.strip().str.lower()

# Interfaz Streamlit
st.title("🔎 Consulta - Karolo")
st.header("👋 Hola, ¿En qué te puedo ayudar?")

st.markdown("""
Ejemplos de preguntas que puedes hacer:

- ¿Qué recomiendas para fortalecer defensas?
- ¿Tienes algo para la diabetes?
- ¿Para qué sirve el zinc?
- Tengo dolor de cabeza
""")

consulta_usuario = st.text_input("✍️ Escribe tu necesidad o pregunta:")

if consulta_usuario:
    st.info(f"🔎 Procesando tu consulta: {consulta_usuario}")

    if detectar_consulta_beneficio(consulta_usuario):
        ingrediente = extraer_ingrediente(consulta_usuario)
        if ingrediente:
            st.success(f"✅ Consulta detectada sobre ingrediente: **{ingrediente.capitalize()}**")
            with st.spinner("Consultando experto..."):
                descripcion = consultar_openai_beneficio(ingrediente)
            st.info(f"ℹ️ {descripcion}")
        else:
            st.warning("⚠️ No se pudo identificar claramente el ingrediente.")
    else:
        with st.spinner("Consultando experto sobre tu malestar..."):
            respuesta_openai = consultar_openai_malestar(consulta_usuario)
        st.success(f"ℹ️ {respuesta_openai}")

        buscar_productos = st.checkbox("🔎 ¿Quieres ver si tenemos productos relacionados?")
        if buscar_productos and not df_productos.empty:
            categoria_busqueda = ""
            if "diabetes" in consulta_usuario.lower():
                categoria_busqueda = "diabetes"
            elif "defensas" in consulta_usuario.lower():
                categoria_busqueda = "vitaminas"
            elif "cabeza" in consulta_usuario.lower():
                categoria_busqueda = "tranquilidad"

            if categoria_busqueda:
                try:
                    productos = df_productos[df_productos.iloc[:, 4].astype(str).str.contains(categoria_busqueda, case=False, na=False)]
                    productos = productos.sort_values(by='nombre')
                    if not productos.empty:
                        st.subheader("🎯 Productos recomendados:")
                        for idx, row in productos.iterrows():
                            try:
                                codigo = str(row.iloc[0])
                                nombre = row['nombre']
                                precio = float(row['precio de venta con iva'])
                                st.write(f"{codigo} | {nombre} | ${precio:,.2f}")
                            except:
                                continue
                    else:
                        st.warning("⚠️ No se encontraron productos relacionados en el catálogo.")
                except Exception as e:
                    st.error(f"❌ Error al buscar productos: {e}")
