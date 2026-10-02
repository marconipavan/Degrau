@echo off
rem Degrau: linha de comando (Windows). Comandos: degrau --help
set "PYTHONPATH=%~dp0."
"%~dp0.venv\Scripts\python.exe" -m motor %*
