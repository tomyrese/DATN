# HƯỚNG DẪN KẾT NỐI TỪ XA & VẬN HÀNH ROBOT TRUNG TÂM THƯƠNG MẠI

Tài liệu hướng dẫn cách thiết lập kết nối từ xa (Remote Internet Control) cho Robot Raspberry Pi và cách sử dụng 2 phân hệ **Khách Hàng (Customer)** & **Nhân Viên (Staff)** trên nền tảng Website React (Vercel).

---

## I. KIẾN TRÚC KẾT NỐI TỪ XA (INTERNET ARCHITECTURE)

Khi trang web được deploy lên **Vercel** (`https://your-robot.vercel.app`):
- **Khách hàng / Nhân viên**: Truy cập từ bất kỳ thiết bị nào (điện thoại, máy tính bảng, laptop) qua 4G/5G/Wi-Fi công cộng.
- **Robot Raspberry Pi**: Chạy service **Cloudflare Tunnel (cloudflared)** tạo kết nối mã hóa hai chiều (HTTPS & WSS an toàn) ra Internet mà **không cần mở Port Forwarding, không cần IP tĩnh (Static IP)** và vượt qua mọi tường lửa NAT/CGNAT của TTTM.

```
[ Người Dùng / Trình Duyệt ]
           │
           ▼ (HTTPS / WSS)
[ Cloudflare Tunnel Edge ]
           │
           ▼ (Encrypted Secure Tunnel)
[ Raspberry Pi Robot Server (FastAPI :8765) ]
 ├── AI Mall Concierge Service (Hỏi đáp TTTM)
 ├── Escort Navigation Engine (Dẫn đường khách hàng)
 ├── Delivery Order Dispatcher (Giao hàng nội bộ)
 ├── TB6612 Motor Driver + Picamera2 CSI + SSD MobileNet V2
```

---

## II. HƯỚNG DẪN CÀI ĐẶT TRÊN RASPBERRY PI (CHỈ MẤT 2 PHÚT)

### Bước 1: Khởi động Robot Backend
Trên terminal của Raspberry Pi:
```bash
cd ~/KLTN/Code
python3 src/main.py
```

### Bước 2: Chạy Cloudflare Tunnel (Miễn phí 100%)
Dự án đã tích hợp sẵn script tự động:
```bash
bash scripts/setup_cloudflare_tunnel.sh
```

Chọn chế độ **1 (Quick Free Tunnel)**. Terminal sẽ hiển thị đường link công khai, ví dụ:
```
Your quick tunnel has been created! Visit it at:
https://pi-robot-mall-xyz.trycloudflare.com
```

### Bước 3: Cấu hình trên Website Vercel
1. Mở trang web Vercel của bạn trên điện thoại hoặc máy tính.
2. Vào tab **Cài Đặt (Settings)**.
3. Dán link `https://pi-robot-mall-xyz.trycloudflare.com` vào ô **Cloudflare Tunnel URL**.
4. Nhấn **"Lưu & Kết Nối"**.
👉 *Hệ thống sẽ tự động lưu cấu hình vào LocalStorage và duy trì kết nối WebSocket thời gian thực mọi lúc mọi nơi!*

---

## III. HƯỚNG DẪN SỬ DỤNG 2 CHẾ ĐỘ TRÊN WEBSITE

### 👥 1. Phân Hệ Dành Cho Khách Hàng (Customer Portal - Không cần đăng nhập)
Khách tham quan TTTM quét mã QR dán tại sảnh hoặc trên thân Robot để mở Web App:

1. **Bản Đồ TTTM Tương Tác (Mall Map)**:
   - Xem sơ đồ mặt bằng các tầng (Tầng 1 Sảnh chính, Tầng 2 Ẩm thực, Tầng 3 Giải trí).
   - Xem vị trí thời gian thực của Robot đang di chuyển.
   - Nhấn vào bất kỳ gian hàng nào (ZARA, UNIQLO, Highlands, WC, CGV Cinema...) và nhấn **"ROBOT DẪN TÔI ĐẾN ĐÂY"**.
   - Robot sẽ lên lộ trình và dẫn đường trực tiếp cho khách hàng.

2. **Trợ Lý Ảo Thông Minh (AI Concierge Q&A)**:
   - Trò chuyện hoặc chọn câu hỏi nhanh: *"Nhà vệ sinh gần nhất ở đâu?", "Quán cà phê ngon?", "Rạp CGV chiếu phim gì?", "Giờ mở cửa?", "WiFi miễn phí?"*.
   - Trợ lý AI trả lời tức thì kèm nút **"Dẫn đường tới địa điểm này"** để khách hàng kích hoạt xe dẫn đường ngay trong tin nhắn.

3. **Danh Mục Gian Hàng (Directory)**:
   - Tìm kiếm nhanh theo tên hoặc lọc theo danh mục: Ẩm thực, Thời trang, Giải trí, Tiện ích WC.

---

### 🛡️ 2. Phân Hệ Dành Cho Nhân Viên Vận Hành (Staff Portal)
Nhân viên nhấn nút **"KHÁCH THAM QUAN"** trên Header -> Quét mã QR trên màn hình OLED của Robot hoặc nhập mã PIN 6 ký tự để mở khóa:

1. **Quản Lý Giao Hàng Nội Bộ (Delivery Dispatcher)**:
   - **Đặt đơn giao hàng mới**: Chọn Điểm lấy hàng (ví dụ: *Kho B1, Quầy giao nhận T1, Shop Zara*) -> Chọn Điểm giao đích (ví dụ: *Quầy Lễ Tân, Sảnh Tây, Quầy CSKH*) -> Nhập tên kiện hàng -> Nhấn **"Xác Nhận Điều Phối"**.
   - **Theo dõi tiến độ đơn hàng**:
     - *Chờ điều phối* ➔ *Robot đang đến lấy hàng* ➔ *Đã đến điểm lấy (Nhân viên xếp hàng lên xe)* ➔ *Đang vận chuyển tới đích* ➔ *Hoàn thành giao hàng*.

2. **Điều Khiển Thủ Công & Camera CSI (Drive & CSI Vision)**:
   - Lái xe bằng bàn phím phím tắt (**W/A/S/D**, **Space**, **E-Stop**, **Reset**).
   - Xem trực tiếp video từ camera góc rộng CSI độ trễ siêu thấp (<80ms) kèm khung nhận diện AI chống va chạm người đi bộ.
   - Kiểm tra nhiệt độ CPU, RAM, điện áp và bench test độc lập 4 kênh động cơ DC.
