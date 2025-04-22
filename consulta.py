import streamlit as st
import pandas as pd
import openai
import re
import unicodedata
import os
from datetime import datetime
import pytz

# Configurar API Key de OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ===============================
# Funciones para ingredientes
# ===============================

def limpiar_acentos(texto):
    if not isinstance(texto, str):
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def cargar_ingredientes():
    archivo = "ingredientes.txt"
    if not os.path.exists(archivo):
        return []
    with open(archivo, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

def agregar_ingredientes_nuevos(nuevos):
    existentes = set(cargar_ingredientes())
    nuevos_filtrados = [i for i in nuevos if i not in existentes]
    if nuevos_filtrados:
        with open("ingredientes.txt", "a", encoding="utf-8") as f:
            for ingr in nuevos_filtrados:
                f.write(f"{ingr}\n")

def extraer_ingredientes_de_respuesta(texto):
    posibles_ingredientes = cargar_ingredientes()
    texto_limpio = limpiar_acentos(texto)
    encontrados = []

    for ingrediente in posibles_ingredientes:
        patron = r"\b" + re.escape(limpiar_acentos(ingrediente)) + r"\b"
        if re.search(patron, texto_limpio):
            encontrados.append(ingrediente)

    # Detectar frases nuevas de 2 o más palabras
    palabras = set(re.findall(r'\b(?:\w+\s+){1,3}\w+\b', texto_limpio))  # busca frases de 2-4 palabras
    nuevos = [p.strip() for p in palabras if p not in posibles_ingredientes and len(p.strip().split()) > 1]
    agregar_ingredientes_nuevos(nuevos)

    return list(set(encontrados + nuevos))

# ===============================
# Funciones de consulta y sistema
# ===============================

def cargar_catalogo():
    try:
        return pd.read_excel('naturista.xlsx')
    except Exception as e:
        st.error(f"Error al cargar el catálogo: {e}")
        return pd.DataFrame()

def consultar_openai_suplementos(consulta):
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=400,
            messages=[
                {"role": "system", "content": """Eres un asesor experto en suplementos naturistas.
Debes interpretar y comprender también los regionalismos y expresiones informales típicas de México para entender mejor al usuario.
Tu tarea es recomendar suplementos o ingredientes naturales que puedan ayudar a aliviar o apoyar de forma complementaria el malestar, síntoma o condición que te describa el usuario.
Siempre responde mencionando directamente suplementos naturistas o ingredientes activos conocidos.
Evita dar consejos médicos, diagnósticos o recomendar consultas a médicos.
No uses frases genéricas como 'consulta a un profesional'.
Sé concreto, breve y claro en tus recomendaciones."""},
                {"role": "user", "content": consulta}
            ]
        )
        return respuesta.choices[0].message['content'].strip()
    except Exception as e:
        return f"❌ Error consultando OpenAI: {e}"

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

# ===============================
# Interfaz principal
# ===============================

df_productos = cargar_catalogo()
if not df_productos.empty:
    df_productos.columns = df_productos.columns.str.strip().str.lower()

categorias_excluidas = ["abarrote", "bebidas", "belleza", "snacks"]

st.title("🔎 Karolo Naturista")
st.header("👋 Hola, ¿En qué te puedo ayudar?")

consulta_usuario = st.text_input("✍️ Escribe tu pregunta:")

if consulta_usuario:
    st.info("🔎 Procesando tu consulta...")

    with st.spinner("Consultando asesor experto..."):
        respuesta_openai = consultar_openai_suplementos(consulta_usuario)
    st.success(f"ℹ️ {respuesta_openai}")

    ingredientes_detectados = extraer_ingredientes_de_respuesta(respuesta_openai)

    pacific = pytz.timezone('America/Los_Angeles')
    hora_pacifico = datetime.now(pacific).strftime("%Y-%m-%d %H:%M:%S")
    guardar_en_historial_csv(hora_pacifico, consulta_usuario, ingredientes_detectados)

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

# ===============================
# Zona de administración
# ===============================

with st.expander("🔒 Acceso de administrador (protegido)"):
    codigo_admin = st.text_input("Ingrese código secreto:", type="password")

    if codigo_admin == "1001":
        st.success("🔐 Acceso concedido.")
        if os.path.exists('historial_consultas.csv'):
            with open('historial_consultas.csv', 'rb') as f:
                st.download_button(
                    label="📥 Descargar historial de consultas",
                    data=f,
                    file_name="historial_consultas.csv",
                    mime='text/csv'
                )
    elif codigo_admin:
        st.error("❌ Código incorrecto.")
