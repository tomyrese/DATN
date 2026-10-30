# HƯỚNG DẪN IN ẤN VÀ LÀM MẠCH IN THỦ CÔNG (PCB DIY GUIDE)

Bộ tài liệu PDF này được xuất chuẩn từ KiCad 10, đúng tỷ lệ vật lý **1:1 (Scale 100%)** với các tùy chọn tối ưu cho từng phương pháp làm mạch in 1 lớp (`B.Cu`).

---

## 1. Danh sách các file PDF trong thư mục

| Tên File | Công Dụng | Đặc Tính Kỹ Thuật | Phương Pháp Khuyên Dùng |
| :--- | :--- | :--- | :--- |
| **`01_Mach_In_Day_B_Cu_MIRROR_Ui_Nhiet.pdf`** | In đường mạch mặt dưới để ủi nhiệt | Tỷ lệ 1:1, Đen trắng, **Lật gương (Mirror)**, Tâm lỗ khoan nhỏ (`Drill Mark`) | **Ủi nhiệt bằng bàn là / Máy cán nhiệt ép decal, giấy bóng, giấy in ảnh** |
| **`02_Mach_In_Day_B_Cu_DIRECT_In_Film.pdf`** | In đường mạch mặt dưới theo chiều thuận | Tỷ lệ 1:1, Đen trắng, **Chiều thuận (Direct)**, Tâm lỗ khoan nhỏ | **In film trong suốt, rọi đèn UV / cảm quang, CNC phay mạch** |
| **`03_Mat_Tren_Linh_Kien_F_Silkscreen.pdf`** | In vị trí linh kiện mặt trên | Tỷ lệ 1:1, Đen trắng, Chiều thuận | In lên giấy decal hoặc in lụa mặt trên để định vị chân khi cắm |
| **`04_Huong_Dan_Lap_Rap_Mau.pdf`** | Bản vẽ màu tổng hợp đầy đủ khung tên | Tỷ lệ 1:1, Đầy đủ màu sắc, Pad thực tế, Khung tên bản vẽ kỹ thuật | Dùng để soi chiếu trên màn hình hoặc in màu khi hàn linh kiện |
| **`05_So_Do_Nguyen_Ly_Schematic.pdf`** | Toàn bộ sơ đồ nguyên lý mạch điện | Khổ A3 tiêu chuẩn, rõ ràng từng nhãn mạng và khối mạch | Đối chiếu tín hiệu, đo kiểm điện áp khi kiểm tra mạch |
| **`00_Bo_Tai_Lieu_Lam_Mach_Day_Du.pdf`** | File gộp đa trang (Multipage) | Chứa đầy đủ các lớp mạch trên 1 file duy nhất | Lưu trữ và in ấn hàng loạt |

---

## 2. Lưu ý QUAN TRỌNG KHI IN để không bị lệch chân 2.54mm

> [!CAUTION]
> **Cài đặt máy in khi in file PDF:**
> * Trong hộp thoại In (Print Dialog) của Adobe Acrobat / Foxit Reader / Trình duyệt Chrome:
>   * **Page Sizing & Handling:** Bắt buộc chọn **`Actual Size`** hoặc **`Custom Scale: 100%`**.
>   * **TUYỆT ĐỐI KHÔNG CHỌN:** `Fit`, `Shrink oversized pages`, hoặc `Scale to fit paper`.
>   * Nếu chọn Fit/Shrink, mạch sẽ bị co lại khoảng 3-5%, làm cho chân cắm Raspberry Pi 4 (40 chân) và TB6612FNG không cắm vừa lỗ khoan!

---

## 3. Quy trình làm mạch ủi nhiệt (Toner Transfer) khuyến nghị

1. **Chuẩn bị:**
   * Giấy in nhiệt (giấy thuốc vàng, giấy decal lột đế, hoặc giấy in ảnh bóng mỏng Couche).
   * Phôi đồng 1 mặt kích thước tối thiểu $145 \times 115\text{ mm}$ (Mạch thực tế là $140 \times 110\text{ mm}$).
   * Máy in laser đen trắng (In đậm nhất có thể, mật độ mực cao - High Quality).
2. **In mạch:**
   * Sử dụng file: **`01_Mach_In_Day_B_Cu_MIRROR_Ui_Nhiet.pdf`**.
3. **Ủi mực sang phôi đồng:**
   * Làm sạch và đánh bóng mặt đồng bằng bùi nhùi nhôm hoặc giấy ráp mịn (P1000 - P1500).
   * Đặt mặt giấy in mực úp vào phôi đồng, dùng băng dính chịu nhiệt cố định 4 góc.
   * Chỉnh nhiệt độ bàn là khoảng $180^\circ\text{C} - 200^\circ\text{C}$ (mức Cotton / Linen), ép đều bề mặt trong 5 - 8 phút.
   * Ngâm phôi vào chậu nước lạnh 10 phút rồi nhẹ nhàng bóc lớp giấy ra.
4. **Ăn mòn & Khoan lỗ:**
   * Ăn mòn bằng dung dịch muối Sắt III Clorua ($FeCl_3$) hoặc hỗn hợp $H_2O_2 + HCl$.
   * Sau khi ăn mòn xong, rửa sạch và lau lớp mực bảo vệ bằng cồn / acetone.
   * Dùng mũi khoan $0.8\text{ mm}$ khoan các lỗ linh kiện (tâm lỗ khoan trắng nhỏ trên pad sẽ tự định tâm mũi khoan chính xác).
   * Dùng mũi khoan $3.2\text{ mm}$ khoan 4 lỗ bắt ốc vít góc M3.
