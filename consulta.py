import streamlit as st
import pandas as pd

# Cargar catálogo
@st.cache_data
def cargar_catalogo():
    df = pd.read_excel('naturista.xlsx')
    return df

# Cargar datos
df_productos = cargar_catalogo()

# MOSTRAR las columnas que realmente encontró
st.title("Diagnóstico de Columnas del Archivo 📋")
st.write("Columnas encontradas en naturista.xlsx:", df_productos.columns.tolist())

# Detener la app aquí
st.stop()
