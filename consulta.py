import streamlit as st
import pandas as pd
import openai
import re
import unicodedata
import os
from datetime import datetime

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

# Función para limpiar acentos
def limpiar_acentos(texto):
    if not isinstance(texto, str):
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

# Función para extraer posibles ingredientes de un texto (dinámico)
def extraer_ingredientes_de_respuesta(texto):
    posibles_ingredientes = [
        "cúrcuma", "glucosamina", "condroitina", "omega", "maca", "ginseng", "rhodiola", "coenzima", "espirulina", "spirulina",
        "pasiflora", "valeriana", "melatonina", "hierba de sapo", "cuachalalate", "probiótico", "probiotico",
        "vitamina", "zinc", "jengibre", "menta", "diente de león", "eufrasia", "colágeno", "magnesio", "carbon activado", "semilla de calabaza", "saw palmetto", "ortiga"
    ]
    encontrados = []
    texto_limpio = limpiar_acentos(texto)
    for ingrediente in posibles_ingredientes:
        if limpiar_acentos(ingrediente) in texto_limpio:
            encontrados.append(ingrediente)
    return list(set(encontrados))

# Función para consultar OpenAI
def consultar_openai_suplementos(consulta):
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=400,
            messages=[
                {"role": "system", "content": """
Eres un asesor experto en suplementos naturistas.

Tu tarea es:
- Recomendar suplementos o ingredientes naturales para aliviar o apoyar de forma complementaria cualquier malestar, síntoma o condición que te describa el usuario.
- Siempre responde mencionando suplementos naturistas o ingredientes activos reales.
- Interpreta y comprende expresiones populares, coloquiales y regionalismos mexicanos (por ejemplo: "chorro", "dolor de panza", "nervios", "estar desganado", etc).
- No des consejos médicos, no digas "consulta a un médico", no emitas diagnósticos.
- No incluyas recomendaciones alimenticias generales ni cambios de estilo de vida.
- Sé concreto, breve, amigable y claro.
- Solo responde recomendando suplementos o combinaciones de suplementos usados comúnmente en herbolaria o naturismo.
"""},
                {"role": "user", "content": consulta}
            ]
        )
        return respuesta.choices[0].message['content'].strip()
    except Exception as e:
        return f"❌ Error consultando OpenAI: {e}"

# Función para guardar historial en CSV
def guardar_en_historial_csv(fecha_hora, pregunta, ingredientes):
    ingredientes_texto = ", ".join(ingredientes) if ingredientes else "Ninguno"
    nuevo_registro = {
        "fecha_hora": fecha_hora,
        "pregunta": pregunta,
        "ingredientes_detectados": ingredientes_texto
    }
    archivo_csv = 'historial_consultas.csv'
    archivo_existe = os.path.exists(archivo_csv)
    df_nuevo = pd.DataFrame([nuevo_registro])

    if archivo_existe:
        df_nuevo.to_csv(archivo_csv, mode='a', header=False, index=False)
    else:
        df_nuevo.to_csv(archivo_csv, mode='w', header=True, index=False)

# Cargar catálogo
df_productos = cargar_catalogo()
if not df_productos.empty:
    df_productos.columns = df_productos.columns.str.strip().str.lower()

# Categorías que no deben mostrarse
categorias_excluidas = ["abarrote", "bebidas", "belleza", "snacks"]

# Interfaz
st.title("🔎 Consulta - Karolo")
st.header("👋 Hola, ¿En qué te puedo ayudar?")

consulta_usuario = st.text_input("✍️ Escribe tu necesidad o pregunta:")

if consulta_usuario:
    st.info("🔎 Procesando tu consulta...")

    with st.spinner("Consultando asesor experto..."):
        respuesta_openai = consultar_openai_suplementos(consulta_usuario)
    st.success(f"ℹ️ {respuesta_openai}")

    # Extraer ingredientes dinámicamente de la respuesta textual
    ingredientes_detectados = extraer_ingredientes_de_respuesta(respuesta_openai)

    # Guardar automáticamente en el CSV
    guardar_en_historial_csv(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        consulta_usuario,
        ingredientes_detectados
    )

    if ingredientes_detectados:
        st.markdown("🔎 Detectamos estos criterios de búsqueda:")
        st.write(", ".join(ingredientes_detectados))

        buscar_productos = st.checkbox("🔍 ¿Deseas ver productos relacionados en catálogo?")

        if buscar_productos:
            productos_relevantes = pd.DataFrame()
            nombre_columna_categoria = df_productos.columns[4]

            for ingrediente in ingredientes_detectados:
                coincidencias_nombre = df_productos[
                    df_productos['nombre'].apply(lambda x: limpiar_acentos(str(x))).str.contains(limpiar_acentos(ingrediente), na=False)
                ]
                coincidencias_categoria = df_productos[
                    df_productos[nombre_columna_categoria].apply(lambda x: limpiar_acentos(str(x))).str.contains(limpiar_acentos(ingrediente), na=False)
                ]
                productos_relevantes = pd.concat([productos_relevantes, coincidencias_nombre, coincidencias_categoria])

            productos_relevantes = productos_relevantes.drop_duplicates()

            # Filtrar para excluir ciertas categorías
            productos_filtrados = productos_relevantes[
                ~productos_relevantes[nombre_columna_categoria].apply(lambda x: limpiar_acentos(str(x))).isin(categorias_excluidas)
            ].sort_values(by='nombre')

            if not productos_filtrados.empty:
                st.subheader("🌟 Productos sugeridos:")
                for idx, row in productos_filtrados.iterrows():
                    try:
                        codigo = str(row.iloc[0])
                        nombre = row['nombre']
                        precio = float(row['precio de venta con iva'])
                        st.write(f"{codigo} | {nombre} | ${precio:,.2f}")
                    except:
                        continue
            else:
                st.warning("⚠️ No se encontraron productos relevantes en catálogo.")
    else:
        st.warning("⚠️ No detectamos ingredientes específicos para buscar productos relacionados.")

# Agregar botón para descargar historial CSV
if os.path.exists('historial_consultas.csv'):
    with open('historial_consultas.csv', 'rb') as f:
        st.download_button('⬇️ Descargar historial de consultas', f, file_name='historial_consultas.csv')
