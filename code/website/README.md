# HỆ THỐNG GIAO DIỆN WEB ĐIỀU KHIỂN & GIÁM SÁT ROBOT TỰ HÀNH TTTM
**Đồ án Tốt nghiệp:** Thiết kế và triển khai Robot tự hành hỗ trợ giao nhận và tương tác khách hàng tại các Trung tâm thương mại  
**Phần cứng:** Raspberry Pi 4 Model B (8GB) • Bo mạch Carrier Board 1 lớp (KiCad 10) • TB6612FNG • 4 Bánh Mecanum • Camera CSI • Cảm biến siêu âm HC-SR04 • Màn hình OLED

---

## 1. Giới thiệu tổng quan

Hệ thống Website được xây dựng theo kiến trúc **Single Page Application (SPA)** hiện đại, mượt mà, phân tách **3 giao diện độc lập hoàn toàn cho 3 nhóm vai trò (Roles)**:
1. **Khách hàng (Guest / Kiosk)**: Không cần đăng nhập. Chào đón khách hàng tại Kiosk Robot, tích hợp Trợ lý Trí tuệ Nhân tạo (AI Concierge) tư vấn gian hàng và ẩm thực TTTM, nhập mã PIN/OTP 6 số để mở khoang chứa đồ nhận hàng, theo dõi biểu cảm OLED ảo của robot.
2. **Nhân viên Điều hành (Manager)**: Tài khoản do Admin cấp. Trung tâm điều phối đơn giao hàng tận bàn, xem luồng Camera CSI với lớp phủ nhận diện thị giác máy tính OpenCV, bàn điều khiển 8 hướng Mecanum và radar siêu âm né vật cản.
3. **Quản trị viên Hệ thống (Admin)**: Quản lý danh sách tài khoản Quản lý (thêm/khóa), cấu hình API Trí tuệ Nhân tạo (Google Gemini / OpenAI), can thiệp bảng phân bổ 40 chân GPIO của Bo mạch Carrier Board 1 lớp và ngắt khẩn cấp E-Stop.

Hệ thống được tối ưu hóa toàn diện:
- **Desktop**: Hiển thị bảng điều khiển nhiều cột, hỗ trợ đầy đủ phím tắt lái Mecanum (WASD / QEZC / Space).
- **Mobile / Tablet**: Thanh điều hướng dưới đáy (Bottom Navigation), bàn phím số cảm ứng lớn cho khách nhập OTP, điều tốc PWM và nút lái cảm ứng mượt mà.

---

## 2. Hướng dẫn khởi chạy Máy chủ

### Yêu cầu môi trường
- Python 3.8+ (khuyên dùng Python 3.10 – 3.12).
- Chạy trực tiếp bằng thư viện chuẩn của Python, **hoàn toàn không cần cài đặt thêm bất kỳ thư viện npm hay pip phức tạp nào**!

### Lệnh khởi chạy
```bash
# Di chuyển vào thư mục website
cd d:\Study\DATN\code\website

# Khởi chạy server tại cổng mặc định 8080
python server.py

# Hoặc tùy chọn cổng khác (ví dụ cổng 80 hoặc 5000):
python server.py 8080
```

### Truy cập giao diện
- **Trên máy tính cá nhân (Desktop)**: Mở trình duyệt truy cập `http://localhost:8080`
- **Trên điện thoại / Tablet cùng mạng Wi-Fi**: Mở trình duyệt truy cập `http://<IP_CỦA_MÁY_TÍNH_HOẶC_PI4>:8080` (Ví dụ: `http://192.168.1.15:8080`).

---

## 3. Tài khoản và Thông tin Đăng nhập Mặc định

Hệ thống được tích hợp sẵn modal **Chuyển đổi vai trò 1-chạm (One-Click Role Switcher)** ở góc phải trên cùng để kiểm thử nhanh chóng:

| Vai trò (Role) | Tên đăng nhập | Mật khẩu | Quyền hạn và Giao diện |
| :--- | :---: | :---: | :--- |
| **GUEST (Khách Hàng)** | *(Không cần)* | *(Không cần)* | Giao diện Kiosk chào đón, Nhập OTP mở hộc hàng, Trợ lý AI TTTM, Bản đồ các tầng TTTM |
| **MANAGER (Quản Lý)** | `manager` | `manager123` | Bàn điều khiển Mecanum 8 hướng, Live Camera CSI, Tạo đơn giao hàng mới, Hàng đợi đơn hàng |
| **ADMIN (Quản Trị Viên)**| `admin` | `admin123` | Quản lý tài khoản Manager (Thêm/Khóa), Cấu hình API AI (Gemini/OpenAI), Bảng 40 chân GPIO Carrier Board |

---

## 4. Tích hợp Trí tuệ Nhân tạo (AI Concierge)

Hệ thống hỗ trợ 2 chế độ AI thông minh:
1. **MegaMall Smart Edge Engine (Cục bộ - Mặc định)**:
   - Hoạt động tức thời ngay trên Raspberry Pi 4 mà không cần API key hay mạng Internet.
   - Nắm rõ thông tin các tầng tại TTTM: Tầng B1 (WinMart), Tầng 1 (Zara, Uniqlo, Highlands Coffee), Tầng 2 (Mỹ phẩm, Phúc Long Tea), Tầng 3 (TiNiWorld, Fahasa), Tầng 4 (Ẩm thực, Haidilao), Tầng 5 (CGV Cinemas IMAX).
   - Tự động thay đổi biểu cảm khuôn mặt OLED của Robot tương ứng với cảm xúc trò chuyện (`happy`, `talking`, `thinking`, `waving`, `navigate`).
   - Hỗ trợ phát âm giọng nói tiếng Việt tự nhiên (Web Speech API).
2. **Cloud AI API (Google Gemini / OpenAI)**:
   - Admin có thể vào tab **🧠 Cấu Hình Trí Tuệ Nhân Tạo** để dán API Key (Google Gemini API hoặc OpenAI).
   - Tùy biến System Prompt định hướng tính cách robot và độ nhạy nhận diện thị giác máy tính.

---

## 5. Thử nghiệm Mở Khoang Hàng bằng OTP

Để thử nghiệm tính năng nhận hàng tại Kiosk:
1. Tại giao diện **Guest**, chọn mục **Nhận Hàng Tại Robot**.
2. Bấm các số mã OTP mẫu trên bàn phím ảo:
   - **`829145`**: Đơn hàng Highlands Coffee (Mở hộc số 1)
   - **`635201`**: Đơn hàng Phúc Long Tea (Mở hộc số 2)
3. Bấm **MỞ HỘC**: Robot sẽ phát âm thanh chúc mừng, mở khóa hộc chứa đồ và hiển thị biểu cảm vui mừng trên màn hình OLED!

