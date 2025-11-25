import pdfplumber
import os
import sys
from tqdm import tqdm

# --- Configuración ---
carpeta = "documentos_unah/"
salida = "documentos_unah_txt/"

def formatear_a_markdown(tabla):
    """
    Convierte una lista de listas (una tabla extraída) a formato Markdown.
    """
    if not tabla:
        return ""
    
    markdown_output = ""
    
    # 1. Encabezado de la tabla (primera fila)
    header = [str(col or '').strip() for col in tabla[0]]
    markdown_output += "| " + " | ".join(header) + " |\n"
    
    # 2. Separador de encabezado (necesario en Markdown)
    separador = ["---"] * len(header)
    markdown_output += "| " + " | ".join(separador) + " |\n"
    
    # 3. Contenido de las filas restantes
    for row in tabla[1:]:
        row_content = [str(col or '').strip() for col in row]
        markdown_output += "| " + " | ".join(row_content) + " |\n"
        
    return markdown_output + "\n"

def procesar_tablas(archivo_pdf):
    """Busca y extrae todas las tablas de un PDF y las guarda en formato Markdown."""
    ruta_pdf = os.path.join(carpeta, archivo_pdf)
    nombre_salida = archivo_pdf.replace(".pdf", "_tablas.md")
    ruta_salida = os.path.join(salida, nombre_salida)
    
    print(f"-> Procesando tablas en: {archivo_pdf}")
    
    texto_md_final = ""
    num_tablas_extraidas = 0
    
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            # Usar tqdm para el progreso de la lectura de páginas
            for i, page in enumerate(tqdm(pdf.pages, desc="Páginas")):
                
                # Intentar extraer todas las tablas de la página
                tablas = page.extract_tables()
                
                if tablas:
                    texto_md_final += f"\n\n## Tabla(s) de la Página {i+1}\n\n"
                    for tabla_data in tablas:
                        texto_md_final += formatear_a_markdown(tabla_data)
                        num_tablas_extraidas += 1
        
        if num_tablas_extraidas > 0:
            # Escribir el archivo Markdown
            with open(ruta_salida, "w", encoding="utf-8") as f:
                f.write(texto_md_final.strip())

            print(f"✓ Éxito. {num_tablas_extraidas} tablas guardadas en: {ruta_salida}")
            return True
        else:
            print("INFO: No se encontraron tablas estructuradas.")
            return False

    except Exception as e:
        print(f"✗ ERROR al procesar {archivo_pdf}: {e}")
        return False

# --- Lógica Principal de Ejecución ---

if __name__ == "__main__":
    os.makedirs(salida, exist_ok=True)
    
    # 1. Obtener la lista de archivos PDF
    archivos_pdf = [f for f in os.listdir(carpeta) if f.endswith(".pdf")]
    
    if not archivos_pdf:
        print(f"No se encontraron archivos .pdf en la carpeta: {carpeta}")
        sys.exit(0)

    print("=" * 50)
    print("Conversor de PDF a Tablas Markdown (Tablas Estructuradas)")
    print("=" * 50)

    if len(sys.argv) > 1:
        # MODO PRUEBA: Procesar Archivo Único
        nombre_archivo_buscado = sys.argv[1]
        archivo_a_procesar = next((f for f in archivos_pdf if nombre_archivo_buscado in f), None)
        
        if archivo_a_procesar:
            print(f"MODO PRUEBA: Procesando solo '{archivo_a_procesar}'")
            procesar_tablas(archivo_a_procesar)
        else:
            print(f"ERROR: Archivo '{nombre_archivo_buscado}' no encontrado en la carpeta '{carpeta}'.")
            
    else:
        # MODO COMPLETO: Procesar todos
        print("MODO COMPLETO: Procesando todos los archivos...")
        for archivo in archivos_pdf:
            procesar_tablas(archivo)
        
        print("\n" + "=" * 50)
        print("PROCESAMIENTO COMPLETO FINALIZADO.")
        print("=" * 50)