# HƯỚNG DẪN VẬN HÀNH CODE ĐIỀU KHIỂN ROBOT 4WD CARRIER

Hệ thống mã nguồn được tổ chức thành 2 phần độc lập theo cấu trúc module:

```
d:/Study/DATN/code/
├── python/                 # Mã nguồn Python điều khiển phần cứng (CLI / Terminal)
│   ├── config.py           # Cấu hình ánh xạ chân BCM GPIO & Header Pi 4
│   ├── motor_controller.py # Lớp điều khiển Driver TB6612 (U_TB1)
│   ├── test_left_motors.py # Kịch bản kiểm tra 2 bánh bên trái
│   └── requirements.txt    # Thư viện phụ thuộc cho Raspberry Pi OS
└── website/                # Giao diện Web Dashboard điều khiển từ xa
    ├── index.html          # Giao diện web hiện đại, hỗ trợ mobile & desktop
    ├── style.css           # Giao diện tối (Dark mode), glassmorphism cao cấp
    ├── app.js              # Xử lý sự kiện bàn phím, cảm ứng và gửi lệnh API
    └── server.py           # Máy chủ Web HTTP & REST API (chạy trực tiếp không cần Flask)
```

---

## 1. BẢNG ÁNH XẠ CHÂN PHẦN CỨNG (TB6612 U_TB1 - 2 BÁNH TRÁI)

Dựa trên sơ đồ nguyên lý và thiết kế mạch in 1 lớp:

| Tín hiệu Driver | Vị trí Header Pi 4 | BCM GPIO | Màu dây / Chức năng |
| :--- | :--- | :--- | :--- |
| **PWMA_L** | **Pin 3** | **GPIO 2** | Băm xung PWM điều khiển tốc độ chung kênh A & B |
| **AIN2_L** | **Pin 5** | **GPIO 3** | Đảo chiều quay (AIN2 & BIN2 nối song song) |
| **AIN1_L** | **Pin 7** | **GPIO 4** | Đảo chiều quay (AIN1 & BIN1 nối song song) |
| **STBY_L** | **Pin 11** | **GPIO 17** | Kích hoạt driver (`HIGH` = Bật, `LOW` = Tắt ngắt nguồn) |

---

## 2. CHẠY KIỂM TRA BẰNG PYTHON TERMINAL

Chạy trực tiếp trên Raspberry Pi 4 (hoặc trên máy tính ở chế độ Giả lập):

```bash
cd d:/Study/DATN/code/python
python test_left_motors.py
```

### Các tùy chọn kiểm tra:
1. **Chế độ 1 (Tự động - Khuyến nghị)**: 
   - Tự động bật driver `STBY = HIGH`.
   - Quay **TIẾN** 50% trong 2.5 giây.
   - **HÃM PHANH** (Short Brake) 1.5 giây.
   - Quay **LÙI** 50% trong 2.5 giây.
   - Thử nghiệm tăng tốc mượt $20\% \to 100\%$ và giảm tốc mượt $100\% \to 10\%$.
   - Dừng và giải phóng GPIO an toàn.
2. **Chế độ 2 (Thủ công qua bàn phím)**:
   - `W`: Quay tiến bánh trái.
   - `S`: Quay lùi bánh trái.
   - `B`: Hãm phanh tức thời.
   - `Space` / `X`: Thả trôi dừng tự nhiên.
   - `+` / `-`: Tăng / giảm tốc độ 10%.
   - `Q`: Thoát.

---

## 3. CHẠY ĐIỀU KHIỂN QUA GIAO DIỆN WEBSITE

Khởi động máy chủ web tích hợp:

```bash
cd d:/Study/DATN/code/website
python server.py
```

Sau khi khởi động, bạn có thể mở trình duyệt trên điện thoại hoặc máy tính:
- Trên máy tính: `http://localhost:8080`
- Từ điện thoại cùng mạng WiFi: `http://<IP_RASPBERRY_PI>:8080`

### Tính năng Web Dashboard:
- Nút bấm cảm ứng to rõ, trực quan cho điện thoại.
- Thanh trượt điều chỉnh tốc độ PWM từ $20\%$ đến $100\%$.
- Nút chạy tự động toàn bộ quy trình kiểm tra (**Auto Test**).
- Đồng bộ phím nóng bàn phím (W, S, B, Space, +, -).
- Bảng nhật ký thời gian thực (Live Logs) hiển thị trạng thái và phản hồi từ robot.
