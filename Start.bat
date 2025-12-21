@echo off
title Universal Converter
cd /d "%~dp0"
chcp 65001 >nul

:MENU
cls
echo ===================================================
echo   Universal Converter
echo ===================================================
echo.
echo   [1] Start Server
echo   [2] Clean Temp Files
echo   [3] Exit
echo.
echo ===================================================
set /p choice="Your choice (1/2/3): "

if "%choice%"=="1" goto START
if "%choice%"=="2" goto CLEAN
if "%choice%"=="3" exit
goto MENU

:START
cls
echo ===================================================
echo   Starting Server
echo ===================================================
echo.

:: Python Check
echo [CHECK] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Download Python 3.9+ from python.org
    pause
    goto MENU
)
echo [OK] Python found

:: Check requirements
if not exist ".installed" (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% equ 0 (
        echo OK > .installed
        echo [OK] Dependencies installed
    ) else (
        echo [WARNING] Some dependencies failed to install
    )
) else (
    echo [OK] Dependencies ready
)

echo.
echo [INFO] Starting server on port 9999...
echo [INFO] Browser will open automatically
echo.
echo Press Ctrl+C to stop
echo ===================================================
echo.

python -m uvicorn app.main:app --port 9999

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server failed to start!
    pause
)
goto MENU

:CLEAN
cls
echo ===================================================
echo   Cleanup
echo ===================================================
echo.

echo Cleaning temporary files...

if exist "temp_uploads" rd /s /q "temp_uploads"
if exist "converted_files" rd /s /q "converted_files"
if exist "__pycache__" rd /s /q "__pycache__"
if exist "app\__pycache__" rd /s /q "app\__pycache__"
if exist "app\converters\__pycache__" rd /s /q "app\converters\__pycache__"

echo.
echo [OK] All temporary files cleaned
echo.
pause
goto MENU
