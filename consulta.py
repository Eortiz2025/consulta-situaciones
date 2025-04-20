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

# Lista extensa de ingredientes naturistas
posibles_ingredientes = [
    "cúrcuma", "glucosamina", "condroitina", "omega", "omega 3", "omega 6", "omega 9", "maca", "ginseng",
    "rhodiola", "coenzima", "espirulina", "spirulina", "pasiflora", "valeriana", "melatonina", "hierba de sapo",
    "cuachalalate", "probiótico", "probiotico", "vitamina", "vitamina c", "vitamina d", "vitamina e", "vitamina a",
    "vitamina b12", "zinc", "magnesio", "calcio", "hierro", "selenio", "diente de león", "eufrasia", "colágeno",
    "ácido hialurónico", "té verde", "té de manzanilla", "té de menta", "té de tila", "manzanilla", "menta",
    "cardo mariano", "saw palmetto", "semilla de calabaza", "ortiga", "árnica", "jengibre", "cáscara sagrada",
    "fenogreco", "aloe vera", "chlorella", "ashwagandha", "melena de león", "resveratrol", "bacopa monnieri",
    "garcinia cambogia", "té rojo", "té blanco", "té negro", "matcha", "triptófano", "5-htp", "l-teanina",
    "curcumina", "ácido alfa lipoico", "extracto de semilla de uva", "pqq", "semilla de lino", "cebada verde",
    "alfalfa", "raíz de regaliz", "shatavari", "tribulus", "moringa", "echinacea", "guaraná", "camu camu",
    "lúcuma", "spirulina azul", "pepita de calabaza", "romero", "ajo negro", "ajo", "clorofila", "guggul",
    "astaxantina", "pterostilbeno", "berberina", "boswellia", "bacopa", "ginkgo biloba", "espino blanco",
    "extracto de hoja de olivo", "extracto de arándano", "extracto de granada", "extracto de romero",
    "extracto de jengibre", "extracto de canela", "extracto de pimienta negra"
]

# Función para extraer posibles ingredientes dinámicamente
def extraer_ingredientes_de_respuesta(texto):
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
            max_tokens=300,
            messages=[
                {"role": "system", "content": """
Eres un asesor experto en suplementos naturistas.
Tu tarea es recomendar suplementos o ingredientes naturales que puedan ayudar a aliviar o apoyar de forma complementaria el malestar, síntoma o condición que te describa el usuario.
Siempre responde mencionando directamente suplementos naturistas o ingredientes activos.
Entiende regionalismos mexicanos (ej. 'chorro' = diarrea).
Evita dar consejos médicos, diagnósticos o recomendar consultas a médicos.
No uses frases genéricas como 'consulta a un profesional'.
Sé concreto, breve y claro en tus recomendaciones."""},
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

# Categorías a excluir
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

    ingredientes_detectados = extraer_ingredientes_de_respuesta(respuesta_openai)

    # Guardar en CSV
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

# Botón de descarga de historial
if os.path.exists('historial_consultas.csv'):
    with open('historial_consultas.csv', 'rb') as f:
        st.download_button('⬇️ Descargar historial de consultas', f, file_name='historial_consultas.csv')
