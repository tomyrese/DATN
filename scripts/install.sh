#!/bin/bash
set -e

echo "=== ROBOT PLATFORM INSTALLER (ISOLATED VENV) ==="

UNAME_M=$(uname -m)
echo "System Architecture: $UNAME_M"

sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-pil \
    python3-smbus \
    i2c-tools \
    libcamera-apps \
    python3-picamera2 \
    python3-rpi.gpio \
    python3-lgpio \
    curl \
    wget

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating isolated Python virtual environment: $VENV_DIR..."
    python3 -m venv --system-site-packages "$VENV_DIR"
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Upgrading pip and installing dependencies into $VENV_DIR (no global pip pollution)..."
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "Initializing SQLite v2 schema and seeding data..."
python3 -m src.database.migrator
python3 -m src.database.seed

echo "Testing I2C bus..."
if command -v i2cdetect >/dev/null 2>&1; then
    sudo i2cdetect -y 1 || true
fi

echo "Testing camera presence..."
if command -v rpicam-hello >/dev/null 2>&1; then
    rpicam-hello --list-cameras || true
elif command -v libcamera-hello >/dev/null 2>&1; then
    libcamera-hello --list-cameras || true
fi

echo "=== INSTALLATION COMPLETE ==="
echo "Virtual environment ready at $ROOT_DIR/$VENV_DIR"
echo "To activate: source $VENV_DIR/bin/activate"
echo "To run server: python3 src/main.py"
