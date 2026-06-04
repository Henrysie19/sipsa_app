@echo off
title Configurando Entorno Limpio...
echo ===================================================
echo   CONFIGURANDO EL APLICATIVO POR PRIMERA VEZ
echo ===================================================
echo.

cd /d "%~dp0"

echo 1. Descargando gestor de paquetes (pip) de forma segura...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'"

echo.
echo 2. Registrando e instalando pip en el Python Portable...
.\python_embed\python.exe get-pip.py --no-warn-script-location
del get-pip.py

echo.
echo 3. Instalando librerias requeridas (Streamlit, Pandas, etc.)...
echo    (Esto puede tardar un par de minutos, por favor espera...)
.\python_embed\python.exe -m pip install -r requirements.txt --no-warn-script-location

echo.
echo ===================================================
echo   ¡CONFIGURACION COMPLETA! Ya puedes cerrar.
echo ===================================================
pause
