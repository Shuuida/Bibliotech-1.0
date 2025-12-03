"""
Funciones auxiliares de experiencia de usuario (UX) para Biblioteca Virtual
Complementa ui.py: confirmaciones, alertas, exportaciones y backups automáticos.
"""

import os
import shutil
import csv
from datetime import datetime
from PySide6.QtWidgets import QMessageBox, QFileDialog


#Confirmaciones y alertas

def confirmar(parent, titulo, mensaje):
    """Muestra un cuadro de confirmación estándar."""
    return QMessageBox.question(parent, titulo, mensaje,
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes


def alerta(parent, titulo, mensaje):
    QMessageBox.warning(parent, titulo, mensaje)


def info(parent, titulo, mensaje):
    QMessageBox.information(parent, titulo, mensaje)


def error(parent, titulo, mensaje):
    QMessageBox.critical(parent, titulo, mensaje)


#Exportación

def exportar_csv(parent, biblioteca_dict, ruta_default="biblioteca_export.csv"):
    """Exporta la biblioteca a CSV."""
    if not biblioteca_dict:
        alerta(parent, "Exportar CSV", "No hay datos para exportar.")
        return

    ruta, _ = QFileDialog.getSaveFileName(parent, "Exportar a CSV", ruta_default, "CSV (*.csv)")
    if not ruta:
        return

    try:
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ISBN", "Título", "Autor", "Editorial", "Fecha de publicación"])
            for isbn, datos in biblioteca_dict.items():
                writer.writerow([
                    isbn,
                    datos.get("Título", ""),
                    datos.get("Autor", ""),
                    datos.get("Editorial", ""),
                    datos.get("Fecha de publicación", "")
                ])
        info(parent, "Exportar CSV", f"Archivo exportado correctamente en:\n{ruta}")
    except Exception as e:
        error(parent, "Error", f"No se pudo exportar el archivo:\n{e}")


#Backup automático

def crear_backup(ruta_archivo):
    """Crea una copia de seguridad con fecha/hora en la carpeta backups/."""
    if not os.path.exists(ruta_archivo):
        return
    backups_dir = os.path.join(os.path.dirname(ruta_archivo), "backups")
    os.makedirs(backups_dir, exist_ok=True)
    nombre = os.path.basename(ruta_archivo)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    copia = os.path.join(backups_dir, f"{nombre}_{timestamp}.bak")
    shutil.copy2(ruta_archivo, copia)
    return copia


#Undo simple (una acción)

class UndoBuffer:
    """Buffer simple para deshacer la última eliminación o edición."""
    def __init__(self):
        self.stack = []

    def push(self, data_type, data):
        """Guarda una acción ('delete' o 'edit') con los datos previos."""
        self.stack.append((data_type, data))

    def pop(self):
        if not self.stack:
            return None
        return self.stack.pop()

    def clear(self):
        self.stack.clear()
undo_buffer = UndoBuffer()