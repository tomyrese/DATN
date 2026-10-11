# HƯỚNG DẪN KẾT NỐI TỪ XA AN TOÀN CHO ROBOT TTTM (REMOTE CONNECTION GUIDE V2.0)

Tài liệu hướng dẫn cấu hình truy cập từ xa qua mạng Internet cho Robot Trung Tâm Thương Mại mà **không cần mở cổng (Port Forwarding)**, không cần IP tĩnh, vượt qua mọi tường lửa NAT/CGNAT của TTTM và đảm bảo an toàn thông tin theo chuẩn doanh nghiệp.

---

## 1. MÔ HÌNH KIẾN TRÚC KẾT NỐI TỪ XA

```
[ Người Dùng Ngoài Internet / 4G / Trình Duyệt ]
                       │
                       ▼ (HTTPS / WSS Chuẩn TLS 1.3)
      [ Mạng Cận Biên Cloudflare Edge ]
                       │
                       ▼ (Mã Hóa Đường Hầm Ngược - Outbound-Only Tunnel)
[ Daemon cloudflared trên Raspberry Pi 4 ]
                       │
                       ▼ (Localhost HTTP / WS)
[ FastAPI Server (Port 8765) trên Robot ]
       ├── Xác thực RBAC (Guest / Staff / Admin)
       ├── API Key OpenRouter lưu trữ an toàn trong .env
       └── Tầng Điều Khiển Phần Cứng & An Toàn Vật Lý
```

### Ưu điểm vượt trội:
1. **Không mở cổng Inbound (Zero Open Ports):** Raspberry Pi chỉ chủ động kết nối ra ngoài (Outbound) tới Cloudflare Edge. Kẻ tấn công quét IP trên Internet sẽ không thấy bất kỳ cổng nào mở trên mạng Wi-Fi của TTTM.
2. **Chứng chỉ SSL/TLS tự động:** Kết nối qua Internet luôn được mã hóa HTTPS và WSS an toàn.
3. **Chống tấn công DDoS:** Cloudflare tự động lọc các lưu lượng độc hại trước khi chuyển tiếp tới Raspberry Pi.

---

## 2. QUY TRÌNH THIẾT LẬP NHANH TRÊN RASPBERRY PI (QUICK SETUP)

### Bước 1: Khởi động Robot Backend
```bash
cd ~/KLTN/Code
python3 src/main.py
```

### Bước 2: Kích hoạt Cloudflare Tunnel
Dự án đã tích hợp sẵn script tự động tải và kích hoạt:
```bash
bash scripts/setup_cloudflare_tunnel.sh
```
Chọn tùy chọn **1 (Quick Free Tunnel)**. Terminal sẽ xuất ra đường link công khai có định dạng:
```
https://pi-robot-mall-xxx.trycloudflare.com
```

### Bước 3: Cấu hình trên Frontend Web Dashboard
1. Truy cập vào trang Web Dashboard trên điện thoại hoặc máy tính.
2. Vào phần **Cài Đặt (Settings)**.
3. Nhập đường dẫn Tunnel (ví dụ `https://pi-robot-mall-xxx.trycloudflare.com`) vào ô **Backend Server URL**.
4. Nhấn **"Lưu & Kết Nối"**. Giao diện sẽ tự động kết nối lại WebSocket và cập nhật trạng thái thời gian thực.

---

## 3. NGUYÊN TẮC BẢO MẬT KHI TRUY CẬP TỪ XA

1. **Khách tham quan (Guest):** Chỉ có thể tra cứu thông tin tĩnh, hỏi đáp AI và gửi yêu cầu dẫn đường. Tuyệt đối không thể kích hoạt động cơ hoặc xem camera qua liên kết Internet.
2. **Nhân viên & Quản trị viên:** Bắt buộc đăng nhập tài khoản. Mọi hành động nhạy cảm (Lái xe, E-Stop, Sửa khuyến mãi, Thêm tài khoản) đều được ghi vào bảng `audit_logs` cùng địa chỉ IP và mã người dùng.
3. **Vé xem Camera (Stream Ticket):** Luồng video CSI MJPEG chỉ mở khi client cung cấp Ticket hợp lệ được cấp trong vòng 30 giây qua API xác thực. Không chia sẻ link video trực tiếp ra ngoài Internet.
