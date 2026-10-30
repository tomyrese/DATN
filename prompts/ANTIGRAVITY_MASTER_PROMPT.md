# PROMPT CHI TIẾT DÀNH CHO ANTIGRAVITY (KICAD-MCP-SERVER AUTOMATION)

Hãy copy toàn bộ nội dung bên dưới và gửi cho **Antigravity** sau khi đã giải nén thư mục này vào workspace của dự án:

---

```markdown
@antigravity Tôi cần bạn đóng vai trò là Kỹ sư Thiết kế Vi mạch & PCB Tự động, sử dụng công cụ **KiCAD-MCP-Server** (`https://github.com/mixelpixx/KiCAD-MCP-Server`) để thiết kế hoàn chỉnh từ A-Z bộ **Schematic (4 khối)** và **PCB 1 Lớp (Single-Layer Compact Board)** cho hệ thống Robot tự hành dùng Raspberry Pi 4.

### BƯỚC 1: ĐỌC HIỂU TÀI LIỆU & SKILL TRONG WORKSPACE
Trước khi gọi bất kỳ tool nào của KiCAD-MCP-Server, hãy đọc toàn bộ các file cấu hình đã được chuẩn bị sẵn trong thư mục giải nén:
1. `skills/SKILL.md`: Quy trình thực thi và cấu trúc 4 khối chức năng.
2. `constraints/design_rules.json`: Thông số kỹ thuật bắt buộc của PCB (Pad, Hole, Track Width, Clearance).
3. `constraints/pinout_mapping.json`: Bảng ánh xạ chân tuyệt đối không giao cắt (Zero-Crossover Planar Pinout).
4. `constraints/CONSTRAINTS_AND_TOPOLOGY.md`: Giải pháp bố trí linh kiện hình học phẳng và tận dụng gầm điện trở THT (P10.16mm).
5. `scripts/verify_pcb_drc.py`: Kịch bản Python kiểm thử tự động toàn bộ ràng buộc sau khi thiết kế xong.

---

### BƯỚC 2: THIẾT KẾ SCHEMATIC CHIA THÀNH 4 KHỐI RÕ RÀNG
Hãy gọi các MCP tools của KiCAD để tạo Schematic `Pi4_Robot_Carrier_1Layer.kicad_sch` và vẽ khung phân chia rõ ràng thành **4 KHỐI**:

1. **KHỐI 1 - KHỐI NGUỒN (POWER BLOCK):**
   - Nguồn vào từ Pin `3S2P (~12V)` qua Domino 2-Pin (`J_BAT`: `IN+`, `IN-`).
   - Nhánh trước giảm áp (`12V_BAT`) cấp trực tiếp cho chân `VM` của 2 module `TB6612FNG`.
   - Module giảm áp `XL4015` (`U_BUCK`) có 4 chân (`IN+`, `IN-`, `OUT+`, `OUT-`). Hạ áp từ `12V_BAT` xuống `5V_BUCK` tại `OUT+`, `OUT-`.
   - Đầu ra `5V_BUCK` và `GND` đưa ra cổng cấp nguồn Type-C (`J_PWR_PI`) để nuôi Raspberry Pi 4 và cấp `VCC (5V)` cho 2 cảm biến `HC-SR04`.
   - Toàn bộ `GND` (Pin 3S2P `IN-`, XL4015 `OUT-`, Pi 4 `GND`, TB6612FNG `GND`, HC-SR04 `GND`, OLED `GND`) phải **nối chung 1 mạng `GND` duy nhất**.

2. **KHỐI 2 - KHỐI TÍN HIỆU (SIGNAL BLOCK):**
   - **2x Header XH2.54 4-Pin** (`J_SONAR_L` - Trước Trái, `J_SONAR_R` - Trước Phải) cho 2 cảm biến siêu âm HC-SR04 với thứ tự chân: `1: VCC (5V_BUCK)`, `2: TRIG`, `3: ECHO`, `4: GND`.
   - Tích hợp cặp điện trở cắm THT (`1kΩ` + `2kΩ`, bước chân `10.16mm`) trên mỗi đường `ECHO` để vừa chia áp 5V -> 3.3V bảo vệ GPIO Pi 4, vừa đóng vai trò làm cầu nhảy hợp lệ cho đường mạch đi qua giữa 2 chân trở.
   - **1x Header XH2.54 4-Pin** (`J_OLED`) cho màn hình OLED 1.3" với thứ tự chân: `1: VCC/VDD (3V3)`, `2: GND`, `3: SCK (GPIO3/Pin 5)`, `4: SDA (GPIO2/Pin 3)`.
   - Ghi chú kỹ thuật trên Schematic: *Module Camera Raspberry Pi kết nối trực tiếp vào cổng CSI trên bo Raspberry Pi 4 bằng cáp FFC để đảm bảo toàn vẹn tín hiệu vi sai tốc độ cao.*

3. **KHỐI 3 - KHỐI ĐIỀU KHIỂN (CONTROL BLOCK):**
   - **1x Header IDC 40-Pin 2.54mm** (`J_PI_IDC40`) kết nối với Raspberry Pi 4 qua cáp bẹ IDC 40-Pin dài 20cm.
   - Gán Netlist chính xác theo file `constraints/pinout_mapping.json`:
     - Hàng Lẻ (Odd Pins 1..39): Cấp tín hiệu cho `J_OLED`, `J_SONAR_L`, `J_SONAR_R` và `U_DRV_L` (TB6612FNG Trái).
     - Hàng Chẵn (Even Pins 2..40): Cấp tín hiệu cho `U_DRV_R` (TB6612FNG Phải) và đối chiếu GND.

4. **KHỐI 4 - KHỐI CHẤP HÀNH (ACTUATOR BLOCK):**
   - **2x Module TB6612FNG** (`U_DRV_L` - 2 động cơ Trái, `U_DRV_R` - 2 động cơ Phải), mỗi module có 16 chân chia làm 2 hàng 1x8 (`VM, VCC, GND, AO1, AO2, BO2, BO1, GND` và `PWMA, AIN2, AIN1, STBY, BIN1, BIN2, PWMB, GND`). Chân `STBY` kéo lên `3V3` qua điện trở `10kΩ` (THT P10.16mm).
   - **2x Header XH2.54 4-Pin** (`J_MOT_L`, `J_MOT_R`) kết nối trực tiếp 4 chân đầu ra động cơ `AO1, AO2, BO2, BO1` của mỗi TB6612FNG.

---

### BƯỚC 3: THIẾT KẾ PCB 1 LỚP & ÁP DỤNG NGHIÊM NGẶT QUY ĐỊNH DRC
Sử dụng các công cụ PCB của `KiCAD-MCP-Server` để dàn trang (Placement) và đi dây (Routing) trên file `Pi4_Robot_Carrier_1Layer.kicad_pcb` theo đúng các ràng buộc bất di bất dịch sau:

1. **Thông số Pad & Hole (Bắt buộc cho toàn bộ chân cắm THT):**
   - `Hole Size (Drill)` = **`0.8 mm`**
   - `Pad Size X = Pad Size Y` = **`1.8 mm`**
2. **Thông số Đường mạch (Track Width) & Lớp đồng:**
   - Chỉ đi dây trên **1 lớp duy nhất (`B.Cu`)**.
   - **Dây nguồn (`12V_BAT`, `VM`, `5V_BUCK`, `3V3`, `GND`):** Độ rộng thống nhất = **`1.5 mm`**.
   - **Dây tín hiệu (GPIO, PWM, I2C, Sonar, Motor Out):** Độ rộng thống nhất = **`1.0 mm`**.
   - Khoảng cách an toàn giữa các dây đồng (`Clearance`): Tối thiểu **`0.4 mm - 0.5 mm`**.
   - **KHÔNG phủ đồng (No Copper Pour / No Zone Fill)**.
3. **Quy tắc Hình học Đi dây:**
   - **TUYỆT ĐỐI KHÔNG đi dây giữa 2 chân linh kiện** (không luồn dây qua khe 2.54mm của IDC 40-pin, TB6612FNG hay XH2.54).
   - **ĐƯỢC PHÉP đi dây xuyên qua giữa 2 chân của Điện trở cắm** (sử dụng footprint điện trở có Pitch `10.16mm`, khe hở thực tế `8.36mm` đủ rộng cho dây `1.0mm` và `1.5mm` đi qua).
   - **TUYỆT ĐỐI KHÔNG để dây này chéo dây kia** (0 Via, 0 пересечений).
   - **TUYỆT ĐỐI KHÔNG đi dây góc vuông ($90^\circ$)** — tất cả các góc bẻ phải là **$45^\circ$**.
   - **Bố cục nhỏ gọn (Compact Layout ~ 85mm x 65mm):**
     - Đặt `J_PI_IDC40` ở trung tâm phía Bắc.
     - Đặt `U_DRV_L` và `J_MOT_L` ở sườn Tây Nam; `U_DRV_R` và `J_MOT_R` ở sườn Đông Nam (hàng chân điều khiển quay vào trong hướng về IDC 40-Pin, hàng chân công suất `AO1..BO1` quay ra mép ngoài nối thẳng sang `J_MOT_L` / `J_MOT_R`).
     - Đặt `J_OLED`, `J_SONAR_L`, `J_SONAR_R` ở cụm Tây Bắc.
     - Đặt khối nguồn `XL4015` (`U_BUCK`), `J_BAT`, `J_PWR_PI` ở sườn Nam, chạy đường Bus nguồn `12V_BAT` (`1.5mm`), `5V_BUCK` (`1.5mm`) và `GND` (`1.5mm`) bao quanh chu vi ngoài cùng của bo mạch.

---

### BƯỚC 4: TỰ ĐỘNG CHẠY KIỂM THỬ (AUTO-VERIFICATION) & BÁO CÁO
1. Sau khi hoàn tất thiết kế Schematic và PCB thông qua `KiCAD-MCP-Server`, hãy chạy công cụ kiểm tra DRC tích hợp của MCP Server VÀ thực thi script kiểm thử độc lập:
   `python3 scripts/verify_pcb_drc.py Pi4_Robot_Carrier_1Layer.kicad_pcb`
2. Nếu phát hiện bất kỳ lỗi nào (ví dụ: còn đoạn dây góc $90^\circ$, pad khác `1.8mm`, hole khác `0.8mm`, dây nguồn khác `1.5mm`, dây tín hiệu khác `1.0mm`, hoặc còn `Unrouted Nets`), hãy tự động điều chỉnh lại toạ độ track ngay trên MCP Server cho đến khi đạt **PASS 100% (0 DRC Errors, 0 Unrouted Nets)**.
3. Xuất file Gerber / PDF xem trước (nếu MCP hỗ trợ) và **thông báo kết quả hoàn tất chi tiết cho tôi**.
```
