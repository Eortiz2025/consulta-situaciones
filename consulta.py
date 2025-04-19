import streamlit as st
import pandas as pd
from datetime import datetime

# Inicializar "base de datos" en memoria
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Fecha", "Empleado", "Tipo de Situación", "Descripción"])

# Título principal
st.title("Consulta y Registro de Situaciones Diarias 📋")

# Sección lateral para nuevo registro
st.sidebar.header("Nuevo Registro")

# Captura de datos
empleado = st.sidebar.text_input("Nombre del Empleado")
tipo_situacion = st.sidebar.selectbox("Tipo de Situación", ["Problema", "Idea de Mejora", "Comentario General"])
descripcion = st.sidebar.text_area("Descripción Breve")

if st.sidebar.button("Registrar"):
    if empleado and descripcion:
        nuevo_registro = {
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Empleado": empleado,
            "Tipo de Situación": tipo_situacion,
            "Descripción": descripcion
        }
        st.session_state.data = pd.concat(
            [st.session_state.data, pd.DataFrame([nuevo_registro])],
            ignore_index=True
        )
        st.sidebar.success("✅ Registro guardado exitosamente.")
    else:
        st.sidebar.error("❌ Por favor, completa todos los campos.")

# Sección principal: mostrar registros
st.header("Situaciones Registradas 📚")

# Mostrar tabla
st.dataframe(st.session_state.data, use_container_width=True)

# Botón para descarga de datos
st.download_button(
    label="📥 Descargar registros en CSV",
    data=st.session_state.data.to_csv(index=False).encode('utf-8'),
    file_name='situaciones_diarias.csv',
    mime='text/csv'
)
