# ĐẶC TẢ GIAO THỨC TRUYỀN THÔNG ROBOT TTTM (PROTOCOL SPECIFICATION V2.0)

Tài liệu đặc tả toàn bộ giao diện lập trình ứng dụng REST API và kênh truyền thời gian thực hai chiều WebSocket giữa ứng dụng Web Dashboard và hệ thống backend Raspberry Pi 4.

---

## 1. TỔNG QUAN XÁC THỰC VÀ PHÂN QUYỀN (RBAC AUTHENTICATION)

Tất cả các API yêu cầu xác thực sử dụng Bearer Token định dạng UUID trong HTTP Header:
```http
Authorization: Bearer <session_token>
```
Hệ thống hỗ trợ 3 cấp bậc vai trò:
- **`guest`**: Công khai, không cần Token.
- **`staff`**: Nhân viên cửa hàng, giới hạn thao tác trong phạm vi các gian hàng được phân công.
- **`admin`**: Quản trị viên toàn hệ thống, toàn quyền cấu hình và điều khiển.

---

## 2. DANH SÁCH REST API (VERSIONED: `/api/v1`)

### 2.1. Nhóm Xác Thực & Tài Khoản (Authentication & Session)

#### `POST /api/v1/login`
- **Quyền truy cập:** Công khai (`guest`).
- **Mục đích:** Đăng nhập lấy Session Token.
- **Body:**
  ```json
  {
    "username": "staff_zara",
    "password": "Staff@123456"
  }
  ```
- **Response 200 OK:**
  ```json
  {
    "success": true,
    "token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "user": {
      "id": "usr_staff_zara",
      "username": "staff_zara",
      "full_name": "Nhân viên Zara",
      "role": "staff",
      "assigned_stores": ["store_zara"]
    }
  }
  ```

#### `POST /api/v1/logout`
- **Quyền truy cập:** Yêu cầu đăng nhập (`staff` hoặc `admin`).
- **Response 200 OK:** `{"success": true, "message": "Đã đăng xuất"}`

#### `GET /api/v1/me`
- **Quyền truy cập:** Yêu cầu đăng nhập (`staff` hoặc `admin`).
- **Response 200 OK:** Thông tin tài khoản hiện tại kèm danh sách gian hàng phụ trách.

---

### 2.2. Nhóm Thông Tin Robot & Sức Khỏe Phần Cứng (Telemetry & Health)

#### `GET /api/v1/health`
- **Quyền truy cập:** Công khai.
- **Response 200 OK:**
  ```json
  {
    "status": "ok",
    "robotState": "IDLE",
    "safetyState": "CLEAR",
    "camera": true,
    "detector": true,
    "motor": true,
    "oled": true,
    "server": true,
    "ultrasonic": {
      "left_cm": 120.5,
      "right_cm": 118.2,
      "state": "CLEAR"
    }
  }
  ```

#### `GET /api/v1/info`
- **Quyền truy cập:** Công khai.
- **Response 200 OK:** Tên robot, ID, phiên bản API `v2.0`, hostname và thông tin phần cứng.

#### `GET /api/v1/status`
- **Quyền truy cập:** Công khai.
- **Response 200 OK:** Dữ liệu đo đạc chi tiết bao gồm tọa độ Odometry ($x, y, \theta$), độ tin cậy (`confidence`), trạng thái pin, nhiệt độ CPU.

---

### 2.3. Nhóm Điều Khiển Khẩn Cấp & Camera Vé Bảo Mật

#### `POST /api/v1/emergency-stop`
- **Quyền truy cập:** Công khai / Khẩn cấp.
- **Mục đích:** Kích hoạt ngắt điện phần cứng động cơ ngay lập tức.
- **Response 200 OK:** `{"success": true, "state": "EMERGENCY_STOP"}`

#### `POST /api/v1/emergency-reset`
- **Quyền truy cập:** Yêu cầu `staff` hoặc `admin`.
- **Mục đích:** Mở khóa trạng thái khẩn cấp sau khi kiểm tra khu vực an toàn.
- **Response 200 OK:** `{"success": true, "state": "IDLE"}`

#### `GET /api/v1/camera/ticket`
- **Quyền truy cập:** Yêu cầu `staff` hoặc `admin`.
- **Mục đích:** Cấp phát vé xem camera trực tiếp thời hạn ngắn (TTL: 30 giây).
- **Response 200 OK:** `{"ticket": "tk_8f3b2a9c1d0e4f5a", "expiresIn": 30.0}`

#### `GET /api/v1/camera/mjpeg?ticket={ticket}`
- **Quyền truy cập:** Yêu cầu Ticket hợp lệ.
- **Response 200 OK:** Luồng dữ liệu video `multipart/x-mixed-replace; boundary=frame`.

---

### 2.4. Nhóm Nghiệp Vụ TTTM (Stores, Promotions, Escort, Delivery)

#### `GET /api/v1/stores`
- **Quyền truy cập:** Công khai. Trả về danh sách gian hàng, tầng, danh mục, tọa độ node bản đồ.

#### `GET /api/v1/promotions`
- **Quyền truy cập:** Công khai. Trả về danh sách khuyến mãi đang có hiệu lực (`is_active = 1`).

#### `POST /api/v1/promotions`
- **Quyền truy cập:** `staff` (chỉ được tạo cho gian hàng phụ trách) hoặc `admin` (toàn quyền).
- **Body:** `{ "store_id": "store_zara", "title": "Giảm giá 30%", "discount_percent": 30, ... }`

#### `PUT /api/v1/promotions/{promo_id}`
- **Quyền truy cập:** `staff` (kiểm tra quyền sở hữu) hoặc `admin`. Cập nhật nội dung khuyến mãi.

#### `DELETE /api/v1/promotions/{promo_id}`
- **Quyền truy cập:** `staff` (kiểm tra quyền sở hữu) hoặc `admin`. Xóa khuyến mãi.

#### `POST /api/v1/escort`
- **Quyền truy cập:** Công khai (`guest`), `staff`, `admin`.
- **Body:** `{ "target_poi_id": "poi_zara" }`
- **Mục đích:** Yêu cầu robot dẫn đường từ vị trí hiện tại tới điểm đến.

#### `GET /api/v1/deliveries`
- **Quyền truy cập:** `staff` hoặc `admin`. Trả về hàng đợi đơn giao hàng nội bộ.

#### `POST /api/v1/deliveries`
- **Quyền truy cập:** `staff` hoặc `admin`. Tạo đơn giao hàng từ điểm lấy hàng tới điểm giao hàng.

---

### 2.5. Nhóm Trợ Lý AI Concierge & Quản Trị Hệ Thống (AI & Admin)

#### `POST /api/v1/ai/ask`
- **Quyền truy cập:** Công khai. Giới hạn tần suất (Rate limit 20 req/min).
- **Body:** `{ "question": "Highlands Coffee nằm ở tầng mấy?" }`
- **Response 200 OK:** `{ "answer": "Highlands Coffee nằm tại Tầng 1, Sảnh Đông...", "suggested_poi": "poi_highlands" }`

#### `GET /api/v1/admin/users`
- **Quyền truy cập:** Chỉ `admin`. Quản lý danh sách tài khoản nhân viên.

#### `POST /api/v1/admin/users`
- **Quyền truy cập:** Chỉ `admin`. Tạo tài khoản nhân viên mới kèm phân công gian hàng.

#### `GET /api/v1/admin/audit-logs`
- **Quyền truy cập:** Chỉ `admin`. Xem nhật ký kiểm toán hệ thống.

#### `POST /api/v1/admin/backup-db`
- **Quyền truy cập:** Chỉ `admin`. Kích hoạt sao lưu tức thời database SQLite sang file `.backup_<timestamp>`.

---

## 3. ĐẶC TẢ GIAO THỨC WEBSOCKET (`/ws/v1/control`)

### 3.1. Thiết Lập Kết Nối & Xác Thực
1. Client kết nối tới `ws://<HOST>:8765/ws/v1/control`.
2. Client gửi gói tin `hello` chứa token (nếu là staff/admin) hoặc rỗng (nếu là guest):
   ```json
   {
     "type": "hello",
     "clientType": "web_dashboard",
     "token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
     "clientTimestamp": 1773381600000
   }
   ```
3. Server phản hồi `welcome` kèm phân quyền xác nhận:
   ```json
   {
     "type": "welcome",
     "authenticated": true,
     "role": "staff",
     "robotState": "IDLE"
   }
   ```

### 3.2. Chu Kỳ Heartbeat (1.2 Giây)
Client gửi heartbeat định kỳ mỗi 1.0 giây:
```json
{ "type": "heartbeat", "timestamp": 1773381601000 }
```
Server phản hồi:
```json
{ "type": "heartbeat_ack", "timestamp": 1773381601005 }
```
*Nếu quá 1.2 giây server không nhận được heartbeat khi đang lái xe thủ công, xe tự động dừng lại lập tức.*

### 3.3. Lệnh Điều Khiển Vận Động (Drive Lease 350ms)
Chỉ cho phép `staff` hoặc `admin`:
```json
{
  "type": "drive",
  "direction": "FORWARD",
  "speed": 0.6,
  "lease_ms": 350
}
```
Các hướng hợp lệ: `FORWARD`, `BACKWARD`, `TURN_LEFT`, `TURN_RIGHT`, `STOP`.

### 3.4. Gói Tin Telemetry Tự Động Từ Server (Tần số 2 - 5 Hz)
Server phát thanh cập nhật liên tục:
```json
{
  "type": "telemetry",
  "robotState": "IDLE",
  "safetyState": "CLEAR",
  "odometry": {
    "x": 12.4,
    "y": 8.6,
    "heading": 1.57,
    "confidence": 0.88,
    "is_estimated": true
  },
  "ultrasonic": {
    "left_cm": 150.0,
    "right_cm": 145.2,
    "obstacle_state": "CLEAR"
  },
  "system": {
    "cpu_temp": 48.5,
    "cpu_percent": 18.2,
    "ram_percent": 34.0
  }
}
```
