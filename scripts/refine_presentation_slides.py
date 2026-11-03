import os, sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

sys.stdout.reconfigure(encoding='utf-8')

PPTX_FILE = 'KLTN_DeCuong_NguyenPhuQuy_LeMinhNgoc.pptx'

NAVY_COLOR = RGBColor(15, 43, 72)
TEXT_COLOR = RGBColor(40, 40, 40)
HEADER_RED = RGBColor(160, 20, 20)

def apply_items_to_tf(tf, items, title=None, title_size=15.0, item_size=13.5, space_after=Pt(7.0), line_spacing=1.20, m_top=0.08, m_bottom=0.08, m_left=0.10, m_right=0.10):
    """Fills a text frame with clean, styled paragraphs."""
    tf.margin_left = Inches(m_left)
    tf.margin_right = Inches(m_right)
    tf.margin_top = Inches(m_top)
    tf.margin_bottom = Inches(m_bottom)
    tf.word_wrap = True

    while len(tf.paragraphs) > 1:
        p_last = tf.paragraphs[-1]._p
        p_last.getparent().remove(p_last)

    p0 = tf.paragraphs[0]
    p0.text = ""

    if title:
        p0.text = title
        p0.line_spacing = line_spacing
        p0.space_after = space_after
        for r in p0.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(title_size)
            r.font.bold = True
            r.font.color.rgb = NAVY_COLOR

    first = True if not title else False

    for bold_pre, norm_txt in items:
        if first:
            p = p0
            first = False
        else:
            p = tf.add_paragraph()

        p.line_spacing = line_spacing
        p.space_after = space_after

        if bold_pre:
            r1 = p.add_run()
            r1.text = bold_pre + (" " if not bold_pre.endswith(" ") and norm_txt else "")
            r1.font.name = "Times New Roman"
            r1.font.size = Pt(item_size)
            r1.font.bold = True
            r1.font.color.rgb = NAVY_COLOR

        if norm_txt:
            r2 = p.add_run()
            r2.text = norm_txt
            r2.font.name = "Times New Roman"
            r2.font.size = Pt(item_size)
            r2.font.bold = False
            r2.font.color.rgb = TEXT_COLOR


def set_box_geometry(shape, top=None, left=None, width=None, height=None):
    """Adjusts shape position and size."""
    if top is not None: shape.top = Inches(top)
    if left is not None: shape.left = Inches(left)
    if width is not None: shape.width = Inches(width)
    if height is not None: shape.height = Inches(height)


def main():
    print(f"Loading presentation: {PPTX_FILE}...")
    prs = Presentation(PPTX_FILE)

    # ==================== SLIDE 2: ĐẶT VẤN ĐỀ & TÍNH CẤP THIẾT ====================
    print("Slide 2: Refining Đặt vấn đề & Tính cấp thiết...")
    s2 = prs.slides[1]
    set_box_geometry(s2.shapes[4], top=1.18, left=0.72, width=2.56, height=4.00)
    set_box_geometry(s2.shapes[6], top=1.18, left=3.72, width=2.56, height=4.00)
    set_box_geometry(s2.shapes[8], top=1.18, left=6.72, width=2.56, height=4.00)

    apply_items_to_tf(s2.shapes[4].text_frame, [
        ("Mặt sàn rộng lớn:", "Nhiều tầng, mật độ gian hàng và khách mua sắm đông đúc."),
        ("Nhu cầu giao nhận:", "Cần vận chuyển liên tục tài liệu, bưu kiện giữa các quầy."),
        ("Hỗ trợ tìm đường:", "Khách hàng thường xuyên cần chỉ dẫn gian hàng và tiện ích.")
    ], title="1. BỐI CẢNH", title_size=15.0, item_size=13.5, space_after=Pt(8), line_spacing=1.22)

    apply_items_to_tf(s2.shapes[6].text_frame, [
        ("Tốn kém nhân lực:", "Phụ thuộc chuyển phát thủ công, dễ chậm giờ cao điểm."),
        ("Nguy cơ nhầm lẫn:", "Dễ thất lạc hoặc nhầm địa chỉ nhận bưu kiện nội bộ."),
        ("Hỗ trợ bị động:", "Quầy thông tin cố định, không thể di chuyển dẫn đường cho khách.")
    ], title="2. THÁCH THỨC", title_size=15.0, item_size=13.5, space_after=Pt(8), line_spacing=1.22)

    apply_items_to_tf(s2.shapes[8].text_frame, [
        ("Robot 4 bánh Mecanum:", "Di chuyển đa hướng linh hoạt, tự động né vật cản."),
        ("Bo mạch tích hợp:", "Chuẩn 1 lớp chống rung lắc, cấp nguồn 5V-5A ổn định."),
        ("Điều khiển qua Web:", "Giao diện trực quan, giám sát hành trình qua Wi-Fi."),
        ("Trợ lý AI & OLED:", "Tạo mã QR động, hỏi đáp thông minh hỗ trợ khách.")
    ], title="3. GIẢI PHÁP", title_size=15.0, item_size=13.0, space_after=Pt(6), line_spacing=1.18)

    # ==================== SLIDE 3: MỤC TIÊU VÀ PHẠM VI ====================
    print("Slide 3: Refining Mục tiêu và Phạm vi...")
    s3 = prs.slides[2]
    set_box_geometry(s3.shapes[4], top=1.18, left=0.80, width=3.90, height=4.00)
    set_box_geometry(s3.shapes[6], top=1.18, left=5.30, width=3.90, height=4.00)

    apply_items_to_tf(s3.shapes[4].text_frame, [
        ("Thiết kế phần cứng:", "Chế tạo Carrier Board 1 lớp chuẩn KiCad 10, cấp nguồn 5V-5A bền bỉ."),
        ("Điều khiển tự hành:", "Lập trình 4 bánh Mecanum di chuyển êm, bám vạch sàn và né vật cản."),
        ("Hệ thống Web điều khiển:", "Giao diện Web Dashboard lái xe và giám sát thời gian thực qua Wi-Fi."),
        ("Dịch vụ số & Trợ lý AI:", "Quản lý đơn giao nhận nội bộ và tích hợp trợ lý AI hỏi đáp thân thiện.")
    ], title="MỤC TIÊU CỐT LÕI", title_size=15.0, item_size=13.5, space_after=Pt(8), line_spacing=1.22)

    apply_items_to_tf(s3.shapes[6].text_frame, [
        ("Không gian hoạt động:", "Khu vực trong nhà, mặt sàn bằng phẳng tại trung tâm thương mại."),
        ("Tải trọng chuyên chở:", "Vận chuyển bưu kiện, hàng mẫu và tài liệu trọng lượng dưới 1.0 kg."),
        ("Truyền thông không dây:", "Mạng Wi-Fi nội bộ tốc độ cao, phản hồi điều khiển độ trễ mili-giây."),
        ("Thời lượng pin:", "Bộ pin sạc Li-ion dung lượng cao hoạt động liên tục từ 1.5 đến 2.5 giờ.")
    ], title="PHẠM VI VÀ GIỚI HẠN", title_size=15.0, item_size=13.5, space_after=Pt(8), line_spacing=1.22)

    # ==================== SLIDE 4: KẾ HOẠCH VÀ TIẾN ĐỘ (TABLE) ====================
    print("Slide 4: Refining Table Tiến độ thực hiện...")
    s4 = prs.slides[3]
    for shape in s4.shapes:
        if shape.has_table:
            t = shape.table
            t.columns[0].width = Inches(1.80)
            t.columns[1].width = Inches(4.55)
            t.columns[2].width = Inches(2.55)

            table_data = [
                ["Giai đoạn", "Nội dung thực hiện chi tiết", "Kết quả / Sản phẩm bàn giao"],
                ["GĐ 1 (Tuần 1 - 3)", "Khảo sát thực tế TTTM, xác định yêu cầu chức năng & mục tiêu đề tài.", "Đề cương chi tiết KLTN"],
                ["GĐ 2 (Tuần 4 - 7)", "Thiết kế kiến trúc tổng thể, vẽ sơ đồ nguyên lý 4 khối chức năng KiCad 10.", "Sơ đồ nguyên lý (.kicad_sch)"],
                ["GĐ 3 (Tuần 8 - 9)", "Lập trình tầng driver Python điều khiển động cơ TB6612, siêu âm & dò line.", "Module Python Motor Driver"],
                ["GĐ 4 (Tuần 10 - 14)", "Thiết kế bo mạch Carrier PCB 1 lớp, xuất bản vẽ gia công & hàn linh kiện.", "Bo mạch Carrier hoàn thiện"],
                ["GĐ 5 (Tuần 15 - 17)", "Xây dựng Web Dashboard điều khiển, phân quyền người dùng và CSDL.", "Giao diện Web điều khiển Wi-Fi"],
                ["GĐ 6 (Tuần 18 - 20)", "Tích hợp thuật toán né vật cản, quy trình giao nhận bưu kiện & API AI.", "Robot tự hành đồng bộ"],
                ["GĐ 7 (Tuần 21 - 24)", "Thử nghiệm thực địa TTTM, đo đạc sai số, hoàn thiện thuyết minh tốt nghiệp.", "Sản phẩm thực tế & Báo cáo"]
            ]
            for r_idx, row in enumerate(t.rows):
                for c_idx, cell in enumerate(row.cells):
                    cell.text = ""
                    p = cell.text_frame.paragraphs[0]
                    p.line_spacing = 1.15
                    r = p.add_run()
                    r.text = table_data[r_idx][c_idx]
                    r.font.name = "Times New Roman"
                    if r_idx == 0:
                        r.font.size = Pt(13.0)
                        r.font.bold = True
                        r.font.color.rgb = RGBColor(255, 255, 255)
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = NAVY_COLOR
                    else:
                        r.font.size = Pt(12.0)
                        r.font.bold = (c_idx == 0)
                        r.font.color.rgb = TEXT_COLOR
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = RGBColor(255, 255, 255) if r_idx % 2 == 1 else RGBColor(245, 247, 250)

    # ==================== SLIDE 5: LINH KIỆN CỐT LÕI ====================
    print("Slide 5: Refining 6 Linh kiện cốt lõi (strict single-line bullets)...")
    s5 = prs.slides[4]
    set_box_geometry(s5.shapes[5], top=1.14, left=1.92, width=2.95, height=1.24)
    set_box_geometry(s5.shapes[8], top=1.14, left=6.38, width=2.95, height=1.24)
    set_box_geometry(s5.shapes[11], top=2.66, left=1.92, width=2.95, height=1.24)
    set_box_geometry(s5.shapes[14], top=2.66, left=6.38, width=2.95, height=1.24)
    set_box_geometry(s5.shapes[16], top=4.18, left=1.92, width=2.95, height=1.24)
    set_box_geometry(s5.shapes[19], top=4.18, left=6.38, width=2.95, height=1.24)

    apply_items_to_tf(s5.shapes[5].text_frame, [
        ("Cấu hình:", "CPU 4 nhân Cortex, 8GB RAM"),
        ("Kết nối:", "Wi-Fi kép, CSI & 40 chân GPIO")
    ], title="Raspberry Pi 4 Model B (8GB)", title_size=12.5, item_size=11.5, space_after=Pt(2.0), line_spacing=1.10, m_top=0.05, m_bottom=0.03, m_left=0.06, m_right=0.06)

    apply_items_to_tf(s5.shapes[8].text_frame, [
        ("Công nghệ:", "MOSFET kép tải 1.2A/kênh"),
        ("Điều khiển:", "4 kênh xung PWM điều tốc xe")
    ], title="Driver Động Cơ TB6612FNG", title_size=12.5, item_size=11.5, space_after=Pt(2.0), line_spacing=1.10, m_top=0.05, m_bottom=0.03, m_left=0.06, m_right=0.06)

    apply_items_to_tf(s5.shapes[11].text_frame, [
        ("Pin Li-ion 12V:", "Cấp nguồn động lực xe"),
        ("Hạ áp 5V-5A:", "Nuôi Pi 4 & tải, chung mass")
    ], title="Khối Nguồn Năng Lượng", title_size=12.5, item_size=11.5, space_after=Pt(2.0), line_spacing=1.10, m_top=0.05, m_bottom=0.03, m_left=0.06, m_right=0.06)

    apply_items_to_tf(s5.shapes[14].text_frame, [
        ("Chuẩn I²C:", "Giao tiếp 2 dây gọn gàng"),
        ("Hiển thị:", "Báo IP mạng, pin & mã QR")
    ], title="Màn Hình OLED 1.3\" I²C", title_size=12.5, item_size=11.5, space_after=Pt(2.0), line_spacing=1.10, m_top=0.05, m_bottom=0.03, m_left=0.06, m_right=0.06)

    apply_items_to_tf(s5.shapes[16].text_frame, [
        ("Cự ly đo:", "2cm - 400cm quét né vật cản"),
        ("Phân áp 3.3V:", "Trở 1k/2k bảo vệ GPIO")
    ], title="Cảm Biến Siêu Âm HC-SR04", title_size=12.5, item_size=11.5, space_after=Pt(2.0), line_spacing=1.10, m_top=0.05, m_bottom=0.03, m_left=0.06, m_right=0.06)

    apply_items_to_tf(s5.shapes[19].text_frame, [
        ("Ống kính 5MP:", "Góc nhìn 72.4° sắc nét"),
        ("Chuẩn CSI:", "Cáp bẹ cắm trực tiếp Pi 4")
    ], title="Camera Quan Sát CSI OV5647", title_size=12.5, item_size=11.5, space_after=Pt(2.0), line_spacing=1.10, m_top=0.05, m_bottom=0.03, m_left=0.06, m_right=0.06)

    # ==================== SLIDE 6: THIẾT KẾ BO MẠCH ROBOT ====================
    print("Slide 6: Refining Thiết kế Bo mạch Carrier...")
    s6 = prs.slides[5]
    set_box_geometry(s6.shapes[4], top=1.18, left=0.80, width=3.90, height=4.00)
    set_box_geometry(s6.shapes[6], top=1.18, left=5.30, width=3.90, height=4.00)

    apply_items_to_tf(s6.shapes[4].text_frame, [
        ("Khắc phục rung lắc:", "Thay dây cắm testboard lỏng lẻo bằng bo mạch cắm nối chuẩn hóa."),
        ("Cách ly nguồn điện:", "Tách riêng nguồn 12V động cơ và 5V vi xử lý để chống sụt áp."),
        ("Bảo vệ cổng GPIO:", "Tích hợp cụm trở phân áp 1kΩ / 2kΩ bảo vệ mức áp 3.3V cho Pi 4."),
        ("Chế tạo thuận tiện:", "Thiết kế 1 lớp đồng mặt đáy, phù hợp tự ủi nhiệt gia công thực tế.")
    ], title="ĐẶT VẤN ĐỀ & GIẢI PHÁP", title_size=14.5, item_size=13.5, space_after=Pt(8), line_spacing=1.22)

    apply_items_to_tf(s6.shapes[6].text_frame, [
        ("Cấu trúc mạch:", "1 lớp đồng (Single-sided), đi dây toàn bộ mặt đáy B.Cu."),
        ("Cầu nối (Jumper):", "Chỉ 5 cầu nối mặt trên F.Cu, bố trí thẳng hàng dễ cắm."),
        ("Đường nét đồng:", "Nguồn 1.5 - 2.0mm dẫn dòng lớn; tín hiệu 0.8mm dễ ủi."),
        ("Khoảng hở an toàn:", "Khoảng cách giữa các nét ≥ 0.5mm, đạt chuẩn DRC 0 lỗi."),
        ("Kích thước bo mạch:", "111.6 × 72.9mm, bắt vừa vặn khung xe Mecanum.")
    ], title="THÔNG SỐ & TIÊU CHUẨN MẠCH", title_size=14.0, item_size=13.0, space_after=Pt(6.5), line_spacing=1.18)

    # ==================== SLIDE 8: SƠ ĐỒ KHỐI TỔNG THỂ ====================
    print("Slide 8: Refining Sơ đồ khối tổng thể...")
    s8 = prs.slides[7]
    set_box_geometry(s8.shapes[4], top=1.15, left=0.35, width=3.85, height=3.80)
    apply_items_to_tf(s8.shapes[4].text_frame, [
        ("1. Xử lý trung tâm:", "Raspberry Pi 4 điều phối thuật toán, xử lý ảnh và Web Server."),
        ("2. Tín hiệu & Cảm biến:", "Siêu âm né vật cản, cảm biến dò line và camera quan sát."),
        ("3. Công suất & Hiển thị:", "2 mạch TB6612 kéo 4 động cơ Mecanum và màn hình OLED."),
        ("4. Nguồn năng lượng:", "Pin Li-ion 12V, mạch Buck hạ áp 5V-5A và cầu chì bảo vệ.")
    ], title="CẤU TRÚC 4 PHÂN HỆ CHÍNH", title_size=15.0, item_size=13.5, space_after=Pt(6.5), line_spacing=1.18)

    # ==================== SLIDE 9: KHỐI 1 - NGUỒN ĐIỆN ====================
    print("Slide 9: Refining Khối 1 - Nguồn điện...")
    s9 = prs.slides[8]
    set_box_geometry(s9.shapes[4], top=1.15, left=0.35, width=3.85, height=3.80)
    apply_items_to_tf(s9.shapes[4].text_frame, [
        ("Nguồn cấp chính:", "Pin sạc Li-ion 12V (3S2P) dòng xả cao nuôi toàn bộ xe."),
        ("Bảo vệ quá dòng:", "Công tắc gạt 10A & cầu chì 7.5A chống chạm chập, cháy nổ."),
        ("Đường động lực 12V:", "Cấp điện trực tiếp 2 mạch driver kéo 4 động cơ bánh xe."),
        ("Hạ áp nuôi vi xử lý:", "Mạch Buck 5V-5A nuôi Pi 4 & cảm biến, chung mass chống sụt áp.")
    ], title="KHỐI 1 - NGUỒN NĂNG LƯỢNG", title_size=15.0, item_size=13.5, space_after=Pt(6.5), line_spacing=1.18)

    # ==================== SLIDE 10: KHỐI 2 - ĐIỀU KHIỂN ====================
    print("Slide 10: Refining Khối 2 - Điều khiển...")
    s10 = prs.slides[9]
    set_box_geometry(s10.shapes[4], top=1.15, left=0.35, width=3.85, height=3.80)
    apply_items_to_tf(s10.shapes[4].text_frame, [
        ("Bộ xử lý trung tâm:", "Raspberry Pi 4 Model B (RAM 8GB) vận hành hệ điều hành Linux."),
        ("Thuật toán điều hướng:", "Tính toán động học 4 bánh Mecanum và điều chế xung PWM."),
        ("Xử lý né vật cản:", "Đọc cảm biến siêu âm theo thời gian thực và quyết định góc lái."),
        ("Máy chủ Web Server:", "Cung cấp REST API nhận lệnh điều khiển và truyền video trực tiếp.")
    ], title="KHỐI 2 - ĐIỀU KHIỂN TRUNG TÂM", title_size=15.0, item_size=13.5, space_after=Pt(6.5), line_spacing=1.18)

    # ==================== SLIDE 11: KHỐI 3 - TÍN HIỆU & CẢM BIẾN ====================
    print("Slide 11: Refining Khối 3 - Tín hiệu & Cảm biến...")
    s11 = prs.slides[10]
    set_box_geometry(s11.shapes[4], top=1.15, left=0.35, width=3.85, height=3.80)
    apply_items_to_tf(s11.shapes[4].text_frame, [
        ("Cảm biến siêu âm (2 bộ):", "Quét vật cản trước trái/phải, phân áp Echo về 3.3V an toàn."),
        ("Cảm biến bám vạch (3 mắt):", "Mắt quang hồng ngoại độ nhạy cao bám vạch dẫn hướng trên sàn."),
        ("Màn hình OLED 1.3\":", "Giao tiếp I²C hiển thị IP mạng, pin, trạng thái và mã QR."),
        ("Camera quan sát 5MP:", "Truyền video độ trễ thấp về Web Dashboard để theo dõi.")
    ], title="KHỐI 3 - TÍN HIỆU & CẢM BIẾN", title_size=15.0, item_size=13.5, space_after=Pt(6.0), line_spacing=1.18)

    # ==================== SLIDE 12: KHỐI 4 - CÔNG SUẤT CHẤP HÀNH ====================
    print("Slide 12: Refining Khối 4 - Công suất chấp hành...")
    s12 = prs.slides[11]
    set_box_geometry(s12.shapes[4], top=1.15, left=0.35, width=3.85, height=3.80)
    apply_items_to_tf(s12.shapes[4].text_frame, [
        ("2 Mạch Driver riêng biệt:", "Tải dòng khỏe 1.2A/động cơ, hiệu suất cao, không sinh nhiệt lớn."),
        ("4 Động cơ giảm tốc TT:", "Kết hợp bánh Mecanum cho phép xe tịnh tiến ngang và xoay tròn."),
        ("Chế độ Standby (STBY):", "Cho phép ngắt công suất khẩn cấp tức thì qua tín hiệu điều khiển."),
        ("Bảo vệ nguồn điện:", "Tụ lọc dung lượng lớn triệt tiêu xung gai ngược từ cuộn dây động cơ.")
    ], title="KHỐI 4 - CÔNG SUẤT CHẤP HÀNH", title_size=15.0, item_size=13.5, space_after=Pt(6.0), line_spacing=1.18)

    # ==================== SLIDE 13: KIẾN TRÚC PHẦN MỀM (2x2 GRID) ====================
    print("Slide 13: Refining Kiến trúc phần mềm...")
    s13 = prs.slides[12]
    set_box_geometry(s13.shapes[4], top=1.20, left=0.75, width=4.00, height=1.90)
    set_box_geometry(s13.shapes[6], top=1.20, left=5.25, width=4.00, height=1.90)
    set_box_geometry(s13.shapes[8], top=3.40, left=0.75, width=4.00, height=1.90)
    set_box_geometry(s13.shapes[10], top=3.40, left=5.25, width=4.00, height=1.90)

    apply_items_to_tf(s13.shapes[4].text_frame, [
        ("Giao tiếp GPIO & PWM:", "Điều khiển chính xác tốc độ và chiều 4 động cơ."),
        ("Tích hợp mô phỏng:", "Thử nghiệm logic chuyển động trực tiếp trên máy tính.")
    ], title="TẦNG 1: ĐIỀU KHIỂN PHẦN CỨNG", title_size=13.5, item_size=12.0, space_after=Pt(5.0), line_spacing=1.16, m_top=0.08, m_bottom=0.08)

    apply_items_to_tf(s13.shapes[6].text_frame, [
        ("Máy chủ Python:", "Nhận lệnh di chuyển và truyền trạng thái cảm biến qua Wi-Fi."),
        ("Cơ chế Heartbeat:", "Tự động ngắt động cơ dừng xe an toàn khi mất kết nối mạng.")
    ], title="TẦNG 2: MÁY CHỦ & DỊCH VỤ REST API", title_size=13.5, item_size=12.0, space_after=Pt(5.0), line_spacing=1.16, m_top=0.08, m_bottom=0.08)

    apply_items_to_tf(s13.shapes[8].text_frame, [
        ("Thiết kế trực quan:", "Giao diện tối màu hiện đại, tối ưu cho cả laptop và điện thoại."),
        ("Điều khiển thuận tiện:", "Dùng nút chạm cảm ứng to rõ, phím nóng & thanh tốc độ.")
    ], title="TẦNG 3: GIAO DIỆN WEB ĐIỀU KHIỂN", title_size=13.5, item_size=12.0, space_after=Pt(5.0), line_spacing=1.16, m_top=0.08, m_bottom=0.08)

    apply_items_to_tf(s13.shapes[10].text_frame, [
        ("Cơ sở dữ liệu:", "Quản lý vị trí các quầy hàng và danh sách đơn giao nhận."),
        ("Trợ lý ảo AI:", "Tích hợp mô hình AI giải đáp thông tin mua sắm cho khách hàng.")
    ], title="TẦNG 4: CƠ SỞ DỮ LIỆU & TRỢ LÝ AI", title_size=13.5, item_size=12.0, space_after=Pt(5.0), line_spacing=1.16, m_top=0.08, m_bottom=0.08)

    # ==================== SLIDE 14: THUẬT TOÁN ĐIỀU HƯỚNG ====================
    print("Slide 14: Refining Thuật toán điều hướng...")
    s14 = prs.slides[13]
    set_box_geometry(s14.shapes[4], top=1.18, left=0.72, width=2.56, height=4.00)
    set_box_geometry(s14.shapes[6], top=1.18, left=3.72, width=2.56, height=4.00)
    set_box_geometry(s14.shapes[8], top=1.18, left=6.72, width=2.56, height=4.00)

    apply_items_to_tf(s14.shapes[4].text_frame, [
        ("Điều tốc mượt mà:", "Điều chỉnh xung PWM từ 20% đến 100%."),
        ("Chuyển động đa hướng:", "Tiến, lùi, tịnh tiến ngang & xoay tại chỗ."),
        ("Khởi động êm:", "Tăng tốc từ từ chống trượt bánh, bảo vệ pin."),
        ("Phanh khẩn cấp:", "Khóa động cơ dừng xe tức thì khi gặp sự cố.")
    ], title="1. ĐIỀU KHIỂN ĐỘNG CƠ", title_size=14.0, item_size=13.0, space_after=Pt(7.0), line_spacing=1.18)

    apply_items_to_tf(s14.shapes[6].text_frame, [
        ("Vùng an toàn (> 30cm):", "Xe di chuyển bình thường theo lộ trình định sẵn."),
        ("Vùng giảm tốc (15 - 30cm):", "Giảm 50% tốc độ, so sánh hai bên để rẽ hướng thoáng."),
        ("Vùng khẩn cấp (< 15cm):", "Phanh dừng ngay lập tức, lùi nhẹ và tự động đổi hướng đi.")
    ], title="2. NÉ TRÁNH VẬT CẢN", title_size=14.0, item_size=13.0, space_after=Pt(8.0), line_spacing=1.20)

    apply_items_to_tf(s14.shapes[8].text_frame, [
        ("Cảm biến đáy xe:", "3 mắt hồng ngoại liên tục quét vạch dẫn đường trên sàn."),
        ("Thuật toán bù lái:", "Tự động bù tốc độ hai bên bánh xe khi vào khúc cua."),
        ("Giữ đúng tâm đường:", "Xe chạy ổn định, không bị chệch khỏi làn đường quy định.")
    ], title="3. BÁM VẠCH TỰ HÀNH", title_size=13.5, item_size=13.0, space_after=Pt(8.0), line_spacing=1.20)

    # ==================== SLIDE 15: GIAO DIỆN WEB DASHBOARD ====================
    print("Slide 15: Refining Giao diện Web Dashboard...")
    s15 = prs.slides[14]
    set_box_geometry(s15.shapes[5], top=1.18, left=6.05, width=3.35, height=4.00)
    apply_items_to_tf(s15.shapes[5].text_frame, [
        ("Giao diện hiện đại:", "Dark mode chống chói, tối ưu cho cả máy tính & điện thoại."),
        ("Điều khiển thuận tiện:", "Nút bấm cảm ứng to rõ, hỗ trợ phím nóng bàn phím."),
        ("Thanh trượt tốc độ:", "Tùy chỉnh vận tốc xe mượt mà từ 20% đến 100% công suất."),
        ("Tự kiểm thử (Auto Test):", "1 chạm tự động chạy kiểm tra toàn diện chuyển động của xe."),
        ("Giám sát thời gian thực:", "Hiển thị cự ly vật cản, mức pin & nhật ký hệ thống.")
    ], title="TÍNH NĂNG GIAO DIỆN WEB", title_size=14.5, item_size=12.5, space_after=Pt(5.5), line_spacing=1.15, m_top=0.08, m_bottom=0.08)

    # ==================== SLIDE 16: KỊCH BẢN VẬN HÀNH ====================
    print("Slide 16: Refining Kịch bản vận hành & Tương tác...")
    s16 = prs.slides[15]
    set_box_geometry(s16.shapes[4], top=1.18, left=0.80, width=3.90, height=4.00)
    set_box_geometry(s16.shapes[6], top=1.18, left=5.30, width=3.90, height=4.00)

    apply_items_to_tf(s16.shapes[4].text_frame, [
        ("Bước 1 (Tạo đơn):", "Nhân viên chọn điểm gửi và điểm nhận đồ trên điện thoại."),
        ("Bước 2 (Di chuyển):", "Xe tự hành chạy theo vạch sàn đến đúng quầy gửi hàng."),
        ("Bước 3 (Nạp hàng):", "Nhân viên đặt bưu kiện vào khay và bấm xác nhận chuyển đi."),
        ("Bước 4 (Vận chuyển):", "Xe tự chạy đến nơi nhận, chủ động giảm tốc né tránh người."),
        ("Bước 5 (Nhận hàng):", "Người nhận nhập mã xác nhận trên Web để lấy hàng hoàn tất.")
    ], title="1. GIAO NHẬN HÀNG HÓA NỘI BỘ", title_size=14.5, item_size=13.0, space_after=Pt(7.0), line_spacing=1.20)

    apply_items_to_tf(s16.shapes[6].text_frame, [
        ("Quét mã QR tương tác:", "Khách quét mã QR trên xe để kết nối trợ lý AI tức thì."),
        ("Hỏi đáp thông minh:", "Hướng dẫn tìm gian hàng, tiện ích ATM, WC & chương trình khuyến mãi."),
        ("Dẫn đường trực tiếp:", "Xe có thể di chuyển phía trước dẫn đường cho khách đến tận quầy.")
    ], title="2. HỖ TRỢ KHÁCH HÀNG & AI", title_size=14.5, item_size=13.0, space_after=Pt(10.0), line_spacing=1.22)

    # ==================== SLIDE 17: KẾT QUẢ ĐÃ ĐẠT ĐƯỢC ====================
    print("Slide 17: Refining Kết quả đã đạt được...")
    s17 = prs.slides[16]
    set_box_geometry(s17.shapes[4], top=1.18, left=0.72, width=2.56, height=4.00)
    set_box_geometry(s17.shapes[6], top=1.18, left=3.72, width=2.56, height=4.00)
    set_box_geometry(s17.shapes[8], top=1.18, left=6.72, width=2.56, height=4.00)

    apply_items_to_tf(s17.shapes[4].text_frame, [
        ("Sơ đồ mạch điện:", "Hoàn thành 100% bản vẽ KiCad 10 & OLED 1.3\"."),
        ("Bo mạch 1 lớp:", "Đi dây toàn bộ mặt B.Cu, tối ưu chỉ 5 cầu Jumper."),
        ("Tiêu chuẩn an toàn:", "Đạt chuẩn 0 lỗi DRC, cách ly chống sụt áp."),
        ("Bản vẽ chế tạo:", "Bộ PDF tỷ lệ 1:1 sẵn sàng gia công thực tế.")
    ], title="1. PHẦN CỨNG MẠCH", title_size=13.5, item_size=13.0, space_after=Pt(7.0), line_spacing=1.18)

    apply_items_to_tf(s17.shapes[6].text_frame, [
        ("Điều khiển động cơ:", "Lập trình chạy mượt các lệnh tiến, lùi, quay vòng, phanh dừng."),
        ("Chế độ mô phỏng:", "Chạy thử thuật toán trên máy tính mà không cần xe thật."),
        ("Kịch bản kiểm tra:", "Có sẵn công cụ tự động kiểm thử toàn diện chuyển động của xe.")
    ], title="2. PHẦN MỀM ĐIỀU KHIỂN", title_size=12.5, item_size=13.0, space_after=Pt(7.0), line_spacing=1.18)

    apply_items_to_tf(s17.shapes[8].text_frame, [
        ("Máy chủ điều khiển:", "Chạy trực tiếp trên Raspberry Pi 4, kết nối Wi-Fi nhanh nhạy."),
        ("Giao diện Web:", "Thiết kế hiện đại, điều khiển mượt mà trên laptop và điện thoại."),
        ("Đầy đủ tính năng:", "Nút bấm lái xe, thanh trượt tốc độ và chế độ tự động kiểm tra.")
    ], title="3. HỆ THỐNG WEBSITE", title_size=13.5, item_size=13.0, space_after=Pt(7.0), line_spacing=1.18)

    # ==================== SLIDE 18: LỘ TRÌNH TIẾP THEO ====================
    print("Slide 18: Refining Lộ trình tiếp theo...")
    s18 = prs.slides[17]
    set_box_geometry(s18.shapes[4], top=1.18, left=0.80, width=3.90, height=4.00)
    set_box_geometry(s18.shapes[6], top=1.18, left=5.30, width=3.90, height=4.00)

    apply_items_to_tf(s18.shapes[4].text_frame, [
        ("SV. Nguyễn Phú Quý (MSSV: 22659651):", ""),
        ("• Phần cứng bo mạch:", "Gia công PCB, hàn linh kiện, lắp ráp xe & khối nguồn."),
        ("• Thị giác máy tính:", "Camera CSI, lập trình bám vạch sàn & né vật cản."),
        ("SV. Lê Minh Ngọc (MSSV: 22652411):", ""),
        ("• Dữ liệu & Quản lý:", "Xây dựng CSDL gian hàng & đơn giao nhận."),
        ("• Trợ lý AI & Web:", "Tích hợp AI hỏi đáp, Web Dashboard & báo cáo.")
    ], title="PHÂN CÔNG NHIỆM VỤ 2 SINH VIÊN", title_size=14.5, item_size=12.5, space_after=Pt(5.0), line_spacing=1.18)

    apply_items_to_tf(s18.shapes[6].text_frame, [
        ("T06/2026:", "Khảo sát thực địa TTTM & chốt đề cương"),
        ("T07/2026:", "Vẽ mạch KiCad 10 & lập trình motor"),
        ("T08/2026:", "Thuật toán né vật cản & bám vạch sàn"),
        ("T09/2026:", "Xây dựng Web Dashboard qua Wi-Fi"),
        ("T10/2026:", "Tích hợp trợ lý AI & hoàn thiện mạch"),
        ("T11/2026:", "Gia công mạch PCB, hàn linh kiện xe"),
        ("T12/2026:", "Chạy thử tại TTTM & bảo vệ KLTN")
    ], title="TIẾN ĐỘ THỜI GIAN THỰC HIỆN", title_size=14.5, item_size=11.5, space_after=Pt(4.5), line_spacing=1.15)

    print(f"Saving updated presentation: {PPTX_FILE}...")
    prs.save(PPTX_FILE)
    print("SUCCESS: All slide layouts and texts refined flawlessly!")

if __name__ == '__main__':
    main()
