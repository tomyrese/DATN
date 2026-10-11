# BÁO CÁO HIỆN TRẠNG VÀ DANH SÁCH LỖI / RỦI RO HỆ THỐNG (PHASE 1 AUDIT REPORT)

**Thời điểm thực hiện:** Tháng 10/2026  
**Dự án:** Hệ thống Robot Tự hành Hỗ trợ Khách hàng Trung tâm Thương mại  
**Phần cứng mục tiêu:** Raspberry Pi 4 Model B (8GB RAM), 4 DC Motors (2x TB6612FNG), Camera CSI OV5647, 2x HC-SR04 Ultrasonic Sensors, I2C OLED 1.3" SH1106.

---

## 1. TỔNG QUAN HIỆN TRẠNG MÃ NGUỒN

### 1.1. Các thành phần đang hoạt động tốt (Working Foundations)
1. **Kiến trúc mạng & WebSocket:**
   - Hệ thống FastAPI + WebSocket (`/ws/v1/control`) hoạt động ổn định với cơ chế nhịp tim (Heartbeat 0.5s) và cấp phép lái ngắn hạn (Press-and-Hold Lease 350ms).
   - Bộ 40 bài kiểm thử tự động (`pytest tests/`) đều vượt qua (100% PASS).
2. **Điều khiển phần cứng cơ bản:**
   - `motor_controller.py` điều khiển logic 2 mạch TB6612FNG cho 4 bánh xe, hỗ trợ phanh khẩn cấp E-Stop ngắt STBY.
   - `oled_controller.py` hỗ trợ hiển thị I2C SH1106 và mã QR ghép nối.
3. **Frontend:**
   - Giao diện React 18 + TypeScript + Vite biên dịch thành công (`dist/` không có lỗi TypeScript).

---

## 2. CÁC KHOẢNG TRỐNG KỸ THUẬT VÀ LỖI / RỦI RO NGHIÊM TRỌNG (GAPS & RISKS)

### 2.1. Thị giác Máy tính (Computer Vision)
- **Rủi ro/Khoảng trống:** Hiện tại `person_detector.py` phụ thuộc hoàn toàn vào mô hình pretrained deep learning `mobilenet_ssd_v2_coco.tflite`.
- **Yêu cầu bắt buộc:** Phải thay thế hoàn toàn bằng thuật toán xử lý ảnh OpenCV cổ điển (Background Subtraction MOG2/KNN, Contour/Shape Analysis, HOG/SVM People Detector tích hợp sẵn, Optical Flow), không dùng file trọng số pretrained bên ngoài. Phải ghi nhận trung thực giới hạn thuật toán và độ chính xác thực tế.

### 2.2. Cảm biến Siêu âm HC-SR04 & Tránh vật cản
- **Khoảng trống:** Trong mã nguồn hiện tại **chưa có module HAL nào cho 2 cảm biến siêu âm HC-SR04**. Robot hiện chỉ dựa vào camera AI để dừng khi thấy người.
- **Rủi ro an toàn:** Camera CSI có góc nhìn giới hạn, không đo được khoảng cách tuyệt đối đến vật cản thấp hoặc vật cản không phải người (tường, thùng hàng, xe đẩy).
- **Cảnh báo điện áp:** Chân Echo của HC-SR04 xuất mức logic 5V. GPIO Raspberry Pi 4 chỉ chịu tối đa 3.3V. Cần ghi chú rõ mạch phân áp (1kΩ / 2kΩ) hoặc Logic Level Shifter để bảo vệ Pi.

### 2.3. Cơ sở dữ liệu và Tính toàn vẹn dữ liệu
- **Khoảng trống:** Tệp cơ sở dữ liệu `data/mall_delivery.db` chỉ chứa duy nhất một bảng `delivery_orders` đơn sơ.
- **Thiếu sót:**
  * Chưa có bảng quản lý người dùng, tài khoản, mật khẩu hash, phân quyền RBAC (`users`, `sessions`, `staff_store_assignments`, `audit_logs`).
  * Chưa có cấu trúc bảng chuẩn hóa cho TTTM: `stores`, `mall_floors`, `mall_pois`, `promotions`, `mall_faq`, `patrol_routes`.
  * Chưa có sơ đồ quan hệ khóa ngoại (Foreign Keys), ràng buộc toàn vẹn, indexes và migration versioning an toàn.

### 2.4. Phân quyền và Bảo mật (Authentication & RBAC)
- **Khoảng trống:** Hệ thống hiện chỉ có cơ chế ghép nối mã PIN 6 số trên OLED cho một thiết bị duy nhất, không phân biệt 3 vai trò rõ ràng:
  * **Guest (Khách tham quan):** Không cần đăng nhập, chỉ xem bản đồ, tra cứu cửa hàng, xem khuyến mãi, hỏi đáp AI, yêu cầu dẫn đường.
  * **Staff (Nhân viên):** Đăng nhập có tài khoản, quản lý khuyến mãi và đơn hàng chỉ của cửa hàng được gán, xem camera và điều khiển thủ công khi được cấp phép.
  * **Admin (Quản trị viên):** Quản lý toàn diện tài khoản, cửa hàng, bản đồ, tuyến tuần tra, OpenRouter API key, sao lưu database.
- **Rủi ro:** Không có password hashing (bcrypt), không có kiểm tra quyền sở hữu dữ liệu tại backend.

### 2.5. Định vị (Localization) và Điều hướng Tự hành (Autonomous Navigation)
- **Khoảng trống:** Hiện tại tính năng dẫn đường trong `mall_service.py` chỉ giả định phần trăm tiến độ bằng biến đếm thời gian (Elapsed Time), biểu tượng robot chỉ di chuyển ảo.
- **Yêu cầu nâng cấp:**
  * Xây dựng Graph bản đồ sàn thực tế: Nodes, Edges, Weights (khoảng cách m), Vùng cấm (Restricted Zones).
  * Thuật toán tìm đường tối ưu A* / Dijkstra.
  * Dead-reckoning Odometry với hiệu chuẩn vận tốc và góc quay, tính toán sai số tích lũy (Confidence Metric), phân biệt rõ ràng giữa vị trí `ESTIMATED` và `CONFIRMED`.
  * State Machine tránh vật cản và phục hồi tuyến đường (Obstacle Avoidance & Route Rejoining).
  * Cơ chế tuần tra tự động sau 5 phút không có yêu cầu dẫn khách mới.

### 2.6. Trợ lý AI OpenRouter
- **Khoảng trống:** Trợ lý ảo hiện chỉ là hàm `if/else` cố định bằng tiếng Việt.
- **Yêu cầu nâng cấp:** Tích hợp OpenRouter ở Backend, chỉ dùng API key từ biến môi trường, cơ chế Context Retrieval an toàn theo vai trò người dùng, chống Prompt Injection và có cơ chế Fallback sang Knowledge Base cục bộ nếu mất mạng/hết hạn mức.

---

## 3. KẾ HOẠCH TRIỂN KHAI CHI TIẾT (ACTION ROADMAP)

1. **Giai đoạn 2:** Chuẩn hóa Kiến trúc Database SQLite, migration có versioning, quan hệ PK/FK, seed dữ liệu mẫu.
2. **Giai đoạn 3:** Xây dựng hệ thống bảo mật & phân quyền RBAC (Guest, Staff, Admin) với bcrypt, sessions, store-scoping và audit logs.
3. **Giai đoạn 4:** Nâng cấp tầng phần cứng HAL (HC-SR04 ultrasonic, Motor Controller Odometry, đa tầng an toàn, Simulation mode mạnh mẽ).
4. **Giai đoạn 5:** Thay thế Person Detector bằng OpenCV cổ điển (MOG2 + HOG/SVM), State Machine tránh vật cản.
5. **Giai đoạn 6:** Xây dựng Graph A*, Odometry Dead-reckoning, tuần tra 5 phút, ưu tiên nhiệm vụ.
6. **Giai đoạn 7:** Nâng cấp Nghiệp vụ TTTM (Quản lý cửa hàng, khuyến mãi phân quyền, đơn giao hàng SQLite, nhiệm vụ dẫn đường).
7. **Giai đoạn 8:** Tích hợp OpenRouter AI Assistant bảo mật với Context Injection và Fallback.
8. **Giai đoạn 9:** Nâng cấp Frontend thống nhất, tự thích ứng giao diện theo 3 vai trò, bản đồ tương tác đường đi thực tế.
9. **Giai đoạn 10:** Kiểm thử toàn diện (Pytest + Frontend Build), viết đầy đủ 12+ tài liệu và báo cáo nghiệm thu.
