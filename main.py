import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox 
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from core.ui import BibliotecaWindow
from core.database import asegurar_directorios


def resource_path(relative_path):
    """Obtiene la ruta absoluta cuando se ejecuta desde .exe o desde Python"""
    try:
        base_path = sys._MEIPASS  # ruta temporal que crea PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def preparar_directorios():
    """
    Crea automáticamente la estructura base del programa
    si no existen las carpetas necesarias (data, backup, cache).
    """
    base_dirs = [
        "data",
        os.path.join("data", "backups"),
        "cache"
    ]

    for ruta in base_dirs:
        try:
            os.makedirs(ruta, exist_ok=True)
        except Exception as e:
            # En caso de error (permisos, disco lleno, etc.)
            print(f"⚠️ No se pudo crear la carpeta '{ruta}': {e}")
            QMessageBox.warning(
                None,
                "Error de inicialización",
                f"No se pudo crear la carpeta requerida:\n{ruta}\n\nDetalles: {e}"
            )

    print("📁 Estructura de carpetas verificada correctamente.")

def main():
    
    preparar_directorios()

    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        import ctypes
        try:
            scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            if scale_factor > 125:
                style_path = resource_path("assets/styles_fluent.qss")
                print(f"🔍 Pantalla HiDPI detectada ({scale_factor}%) — usando estilo escalado.")
            else:
                style_path = resource_path("assets/styles_default.qss")
                print(f"🔍 Pantalla estándar detectada ({scale_factor}%) — usando estilo normal.")
        except Exception as e:
            print(f"⚠️ No se pudo detectar la escala de la pantalla: {e}")
            style_path = resource_path("assets/styles_default.qss")

        try:
            with open(style_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            print(f"⚠️ No se pudo cargar el estilo: {e}")

        ventana = BibliotecaWindow()

        icon_path = resource_path("assets/icon.ico")
        ventana.setWindowIcon(QIcon(icon_path))

        asegurar_directorios()
        ventana.show()

        sys.exit(app.exec())
    
    except Exception as e:
        QMessageBox.critical(None, "Error crítico", f"Ocurrió un error inesperado al iniciar la aplicación:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()