# ==========================================
# Módulo de lectura avanzada de PDFs
# para el Asistente Bibliotecario Virtual ----Bibliotech----.
# Incluye:
#   - Lectura de metadatos
#   - Extracción de texto
#   - Detección automática de ISBN
#   - Generación y visualización de miniatura de portada
#   - Procesamiento en lote
#   - Vista previa dentro de la UI
# ==========================================

import os
import re
import subprocess
import sys
import fitz  # PyMuPDF
import database
from datetime import datetime
from PySide6.QtWidgets import (
    QFileDialog, QMessageBox, QLabel, QVBoxLayout, QDialog, QPushButton, QWidget, QHBoxLayout
)
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QFont
from PySide6.QtCore import Qt
from typing import Optional

#Funciones Principales

# Lista de nombres alternativos comunes para cada campo
_field_names = {
    "isbn": ["inputISBN", "isbn_input", "isbnInput", "txt_isbn", "inputIsbn", "isbnLineEdit"],
    "titulo": ["inputTitulo", "titulo_input", "title_input", "tituloInput", "tituloLineEdit"],
    "autor": ["inputAutor", "autor_input", "author_input", "autorInput", "autorLineEdit"],
    "editorial": ["inputEditorial", "editorial_input", "publisher_input", "editorialInput", "editorialLineEdit"],
    "fecha": ["inputFecha", "fecha_input", "date_input", "fechaInput", "fechaLineEdit"]
}

def _find_field(parent, candidates):
    """
    Busca en el objeto parent por atributos con nombres en candidates.
    Retorna el widget si existe, o None.
    """
    for name in candidates:
        if hasattr(parent, name):
            return getattr(parent, name)
    # también buscar en children por objectName (si fueron seteados)
    try:
        for child in parent.findChildren(object):
            try:
                oname = child.objectName()
            except Exception:
                oname = None
            if oname and oname in candidates:
                return child
    except Exception:
        pass
    return None

def _safe_set_text(widget, text: str):
    """Intenta asignar texto a un widget QLineEdit / QLabel / similar si existe."""
    if widget is None:
        return False
    try:
        # QLineEdit tiene setText
        if hasattr(widget, "setText"):
            widget.setText(text)
            return True
        # QLabel usa setText también
        if hasattr(widget, "setText"):
            widget.setText(text)
            return True
    except Exception:
        return False
    return False

def importar_pdf(parent):
    """
    Versión robusta para importar PDFs y poblar campos en 'parent'.
    Busca varios nombres comunes para los widgets del formulario y no lanza excepción
    si faltan — en su lugar devuelve/establece parent.current_pdf_path.
    """
    file_paths, _ = QFileDialog.getOpenFileNames(
        parent,
        "Seleccionar archivo(s) PDF",
        "",
        "Archivos PDF (*.pdf)"
    )

    if not file_paths:
        return

    for pdf_path in file_paths:
        try:
            doc = fitz.open(pdf_path)
            info = doc.metadata or {}
            doc.close()
            
            import random
            import string
            titulo = _clean_text(info.get("title") or os.path.splitext(os.path.basename(pdf_path))[0])
            autor = _clean_text(info.get("author") or "Autor desconocido")
            editorial = _clean_text(info.get("producer") or f"Editorial_{''.join(random.choices(string.ascii_uppercase + string.digits, k=5))}")
            fecha_raw = info.get("creationDate", "")
            fecha = _parse_pdf_date(fecha_raw)

            # intentar asignar a widgets con nombres alternativos
            fields = {
                "isbn": _find_field(parent, _field_names["isbn"]),
                "titulo": _find_field(parent, _field_names["titulo"]),
                "autor": _find_field(parent, _field_names["autor"]),
                "editorial": _find_field(parent, _field_names["editorial"]),
                "fecha": _find_field(parent, _field_names["fecha"])
            }

            # Intentar detectar ISBN en las primeras páginas (opcional, aquí no extraemos texto completo)
            texto_preview = ""
            try:
                # intentamos leer las primeras 5 páginas para detectar ISBN si hace falta
                pages = min(len(fitz.open(pdf_path)), 5)
                doc2 = fitz.open(pdf_path)
                texto_preview = ""
                for i in range(pages):
                    try:
                        texto_preview += doc2[i].get_text("text") + "\n"
                    except Exception:
                        pass
                doc2.close()
            except Exception:
                texto_preview = ""

            # si no hay widget de ISBN, igual intentamos detectar ISBN y lo devolvemos a parent
            isbn_detected = None
            try:
                # patrón simple para ISBN (puede mejorarse)
                import re
                patron = r"(97[89][-– ]?\d{1,5}[-– ]?\d{1,7}[-– ]?\d{1,7}[-– ]?\d|(?:\d{1,5}[-– ]?\d{1,7}[-– ]?\d{1,7}[-– ]?[\dX]))"
                match = re.search(patron, texto_preview)
                if match:
                    isbn_detected = match.group(0).replace(" ", "").replace("-", "")
            except Exception:
                isbn_detected = None

            import random
            if not isbn_detected:
                while True:
                    isbn_candidate = str(random.randint(10**9, 10**10 - 1))
                    if isbn_candidate not in getattr(parent, "biblioteca", {}):
                        isbn_detected = isbn_candidate
                        break

            # Asignar valores (si los widgets existen)
            if fields["titulo"]:
                _safe_set_text(fields["titulo"], titulo)
            if fields["autor"]:
                _safe_set_text(fields["autor"], autor)
            if fields["editorial"]:
                _safe_set_text(fields["editorial"], editorial)
            if fields["fecha"]:
                _safe_set_text(fields["fecha"], fecha)
            if fields["isbn"] and isbn_detected:
                _safe_set_text(fields["isbn"], isbn_detected)

            # guardar ruta del pdf en parent para que _on_add la asocie
            parent.current_pdf_path = pdf_path

            # informar al usuario (no fallar si no existe QMessageBox por alguna razón)
            try:
                QMessageBox.information(
                    parent,
                    "PDF importado",
                    f"Archivo leído: {os.path.basename(pdf_path)}\n\n"
                    f"Título: {titulo}\nAutor: {autor or 'Desconocido'}\nEditorial: {editorial or 'N/A'}\nFecha: {fecha or 'Desconocida'}\n"
                    f"{'ISBN detectado: ' + isbn_detected if isbn_detected else ''}"
                )
            except Exception:
                pass

        except Exception as e:
            try:
                QMessageBox.warning(
                    parent,
                    "Error al leer PDF",
                    f"No se pudo procesar el archivo:\n{pdf_path}\n\nDetalles:\n{e}"
                )
            except Exception:
                print("Error al procesar PDF:", pdf_path, e)


def procesar_lote(parent):
    """
    Procesa automáticamente varios PDFs de una carpeta seleccionada.
    Extrae metadatos, ISBN y texto, y los indexa en la biblioteca.
    """
    folder = QFileDialog.getExistingDirectory(parent, "Seleccionar carpeta de PDFs")
    if not folder:
        return

    pdf_files = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
    if not pdf_files:
        QMessageBox.warning(parent, "Sin PDF", "No se encontraron archivos en la carpeta seleccionada")
        return
    nuevos_registros = 0

    for archivo in pdf_files:
        ruta_pdf = os.path.join(folder, archivo)
        try:
            doc = fitz.open(ruta_pdf)
            info = doc.metadata or {}

            titulo = info.get("title") or os.path.splitext(archivo) [0]
            autor = info.get("author", "")
            editorial = info.get("producer", "")
            fecha_raw = info.get("creationDate", "")
            if fecha_raw.startswith("D:"):
                fecha_raw = fecha_raw[2:]
            try:
                fecha_publicacion = datetime.striptime(fecha_raw[:8], "%Y%m%d").strftime("%Y-%m-%d")
            except Exception:
                fecha_publicacion = ""
            #genera miniatura
            portada_path = ""
            try:
                portada_path = generar_miniatura_segura(ruta_pdf, archivo)
            except Exception:
                portada_path = ""

            doc.close()
            #Intenta detectar ISBN en el texto
            isbn_detectado = None
            try:
                texto = ""
                doc2 = fitz.open(ruta_pdf)
                for i in range(min(5, len(doc2))):
                    texto += doc2[i].get_text("text")
                doc2.close()
                import re
                match = re.search(r"(97[89][-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?[\dX])", texto)
                if match:
                    isbn_detectado = match.group(0).replace(" ", "").replace("-", "")
            except Exception:
                isbn_detectado = None

            isbn = isbn_detectado or f"NOISBN_{os.path.splitext(archivo)[0]}"
            #Si ya existe, se lo salta
            if isbn in parent.biblioteca:
                continue
            parent.biblioteca[isbn] = {
                "Título": titulo,
                "Autor": autor,
                "Editorial": editorial,
                "Fecha de publicación": fecha_publicacion,
                "Archivo PDF": ruta_pdf,
                "Portada": portada_path
            }

            nuevos_registros += 1

        except Exception as e:
            print(f"Error procesado {archivo}: {e}")
        #guarda y refresca la tabla
        if nuevos_registros > 0:
            try:
                database.guardar_biblioteca(parent.biblioteca, fecha=parent.selected_date, global_file=parent.use_global)
                parent._actualizar_tabla()
                QMessageBox.information(
                    parent,
                    "Lote Procesado",
                    f"Se procesaron {nuevos_registros} PDF(s) correctamente"
                )
            except Exception as e:
                QMessageBox.critical(parent, "Error al guardar", f"No se pudieron almacenar los libros procesados:\n{e}")
        else:
            QMessageBox.information(parent, "Sin cambios", "No se agregaron nuevos libros al sistema.")


#Funciones de vista/Previsualización

def mostrar_portada(parent, isbn):
    """
    Muestra la miniatura del PDF en un QLabel designado (ej: self.lblPreview)
    cuando el usuario selecciona una fila o un libro en la tabla.
    """
    if not hasattr(parent, "lblPreview"):
        return

    parent.lblPreview.clear()
    parent.lblPreview.setText("Sin vista previa disponible")

    if not hasattr(parent, "biblioteca") or not isinstance(parent.biblioteca, dict):
        return

    datos = parent.biblioteca.get(isbn, {})
    portada_path = datos.get("Portada", "")

    if portada_path and os.path.exists(portada_path):
        image = QImage(portada_path)
        pix = QPixmap.fromImage(image).scaledToWidth(200, Qt.SmoothTransformation)
        parent.lblPreview.setPixmap(pix)
        parent.lblPreview.setAlignment(Qt.AlignCenter)
    else:
        parent.lblPreview.setText("Sin miniatura disponible.")


def abrir_pdf_externo(parent, isbn):
    """
    Abre el PDF vinculado al libro (campo 'Archivo PDF') con la aplicación
    predeterminada del sistema (Word, Acrobat, navegador, etc.)
    """
    if not hasattr(parent, "biblioteca") or not isinstance(parent.biblioteca, dict):
        return

    datos = parent.biblioteca.get(isbn, {})
    pdf_path = datos.get("Archivo PDF", "")

    if not pdf_path or not os.path.exists(pdf_path):
        QMessageBox.warning(parent, "Archivo no encontrado",
                            "No se encontró el archivo PDF asociado a este libro.")
        return

    try:
        #Abrir según sistema operativo
        if sys.platform.startswith('darwin'):  # macOS
            subprocess.call(('open', pdf_path))

        elif os.name == 'nt':  # Windows
            os.startfile(pdf_path)

        elif os.name == 'posix':  # Linux
            subprocess.call(('xdg-open', pdf_path))

        else:
            QMessageBox.information(parent, "Sistema no soportado",
                                    "No se pudo determinar la aplicación predeterminada.")
    except Exception as e:
        QMessageBox.critical(parent, "Error al abrir PDF",
                             f"No se pudo abrir el archivo:\n{pdf_path}\n\nDetalles: {e}")


def vista_previa_pdf(parent, pdf_path):
    """
    Abre un cuadro de diálogo con la portada y los metadatos del PDF seleccionado.
    """
    if not pdf_path or not os.path.exists(pdf_path):
        QMessageBox.warning(parent, "Archivo no encontrado", "El archivo PDF no existe.")
        return

    info = leer_metadatos(pdf_path)
    portada = generar_portada(pdf_path)

    dialog = QDialog(parent)
    dialog.setWindowTitle(info.get("Título", "Vista previa del PDF"))
    dialog.resize(600, 450)

    layout = QVBoxLayout(dialog)

    if portada and os.path.exists(portada):
        image = QImage(portada)
        pix = QPixmap.fromImage(image).scaledToWidth(250, Qt.SmoothTransformation)
        lbl_img = QLabel()
        lbl_img.setPixmap(pix)
        lbl_img.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_img)

    lbl_info = QLabel(
        f"<b>Título:</b> {info.get('Título', '')}<br>"
        f"<b>Autor:</b> {info.get('Autor', '')}<br>"
        f"<b>Editorial:</b> {info.get('Editorial', '')}<br>"
        f"<b>Fecha:</b> {info.get('Fecha', '')}"
    )
    lbl_info.setTextFormat(Qt.RichText)
    lbl_info.setAlignment(Qt.AlignCenter)
    layout.addWidget(lbl_info)

    btn_abrir = QPushButton("Abrir PDF")
    btn_abrir.clicked.connect(lambda: os.startfile(pdf_path))
    layout.addWidget(btn_abrir, alignment=Qt.AlignCenter)

    btn_ok = QPushButton("Cerrar")
    btn_ok.clicked.connect(dialog.accept)
    layout.addWidget(btn_ok, alignment=Qt.AlignCenter)

    dialog.exec()


#Funciones Auxiliares

def leer_metadatos(pdf_path):
    doc = fitz.open(pdf_path)
    info = doc.metadata or {}
    doc.close()

    titulo = _clean_text(info.get("title") or os.path.splitext(os.path.basename(pdf_path))[0])
    autor = _clean_text(info.get("author") or "Desconocido")
    editorial = _clean_text(info.get("producer") or "N/A")
    fecha_raw = info.get("creationDate", "")
    fecha = _parse_pdf_date(fecha_raw)

    return {"Título": titulo, "Autor": autor, "Editorial": editorial, "Fecha": fecha}


def extraer_texto(pdf_path, limit_pages=10):
    texto = []
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        if i >= limit_pages:
            break
        texto.append(page.get_text("text"))
    doc.close()
    return "\n".join(texto)


def detectar_isbn(texto):
    if not texto:
        return None
    patron = r"(97[89][-– ]?\d{1,5}[-– ]?\d{1,7}[-– ]?\d{1,7}[-– ]?\d|(?:\d{1,5}[-– ]?\d{1,7}[-– ]?\d{1,7}[-– ]?[\dX]))"
    coincidencias = re.findall(patron, texto)
    if coincidencias:
        isbn = coincidencias[0].replace(" ", "").replace("-", "").strip()
        return isbn
    return None


def generar_portada(pdf_path):
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    img_path = os.path.join(cache_dir, os.path.splitext(os.path.basename(pdf_path))[0] + "_preview.jpg")

    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        pix.save(img_path)
        doc.close()
        return img_path
    except Exception:
        return ""


def mostrar_resumen(parent, info, isbn, texto, portada_path):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Resumen del PDF")
    dialog.resize(600, 400)
    layout = QVBoxLayout(dialog)

    if portada_path and os.path.exists(portada_path):
        image = QImage(portada_path)
        pix = QPixmap.fromImage(image).scaledToWidth(150, Qt.SmoothTransformation)
        lbl_img = QLabel()
        lbl_img.setPixmap(pix)
        lbl_img.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_img)

    lbl_info = QLabel(
        f"<b>Título:</b> {info.get('Título', '')}<br>"
        f"<b>Autor:</b> {info.get('Autor', '')}<br>"
        f"<b>Editorial:</b> {info.get('Editorial', '')}<br>"
        f"<b>Fecha:</b> {info.get('Fecha', '')}<br>"
        f"<b>ISBN detectado:</b> {isbn or 'Ninguno'}"
    )
    lbl_info.setTextFormat(Qt.RichText)
    layout.addWidget(lbl_info)

    btn_ok = QPushButton("Aceptar")
    btn_ok.clicked.connect(dialog.accept)
    layout.addWidget(btn_ok, alignment=Qt.AlignCenter)
    dialog.exec()



# Funciones Internas
def _parse_pdf_date(raw_date: str) -> str:
    if not raw_date:
        return ""
    try:
        if raw_date.startswith("D:"):
            raw_date = raw_date[2:]
        dt = datetime.strptime(raw_date[:8], "%Y%m%d")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return ""

def _clean_text(text: str) -> str:
    if not text:
        return ""
    return str(text).replace("\x00", "").strip()

def generar_miniatura_segura(pdf_path, nombre_archivo):
    """
    Genera una miniatura (portada) para un PDF de forma segura.
    Si el PDF no puede renderizarse, crea un placeholder visual.
    Devuelve la ruta completa del .jpg generado.
    """
    cache_dir = os.path.join(os.getcwd(), "cache")
    os.makedirs(cache_dir, exist_ok=True)

    # Sanitizar nombre base
    nombre_base = os.path.splitext(os.path.basename(nombre_archivo))[0]
    nombre_base = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in nombre_base)

    portada_path = os.path.join(cache_dir, f"{nombre_base}_preview.jpg")

    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            raise ValueError("El PDF no contiene páginas.")

        # Intentar renderizar la primera página
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        pix.save(portada_path)
        doc.close()

        if os.path.exists(portada_path):
            return portada_path
        else:
            raise FileNotFoundError("No se generó el archivo de portada.")

    except Exception as e:
        print(f"⚠️ No se pudo generar portada para '{nombre_archivo}': {e}")
        # Si falla, generar una imagen de placeholder visual
        try:
            width, height = 400, 550
            image = QImage(width, height, QImage.Format_RGB32)
            painter = QPainter(image)
            painter.fillRect(0, 0, width, height, QColor("#1e1e1e"))
            painter.setPen(QColor("#007acc"))
            painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
            painter.drawText(50, 250, 300, 100, 0x84, "Sin Portada")
            painter.end()
            image.save(portada_path, "JPG")
            return portada_path
        except Exception as img_err:
            print(f"⚠️ Error creando placeholder: {img_err}")
            return ""
