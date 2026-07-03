# Documentación del Proyecto: Mi Profesor Particular

## 1. Introducción y Objetivo
El objetivo de este proyecto es desarrollar una herramienta de IA privada y local que funcione como un tutor personal. A diferencia de los modelos basados en la nube (como GPT-4), este sistema permite consultar apuntes personales sin enviar datos fuera de tu máquina, garantizando privacidad total y coste cero de ejecución.

## 2. Arquitectura del Sistema (RAG)
Hemos implementado una arquitectura RAG (Retrieval-Augmented Generation). Este flujo permite que el modelo no "invente" respuestas, sino que se base exclusivamente en los documentos proporcionados.



## 3. Stack Tecnológico
* **Lenguaje:** Python.
* **Orquestación:** LangChain (para conectar piezas).
* **Base de Datos Vectorial:** ChromaDB (gestión de memoria a largo plazo).
* **Motor de IA Local:** Ollama (ejecutando Llama 3.2 para generación y Nomic-Embed-Text para embeddings).

## 4. Desafíos Técnicos y Soluciones

| Problema | Solución |
| :--- | :--- |
| **Variables de Entorno** | Configuración manual del PATH tras la instalación de Ollama. |
| **Conflictos de Dependencias** | Recreación del entorno virtual (venv) y estandarización de versiones. |
| **Error 501 (Embeddings)** | Cambio del modelo de embeddings a `nomic-embed-text` y uso de `ollama serve`. |
| **Versiones de LangChain** | Simplificación de la lógica de consulta mediante búsqueda de similitud manual, eliminando dependencias de `langchain.chains`. |

## 5. Proceso de Uso

### Preparación
1. Colocar los archivos de texto (.txt) dentro de la carpeta `./apuntes`.

### Ingesta de Datos
Para actualizar el conocimiento del profesor, ejecuta el script de ingesta. Este proceso borra la base de datos anterior y procesa los nuevos archivos:
`.\venv\Scripts\python.exe main.py`

### Consulta
Para preguntar al profesor sobre tus apuntes:
`.\venv\Scripts\python.exe consulta.py "¿Tu pregunta aquí?"`

## 6. Mantenimiento
El sistema utiliza una base de datos vectorial persistente en `./chroma_db`. Si realizas cambios en los archivos .txt, es obligatorio ejecutar `main.py` de nuevo para que el sistema "aprenda" las modificaciones, ya que la base de datos no es dinámica en tiempo real.