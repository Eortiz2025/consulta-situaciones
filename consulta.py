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

# Función para detectar si es una consulta de beneficio
def detectar_consulta_beneficio(texto):
    patrones = ["para qué sirve", "beneficio", "beneficios", "ayuda", "utilidad",
                "para que sirve", "para que es bueno", "para qué es bueno", "qué beneficios", "qué hace"]
    texto = texto.lower()
    return any(patron in texto for patron in patrones)

# Función para extraer posible ingrediente de la pregunta
def extraer_ingrediente(texto):
    palabras = re.findall(r'\b[a-záéíóúñ]+\b', texto.lower())
    exclusiones = {"para", "qué", "sirve", "beneficio", "beneficios", "ayuda", "utilidad",
                   "es", "el", "la", "los", "las", "un", "una", "de", "del", "en", "con", "y", "bueno", "hace"}
    ingredientes = [palabra for palabra in palabras if palabra not in exclusiones]
    return ingredientes[0] if ingredientes else ""

# Función para preguntar a OpenAI sobre un beneficio
def consultar_openai_beneficio(ingrediente):
    mensaje_usuario = f"¿Para qué sirve el suplemento naturista {ingrediente}?"
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=200,
            messages=[
                {"role": "system", "content": "Eres un asesor experto en suplementos naturistas. Responde de forma clara, breve y sin prometer curas."},
                {"role": "user", "content": mensaje_usuario}
            ]
        )
        return respuesta.choices[0].message['content'].strip()
    except Exception as e:
        return f"❌ Error consultando OpenAI: {e}"

# Función para preguntar a OpenAI sobre un malestar
def consultar_openai_malestar(pregunta_usuario):
    mensaje_usuario = f"""
Eres un asesor experto en suplementos naturistas.

Un usuario te pregunta: '{pregunta_usuario}'.
Sugiere de forma breve y responsable suplementos naturistas que podrían apoyar esa situación.
Nunca hagas diagnóstico médico. Siempre sugiere consultar a un profesional de la salud si el síntoma persiste.
Menciona los ingredientes principales recomendados en tu respuesta.
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

# Función para extraer posibles ingredientes de una respuesta de OpenAI
def extraer_ingredientes_respuesta(respuesta_openai):
    palabras = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b', respuesta_openai.lower())
    comunes = {"el", "la", "los", "las", "un", "una", "y", "de", "del", "para", "que", "en", "con", "suplemento", "suplementos", "naturista", "naturistas", "puede", "podría", "ayuda", "ayudar", "aliviar", "síntomas", "consultar", "profesional", "salud"}
    ingredientes = [p for p in palabras if p not in comunes and len(p) > 3]
    return list(set(ingredientes))

# Función para buscar productos por ingredientes en Categoría (5ta columna) y Nombre
def buscar_productos_por_ingredientes(df, ingredientes):
    resultados = pd.DataFrame()
    try:
        columna_categoria = df.iloc[:, 4]  # 5ta columna
    except Exception as e:
        st.error(f"❌ Error accediendo a la columna de categoría: {e}")
        return resultados

    for ingrediente in ingredientes:
        coincidencias_categoria = df[columna_categoria.astype(str).str.contains(ingrediente, case=False, na=False)]
        coincidencias_nombre = df[df['nombre'].astype(str).str.contains(ingrediente, case=False, na=False)]
        resultados = pd.concat([resultados, coincidencias_categoria, coincidencias_nombre])
    resultados = resultados.drop_duplicates()

    # Aplicar filtro para excluir productos no deseados
    palabras_excluir = ["jabón", "shampoo", "gel", "crema", "desodorante", "pomada", "spray", "cosmético", "loción", "perfume", "sabon", "barra", "protector", "ungüento"]
    resultados = resultados[~resultados['nombre'].str.lower().str.contains('|'.join(palabras_excluir))]

    # Ordenar alfabéticamente por nombre
    resultados = resultados.sort_values(by='nombre')

    return resultados

# Cargar catálogo
df_productos = cargar_catalogo()
if not df_productos.empty:
    df_productos.columns = df_productos.columns.str.strip().str.lower()

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

tipo_consulta = st.radio(
    "Selecciona el tipo de consulta:",
    ("Consulta por producto o beneficio", "Consulta por síntoma o malestar")
)

consulta_usuario = st.text_input("✍️ Escribe tu necesidad o pregunta:")

if consulta_usuario:
    st.info("🔎 Analizando tu consulta...")

    if tipo_consulta == "Consulta por producto o beneficio":
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
            st.warning("⚠️ No se detectó un ingrediente específico.")
    else:
        st.success("✅ Consulta tipo síntoma detectada.")
        with st.spinner("Consultando experto naturista..."):
            respuesta_openai = consultar_openai_malestar(consulta_usuario)
        st.info(f"ℹ️ {respuesta_openai}")

        buscar_productos = st.checkbox("🔎 ¿Quieres ver si tenemos productos recomendados para esto?")
        if buscar_productos:
            if not df_productos.empty:
                ingredientes_detectados = extraer_ingredientes_respuesta(respuesta_openai)
                if ingredientes_detectados:
                    productos_encontrados = buscar_productos_por_ingredientes(df_productos, ingredientes_detectados)
                    if not productos_encontrados.empty:
                        st.subheader("🎯 Productos recomendados según tu necesidad:")
                        for idx, row in productos_encontrados.iterrows():
                            try:
                                codigo = str(row.iloc[0])
                                nombre = row['nombre']
                                precio = float(row['precio de venta con iva'])
                                st.write(f"{codigo} | {nombre} | ${precio:,.2f}")
                            except:
                                continue
                    else:
                        st.warning("⚠️ No se encontraron productos exactos para los ingredientes sugeridos.")
                else:
                    st.warning("⚠️ No se detectaron ingredientes específicos en la respuesta.")
            else:
                st.error("❌ No se pudo cargar el catálogo de productos.")
