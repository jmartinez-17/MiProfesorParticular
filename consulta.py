import sys
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama

def consultar_apuntes(pregunta):
    # 1. Cargamos la base de datos
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    
    # 2. Buscamos los documentos relevantes manualmente
    docs = db.similarity_search(pregunta, k=3)
    contexto = "\n".join([doc.page_content for doc in docs])

    # 3. Llamamos directamente al modelo
    llm = ChatOllama(model="llama3.2")
    
    prompt = f"""
    Responde a la pregunta basándote en el siguiente contexto:
    {contexto}
    
    Pregunta: {pregunta}
    """
    
    respuesta = llm.invoke(prompt)
    
    print("\n--- Respuesta del Profesor ---")
    print(respuesta.content)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pregunta_usuario = " ".join(sys.argv[1:])
        consultar_apuntes(pregunta_usuario)
    else:
        print("Uso: python consulta.py 'Tu pregunta aquí'")