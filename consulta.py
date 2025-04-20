import streamlit as st
import pandas as pd
import openai
import re
from datetime import datetime
import unicodedata

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

# Función para eliminar acentos
def eliminar_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# Función para consultar OpenAI sobre suplementos
def consultar_openai_suplementos(consulta):
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=300,
            messages=[
                {"role": "system", "content": """Eres un asesor experto en suplementos naturistas.
Tu tarea es recomendar suplementos o ingredientes naturales que puedan ayudar a aliviar o apoyar de forma complementaria el malestar, síntoma o condición que te describa el usuario.
Siempre responde mencionando directamente suplementos naturistas o ingredientes activos.
Evita dar consejos médicos, diagnósticos o recomendar consultas a médicos.
Limítate a sugerir suplementos o combinaciones de suplementos que sean comunes en el ámbito naturista.
Sé concreto, breve y claro en tus recomendaciones."""},
                {"role": "user", "content": consulta}
            ]
        )
        return respuesta.choices[0].message['content'].strip()
    except Exception as e:
        return f"❌ Error consultando OpenAI: {e}"

# Función para detectar posibles ingredientes de la respuesta
def detectar_ingredientes(respuesta):
    ingredientes_clave = [
        "cúrcuma", "glucosamina", "condroitina", "omega", "manzanilla", "jengibre",
        "menta", "zinc", "vitamina", "probiotico", "espirulina", "spirulina",
        "ginkgo", "pasiflora", "hierba de sapo", "cuachalalate", "colágeno",
        "magnesio", "resveratrol", "melatonina", "té verde", "maca", "ginseng",
        "triptófano", "carbon activado", "lactobacillus", "luteína"
    ]
    respuesta_sin_acentos = eliminar_acentos(respuesta.lower())
    encontrados = []
    for ingrediente in ingredientes_clave:
        if eliminar_acentos(ingrediente) in respuesta_sin_acentos:
            encontrados.append(ingrediente)
    return list(set(encontrados))

# Función para registrar historial
def guardar_en_historial(fecha, consulta, ingredientes):
    nuevo_registro = pd.DataFrame({
        'Fecha y hora': [fecha],
        'Consulta': [consulta],
        'Ingredientes detectados': [", ".join(ingredientes)]
    })
    try:
        historial_existente = pd.read_csv('historial_consultas.csv')
        historial_actualizado = pd.concat([historial_existente, nuevo_registro], ignore_index=True)
    except FileNotFoundError:
        historial_actualizado = nuevo_registro

    historial_actualizado.to_csv('historial_consultas.csv', index=False)

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

    ingredientes_detectados = detectar_ingredientes(respuesta_openai)

    # Guardar automáticamente en historial
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    guardar_en_historial(fecha_actual, consulta_usuario, ingredientes_detectados)

    if ingredientes_detectados:
        st.markdown("🔎 Detectamos estos criterios de búsqueda:")
        st.write(", ".join(ingredientes_detectados))

        buscar_productos = st.checkbox("🔍 ¿Deseas ver productos relacionados en catálogo?")

        if buscar_productos:
            productos_relevantes = pd.DataFrame()
            nombre_columna_categoria = df_productos.columns[4]

            for ingrediente in ingredientes_detectados:
                coincidencias_nombre = df_productos[df_productos['nombre'].str.contains(ingrediente, case=False, na=False)]
                coincidencias_categoria = df_productos[df_productos[nombre_columna_categoria].astype(str).str.contains(ingrediente, case=False, na=False)]
                productos_relevantes = pd.concat([productos_relevantes, coincidencias_nombre, coincidencias_categoria])

            productos_relevantes = productos_relevantes.drop_duplicates()

            # Filtrar para excluir ciertas categorías
            productos_filtrados = productos_relevantes[
                ~df_productos[nombre_columna_categoria].astype(str).str.lower().isin(categorias_excluidas)
            ].sort_values(by='nombre')

            if not productos_filtrados.empty:
                st.subheader("🎯 Productos sugeridos:")
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
