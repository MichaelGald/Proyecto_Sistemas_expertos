import streamlit as st
from rag import SistemaExpertoUNAH
import os
import chromadb

st.set_page_config(page_title="Sistema Experto UNAH", page_icon="🎓")


st.title("🎓 Sistema Experto UNAH — Mistral 7B")
st.write("Asesor académico basado en documentos oficiales de la UNAH.")

# Inicializar el bot solo una vez
if "bot" not in st.session_state:
    st.session_state.bot = SistemaExpertoUNAH()
    st.session_state.db_cargada = False

# Sección de configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Verificar estado de la base de datos
    vectores_existen = os.path.exists("vectores/") and os.listdir("vectores/")
    
    if vectores_existen:
        st.success("✓ Base de datos encontrada")
        if st.button("🔄 Recargar base de datos"):
            with st.spinner("Cargando base de datos..."):
                st.session_state.bot.db = st.session_state.bot.cargar_vectores_existentes()
                if st.session_state.bot.db is not None:
                    st.session_state.db_cargada = True
                    st.success("Base de datos cargada correctamente")
                else:
                    st.error("Error al cargar la base de datos")
    else:
        st.warning("⚠️ Base de datos no encontrada")
        if st.button("📥 Indexar documentos"):
            with st.spinner("Indexando documentos... Por favor espere, esto puede tardar varios minutos."):
                # Mostrar el progreso en la terminal
                st.info("Revise la terminal/consola para ver el progreso detallado")
                exito = st.session_state.bot.cargar_documentos()
                if exito:
                    st.session_state.db_cargada = True
                    st.success("¡Documentos indexados correctamente!")
                    st.balloons()
                else:
                    st.error("Error al indexar documentos. Revise la terminal para más detalles.")
    
    st.divider()
    st.caption("Verifica que:")
    st.caption("1. Ollama esté ejecutándose")
    st.caption("2. El modelo 'mistral' esté descargado")
    st.caption("3. Los archivos .txt estén en 'documentos_unah_txt/'")

# Cargar base de datos automáticamente si existe
if not st.session_state.db_cargada and vectores_existen:
    with st.spinner("Cargando base de datos..."):
        st.session_state.bot.db = st.session_state.bot.cargar_vectores_existentes()
        if st.session_state.bot.db is not None:
            st.session_state.db_cargada = True
            st.success("Base de datos cargada correctamente")

# Área principal de consultas
if st.session_state.db_cargada:
    st.divider()
    
    pregunta = st.text_area(
        "💬 Ingrese su consulta:", 
        height=100,
        placeholder="Ejemplo: ¿Cuáles son los requisitos para solicitar una beca?"
    )

    if st.button("🔍 Consultar", type="primary"):
        if pregunta.strip():
            with st.spinner("Analizando documentos y generando respuesta..."):
                respuesta = st.session_state.bot.consultar(pregunta)
                st.divider()
                st.subheader("📋 Respuesta")
                st.write(respuesta)
        else:
            st.warning("Por favor ingrese una consulta válida")
else:
    st.info("👆 Por favor cargue o indexe la base de datos desde el panel lateral para comenzar.")