import os
import shutil
# Importaciones simplificadas y directas
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

def crear_base_datos():
    # 1. Limpiar base de datos antigua
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
        print("Base de datos antigua eliminada.")

    # 2. Cargamos los archivos
    print("Cargando archivos...")
    loader = DirectoryLoader('./apuntes', glob="**/*.txt", loader_cls=TextLoader)
    documentos = loader.load()

    # 3. Fragmentamos el texto
    print("Fragmentando texto...")
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    textos = splitter.split_documents(documentos)

    # 4. Creamos los embeddings y la nueva base de datos
    print("Creando base de datos vectorial con Ollama...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    db = Chroma.from_documents(textos, embeddings, persist_directory="./chroma_db")
    print("¡Éxito! Base de datos creada y actualizada.")

if __name__ == "__main__":
    crear_base_datos()