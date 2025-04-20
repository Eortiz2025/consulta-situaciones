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

# Función para detectar si la consulta es sobre beneficios
def detectar_consulta_beneficio(texto):
    patrones = ["para qué sirve", "beneficio", "beneficios", "ayuda", "utilidad", "para que sirve", "para qué es bueno"]
    texto = texto.lower()
    return any(patron in texto for patron in patrones)

# Función para extraer posibles ingredientes de una respuesta
def extraer_ingredientes_de_respuesta(texto):
    posibles = ["cúrcuma", "glucosamina", "condroitina", "omega", "manzanilla", "jengibre", "menta", "zinc", "vitamina", "probiotico", "spirulina", "ginkgo", "pasiflora", "hierba de sapo", "cuachalalate"]
    encontrados = []
    texto = texto.lower()
    for palabra in posibles:
        if palabra in texto:
            encontrados.append(palabra)
    return encontrados

# Función para preguntar a OpenAI sobre beneficios
def consultar_openai_beneficio(consulta):
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=300,
            messages=[
                {"role": "system", "content": "Eres un asesor experto en suplementos naturistas. Responde brevemente, sin prometer curas."},
                {"role": "user", "content": consulta}
            ]
        )
        return respuesta.choices[0].message['content'].strip()
    except Exception as e:
        return f"❌ Error consultando OpenAI: {e}"

# Cargar catálogo
df_productos = cargar_catalogo()
if not df_productos.empty:
    df_productos.columns = df_productos.columns.str.strip().str.lower()

# Interfaz
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
        with st.spinner("Consultando experto..."):
            respuesta_openai = consultar_openai_beneficio(consulta_usuario)
        st.success(f"ℹ️ {respuesta_openai}")

        # Buscar ingredientes en la respuesta de OpenAI
        ingredientes_detectados = extraer_ingredientes_de_respuesta(respuesta_openai)

        if ingredientes_detectados:
            st.markdown("🔎 Detectamos que estos ingredientes podrían ser relevantes:")
            st.write(", ".join(ingredientes_detectados))

            buscar_productos = st.checkbox("🔍 ¿Deseas ver productos relacionados a estos ingredientes?")

            if buscar_productos:
                productos_relevantes = pd.DataFrame()
                nombre_columna_categoria = df_productos.columns[4]

                for ingrediente in ingredientes_detectados:
                    coincidencias_nombre = df_productos[df_productos['nombre'].str.contains(ingrediente, case=False, na=False)]
                    coincidencias_categoria = df_productos[df_productos[nombre_columna_categoria].astype(str).str.contains(ingrediente, case=False, na=False)]
                    productos_relevantes = pd.concat([productos_relevantes, coincidencias_nombre, coincidencias_categoria])

                productos_relevantes = productos_relevantes.drop_duplicates().sort_values(by='nombre')

                if not productos_relevantes.empty:
                    st.subheader("🎯 Productos recomendados:")
                    for idx, row in productos_relevantes.iterrows():
                        try:
                            codigo = str(row.iloc[0])
                            nombre = row['nombre']
                            precio = float(row['precio de venta con iva'])
                            st.write(f"{codigo} | {nombre} | ${precio:,.2f}")
                        except:
                            continue
                else:
                    st.warning("⚠️ No encontramos productos relacionados en el catálogo.")
        else:
            st.warning("⚠️ No detectamos ingredientes específicos en la respuesta del asesor.")

    else:
        with st.spinner("Consultando experto sobre tu malestar..."):
            respuesta_openai = consultar_openai_beneficio(consulta_usuario)
        st.success(f"ℹ️ {respuesta_openai}")

        # Igual búsqueda basada en la respuesta
        ingredientes_detectados = extraer_ingredientes_de_respuesta(respuesta_openai)

        if ingredientes_detectados:
            st.markdown("🔎 Detectamos que estos ingredientes podrían ser relevantes:")
            st.write(", ".join(ingredientes_detectados))

            buscar_productos = st.checkbox("🔍 ¿Deseas ver productos relacionados a estos ingredientes?")

            if buscar_productos:
                productos_relevantes = pd.DataFrame()
                nombre_columna_categoria = df_productos.columns[4]

                for ingrediente in ingredientes_detectados:
                    coincidencias_nombre = df_productos[df_productos['nombre'].str.contains(ingrediente, case=False, na=False)]
                    coincidencias_categoria = df_productos[df_productos[nombre_columna_categoria].astype(str).str.contains(ingrediente, case=False, na=False)]
                    productos_relevantes = pd.concat([productos_relevantes, coincidencias_nombre, coincidencias_categoria])

                productos_relevantes = productos_relevantes.drop_duplicates().sort_values(by='nombre')

                if not productos_relevantes.empty:
                    st.subheader("🎯 Productos recomendados:")
                    for idx, row in productos_relevantes.iterrows():
                        try:
                            codigo = str(row.iloc[0])
                            nombre = row['nombre']
                            precio = float(row['precio de venta con iva'])
                            st.write(f"{codigo} | {nombre} | ${precio:,.2f}")
                        except:
                            continue
                else:
                    st.warning("⚠️ No encontramos productos relacionados en el catálogo.")
        else:
            st.warning("⚠️ No detectamos ingredientes específicos en la respuesta del asesor.")
