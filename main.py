import os

# Ruta a tus apuntes
ruta_apuntes = "./apuntes"

def listar_apuntes():
    archivos = os.listdir(ruta_apuntes)
    print(f"He encontrado {len(archivos)} archivos en la carpeta:")
    for archivo in archivos:
        print(f"- {archivo}")

if __name__ == "__main__":
    listar_apuntes()