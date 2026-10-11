@echo off
echo =======================================================
echo   CHAY TEST SUITE TOAN DIEN BANG .VENV PYTHON
echo =======================================================

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [CANH BAO] Chua tim thay .venv! Vui long chay setup_venv.bat truoc.
    pause
    exit /b 1
)

echo [*] Dang chay 53 test cases qua pytest trong .venv...
echo.
call .\.venv\Scripts\python.exe -m pytest tests/ -v

echo.
pause
