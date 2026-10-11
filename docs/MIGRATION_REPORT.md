# BÁO CÁO CHUYỂN ĐỔI CƠ SỞ DỮ LIỆU & QUY TRÌNH KHÔI PHỤC (MIGRATION REPORT)

Báo cáo chi tiết về quy trình nâng cấp cấu trúc cơ sở dữ liệu SQLite từ phiên bản cũ lên phiên bản chuẩn hóa v2.0, cơ chế tự động sao lưu và kế hoạch khôi phục (Rollback Plan).

---

## 1. TỔNG QUAN CHUYỂN ĐỔI

- **Hệ quản trị:** SQLite 3.
- **Tệp cơ sở dữ liệu:** `data/mall_delivery.db`.
- **Cấu hình tối ưu:**
  - Chế độ nhật ký: `PRAGMA journal_mode = WAL;` (Write-Ahead Logging).
  - Ràng buộc khóa ngoại: `PRAGMA foreign_keys = ON;` (Kích hoạt bắt buộc).
  - Khóa đồng thời: `PRAGMA busy_timeout = 10000;` (10 giây).
- **Bộ công cụ chuyển đổi:** `src/database/migrator.py` (`DatabaseMigrator`).

---

## 2. LỊCH SỬ CÁC PHIÊN BẢN MIGRATION ĐÃ ÁP DỤNG

### Migration 1: Full v2.0 Normalized Schema
- **Thời điểm áp dụng:** Hoàn tất thành công tại Phase 2.
- **Mục tiêu:** Thiết lập 19 bảng chuẩn hóa thay thế cho các bảng rời rạc không ràng buộc trước đây:
  - Phân quyền & Tài khoản: `users`, `roles`, `user_roles`, `staff_store_assignments`, `user_sessions`, `audit_logs`.
  - Trung tâm thương mại & Bản đồ: `mall_floors`, `stores`, `store_categories`, `store_hours`, `mall_pois`, `map_nodes`, `map_edges`, `restricted_zones`, `patrol_routes`, `patrol_route_waypoints`.
  - Khuyến mãi & FAQ: `promotions`, `promotion_stores`, `mall_faqs`.
  - Robot & Giao hàng: `robots`, `robot_tasks`, `delivery_orders`.
- **Toàn vẹn dữ liệu:** Toàn bộ bảng đều có Primary Key, Foreign Key với `ON DELETE CASCADE` / `ON DELETE RESTRICT` rõ ràng và chỉ mục (Indexes) trên các cột truy vấn thường xuyên.

### Migration 2: Delivery Order Creator User Scoping
- **Thời điểm áp dụng:** Hoàn tất thành công tại Phase 2.
- **Nội dung:** Bổ sung trường `creator_user_id TEXT` vào bảng `delivery_orders` với liên kết khóa ngoại tham chiếu tới `users(id)`:
  ```sql
  ALTER TABLE delivery_orders ADD COLUMN creator_user_id TEXT REFERENCES users(id);
  ```
- **Mục đích:** Hỗ trợ phân quyền truy vết nhân viên kho / nhân viên quầy tạo đơn giao hàng nội bộ.

---

## 3. CƠ CHẾ SAO LƯU TỰ ĐỘNG (ATOMIC BACKUP)

Trước khi thực thi bất kỳ câu lệnh chuyển đổi schema nào, `DatabaseMigrator.backup_database()` tự động tạo bản sao lưu snapshot đầy đủ:
- Tệp sao lưu định dạng: `data/mall_delivery.db.backup_<UNIX_TIMESTAMP>`.
- Được sao chép nguyên trạng ở mức byte (shutil.copy2) bao gồm cả chỉ mục và dữ liệu cũ.
- Ngoài ra, Quản trị viên có thể kích hoạt sao lưu tức thời bất cứ lúc nào qua API `POST /api/v1/admin/backup-db` hoặc nút bấm trên Admin Dashboard.

---

## 4. KẾ HOẠCH KHÔI PHỤC KHI CÓ SỰ CỐ (ROLLBACK PROCEDURES)

Nếu xảy ra sự cố hỏng dữ liệu hoặc xung đột phiên bản phần mềm:

### Bước 1: Dừng dịch vụ Robot
```bash
# Trên Raspberry Pi
sudo systemctl stop pi-robot.service

# Hoặc trên máy phát triển (tắt tiến trình Python)
taskkill /F /IM python.exe
```

### Bước 2: Xác định tệp sao lưu gần nhất
```bash
ls -la data/mall_delivery.db.backup_*
```

### Bước 3: Phục hồi cơ sở dữ liệu từ bản sao lưu
```bash
# Đổi tên tệp lỗi thành bản ghi sự cố
mv data/mall_delivery.db data/mall_delivery.db.corrupted

# Phục hồi tệp sao lưu về vị trí chính
cp data/mall_delivery.db.backup_<TIMESTAMP> data/mall_delivery.db
```

### Bước 4: Kiểm tra tính toàn vẹn (Integrity Check)
```bash
sqlite3 data/mall_delivery.db "PRAGMA integrity_check;"
# Kết quả phải trả về: "ok"

sqlite3 data/mall_delivery.db "PRAGMA foreign_key_check;"
# Kết quả không trả về lỗi nào
```

### Bước 5: Khởi động lại dịch vụ
```bash
sudo systemctl start pi-robot.service
sudo systemctl status pi-robot.service
```
