#!/usr/bin/env bash
# ==============================================================================
# Production / Local Linux / VPS runner for Pocket Option AI Analyzer Bot
# ==============================================================================
set -e

echo "==================================================="
echo "  Starting Pocket Option AI Analyzer Bot (Linux/VPS)"
echo "==================================================="

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.12+."
    exit 1
fi

# Create venv if not present
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
fi

echo "[*] Activating virtual environment..."
source venv/bin/activate

echo "[*] Ensuring dependencies are up-to-date..."
pip install --upgrade pip
pip install -r requirements.txt

# Ensure .env exists
if [ ! -f ".env" ]; then
    echo "[!] .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "[!] Please configure TELEGRAM_BOT_TOKEN in .env"
fi

MODE="${1:-polling}"

if [ "$MODE" = "server" ]; then
    echo "[*] Starting FastAPI Server on port ${PORT:-3000}..."
    exec python main.py --mode server
else
    echo "[*] Starting Telegram Bot in Long Polling mode..."
    exec python main.py --mode polling
fi
