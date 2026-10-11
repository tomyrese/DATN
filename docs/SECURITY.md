# KIẾN TRÚC BẢO MẬT & MÔ HÌNH PHÂN QUYỀN (SECURITY & RBAC)

Tài liệu thiết kế bảo mật toàn diện cho hệ thống Robot Tự Hành Trung Tâm Thương Mại: xác thực, phân quyền 3 tầng (Guest, Staff, Admin), quản lý bí mật, chống tiêm câu lệnh (Prompt Injection) và kiểm toán hệ thống.

---

## 1. MÔ HÌNH PHÂN QUYỀN 3 TẦNG (3-TIER RBAC)

Hệ thống cung cấp một ứng dụng Web duy nhất. Sau khi đăng nhập, giao diện và quyền truy cập API tại Backend được tự động phân nhánh nghiêm ngặt:

```
[Khách Tham Quan (Guest)]       [Nhân Viên Gian Hàng (Staff)]        [Quản Trị Viên (Admin)]
        |                                      |                                     |
   - Xem bản đồ TTTM                     - Xem bản đồ & robot status           - Toàn quyền Admin
   - Tra cứu cửa hàng & KM               - Xem live camera (có ticket)         - Tạo/khóa/sửa user Staff
   - Hỏi AI Concierge công khai          - Điều khiển D-Pad thủ công           - Gán quyền gian hàng
   - Yêu cầu robot dẫn đường             - Quản lý KM gian hàng mình           - Quản lý KM toàn TTTM
   - Hủy dẫn đường của mình              - Quản lý đơn giao hàng mình          - Cấu hình bản đồ/tuần tra
                                                                               - Backup DB & Audit logs
```

### 1.1. Ma trận phân quyền chi tiết (Access Control Matrix)

| Nhóm Chức Năng / Endpoint API | Khách (Guest) | Nhân Viên (Staff) | Quản Trị (Admin) |
| :--- | :---: | :---: | :---: |
| `GET /api/v1/mall/pois`, `/stores`, `/promotions` | ✅ Cho phép | ✅ Cho phép | ✅ Cho phép |
| `POST /api/v1/mall/escort` (Dẫn đường) | ✅ Cho phép | ✅ Cho phép | ✅ Cho phép |
| `POST /api/v1/mall/ai/ask` (Hỏi đáp TTTM) | ✅ Công khai | ✅ Theo gian hàng | ✅ Toàn quyền |
| `POST /api/v1/emergency-stop` (Dừng khẩn) | ✅ **Ai cũng có thể bấm** | ✅ Cho phép | ✅ Cho phép |
| `POST /api/v1/emergency-reset` (Mở khóa E-stop) | ❌ Chặn (401) | ✅ Cần xác thực | ✅ Cho phép |
| `GET /api/v1/camera/ticket`, `/mjpeg` (Xem cam) | ❌ Chặn (401) | ✅ Cần xác thực | ✅ Cho phép |
| `POST /api/v1/control/drive` (Lái thủ công) | ❌ Chặn (401) | ✅ Cần xác thực | ✅ Cho phép |
| `POST /api/v1/mall/delivery/orders` (Giao hàng) | ❌ Chặn (401) | ✅ Gian hàng mình | ✅ Mọi gian hàng |
| `POST/PUT/DEL /api/v1/mall/promotions` | ❌ Chặn (401) | ✅ Gian hàng mình | ✅ Mọi gian hàng |
| `GET /api/v1/admin/users`, `POST /admin/users` | ❌ Chặn (401) | ❌ Chặn (403) | ✅ Cho phép |
| `GET /api/v1/admin/audit-logs` (Kiểm toán) | ❌ Chặn (401) | ❌ Chặn (403) | ✅ Cho phép |
| `POST /api/v1/admin/backup-db` (Sao lưu DB) | ❌ Chặn (401) | ❌ Chặn (403) | ✅ Cho phép |

---

## 2. QUẢN LÝ ĐĂNG NHẬP, MẬT KHẨU & PHIÊN LÀM VIỆC (SESSIONS)

### 2.1. Mã hóa mật khẩu một chiều
- Thuật toán băm: **bcrypt** với hệ số chi phí (work factor) $12$.
- Cơ chế Fallback an toàn: PBKDF2-HMAC-SHA256 với $100,000$ vòng lặp khi môi trường thiếu thư viện native C.
- Mật khẩu dạng rõ (plaintext) tuyệt đối không bao giờ được lưu vào cơ sở dữ liệu hoặc ghi log.

### 2.2. Token phiên làm việc & Xác thực
- Token phiên được tạo ngẫu nhiên bảo mật cao bằng `secrets.token_hex(32)` (256-bit entropy).
- Token được lưu trong bảng `user_sessions` với thời gian sống (TTL) 7 ngày.
- Khi người dùng bấm Đăng Xuất (`POST /api/v1/auth/logout`), token lập tức bị xóa khỏi database và thu hồi quyền WebSocket.

### 2.3. Cách ly dữ liệu theo gian hàng (Store Scoping Enforcement)
- Nhân viên được liên kết với một hoặc nhiều gian hàng qua bảng `staff_store_assignments`.
- Backend kiểm tra độc lập tại controller:
  ```python
  if session.role != "admin" and store_id not in session.assigned_store_ids:
      raise HTTPException(status_code=403, detail="FORBIDDEN: Không có quyền thao tác trên gian hàng này")
  ```
- Backend không bao giờ tin tưởng `store_id` hoặc `user_id` do Frontend tự gửi nếu không đối chiếu với Session Token đã xác thực.

---

## 3. BẢO MẬT TÍCH HỢP OPENROUTER AI & CHỐNG PROMPT INJECTION

1. **Bảo vệ API Key:**
   - Khóa bí mật `OPENROUTER_API_KEY` chỉ tồn tại trong biến môi trường phía Server (`.env`).
   - Frontend không có quyền đọc hay truy vấn API key.
2. **Ngăn chặn Prompt Injection:**
   - Dữ liệu câu hỏi từ người dùng được đặt nghiêm ngặt trong khối thẻ cô lập `<user_query>...</user_query>`.
   - Các từ khóa chỉ thị hệ thống như `SYSTEM:`, `IGNORE PREVIOUS INSTRUCTIONS`, `DROP TABLE`, `GRANT ADMIN` bị bộ lọc chặn đứng ngay tại tầng tiền xử lý.
3. **Giới hạn ngữ cảnh (Bounded Context Retrieval):**
   - AI chỉ được cung cấp dữ liệu nghiệp vụ rút gọn trích xuất từ SQLite (danh sách cửa hàng, POI, khuyến mãi đang hoạt động).
   - Tuyệt đối không cho phép AI tự sinh hoặc thực thi các câu lệnh SQL tùy ý.
4. **Fallback nội bộ khi mất mạng:**
   - Khi dịch vụ OpenRouter mất kết nối hoặc timeout quá $10.0\text{ giây}$, hệ thống tự động kích hoạt bộ máy phản hồi quy tắc tiếng Việt nội bộ (Rule-based Engine) mà không làm sập ứng dụng.

---

## 4. NHẬT KÝ KIỂM TOÁN THAO TÁC (AUDIT LOGGING)

Mọi thao tác nhạy cảm đều được ghi nhận vĩnh viễn vào bảng `audit_logs`:
- **`user_id` / `username` / `role`**: Người thực hiện thao tác.
- **`action`**: `LOGIN`, `CREATE_USER`, `TOGGLE_USER_STATUS`, `CREATE_PROMOTION`, `EMERGENCY_RESET`, `BACKUP_DATABASE`.
- **`resource`**: Tên đối tượng bị tác động (`DATABASE`, `PROMOTION`, `MOTOR`, `USER`).
- **`ip_address` & `created_at`**: Địa chỉ IP mạng và dấu thời gian chính xác.
