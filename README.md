# 📚 Bibliotech — Virtual Library Assistant

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python\&logoColor=white)
![PySide6](https://img.shields.io/badge/UI-PySide6-41CD52?logo=qt\&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

---

**Bibliotech** is a desktop application developed in **Python + PySide6** that allows users to register, edit, delete, and manage books efficiently, securely, and with a modern touch, including PDF file management and reading and batch processing.
It features a **Visual Studio Code–style dark interface**, automatic saving, CSV export, data backups, and support for both daily and global data modes.

*(Currently in its initial release — future updates are expected.)*

---

## 🧩 Main Features

✅ Modern dark interface inspired by VS Code
✅ Full book registration (ISBN, Title, Author, Publisher, Publication Date)
✅ Automatic duplicate detection
✅ Daily or global data saving (depending on selected mode)
✅ Automatic backups on every save
✅ Real-time search by title or author
✅ CSV export functionality
✅ PDF file and batch import support
✅ Storage of PDFs and their metadata
✅ Ability to open PDFs directly from the software by using double-clicking (requires third-party apps)
✅ Cover preview (thumbnails) for uploaded PDFs
✅ Data validation (ISBN and dates)
✅ Configurable auto-save intervals (in seconds)
✅ Automatic display adaptation for different resolutions. From standard displays to high-resolution (HiDPI) displays.
✅ Fully **offline and cross-platform**

---

## 🖥️ Interface Preview

```text
assets/screenshot.png
```

---

## ⚙️ Installation and Execution

### 🔸 1. Clone the Repository

```bash
git clone https://github.com/YourUser/Bibliotech.git
cd Bibliotech
```

### 🔸 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On Linux/Mac
```

### 🔸 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> If you don’t have a `requirements.txt` file, you can install dependencies manually:
>
> ```bash
> pip install PySide6
> pip install PyMuPDF
> ```

### 🔸 4. Run the Application

```bash
python main.py
```

---

## 💾 Data Files

* Data is stored in **JSON format** inside the `data/` directory.
* Files are automatically created based on the **selected mode**:

  * 📅 **Daily Mode:** `biblioteca_2025-10-19.json`
  * 🌐 **Global Mode:** `biblioteca_global.json`
* Automatic **backups** are created in `data/backups/`.

---

## 📤 Exporting to CSV

You can export your library inventory to a CSV file from the interface (“Export CSV” button) or from the side menu if enabled.

The file will include the following columns:

```
ISBN, Title, Author, Publisher, Publication Date
```

---

## Batch Processing

You can import and process folders containing different PDF files into the system for management and reading. Upon upload, the system will read the file's metadata and use it as ISBN, Title, Author, Publisher, and Date created or published. These metadata can also be edited at the user's convenience.

---

## 🧠 Validations

* **ISBN** must follow a valid format (`978-XXXXXXX` or similar).
* **Dates** must follow the format `YYYY-MM-DD`.
* The system shows visual alerts when a field is incorrect or incomplete.

---

## 🌙 Visual Theme (VS Code Style)

The application uses a dark theme inspired by **Visual Studio Code**, defined in `assets/style.qss`.
You can edit colors, typography, or button styles in that file to customize the appearance.

---

# Customizable Cover Viewer

The program has its own cover viewer. When uploading PDF files, a preview of the cover will be created using the cached JPG image of the first page of the PDF as a reference. This preview can also be customized with the user's preferred image (preferably in the same format as the previews created by the program).

---

## 🧩 Build Automation (Windows)

Bibliotech includes an automated build script to easily create a standalone executable (`.exe`) version of the program.

### 🧱 How to use it

1. Make sure you have **Python 3.13** (or higher) installed and added to your system PATH.
2. Double-click the `build_exe.bat` file located in the project root.
3. Wait for the process to complete.

Once finished, your compiled executable will be located at:

dist/Bibliotech.exe

### ⚙️ What the script does

The build script automatically:
- Cleans up previous build directories (`build/`, `dist/`, `.spec`)
- Installs and updates required dependencies:
  - **PyInstaller 6.16.0**
  - **PySide6 6.10.0**
- Packages all necessary modules and assets, including:
  - `assets/`, `data/`, `cache/`
  - `ui.py`, `ux_helpers.py`, `pdf_reader.py`, `database.py`, `utils.py`, `models.py`
- Generates the final executable ready to run on any Windows machine.

> 💡 This script makes it simple for contributors and users to rebuild the project or test the standalone version without manual setup.

## 🧑‍💻 Author

**Developed by:** Michego Takoro
**Year:** 2025
**License:** MIT License (Free use with attribution)

---

## 📜 License

This project is distributed under the **MIT License**, allowing free use, modification, and redistribution as long as proper credit is maintained.

```
MIT License © 2025 Michego Takoro
```





---



# 📚 Bibliotech — Asistente Bibliotecario Virtual

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python\&logoColor=white)
![PySide6](https://img.shields.io/badge/UI-PySide6-41CD52?logo=qt\&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

---

**Bibliotech** es una aplicación de escritorio desarrollada en **Python + PySide6** que permite registrar, editar, eliminar y gestionar libros de manera eficiente, moderna y segura incluyendo la gestión y lectura de archivos PDF y procesado por lotes.
Cuenta con **interfaz gráfica tipo Visual Studio Code**, guardado automático, exportación a CSV, respaldo de datos y soporte para archivos diarios o globales.

---

## 🧩 Características principales

✅ Interfaz moderna y oscura inspirada en VS Code
✅ Registro completo de libros (ISBN, título, autor, editorial, fecha de publicación)
✅ Detección automática de duplicados
✅ Guardado diario o global (según modo elegido)
✅ Backup automático en cada guardado
✅ Búsqueda en tiempo real por título o autor
✅ Exportación a CSV
✅ Compatible con importación de archivos PDFs y lotes
✅ Almacenamiento de PDFs y metadatos del archivo
✅ Puede abrir los PDF dentro del software al darle doble click (Necesario aplicaciones de terceros)
✅ Visualizador de portadas (Imágenes) para los PDF subidos
✅ Validación de datos (ISBN y fechas)
✅ Auto-guardado configurable (por segundos)
✅ Adaptación de pantalla automática para diferentes tipos de resolución. Desde pantallas comunes a de altas resoluciones (HiDPI)
✅ Totalmente **offline y multiplataforma**

---

## 🖥️ Captura de interfaz

```text
assets/screenshot.png
```

---

## ⚙️ Instalación y ejecución

### 🔸 1. Clonar el repositorio

```bash
git clone https://github.com/TuUsuario/Bibliotech.git
cd Bibliotech
```

### 🔸 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
venv\Scripts\activate   # En Windows
source venv/bin/activate  # En Linux/Mac
```

### 🔸 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

> Si no tienes el archivo `requirements.txt`, puedes instalar manualmente:
>
> ```bash
> pip install PySide6
> pip install PyMuPDF
> ```

### 🔸 4. Ejecutar el programa

```bash
python main.py
```

---

## 💾 Archivos de datos

* Los datos se almacenan en formato **JSON** dentro de la carpeta `data/`.
* Se crean automáticamente según el **modo seleccionado**:

  * 📅 **Modo diario:** `biblioteca_2025-10-19.json`
  * 🌐 **Modo global:** `biblioteca_global.json`
* Se realizan **backups automáticos** en `data/backups/`.

---

## 📤 Exportar CSV

Puedes exportar tu inventario a un archivo CSV desde la interfaz (botón “Exportar CSV”), o desde el menú lateral si fue habilitado.

El archivo incluirá las columnas:

```
ISBN, Título, Autor, Editorial, Fecha de publicación
```

---

## Procesamiento por lotes

Puedes importar y procesar al sistema carpetas con distintos archivos PDF para gestion y lectura. Al subirlo el sistema leera los metadatos del archivo y los usara como ISBN, Título, Autor, Editorial y Fecha en que fue creado o publicado, siendo editable de igual manera a conveniencia del usuario.

---

## 🧠 Validaciones

* **ISBN** debe tener formato válido (`978-XXXXXXX` o similar).
* **Fechas** deben seguir el formato `YYYY-MM-DD`.
* El sistema muestra alertas visuales si un campo es incorrecto o incompleto.

---

## 🌙 Tema Visual (VS Code Style)

El programa utiliza un tema oscuro inspirado en **Visual Studio Code**, definido en `assets/style.qss`.
Puedes modificar los colores, tipografía o botones desde ese archivo para personalizar la apariencia.

---

# Visualizador de Portadas personalizable

El programa cuenta con un visor de portadas propio, en donde al subir los archivos PDF, se creara una preview de la portada usando de referencia la primera pagina del PDF en JPG guardada en cache, que puede ser igualmente personalizado con la imagen de preferencia del usuario (De preferencia, en el mismo formato que en las preview creadas por el programa).

---

## 🧩 Automatización de compilación (Windows)

Bibliotech incluye un script de construcción automatizado que permite crear fácilmente una versión ejecutable (`.exe`) del programa.

### 🧱 Cómo usarlo

1. Asegúrate de tener **Python 3.13** (o superior) instalado y agregado al PATH del sistema.
2. Haz doble clic sobre el archivo `build_exe.bat` ubicado en la raíz del proyecto.
3. Espera a que el proceso termine.

Cuando finalice, el ejecutable compilado estará disponible en:

dist/Bibliotech.exe

### ⚙️ Qué hace el script

El script de compilación se encarga automáticamente de:
- Limpiar las carpetas de compilaciones previas (`build/`, `dist/`, `.spec`)
- Instalar y actualizar las dependencias necesarias:
  - **PyInstaller 6.16.0**
  - **PySide6 6.10.0**
- Incluir todos los módulos y recursos requeridos:
  - `assets/`, `data/`, `cache/`
  - `ui.py`, `ux_helpers.py`, `pdf_reader.py`, `database.py`, `utils.py`, `models.py`
- Generar el ejecutable final listo para funcionar en cualquier sistema Windows.

> 💡 Este script facilita que cualquier colaborador o usuario pueda reconstruir el proyecto o probar su versión independiente sin configuraciones manuales.

## 🧑‍💻 Autor

**Desarrollado por:** Michego Takoro
**Año:** 2025
**Licencia:** MIT License (uso libre con atribución)

---

## 📜 Licencia

Este proyecto se distribuye bajo la **MIT License**, lo que permite su uso, modificación y distribución libre siempre que se mantengan los créditos originales.

```
MIT License © 2025 Michego Takoro
```

---

