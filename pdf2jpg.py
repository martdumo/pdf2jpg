from pdf2image import convert_from_path
import os
from tkinter import Tk, filedialog

def pdf_a_jpg(pdf_path, output_folder="salida", dpi=300, poppler_path=r"C:\poppler\bin"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    paginas = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)

    for i, pagina in enumerate(paginas, start=1):
        output_path = os.path.join(output_folder, f"pagina_{i}.jpg")
        pagina.save(output_path, "JPEG")
        print(f"Guardado: {output_path}")

if __name__ == "__main__":
    # Oculta la ventana principal de Tk
    Tk().withdraw()

    # Abre el diálogo para elegir archivo
    pdf_path = filedialog.askopenfilename(
        title="Selecciona un archivo PDF",
        filetypes=[("Archivos PDF", "*.pdf")]
    )

    if pdf_path:
        print(f"Procesando: {pdf_path}")
        pdf_a_jpg(pdf_path)
    else:
        print("No seleccionaste ningún archivo.")
