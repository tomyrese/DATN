@echo off
echo =======================================================
echo   KHOI DONG PI ROBOT BACKEND BANG MOI TRUONG AO (.VENV)
echo =======================================================

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [CANH BAO] Chua tim thay .venv! Dang tu dong khoi tao...
    call setup_venv.bat
)

echo [*] Dang khoi dong Backend Robot Server qua .venv...
echo [*] Web Dashboard: http://localhost:8765
echo.
call .\.venv\Scripts\python.exe src\main.py

pause
