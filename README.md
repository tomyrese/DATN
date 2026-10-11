# HỆ THỐNG ROBOT TỰ HÀNH HỖ TRỢ TRUNG TÂM THƯƠNG MẠI (V2.0 ENTERPRISE)

Hệ thống robot tự hành phục vụ và hỗ trợ khách hàng, nhân viên và ban quản lý tại Trung Tâm Thương Mại (TTTM) trên nền tảng **Raspberry Pi 4 Model B (8GB RAM)**, kết hợp ứng dụng điều khiển web responsive thời gian thực đa vai trò (**React 18 + TypeScript + Vite**), cơ sở dữ liệu quan hệ chuẩn hóa (**SQLite v2 WAL Mode**), thị giác máy tính cổ điển (**OpenCV Classical Vision** - không dùng mô hình học sâu tải sẵn), định vị đồ thị không gian và điều hướng thông minh.

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG

```
+-----------------------------------------------------------------------------------------+
|                  GIAO DIỆN WEB ĐIỀU KHIỂN ĐA VAI TRÒ (REACT 18 + VITE)                  |
|  - Guest: Bản đồ TTTM, Tìm kiếm gian hàng, Khuyến mãi công khai, Hỏi đáp AI, Dẫn đường |
|  - Staff: Quản lý khuyến mãi theo gian hàng, Giao hàng nội bộ, Lái xe & Camera vé bảo vệ|
|  - Admin: Dashboard quản trị, Quản lý tài khoản/cửa hàng/bản đồ/tuyến tuần tra, E-Stop  |
+--------------------------------------------+--------------------------------------------+
                                             | REST (Bearer Session) & WebSocket (/ws/v1/control)
+--------------------------------------------v--------------------------------------------+
|                              RASPBERRY PI 4 RUNTIME BACKEND                             |
|                                                                                         |
|  [ FastApi / Uvicorn Server (Port 8765) ]                                               |
|  ├── Security & RBAC: Sessions, Scoped Store Access, bcrypt/PBKDF2, Audit Logger       |
|  ├── AI Concierge: OpenRouter + Defense Prompt Injection + Local Rule-based Fallback   |
|  └── Mall Services: Stores, Promotions, POI, Graph Routing, Escort & Delivery Queue     |
|                                                                                         |
|  [ Autonomous Navigation & Safety Engine ]                                              |
|  ├── Topological Graph: Node-Edge Network, A* Planner, Dynamic Edge Blocking           |
|  ├── Odometry: Dead-Reckoning (V_linear, Omega), Runge-Kutta, Confidence Decay Metric   |
|  ├── Patrol Engine: Tự động tuần tra sau 5 phút nhàn rỗi, ngắt ưu tiên bởi Escort/Task  |
|  ├── Obstacle Avoidance: State Machine 8 trạng thái (CLEAR -> DETECTED -> AVOIDING...)  |
|  └── Multi-Tier Safety Controller: E-Stop vật lý/phần mềm, Ultrasonic (<25cm), Watchdog|
|                                                                                         |
|  [ Hardware Abstraction Layer & Classical Vision ]                                      |
|  ├── CameraService: CSI OV5647 Single Source, Shared Frame Buffer                       |
|  ├── PersonDetector: Classical OpenCV (MOG2 Background Subtraction + Dalal-Triggs HOG)  |
|  ├── UltrasonicSensors: 2x HC-SR04 (Trig/Echo 3.3V Protected), Median Filter            |
|  ├── MotorController: 4x DC Motors via 2x TB6612FNG (Hardware PWM + Coast/Brake)       |
|  └── OLEDController: 1.3" I2C SH1106 / SSD1306 (QR Code pairing & IP status)           |
+--------------------------------------------+--------------------------------------------+
                                             | SQLite Foreign Key Transactions
+--------------------------------------------v--------------------------------------------+
|                    PERSISTENCE LAYER (data/mall_delivery.db)                            |
|  19 bảng chuẩn hóa: users, roles, staff_store_assignments, stores, mall_floors,        |
|  map_nodes, map_edges, restricted_zones, patrol_routes, promotions, delivery_orders...  |
+-----------------------------------------------------------------------------------------+
```

---

## 2. TÍNH NĂNG NỔI BẬT ĐÃ TRIỂN KHAI

### 2.1. Phân quyền chặt chẽ 3 vai trò (RBAC)
1. **Khách tham quan (Guest - Công khai):**
   - Không cần đăng nhập.
   - Xem bản đồ TTTM theo tầng, tra cứu thông tin gian hàng và tiện ích (WC, thang máy).
   - Xem danh sách khuyến mãi đang diễn ra.
   - Hỏi đáp trợ lý AI Concierge về vị trí, giờ mở cửa, Wi-Fi.
   - Yêu cầu robot dẫn đường (Escort Mission) đến gian hàng mong muốn.
   - **Bảo mật:** Không xem được camera trực tiếp, không có quyền điều khiển động cơ, không truy cập đơn giao hàng nội bộ.
2. **Nhân viên gian hàng (Staff - Đăng nhập):**
   - Đăng nhập bằng tài khoản được cấp.
   - Xem camera trực tiếp qua cơ chế **Camera Stream Ticket** (thời hạn 30s).
   - Điều khiển xe thủ công (D-Pad / Bàn phím WASD) với cơ chế an toàn **Press-and-Hold Lease (350ms)**.
   - Quản lý khuyến mãi **chỉ áp dụng cho gian hàng được phân công** (`staff_store_assignments`).
   - Theo dõi và điều phối đơn giao hàng nội bộ liên quan đến gian hàng.
3. **Quản trị viên (Admin - Toàn quyền):**
   - Quản lý người dùng, tạo tài khoản Staff và phân công quản lý cửa hàng.
   - Quản lý danh mục cửa hàng, tầng, POI, node bản đồ và vùng cấm di chuyển.
   - Quản lý và kích hoạt tuyến tuần tra (Patrol Route).
   - Kích hoạt Dừng khẩn cấp toàn hệ thống (E-Stop) và Reset khi an toàn.
   - Xem nhật ký kiểm toán hệ thống (`audit_logs`) và sao lưu cơ sở dữ liệu (`/api/v1/admin/backup-db`).

### 2.2. Thị giác máy tính cổ điển (OpenCV Classical Vision)
- **Không dùng mô hình AI tiền huấn luyện:** Loại bỏ hoàn toàn sự phụ thuộc vào SSD MobileNet V2 hay model `.tflite`.
- **Pipeline xử lý ảnh cổ điển:**
  - Tiền xử lý: Resize `480x360`, làm mờ Gaussian.
  - Phân tách chuyển động: Background Subtraction MOG2 (`detectShadows=True`).
  - Lọc hình thái học Morphology (`cv2.MORPH_OPEN` & `CLOSE`) loại bỏ nhiễu rung lắc.
  - Bộ phân loại HOG + SVM người đi bộ chuẩn mực (Dalal-Triggs `HOGDescriptor_getDefaultPeopleDetector()`).
  - Hạn chế vùng quan tâm (ROI) và ước lượng độ tin cậy kết hợp cảm biến siêu âm.
  - Độ trễ xử lý cực thấp: ~9.3 ms/frame, tối ưu hóa triệt để cho CPU Raspberry Pi 4.

### 2.3. Cảm biến siêu âm & Máy trạng thái tránh vật cản (FSM)
- Tích hợp 2 cảm biến siêu âm **HC-SR04** (Trái/Phải).
- **Mạch bảo vệ 5V -> 3.3V:** Chân Echo HC-SR04 bắt buộc đi qua cầu phân áp 1kΩ / 2kΩ để bảo vệ GPIO Raspberry Pi 4.
- Lọc trung vị (Median Filter) 3 mẫu liên tiếp loại bỏ nhiễu phản xạ sóng âm.
- Máy trạng thái tránh vật cản 8 bước:
  `CLEAR` -> `OBSTACLE_DETECTED` -> `SLOWING_DOWN` (<50cm) -> `STOPPED_FOR_OBSTACLE` (<25cm) -> `AVOIDING` -> `REJOINING_ROUTE` -> `BLOCKED` -> `EMERGENCY_STOP`.

### 2.4. Bản đồ đồ thị, Ước lượng quãng đường & Tuần tra tự động
- Đồ thị không gian 2D với các Node và Edge có trọng số khoảng cách thực tế (mét).
- Thuật toán tìm đường ngắn nhất **A* (A-Star)** với khả năng chặn cạnh động khi có vật cản.
- **Ước lượng quãng đường (Dead-Reckoning Odometry):**
  - Động cơ DC không có encoder: Tích phân vận tốc tuyến tính ($v$) và vận tốc góc ($\omega$) theo thời gian điều khiển qua xấp xỉ Runge-Kutta bậc 2.
  - **Tính trung thực dữ liệu:** Hệ số độ tin cậy (`confidence`) tự động suy giảm theo quãng đường ($0.05/\text{m}$) và thời gian ($0.005/\text{s}$). Giao diện gắn nhãn rõ ràng `[SIMULATED DEAD-RECKONING]`.
- **Tự động tuần tra sau 5 phút:** Nếu robot ở trạng thái nhàn rỗi (`IDLE`) trong 300 giây, hệ thống tự động kích hoạt tuần tra qua các điểm Waypoint định sẵn. Khi có yêu cầu dẫn đường khách hàng, robot dừng an toàn và nhường quyền ưu tiên lập tức.

### 2.5. Trợ lý AI Concierge OpenRouter & Ngăn chặn Prompt Injection
- Tích hợp OpenRouter backend, bảo mật API key qua biến môi trường `OPENROUTER_API_KEY`.
- Tách biệt chỉ thị hệ thống (`System Prompt`) và dữ liệu đầu vào người dùng; lọc các từ khóa chèn lệnh độc hại.
- Rút trích ngữ cảnh từ cơ sở dữ liệu (`context_retriever.py`): Giờ mở cửa, vị trí, Wi-Fi, khuyến mãi thực tế.
- Tự động chuyển sang bộ quy tắc luật Tiếng Việt nội bộ khi không có API key hoặc mạng Internet bị ngắt.

---

## 3. CẤU HÌNH PHẦN CỨNG & SƠ ĐỒ ĐẤU DÂY

Chi tiết sơ đồ chân, cảnh báo điện áp và kết nối: xem tại [docs/HARDWARE_SETUP.md](file:///d:/Study/KLTN/Code/docs/HARDWARE_SETUP.md).

### Tóm tắt chân GPIO Raspberry Pi 4 Model B:
- **TB6612FNG Cụm Trái (Motor 1 & 2):**
  `PWMA=GPIO 13`, `AIN1=GPIO 5`, `AIN2=GPIO 6`, `PWMB=GPIO 19`, `BIN1=GPIO 26`, `BIN2=GPIO 22`, `STBY=GPIO 27`.
- **TB6612FNG Cụm Phải (Motor 3 & 4):**
  `PWMA=GPIO 12`, `AIN1=GPIO 16`, `AIN2=GPIO 20`, `PWMB=GPIO 18`, `BIN1=GPIO 23`, `BIN2=GPIO 24`, `STBY=GPIO 21`.
- **Cảm biến siêu âm HC-SR04:**
  - HC-SR04 Trái: `TRIG=GPIO 25`, `ECHO=GPIO 8` *(Qua cầu trở 1kΩ/2kΩ xuống 3.3V)*.
  - HC-SR04 Phải: `TRIG=GPIO 7`, `ECHO=GPIO 1` *(Qua cầu trở 1kΩ/2kΩ xuống 3.3V)*.
- **Màn hình OLED 1.3" I2C:**
  `SDA=GPIO 2`, `SCL=GPIO 3`, `VCC=3.3V`, `GND=GND`.
- **Camera CSI:** Cáp Ribbon 15-pin cắm vào cổng CSI Raspberry Pi 4.

---

## 4. HƯỚNG DẪN KHỞI CHẠY (QUICK START)

### 4.1. Chế độ Mô phỏng trên Máy tính (PC / Simulation Mode)

1. **Cài đặt môi trường Python (Python 3.10+):**
   ```bash
   pip install -r requirements.txt
   ```
2. **Tạo file cấu hình môi trường:**
   ```bash
   copy .env.example .env
   ```
3. **Khởi tạo và Seed cơ sở dữ liệu:**
   ```bash
   python -m src.database.migrator
   python -m src.database.seed
   ```
4. **Build Frontend Web App:**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```
5. **Chạy Backend Server:**
   ```bash
   python src/main.py
   ```
   *Truy cập Web Dashboard tại:* `http://localhost:8765`

### 4.2. Tài khoản thử nghiệm (Test Accounts):
- **Admin:** `admin` / Mật khẩu: `Admin@123456` (Toàn quyền quản trị).
- **Staff ZARA:** `staff_zara` / Mật khẩu: `Staff@123456` (Chỉ quản lý ZARA).
- **Staff UNIQLO:** `staff_uniqlo` / Mật khẩu: `Staff@123456` (Chỉ quản lý UNIQLO).
- **Khách hàng (Guest):** Không cần đăng nhập, sử dụng trực tiếp trên giao diện.

---

## 5. BỘ TÀI LIỆU KỸ THUẬT CHI TIẾT

| STT | Tài liệu | Nội dung chính |
| :---: | :--- | :--- |
| 1 | [ARCHITECTURE.md](file:///d:/Study/KLTN/Code/docs/ARCHITECTURE.md) | Kiến trúc tổng thể 12 lớp, luồng dữ liệu thời gian thực |
| 2 | [DATABASE_SCHEMA.md](file:///d:/Study/KLTN/Code/docs/DATABASE_SCHEMA.md) | Sơ đồ ERD, 19 bảng SQLite, khóa chính/ngoại, index, migration |
| 3 | [PROTOCOL.md](file:///d:/Study/KLTN/Code/docs/PROTOCOL.md) | Đặc tả 18 REST APIs và giao thức WebSocket nhị phân/JSON |
| 4 | [REMOTE_CONNECTION.md](file:///d:/Study/KLTN/Code/docs/REMOTE_CONNECTION.md) | Hướng dẫn kết nối từ xa qua Cloudflare Tunnel không cần mở Port |
| 5 | [HARDWARE_SETUP.md](file:///d:/Study/KLTN/Code/docs/HARDWARE_SETUP.md) | Sơ đồ đấu dây chi tiết, bảo vệ điện áp 5V->3.3V, mạch cấp nguồn |
| 6 | [AUTONOMOUS_NAVIGATION.md](file:///d:/Study/KLTN/Code/docs/AUTONOMOUS_NAVIGATION.md) | Đồ thị bản đồ, thuật toán A*, Odometry dead-reckoning, tuần tra 5p |
| 7 | [VISION_AND_SAFETY.md](file:///d:/Study/KLTN/Code/docs/VISION_AND_SAFETY.md) | OpenCV cổ điển (MOG2 + HOG/SVM), FSM tránh vật cản, benchmarks |
| 8 | [SECURITY.md](file:///d:/Study/KLTN/Code/docs/SECURITY.md) | Xác thực Session, phân quyền RBAC, bảo vệ OpenRouter, Audit Log |
| 9 | [DEPLOYMENT_RASPBERRY_PI.md](file:///d:/Study/KLTN/Code/docs/DEPLOYMENT_RASPBERRY_PI.md) | Triển khai systemd, cấu hình khởi động cùng hệ thống trên Pi 4 |
| 10 | [SIMULATION_AND_TESTING.md](file:///d:/Study/KLTN/Code/docs/SIMULATION_AND_TESTING.md) | Hướng dẫn chạy test suite tự động và mô phỏng cảm biến trên PC |
| 11 | [MIGRATION_REPORT.md](file:///d:/Study/KLTN/Code/docs/MIGRATION_REPORT.md) | Báo cáo chuyển đổi dữ liệu, kiểm tra tương thích ngược và rollback |

---

## 6. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG

Dự án sở hữu bộ kiểm thử tự động toàn diện với **53/53 test cases thành công (100% Pass Rate)**:
```bash
python -m pytest tests/ -v
# 53 passed, 1 warning in 11.34s
```
Bao gồm:
- Kiểm thử phân quyền RBAC, kiểm tra rò rỉ dữ liệu giữa các gian hàng.
- Kiểm thử thuật toán tìm đường A* và chặn cạnh động.
- Kiểm thử suy giảm độ tin cậy của thuật toán Odometry.
- Kiểm thử chu trình tuần tra tự động 5 phút và cơ chế ngắt ưu tiên.
- Kiểm thử thị giác máy tính OpenCV cổ điển và tính toán ma trận tương quan.
- Kiểm thử máy trạng thái tránh vật cản siêu âm HC-SR04.
