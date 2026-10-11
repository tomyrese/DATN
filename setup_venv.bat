@echo off
echo =======================================================
echo   KHOI TAO MOI TRUONG AO PYTHON (.VENV) CHO PI ROBOT
echo =======================================================

cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Khong tim thay Python tren he thong! Vui long cai dat Python 3.10 tro len.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [*] Dang tao moi truong ao .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Tao moi truong ao that bai!
        pause
        exit /b 1
    )
    echo [OK] Da tao thanh cong thu muc .venv!
) else (
    echo [*] Moi truong ao .venv da ton tai.
)

echo [*] Dang cap nhat pip va cai dat thu vien vao .venv (khong dung pip global)...
call .\.venv\Scripts\python.exe -m pip install --upgrade pip
call .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Cai dat thu vien vao .venv that bai!
    pause
    exit /b 1
)

if not exist ".env" (
    echo [*] Tao file cau hinh .env tu .env.example...
    copy .env.example .env >nul
)

echo [*] Khoi tao va cap nhat Co so du lieu SQLite v2...
call .\.venv\Scripts\python.exe -m src.database.migrator
call .\.venv\Scripts\python.exe -m src.database.seed

echo.
echo =======================================================
echo   HOAN TAT CAI DAT VAO .VENV!
echo   De kich hoat moi truong ao trong PowerShell / CMD:
echo     PowerShell:  .\.venv\Scripts\Activate.ps1
echo     CMD:         call .\.venv\Scripts\activate.bat
echo   Hoac chay truc tiep: run_backend.bat
echo =======================================================
pause
