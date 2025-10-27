@echo off
REM MOV to MP4 Converter - Automated Start Script for Windows
REM This script sets up virtual environment and runs the converter

setlocal enabledelayedexpansion

echo === MOV to MP4 Converter - Setup ^& Run ===
echo.

REM Configuration
set VENV_DIR=venv
set PYTHON_CMD=python

REM Check if Python is installed
where %PYTHON_CMD% >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%

REM Check if FFmpeg is installed
where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] FFmpeg is not installed
    echo Please install FFmpeg from https://ffmpeg.org/download.html
    echo.
    set /p "CONTINUE=Continue anyway? (y/N): "
    if /i not "!CONTINUE!"=="y" exit /b 1
) else (
    for /f "tokens=3" %%i in ('ffmpeg -version 2^>^&1 ^| findstr /r "^ffmpeg"') do (
        echo [OK] Found FFmpeg %%i
        goto :ffmpeg_found
    )
    :ffmpeg_found
)

REM Create virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo.
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv %VENV_DIR%
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip -q

REM Install requirements
echo.
echo Installing dependencies...
if exist requirements.txt (
    pip install -r requirements.txt -q
    echo [OK] Dependencies installed
) else (
    echo Error: requirements.txt not found
    pause
    exit /b 1
)

REM Install the package in development mode
echo.
echo Installing mov2mp4 package...
pip install -e . -q
echo [OK] Package installed

echo.
echo === Setup Complete ===
echo.

REM Check if arguments were passed
if "%~1"=="" (
    REM No arguments - show help
    echo Usage: start.bat [OPTIONS] INPUT_FILES...
    echo.
    echo Examples:
    echo   start.bat video.mov
    echo   start.bat video.mov -q high -o .\output\
    echo   start.bat *.mov -p 4
    echo   start.bat C:\Videos\ -r
    echo.
    echo Run with --help for full options:
    echo   start.bat --help
    echo.
    echo Virtual environment is active. You can also run directly:
    echo   mov2mp4 --help
) else (
    REM Run the converter with provided arguments
    echo Running mov2mp4 with arguments: %*
    echo.
    mov2mp4 %*
)

echo.
echo Done!
pause
