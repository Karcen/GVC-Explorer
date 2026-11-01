@echo off
setlocal
cd /d "%~dp0"
if exist .venv\.gvc_studio_020 goto launch
py -3 -m venv .venv || goto failed
.venv\Scripts\python.exe -m pip install -e . || goto failed
type nul >.venv\.gvc_studio_020
:launch
.venv\Scripts\python.exe desktop.py || goto failed
exit /b 0
:failed
pause
exit /b 1
