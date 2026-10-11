#!/bin/bash
set -e

echo "================================================================="
echo "   HỆ THỐNG ROBOT TỰ HÀNH TTTM — CÀI ĐẶT TRÊN RASPBERRY PI 4"
echo "================================================================="

# 1. Kiểm tra kiến trúc hệ thống
ARCH=$(uname -m)
echo "[*] Kien truc CPU: $ARCH"
if [ "$ARCH" != "aarch64" ] && [ "$ARCH" != "armv7l" ]; then
    echo "[!] Canh bao: Ban khong chay tren Raspberry Pi (CPU khac ARM). Van tiep tuc cai dat..."
fi

# 2. Cài đặt các gói hệ thống Linux (Debian Bookworm)
echo "[*] Cap nhat goi he thong va cai dat thu vien ngoai vi..."
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    libcamera-apps \
    libcamera-dev \
    python3-picamera2 \
    python3-rpi.gpio \
    python3-lgpio \
    python3-pil \
    python3-smbus \
    i2c-tools \
    sqlite3 \
    curl \
    git

# 3. Chuyển vào thư mục gốc dự án
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

# 4. Tạo môi trường ảo .venv (kết hợp system-site-packages cho Pi camera driver)
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Dang tao moi truong ao Python: $VENV_DIR..."
    python3 -m venv --system-site-packages "$VENV_DIR"
fi

echo "[*] Kich hoat moi truong ao $VENV_DIR..."
source "$VENV_DIR/bin/activate"

# 5. Cài đặt thư viện Python vào riêng .venv
echo "[*] Dang cai dat thu vien Python vao $VENV_DIR (khong cham pip global)..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. Cấu hình file .env cho phần cứng Pi 4
if [ ! -f ".env" ]; then
    echo "[*] Tao file .env cho phan cung Pi 4..."
    cp .env.example .env
    # Cập nhật các cờ phần cứng sang true
    sed -i 's/SIMULATION_MODE=true/SIMULATION_MODE=false/g' .env || true
    sed -i 's/MOTOR_ENABLED=false/MOTOR_ENABLED=true/g' .env || true
    sed -i 's/CAMERA_ENABLED=false/CAMERA_ENABLED=true/g' .env || true
    sed -i 's/ULTRASONIC_ENABLED=false/ULTRASONIC_ENABLED=true/g' .env || true
    sed -i 's/OLED_ENABLED=false/OLED_ENABLED=true/g' .env || true
fi

# 7. Khởi tạo cơ sở dữ liệu SQLite v2
echo "[*] Khoi tao Database SQLite v2 (Migrator & Seed)..."
python3 -m src.database.migrator
python3 -m src.database.seed

# 8. Kiểm tra kết nối ngoại vi
echo ""
echo "================================================================="
echo "[*] KIEM TRA PHAN CUNG NGOAI VI:"
echo "--- 1. I2C Bus (OLED 0x3c) ---"
if command -v i2cdetect >/dev/null 2>&1; then
    sudo i2cdetect -y 1 || true
fi

echo "--- 2. Camera CSI (OV5647) ---"
if command -v rpicam-hello >/dev/null 2>&1; then
    rpicam-hello --list-cameras || true
elif command -v libcamera-hello >/dev/null 2>&1; then
    libcamera-hello --list-cameras || true
fi

echo ""
echo "================================================================="
echo "   HOAN TAT CAI DAT HE THONG TREN RASPBERRY PI 4!"
echo "================================================================="
echo "1. Chay thu nghiem phan cung (Ke banh xe len khong trung):"
echo "   source .venv/bin/activate"
echo "   python3 scripts/test_motor.py"
echo "   python3 scripts/test_ultrasonic.py"
echo "   python3 scripts/test_camera.py"
echo "   python3 scripts/test_oled.py"
echo ""
echo "2. Khoi dong Robot Backend:"
echo "   source .venv/bin/activate"
echo "   python3 src/main.py"
echo ""
echo "3. Cai dat chay ngam Service tu dong cung he thong:"
echo "   sudo cp systemd/pi-robot.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable --now pi-robot.service"
echo "================================================================="
