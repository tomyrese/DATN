# SKILL: KiCAD 1-Layer Robotics Carrier PCB Automated Design (via KiCAD-MCP-Server)

## 1. Mục tiêu Skill (Objective)
Skill này hướng dẫn AI Agent (Antigravity) giao tiếp với `KiCAD-MCP-Server` (https://github.com/mixelpixx/KiCAD-MCP-Server) để tự động khởi tạo dự án, vẽ sơ đồ nguyên lý (Schematic) chia làm 4 khối chuẩn mực, thiết kế mạch in (PCB) 1 lớp (Single-Layer `B.Cu`) tối ưu hóa không giao cắt dây, chạy kiểm tra DRC/ERC tự động và thông báo kết quả hoàn tất.

## 2. Kiến trúc 4 Khối trên Schematic (4-Block Schematic Architecture)
Khi gọi công cụ tạo Schematic trên KiCAD-MCP-Server, bắt buộc phân vùng toạ độ bản vẽ A4 thành 4 khung (Graphical Boxes / Hierarchical Labels) rõ ràng:

1. **KHỐI NGUỒN (POWER BLOCK) [Góc Trên - Trái]:**
   - **Đầu vào Pin 3S2P (~12V):** Cổng Domino / Terminal Block 2 Pin (`J_BAT`: `12V_BAT`, `GND`).
   - **Module giảm áp XL4015 (`U_BUCK`):**
     - `IN+` nối `12V_BAT` (cấp trực tiếp ra nhánh `VM` của 2 module TB6612FNG).
     - `IN-` nối `GND` chung toàn mạch.
     - `OUT+` xuất áp `5V_BUCK`, `OUT-` nối `GND`.
   - **Đầu ra cấp nguồn Raspberry Pi 4 (`J_PWR_PI`):** Header/Pad xuất `5V_BUCK` và `GND` ra cáp USB Type-C cấp cho Pi 4. Ngoài ra `5V_BUCK` cấp nguồn `5V` cho 2 cảm biến HC-SR04. Logic `3V3` và `5V` có thể lấy/đối chiếu qua cổng IDC 40-pin nhưng đường công suất chính đi từ XL4015.

2. **KHỐI TÍN HIỆU (SIGNAL & SENSOR BLOCK) [Góc Dưới - Trái]:**
   - **2x Header XH2.54 4-Pin cho HC-SR04 (`J_SONAR_L` - Trước Trái, `J_SONAR_R` - Trước Phải):**
     - Sơ đồ chân chuẩn: `Pin 1: VCC (5V_BUCK)`, `Pin 2: TRIG`, `Pin 3: ECHO`, `Pin 4: GND`.
     - **Mạch phân áp bảo vệ GPIO Pi 4 (BẮT BUỘC đồng thời là cầu nhảy Jump 1 lớp):** Chân `ECHO` của HC-SR04 xuất mức 5V, trong khi GPIO Raspberry Pi 4 chỉ chịu tối đa 3.3V. Do đó mỗi đường `ECHO` đi qua cặp điện trở cắm THT 0.25W (`R1=1kΩ` nối tiếp từ `ECHO` vào `GPIO_ECHO`, `R2=2kΩ` kéo từ `GPIO_ECHO` xuống `GND`). Thân điện trở THT (khoảng cách chân 7.62mm hoặc 10.16mm) đồng thời đóng vai trò "cầu nhảy tự nhiên" cho phép đi 1 hoặc 2 đường mạch đồng 1mm xuyên qua giữa 2 chân trở!
   - **1x Header XH2.54 4-Pin cho Màn hình OLED 1.3" I2C (`J_OLED`):**
     - Sơ đồ chân theo đúng module thực tế: `Pin 1: VDD/VCC (3V3 hoặc 5V)`, `Pin 2: GND`, `Pin 3: SCK (GPIO3 / SCL1)`, `Pin 4: SDA (GPIO2 / SDA1)`.
   - *Lưu ý Camera Raspberry Pi:* Kết nối trực tiếp vào cổng CSI trên bo Raspberry Pi 4 bằng cáp FFC chuyên dụng, không đi qua mạch đồng PCB để bảo toàn trở kháng vi sai MIPI CSI-2.

3. **KHỐI ĐIỀU KHIỂN (CONTROL INTERFACE BLOCK) [Góc Trên - Phải]:**
   - **1x Header IDC 40-Pin 2.54mm (`J_PI_IDC40` - `Conn_02x20_Odd_Even`):**
     - Kết nối với Raspberry Pi 4 thông qua cáp bẹ IDC 40 Pin dài 20cm.
     - Quy hoạch các chân GPIO liền kề nhau trên cùng một phía của hàng rào IDC 40-pin để đường mạch thoát ra song song, tuyệt đối không bị chéo dây (Zero-Crossover Escape Routing).

4. **KHỐI CHẤP HÀNH (ACTUATOR & MOTOR DRIVER BLOCK) [Góc Dưới - Phải]:**
   - **2x Module TB6612FNG (`U_DRV_L` điều khiển 2 động cơ Trái, `U_DRV_R` điều khiển 2 động cơ Phải):**
     - Mỗi module gồm 2 hàng rào Pin Header Cái (Female Header) 1x8 chân (tổng 16 chân, khoảng cách 2 hàng 15.24mm / 600 mil):
       - Hàng điều khiển (Control Row - 8 pin): `PWMA`, `AIN2`, `AIN1`, `STBY`, `BIN1`, `BIN2`, `PWMB`, `GND`.
       - Hàng công suất (Power/Motor Row - 8 pin): `VM`, `VCC`, `GND`, `AO1`, `AO2`, `BO2`, `BO1`, `GND`.
     - Chân `STBY` của 2 module có thể nối vào GPIO điều khiển hoặc kéo lên `VCC (3.3V)` qua trở `R_STBY (10kΩ)` để luôn sẵn sàng cũng như tận dụng gầm trở làm cầu đi dây.
   - **2x Header XH2.54 4-Pin ra Động cơ (`J_MOT_L` cho 2 motor trái, `J_MOT_R` cho 2 motor phải):**
     - Đặt ngay sát bên cạnh hàng chân `AO1, AO2, BO2, BO1` của mỗi TB6612FNG.
     - Thứ tự chân 1-4: `Pin 1: AO1`, `Pin 2: AO2`, `Pin 3: BO2`, `Pin 4: BO1` -> Nối thẳng 1:1 song song tuyệt đối từ chân TB6612FNG sang Header XH2.54 4-Pin mà không cần vòng vèo!

## 3. Quy trình thực thi chuẩn trên KiCAD-MCP-Server (Execution Pipeline)
1. Khởi tạo Project mới: `create_project(project_name="Pi4_Robot_Carrier_1Layer")`
2. Thiết lập Netlist & Design Rules (theo file `design_rules.json` và `pinout_mapping.json`).
3. Đặt linh kiện lên Schematic theo 4 phân vùng toạ độ.
4. Sắp xếp vị trí linh kiện trên PCB (Placement Strategy) để đạt **0 giao cắt (Planar Graph Topology)**.
5. Đi dây tự động / bán tự động trên lớp `B.Cu` (Bottom Copper) với góc bẻ 45 độ, kiểm tra DRC.
