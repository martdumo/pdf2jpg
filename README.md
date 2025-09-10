# PDF a JPG Converter

Este programa convierte cada página de un archivo PDF en una imagen JPG, preservando texto y formato.  

## 🚀 Requisitos

- Python 3.9 o superior
- Poppler instalado (necesario para `pdf2image`)

### Instalación de dependencias

```bash
pip install -r requirements.txt

Instalación de Poppler en Windows

    Descargar desde: Poppler for Windows

    Extraer en C:\poppler

    Asegurarse de que exista C:\poppler\bin\pdfinfo.exe

📌 Uso

python pdf2jpg.py

Se abrirá un diálogo para elegir un PDF y generará los JPG en la carpeta salida/.