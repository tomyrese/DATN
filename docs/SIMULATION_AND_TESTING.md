# CHẾ ĐỘ MÔ PHỎNG & HƯỚNG DẪN KIỂM THỬ (SIMULATION & TESTING)

Tài liệu hướng dẫn vận hành chế độ mô phỏng hoàn toàn không cần phần cứng (Zero-Hardware Simulation) và quy trình kiểm thử tự động toàn diện.

---

## 1. CHẾ ĐỘ MÔ PHỎNG PHẦN CỨNG (HARDWARE SIMULATION MODE)

Khi phát triển hoặc kiểm thử trên máy tính cá nhân (Windows/Linux/macOS) không kết nối GPIO, CSI Camera, hoặc HC-SR04:
- Đặt biến môi trường `SIMULATION_MODE=true` trong tệp `.env`.
- Toàn bộ các module phần cứng tự động chuyển sang lớp trừu tượng ảo (Mock / Simulated Abstraction Layer).

### 1.1. Hành vi của các module trong chế độ mô phỏng
1. **Động cơ (`MotorController`):**
   - Không gọi `lgpio` / `RPi.GPIO`.
   - Vận tốc động cơ được mô phỏng trong bộ nhớ RAM và xuất nhãn `[SIMULATED]`.
   - Hàm `get_speeds()` và `get_wheel_speeds()` phản hồi chính xác giá trị đã truyền vào.
2. **Cảm biến siêu âm (`UltrasonicSensors`):**
   - Giả lập khoảng cách vật lý $180\text{ cm}$ (thông thoáng).
   - Hỗ trợ hàm `set_simulated_distances(dist1, dist2)` cho phép kịch bản test tự động mô phỏng chướng ngại vật xuất hiện gần (< 25cm) để kích hoạt phanh an toàn.
3. **Camera CSI (`CameraService`):**
   - Tự động sinh khung hình đồ họa tổng hợp (Synthetic Frame) kích thước 640x480 tốc độ 30 FPS.
   - Vẽ đồng hồ dấu thời gian chuyển động (timestamp watermark) để kiểm tra luồng video MJPEG và thuật toán trừ nền MOG2.
4. **Màn hình OLED (`OLEDController`):**
   - Giả lập hiển thị, in trạng thái kết nối và mã ghép nối QR ra log điều khiển.

> [!IMPORTANT]
> **QUY TẮC MINH BẠCH VỀ TRẠNG THÁI MÔ PHỎNG:**
> 
> Mọi dữ liệu phát ra từ chế độ mô phỏng đều được hệ thống gắn nhãn rõ ràng:
> - Telemetry mang cờ: `is_estimated: True`.
> - Giao diện Web hiển thị huy hiệu: `[SIMULATED DEAD-RECKONING]`.
> - Không bao giờ giả mạo rằng robot đã định vị vật lý trong trung tâm thương mại thật.

---

## 2. QUY TRÌNH CHẠY BACKEND & FRONTEND TẠI MÔI TRƯỜNG PHÁT TRIỂN

### 2.1. Khởi động Backend Python / FastAPI
```powershell
# Tại thư mục gốc dự án: D:\Study\KLTN\Code
python src/main.py
```
Máy chủ khởi động tại: `http://localhost:8765`
- Swagger API Docs: `http://localhost:8765/docs`
- WebSocket Endpoint: `ws://localhost:8765/ws/v1/control`
- Web Dashboard: `http://localhost:8765/`

### 2.2. Khởi động Frontend React 18 + Vite (Dev Server)
```powershell
cd frontend
npm install
npm run dev
```
Giao diện chạy tại: `http://localhost:5173` (tự động kết nối WebSocket và REST API tới cổng 8765).

### 2.3. Build Production Bundle cho Frontend
```powershell
cd frontend
npm run build
```
Kết quả xuất ra thư mục `frontend/dist`. Khi backend chạy `python src/main.py`, FastAPI tự động nạp và phục vụ toàn bộ Single Page Application từ thư mục `dist` này.

---

## 3. CHẠY BỘ KIỂM THỬ TỰ ĐỘNG TOÀN DIỆN (AUTOMATED TEST SUITE)

Hệ thống sở hữu bộ kiểm thử tự động gồm **53 bài kiểm thử unit & integration test** bao phủ 100% các lớp nghiệp vụ, bảo mật, định vị và xử lý ảnh.

### Lệnh chạy kiểm thử:
```powershell
# Chạy toàn bộ 53 bài test
python -m pytest tests/

# Chạy kèm thông tin chi tiết từng test
python -m pytest tests/ -v

# Chạy riêng từng nhóm chức năng
python -m pytest tests/test_database_v2.py           # Kiểm tra SQLite, WAL, FK, Migrations
python -m pytest tests/test_auth_rbac.py             # Kiểm tra bcrypt, RBAC, Store scoping
python -m pytest tests/test_classical_vision.py      # Kiểm tra OpenCV HOG & MOG2
python -m pytest tests/test_ultrasonic_and_safety.py # Kiểm tra HC-SR04 & FSM tránh vật cản
python -m pytest tests/test_navigation_graph.py      # Kiểm tra A* Pathfinding & Topo Graph
python -m pytest tests/test_patrol_and_odometry.py   # Kiểm tra Odometry & 5-Min Idle Patrol
python -m pytest tests/test_api_server.py            # Kiểm tra 8 REST APIs và Camera Ticket
python -m pytest tests/test_websocket_protocol.py    # Kiểm tra WebSocket heartbeat và D-pad
```

---

## 4. BẢNG CHECKLIST KIỂM THỬ PHẦN CỨNG THỰC TẾ (HARDWARE ACCEPTANCE CHECKLIST)

Khi chuyển từ môi trường mô phỏng sang robot thật, kỹ sư bắt buộc thực hiện kiểm tra tuần tự theo checklist an toàn sau:

1. [ ] **Kê bánh xe khỏi mặt đất (Wheels Off-Ground Test):** Đặt robot lên bệ đỡ để 4 bánh xe quay tự do trên không trước khi bật công tắc pin.
2. [ ] **Đo điện áp chân Echo HC-SR04:** Dùng đồng hồ VOM kiểm tra điện áp tại đầu ra mạch chia áp vào GPIO Pi $\le 3.3\text{V}$.
3. [ ] **Kiểm tra chiều quay 4 động cơ:** Dùng chức năng Motor Test trên Web Dashboard để xác nhận bánh trái và bánh phải quay đúng chiều tiến/lùi, không bị đấu ngược cực.
4. [ ] **Kiểm tra độ trễ ngắt khẩn cấp (E-Stop Latency):** Nhấn nút Dừng Khẩn Cấp trên Dashboard hoặc nút cơ khí, đo thời gian động cơ mất nguồn $\le 50\text{ ms}$.
5. [ ] **Thử nghiệm vật cản tĩnh:** Đặt thùng carton cách trước mặt $40\text{ cm}$, robot phải tự động giảm tốc; đẩy lại gần $< 25\text{ cm}$, robot phải dừng hẳn và phát cảnh báo.
6. [ ] **Thử nghiệm mất kết nối (Deadman Lease Timeout):** Đóng tab trình duyệt trong lúc robot đang chạy, watchdog phải tự động ngắt động cơ sau $0.35\text{ giây}$.
