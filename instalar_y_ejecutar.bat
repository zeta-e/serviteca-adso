@echo off
title Serviteca ADSO - Instalacion
color 0A
echo.
echo  ============================================
echo   SERVITECA ADSO - Instalador
echo  ============================================
echo.
echo  [1/3] Verificando Python...
python --version
if errorlevel 1 (
    echo  ERROR: Python no encontrado. Instale Python 3.10+
    pause
    exit /b 1
)

echo.
echo  [2/3] Instalando dependencias...
python -m pip install customtkinter mysql-connector-python Pillow
if errorlevel 1 (
    echo  ERROR: Fallo la instalacion de dependencias.
    pause
    exit /b 1
)

echo.
echo  [3/3] Lanzando Serviteca ADSO...
echo.
echo  RECUERDE: Asegurese de que MySQL este en ejecucion
echo  y haya importado database/serviteca_db.sql
echo.
cd /d "%~dp0"
python main.py

pause
