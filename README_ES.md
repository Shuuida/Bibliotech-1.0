# 📚 Bibliotech — Asistente Bibliotecario Virtual

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python\&logoColor=white)
![PySide6](https://img.shields.io/badge/UI-PySide6-41CD52?logo=qt\&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

---

**Bibliotech** es una aplicación de escritorio desarrollada en **Python + PySide6** que permite registrar, editar, eliminar y gestionar libros de manera eficiente, moderna y segura incluyendo la gestión y lectura de archivos PDF y procesado por lotes.
Cuenta con **interfaz gráfica tipo Visual Studio Code**, guardado automático, exportación a CSV, respaldo de datos y soporte para archivos diarios o globales.

(In the initial phase! May receive updates)

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