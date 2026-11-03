# Hướng Dẫn Vận Hành Phần Mềm Robot 4WD Raspberry Pi 4

Thư mục này chứa toàn bộ mã nguồn điều khiển phần cứng của **Robot Tự Hành 4WD**, chạy trực tiếp trên hệ điều hành **Raspberry Pi OS** (hoặc chạy mô phỏng trên PC/Laptop).

---

## 1. Sơ Đồ Đấu Nối Phần Cứng (Mạch Carrier 1 Lớp)

### A. Hệ thống 2 Cụm Động cơ 4WD (Driver TB6612FNG)
- **Cụm Bánh Trái (U_TB1)**:
  - `PWMA_L` (Điều tốc PWM): **BCM GPIO 2** (Header Pin 3)
  - `AIN1_L` (Chiều quay 1): **BCM GPIO 4** (Header Pin 7)
  - `AIN2_L` (Chiều quay 2): **BCM GPIO 3** (Header Pin 5)
  - `STBY_L` (Bật driver) : **BCM GPIO 17** (Header Pin 11)
  - `VCC` (Nguồn logic 5V) : **Header Pin 2 (+5V_PI_1)**
  - `VM` (Nguồn động cơ)  : **Pin 11.1V qua công tắc nguồn**

- **Cụm Bánh Phải (U_TB2)**:
  - `PWMA_R` (Điều tốc PWM): **BCM GPIO 13** (Header Pin 33)
  - `AIN1_R` (Chiều quay 1): **BCM GPIO 26** (Header Pin 37)
  - `AIN2_R` (Chiều quay 2): **BCM GPIO 19** (Header Pin 35)
  - `STBY_R` (Bật driver) : **BCM GPIO 20** (Header Pin 38)
  - `VCC` (Nguồn logic 5V) : **Header Pin 4 (+5V_PI_2)**
  - `VM` (Nguồn động cơ)  : **Pin 11.1V qua công tắc nguồn**

### B. Hệ thống 2 Cảm biến Siêu âm HC-SR04
- **Cảm biến Trái (U_US1)**:
  - `TRIG_L`: **BCM GPIO 27** (Header Pin 13)
  - `ECHO_L`: **BCM GPIO 22** (Header Pin 15 - qua cầu phân áp 1kΩ / 2kΩ)
- **Cảm biến Phải (U_US2)**:
  - `TRIG_R`: **BCM GPIO 5** (Header Pin 29)
  - `ECHO_R`: **BCM GPIO 6** (Header Pin 31 - qua cầu phân áp 1kΩ / 2kΩ)

---

## 2. Các Kịch Bản Chạy Kiểm Thử & Vận Hành

### Kịch bản 1: Chẩn đoán & Kiểm tra Động cơ Bánh Phải (`test_right_motors.py`)
Dành riêng để chẩn đoán nguyên nhân bánh phải không quay:
```bash
python3 test_right_motors.py
```
- **Chế độ 1**: Chẩn đoán trực tiếp không băm xung (Bypass Test - cấp trực tiếp mức HIGH vào chân PWM và STBY trong 3 giây để xác minh nguồn 5V và Driver).
- **Chế độ 2**: Tự động tăng giảm tốc PWM.
- **Chế độ 3**: Điều khiển thủ công phím W/S/B/X.

### Kịch bản 2: Kiểm tra Động cơ Bánh Trái (`test_left_motors.py`)
```bash
python3 test_left_motors.py
```

### Kịch bản 3: Kiểm tra Đồng bộ Cả 4 Bánh Xe (`test_all_motors.py`)
Kiểm tra phối hợp 4 bánh: Tiến, Lùi, Rẽ vi sai mượt, Xoay tròn tại chỗ (Tank Turn) và lái tự do:
```bash
python3 test_all_motors.py
```

### Kịch bản 4: Test Cảm biến Siêu âm (`test_ultrasonic.py`)
```bash
python3 test_ultrasonic.py
```

### Kịch bản 5: TỰ HÀNH NÉ VẬT CẢN THÔNG MINH (`auto_drive.py`)
Kịch bản tự động hóa chính của xe: Quét liên tục 2 cảm biến siêu âm, tự động giảm tốc, bẻ lái né vật cản, hoặc lùi và xoay góc thoát hiểm:
```bash
python3 auto_drive.py
```
- Nhấn phím `1` để kích hoạt Tự hành thông minh.
- Nhấn `Ctrl + C` để dừng xe an toàn bất kỳ lúc nào.
