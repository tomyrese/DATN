# HƯỚNG DẪN IN ẤN VÀ LÀM MẠCH IN THỦ CÔNG (PCB DIY GUIDE)
## BẢN THU GỌN VÀ GHÉP TẤM (PANEL 4X & 2X TRÊN KHỔ A4)

Bộ tài liệu PDF này được xuất chuẩn từ KiCad 10, đúng tỷ lệ vật lý **1:1 (Scale 100%)** với các tùy chọn tối ưu cho từng phương pháp làm mạch in 1 lớp (`B.Cu`).

---

## 1. Thông số kích thước sau khi thu gọn
- **Kích thước mạch ban đầu:** $140.2 \times 110.2\text{ mm}$ (nhiều khoảng trống thừa bên trong).
- **Kích thước sau khi thu gọn:** **$124.0 \times 86.0\text{ mm}$** (thu hẹp $24.2\text{ mm}$ chiều dọc và $16.2\text{ mm}$ chiều ngang, dồn các khối linh kiện lại gần nhau tối ưu diện tích).
- **Nhờ kích thước $124 \times 86\text{ mm}$**, 1 trang giấy in A4 ($297 \times 210\text{ mm}$) giờ đây có thể ghép vừa vặn **4 mạch (lưới 2 x 2)** với lề an toàn cực kỳ thoải mái!

---

## 2. Danh sách các file PDF trong thư mục

### A. Ghép nhiều bản trên 1 trang A4 (Khuyên dùng - Tiết kiệm tối đa)
| Tên File | Quy Cách | Công Dụng & Phương Pháp |
| :--- | :--- | :--- |
| **`01_Panel_4x_A4_B_Cu_MIRROR_Ui_Nhiet.pdf`** | **Ghép 4 mạch (2x2)** trên 1 tờ A4 | **Lật gương (Mirror)**, Đen trắng. Chuyên dùng để **ủi nhiệt** (giấy bóng, decal nhiệt) làm 4 bo mạch cùng lúc. |
| **`02_PANEL_4X_A4_B_Cu_DIRECT_In_Film.pdf`** | **Ghép 4 mạch (2x2)** trên 1 tờ A4 | **Chiều thuận (Direct)**, Đen trắng. Dùng **in phim trong suốt** để rọi đèn UV cảm quang hoặc máy CNC. |
| **`03_PANEL_4X_A4_F_Silkscreen.pdf`** | **Ghép 4 mạch (2x2)** trên 1 tờ A4 | Mặt trên vị trí linh kiện (Silkscreen), dùng in lụa hoặc dán decal định vị linh kiện. |
| **`04_PANEL_2X_A4_B_Cu_MIRROR_Ui_Nhiet.pdf`** | **Ghép 2 mạch (2x1)** trên 1 tờ A4 | Lật gương, dùng cho phôi đồng dạng thanh dài hoặc làm 2 bo mạch. |
| **`05_PANEL_2X_A4_B_Cu_DIRECT_In_Film.pdf`** | **Ghép 2 mạch (2x1)** trên 1 tờ A4 | Chiều thuận in film rọi UV cho 2 bo mạch. |

### B. Bản in mạch đơn (1 mạch lẻ)
| Tên File | Công Dụng | Đặc Tính Kỹ Thuật |
| :--- | :--- | :--- |
| **`06_Don_1X_Mach_Day_B_Cu_MIRROR_Ui_Nhiet.pdf`** | In 1 mạch đơn để ủi nhiệt | Tỷ lệ 1:1, Lật gương, có tâm lỗ khoan (`Drill Mark`). |
| **`07_Don_1X_Mach_Day_B_Cu_DIRECT_In_Film.pdf`** | In 1 mạch đơn để rọi film UV | Tỷ lệ 1:1, Chiều thuận. |
| **`08_Don_1X_Mat_Tren_F_Silkscreen.pdf`** | Mặt linh kiện đơn | Tỷ lệ 1:1, Chiều thuận. |
| **`09_Don_1X_Huong_Dan_Lap_Rap_Mau.pdf`** | Bản vẽ màu đối chiếu lắp ráp | Đầy đủ màu sắc, pad thực tế để soi khi hàn linh kiện. |
| **`10_So_Do_Nguyen_Ly_Schematic.pdf`** | Sơ đồ nguyên lý toàn mạch | Khổ A3 tiêu chuẩn, rõ ràng từng nhãn mạng. |

---

## 3. Lưu ý QUAN TRỌNG KHI IN để không bị lệch chân 2.54mm

> [!CAUTION]
> **Cài đặt máy in khi in file PDF:**
> * Trong hộp thoại In (Print Dialog) của Adobe Acrobat / Foxit Reader / Trình duyệt Chrome:
>   * **Page Sizing & Handling:** Bắt buộc chọn **`Actual Size`** hoặc **`Custom Scale: 100%`**.
>   * **TUYỆT ĐỐI KHÔNG CHỌN:** `Fit`, `Shrink oversized pages`, hoặc `Scale to fit paper`.
>   * Nếu chọn Fit/Shrink, mạch sẽ bị co nhỏ lại khoảng 3-5%, làm cho chân cắm Raspberry Pi 4 (40 chân) và TB6612FNG không cắm vừa lỗ khoan!

---

## 4. Quy trình làm mạch ủi nhiệt (Toner Transfer) khuyến nghị

1. **Chuẩn bị:**
   * Giấy in nhiệt (giấy thuốc vàng, giấy decal lột đế, hoặc giấy in ảnh bóng mỏng Couche).
   * Phôi đồng 1 mặt: Nếu in file **`Panel_4x`** cần tấm phôi khoảng khổ A4 ($260 \times 190\text{ mm}$); nếu in mạch đơn cần phôi tối thiểu $130 \times 90\text{ mm}$.
   * Máy in laser đen trắng (In đậm nhất có thể, mật độ mực cao - High Quality).
2. **In mạch:**
   * Sử dụng file: **`01_Panel_4x_A4_B_Cu_MIRROR_Ui_Nhiet.pdf`** (hoặc `06_Don_1X_...` nếu làm mạch đơn).
3. **Ủi mực sang phôi đồng:**
   * Làm sạch và đánh bóng mặt đồng bằng bùi nhùi nhôm hoặc giấy ráp mịn (P1000 - P1500).
   * Đặt mặt giấy in mực úp vào phôi đồng, dùng băng dính nhiệt cố định mép.
   * Chỉnh nhiệt độ bàn là khoảng $180^\circ\text{C} - 200^\circ\text{C}$ (mức Cotton / Linen), ép đều bề mặt trong 5 - 8 phút.
   * Ngâm phôi vào chậu nước lạnh 10 phút rồi nhẹ nhàng bóc lớp giấy ra.
4. **Ăn mòn & Khoan lỗ:**
   * Ăn mòn bằng dung dịch muối Sắt III Clorua ($FeCl_3$) hoặc hỗn hợp $H_2O_2 + HCl$.
   * Sau khi ăn mòn xong, rửa sạch và lau lớp mực bảo vệ bằng cồn / acetone.
   * Dùng mũi khoan $0.8\text{ mm}$ khoan các lỗ linh kiện (tâm lỗ khoan trắng nhỏ trên pad sẽ tự định tâm mũi khoan chính xác).
   * Dùng mũi khoan $3.2\text{ mm}$ khoan 4 lỗ bắt ốc vít góc M3.
