# Pi Robot System Architecture (Phase 2)

Tài liệu thiết kế kiến trúc hệ thống toàn diện của Robot Trung Tâm Thương Mại trên Raspberry Pi 4 Model B kết hợp ứng dụng điều khiển Web Application Central Command.

---

## 1. Sơ Đồ Khối Kiến Trúc Tổng Thể

```
+---------------------------------------------------------------------------------+
|               Giao Diện Web Dashboard Điều Khiển (Responsive Web App)           |
|                                                                                 |
|  [ PairModal / WebQrScanner ]  -->  [ Dashboard ]  -->  [ Control / D-Pad ]     |
|  [ Camera Screen (MJPEG)    ]  -->  [ Motor Test ] -->  [ Diagnostics / Settings|
|                                                                                 |
|       +-----------------------------------------------------------------+       |
|       |     RobotSocket (WebSocket)   &   RobotApi (FastAPI REST)       |       |
|       +-----------------------------------------------------------------+       |
+----------------------------------------|----------------------------------------+
                                         | Wi-Fi LAN / HTTP & WS
+----------------------------------------v----------------------------------------+
|                            Raspberry Pi 4 Model B                               |
|                                                                                 |
|   +-------------------------------------------------------------------------+   |
|   |                  FastAPI / Uvicorn Server (Port 8765)                   |   |
|   |   - Web Server: / (index.html, css/, js/)                               |   |
|   |   - REST: /api/v1/health, /pair, /camera/mjpeg, /camera/ticket, /info   |   |
|   |   - WebSocket: /ws/v1/control (Hello, Drive, Heartbeat, Telemetry)      |   |
|   +-------------------------------------------------------------------------+   |
|                                        |                                        |
|   +------------------------------------v------------------------------------+   |
|   |                 RobotController (Bộ Điều Phối Trung Tâm)                |   |
|   |   - AuthManager & PairingManager (OLED QR Generation)                   |   |
|   |   - ConnectionWatchdog (350ms Lease & 1.2s Heartbeat Timeout)           |   |
|   |   - TelemetryService (2–5 Hz Live Sensor & Metric Broadcasting)         |   |
|   +-------------------------------------------------------------------------+   |
|             |                          |                          |             |
|             v                          v                          v             |
|   +-------------------+      +-------------------+      +-------------------+   |
|   |   CameraService   |      |  SafetyController |      |  OLEDController   |   |
|   | (CSI Picamera2)   |      | (Priority Engine) |      | (SH1106 / SSD1306)|   |
|   +-------------------+      +-------------------+      +-------------------+   |
|             |                          |                          |             |
|      +------+------+                   |                          v             |
|      |             |                   |                  Màn Hình OLED 1.3"    |
|      v             v                   |                  (QR & Trạng Thái)     |
|  +--------+   +----------+             |                                        |
|  | AI SSD |   |  MJPEG   |             v                                        |
|  | Detect |   |  Stream  |   +-------------------+                              |
|  +--------+   +----------+   |  MotorController  |                              |
|      |                       |  (2x TB6612FNG)   |                              |
|      +----------->-----------+-------------------+                              |
|                                        |                                        |
|                                        v                                        |
|                               4 Động Cơ DC Bánh Xe                              |
+---------------------------------------------------------------------------------+
```

---

## 2. Mô Hình Chia Sẻ Camera CSI Duy Nhất (Single Camera Source)

Cổng CSI trên Raspberry Pi 4 chỉ cho phép mở camera một lần duy nhất từ một process:
- **`CameraService`** là dịch vụ duy nhất nắm giữ phần cứng `Picamera2` / `libcamera`.
- `CameraService` duy trì luồng capture liên tục lưu frame mới nhất vào bộ nhớ RAM.
- **`PersonDetector`** lấy frame từ buffer để chạy mô hình AI nhận diện người (`300x300`).
- **`CameraStreamManager`** lấy cùng frame từ buffer để nén JPEG (`640x480 @ 8 FPS`) phục vụ video trực tiếp cho App Android.
- Đảm bảo AI an toàn và video preview hoạt động đồng thời mà không xung đột tài nguyên.

---

## 3. Hệ Thống Phân Cấp Ưu Tiên An Toàn (Safety Priority Hierarchy)

Mọi lệnh điều khiển từ xa (App Android, CLI) đều bắt buộc đi qua bộ lọc an toàn `SafetyController` theo thứ tự ưu tiên tuyệt đối:

```
[1] EMERGENCY_STOP     (Dừng khẩn cấp người dùng bấm - ngắt STBY)
       ↓
[2] SYSTEM_ERROR       (Lỗi hệ thống ngoại lệ nghiêm trọng)
       ↓
[3] CAMERA_ERROR       (Mất tín hiệu camera CSI hoặc watchdog timeout > 2.0s)
       ↓
[4] PERSON_DETECTED    (Phát hiện người trong STOP_ZONE X: 0.20-0.80)
       ↓
[5] SAFETY_STOP        (Trạng thái dừng an toàn)
       ↓
[6] CONNECTION_LOST    (Mất heartbeat > 1.2s hoặc lease timeout > 350ms)
       ↓
[7] MANUAL_STOP        (Lệnh nhả nút dừng từ App)
       ↓
[8] MOVEMENT_COMMAND   (Lệnh di chuyển tiến, lùi, rẽ)
```

---

## 4. Nguyên Lý Điều Khiển Nhấn-Giữ (Press-and-Hold Lease)

Để tránh tình trạng robot chạy mất kiểm soát khi điện thoại bị sập nguồn, mất Wi-Fi, hoặc crash ứng dụng:
1. Khi người dùng nhấn giữ nút trên App, App gửi lệnh `drive` liên tục mỗi `100 ms`.
2. Server cấp phép di chuyển trong thời hạn ngắn `DRIVE_COMMAND_TIMEOUT = 350 ms`.
3. Khi người dùng nhả nút: App gửi lệnh `stop` ngay lập tức.
4. Nếu App bị ngắt kết nối đột ngột: sau đúng `350 ms` không có lệnh làm mới, `ConnectionWatchdog` tự động ngắt động cơ về `0.0`.
