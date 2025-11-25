import pdfplumber
import os
import sys
from tqdm import tqdm

# --- Configuración ---
carpeta = "documentos_unah/"
salida = "documentos_unah_txt/"

def limpiar_texto(texto):
    """
    Aplica reglas de limpieza para mejorar la legibilidad del texto extraído de PDF:
    1. Elimina guiones al final de línea.
    2. Convierte saltos de línea incorrectos a espacios.
    3. Preserva los saltos de párrafo dobles.
    """
    
    # 1. Reemplazar guiones de fin de línea
    texto_limpio = texto.replace('-\n', '')
    
    # 2. Reemplazar saltos de línea por espacios (excepto saltos dobles)
    # Esto une líneas que se cortaron en el PDF (columnas o diseño)
    # y usa el doble salto de línea (párrafo) como separador lógico.
    parrafos = texto_limpio.split('\n\n')
    texto_final = ""
    
    for parrafo in parrafos:
        # Colapsar múltiples saltos de línea simples dentro de un 'párrafo'
        # en un solo espacio para que la oración no se rompa.
        lineas_parrafo = parrafo.split('\n')
        lineas_parrafo_limpias = [linea.strip() for linea in lineas_parrafo if linea.strip()]
        
        # Unir las líneas internas con un espacio y luego añadir un doble salto para
        # separar el párrafo del siguiente.
        if lineas_parrafo_limpias:
            texto_final += " ".join(lineas_parrafo_limpias) + "\n\n"
            
    return texto_final.strip()

def convertir_pdf_a_md(archivo_pdf):
    """Convierte un único PDF a un archivo Markdown (.md) limpio."""
    ruta_pdf = os.path.join(carpeta, archivo_pdf)
    nombre_salida = archivo_pdf.replace(".pdf", ".md")
    ruta_salida = os.path.join(salida, nombre_salida)
    
    print(f"-> Procesando: {archivo_pdf}")
    
    try:
        texto = ""
        with pdfplumber.open(ruta_pdf) as pdf:
            # Usar tqdm para el progreso de la lectura de páginas
            for page in tqdm(pdf.pages, desc="Páginas"):
                # Extraemos el texto de la página y añadimos un separador de página
                texto += page.extract_text() + "\n\n--- FIN DE PÁGINA ---\n\n"

        # Aplicar la lógica de limpieza
        texto_limpio = limpiar_texto(texto)

        # Escribir el archivo Markdown
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(texto_limpio)

        print(f"✓ Éxito. Guardado en: {ruta_salida}")
        return True

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
    print(f"Conversor de PDF a Markdown ({len(archivos_pdf)} archivos encontrados)")
    print("=" * 50)

    if len(sys.argv) > 1:
        # Modo de Archivo Único para Pruebas
        nombre_archivo_buscado = sys.argv[1]
        
        # Buscar el nombre de archivo que coincida con el argumento
        archivo_a_procesar = next((f for f in archivos_pdf if nombre_archivo_buscado in f), None)
        
        if archivo_a_procesar:
            print(f"MODO PRUEBA: Procesando solo '{archivo_a_procesar}'")
            convertir_pdf_a_md(archivo_a_procesar)
        else:
            print(f"ERROR: Archivo '{nombre_archivo_buscado}' no encontrado en la carpeta '{carpeta}'.")
            print("Archivos disponibles: " + ", ".join(archivos_pdf[:5]) + "...")
            
    else:
        # Modo de Procesamiento Completo
        print("MODO COMPLETO: Procesando todos los archivos...")
        for archivo in archivos_pdf:
            convertir_pdf_a_md(archivo)
        
        print("\n" + "=" * 50)
        print("PROCESAMIENTO COMPLETO FINALIZADO.")
        print("=" * 50)