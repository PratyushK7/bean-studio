@echo off
rem Bean Studio: double-click to start. Sets itself up the first time, and again whenever requirements.txt changes
rem (for example after a git pull adds a package).
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Setting up Bean Studio for the first time...
  python -m venv .venv || (echo Python 3.10+ is needed: https://www.python.org/downloads/ & pause & exit /b 1)
)
set REQHASH=
for /f %%h in ('certutil -hashfile requirements.txt MD5 ^| findstr /v ":"') do if not defined REQHASH set REQHASH=%%h
set OLDHASH=
if exist ".venv\req.hash" set /p OLDHASH=<".venv\req.hash"
if not "%REQHASH%"=="%OLDHASH%" (
  echo Installing packages...
  ".venv\Scripts\python.exe" -m pip install -q --upgrade pip
  ".venv\Scripts\python.exe" -m pip install -q -r requirements.txt || (echo Install failed. & pause & exit /b 1)
  >".venv\req.hash" echo %REQHASH%
)
".venv\Scripts\python.exe" app\server.py
if errorlevel 1 pause
