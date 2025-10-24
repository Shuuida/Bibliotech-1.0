@echo off
title Generador de ejecutable Bibliotech
echo ===========================================
echo      🧩 BIBLIOTECH - BUILD AUTOMATION
echo ===========================================

:: 1️⃣ Comprobación de Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python no esta en el PATH. Instalalo o agrega Python al PATH.
    pause
    exit /b
)

:: 2️⃣ Limpieza de builds anteriores
echo 🧹 Limpiando carpetas anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Bibliotech.spec del /f /q Bibliotech.spec

:: 3️⃣ Actualización de pip y dependencias necesarias
echo 🚀 Instalando / actualizando dependencias...
python -m pip install --upgrade pip
python -m pip install pyinstaller==6.16.0
python -m pip install PySide6==6.10.0

:: 4️⃣ Creación del ejecutable
echo ⚙️ Compilando ejecutable con PyInstaller...
python -m PyInstaller --noconsole --onefile --name "Bibliotech" ^
--collect-all PySide6 ^
--add-data "assets;assets" ^
--add-data "data;data" ^
--add-data "cache;cache" ^
--add-data "ui.py;." ^
--add-data "ux_helpers.py;." ^
--add-data "pdf_reader.py;." ^
--add-data "database.py;." ^
--add-data "utils.py;." ^
--add-data "models.py;." ^
main.py

:: 5️⃣ Finalización
if exist dist\Bibliotech.exe (
    echo ✅ Compilacion completada con éxito.
    echo -------------------------------------------
    echo 📦 Ejecutable generado en: dist\Bibliotech.exe
) else (
    echo ❌ Error durante la compilacion. Revisa la salida anterior.
)

pause
exit /b