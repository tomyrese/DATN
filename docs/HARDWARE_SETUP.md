# HƯỚNG DẪN CẤU HÌNH PHẦN CỨNG & SƠ ĐỒ KẾT NỐI (HARDWARE SETUP)

Tài liệu kỹ thuật chi tiết về cấu hình phần cứng, sơ đồ chân GPIO, phân chia nguồn điện và cảnh báo mức logic cho Robot Tự Hành Trung Tâm Thương Mại (Mall Concierge Robot).

---

## 1. DANH SÁCH THIẾT BỊ PHẦN CỨNG THỰC TẾ

1. **Bộ điều khiển trung tâm:** Raspberry Pi 4 Model B, 8 GB RAM.
2. **Camera trực tiếp:** Raspberry Pi CSI 5 MP (Cảm biến OmniVision OV5647).
3. **Màn hình hiển thị tại chỗ:** OLED 1.3 inch 128x64 pixels, chuẩn giao tiếp I2C, IC điều khiển SH1106.
4. **Động cơ chấp hành:** 4 Động cơ DC giảm tốc (DC Geared Motors) dẫn động 4 bánh xe (Differential / Skid-steer Drive).
5. **Mạch công suất điều khiển động cơ:** 2 Module mạch cầu H kép Toshiba TB6612FNG.
6. **Cảm biến khoảng cách:** 2 Cảm biến siêu âm HC-SR04 đặt ở mặt trước bên trái và bên phải robot.
7. **Nguồn điện:** Khối pin Li-ion 3S (11.1V - 12.6V) kết hợp các mạch hạ áp Buck LM2596 / XL4015 cấp nguồn độc lập.

---

## 2. BẢNG TRA CỨU SƠ ĐỒ CHÂN GPIO RASPBERRY PI 4

### 2.1. Module TB6612FNG Số 1 — Cụm Động Cơ Bên Trái (Left Motors)

| Chân Module TB6612FNG | Chân GPIO Raspberry Pi 4 | Chân Vật Lý (Pin #) | Chức Năng |
| :--- | :--- | :--- | :--- |
| **STBY (Standby)** | GPIO 27 | Pin 13 | Bật/tắt tầng công suất (HIGH = Kích hoạt, LOW = Phanh mềm) |
| **AIN1 (Motor 1 Dir A)** | GPIO 5 | Pin 29 | Hướng quay động cơ trước-trái |
| **AIN2 (Motor 1 Dir B)** | GPIO 6 | Pin 31 | Hướng quay động cơ trước-trái |
| **PWMA (Motor 1 Speed)**| GPIO 13 | Pin 33 (Hardware PWM) | Điều xung tốc độ động cơ trước-trái |
| **BIN1 (Motor 2 Dir A)** | GPIO 26 | Pin 37 | Hướng quay động cơ sau-trái |
| **BIN2 (Motor 2 Dir B)** | GPIO 22 | Pin 15 | Hướng quay động cơ sau-trái |
| **PWMB (Motor 2 Speed)**| GPIO 19 | Pin 35 (Hardware PWM) | Điều xung tốc độ động cơ sau-trái |
| **VCC (Logic Power)** | 3.3V | Pin 1 hoặc Pin 17 | Nguồn logic 3.3V |
| **VM (Motor Power)** | Nguồn Pin 12V (Buck 9V-12V) | — | Cấp nguồn công suất cho động cơ |
| **GND** | GND chung | Pin 6 / Pin 9 / Pin 14 | Nối chung mass toàn hệ thống |

### 2.2. Module TB6612FNG Số 2 — Cụm Động Cơ Bên Phải (Right Motors)

| Chân Module TB6612FNG | Chân GPIO Raspberry Pi 4 | Chân Vật Lý (Pin #) | Chức Năng |
| :--- | :--- | :--- | :--- |
| **STBY (Standby)** | GPIO 21 | Pin 40 | Bật/tắt tầng công suất bên phải |
| **AIN1 (Motor 3 Dir A)** | GPIO 16 | Pin 36 | Hướng quay động cơ trước-phải |
| **AIN2 (Motor 3 Dir B)** | GPIO 20 | Pin 38 | Hướng quay động cơ trước-phải |
| **PWMA (Motor 3 Speed)**| GPIO 12 | Pin 32 (Hardware PWM) | Điều xung tốc độ động cơ trước-phải |
| **BIN1 (Motor 4 Dir A)** | GPIO 23 | Pin 16 | Hướng quay động cơ sau-phải |
| **BIN2 (Motor 4 Dir B)** | GPIO 24 | Pin 18 | Hướng quay động cơ sau-phải |
| **PWMB (Motor 4 Speed)**| GPIO 18 | Pin 12 (Hardware PWM) | Điều xung tốc độ động cơ sau-phải |
| **VCC (Logic Power)** | 3.3V | Pin 1 / Pin 17 | Nguồn logic 3.3V |
| **VM (Motor Power)** | Nguồn Pin 12V | — | Nguồn công suất động cơ |
| **GND** | GND chung | Pin 20 / Pin 25 | Nối chung mass |

---

## 3. CẢM BIẾN SIÊU ÂM HC-SR04 & CẢNH BÁO ĐIỆN ÁP LOGIC 5V -> 3.3V

> [!CAUTION]
> **CẢNH BÁO NGUY HIỂM CHÁY HỎNG PHẦN CỨNG (CRITICAL ELECTRICAL WARNING):**
>
> 1. Cảm biến HC-SR04 bắt buộc chạy nguồn nuôi `VCC = 5V` để phát xung sóng siêu âm đạt cự ly chuẩn.
> 2. Chân `Echo` của HC-SR04 xuất tín hiệu logic **5.0V TTL** khi phản xạ sóng trở về.
> 3. Các chân GPIO của Raspberry Pi 4 **CHỈ CHỊU ĐƯỢC TỐI ĐA 3.3V** và **KHÔNG CÓ KHẢ NĂNG 5V TOLERANT**.
> 4. **TUYỆT ĐỐI KHÔNG ĐƯỢC NỐI TRỰC TIẾP CHÂN ECHO VÀO GPIO CỦA RASPBERRY PI.** Việc nối trực tiếp sẽ làm hỏng vĩnh viễn khối ngoại vi GPIO hoặc phá hủy SoC BCM2711 của Raspberry Pi!

### 3.1. Sơ đồ mạch chia áp (Voltage Divider) bắt buộc cho chân Echo

Mỗi cảm biến HC-SR04 phải đi qua một mạch chia áp gồm 2 điện trở:
- $R_1 = 1.0\ \text{k}\Omega$ (nối nối tiếp từ chân Echo đến chân GPIO)
- $R_2 = 2.0\ \text{k}\Omega$ (hoặc $2.2\ \text{k}\Omega$) (nối từ chân GPIO xuống GND)

Công thức điện áp ra:
$$V_{\text{GPIO}} = V_{\text{Echo}} \times \frac{R_2}{R_1 + R_2} = 5.0\text{V} \times \frac{2.0}{1.0 + 2.0} \approx 3.33\text{V} \quad (\text{An toàn tuyệt đối cho Pi 4})$$

```
  [HC-SR04 Echo Pin (5V)] 
             |
            [R1: 1.0 kΩ]
             |
             +-------------> Nối vào chân GPIO Raspberry Pi (3.3V Logic)
             |
            [R2: 2.0 kΩ]
             |
          [GND Chung]
```

*(Hoặc sử dụng Module Logic Level Converter 4 kênh hai chiều 5V <-> 3.3V chuyên dụng).*

### 3.2. Sơ đồ chân hai cảm biến siêu âm

| Cảm biến | Chân HC-SR04 | Chân GPIO Pi 4 | Chân Vật Lý | Lưu Ý Kỹ Thuật |
| :--- | :--- | :--- | :--- | :--- |
| **Cảm biến 1 (Trước - Trái)** | VCC | 5V Power | Pin 2 | Nguồn 5V từ mạch Buck ổn áp |
| | Trig | GPIO 25 | Pin 22 | Tín hiệu kích hoạt xung (Pi xuất 3.3V -> HC-SR04 nhận tốt) |
| | Echo | GPIO 8 | Pin 24 | **PHẢI QUA MẠCH CHIA ÁP 5V -> 3.3V** |
| | GND | GND | Pin 6 | Nối mass chung |
| **Cảm biến 2 (Trước - Phải)** | VCC | 5V Power | Pin 4 | Nguồn 5V từ mạch Buck ổn áp |
| | Trig | GPIO 7 | Pin 26 | Tín hiệu kích hoạt xung |
| | Echo | GPIO 1 | Pin 28 | **PHẢI QUA MẠCH CHIA ÁP 5V -> 3.3V** |
| | GND | GND | Pin 9 | Nối mass chung |

---

## 4. CAMERA CSI VÀ MÀN HÌNH OLED I2C

### 4.1. Camera Raspberry Pi CSI (OV5647 5 MP)
- Kết nối bằng cáp dẹt FPC 15-pin vào cổng CAMERA CSI trên bo mạch Raspberry Pi 4 (giữa cổng HDMI và jack Audio 3.5mm).
- Mặt tiếp xúc kim loại hướng về phía cổng HDMI.
- Trình điều khiển: `libcamera` / `picamera2` native kernel driver (Broadcom Unicam).

### 4.2. Màn hình OLED SH1106 1.3" I2C
- **VCC:** Nối 3.3V (Pin 1)
- **GND:** Nối GND (Pin 14)
- **SDA:** Nối GPIO 2 (I2C1 SDA - Pin 3)
- **SCL:** Nối GPIO 3 (I2C1 SCL - Pin 5)
- Địa chỉ I2C mặc định: `0x3C` (Kiểm tra bằng lệnh: `i2cdetect -y 1`).

---

## 5. PHÂN BỐ NGUỒN ĐIỆN VÀ AN TOÀN VẬT LÝ

```
     [Khối Pin Li-ion 3S (11.1V - 12.6V, 5000mAh)]
             |
             +---> [Cầu dao / Công tắc an toàn chính (Main Switch)]
             |
             +---> [Mạch Buck LM2596 / XL4015 (Số 1)] ---> 5.1V / 3.5A ---> Cổng Type-C Raspberry Pi 4
             |
             +---> [Mạch Buck LM2596 (Số 2)] -------------> 5.0V / 2A ---> Cấp nguồn HC-SR04 & Phụ kiện
             |
             +---> [Nguồn VM Trực tiếp hoặc Buck 9V] ------> 9V-12V / 5A ---> VM của 2x TB6612FNG (Động cơ)
```

**Nguyên tắc vàng:**
1. Tách biệt nguồn logic của Raspberry Pi khỏi nguồn tải cảm ứng của động cơ DC để triệt tiêu nhiễu sụt áp và xung ngược (inductive kickback).
2. Nối chung toàn bộ Mass (GND) của nguồn Pi, nguồn động cơ và các module cảm biến.
3. Luôn trang bị nút ngắt nguồn vật lý khẩn cấp (Emergency Power Cutoff) cơ khí độc lập trên khung vỏ robot.
