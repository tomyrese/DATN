# QUY ĐỊNH THIẾT KẾ MẠCH & RÀNG BUỘC KẾT NỐI CHÂN (DRC & PLANAR ROUTING RULES)

## I. Quy định Bắt buộc về Hình học & Công nghệ PCB 1 Lớp
1. **Số lớp mạch:** Duy nhất **1 lớp đồng ở mặt dưới (`B.Cu`)**. Tuyệt đối không vẽ đường mạch trên `F.Cu`, không dùng Via đổi lớp.
2. **Kích thước Pad và Lỗ khoan (Pad & Drill Size):**
   - Toàn bộ chân linh kiện cắm (Header IDC 40P, Female Header TB6612FNG, Header XH2.54 4P, Điện trở, XL4015):
   - **Hole Size (Đường kính lỗ khoan):** `0.8 mm`
   - **Pad Size X / Y (Đường kính ngoài Pad đồng):** `1.8 mm`
   - *Hệ quả hình học quan trọng:* Với bước chân (Pitch) tiêu chuẩn `2.54 mm` và Pad Size `1.8 mm`, khe hở giữa 2 mép Pad liền kề là:
     $$2.54\text{ mm} - 1.8\text{ mm} = 0.74\text{ mm}$$
     Vì dây tín hiệu có bề rộng `1.0 mm` ($> 0.74\text{ mm}$), **TUYỆT ĐỐI KHÔNG ĐƯỢC ĐI DÂY GIỮA 2 CHÂN LINH KIỆN** (tuân thủ nghiêm ngặt cả về quy tắc thiết kế lẫn toán học vật lý).
3. **Độ rộng đường mạch (Track Width) & Khoảng cách (Clearance):**
   - **Dây nguồn (`12V_BAT`, `VM`, `5V_BUCK`, `3V3`, `GND`):** Thống nhất cố định **`1.5 mm`**.
   - **Dây tín hiệu (GPIO, PWM, TRIG, ECHO, SDA, SCK, AO1..BO2):** Thống nhất cố định **`1.0 mm`**.
   - **Khoảng cách an toàn giữa các dây đồng (Clearance):** Tối thiểu **`0.4 mm - 0.5 mm`**.
   - **Không phủ đồng (No Copper Pour / No Soldermask Resin):** Không tạo vùng phủ đồng tràn (`Zone Fill`), để mạch thoáng, rõ ràng từng đường nguồn và đường tín hiệu.
4. **Quy tắc Đi dây (Routing Geometry):**
   - **Không đi góc vuông ($90^\circ$):** Mọi góc rẽ phải bẻ góc **$45^\circ$** (mitred corners).
   - **Không chéo dây (Zero Crossovers):** Các tuyến dây được quy hoạch theo thứ tự chân tuyến tính từ IDC 40-Pin ra các module để chạy song song.
   - **Đi dây qua gầm điện trở (Resistor Underpass Allowed):** Sử dụng các điện trở cắm THT (footprint `Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal` có khoảng cách tâm 2 chân là `10.16 mm`). Khoảng trống giữa 2 mép pad của điện trở là:
     $$10.16\text{ mm} - 1.8\text{ mm} = 8.36\text{ mm}$$
     Khoảng trống `8.36 mm` này cho phép đi tối đa 2 đến 3 đường mạch (`1.0 mm` hoặc `1.5 mm`) xuyên qua giữa 2 chân điện trở một cách hợp lệ mà không vi phạm DRC!

---

## II. Giải pháp "Bất Khả Giao Cắt" (Zero-Crossover Planar Topology)
Làm thế nào để thoát các chân từ **Header IDC 40-Pin (2 hàng x 20 chân)** mà **không cần luồn dây vào giữa các chân 2.54mm**?

### 1. Bí quyết thoát dây ở IDC 40-Pin (`J_PI_IDC40`):
- Header IDC 40-Pin gồm **Hàng Lẻ (Odd Pins: 1, 3, 5... 39)** và **Hàng Chẵn (Even Pins: 2, 4, 6... 40)** cách nhau `2.54 mm`.
- Vì không được luồn dây `1.0 mm` xuyên qua khe `0.74 mm` giữa các chân cùng hàng, tất cả các chân ở **Hàng Lẻ** sẽ thoát dây thẳng sang **bên Trái**, và tất cả các chân ở **Hàng Chẵn** sẽ thoát dây thẳng sang **bên Phải**!
- **Phân bổ hoàn hảo trên IDC 40-Pin:**
  - **Cụm Bên Trái (Nối vào Hàng Lẻ - Odd Pins):**
    - `Pin 1 (3V3)` -> Đường nguồn 3.3V dọc sườn trái.
    - `Pin 3 (GPIO2 - SDA)` & `Pin 5 (GPIO3 - SCL)` -> Đi thẳng ra `J_OLED` (XH2.54 4-Pin).
    - `Pin 7 (GPIO4)` & `Pin 11 (GPIO17)` -> Đi thẳng ra `J_SONAR_L` (HC-SR04 Trước Trái).
    - `Pin 13 (GPIO27)` & `Pin 15 (GPIO22)` -> Đi thẳng ra `J_SONAR_R` (HC-SR04 Trước Phải).
    - `Pin 19 (GPIO10 - PWMA)`, `Pin 21 (GPIO9 - AIN2)`, `Pin 23 (GPIO11 - AIN1)`, `Pin 29 (GPIO5 - BIN1)`, `Pin 31 (GPIO6 - BIN2)`, `Pin 33 (GPIO13 - PWMB)`, `Pin 39 (GND)` -> Đi thẳng theo đúng thứ tự từ trên xuống dưới vào **Hàng Điều Khiển của `U_DRV_L` (TB6612FNG Trái)**! Không một sợi dây nào bị bắt chéo!
  - **Cụm Bên Phải (Nối vào Hàng Chẵn - Even Pins):**
    - `Pin 2, 4 (5V)` & `Pin 6 (GND)` -> Đối chiếu áp 5V / GND chung.
    - `Pin 16 (GPIO23 - PWMA)`, `Pin 18 (GPIO24 - AIN2)`, `Pin 22 (GPIO25 - AIN1)`, `Pin 24 (GPIO8 - BIN1)`, `Pin 26 (GPIO7 - BIN2)`, `Pin 32 (GPIO12 - PWMB)`, `Pin 34 (GND)` -> Đi thẳng theo đúng thứ tự từ trên xuống dưới vào **Hàng Điều Khiển của `U_DRV_R` (TB6612FNG Phải)**! Hoàn toàn song song 100%!

### 2. Bí quyết nối đầu ra TB6612FNG ra Header Động cơ (`J_MOT_L` & `J_MOT_R`):
- Hàng chân công suất của TB6612FNG có thứ tự tự nhiên: `VM`, `VCC`, `GND`, `AO1`, `AO2`, `BO2`, `BO1`, `GND`.
- Đặt Header XH2.54 4-Pin (`J_MOT_L` và `J_MOT_R`) nằm song song ngay bên ngoài hàng chân công suất, đối diện trực tiếp với 4 chân `AO1, AO2, BO2, BO1`.
- 4 đường mạch `1.0 mm` nối thẳng tắp (~5mm) từ `AO1, AO2, BO2, BO1` sang `Pin 1, 2, 3, 4` của XH2.54.

### 3. Bí quyết xử lý nút giao ở `J_OLED` và `HC-SR04`:
- Trên module OLED 1.3" thực tế, thứ tự chân là `1: VDD, 2: GND, 3: SCK, 4: SDA`. Trong khi trên Pi 4, `Pin 3` là `SDA` và `Pin 5` là `SCK`. Để `SDA` và `SCK` không chéo nhau hoặc để đường `GND`/`VCC` băng qua an toàn, ta đặt **1 điện trở Pull-up hoặc trở cầu `0Ω` (`R_JMP1` chuẩn THT P10.16mm)** nằm ngang trên đường đi để 1 đường tín hiệu chui hợp lệ qua gầm giữa 2 chân điện trở!
- Tương tự, tại `J_SONAR_L` và `J_SONAR_R`, cặp điện trở phân áp `R1 (1kΩ)` và `R2 (2kΩ)` vừa hạ áp `ECHO` từ 5V xuống 3.3V bảo vệ Pi 4, vừa làm cầu bắc qua đường `GND` / `5V_BUCK` (`1.5 mm`).
