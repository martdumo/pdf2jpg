#!/usr/bin/env python3
"""
Conversor de PDF a Imágenes - Versión Mejorada
Convierte archivos PDF a imágenes JPG/PNG con interfaz gráfica y manejo robusto de errores.
"""

import os
import sys
import platform
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

# Try imports with fallbacks
try:
    from pdf2image import convert_from_path
    from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError
except ImportError:
    print("Error: pdf2image no está instalado. Ejecuta: pip install pdf2image")
    sys.exit(1)

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("Advertencia: tqdm no está instalado. Instálalo para ver barras de progreso.")

# Configuración por defecto
class Config:
    """Configuración global de la aplicación"""
    DPI_DEFAULT = 300
    DPI_MIN = 72
    DPI_MAX = 600
    QUALITY_DEFAULT = 95
    QUALITY_MIN = 1
    QUALITY_MAX = 100
    OUTPUT_FORMATS = [("JPEG", "jpg"), ("PNG", "png")]
    OUTPUT_FORMAT_DEFAULT = "JPEG"
    BASE_OUTPUT_FOLDER = "pdf_conversions"
    
    # Rutas comunes de Poppler por SO
    POPPLER_PATHS = {
        "Windows": [
            r"C:\poppler\bin",
            r"C:\Program Files\poppler\bin", 
            r"C:\Program Files (x86)\poppler\bin"
        ],
        "Darwin": [
            "/opt/homebrew/bin",
            "/usr/local/bin",
            "/opt/local/bin"
        ],
        "Linux": [
            "/usr/bin",
            "/usr/local/bin"
        ]
    }

class PDFConverter:
    """Clase principal para la conversión de PDF a imágenes"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Ocultar ventana principal desde el inicio
        self.setup_logging()
        self.system = platform.system()
        self.poppler_path = self.detect_poppler()
        
    def setup_logging(self):
        """Configura el sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pdf_converter.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def detect_poppler(self) -> Optional[str]:
        """
        Detecta automáticamente la instalación de Poppler en el sistema.
        Retorna la ruta si se encuentra, None si no.
        """
        # Primero verificar si poppler está en PATH
        try:
            result = subprocess.run(
                ["pdftoppm", "-v"] if self.system == "Windows" else ["which", "pdftoppm"],
                capture_output=True,
                check=True,
                text=True
            )
            self.logger.info("Poppler encontrado en PATH del sistema")
            return None
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Buscar en rutas comunes
        possible_paths = Config.POPPLER_PATHS.get(self.system, [])
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"Poppler detectado en: {path}")
                return path
        
        self.logger.warning("Poppler no encontrado en rutas comunes ni en PATH.")
        return None
    
    def validate_pdf(self, pdf_path: str) -> Tuple[bool, str]:
        """Valida que el archivo PDF sea válido y accesible"""
        if not pdf_path:
            return False, "No se proporcionó ninguna ruta"
        
        if not os.path.exists(pdf_path):
            return False, f"El archivo no existe: {pdf_path}"
        
        if not os.path.isfile(pdf_path):
            return False, f"La ruta no es un archivo: {pdf_path}"
        
        if not pdf_path.lower().endswith('.pdf'):
            return False, "El archivo debe tener extensión .pdf"
        
        # Verificar que sea un PDF válido leyendo el header
        try:
            with open(pdf_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    return False, "El archivo no parece ser un PDF válido"
        except Exception as e:
            return False, f"No se pudo leer el archivo: {e}"
        
        return True, "OK"
    
    def get_output_settings(self) -> Optional[dict]:
        """Obtiene la configuración de salida del usuario"""
        try:
            # Nombre de la carpeta
            nombre_base = simpledialog.askstring(
                "Nombre de carpeta",
                "Escribe un nombre para la carpeta de salida:",
                initialvalue="documento"
            )
            
            if nombre_base is None:  # Usuario canceló
                return None
            
            if not nombre_base.strip():
                if not messagebox.askyesno(
                    "Nombre vacío", 
                    "¿Usar nombre por defecto 'documento'?"
                ):
                    return None
                nombre_base = "documento"
            
            # Configuración inicial
            config = {
                "nombre_base": nombre_base.strip(),
                "dpi": Config.DPI_DEFAULT,
                "calidad": Config.QUALITY_DEFAULT,
                "formato": Config.OUTPUT_FORMAT_DEFAULT
            }
            
            if messagebox.askyesno(
                "Configuración avanzada",
                "¿Deseas configurar opciones avanzadas (DPI, calidad, formato)?"
            ):
                # DPI
                dpi = simpledialog.askinteger(
                    "Calidad (DPI)",
                    f"DPI para las imágenes ({Config.DPI_MIN}-{Config.DPI_MAX}):",
                    initialvalue=Config.DPI_DEFAULT,
                    minvalue=Config.DPI_MIN,
                    maxvalue=Config.DPI_MAX
                )
                if dpi is not None:
                    config["dpi"] = dpi
                
                # Formato
                formatos_disponibles = [f[0] for f in Config.OUTPUT_FORMATS]
                formato_input = simpledialog.askstring(
                    "Formato de salida",
                    f"Formato ({'/'.join(formatos_disponibles)}):",
                    initialvalue=Config.OUTPUT_FORMAT_DEFAULT
                )
                if formato_input:
                    formato_upper = formato_input.strip().upper()
                    if formato_upper in formatos_disponibles:
                        config["formato"] = formato_upper
                    else:
                        messagebox.showwarning("Formato inválido", f"Formato '{formato_input}' no reconocido. Se usará {config['formato']}.")
                
                # Calidad JPEG (solo si aplica)
                if config["formato"] == "JPEG":
                    calidad = simpledialog.askinteger(
                        "Calidad JPEG",
                        f"Calidad de compresión ({Config.QUALITY_MIN}-{Config.QUALITY_MAX}):",
                        initialvalue=Config.QUALITY_DEFAULT,
                        minvalue=Config.QUALITY_MIN,
                        maxvalue=Config.QUALITY_MAX
                    )
                    if calidad is not None:
                        config["calidad"] = calidad
                # Si es PNG, no se pide calidad (PNG no la usa)
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error al obtener configuración: {e}")
            messagebox.showerror("Error", f"Error en configuración: {e}")
            return None
    
    def create_output_folder(self, base_folder: str, nombre_base: str) -> Optional[Path]:
        """Crea la estructura de carpetas para la salida"""
        try:
            script_dir = Path(__file__).parent.absolute()
            output_root = script_dir / base_folder
            output_root.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = output_root / f"{nombre_base}_{timestamp}"
            output_folder.mkdir()
            
            self.logger.info(f"Carpeta de salida creada: {output_folder}")
            return output_folder
            
        except Exception as e:
            self.logger.error(f"Error al crear carpeta de salida: {e}")
            messagebox.showerror("Error", f"No se pudo crear la carpeta de salida: {e}")
            return None
    
    def convert_pdf_to_images(self, pdf_path: str, output_folder: Path, 
                            dpi: int, formato: str, calidad: int) -> Tuple[bool, str]:
        """Convierte el PDF a imágenes"""
        try:
            self.logger.info(f"Iniciando conversión: {pdf_path}")
            
            # Convertir PDF a imágenes
            paginas = convert_from_path(
                pdf_path, 
                dpi=dpi, 
                poppler_path=self.poppler_path,
                fmt=formato.lower()
            )
            
            self.logger.info(f"PDF convertido a {len(paginas)} páginas")
            
            # Configurar barra de progreso
            if HAS_TQDM:
                paginas_iter = tqdm(paginas, desc="Procesando páginas")
            else:
                paginas_iter = paginas
                print(f"Procesando {len(paginas)} páginas...")
            
            # Guardar cada página
            extension = dict(Config.OUTPUT_FORMATS)[formato]
            for i, pagina in enumerate(paginas_iter, 1):
                nombre_archivo = f"pagina_{i:03d}.{extension}"
                output_path = output_folder / nombre_archivo
                
                save_kwargs = {}
                if formato == "JPEG":
                    save_kwargs["quality"] = calidad
                    save_kwargs["optimize"] = True
                
                pagina.save(output_path, formato, **save_kwargs)
                
                if not HAS_TQDM:
                    print(f"Guardado: {nombre_archivo}")
            
            self.logger.info(f"Conversión completada: {len(paginas)} páginas guardadas")
            return True, f"Conversión exitosa: {len(paginas)} páginas"
            
        except PDFInfoNotInstalledError:
            error_msg = "Poppler no está instalado o no se encontró. Instala poppler-utils."
            self.logger.error(error_msg)
            return False, error_msg
        except PDFPageCountError:
            error_msg = "No se pudo determinar el número de páginas del PDF."
            self.logger.error(error_msg)
            return False, error_msg
        except PDFSyntaxError:
            error_msg = "El archivo PDF está corrupto o tiene sintaxis inválida."
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error inesperado durante la conversión: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def open_folder(self, folder_path: Path):
        """Abre la carpeta en el explorador de archivos del sistema"""
        try:
            folder_str = str(folder_path)
            
            if self.system == "Windows":
                subprocess.Popen(f'explorer "{folder_str}"')
            elif self.system == "Darwin":
                subprocess.Popen(["open", folder_str])
            else:  # Linux y otros
                subprocess.Popen(["xdg-open", folder_str])
            
            self.logger.info(f"Carpeta abierta: {folder_path}")
            
        except Exception as e:
            self.logger.warning(f"No se pudo abrir la carpeta automáticamente: {e}")
            messagebox.showwarning(
                "Abrir carpeta", 
                f"No se pudo abrir la carpeta automáticamente:\n{folder_str}"
            )
    
    def select_pdf_file(self) -> Optional[str]:
        """Muestra diálogo para seleccionar archivo PDF"""
        file_path = filedialog.askopenfilename(
            title="Selecciona un archivo PDF",
            filetypes=[
                ("Archivos PDF", "*.pdf"),
                ("Todos los archivos", "*.*")
            ]
        )
        return file_path if file_path else None
    
    def check_poppler_warning(self) -> bool:
        """Advierte si Poppler no se detectó (especialmente en Windows)"""
        if self.poppler_path is None and self.system == "Windows":
            respuesta = messagebox.askyesno(
                "Poppler no detectado",
                "No se encontró Poppler en tu sistema. Es necesario para convertir PDFs.\n\n"
                "¿Deseas continuar de todos modos? (Es probable que falle si no está instalado)"
            )
            return respuesta
        return True  # En macOS/Linux, confiamos en que esté en PATH o el usuario lo tenga
    
    def run_conversion(self):
        """Ejecuta el proceso completo de conversión"""
        self.logger.info("Iniciando aplicación de conversión PDF a imágenes")
        
        # Advertencia temprana sobre Poppler (solo en Windows)
        if not self.check_poppler_warning():
            self.logger.info("Usuario canceló tras advertencia de Poppler")
            return
        
        # Seleccionar archivo PDF
        pdf_path = self.select_pdf_file()
        if not pdf_path:
            self.logger.info("Usuario canceló la selección de archivo")
            return
        
        # Validar PDF
        es_valido, mensaje = self.validate_pdf(pdf_path)
        if not es_valido:
            messagebox.showerror("Error en PDF", mensaje)
            self.logger.error(f"PDF inválido: {mensaje}")
            return
        
        # Obtener configuración
        config = self.get_output_settings()
        if not config:
            self.logger.info("Usuario canceló la configuración")
            return
        
        # Crear carpeta de salida
        output_folder = self.create_output_folder(
            Config.BASE_OUTPUT_FOLDER, 
            config["nombre_base"]
        )
        if not output_folder:
            return
        
        # Realizar conversión
        exito, mensaje = self.convert_pdf_to_images(
            pdf_path,
            output_folder,
            config["dpi"],
            config["formato"],
            config["calidad"]
        )
        
        # Mostrar resultados
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            if messagebox.askyesno("Abrir carpeta", "¿Deseas abrir la carpeta de resultados?"):
                self.open_folder(output_folder)
        else:
            messagebox.showerror("Error en conversión", mensaje)
        
        self.logger.info("Proceso de conversión finalizado")
    
    def cleanup(self):
        """Limpia la instancia de Tk"""
        try:
            self.root.destroy()
        except tk.TclError:
            pass  # Ya destruida

def main():
    """Función principal de la aplicación"""
    converter = None
    try:
        converter = PDFConverter()
        converter.run_conversion()
    except Exception as e:
        logging.error(f"Error fatal en la aplicación: {e}")
        messagebox.showerror("Error fatal", f"La aplicación encontró un error: {e}")
    finally:
        if converter:
            converter.cleanup()

if __name__ == "__main__":
    main()