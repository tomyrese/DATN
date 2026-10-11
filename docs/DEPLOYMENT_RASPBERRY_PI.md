# HƯỚNG DẪN TRIỂN KHAI TRÊN RASPBERRY PI 4 (DEPLOYMENT ON PI)

Tài liệu hướng dẫn triển khai thực tế hệ thống Robot Tự Hành trên Raspberry Pi 4 Model B chạy Raspberry Pi OS 64-bit (Debian Bookworm).

---

## 1. YÊU CẦU MÔI TRƯỜNG & HỆ ĐIỀU HÀNH

- **Phần cứng:** Raspberry Pi 4 Model B (RAM 4GB hoặc 8GB).
- **Thẻ nhớ:** MicroSD Class 10 U3 tối thiểu 32GB (khuyến nghị SanDisk Extreme hoặc SSD USB 3.0).
- **Hệ điều hành:** Raspberry Pi OS Lite 64-bit (Debian 12 Bookworm).
- **Python:** Phiên bản 3.11 hoặc 3.12 (64-bit).
- **Node.js:** v18.x trở lên (nếu build frontend trực tiếp trên Pi; khuyến nghị build trên máy phát triển rồi copy thư mục `frontend/dist`).

---

## 2. CÀI ĐẶT CÁC THƯ VIỆN HỆ THỐNG (SYSTEM PACKAGES)

Cập nhật hệ điều hành và cài đặt các gói phụ thuộc phần cứng (Camera, I2C, GPIO, OpenCV):

```bash
sudo apt update && sudo apt full-upgrade -y

# Cài đặt công cụ lập trình và thư viện ngoại vi
sudo apt install -y python3-pip python3-venv python3-dev \
    libcamera-dev libcamera-tools \
    python3-opencv libopencv-dev \
    i2c-tools python3-smbus \
    libgpiod-dev gpiod \
    sqlite3 git curl
```

### Bật giao tiếp Camera CSI và I2C trong cấu hình Pi:
Chạy lệnh `sudo raspi-config`:
1. **Interface Options** $\rightarrow$ **I2C** $\rightarrow$ Chọn **Enable**.
2. **Interface Options** $\rightarrow$ **Camera** $\rightarrow$ Chọn **Enable**.
3. Khởi động lại Raspberry Pi:
   ```bash
   sudo reboot
   ```

Kiểm tra kết nối phần cứng sau khi khởi động:
```bash
# Kiểm tra màn hình OLED I2C (phải xuất hiện địa chỉ 0x3c)
i2cdetect -y 1

# Kiểm tra camera CSI OV5647
rpicam-hello --list-cameras
```

---

## 3. CÀI ĐẶT MÃ NGUỒN VÀ PYTHON VIRTUAL ENVIRONMENT

```bash
# Clone hoặc sao chép mã nguồn vào thư mục người dùng
cd /home/pi
git clone https://github.com/tomyrese/DATN.git robot_code
cd robot_code

# Tạo môi trường ảo Python
python3 -m venv venv
source venv/bin/activate

# Cài đặt các gói phụ thuộc Python
pip install --upgrade pip
pip install -r requirements.txt
```

### Cấu hình biến môi trường:
Tạo tệp `.env` từ `.env.example`:
```bash
cp .env.example .env
nano .env
```
Cập nhật các giá trị thực tế trên Pi:
```env
SIMULATION_MODE=false
ULTRASONIC_ENABLED=true
MOTOR_ENABLED=true
CAMERA_ENABLED=true
OLED_ENABLED=true
OPENROUTER_API_KEY=your_actual_openrouter_key
```

---

## 4. TỰ ĐỘNG KHỞI ĐỘNG CÙNG HỆ THỐNG QUA SYSTEMD (SYSTEM SERVICE)

Tạo tệp dịch vụ hệ thống systemd để robot tự động khởi động sau khi cấp điện:

```bash
sudo nano /etc/systemd/system/pi-robot.service
```

Nội dung tệp cấu hình:
```ini
[Unit]
Description=Pi Robot Central Command Service (Mall Concierge)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/robot_code
ExecStart=/home/pi/robot_code/venv/bin/python src/main.py
Restart=always
RestartSec=5
KillSignal=SIGINT
TimeoutStopSec=10
EnvironmentFile=/home/pi/robot_code/.env

[Install]
WantedBy=multi-user.target
```

Kích hoạt và khởi động dịch vụ:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pi-robot.service
sudo systemctl start pi-robot.service

# Kiểm tra trạng thái dịch vụ
sudo systemctl status pi-robot.service

# Xem nhật ký hoạt động thời gian thực
journalctl -u pi-robot.service -f
```

---

## 5. TRUY CẬP TỪ XA AN TOÀN TRONG TRUNG TÂM THƯƠNG MẠI

### 5.1. Mạng nội bộ Wi-Fi (Local Mall Wi-Fi)
- Robot kết nối vào mạng Wi-Fi sảnh TTTM và nhận IP tĩnh (ví dụ: `192.168.1.100`).
- Người dùng truy cập trực tiếp qua trình duyệt: `http://192.168.1.100:8765`.

### 5.2. Đường hầm Cloudflare Tunnel (Miễn phí & Không cần mở port router)
1. Cài đặt `cloudflared` trên Pi:
   ```bash
   curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
   sudo dpkg -i cloudflared.deb
   ```
2. Mở đường hầm HTTPS an toàn:
   ```bash
   cloudflared tunnel --url http://localhost:8765
   ```
3. URL HTTPS được sinh tự động (ví dụ: `https://robot-mall.trycloudflare.com`) giúp nhân viên điều khiển từ xa qua 4G/5G với mã hóa SSL toàn diện.
