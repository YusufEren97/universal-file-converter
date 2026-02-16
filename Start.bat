@echo off
chcp 65001 >nul 2>&1
title Universal Converter v3.0
color 0B
cd /d "%~dp0"

:MENU
cls
echo.
echo   ██████╗ ██████╗ ███╗   ██╗██╗   ██╗███████╗██████╗ ████████╗███████╗██████╗
echo  ██╔════╝██╔═══██╗████╗  ██║██║   ██║██╔════╝██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
echo  ██║     ██║   ██║██╔██╗ ██║██║   ██║█████╗  ██████╔╝   ██║   █████╗  ██████╔╝
echo  ██║     ██║   ██║██║╚██╗██║╚██╗ ██╔╝██╔══╝  ██╔══██╗   ██║   ██╔══╝  ██╔══██╗
echo  ╚██████╗╚██████╔╝██║ ╚████║ ╚████╔╝ ███████╗██║  ██║   ██║   ███████╗██║  ██║
echo   ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
echo.
echo   Universal File Converter v3.0
echo   ═══════════════════════════════════════
echo.
echo   [1] Start Server
echo   [2] Install / Update Dependencies
echo   [3] Clean Temp Files
echo   [4] Exit
echo.
set /p choice="   Your choice (1-4): "

if "%choice%"=="1" goto START
if "%choice%"=="2" goto INSTALL
if "%choice%"=="3" goto CLEAN
if "%choice%"=="4" goto EXIT

echo   Invalid choice!
timeout /t 2 >nul
goto MENU

:INSTALL
cls
echo.
echo   [*] Installing dependencies...
echo   [*] Make sure you have internet connection.
echo.
py -3.12 -m pip install -r requirements.txt
if %errorlevel% equ 0 (
    echo OK > .installed
    echo.
    echo   [+] Installation complete!
) else (
    echo.
    echo   [!] Some dependencies failed to install.
)
echo.
pause
goto MENU

:START
cls
echo.
echo   [*] Starting Universal Converter...
echo.

:: Python 3.12 Check
echo   [CHECK] Checking Python 3.12...
py -3.12 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERROR] Python 3.12 not found!
    echo   Download Python 3.12 from python.org
    pause
    goto MENU
)
echo   [OK] Python 3.12 found

:: Check requirements
if not exist ".installed" (
    echo   [INFO] Installing dependencies...
    py -3.12 -m pip install -r requirements.txt
    if %errorlevel% equ 0 (
        echo OK > .installed
        echo   [OK] Dependencies installed
    ) else (
        echo   [!] Some dependencies failed to install
    )
) else (
    echo   [OK] Dependencies ready
)

echo.
echo   [INFO] Starting server on port 1453...
echo   [INFO] Browser will open automatically
echo.
echo   Press Ctrl+C to stop
echo   ═══════════════════════════════════════
echo.

py -3.12 -m uvicorn app.main:app --port 1453

if %errorlevel% neq 0 (
    echo.
    echo   [ERROR] Server failed to start!
    pause
)
goto MENU

:CLEAN
cls
echo.
echo   [*] Cleaning temporary files...
echo.

if exist "temp_uploads" rd /s /q "temp_uploads"
if exist "converted_files" rd /s /q "converted_files"
if exist "__pycache__" rd /s /q "__pycache__"
if exist "app\__pycache__" rd /s /q "app\__pycache__"
if exist "app\converters\__pycache__" rd /s /q "app\converters\__pycache__"

echo   [+] All temporary files cleaned!
echo.
timeout /t 2 >nul
goto MENU

:EXIT
cls
echo.
echo   Goodbye!
echo.
timeout /t 1 >nul
exit
