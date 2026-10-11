# HƯỚNG DẪN THIẾT LẬP & VẬN HÀNH ROBOT TỰ HÀNH TTTM TRÊN RASPBERRY PI 4

Hệ thống robot tự hành hỗ trợ khách hàng, nhân viên và ban quản lý tại Trung Tâm Thương Mại (TTTM) trên nền tảng **Raspberry Pi 4 Model B (8GB RAM)**, kết hợp ứng dụng điều khiển Web Responsive đa vai trò (**React 18 + Vite**), cơ sở dữ liệu quan hệ (**SQLite v2 WAL Mode**), thị giác máy tính cổ điển (**OpenCV Classical Vision** - không dùng mô hình deep learning huấn luyện sẵn), 2 cảm biến siêu âm **HC-SR04**, điều khiển 4 động cơ DC qua 2 mạch cầu H **TB6612FNG**, camera CSI OV5647 và màn hình OLED 1.3" I2C.

---

## 1. CẤU HÌNH PHẦN CỨNG & SƠ ĐỒ ĐẤU DÂY RASPBERRY PI 4

### 1.1. Cảnh Báo An Toàn Điện Nguồn & Mức Logic
> [!CAUTION]
> 1. **TUYỆT ĐỐI KHÔNG cấp nguồn động cơ từ chân 3.3V hoặc 5V của Raspberry Pi:** Động cơ phải dùng nguồn Pin riêng (2S/3S Li-ion/LiPo hoặc 7.4V - 12V DC) đấu vào chân **VM** và **GND** của module TB6612FNG.
> 2. **BẮT BUỘC NỐI CHUNG NỐI ĐẤT (Common Ground):** Chân GND của Raspberry Pi, chân GND của 2 module TB6612FNG và cực âm (-) của khối Pin động cơ PHẢI NỐI CHUNG VỚI NHAU để mức logic điều khiển ổn định.
> 3. **BẢO VỆ CHÂN GPIO ECHO HC-SR04 (5V -> 3.3V):** Chân Echo của cảm biến HC-SR04 phát ra mức logic 5V TTL. Chân GPIO Raspberry Pi chỉ chịu được tối đa 3.3V. **BẮT BUỘC dùng cầu phân áp 2 điện trở: $R_1 = 1\text{ k}\Omega$ (nối Echo vào GPIO) và $R_2 = 2\text{ k}\Omega$ (nối GPIO xuống GND)** để hạ điện áp xuống 3.3V an toàn.

---

### 1.2. Bảng Chân Kết Nối 4 Động Cơ DC (2x TB6612FNG)

| Module | Chân TB6612 | Chân BCM GPIO | Physical Pin Pi 4 | Chức Năng |
| :--- | :--- | :--- | :--- | :--- |
| **TB_LEFT (Cụm Bánh Trái)** | **STBY_L** | **GPIO 27** | Pin 13 | Bật/tắt cầu H bên trái (Standby) |
| | AIN1_L | **GPIO 5** | Pin 29 | Hướng Motor 1 (Trái Trước) |
| | AIN2_L | **GPIO 6** | Pin 31 | Hướng Motor 1 (Trái Trước) |
| | PWMA_L | **GPIO 13** | Pin 33 | Tốc độ PWM Motor 1 (Hardware PWM1) |
| | BIN1_L | **GPIO 26** | Pin 37 | Hướng Motor 2 (Trái Sau) |
| | BIN2_L | **GPIO 22** | Pin 15 | Hướng Motor 2 (Trái Sau) |
| | PWMB_L | **GPIO 19** | Pin 35 | Tốc độ PWM Motor 2 (Hardware PWM1) |
| **TB_RIGHT (Cụm Bánh Phải)** | **STBY_R** | **GPIO 21** | Pin 40 | Bật/tắt cầu H bên phải (Standby) |
| | PWMA_R | **GPIO 12** | Pin 32 | Tốc độ PWM Motor 3 (Phải Trước - PWM0) |
| | AIN1_R | **GPIO 16** | Pin 36 | Hướng Motor 3 (Phải Trước) |
| | AIN2_R | **GPIO 20** | Pin 38 | Hướng Motor 3 (Phải Trước) |
| | PWMB_R | **GPIO 18** | Pin 12 | Tốc độ PWM Motor 4 (Phải Sau - PWM0) |
| | BIN1_R | **GPIO 23** | Pin 16 | Hướng Motor 4 (Phải Sau) |
| | BIN2_R | **GPIO 24** | Pin 18 | Hướng Motor 4 (Phải Sau) |

---

### 1.3. Bảng Chân Cảm Biến Siêu Âm HC-SR04 & Màn Hình OLED

| Thiết bị | Chân thiết bị | Chân BCM GPIO | Physical Pin Pi 4 | Ghi chú an toàn |
| :--- | :--- | :--- | :--- | :--- |
| **HC-SR04 Trái** | **TRIG_L** | **GPIO 25** | Pin 22 | Tín hiệu kích hoạt xung (3.3V) |
| | **ECHO_L** | **GPIO 8** | Pin 24 | **Qua cầu trở 1kΩ / 2kΩ xuống 3.3V** |
| | VCC | 5V Power | Pin 2 hoặc 4 | Cấp nguồn 5V cho cảm biến |
| | GND | Ground | Pin 6 | Nối đất |
| **HC-SR04 Phải** | **TRIG_R** | **GPIO 7** | Pin 26 | Tín hiệu kích hoạt xung (3.3V) |
| | **ECHO_R** | **GPIO 1** | Pin 28 | **Qua cầu trở 1kΩ / 2kΩ xuống 3.3V** |
| | VCC / GND | 5V / GND | Pin 2 / Pin 30 | Nối nguồn và đất |
| **OLED 1.3" I2C** | **SDA** | **GPIO 2 (SDA1)** | Pin 3 | Tín hiệu I2C Data |
| | **SCL / SCK** | **GPIO 3 (SCL1)** | Pin 5 | Tín hiệu I2C Clock |
| | VCC | 3.3V Power | Pin 1 | Cấp nguồn 3.3V Logic |
| | GND | Ground | Pin 9 | Nối đất |
| **Camera CSI** | Cáp Ribbon 15-pin | Cổng Camera CSI | Dọc khe board Pi 4 | Camera Raspberry Pi OV5647 |

---

## 2. QUY TRÌNH THIẾT LẬP RASPBERRY PI 4 TỪ A - Z

### Bước 1: Chuẩn bị Hệ Điều Hành Raspberry Pi OS 64-bit
1. Sử dụng **Raspberry Pi Imager** để nạp hệ điều hành:
   - Chọn OS: **Raspberry Pi OS Lite (64-bit)** hoặc **Raspberry Pi OS with Desktop (64-bit)** (Debian 12 Bookworm).
   - Thiết lập trước: Tên người dùng `pi`, mật khẩu, cấu hình kết nối Wi-Fi và kích hoạt SSH.
2. Cắm thẻ nhớ vào Raspberry Pi 4, cắm nguồn (Type-C 5V 3A) và kết nối SSH từ máy tính:
   ```bash
   ssh pi@<IP_CUA_RASPBERRY_PI>
   ```

---

### Bước 2: Kích hoạt Giao tiếp Ngoại vi (I2C & Camera CSI)
Chạy công cụ cấu hình hệ thống:
```bash
sudo raspi-config
```
1. Chọn **Interface Options** $\rightarrow$ **I2C** $\rightarrow$ Chọn **Yes** (Bật I2C).
2. Chọn **Interface Options** $\rightarrow$ **Camera** (hoặc kiểm tra `rpicam-hello` trên Bookworm).
3. Khởi động lại Raspberry Pi:
   ```bash
   sudo reboot
   ```

Sau khi khởi động lại, kiểm tra trạng thái ngoại vi:
```bash
# 1. Kiểm tra màn hình OLED I2C (phải hiện địa chỉ 0x3c)
sudo i2cdetect -y 1

# 2. Kiểm tra Camera CSI OV5647
rpicam-hello --list-cameras
```

---

### Bước 3: Tải Mã Nguồn & Chạy Script Cài Đặt Tự Động
Toàn bộ mã nguồn và thư viện được cấu hình cài đặt vào **môi trường ảo Python cô lập (`.venv`)**, tuyệt đối không can thiệp vào `pip` toàn cục của hệ thống (tránh lỗi `externally-managed-environment` của Debian 12):

```bash
# Di chuyển vào thư mục làm việc
cd /home/pi
git clone https://github.com/tomyrese/DATN.git Code
cd Code

# Chạy script cài đặt trọn gói 1 bước
bash scripts/setup_pi.sh
```

**Script `setup_pi.sh` sẽ tự động thực hiện:**
- Cài đặt các gói phần mềm hệ thống: `libcamera-apps`, `i2c-tools`, `python3-venv`, `sqlite3`, `curl`.
- Khởi tạo môi trường ảo `.venv` với cờ `--system-site-packages` để tương thích driver camera Raspberry Pi.
- Cài đặt đầy đủ `requirements.txt` vào riêng `.venv` (bao gồm `fastapi`, `uvicorn`, `opencv-python-headless 4.x`, `bcrypt`...).
- Tự động sinh file cấu hình `.env` cho phần cứng thực tế (`SIMULATION_MODE=false`, `MOTOR_ENABLED=true`, `CAMERA_ENABLED=true`...).
- Tự động khởi tạo và nạp dữ liệu SQLite v2 (`migrator.py` & `seed.py`).

---

### Bước 4: Kiểm Tra Phần Cứng Độc Lập (Bắt Buộc Kê Bánh Xe)
> [!IMPORTANT]
> **KÊ KHUNG ROBOT LÊN KHÔNG TRUNG:** Đảm bảo 4 bánh xe quay tự do trong không khí trước khi kích hoạt động cơ!

Chạy các script kiểm tra từng module phần cứng riêng lẻ:
```bash
# Kích hoạt môi trường ảo
source .venv/bin/activate

# 1. Kiểm tra 4 động cơ quay tiến/lùi độc lập
python3 scripts/test_motor.py

# 2. Kiểm tra đọc khoảng cách từ 2 cảm biến siêu âm HC-SR04
python3 scripts/test_ultrasonic.py

# 3. Kiểm tra Camera CSI OV5647
python3 scripts/test_camera.py

# 4. Kiểm tra hiển thị màn hình OLED 1.3"
python3 scripts/test_oled.py
```

---

### Bước 5: Khởi Động Hệ Thống Robot

#### Cách 1: Chạy trực tiếp từ dòng lệnh
```bash
bash scripts/run_robot.sh
```
*Backend sẽ khởi động dịch vụ tại cổng `8765`.* Mở trình duyệt trên máy tính/điện thoại kết nối cùng mạng Wi-Fi và truy cập:
👉 **`http://<IP_CUA_RASPBERRY_PI>:8765`**

---

#### Cách 2: Cài đặt Dịch vụ Chạy Ngầm Tự Động cùng Hệ Thống (Systemd Service)
Để robot tự động khởi chạy mỗi khi bật nguồn mà không cần cắm màn hình hay gõ lệnh:
```bash
sudo cp systemd/pi-robot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pi-robot.service
sudo systemctl start pi-robot.service
```

Kiểm tra trạng thái hoạt động của dịch vụ:
```bash
# Xem trạng thái running
sudo systemctl status pi-robot.service

# Xem nhật ký log thời gian thực
sudo journalctl -u pi-robot.service -f
```

---

## 3. KẾT NỐI ĐIỀU KHIỂN TỪ XA QUA INTERNET (CLOUDFLARE TUNNEL)

Khi đưa robot vào trung tâm thương mại và muốn truy cập điều khiển qua mạng 4G/5G/Internet công cộng mà **không cần mở Port Forwarding, không cần IP tĩnh**:

1. Chạy script tạo đường hầm mã hóa Cloudflare tích hợp sẵn trên Pi 4:
   ```bash
   bash scripts/setup_cloudflare_tunnel.sh
   ```
2. Chọn tùy chọn **1 (Quick Free Tunnel)**. Terminal sẽ xuất ra đường link HTTPS an toàn, ví dụ:
   ```
   https://pi-robot-mall-xyz.trycloudflare.com
   ```
3. Mở Web Dashboard trên điện thoại, vào mục **Cài Đặt (Settings)** $\rightarrow$ Dán đường link trên vào ô **Backend Server URL** $\rightarrow$ Nhấn **"Lưu & Kết Nối"**.

---

## 4. TÀI KHOẢN MẪU & PHÂN QUYỀN TRUY CẬP (RBAC)

Hệ thống cung cấp giao diện Web thống nhất và tự động thay đổi tính năng theo vai trò:

| Vai trò | Tên đăng nhập | Mật khẩu | Chức năng chính |
| :--- | :--- | :--- | :--- |
| **Khách tham quan (Guest)** | *(Không đăng nhập)* | *(Không có)* | Xem bản đồ TTTM, tìm gian hàng, xem khuyến mãi, hỏi đáp AI Concierge, yêu cầu robot dẫn đường. |
| **Nhân viên Zara** | `staff_zara` | `Staff@123456` | Xem Camera CSI trực tiếp (vé 30s), lái xe thủ công (D-Pad / WASD), quản lý khuyến mãi ZARA, theo dõi đơn giao hàng. |
| **Nhân viên Uniqlo** | `staff_uniqlo` | `Staff@123456` | Tương tự nhân viên Zara, bị giới hạn chỉ thao tác dữ liệu thuộc shop UNIQLO. |
| **Quản trị viên (Admin)** | `admin` | `Admin@123456` | Toàn quyền quản trị tài khoản, sơ đồ bản đồ đồ thị, kích hoạt tuần tra hành lang, nút dừng khẩn cấp E-Stop toàn cục, xem Audit Logs, sao lưu Database. |

---

## 5. BỘ KIỂM THỬ TỰ ĐỘNG (53/53 TESTS PASS)

Để chạy kiểm thử toàn diện toàn bộ các module phần mềm (Phân quyền, SQLite v2, Thị giác OpenCV cổ điển, Odometry, FSM tránh vật cản) ngay trên môi trường ảo của Pi 4:
```bash
source .venv/bin/activate
pytest tests/ -v
# Kết quả: 53 passed, 100% Pass Rate
```

---

## 6. DANH MỤC TÀI LIỆU KỸ THUẬT CHI TIẾT

- [docs/HARDWARE_SETUP.md](file:///d:/Study/KLTN/Code/docs/HARDWARE_SETUP.md): Chi tiết sơ đồ mạch, bảo vệ điện áp 5V->3.3V và nguyên lý cấp nguồn.
- [docs/DEPLOYMENT_RASPBERRY_PI.md](file:///d:/Study/KLTN/Code/docs/DEPLOYMENT_RASPBERRY_PI.md): Cẩm nang triển khai sản xuất, tối ưu hóa CPU và giám sát hệ thống trên Pi 4.
- [docs/AUTONOMOUS_NAVIGATION.md](file:///d:/Study/KLTN/Code/docs/AUTONOMOUS_NAVIGATION.md): Thuật toán tìm đường A*, Odometry dead-reckoning và chu trình tuần tra 5 phút.
- [docs/VISION_AND_SAFETY.md](file:///d:/Study/KLTN/Code/docs/VISION_AND_SAFETY.md): Thị giác máy tính OpenCV cổ điển (MOG2 + Dalal-Triggs HOG/SVM) và FSM tránh vật cản 8 trạng thái.
- [docs/DATABASE_SCHEMA.md](file:///d:/Study/KLTN/Code/docs/DATABASE_SCHEMA.md): Sơ đồ ERD, 19 bảng SQLite, ràng buộc toàn vẹn và migration.
- [docs/SECURITY.md](file:///d:/Study/KLTN/Code/docs/SECURITY.md): Mô hình an ninh, Session RBAC, chống Prompt Injection và Audit Log.
- [docs/PROTOCOL.md](file:///d:/Study/KLTN/Code/docs/PROTOCOL.md): Đặc tả 18 REST APIs và kênh truyền WebSocket thời gian thực.
