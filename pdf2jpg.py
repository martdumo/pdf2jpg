import os
import platform
import subprocess
from datetime import datetime
from tkinter import Tk, filedialog, simpledialog
from pdf2image import convert_from_path

def abrir_carpeta(ruta):
    """Abre una carpeta en el explorador de archivos según el sistema operativo."""
    try:
        sistema = platform.system()
        if sistema == "Windows":
            subprocess.Popen(f'explorer "{ruta}"')
        elif sistema == "Darwin":  # macOS
            subprocess.Popen(["open", ruta])
        else:  # Linux y otros
            subprocess.Popen(["xdg-open", ruta])
    except Exception as e:
        print(f"No se pudo abrir la carpeta automáticamente: {e}")

def pdf_a_jpg(pdf_path, base_output_folder="salida", dpi=300, poppler_path=r"C:\poppler\bin"):
    # Carpeta principal de salida (en la misma carpeta que el script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_root = os.path.join(script_dir, base_output_folder)

    if not os.path.exists(output_root):
        os.makedirs(output_root)

    # Pedir nombre para la subcarpeta
    nombre_base = simpledialog.askstring(
        "Nombre de carpeta",
        "Escribe un nombre para la carpeta de salida (ej: libro):"
    )

    if not nombre_base:
        nombre_base = "exportacion"

    # Generar nombre único con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join(output_root, f"{nombre_base}_{timestamp}")
    os.makedirs(output_folder)

    # Convertir PDF a imágenes
    paginas = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)

    for i, pagina in enumerate(paginas, start=1):
        output_path = os.path.join(output_folder, f"pagina_{i}.jpg")
        pagina.save(output_path, "JPEG")
        print(f"Guardado: {output_path}")

    # Abrir carpeta de salida automáticamente
    abrir_carpeta(output_folder)

if __name__ == "__main__":
    # Ocultar ventana principal de Tk
    Tk().withdraw()

    # Selección de archivo PDF
    pdf_path = filedialog.askopenfilename(
        title="Selecciona un archivo PDF",
        filetypes=[("Archivos PDF", "*.pdf")]
    )

    if pdf_path:
        print(f"Procesando: {pdf_path}")
        pdf_a_jpg(pdf_path)
    else:
        print("No seleccionaste ningún archivo.")
