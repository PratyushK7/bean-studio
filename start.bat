@echo off
rem Bean Studio: double-click to start. First run sets up .venv (about a minute).
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Setting up Bean Studio for the first time...
  python -m venv .venv || (echo Python 3.10+ is needed: https://www.python.org/downloads/ & pause & exit /b 1)
  ".venv\Scripts\python.exe" -m pip install -q --upgrade pip
  ".venv\Scripts\python.exe" -m pip install -q -r requirements.txt || (echo Install failed. & pause & exit /b 1)
)
".venv\Scripts\python.exe" app\server.py
pause
