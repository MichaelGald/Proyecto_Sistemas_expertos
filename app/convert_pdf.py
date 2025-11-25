import pdfplumber
import os

carpeta = "documentos_unah/"
salida = "documentos_unah_txt/"

os.makedirs(salida, exist_ok=True)

for archivo in os.listdir(carpeta):
    if archivo.endswith(".pdf"):
        ruta = os.path.join(carpeta, archivo)
        with pdfplumber.open(ruta) as pdf:
            texto = ""
            for page in pdf.pages:
                texto += page.extract_text() + "\n"

        with open(os.path.join(salida, archivo.replace(".pdf", ".txt")), "w", encoding="utf-8") as f:
            f.write(texto)

print("PDF convertidos a TXT.")
