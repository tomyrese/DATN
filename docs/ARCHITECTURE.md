# KIẾN TRÚC HỆ THỐNG ROBOT TỰ HÀNH TRUNG TÂM THƯƠNG MẠI (V2.0 ENTERPRISE)

Tài liệu thiết kế kiến trúc toàn diện của Robot Trung Tâm Thương Mại trên nền tảng **Raspberry Pi 4 Model B (8GB RAM)**, bao gồm 12 tầng trách nhiệm phân lập rõ ràng, không phụ thuộc mô hình deep learning huấn luyện sẵn, tích hợp phân quyền RBAC và an toàn đa lớp.

---

## 1. SƠ ĐỒ KHỐI KIẾN TRÚC 12 TẦNG (12-LAYER ARCHITECTURE)

```
+---------------------------------------------------------------------------------------------------+
| [12] TẦNG GIAO DIỆN NGƯỜI DÙNG (FRONTEND LAYER - REACT 18 + TYPESCRIPT + VITE)                    |
| - Guest: Bản đồ tương tác, Tìm kiếm cửa hàng, Khuyến mãi công khai, AI Concierge, Yêu cầu dẫn đường|
| - Staff: Dashboard gian hàng, Quản lý khuyến mãi scoped, Đơn giao hàng, Lái xe & Camera vé 30s    |
| - Admin: Quản trị tài khoản, Sơ đồ đồ thị & Waypoint tuần tra, E-Stop toàn cục, Audit log, Backup  |
+-------------------------------------------------+-------------------------------------------------+
                                                  | REST (Bearer Session) / WebSocket (/ws/v1/control)
+-------------------------------------------------v-------------------------------------------------+
| [7] TẦNG GIAO TIẾP VÀ MẠNG (API & NETWORK LAYER)                                                  |
| - FastAPI HTTP Server (Port 8765): 18 REST endpoints (Auth, Stores, Promotions, Escort, Admin)     |
| - WebSocketManager: Xác thực kết nối, Broadcast Telemetry (2-5Hz), Heartbeat (1.2s), Lease (350ms)|
| - CameraStreamManager: MJPEG Streaming được bảo vệ bởi Ticket truy cập có thời hạn 30s            |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
+-------------------------------------------------v-------------------------------------------------+
| [8] TẦNG XÁC THỰC VÀ PHÂN QUYỀN (AUTHENTICATION & AUTHORIZATION LAYER)                            |
| - AuthService: Quản lý phiên Session UUID, Argon2id/bcrypt mã hóa mật khẩu, Audit log kiểm toán   |
| - RBAC Dependencies: require_admin, require_staff_or_admin, check_store_access (Scoped Store RBAC) |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
+-------------------------------------------------v-------------------------------------------------+
| [9] TẦNG NGHIỆP VỤ TRUNG TÂM THƯƠNG MẠI (MALL BUSINESS LAYER)                                     |
| - MallService: Quản lý Cửa hàng, Tầng, POI, Khuyến mãi (RBAC scoped), FAQ, Hàng đợi giao hàng FIFO|
| - EscortService: Điều phối nhiệm vụ dẫn đường khách tham quan và chuyển giao trạng thái           |
+----------------------------------------+--------+----------------------------------------+
                                         |                                                 |
+----------------------------------------v--------+       +--------------------------------v--------+
| [10] TẦNG TÍCH HỢP AI (AI INTEGRATION LAYER)    |       | [6] TẦNG ĐIỀU PHỐI ROBOT (SERVICE LAYER)|
| - ContextRetriever: Rút trích dữ liệu tối thiểu |       | - RobotController: Máy trạng thái tổng  |
| - OpenRouterClient: LLM an toàn, prompt defense |       | - TaskPriority: E-Stop > Escort > Patrol|
| - Local Rule-based Fallback (Tiếng Việt offline)|       | - ConnectionWatchdog & TelemetryService |
+-------------------------------------------------+       +-------------------+---------------------+
                                                                              |
+-----------------------------------------------------------------------------v---------------------+
| [4] TẦNG ĐIỀU HƯỚNG TỰ HÀNH (NAVIGATION LAYER)                                                    |
| - MapGraph: Mạng lưới Node/Edge 2D, trọng số mét thực tế, hỗ trợ chặn cạnh động khi có chướng ngại|
| - AStarPlanner: Thuật toán tìm đường ngắn nhất tối ưu                                             |
| - PatrolController: Tự động kích hoạt tuần tra sau 5 phút nhàn rỗi, ngắt ưu tiên bởi Escort/Task   |
| - Navigator: Điều phối hành trình, giám sát đường dự kiến (planned) vs đường thực tế (executed)   |
+---------------------------------------------------+-----------------------------------------------+
                                                    |
+---------------------------------------------------v-----------------------------------------------+
| [3] TẦNG ĐỊNH VỊ VÀ ĐO QUÃNG ĐƯỜNG (LOCALIZATION LAYER)                                           |
| - DeadReckoningOdometry: Tích phân v và w (Runge-Kutta bậc 2) dựa trên vận tốc mô tơ TB6612     |
| - Confidence Decay Metric: Tự động giảm độ tin cậy theo quãng đường và thời gian (không có encoder)|
| - Gắn nhãn trung thực dữ liệu: [SIMULATED DEAD-RECKONING] và is_estimated: True                   |
+---------------------------------------------------+-----------------------------------------------+
                                                    |
+---------------------------------------------------v-----------------------------------------------+
| [5] TẦNG AN TOÀN ĐA LỚP (SAFETY LAYER)                                                            |
| - SafetyController: Phân cấp ưu tiên tuyệt đối (E-Stop > Ultrasonic <25cm > Person > Slow <50cm)  |
| - CameraWatchdog, SystemWatchdog, ConnectionWatchdog                                              |
| - Hardware E-Stop Standby Cutoff (STBY_L / STBY_R = LOW)                                          |
+----------------------------------------+----------------------------------------+
                                         |                                        |
+----------------------------------------v--------+      +------------------------v-----------------+
| [2] TẦNG TRI GIÁC (PERCEPTION LAYER)            |      | [1] TẦNG TRỪU TƯỢNG PHẦN CỨNG (HAL)      |
| - PersonDetector: OpenCV Cổ Điển MOG2 Background|      | - MotorController: 4x DC Motors TB6612FNG|
|   Subtraction + Dalal-Triggs HOG/SVM Người đi bộ|      | - UltrasonicSensors: 2x HC-SR04 (3.3V)   |
| - ObstacleAvoidanceController: FSM 8 trạng thái |      | - CameraService: CSI OV5647 Picamera2    |
|   (CLEAR, DETECTED, SLOWING, STOPPED, AVOIDING..|      | - OLEDController: 1.3" I2C SH1106        |
+-------------------------------------------------+      +------------------------------------------+
                                         |
+----------------------------------------v----------------------------------------------------------+
| [11] TẦNG LƯU TRỮ VÀ TOÀN VẸN DỮ LIỆU (PERSISTENCE LAYER - SQLITE V2 WAL MODE)                    |
| - 19 bảng chuẩn hóa với Khóa chính, Khóa ngoại, Ràng buộc Unique/Check, Index tối ưu              |
| - Migrator với cơ chế sao lưu tự động trước khi di chuyển dữ liệu (.backup_<timestamp>)           |
| - Ghi log kiểm toán thao tác bảo mật (audit_logs)                                                 |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. NGUYÊN TẮC QUẢN LÝ TÀI NGUYÊN CAMERA CSI DUY NHẤT

Phần cứng Camera CSI trên Raspberry Pi 4 Model B chỉ cho phép mở một tiến trình camera độc quyền (`exclusive device access`):
1. **`CameraService`** là lớp duy nhất tương tác trực tiếp với phần cứng driver `Picamera2` / `libcamera`.
2. Luồng Capture chạy ngầm liên tục đưa frame hình ảnh RGB thô vào buffer chia sẻ trong RAM (Ring Buffer với cờ khóa luồng `threading.Lock`).
3. **`PersonDetector`** đọc frame từ buffer RAM với tần số 10 FPS để chạy thuật toán OpenCV cổ điển (MOG2 + Morphology + HOG/SVM), không gây nghẽn phần cứng camera.
4. **`CameraStreamManager`** lấy cùng frame từ buffer để nén ảnh JPEG và phân phối luồng MJPEG thời gian thực cho nhân viên và admin có Ticket hợp lệ.
5. Khi không có phần cứng CSI thật (ví dụ chạy trên máy tính phát triển), `CameraService` tự động chuyển sang chế độ mô phỏng hình ảnh thử nghiệm (`SIMULATED_TEST_PATTERN`) có nhãn nhận diện rõ ràng.

---

## 3. THỨ TỰ ƯU TIÊN AN TOÀN TUYỆT ĐỐI (SAFETY HIERARCHY)

Mọi lệnh điều khiển vận động từ bất kỳ nguồn nào (Tự hành, Tuần tra, Lái xe thủ công Web) đều bắt buộc đi qua `SafetyController` theo thứ bậc ưu tiên cố định:

```
[1] EMERGENCY_STOP          (Nút dừng khẩn cấp trên UI hoặc công tắc vật lý - Cắt STBY ngay lập tức)
       ↓
[2] HARDWARE_FAULT          (Lỗi mạch TB6612, mất nguồn logic, nhiệt độ CPU Pi > 80°C)
       ↓
[3] ULTRASONIC_EMERGENCY    (Khoảng cách HC-SR04 trước mặt < 25 cm - Phanh hãm lập tức)
       ↓
[4] SYSTEM_WATCHDOG_TIMEOUT (Hệ thống hoặc Camera treo > 2.0 giây không phản hồi)
       ↓
[5] CONNECTION_LOST         (Mất kết nối WebSocket / Mất Heartbeat > 1.2s hoặc Lease > 350ms)
       ↓
[6] PERSON_IN_DANGER_ZONE   (Phát hiện người ở cự ly gần trong vùng ROI nguy hiểm)
       ↓
[7] ULTRASONIC_SLOWDOWN     (Khoảng cách HC-SR04 nằm trong khoảng 25 cm - 50 cm - Giảm 50% tốc độ)
       ↓
[8] MISSION_PREEMPTION      (Nhiệm vụ dẫn đường khách hàng ngắt tuyến tuần tra nhàn rỗi)
       ↓
[9] MANUAL_DRIVE_COMMAND    (Lệnh điều khiển thủ công hợp lệ từ nhân viên có quyền)
       ↓
[10] IDLE_PATROL_COMMAND    (Tuyến tuần tra tự động sau 5 phút nhàn rỗi)
```

---

## 4. QUY TRÌNH ĐIỀU KHIỂN THỦ CÔNG NHẤN-GIỮ (PRESS-AND-HOLD LEASE)

Để ngăn ngừa triệt để nguy cơ robot tiếp tục lao đi khi mạng Wi-Fi bị đứt, thiết bị điều khiển hết pin hoặc trình duyệt bị đóng:
1. Giao diện Web (D-Pad / Phím W-A-S-D) gửi lệnh `drive` liên tục với chu kỳ **100 ms**.
2. Backend kiểm tra phiên làm việc và cấp phép di chuyển có thời hạn **`DRIVE_COMMAND_TIMEOUT = 350 ms`**.
3. Khi người dùng nhả phím hoặc nhả chuột: Giao diện gửi ngay lệnh `stop`.
4. Nếu gói tin bị mất trên đường truyền mạng: Sau đúng **350 ms**, `ConnectionWatchdog` tự động hạ tốc độ 4 bánh xe về `0.0` và kích hoạt chế độ phanh động lực.

---

## 5. BẢO VỆ PHẦN CỨNG ĐIỆN ÁP 5V -> 3.3V

1. Chân **Echo** của cảm biến siêu âm **HC-SR04** hoạt động ở điện áp **5V TTL**.
2. Chân GPIO của **Raspberry Pi 4 Model B** chỉ chịu được điện áp tối đa **3.3V**.
3. **Giải pháp bắt buộc:** Cầu phân áp 2 điện trở nối tiếp:
   - $R_1 = 1\text{ k}\Omega$ (nối từ Echo vào chân GPIO).
   - $R_2 = 2\text{ k}\Omega$ (nối từ chân GPIO xuống GND).
   - Điện áp thực tế vào chân GPIO: $V_{\text{out}} = 5\text{V} \times \frac{2\text{k}\Omega}{1\text{k}\Omega + 2\text{k}\Omega} = 3.33\text{V}$ (Đạt chuẩn an toàn tuyệt đối).
