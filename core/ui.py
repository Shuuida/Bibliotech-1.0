"""
Interfaz principal de la Biblioteca (VS Code - style sidebar, funcional)
Requiere: PySide6, y los módulos database.py, models.py, utils.py
"""

import os
from datetime import date

from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QFont, QAction, QIcon, QPixmap, QImage
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QAbstractItemView, QApplication, QComboBox, QDateEdit, QCheckBox,
    QSpinBox, QFrame, QSplitter, QSizePolicy, QToolButton, QStatusBar,
    QFileDialog, QMenu, QDialog
)

from models import Libro
import database 
import shutil
import utils
import ux_helpers as ux
import pdf_reader
import json


# Ruta del QSS local (si existe) — preferimos usar styles.qss del proyecto
STYLE_PATH = os.path.join(os.path.dirname(__file__), "styles.qss")


class BibliotecaWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bibliotech — Asistente Bibliotecario Virtual")
        self.resize(1360, 768)
        self.setMinimumSize(900, 600)

        # Intentar cargar QSS externo; si no, aplicar tema por defecto
        if os.path.exists(STYLE_PATH):
            with open(STYLE_PATH, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            self.setStyleSheet(self._default_dark_qss())

        # Fuente legible
        base_font = QFont("Segoe UI", 10)
        QApplication.instance().setFont(base_font)

        # Estado de persistencia
        self.use_global = False
        self.selected_date = date.today()

        # Cargar datos
        self.biblioteca = database.cargar_biblioteca(fecha=self.selected_date, global_file=self.use_global)

        # Autosave
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._autoguardar)

        # Construcción UI
        self._build_ui()
        self._connect_signals()

        # Inicializar tabla
        self._actualizar_tabla()
        # Tabla de opciones al oprimir click derecho.
        self._setup_context_menu()

        # Mensaje inicial
        self.status.showMessage("Listo — datos cargados.", 4000)

    #UI BUILDERS
    def _build_ui(self):
        root_layout = QHBoxLayout(self)
        # Sidebar (estilo VS Code)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(260)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(12, 12, 12, 12)
        sb_layout.setSpacing(10)

        title = QLabel("Bibliotech")
        title.setObjectName("app_title")
        title.setFont(QApplication.instance().font())
        title.setStyleSheet("font-weight: 700; font-size: 14pt;")
        sb_layout.addWidget(title)

        # Storage mode controls
        sb_layout.addWidget(QLabel("Modo almacenamiento:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Diario (por fecha)", "Global (un solo archivo)"])
        sb_layout.addWidget(self.mode_combo)

        sb_layout.addWidget(QLabel("Fecha (archivo diario):"))
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        sb_layout.addWidget(self.date_edit)

        self.btn_load = QPushButton("Cargar archivo")
        self.btn_load.setCursor(Qt.PointingHandCursor)
        sb_layout.addWidget(self.btn_load)

        self.btn_list_files = QPushButton("Listar archivos diarios")
        self.btn_list_files.setCursor(Qt.PointingHandCursor)
        sb_layout.addWidget(self.btn_list_files)

        sb_layout.addSpacing(8)
        # Search
        sb_layout.addWidget(QLabel("Buscar (título/autor):"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Escribe para buscar (filtro en tiempo real)...")
        sb_layout.addWidget(self.search_input)

        # Auto-save controls
        sb_layout.addSpacing(8)
        self.autosave_checkbox = QCheckBox("Auto-save")
        self.autosave_checkbox.setCursor(Qt.PointingHandCursor)
        sb_layout.addWidget(self.autosave_checkbox)

        autosave_row = QHBoxLayout()
        autosave_row.addWidget(QLabel("Intervalo (s):"))
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(5, 3600)
        self.autosave_interval.setValue(60)
        autosave_row.addWidget(self.autosave_interval)
        sb_layout.addLayout(autosave_row)

        # Backup info & actions
        sb_layout.addSpacing(10)
        self.btn_reload_from_disk = QPushButton("Recargar desde archivo (disco)")
        self.btn_reload_from_disk.setCursor(Qt.PointingHandCursor)
        sb_layout.addWidget(self.btn_reload_from_disk)

        sb_layout.addStretch()

        # Quick actions (add/edit/delete shortcuts)
        act_label = QLabel("Acciones rápidas")
        act_label.setStyleSheet("color: #9AA5B1; font-size: 10pt;")
        sb_layout.addWidget(act_label)
        self.quick_edit_btn = QPushButton("Editar seleccionado")
        self.quick_edit_btn.setCursor(Qt.PointingHandCursor)
        sb_layout.addWidget(self.quick_edit_btn)
        self.quick_delete_btn = QPushButton("Eliminar seleccionado")
        self.quick_delete_btn.setCursor(Qt.PointingHandCursor)
        sb_layout.addWidget(self.quick_delete_btn)
        self.quick_export_btn = QPushButton("Exportar CSV")
        self.quick_export_btn.setCursor(Qt.PointingHandCursor)
        sb_layout.addWidget(self.quick_export_btn)
        self.btn_procesar_lote = QPushButton("Procesar Lote PDF")
        self.btn_procesar_lote.setCursor(Qt.PointingHandCursor)
        self.btn_procesar_lote.setToolTip("Procesar todos los PDFs en una carpeta")
        sb_layout.addWidget(self.btn_procesar_lote)
        self.btn_portada = QPushButton("🖼️ Añadir Portada")
        self.btn_portada.setCursor(Qt.PointingHandCursor)
        self.btn_portada.setToolTip("Seleccionar e insertar una imagen de portada para el libro seleccionado.")
        sb_layout.addWidget(self.btn_portada)


        # Main area (splitter: form / table)
        main_frame = QFrame()
        main_frame_layout = QVBoxLayout(main_frame)
        main_frame_layout.setContentsMargins(12, 12, 12, 12)

        # Top toolbar (buttons)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        self.add_btn = QPushButton("Agregar")
        self.edit_btn = QPushButton("Editar")
        self.delete_btn = QPushButton("Eliminar")
        self.clear_btn = QPushButton("Limpiar campos")
        self.reload_btn = QPushButton("Recargar archivo")
        self.btn_importar_pdf = QPushButton("Importar PDF")
        btns = [self.add_btn, self.edit_btn, self.delete_btn, self.clear_btn, self.reload_btn, self.btn_importar_pdf]
        for b in btns:
            b.setCursor(Qt.PointingHandCursor)
            b.setMinimumHeight(34)
            toolbar.addWidget(b)
        toolbar.addStretch()

        main_frame_layout.addLayout(toolbar)

        # Form (inputs) - organized in grid for compactness
        form = QFrame()
        form_layout = QGridLayout(form)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(8)

        lbl_isbn = QLabel("ISBN:")
        self.isbn_input = QLineEdit()
        self.isbn_input.setPlaceholderText("Ej. 978-1234567897")
        self.isbn_input.setClearButtonEnabled(True)

        lbl_titulo = QLabel("Título:")
        self.titulo_input = QLineEdit()
        self.titulo_input.setPlaceholderText("Título del libro")

        lbl_autor = QLabel("Autor:")
        self.autor_input = QLineEdit()
        self.autor_input.setPlaceholderText("Nombre del autor")

        lbl_editorial = QLabel("Editorial:")
        self.editorial_input = QLineEdit()
        self.editorial_input.setPlaceholderText("Editorial")

        lbl_fecha = QLabel("Fecha de Publicación (YYYY-MM-DD):")
        self.fecha_input = QLineEdit()
        self.fecha_input.setPlaceholderText("YYYY-MM-DD")
        self.fecha_input.setClearButtonEnabled(True)

        self.lblPreview = QLabel("Sin vista previa disponible.")
        self.lblPreview.setAlignment(Qt.AlignCenter)
        self.lblPreview.setStyleSheet("border: 1px solid #555; padding: 8px; color: #bbb; background-color: #0b1220;")
        self.lblPreview.setMinimumSize(220, 300)
        main_frame_layout.addWidget(self.lblPreview)

        # Add to grid
        form_layout.addWidget(lbl_isbn, 0, 0)
        form_layout.addWidget(self.isbn_input, 0, 1)
        form_layout.addWidget(lbl_titulo, 1, 0)
        form_layout.addWidget(self.titulo_input, 1, 1)
        form_layout.addWidget(lbl_autor, 2, 0)
        form_layout.addWidget(self.autor_input, 2, 1)
        form_layout.addWidget(lbl_editorial, 3, 0)
        form_layout.addWidget(self.editorial_input, 3, 1)
        form_layout.addWidget(lbl_fecha, 4, 0)
        form_layout.addWidget(self.fecha_input, 4, 1)

        main_frame_layout.addWidget(form)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ISBN", "Título", "Autor", "Editorial", "Fecha de Publicación"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self._on_table_selection)
        self.table.itemDoubleClicked.connect(self._on_table_double_click)
        main_frame_layout.addWidget(self.table)

        # Status bar
        self.status = QStatusBar()
        self.status.setSizeGripEnabled(False)
        main_frame_layout.addWidget(self.status)

        # Splitter to allow resizing between sidebar and main
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(sidebar)
        splitter.addWidget(main_frame)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        root_layout.addWidget(splitter)

        # Set some accessible names for easier debugging/testing
        self.setObjectName("biblioteca_window")

    #Signal connections
    def _connect_signals(self):
        # Sidebar
        self.btn_load.clicked.connect(self._on_load_clicked)
        self.btn_list_files.clicked.connect(self._on_list_files)
        self.btn_reload_from_disk.clicked.connect(self._on_reload_from_disk)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.date_edit.dateChanged.connect(self._on_date_changed)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.btn_list_files.clicked.connect(self._on_list_files)
        self.btn_importar_pdf.clicked.connect(lambda: pdf_reader.importar_pdf(self))
        self.btn_procesar_lote.clicked.connect(lambda: pdf_reader.procesar_lote(self))
        self.btn_portada.clicked.connect(self._asignar_portada_manual)

        # Quick actions
        self.quick_edit_btn.clicked.connect(self._on_quick_edit)
        self.quick_delete_btn.clicked.connect(self._on_quick_delete)
        self.quick_export_btn.clicked.connect(lambda: ux.exportar_csv(self, self.biblioteca))

        # Toolbar buttons
        self.add_btn.clicked.connect(self._on_add)
        self.edit_btn.clicked.connect(self._on_edit)
        self.delete_btn.clicked.connect(self._on_delete)
        self.clear_btn.clicked.connect(self._on_clear)
        self.reload_btn.clicked.connect(self._on_reload_from_disk)

        # Table interactions
        self.table.cellDoubleClicked.connect(self._on_table_double_clicked)
        self.table.itemSelectionChanged.connect(self._on_table_selection_changed)

        # Autosave controls
        self.autosave_checkbox.toggled.connect(self._on_autosave_toggled)

    #UI ACTIONS
    def _on_mode_changed(self, idx):
        self.use_global = (idx == 1)
        self.status.showMessage("Modo cambiado a global." if self.use_global else "Modo cambiado a diario.", 3000)

    def _on_date_changed(self, qdate):
        self.selected_date = date(qdate.year(), qdate.month(), qdate.day())
        self.status.showMessage(f"Fecha seleccionada: {self.selected_date.isoformat()}", 2500)

    def _on_load_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de Biblioteca",
            "data/",
            "Archivo JSON (*.json);;Todos los archivos (*)"
        )
        if not file_path:
            return #usuario canceló
        
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Archivo no encontrado", "El archivo seleccionado no existe o no es el formato requerido.")
            return
        
        try:
            with open(file_path, "r", encouding = "utf-8") as f:
                data = json.load(f)
                #Normaliza claves antiguas de ser necesario
                for isbn, datos in list(data.items()):
                    if "Titulo" in datos and "Título" not in datos:
                        datos["Título"] = datos.pop("Titulo")
                    if "Fecha de publicacion" in datos and "Fecha de Publicación" not in datos:
                        datos["Fecha de Publicación"] = datos.pop("Fecha de publicacion")
                data = database.cargar_biblioteca(path=file_path)
                self.biblioteca = data
                self._actualizar_tabla()
                self.status.showMessage(f"Archivo cargado: {os.path.basename(file_path)}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo.\n\nDetalles: {e}")

    def _on_list_files(self):
        files = database.listar_archivos_diarios()
        if not files:
            QMessageBox.information(self, "Archivos diarios", "No se encontraron archivos diarios en data/.")
            return
        msg = "Archivos diarios:\n" + "\n".join(files)
        QMessageBox.information(self, "Archivos diarios", msg)

    def _on_reload_from_disk(self):
        #Recargar desde disco el archivo activo (ignora lo que haya en memoria) según modo: global o diario.
        #Evira referenciar variables no inicializadas (como fecha_str) en modo global.
        import os, json
        from datetime import datetime

        try:
            #Determinar ruta según modo
            if self.use_global:
                path = os.path.join(os.path.dirname(__file__), "data", "biblioteca_global.json")
                fecha_str = None

            else:
                #Obtener fecha en formato: YYYY-MM-DD de self.selected_date
                fecha_str = None
                #Si selected_date es QDate
                if hasattr(self, "selected_date") and hasattr(self.selected_date, "toString"):
                    try:
                        fecha_str = self.selected_date.toString("yyyy-MM-dd")
                    except Exception:
                        fecha_str = None
                else:
                    #si es datatime.date u otro objeto con isoformat
                    try:
                        fecha_str = (self.selected_date.isoformat()
                                     if hasattr(self.selected_date, "isoformat")
                                     else str(self.selected_date))
                    except Exception:
                        fecha_str = None

                if not fecha_str:
                    QMessageBox.warning(self, "Fecha inválida", "No se ha seleccionado una fecha válida para recargar el archivo.")
                    return
                filename = f"biblioteca_{fecha_str}.json"
                path = os.path.join(os.path.dirname(__file__), "data", filename)
            #comprobar existencia
            if not os.path.exists(path):
                QMessageBox.information(self, "Archivo no encontrado",
                                        f"No existe el archivo en disco:\n{os.path.basename(path)}")
                return
            #Intentar usar database.cargar_biblioteca(path=...) si existe y si la función acepta "path"
            try:
                #llamar con keyword "path" si la función lo soporta
                data = database.cargar_biblioteca(path=path)
            except TypeError:
                #fallback: lectura directa
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            #Normalizar claves antiguas si existen
            for isbn, datos in list(data.items()):
                if isinstance(datos, dict):
                    if "Titulo" in datos and "Título" not in datos:
                        datos["Título"] = datos.pop("Titulo")
                    if "Fecha de publicacion" in datos and "Fecha de Publicación" not in datos:
                        datos["Fecha de Publicación"] = datos.pop("Fecha de publicacion")
                    data[isbn] = datos
            #Actualizar la memoria y UI        
            self.biblioteca = data
            self._actualizar_tabla()
            #Si recargamos un archivo diario, sincronizar date_edit y selected_date
            if fecha_str:
                try:
                    qdate = QDate.fromString(fecha_str, "yyyy-MM-dd")
                    if qdate.isValid():
                        self.date_edit.setDate(qdate)
                        self.selected_date = date(qdate.year(), qdate.month(), qdate.day())
                        self.mode_combo.setCurrentIndex(0)
                        self.use_global = False
                except Exception:
                    #no es critico, si falla, no abortamos
                    pass
            self.status.showMessage(f"Recargado desde disco: {os.path.basename(path)}", 3500)

        except Exception as e:
            #Muestra excepción completa para depuración
            QMessageBox.critical(self, "Error al recargar", f"No se pudo recargar el archivo:\n{e}")

    def _on_search_text_changed(self, txt):
        txt = txt.strip().lower()
        if not txt:
            self._actualizar_tabla()
            return
        filtrado = {isbn: d for isbn, d in self.biblioteca.items()
                    if txt in d.get("Título", "").lower() or txt in d.get("Autor", "").lower()}
        self._actualizar_tabla(datos=filtrado)

    # Quick actions map to main actions

    def _on_quick_edit(self):
        self._on_edit()

    def _on_quick_delete(self):
        self._on_delete()

    #CRUD
    def _validate_form(self):
        isbn = self.isbn_input.text().strip()
        titulo = self.titulo_input.text().strip()
        autor = self.autor_input.text().strip()
        editorial = self.editorial_input.text().strip()
        fecha_pub = self.fecha_input.text().strip()

        # Visual reset
        for w in (self.isbn_input, self.titulo_input, self.autor_input, self.editorial_input, self.fecha_input):
            w.setStyleSheet("")

        if not (isbn and titulo and autor and editorial and fecha_pub):
            QMessageBox.warning(self, "Validación", "Todos los campos son obligatorios.")
            self._mark_empty_fields([("isbn", isbn), ("titulo", titulo), ("autor", autor), ("editorial", editorial), ("fecha", fecha_pub)])
            return None

        if not utils.validar_isbn(isbn):
            QMessageBox.warning(self, "Validación", "ISBN inválido. Use solo números y guiones (5-20 chars).")
            self.isbn_input.setStyleSheet("border: 1px solid #ff6666;")
            return None

        if not utils.validar_fecha_iso(fecha_pub):
            QMessageBox.warning(self, "Validación", "Fecha inválida. Formato esperado: YYYY-MM-DD.")
            self.fecha_input.setStyleSheet("border: 1px solid #ff6666;")
            return None

        return Libro(isbn, titulo, autor, editorial, fecha_pub)

    def _mark_empty_fields(self, field_values):
        # field_values: list of tuples (name, value)
        mapping = {
            "isbn": self.isbn_input,
            "titulo": self.titulo_input,
            "autor": self.autor_input,
            "editorial": self.editorial_input,
            "fecha": self.fecha_input
        }
        for name, val in field_values:
            if not val:
                w = mapping.get(name)
                if w:
                    w.setStyleSheet("border: 1px solid #ff6666;")

    def _on_add(self):
        libro = self._validate_form()
        if libro is None:
            return
        if libro.isbn in self.biblioteca:
            QMessageBox.warning(self, "Duplicado", "El ISBN ya existe en la biblioteca actual.")
            return
        self.biblioteca[libro.isbn] = libro.to_dict()
        try:
            database.guardar_biblioteca(self.biblioteca, fecha=self.selected_date, global_file=self.use_global)
            self.status.showMessage("Libro guardado.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
        self._actualizar_tabla()
        self._on_clear()

        data = libro.to_dict()
        if hasattr(self, "current_pdf_path"):
            data["Archivo PDF"] = self.current_pdf_path
        if hasattr(self, "current_pdf_preview"):
            data["Portada"] = self.current_pdf_preview

        self.biblioteca[libro.isbn] = data

    def _on_edit(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Editar", "Selecciona la fila del libro a editar.")
            return
        row = selected[0].row()
        isbn_original = self.table.item(row, 0).text()
        libro = self._validate_form()
        if libro is None:
            return
        # check duplicate isbn if changed
        if libro.isbn != isbn_original and libro.isbn in self.biblioteca:
            QMessageBox.warning(self, "Validación", "El nuevo ISBN ya existe.")
            return
        # replace key if isbn changed
        if libro.isbn != isbn_original:
            self.biblioteca.pop(isbn_original, None)
        self.biblioteca[libro.isbn] = libro.to_dict()
        try:
            # fecha_guardado -> Agregado para asegurar el guardado en data como Biblioteca_YYYY_MM_DD en JSON
            fecha_guardado = self.selected_date.toString("yyyy-MM-dd") if isinstance(self.selected_date, QDate) else self.selected_date
            database.guardar_biblioteca(self.biblioteca, fecha=self.selected_date, global_file=self.use_global)
            self.status.showMessage("Libro editado y guardado.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
        self._actualizar_tabla()
        self._on_clear()

    def _on_delete(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Eliminar", "Selecciona la fila a eliminar.")
            return
        row = selected[0].row()
        isbn = self.table.item(row, 0).text()
        if QMessageBox.question(self, "Confirmar eliminación", f"Eliminar libro con ISBN {isbn}?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.biblioteca.pop(isbn, None)
            try:
                database.guardar_biblioteca(self.biblioteca, fecha=self.selected_date, global_file=self.use_global)
                self.status.showMessage("Libro eliminado y archivo actualizado.", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar después de eliminar: {e}")
            self._actualizar_tabla()
            self._on_clear()

        if not ux.confirmar(self, "Confirmar eliminación", f"Seguro que desea eliminar libro con ISBN {isbn}?"):
            return

    def _on_clear(self):
        self.isbn_input.clear()
        self.titulo_input.clear()
        self.autor_input.clear()
        self.editorial_input.clear()
        self.fecha_input.clear()
        for w in (self.isbn_input, self.titulo_input, self.autor_input, self.editorial_input, self.fecha_input):
            w.setStyleSheet("")
        self.table.clearSelection()
        self.status.showMessage("Campos limpiados.", 1800)

    #Table interactions
    def _on_table_double_clicked(self, row, col):
        # cargar datos al formulario para editar
        isbn = self.table.item(row, 0).text()
        datos = self.biblioteca.get(isbn, {})
        self.isbn_input.setText(isbn)
        self.titulo_input.setText(datos.get("Título", ""))
        self.autor_input.setText(datos.get("Autor", ""))
        self.editorial_input.setText(datos.get("Editorial", ""))
        self.fecha_input.setText(datos.get("Fecha de Publicación", ""))

    def _on_table_selection_changed(self):
        selected = self.table.selectionModel().selectedRows()
        if selected:
            self.status.showMessage("Fila seleccionada.", 800)
        else:
            self.status.clearMessage()

    #Persistence helpers
    def _autoguardar(self):
        try:
            if not getattr(self, "biblioteca", None):
                return
            
            database.guardar_biblioteca(self.biblioteca, fecha=self.selected_date, global_file=self.use_global)
            self.status.showMessage("Auto-guardado: cambios guardados.", 2000)

            if hasattr(database, "DB_PATH") and database.DB_PATH and os.path.exists(database.DB_PATH):
                backup_path = ux.crear_backup(database.DB_PATH)
                if backup_path:
                    print(f"🗂️ Backup creado correctamente: {backup_path}")
        except Exception as e:
            self.status.showMessage(f"Error en auto-guardado: {e}", 4000)
            print(f"Error en auto-guardado: {e}")

    def _on_autosave_toggled(self, checked):
        if checked:
            interval = self.autosave_interval.value()
            self.autosave_timer.start(interval * 1000)
            self.status.showMessage(f"Auto-save activado ({interval}s).", 2500)
        else:
            self.autosave_timer.stop()
            self.status.showMessage("Auto-save desactivado.", 2500)

    #Table rendering
    def _actualizar_tabla(self, datos=None):
        if datos is None:
            datos = self.biblioteca
        self.table.setRowCount(0)
        for row_idx, (isbn, d) in enumerate(datos.items()):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(isbn))
            self.table.setItem(row_idx, 1, QTableWidgetItem(d.get("Título", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(d.get("Autor", "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(d.get("Editorial", "")))
            self.table.setItem(row_idx, 4, QTableWidgetItem(d.get("Fecha de Publicación", "")))

        # Ajustes de fuente y alineación para legibilidad
        font = QFont("Segoe UI", 10)
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item:
                    item.setFont(font)
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

    def _on_btn_importar_pdf(self):
        try:
            if not hasattr(pdf_reader, "importar_pdf"):
                QMessageBox.critical(self, "Error", "La función pdf_reader.importar_pdf no existe o no se encuentra.")
                return
            pdf_reader.importar_pdf(self)
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error al importar el PDF", f"Ocurrió un error en:\n{e}")

    def _on_btn_procesar_lote(self):
        try:
            if not hasattr(pdf_reader, "procesar_lote"):
                QMessageBox.critical(self, "Error", "La función pdf_reader.procesar_lote no existe o no se encuentra.")
                return
            pdf_reader.procesar_lote(self)
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error al procesar lote", f"Ocurrio un error en:\n{e}")

    def _on_table_selection(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.lblPreview.clear()
            self.lblPreview.setText("Sin vista previa disponible.")
            return

        row = selected_rows[0].row()
        isbn = self.table.item(row, 0).text().strip()

        import pdf_reader
        pdf_reader.mostrar_portada(self, isbn)

    def _on_table_double_click(self, item):
        row = item.row()
        isbn = self.table.item(row, 0).text().strip()

        import pdf_reader
        pdf_reader.abrir_pdf_externo(self, isbn)


    def _setup_context_menu(self):
        """
        Habilita el menú contextual en la tabla principal.
        """

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_context_menu_request)

    def _on_context_menu_request(self, position):
        """Genera y muestra el menú contextual al hacer clic derecho en la tabla."""
        index = self.table.indexAt(position)
        if not index.isValid():
            return

        row = index.row()
        isbn = self.table.item(row, 0).text().strip()
        datos = self.biblioteca.get(isbn, {})

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e1e;
                border: 1px solid #333;
                color: #ddd;
            }
            QMenu::item {
                padding: 6px 20px;
            }
            QMenu::item:selected {
                background-color: #007acc;
                color: #fff;
            }
        """)

        abrir_pdf_action = QAction("📖  Abrir PDF", self)
        ver_portada_action = QAction("🖼️  Ver portada", self)
        abrir_carpeta_action = QAction("📂  Abrir carpeta del PDF", self)
        eliminar_action = QAction("🗑️  Eliminar registro", self)

        abrir_pdf_action.triggered.connect(lambda: pdf_reader.abrir_pdf_externo(self, isbn))
        ver_portada_action.triggered.connect(lambda: self._mostrar_portada_ventana(isbn))
        abrir_carpeta_action.triggered.connect(lambda: self._abrir_carpeta_pdf(isbn))
        eliminar_action.triggered.connect(lambda: self._eliminar_registro(isbn))

        menu.addAction(abrir_pdf_action)
        menu.addAction(ver_portada_action)
        menu.addAction(abrir_carpeta_action)
        menu.addSeparator()
        menu.addAction(eliminar_action)

        menu.exec_(self.table.viewport().mapToGlobal(position))


    def _mostrar_portada_ventana(self, isbn):
        """Abre la portada en una ventana emergente más grande."""
        datos = self.biblioteca.get(isbn, {})
        portada = datos.get("Portada", "")

        if not portada or not os.path.exists(portada):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Sin portada", "No hay portada disponible para este libro.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Vista previa – {datos.get('Título', 'Libro sin título')}")
        dlg.resize(500, 700)

        layout = QVBoxLayout(dlg)
        lbl = QLabel(dlg)
        lbl.setAlignment(Qt.AlignCenter)
        image = QImage(portada)
        pixmap = QPixmap.fromImage(image).scaledToWidth(450, Qt.SmoothTransformation)
        lbl.setPixmap(pixmap)

        layout.addWidget(lbl)
        dlg.exec_()


    def _abrir_carpeta_pdf(self, isbn):
        """Abre la carpeta donde está el PDF asociado."""
        datos = self.biblioteca.get(isbn, {})
        pdf_path = datos.get("Archivo PDF", "")
        if not pdf_path or not os.path.exists(pdf_path):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Archivo no encontrado", "No se encontró el PDF asociado.")
            return

        folder = os.path.dirname(pdf_path)
        if os.name == "nt":  # Windows
            os.startfile(folder)
        elif os.name == "posix":
            import subprocess
            subprocess.Popen(["xdg-open", folder])
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", folder])


    def _eliminar_registro(self, isbn):
        """Elimina un registro del listado y del diccionario."""
        from PySide6.QtWidgets import QMessageBox
        respuesta = QMessageBox.question(
            self,
            "Eliminar libro",
            f"¿Deseas eliminar el libro con ISBN {isbn}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            if isbn in self.biblioteca:
                del self.biblioteca[isbn]
                self._actualizar_tabla()
                self.status.showMessage("Registro eliminado.", 3000)

    def _asignar_portada_manual(self):
        """Permite al usuario seleccionar manualmente una imagen como portada para el libro seleccionado."""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Asignar portada", "Selecciona la fila del libro para asignar una portada.")
            return

        row = selected[0].row()
        isbn = self.table.item(row, 0).text().strip()

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen de portada",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        if not file_path:
            return

        try:
            cache_dir = os.path.join(os.getcwd(), "cache")
            os.makedirs(cache_dir, exist_ok = True)
            
            import uuid
            dest_path = os.path.join(cache_dir, f"{isbn}_custom_{uuid.uuid4().hex[:6]}.jpg")
            shutil.copyfile(file_path, dest_path)

            self.biblioteca[isbn]["Portada"] = dest_path
            database.guardar_biblioteca(self.biblioteca, fecha = self.selected_date, global_file = self.use_global)

            self._actualizar_tabla()
            self.lblPreview.setPixmap(QPixmap(dest_path).scaledToWidth(220, Qt.SmoothTransformation))

            QMessageBox.information(self, "Portada asignada", "La portada se asignó correctamente al libro seleccionado.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo asignar la portada:\n{e}")

    #Utility: theme fallback (En caso de no leer styles_default.qss, no arruinar la estética de la UI en la app principal)
    def _default_dark_qss(self):
        # Paleta inspirada en VS Code (oscuro, acentos cyan)
        return """
        QWidget { background: #0f1720; color: #cbd5e1; }
        #sidebar { background: #0b1220; }
        QLineEdit, QDateEdit, QComboBox { background: #111827; color: #e6eef6; border: 1px solid #27323d; border-radius: 4px; padding: 6px;}
        QTableWidget { background: #0b1220; color: #e6eef6; selection-background-color: #075985; selection-color: #e6eef6; }
        QHeaderView::section { background: #071221; color: #9fb4c8; padding: 6px; border: none; }
        QPushButton { background: #0b63a9; color: white; border-radius: 6px; padding: 6px 10px;}
        QPushButton:hover { background: #0f7acb; }
        QPushButton:disabled { background: #334155; color: #94a3b8; }
        QCheckBox { color: #9fb4c8; }
        QStatusBar { background: #071221; color: #9fb4c8; border: none; }
        QLabel { color: #cbd5e1; }
        QComboBox { padding: 6px; }
        QSpinBox { background: #0f1720; color: #cbd5e1; border: 1px solid #27323d; border-radius: 4px; padding: 4px;}
        """