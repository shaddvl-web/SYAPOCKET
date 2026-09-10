@echo off
echo ===================================================
echo   Starting Pocket Option AI Analyzer Bot (Windows)
echo ===================================================

REM Check if Python 3 is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH. Please install Python 3.12+ and check 'Add to PATH'.
    pause
    exit /b 1
)

REM Setup virtual environment if not already present
if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
)

echo [*] Activating virtual environment...
call venv\Scripts\activate

echo [*] Installing / upgrading dependencies...
pip install -r requirements.txt

REM Ensure .env file exists
if not exist ".env" (
    echo [!] .env file not found. Copying from .env.example...
    copy .env.example .env
    echo [!] Please configure your TELEGRAM_BOT_TOKEN in the .env file.
)

echo ===================================================
echo   Choose Execution Mode:
echo   1. Standalone Telegram Bot (Polling Mode)
echo   2. FastAPI Webhook Server + Healthcheck (Port 3000)
echo ===================================================
set /p MODE="Select mode (1 or 2, default is 1): "

if "%MODE%"=="2" (
    echo [*] Launching FastAPI Webhook Server on port 3000...
    python main.py --mode server
) else (
    echo [*] Launching Telegram Bot in Long Polling Mode...
    python main.py --mode polling
)

pause
