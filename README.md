# PDF a JPG Converter

Convierte cada página de un PDF en una imagen JPG manteniendo texto y formato.  
Ahora soporta **subcarpetas únicas por conversión** y **abre automáticamente la carpeta de salida** al terminar.  

---

## 🚀 Características

✅ Convierte cada página de un PDF a JPG en alta calidad (300 DPI por defecto).  
✅ Guarda los resultados en `salida/` en la misma carpeta del script.  
✅ Crea una subcarpeta única por cada PDF convertido:  
   - Podés elegir un nombre (ej. `libro`)  
   - Se le agrega fecha y hora exacta (ej. `libro_20250909_143432`)  
✅ Abre la carpeta de salida automáticamente (Windows, macOS, Linux).  

---

## 📦 Instalación

### 1️⃣ Instalar dependencias

```bash
pip install -r requirements.txt

2️⃣ Instalar Poppler

    Windows:

        Descargar Poppler para Windows

    Extraer en C:\poppler

    Asegurarse de que C:\poppler\bin\pdfinfo.exe existe

Linux:

sudo apt-get install poppler-utils

macOS:

    brew install poppler

🖥 Uso

python pdf2jpg.py

    Se abrirá un diálogo para seleccionar un PDF

    Se pedirá un nombre de carpeta

    Se convertirán las páginas y se abrirá la carpeta de salida automáticamente

Ejemplo de estructura resultante:

pdf2jpg/
├── pdf2jpg.py
├── salida/
│   └── libro_20250909_143432/
│       ├── pagina_1.jpg
│       ├── pagina_2.jpg
│       └── ...


---
