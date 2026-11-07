@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
  if errorlevel 1 exit /b 1
  .venv\Scripts\python.exe -m pip install -e ".[studio]"
  if errorlevel 1 exit /b 1
)
echo Open http://127.0.0.1:8765 in your browser. Press Ctrl+C to stop.
.venv\Scripts\python.exe -m medillustrate studio %*
