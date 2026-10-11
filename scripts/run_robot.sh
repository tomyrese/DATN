#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
    echo "[!] Chua tim thay moi truong ao .venv. Dang chay setup_pi.sh..."
    bash scripts/setup_pi.sh
fi

echo "[*] Kich hoat moi truong ao .venv va khoi dong Robot Backend..."
source .venv/bin/activate
python3 src/main.py
