import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox 
from ui import BibliotecaWindow
from database import asegurar_directorios


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
        qss_path = os.path.join(os.path.dirname(__file__), "styles.qss")
        if os.path.isfile(qss_path):
            with open(qss_path, "r", encoding="utf-8") as style_file:
                app.setStyleSheet(style_file.read())

        try:
            style_path = resource_path("style.qss")
            with open(style_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            print(f"⚠️ No se pudo cargar el estilo: {e}")

        ventana = BibliotecaWindow()
        asegurar_directorios()
        ventana.show()

        sys.exit(app.exec())
    
    except Exception as e:
        QMessageBox.critical(None, "Error crítico", f"Ocurrió un error inesperado al iniciar la aplicación:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()