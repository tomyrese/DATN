# HƯỚNG DẪN IN ẤN VÀ LÀM MẠCH IN THỦ CÔNG (PCB DIY GUIDE)
## BẢN THIẾT KẾ MỚI NHẤT & BẢN GHÉP TẤM (PANEL 4X & 2X TRÊN KHỔ A4)

Bộ tài liệu PDF này được xuất chuẩn từ KiCad 10, đúng tỷ lệ vật lý **1:1 (Scale 100%)** với các tùy chọn tối ưu cho phương pháp làm mạch in thủ công 1 lớp (`B.Cu`).

---

## 1. Thông số kỹ thuật & Cải tiến độ dày đồng (Vành khuyên Pad)
* **Kích thước bo mạch:** **`111.63 mm` $\times$ `72.94 mm`** (Diện tích: **`81.43 cm²`**).
* **Độ dày đường mạch (Trace Width):**
  * Đường tín hiệu (Signal): **`1.00 mm`** (rất to, chống đứt khi ủi nhiệt).
  * Đường nguồn & Động cơ (Power / Motor): **`1.40 mm`** (chịu dòng cao tới $3\text{A}$).
* **Kích thước chân hàn (Pad Size) & Lỗ khoan (Drill Hole) - ĐÃ ĐIỀU CHỈNH THEO YÊU CẦU:**
  * **Kích thước Pad (Size X / Size Y):** Chuẩn hóa toàn bộ về **`2.00 mm x 2.00 mm`** (theo đúng yêu cầu đưa toàn bộ Size X về 2.0mm).
  * **Đường kính lỗ khoan (Hole Size X / Y):** Giữ nguyên chuẩn **`0.80 mm`**.
  * **Vành khuyên đồng (Annular Ring):** $(2.00 - 0.80) / 2 = \mathbf{0.60\text{ mm}}$ (vành đồng siêu dày, bám chì hàn cực tốt, chống bong tróc tuyệt đối khi hàn nhiệt và khoan tay).
  * **Khoảng hở cách ly giữa các chân (Clearance):** $2.54 - 2.00 = \mathbf{0.54\text{ mm}}$ (độ hở cách ly an toàn $>0.5\text{ mm}$, loại bỏ hoàn toàn nguy cơ dính chập thiếc khi làm mạch thủ công).
  * **Tối ưu góc đường mạch:** Toàn bộ các góc rẽ vuông 90° đã được vát chéo chuẩn hóa thành góc cong vát **45° (Chamfer / Mitre)**, loại bỏ bẫy axit và đảm bảo dòng tín hiệu trơn tru.
* **Chế độ xuất hình dạng lỗ khoan (Drill Shape Option):**
  * Toàn bộ các file PDF mạch đáy (`B.Cu`) được xuất ở chế độ **lỗ khoan thực tế (Actual Drill Shape 0.8mm)**.
  * Lỗ tròn màu trắng có đường kính **`0.80 mm`**, bao bọc xung quanh là vành đồng đen dày **`0.60 mm`** rất nổi bật.
  * Khi khoan lỗ: Dùng mũi khoan **$0.8\text{ mm}$** (hoặc $1.0\text{ mm}$), vành đồng $0.60\text{ mm}$ vẫn giữ nguyên vẹn và bám chì hàn siêu chắc.

---

## 2. Danh sách 4 File PDF Chuẩn để In Mạch (Không rườm rà)

| TT | Tên File PDF | Quy Cách & Lớp In | Công Dụng & Phương Pháp Gia Công |
| :---: | :--- | :--- | :--- |
| **01** | **`01_Mat_Day_B_Cu_MIRROR_Ui_Nhiet.pdf`** | Khổ A4, **Lật gương (Mirror)**, Đen trắng, ghép 4 mạch | Chuyên dùng để **in giấy decal/giấy bóng ủi nhiệt** lên phôi đồng. Bản lật gương đảm bảo khi áp mặt giấy vào đồng và là nóng sẽ tạo ra đường mạch đúng chiều. |
| **02** | **`02_Mat_Day_B_Cu_DIRECT_In_Film.pdf`** | Khổ A4, **Chiều thuận (Direct)**, Đen trắng, ghép 4 mạch | Chuyên dùng để **in film nhựa trong suốt rọi tia UV** (phương pháp cảm quang) hoặc đưa vào máy soi / khắc CNC. |
| **03** | **`03_Mat_Tren_F_Silkscreen.pdf`** | Khổ A4, **Chiều thuận (Direct)**, Đen trắng, ghép 4 mạch | In mặt trên linh kiện (tên linh kiện, chân Pi, vị trí 6 cầu nối Jumper) để ủi/in lụa lên mặt phíp trước khi cắm chân. |
| **04** | **`04_So_Do_Nguyen_Ly_Schematic.pdf`** | Khổ A3 tiêu chuẩn, Toàn bộ sơ đồ nguyên lý | Dùng để in ra giấy hoặc mở trên màn hình để đối chiếu nhãn mạng, giá trị linh kiện khi lắp ráp. |

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
   * Phôi đồng 1 mặt: Nếu in file **`Panel_4x`** cần tấm phôi khoảng $235 \times 160\text{ mm}$; nếu in mạch đơn cần phôi tối thiểu $115 \times 75\text{ mm}$.
   * Máy in laser đen trắng (In đậm nhất có thể, mật độ mực cao - High Quality).
2. **In mạch:**
   * Sử dụng file: **`01_Mat_Day_B_Cu_MIRROR_Ui_Nhiet.pdf`**.
3. **Ủi mực sang phôi đồng:**
   * Làm sạch và đánh bóng mặt đồng bằng bùi nhùi nhôm hoặc giấy ráp mịn (P1000 - P1500).
   * Đặt mặt giấy in mực úp vào phôi đồng, dùng băng dính nhiệt cố định mép.
   * Chỉnh nhiệt độ bàn là khoảng $180^\circ\text{C} - 200^\circ\text{C}$ (mức Cotton / Linen), ép đều bề mặt trong 5 - 8 phút.
   * Ngâm phôi vào chậu nước lạnh 10 phút rồi nhẹ nhàng bóc lớp giấy ra.
4. **Ăn mòn & Khoan lỗ:**
   * Ăn mòn bằng dung dịch muối Sắt III Clorua ($FeCl_3$) hoặc hỗn hợp $H_2O_2 + HCl$.
   * Sau khi ăn mòn xong, rửa sạch và lau lớp mực bảo vệ bằng cồn / acetone.
   * Dùng mũi khoan **$1.0\text{ mm}$** khoan đồng loạt tất cả các lỗ chân linh kiện, header Raspberry Pi, TB6612, via jumper và cọc nguồn (chấm tâm định vị trên pad sẽ tự động hút và dẫn hướng mũi khoan chính xác $100\%$).
   * Dùng mũi khoan $3.2\text{ mm}$ khoan 4 lỗ bắt ốc vít góc M3.

---

## 5. Hướng dẫn hàn linh kiện & 6 Cầu nối dây (Jumpers)

Mạch được thiết kế chuẩn **1 lớp đồng đáy (B.Cu)** kết hợp **6 cầu nối dây ngắn** ở mặt trên linh kiện (đã in rõ tên và vị trí trên lớp Silkscreen mặt trước):

| Ký hiệu Jumper | Tín hiệu | Khoảng cách | Ghi chú thi công |
| :---: | :---: | :---: | :--- |
| **JMP1: SDA** | Tín hiệu I2C SDA | **32 mm** | Dây bọc cách điện nối từ via cạnh Pi sang via cạnh OLED |
| **JMP2: +3V3** | Nguồn logic 3.3V | **53 mm** | Dây bọc cách điện cấp 3.3V từ Pi sang thanh bus 3.3V cảm biến |
| **JMP3: GND_L** | Mass Driver Trái | **13 mm** | Dây nối mass ngắn qua cụm Driver trái |
| **JMP4: GND_TCRT** | Mass Cảm biến Line | **14 mm** | Dây nối mass cho cụm TCRT5000 |
| **JMP5: GND_PI4** | Mass Chân Pi 4 | **14 mm** | Dây nối mass từ chân GND của Pi 4 |
| **JMP6: VM** | Nguồn động cơ Motor | **6 mm** | Cầu nối nguồn động cơ cực ngắn |

### Thứ tự hàn linh kiện tối ưu:
1. **Bước 1:** Hàn 6 cầu nối dây jumper mặt trên trước tiên (dùng chân linh kiện cắt thừa hoặc dây điện nhỏ bọc cách điện).
2. **Bước 2:** Hàn các điện trở phân áp $1\text{ k}\Omega$ và $2\text{ k}\Omega$.
3. **Bước 3:** Hàn hàng socket cái 40 chân cho Raspberry Pi 4 và socket cho 2 module TB6612FNG, OLED 1.3".
4. **Bước 4:** Hàn các cọc đấu dây vặn ốc Domino KF301 (nguồn pin và động cơ).
5. **Bước 5:** Dùng đồng hồ VOM thang đo thông mạch để kiểm tra không bị chạm chập giữa VCC ($5\text{V}$, $3.3\text{V}$) và GND trước khi cắm Raspberry Pi và cấp nguồn!
