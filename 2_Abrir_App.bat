@echo off
title Iniciando Automatizador...
cd /d "%~dp0"

echo Iniciando el servidor de reportes locales...
start http://localhost:8501

.\python_embed\Scripts\streamlit.exe run app.py --server.port=8501 --server.headless=true
