# ĐỒ ÁN TỐT NGHIỆP: BO MẠCH CARRIER ROBOT 4WD CHO RASPBERRY PI 4 (CHUẨN 1 LỚP)

Hệ thống thiết kế phần cứng điện tử và phần mềm điều khiển cho Robot tự hành 4 bánh (4WD) sử dụng vi máy tính **Raspberry Pi 4**, tích hợp mạch nguồn hạ áp XL4015, 2 mạch cầu H công suất TB6612FNG, cảm biến siêu âm HC-SR04 và module dò line TCRT5000.

Mạch in được thiết kế tối ưu hóa đặc biệt theo dạng **Phẳng 1 Lớp (Single-Sided Planar PCB)**: **100% đường mạch đi trên lớp đáy (`B.Cu`), không sử dụng via, không jumper chéo dây, không phủ mass đồng kín**.

---

## 1. THÔNG SỐ KỸ THUẬT PHẦN CỨNG & DRC

| Tiêu chuẩn / Thông số | Giá trị thiết kế | Ghi chú kỹ thuật |
| :--- | :--- | :--- |
| **Số lớp mạch (Layers)** | **1 lớp duy nhất (`B.Cu`)** | Toàn bộ đường mạch nằm ở mặt hàn dưới |
| **Via xuyên lớp** | **0 Via** | Không chuyển lớp |
| **Khoảng cách chân (Pitch)** | **2.54 mm (100 mil)** | Đồng bộ 100% cho tất cả header, connector, IC |
| **Điện trở cắm (Axial R)** | **7.62 mm ($3 \times 2.54\text{ mm}$)** | Chuẩn lưới 2.54mm |
| **Kích thước Pad đồng** | **$1.4\text{ mm} \times 1.4\text{ mm}$** | Tròn / Oval cho độ bám thiếc tối ưu |
| **Đường kính lỗ khoan (Drill)** | **0.8 mm** | 3.2 mm cho 4 lỗ ốc cố định khung M3 |
| **Độ rộng dây Nguồn (Power)** | **1.4 mm** | Dòng tải cao cho 4 động cơ và Pi 4 |
| **Độ rộng dây Tín hiệu (Signal)** | **1.0 mm** | Chống đứt đường in khi gia công thủ công / phay |
| **Khoảng hở cách điện (Clearance)** | **$\ge 0.5\text{ mm}$** | Đảm bảo an toàn gia công, không lo chạm chập |
| **KiCad DRC Violations** | **0 lỗi (Zero DRC Errors)** | Đã qua kiểm tra DRC chính thức trên KiCad 10 |

---

## 2. BẢNG QUY HOẠCH CHÂN GPIO RASPBERRY PI 4 (IDC 40-PIN)

Tất cả tín hiệu được quy hoạch đối xứng để đi dây 1 lớp không chéo nhau:

### Khối Động cơ Trái (Driver `U_TB1` - `J_M1` & `J_M2`):
- **`PWMA_L`**: Pin 3 -> **BCM GPIO 2** (Điều khiển tốc độ PWM kênh A & B nối song song)
- **`AIN2_L`**: Pin 5 -> **BCM GPIO 3** (Điều khiển chiều quay AIN2 & BIN2)
- **`AIN1_L`**: Pin 7 -> **BCM GPIO 4** (Điều khiển chiều quay AIN1 & BIN1)
- **`STBY_L`**: Pin 11 -> **BCM GPIO 17** (Chân Standby bật/tắt driver công suất)

### Khối Động cơ Phải (Driver `U_TB2` - `J_M3` & `J_M4`):
- **`PWMA_R`**: Pin 33 -> **BCM GPIO 13** (PWM kênh A & B)
- **`AIN2_R`**: Pin 35 -> **BCM GPIO 19** (Chiều quay AIN2 & BIN2)
- **`AIN1_R`**: Pin 37 -> **BCM GPIO 26** (Chiều quay AIN1 & BIN1)
- **`STBY_R`**: Pin 38 -> **BCM GPIO 20** (Standby bật/tắt driver)

### Khối Cảm biến & Nguồn:
- **Cảm biến Siêu âm Trái (`U_US1`)**: TRIG -> Pin 13 (GPIO 27), ECHO -> Pin 15 (GPIO 22)
- **Cảm biến Siêu âm Phải (`U_US2`)**: TRIG -> Pin 29 (GPIO 5), ECHO -> Pin 31 (GPIO 6)
- **Cảm biến Dò Line 3 Kênh (`U_LINE`)**: Line Trái -> Pin 19 (GPIO 10), Line Giữa -> Pin 21 (GPIO 9), Line Phải -> Pin 23 (GPIO 11)
- **Nguồn cấp Pi 4**: Pin 2, 4 -> Nối trực tiếp nguồn **`+5V_PI`** từ mạch Buck XL4015 5A

---

## 3. CẤU TRÚC DỰ ÁN

```
.
├── code/                                # Mã nguồn phần mềm điều khiển
│   ├── python/                          # Chương trình Python CLI điều khiển động cơ
│   │   ├── config.py                    # Cấu hình chân GPIO phần cứng
│   │   ├── motor_controller.py          # Lớp điều khiển TB6612 (hỗ trợ Pi & PC simulation)
│   │   ├── test_left_motors.py          # Kịch bản kiểm tra tự động & thủ công 2 bánh trái
│   │   └── requirements.txt             # Thư viện phụ thuộc cho Raspberry Pi OS
│   ├── website/                         # Giao diện Web điều khiển từ xa qua WiFi
│   │   ├── index.html                   # Cyber-Dashboard điều khiển cảm ứng
│   │   ├── style.css                    # Dark mode, glassmorphism cao cấp
│   │   ├── app.js                       # Logic gửi lệnh API & bắt phím nóng bàn phím
│   │   └── server.py                    # HTTP & REST API Server tích hợp
│   └── README.md                        # Hướng dẫn chi tiết vận hành code
├── constraints/                         # Tài liệu ràng buộc thiết kế & topo mạch 1 lớp
├── gerbers/                             # Tệp Gerber & Khoan lỗ sẵn sàng gửi xưởng gia công
├── libraries/                           # Thư viện Footprint & Ký hiệu Schematic KiCad
├── Pi4_Robot_Carrier_1Layer.kicad_pcb   # File thiết kế PCB KiCad chính thức (Chuẩn 1 Lớp)
├── Pi4_Robot_Carrier_1Layer.kicad_sch   # File sơ đồ nguyên lý KiCad
├── Pi4_Robot_Carrier_1Layer.pdf         # Bản vẽ in ấn PCB chất lượng cao (PDF)
├── Pi4_Robot_Carrier_1Layer.svg         # Bản vẽ vector PCB (SVG)
├── Pi4_Robot_Carrier_BOM.html           # Bảng kê danh mục linh kiện (HTML tương tác)
├── Pi4_Robot_Carrier_BOM.csv            # Bảng kê linh kiện (CSV)
└── Pi4_Robot_Carrier_Schematic.pdf      # Sơ đồ nguyên lý xuất PDF
```

---

## 4. HƯỚNG DẪN CHẠY PHẦN MỀM

### A. Kiểm tra phần cứng bằng Python CLI
```bash
cd code/python
python test_left_motors.py
```
- Chọn `1`: Chạy kịch bản tự động kiểm tra tiến, lùi, phanh dừng và gia tốc mượt.
- Chọn `2`: Điều khiển thủ công bằng bàn phím (`W`: tiến, `S`: lùi, `B`: phanh, `Space`: dừng, `+`/`-`: tốc độ).

### B. Điều khiển trực tuyến qua Web Dashboard
```bash
cd code/website
python server.py
```
Truy cập qua trình duyệt:
- Trên máy tính: `http://localhost:8080`
- Trên điện thoại thông minh: `http://<IP_RASPBERRY_PI>:8080`
