import streamlit as st
import os
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma

# --- CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="Profesor IA")
st.markdown("""<style>.stAppDeployButton { display: none !important; }</style>""", unsafe_allow_html=True)

llm = ChatOllama(model="llama3.2")
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# --- ESTADO DE SESIÓN ---
if "messages" not in st.session_state: st.session_state.messages = []
if "docs" not in st.session_state: st.session_state.docs = []

# --- FUNCIÓN DE LECTURA (Solo Texto) ---
def procesar_archivo_inteligente(path):
    try:
        if path.endswith('.pdf'): loader = PyPDFLoader(path)
        elif path.endswith('.txt'): loader = TextLoader(path)
        else: loader = Docx2txtLoader(path)
        
        docs = loader.load()
        texto = "\n".join([d.page_content for d in docs])
        
        if not texto.strip():
            return None # Señal de que no hay texto digital
        return texto
    except Exception as e:
        return f"Error: {e}"

# --- INTERFAZ ---
with st.sidebar:
    st.title("📚 Documentos")
    archivo = st.file_uploader("Añadir documento", type=['txt', 'pdf', 'docx'])
    if archivo and st.button("Cargar"):
        os.makedirs("data", exist_ok=True)
        path = f"data/{archivo.name}"
        with open(path, "wb") as f: f.write(archivo.getvalue())
        st.session_state.docs.append(path)
        st.rerun()
    
    st.write("---")
    for d in st.session_state.docs:
        col1, col2 = st.columns([3, 1])
        col1.text(os.path.basename(d))
        if col2.button("🗑️", key=d):
            st.session_state.docs.remove(d)
            os.remove(d)
            st.rerun()

st.title("👨🏻‍🏫 Tu Profesor Particular")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("¿Qué quieres saber sobre tus documentos?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        if st.session_state.docs:
            texto_limpio = procesar_archivo_inteligente(st.session_state.docs[0])
            
            if texto_limpio is None:
                st.error("No pude extraer texto. Por favor, asegúrate de que el PDF contenga texto seleccionable (no sea una imagen escaneada).")
            elif "Error" in str(texto_limpio):
                st.error(texto_limpio)
            else:
                splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                docs = splitter.create_documents([texto_limpio])
                db = Chroma.from_documents(docs, embeddings)
                contexto = "\n".join([d.page_content for d in db.similarity_search(prompt)])
                
                resp = llm.invoke(f"Basado en: {contexto}\n\nPregunta: {prompt}")
                st.markdown(resp.content)
                st.session_state.messages.append({"role": "assistant", "content": resp.content})
        else:
            st.warning("¡Sube un documento primero!")