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