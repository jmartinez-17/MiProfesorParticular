import streamlit as st
import os
import easyocr
from pdf2image import convert_from_path
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma

# --- CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="Profesor IA")
st.markdown("""<style>.stAppDeployButton { display: none !important; }</style>""", unsafe_allow_html=True)

# Inicializar EasyOCR (se ejecuta una sola vez)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['es', 'en'])

reader = load_ocr()
llm = ChatOllama(model="llama3.2")
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# --- ESTADO DE SESIÓN ---
if "messages" not in st.session_state: st.session_state.messages = []
if "docs" not in st.session_state: st.session_state.docs = []

# --- FUNCIÓN DE LECTURA INTELIGENTE ---
def procesar_archivo_inteligente(path):
    texto = ""
    # 1. Intento de carga estándar
    if path.endswith('.pdf'):
        loader = PyPDFLoader(path)
        docs = loader.load()
        texto = "\n".join([d.page_content for d in docs])
    elif path.endswith('.txt'):
        texto = open(path, 'r', encoding='utf-8').read()
    else:
        loader = Docx2txtLoader(path)
        texto = "\n".join([d.page_content for d in loader.load()])
    
    # 2. Si sigue vacío (ej: PDF escaneado), usar EasyOCR
    if not texto.strip() and path.endswith('.pdf'):
        images = convert_from_path(path)
        for img in images:
            resultado = reader.readtext(img, detail=0)
            texto += " ".join(resultado) + "\n"
            
    return texto

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
            try:
                texto_limpio = procesar_archivo_inteligente(st.session_state.docs[0])
                if not texto_limpio.strip():
                    st.error("No se pudo extraer texto. Archivo ilegible.")
                else:
                    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                    docs = splitter.create_documents([texto_limpio])
                    db = Chroma.from_documents(docs, embeddings)
                    contexto = "\n".join([d.page_content for d in db.similarity_search(prompt)])
                    
                    resp = llm.invoke(f"Basado en: {contexto}\n\nPregunta: {prompt}")
                    st.markdown(resp.content)
                    st.session_state.messages.append({"role": "assistant", "content": resp.content})
            except Exception as e:
                st.error(f"Error técnico: {e}")
        else:
            st.warning("¡Sube un documento primero!")