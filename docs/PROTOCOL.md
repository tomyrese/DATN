# Pi Robot Protocol Specification (v1.0)

Tài liệu đặc tả toàn bộ giao thức truyền thông giữa robot (Raspberry Pi 4) và ứng dụng điều khiển Web Dashboard / Client.

---

## 1. Định Dạng Mã QR Ghép Nối (Pairing QR Format)

Mã QR hiển thị trên màn hình OLED 1.3" 128x64 sử dụng chuỗi văn bản tối giản phân tách bằng dấu gạch đứng `|`:

```
P1|HOST|PORT|PAIR_CODE
```

### Các trường dữ liệu:
- **`P1`**: Phiên bản giao thức (Protocol Version 1).
- **`HOST`**: Địa chỉ IPv4 mạng cục bộ của Raspberry Pi (ví dụ `192.168.1.50`).
- **`PORT`**: Cổng dịch vụ Robot Server (mặc định `8765`).
- **`PAIR_CODE`**: Mã xác thực ngẫu nhiên 6 ký tự gồm chữ in hoa và chữ số (ví dụ `A7K39P`), thời gian sống (TTL) là 120 giây.

---

## 2. Danh Sách REST API (Versioned: `/api/v1`)

### 2.1. `GET /api/v1/health`
Kiểm tra sức khỏe hệ thống phần cứng và server.
- **Yêu cầu xác thực:** Không.
- **Phản hồi mẫu:**
```json
{
  "status": "ok",
  "robotState": "STOPPED",
  "safetyState": "CLEAR",
  "camera": true,
  "detector": true,
  "motor": true,
  "oled": true,
  "server": true
}
```

### 2.2. `GET /api/v1/info`
Thông tin chung về robot.
- **Yêu cầu xác thực:** Không.
- **Phản hồi mẫu:**
```json
{
  "robotId": "RBT01",
  "robotName": "Pi Robot",
  "apiVersion": "v1",
  "protocolVersion": 1,
  "hostname": "raspberrypi",
  "serverVersion": "1.0.0",
  "paired": true
}
```

### 2.3. `GET /api/v1/status`
Ảnh chụp nhanh trạng thái telemetry hiện tại.
- **Yêu cầu xác thực:** Không.

### 2.4. `POST /api/v1/pair`
Xác thực mã ghép nối và cấp phát Session Token.
- **Yêu cầu xác thực:** Không.
- **Body gửi lên:**
```json
{
  "pairCode": "A7K39P",
  "clientInfo": "Android Device"
}
```
- **Phản hồi thành công:**
```json
{
  "success": true,
  "token": "4vO2K-8dM_3...",
  "robotId": "RBT01",
  "robotName": "Pi Robot",
  "message": "Pairing successful"
}
```

### 2.5. `POST /api/v1/emergency-stop`
Kích hoạt dừng khẩn cấp toàn bộ hệ thống động cơ ngay lập tức.
- **Yêu cầu xác thực:** Không.

### 2.6. `POST /api/v1/emergency-reset`
Mở khóa an toàn sau khi dừng khẩn cấp (chỉ cho phép khi khu vực an toàn).
- **Yêu cầu xác thực:** Có (`Authorization: Bearer <token>`).

### 2.7. `GET /api/v1/camera/ticket`
Cấp vé truy cập ngắn hạn (TTL: 30s) để xem luồng MJPEG.
- **Yêu cầu xác thực:** Có (`Authorization: Bearer <token>`).
- **Phản hồi mẫu:**
```json
{
  "ticket": "8f3b2a9c1d0e4f5a",
  "expiresIn": 30.0
}
```

### 2.8. `GET /api/v1/camera/snapshot`
Lấy 1 frame ảnh tĩnh định dạng JPEG từ camera CSI.
- **Yêu cầu xác thực:** Token hoặc Ticket.

### 2.9. `GET /api/v1/camera/mjpeg`
Luồng video MJPEG thời gian thực (`multipart/x-mixed-replace; boundary=frame`) ở tốc độ 8 FPS.
- **Yêu cầu xác thực:** Token hoặc Ticket (`?ticket=...`).

### 2.10. `GET /api/v1/logs/recent`
Lấy 50 sự kiện quan trọng gần nhất của robot.
- **Yêu cầu xác thực:** Có.

### 2.11. `DELETE /api/v1/session`
Hủy phiên ghép nối hiện tại (Quên robot).
- **Yêu cầu xác thực:** Có.

---

## 3. Giao Thức WebSocket Realtime (`/ws/v1/control`)

Kênh truyền thông điều khiển 2 chiều với độ trễ siêu thấp.
Kết nối: `ws://<HOST>:<PORT>/ws/v1/control?token=<TOKEN>`

### 3.1. Handshake Khởi Tạo
Client gửi:
```json
{
  "type": "hello",
  "protocol": 1,
  "client": "android",
  "appVersion": "1.0.0"
}
```
Server phản hồi:
```json
{
  "type": "hello_ack",
  "protocol": 1,
  "robotId": "RBT01",
  "robotName": "Pi Robot",
  "state": "STOPPED"
}
```

### 3.2. Heartbeat Giám Sát Kết Nối (Gửi mỗi 400ms)
Client gửi:
```json
{
  "type": "heartbeat",
  "timestamp": 1718000000.123
}
```
Server phản hồi:
```json
{
  "type": "heartbeat_ack",
  "timestamp": 1718000000.125
}
```

### 3.3. Lệnh Điều Khiển Di Chuyển (Press-and-Hold với Lease 350ms)
Client gửi lặp lại mỗi 100ms khi giữ nút:
```json
{
  "type": "drive",
  "direction": "forward",
  "speed": 0.35,
  "seq": 101
}
```
*(Các hướng: `"forward"`, `"backward"`, `"left"`, `"right"`)*

Server phản hồi:
```json
{
  "type": "command_ack",
  "seq": 101,
  "accepted": true
}
```
*(Nếu bị chặn do có người hoặc E-Stop: `accepted: false, reason: "PERSON_DETECTED"`)*

### 3.4. Lệnh Dừng (Stop)
Khi người dùng nhả nút điều khiển:
```json
{
  "type": "stop",
  "seq": 102
}
```

### 3.5. Kiểm Tra Độc Lập Từng Động Cơ (Motor Test)
```json
{
  "type": "motor_test",
  "motor": 1,
  "speed": 0.20,
  "seq": 103
}
```

### 3.6. Dòng Dữ Liệu Telemetry Định Kỳ (2–5 Hz)
Server phát liên tục:
```json
{
  "type": "telemetry",
  "robotState": "FORWARD",
  "safetyState": "CLEAR",
  "speed": 0.35,
  "leftSpeed": 0.35,
  "rightSpeed": 0.35,
  "m1": 0.35,
  "m2": 0.35,
  "m3": 0.35,
  "m4": 0.35,
  "personDetected": false,
  "personConfidence": 0.0,
  "cameraOk": true,
  "detectorOk": true,
  "oledOk": true,
  "motorOk": true,
  "cameraFps": 30.0,
  "inferenceFps": 11.2,
  "cpuTemp": 51.4,
  "cpuUsage": 28.5,
  "memoryUsage": 38.0,
  "uptime": 245.5,
  "timestamp": 1718000001.5
}
```

### 3.7. Sự Kiện An Toàn Tức Thì (Immediate Safety Events)
Khi phát hiện người bước vào STOP_ZONE, server gửi ngay lập tức:
```json
{
  "type": "safety_event",
  "event": "person_detected",
  "confidence": 0.88
}
```
Khi người rời khỏi:
```json
{
  "type": "safety_event",
  "event": "person_clear"
}
```

---

## 4. Bảng Mã Lỗi Chuẩn (Standard Error Codes)

| Mã lỗi | Ý nghĩa | Hành động của App |
| :--- | :--- | :--- |
| `AUTH_REQUIRED` | Thiếu token xác thực | Chuyển về màn hình Ghép nối |
| `AUTH_INVALID` | Token không hợp lệ hoặc đã bị hủy | Yêu cầu quét lại mã QR |
| `PAIR_CODE_INVALID` | Mã ghép nối sai hoặc đã hết hạn | Báo lỗi trên màn hình QR |
| `CONTROLLER_BUSY` | Đã có một thiết bị khác đang điều khiển | Báo bận, từ chối kết nối |
| `SAFETY_BLOCKED` | Lệnh di chuyển bị từ chối do khóa an toàn | Hiển thị cảnh báo an toàn |
| `PERSON_DETECTED` | Phát hiện người trong vùng nguy hiểm | Dừng motor, báo động đỏ |
| `CAMERA_ERROR` | Mất tín hiệu camera CSI | Dừng robot, khóa di chuyển |
| `EMERGENCY_ACTIVE` | Đang ở trạng thái dừng khẩn cấp | Yêu cầu bấm nút Reset E-Stop |

---

## 5. Các Tham Số Thời Gian & Timeouts (Safety Invariants)

- **`DRIVE_COMMAND_INTERVAL`**: 100 ms (tần suất app gửi làm mới lệnh khi giữ nút).
- **`DRIVE_COMMAND_TIMEOUT`**: 350 ms (hết hạn lệnh di chuyển nếu app mất kết nối hoặc bị đóng).
- **`HEARTBEAT_INTERVAL`**: 400 ms.
- **`CONNECTION_TIMEOUT`**: 1.2 s (ngắt kết nối và dừng robot nếu không nhận được heartbeat).
- **`CAMERA_WATCHDOG_TIMEOUT`**: 2.0 s (dừng robot nếu luồng camera bị đơ khi đang chạy).
- **`PERSON_CLEAR_DELAY`**: 1.5 s (thời gian trễ xác nhận sau khi người rời đi).
- **`AUTO_RESUME_AFTER_PERSON_CLEAR`**: `false` (robot luôn ở trạng thái STOPPED, không tự động chạy lại).
