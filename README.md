# Raspberry Pi 4 Robot Foundation Platform (Phase 1)

Nền tảng robot tự hành công nghiệp/thương mại sử dụng **Raspberry Pi 4 Model B**, trang bị hệ thống an toàn đa tầng với camera CSI, nhận diện người thời gian thực (Person Detection), màn hình trạng thái OLED I2C và điều khiển 4 động cơ DC qua 2 mạch TB6612FNG.

---

## 1. Tổng quan Kiến trúc

```
+-----------------------------------------------------------------------------+
|                               Raspberry Pi 4                                |
|                                                                             |
|  +----------------+     +-------------------+     +----------------------+  |
|  |  CameraService | --> |   PersonDetector  | --> |   SafetyController   |  |
|  |  (CSI Camera)  |     | (SSD MobileNet V2)|     | (Priority & Lock)    |  |
|  +----------------+     +-------------------+     +----------------------+  |
|         |                         |                           |             |
|         v                         v                           v             |
|  +-----------------------------------------------------------------------+  |
|  |                   Camera & System Watchdog Monitors                   |  |
|  +-----------------------------------------------------------------------+  |
|                                                               |             |
|                                                               v             |
|  +----------------+                               +----------------------+  |
|  | OLEDController | <---------------------------- |   MotorController    |  |
|  |  (SH1106 I2C)  |                               |    (2x TB6612FNG)    |  |
|  +----------------+                               +----------------------+  |
+-----------------------------------------------------------------------------+
```

---

## 2. Bảng Đấu Nối Phần Cứng (Hardware Wiring)

> [!CAUTION]
> **CẢNH BÁO NGUỒN ĐIỆN (POWER WARNING):**
> 1. **TUYỆT ĐỐI KHÔNG** cấp nguồn động cơ từ chân 3.3V hoặc 5V của Raspberry Pi.
> 2. Động cơ phải dùng nguồn pin riêng (ví dụ 2S/3S LiPo hoặc 7.4V–12V DC) đấu vào chân **VM** và **GND** của module TB6612FNG.
> 3. **GND của Raspberry Pi, GND của TB6612 và Cực Âm (-) của khối Pin Motor PHẢI ĐƯỢC NỐI CHUNG (Common Ground)** để logic điều khiển hoạt động chính xác.

### 2.1. Bảng Chân Điều Khiển 4 Motor (2x TB6612FNG)

| Module TB6612 | Chức năng Pin | BCM GPIO | Physical Pin trên Pi 4 | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| **TB_LEFT (Bên Trái)** | STBY_L | **GPIO 27** | Pin 13 | Bật/tắt cầu H bên trái |
| | AIN1_L | **GPIO 5** | Pin 29 | Hướng Motor 1 (Trái Trước) |
| | AIN2_L | **GPIO 6** | Pin 31 | Hướng Motor 1 (Trái Trước) |
| | PWMA_L | **GPIO 13** | Pin 33 | Tốc độ Motor 1 (Hardware PWM1) |
| | BIN1_L | **GPIO 26** | Pin 37 | Hướng Motor 2 (Trái Sau) |
| | BIN2_L | **GPIO 22** | Pin 15 | Hướng Motor 2 (Trái Sau) |
| | PWMB_L | **GPIO 19** | Pin 35 | Tốc độ Motor 2 (Hardware PWM1) |
| **TB_RIGHT (Bên Phải)** | STBY_R | **GPIO 21** | Pin 40 | Bật/tắt cầu H bên phải |
| | PWMA_R | **GPIO 12** | Pin 32 | Tốc độ Motor 3 (Phải Trước - PWM0) |
| | AIN1_R | **GPIO 16** | Pin 36 | Hướng Motor 3 (Phải Trước) |
| | AIN2_R | **GPIO 20** | Pin 38 | Hướng Motor 3 (Phải Trước) |
| | PWMB_R | **GPIO 18** | Pin 12 | Tốc độ Motor 4 (Phải Sau - PWM0) |
| | BIN1_R | **GPIO 23** | Pin 16 | Hướng Motor 4 (Phải Sau) |
| | BIN2_R | **GPIO 24** | Pin 18 | Hướng Motor 4 (Phải Sau) |

### 2.2. Bảng Chân Màn Hình OLED (1.3" I2C 128x64 SH1106 / SSD1306)

| Chân OLED | Chức năng | Chân Raspberry Pi 4 | Physical Pin |
| :--- | :--- | :--- | :--- |
| **VCC** | Nguồn 3.3V Logic | 3.3V Power | **Pin 1** |
| **GND** | Nối đất | Ground | **Pin 6** |
| **SDA** | I2C Data | BCM GPIO 2 (SDA1) | **Pin 3** |
| **SCK / SCL** | I2C Clock | BCM GPIO 3 (SCL1) | **Pin 5** |

---

## 3. Quy Ước Điều Khiển Động Cơ & Chiều Quay

- **Motor 1** = TB_LEFT Channel A (Bánh trước bên trái)
- **Motor 2** = TB_LEFT Channel B (Bánh sau bên trái)
- **Motor 3** = TB_RIGHT Channel A (Bánh trước bên phải)
- **Motor 4** = TB_RIGHT Channel B (Bánh sau bên phải)

### Logic Cầu H TB6612:
- Tốc độ hợp lệ: `-1.0` đến `+1.0`. Tần số PWM: `1000 Hz`.
- `Speed > 0`: `IN1 = HIGH`, `IN2 = LOW`, `PWM = Speed * 100%`
- `Speed < 0`: `IN1 = LOW`, `IN2 = HIGH`, `PWM = |Speed| * 100%`
- `Speed == 0`: `IN1 = LOW`, `IN2 = LOW`, `PWM = 0%` (Coast / Float)
- `Emergency Stop`: Tất cả `PWM = 0`, `IN1/IN2 = LOW`, `STBY_L = LOW`, `STBY_R = LOW` (Brake & Shutdown)

### Lệnh di chuyển:
- **Tiến (Forward):** Motor Trái = `+Speed`, Motor Phải = `+Speed`
- **Lùi (Backward):** Motor Trái = `-Speed`, Motor Phải = `-Speed`
- **Quay Trái (Turn Left):** Motor Trái = `-Speed`, Motor Phải = `+Speed`
- **Quay Phải (Turn Right):** Motor Trái = `+Speed`, Motor Phải = `-Speed`
- **Dừng (Stop):** Toàn bộ Motor = `0.0`

---

## 4. Hệ Thống An Toàn (Safety System & Vision Logic)

> [!WARNING]
> **GIỚI HẠN CỦA CAMERA AI (LIMITATION):**
> Nhận diện người qua camera thị giác máy tính là phương pháp heuristic giúp phản xạ tránh va chạm. Trong môi trường thực tế, camera có thể bị che khuất hoặc ánh sáng yếu. Trong các phase tiếp theo, cần tích hợp cảm biến tiếp xúc (Bumper), siêu âm (Ultrasonic), ToF hoặc LiDAR để đạt tiêu chuẩn an toàn công nghiệp hoàn chỉnh.

### 4.1. Vùng Dừng Khẩn Cấp (STOP_ZONE) & Lọc Đối Tượng
- **Vùng trung tâm (STOP_ZONE):** Tọa độ X trục ngang từ `0.20` đến `0.80` (20% đến 80% độ rộng khung hình camera).
- **Ngưỡng diện tích (PERSON_MIN_AREA_RATIO):** Tối thiểu `0.03` (3% diện tích khung hình) để loại bỏ người ở khoảng cách quá xa không gây nguy hiểm.
- **Ngưỡng độ tin cậy (PERSON_CONFIDENCE_THRESHOLD):** Mặc định `0.55`.

### 4.2. Trạng Thái An Toàn & Phản Xạ Dừng
1. **Phát hiện người khi đang di chuyển:**
   - Khi robot đang chạy (`FORWARD`, `BACKWARD`, `TURN_LEFT`, `TURN_RIGHT`) và camera phát hiện `person` trong `STOP_ZONE`:
   - `motor.stop()` được thực thi **ngay lập tức** không chờ đợi UI hay render OLED.
   - Trạng thái chuyển thành `PERSON_DETECTED` / `SAFETY_STOP`.
2. **Khử rung & trễ an toàn (Hysteresis & Clear Delay):**
   - Khi người rời khỏi vùng quan sát, robot duy trì trạng thái an toàn trong `PERSON_CLEAR_DELAY` (1.5 giây).
   - Chỉ sau 1.5s liên tục không có người, hệ thống mới giải phóng cờ an toàn và chuyển về `STOPPED`.
3. **Chính sách không tự chạy lại (No Auto Resume):**
   - `AUTO_RESUME_AFTER_PERSON_CLEAR = false`: Khi người đã rời đi, robot **GIỮ NGUYÊN TRẠNG THÁI STOPPED** và không bao giờ tự động chạy lại. Người vận hành bắt buộc phải nhập lệnh di chuyển mới từ CLI.
4. **Phân cấp ưu tiên (Strict Priority Hierarchy):**
   `EMERGENCY_STOP` > `SYSTEM_ERROR` > `CAMERA_ERROR` > `PERSON_SAFETY_STOP` > `MANUAL_STOP` > `MOVEMENT_COMMAND`
5. **Watchdog Giám sát Camera:**
   - Nếu robot đang di chuyển mà không nhận được frame mới trong `CAMERA_WATCHDOG_TIMEOUT` (2.0 giây), hệ thống tự động kích hoạt `SAFETY_STOP` và báo lỗi `CAMERA_ERROR`.

---

## 5. Cài Đặt Hệ Thống Trên Raspberry Pi 4

### 5.1. Bật Giao Tiếp I2C và Camera trên Raspberry Pi OS

Mở terminal trên Raspberry Pi:
```bash
sudo raspi-config
```
- Vào **Interface Options** -> **I2C** -> Chọn **Yes** (Enable).
- Vào **Interface Options** -> **Camera** -> Chọn **Yes** (Enable).
- Chọn **Finish** và khởi động lại:
```bash
sudo reboot
```

Kiểm tra I2C:
```bash
sudo i2cdetect -y 1
```
*(Kết quả sẽ thấy địa chỉ `0x3c` của màn hình OLED)*

Kiểm tra Camera CSI:
```bash
rpicam-hello --list-cameras
```
*(Hoặc `libcamera-hello --list-cameras` nếu dùng Raspberry Pi OS Bullseye/Bookworm)*

### 5.2. Chạy Script Cài Đặt Tự Động

```bash
cd ~/robot-pi
chmod +x scripts/*.sh
./scripts/install.sh
```

---

## 6. Hướng Dẫn Kiểm Thử Từng Module (Testing Steps)

### Bước 1: Kiểm thử Camera
Chụp 1 ảnh mẫu và đo FPS:
```bash
source venv/bin/activate
python scripts/test_camera.py
```

### Bước 2: Kiểm thử Màn hình OLED
Hiển thị lần lượt các màn hình BOOT, READY, MOVING, SAFETY STOP:
```bash
python scripts/test_oled.py
```

### Bước 3: Kiểm thử Từng Động Cơ (Motor Test)
> [!IMPORTANT]
> Đặt robot kê bánh lên cao (không chạm đất) trước khi chạy test motor.

```bash
python scripts/test_motor.py
```
*Script sẽ yêu cầu xác nhận 'y', sau đó quay thử Motor 1, 2, 3, 4 ở tốc độ 20% trong 0.4 giây.*

### Bước 4: Kiểm thử Nhận Diện Người Thời Gian Thực
```bash
# Chạy ở chế độ dòng lệnh
python scripts/test_person_detection.py

# Nếu cắm màn hình Desktop HDMI, chạy kèm cờ preview để xem khung nhận diện và STOP_ZONE:
python scripts/test_person_detection.py --preview
```

### Bước 5: Chạy Toàn Bộ Kịch Bản An Toàn & Unit Tests
```bash
python scripts/test_safety.py
python -m pytest tests/ -v
```

---

## 7. Vận Hành Robot & Giao Diện Điều Khiển Website (Web Dashboard)

Khởi động hệ thống điều khiển robot và máy chủ Web:
```bash
source venv/bin/activate
python -m src.main
```

Khi robot khởi động, máy chủ FastAPI & WebSocket sẽ tự động phục vụ **Giao diện Điều khiển Website** tại địa chỉ:
👉 **`http://<IP_ROBOT>:8765/`** *(hoặc `http://localhost:8765/` khi chạy trên máy)*

### 7.1. Các tính năng trên Giao diện Web:
- **Ghép nối bảo mật (Pairing System)**: Quét mã QR trên màn hình OLED bằng camera trình duyệt hoặc nhập mã PIN 6 ký tự.
- **Drive Controller**: Điều khiển hướng di chuyển bằng phím ảo D-Pad cảm ứng hoặc bàn phím (`W`, `A`, `S`, `D`, `Space`/`X` để dừng, `1`-`5` để chỉnh tốc độ).
- **CSI Camera Live Stream**: Xem luồng video MJPEG thời gian thực kèm lớp phủ nhận diện AI và cảnh báo vật cản.
- **HUD Telemetry & Diagnostics**: Giám sát nhiệt độ CPU, tải CPU/RAM, FPS camera/AI, đồ thị công suất 4 motor DC và nhật ký sự kiện hệ thống (Live Logs).
- **Motor Bench Test**: Thử nghiệm độc lập chiều quay từng motor (+20% FWD / -20% REV) khi robot đặt trên giá đỡ.
- **Critical Emergency Stop**: Nút phanh dừng khẩn cấp tức thời (Phím tắt: `E`, Reset: `R`).

### 7.2. Các phím điều khiển qua bàn phím (CLI / Web):
| Phím | Chức năng | Mô tả hành vi |
| :---: | :--- | :--- |
| **`w`** / `▲` | Tiến (Forward) | 4 bánh quay tiến theo tốc độ đã chọn |
| **`s`** / `▼` | Lùi (Backward) | 4 bánh quay lùi theo tốc độ đã chọn |
| **`a`** / `◀` | Quay trái (Turn Left) | Bánh trái quay lùi, bánh phải quay tiến |
| **`d`** / `▶` | Quay phải (Turn Right) | Bánh trái quay tiến, bánh phải quay lùi |
| **`x`** / `Space` | Dừng (Stop) | Ngắt PWM về 0 |
| **`e`** | Dừng khẩn cấp (E-Stop) | Ngắt PWM, tắt chân STBY cả 2 bên TB6612 |
| **`r`** | Reset E-Stop | Mở khóa an toàn sau khi đã clear chướng ngại vật |
| **`1` - `5`** | Tốc độ ga (Throttle) | Chuyển nhanh giữa các mức 20%, 35%, 50%, 75%, 100% |
| **`q`** | Thoát (Quit) | Dừng motor, tắt camera, dọn dẹp GPIO và thoát sạch sẽ |

---

## 8. Cài Đặt Dịch Vụ Khởi Động Tự Động (Systemd Service)

Sau khi kiểm thử thực tế hoàn tất, có thể cấu hình robot chạy dưới dạng background service:

1. Copy file service vào thư mục systemd:
```bash
sudo cp systemd/robot.service /etc/systemd/system/
sudo systemctl daemon-reload
```

2. Bật và khởi động service:
```bash
sudo systemctl enable robot.service
sudo systemctl start robot.service
```

3. Kiểm tra trạng thái và theo dõi logs:
```bash
sudo systemctl status robot.service
journalctl -u robot.service -f
```

4. Dừng service:
```bash
sudo systemctl stop robot.service
```

---

## 9. Cấu Hình Tham Số Tập Trung (.env)

Tất cả các tham số có thể điều chỉnh linh hoạt trong file `.env` mà không cần sửa code:

```env
# Tốc độ & PWM
PWM_FREQ=1000
DEFAULT_SPEED=0.35
MOTOR_ENABLED=true
SIMULATION_MODE=false

# Cấu hình Nhận diện & Vùng dừng an toàn
PERSON_CONFIDENCE_THRESHOLD=0.55
PERSON_MIN_AREA_RATIO=0.03
STOP_ZONE_X_MIN=0.20
STOP_ZONE_X_MAX=0.80
PERSON_CLEAR_DELAY=1.5
PERSON_DETECTED_CONFIRM_FRAMES=2
AUTO_RESUME_AFTER_PERSON_CLEAR=false
CAMERA_WATCHDOG_TIMEOUT=2.0
```

---

## 10. Xử Lý Sự Cố (Troubleshooting)

1. **Lỗi `Failed to initialize Picamera2`:**
   - Kiểm tra lại cáp dẹt CSI đã cắm chặt và đúng chiều vào cổng CAMERA của Raspberry Pi 4.
   - Chạy lệnh `rpicam-hello` kiểm tra xem camera có phản hồi không.
2. **Lỗi `OLED display not detected`:**
   - Kiểm tra lại chân VCC (3.3V Pin 1), GND (Pin 6), SDA (Pin 3), SCL (Pin 5).
   - Chạy `sudo i2cdetect -y 1` xem có xuất hiện địa chỉ `0x3c` không.
   - Nếu dùng OLED SSD1306 thay vì SH1106, đổi `OLED_DRIVER=ssd1306` trong `.env`.
3. **Bánh xe quay ngược chiều:**
   - Đảo vị trí 2 dây motor AIN1/AIN2 hoặc BIN1/BIN2 trên cầu đấu ốc của mạch TB6612 tương ứng.
4. **Motor không quay dù đèn LED sáng:**
   - Kiểm tra nguồn cấp vào chân **VM** của TB6612 (phải từ 7V đến 12V DC).
   - Kiểm tra xem dây GND giữa Pin và Raspberry Pi đã được nối chung chưa.
