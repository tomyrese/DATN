import os, sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def apply_items_to_tf(tf, items, title=None, title_size=13.0, item_size=10.5, space_after=Pt(3.5), line_spacing=1.12):
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.08)
    tf.margin_bottom = Inches(0.08)
    tf.word_wrap = True
    
    # Clear paragraphs except first
    while len(tf.paragraphs) > 1:
        p_last = tf.paragraphs[-1]._p
        p_last.getparent().remove(p_last)
        
    p0 = tf.paragraphs[0]
    p0.text = ""
    
    if title:
        p0.text = title
        p0.line_spacing = line_spacing
        p0.space_after = Pt(4.5)
        for r in p0.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(title_size)
            r.font.bold = True
            r.font.color.rgb = RGBColor(15, 43, 72)
            
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
            r1.font.color.rgb = RGBColor(15, 43, 72)
            
        if norm_txt:
            r2 = p.add_run()
            r2.text = norm_txt
            r2.font.name = "Times New Roman"
            r2.font.size = Pt(item_size)
            r2.font.bold = False
            r2.font.color.rgb = RGBColor(50, 50, 50)

def set_title(shape, text, size=18):
    if shape.has_text_frame:
        shape.text_frame.word_wrap = True
        shape.text_frame.text = ""
        p = shape.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = text
        r.font.name = "Times New Roman"
        r.font.size = Pt(size)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 43, 72)

def main():
    pptx_path = 'KLTN_DeCuong_NguyenPhuQuy_LeMinhNgoc.pptx'
    prs = Presentation(pptx_path)
    print(f"Refining presentation: {len(prs.slides)} slides.")

    # ==================== SLIDE 1 ====================
    # USER CONSTRAINT: "giữ nguyên tên đề tài chỉnh sửa các phần ở sau thôi"
    print("Slide 1: Preserving thesis title exactly as requested.")

    # ==================== SLIDE 2: ĐẶT VẤN ĐỀ ====================
    print("Slide 2: Refining text...")
    s2 = prs.slides[1]
    # Card 1: 1. BOI CANH
    apply_items_to_tf(s2.shapes[4].text_frame, [
        ("Mặt sàn rộng lớn:", "Nhiều tầng, mật độ gian hàng và lượng khách mua sắm đông đúc."),
        ("Nhu cầu vận chuyển:", "Cần giao nhận liên tục tài liệu, bưu kiện, hàng mẫu giữa kho và quầy."),
        ("Hỗ trợ khách hàng:", "Khách thường xuyên cần chỉ đường đến gian hàng, quầy ATM, nhà vệ sinh.")
    ], title="1. BỐI CẢNH", title_size=13.0, item_size=10.5, space_after=Pt(4))

    # Card 2: 2. THACH THUC
    apply_items_to_tf(s2.shapes[6].text_frame, [
        ("Tốn kém nhân lực:", "Phụ thuộc nhân viên chuyển phát thủ công, dễ chậm trễ giờ cao điểm."),
        ("Dễ nhầm lẫn:", "Giao nhận thủ công dễ thất lạc hoặc nhầm địa chỉ quầy nhận."),
        ("Thiếu tính chủ động:", "Quầy thông tin cố định, không thể di chuyển dẫn đường cho khách.")
    ], title="2. THÁCH THỨC", title_size=13.0, item_size=10.5, space_after=Pt(4))

    # Card 3: 3. GIAI PHAP
    apply_items_to_tf(s2.shapes[8].text_frame, [
        ("Robot tự hành 4 bánh:", "Điều hướng linh hoạt, tự động tránh người và đi theo vạch sàn."),
        ("Bo mạch tích hợp gọn gàng:", "Chống rung lắc, cấp nguồn ổn định và bảo vệ an toàn hệ thống."),
        ("Điều khiển qua Web:", "Giao diện trực quan, điều khiển từ xa qua mạng Wi-Fi."),
        ("Trợ lý ảo thông minh (AI):", "Hỏi đáp tự nhiên, hướng dẫn tìm đường thân thiện cho khách.")
    ], title="3. GIẢI PHÁP", title_size=13.0, item_size=10.5, space_after=Pt(4))

    # ==================== SLIDE 3: MỤC TIÊU & PHẠM VI ====================
    print("Slide 3: Refining text...")
    s3 = prs.slides[2]
    apply_items_to_tf(s3.shapes[4].text_frame, [
        ("Thiết kế phần cứng:", "Chế tạo bo mạch trung gian cắm nối gọn gàng, cấp nguồn 5A ổn định."),
        ("Điều khiển xe tự hành:", "Lập trình 4 bánh xe chạy êm, tự tránh vật cản và bám vạch sàn."),
        ("Hệ thống Web điều khiển:", "Giao diện giám sát thời gian thực qua Wi-Fi trên laptop và điện thoại."),
        ("Dịch vụ số & Trợ lý AI:", "Quản lý đơn giao nhận và tích hợp AI hỏi đáp hỗ trợ khách hàng.")
    ], title="MỤC TIÊU CỐT LÕI", title_size=13.0, item_size=10.5, space_after=Pt(4))

    apply_items_to_tf(s3.shapes[6].text_frame, [
        ("Khu vực hoạt động:", "Không gian trong nhà, mặt sàn bằng phẳng tại trung tâm thương mại."),
        ("Tải trọng vận chuyển:", "Chuyên chở tài liệu, hàng mẫu, gói đồ nhỏ dưới 1.0 kg."),
        ("Mạng kết nối:", "Mạng không dây Wi-Fi nội bộ tốc độ cao, độ trễ thấp."),
        ("Thời gian hoạt động:", "Pin dung lượng cao, chạy liên tục từ 1.5 đến 2.5 giờ."),
        ("Đối tượng sử dụng:", "Nhân viên quầy gửi nhận hàng và khách tham quan mua sắm.")
    ], title="PHẠM VI VÀ GIỚI HẠN", title_size=13.0, item_size=10.5, space_after=Pt(4))

    # ==================== SLIDE 5: SƠ ĐỒ KHỐI TỔNG THỂ ====================
    print("Slide 5: Refining text & image alignment...")
    s5 = prs.slides[4]
    for s in s5.shapes:
        if s.name == 'TextBox 2':
            set_title(s, "SƠ ĐỒ KHỐI TỔNG THỂ HỆ THỐNG ROBOT", size=18)
        elif s.name == 'Rounded Rectangle 4':
            s.left = Pt(18.0)
            s.top = Pt(78.0)
            s.width = Pt(300.0)
            s.height = Pt(295.0)
        elif s.name == 'TextBox 5':
            s.left = Pt(26.0)
            s.top = Pt(84.0)
            s.width = Pt(285.0)
            s.height = Pt(280.0)
            apply_items_to_tf(s.text_frame, [
                ("1. Xử lý trung tâm:", "Raspberry Pi 4 điều phối hoạt động, xử lý điều hướng và máy chủ điều khiển."),
                ("2. Cảm biến & Thị giác:", "Cảm biến siêu âm tránh vật cản, mắt hồng ngoại bám vạch và camera quan sát."),
                ("3. Chấp hành & Hiển thị:", "4 động cơ giảm tốc dẫn động 4 bánh xe và màn hình OLED hiển thị thông số."),
                ("4. Nguồn năng lượng:", "Pin sạc 12V dung lượng cao, mạch hạ áp 5V-5A và cầu chì bảo vệ an toàn.")
            ], title="CẤU TRÚC 4 PHÂN HỆ CHÍNH", title_size=13.0, item_size=10.5, space_after=Pt(4))
        elif s.name.startswith('Picture'):
            s.left = Pt(328.0)
            s.top = Pt(78.0)
            s.width = Pt(374.0)
            s.height = Pt(295.0)

    # ==================== SLIDE 6: LINH KIỆN CỐT LÕI ====================
    print("Slide 6: Refining text (removing jargon)...")
    s6 = prs.slides[5]
    for s in s6.shapes:
        if s.name == 'TextBox 51': # Pi 4
            apply_items_to_tf(s.text_frame, [
                ("Vi xử lý:", "4 nhân 1.5GHz xử lý nhanh."),
                ("Bộ nhớ RAM:", "4GB tốc độ cao."),
                ("Mạng:", "Wi-Fi kép 2.4/5GHz mượt mà."),
                ("Kết nối:", "Chân cắm 40 chân tiêu chuẩn.")
            ], title="Raspberry Pi 4 Model B", title_size=11.5, item_size=9.5, space_after=Pt(2))
        elif s.name == 'TextBox 54': # TB6612
            apply_items_to_tf(s.text_frame, [
                ("Công nghệ:", "Đóng ngắt hiệu suất cao."),
                ("Dòng tải:", "1.2A liên tục mỗi động cơ."),
                ("Ưu điểm:", "Không sụt áp, chạy êm mát."),
                ("Điều khiển:", "Chỉnh tốc độ mượt mà.")
            ], title="Mạch Điều Khiển Động Cơ", title_size=11.5, item_size=9.5, space_after=Pt(2))
        elif s.name == 'TextBox 57': # Nguon
            apply_items_to_tf(s.text_frame, [
                ("Pin nguồn 12V:", "Dung lượng cao cho xe."),
                ("Hạ áp 5V-5A:", "Nuôi máy tính và cảm biến."),
                ("Chung mass:", "Chống nhiễu, ổn định áp.")
            ], title="Khối Nguồn Năng Lượng", title_size=11.5, item_size=9.5, space_after=Pt(2))
        elif s.name == 'TextBox 12': # OLED
            apply_items_to_tf(s.text_frame, [
                ("Màn hình:", "1.3 inch nét, tiết kiệm điện."),
                ("Kết nối:", "Dây tín hiệu 2 dây gọn gàng."),
                ("Hiển thị:", "Báo IP mạng, pin, trạng thái.")
            ], title="Màn Hình OLED 1.3\"", title_size=11.5, item_size=9.5, space_after=Pt(2))
        elif s.name == 'TextBox 18': # HC-SR04
            apply_items_to_tf(s.text_frame, [
                ("Khoảng cách đo:", "Từ 2cm đến 400cm."),
                ("Góc quét:", "Rộng, phát hiện người đi bộ."),
                ("Bảo vệ mạch:", "Hạ áp về 3.3V an toàn.")
            ], title="Cảm Biến Siêu Âm (2 Bộ)", title_size=11.5, item_size=9.5, space_after=Pt(2))
        elif s.name == 'TextBox 24': # Camera
            apply_items_to_tf(s.text_frame, [
                ("Độ phân giải:", "5 Megapixel sắc nét."),
                ("Góc nhìn:", "72.4° bao quát không gian."),
                ("Kết nối:", "Cáp bẹ cắm thẳng máy tính.")
            ], title="Camera Quan Sát", title_size=11.5, item_size=9.5, space_after=Pt(2))

    # ==================== SLIDE 7: THIẾT KẾ BO MẠCH (REMOVING F.CU / B.CU) ====================
    print("Slide 7: Eliminating F.Cu / B.Cu jargon...")
    s7 = prs.slides[6]
    apply_items_to_tf(s7.shapes[4].text_frame, [
        ("Khắc phục rung lắc:", "Thay dây cắm lỏng lẻo bằng bo mạch cắm thẳng cáp bẹ 40 chân chắc chắn."),
        ("Tách biệt nguồn điện:", "Tách riêng nguồn động cơ 12V và nguồn điều khiển 5V để chống nhiễu."),
        ("Bảo vệ vi xử lý:", "Cặp điện trở phân áp bảo vệ an toàn tuyệt đối các chân tín hiệu máy tính."),
        ("Dễ dàng chế tạo:", "Thiết kế mạch 1 lớp đồng mặt đáy, phù hợp tự làm thủ công hoặc đặt xưởng giá rẻ.")
    ], title="ĐẶT VẤN ĐỀ & GIẢI PHÁP THIẾT KẾ", title_size=13.0, item_size=10.5, space_after=Pt(4))

    apply_items_to_tf(s7.shapes[6].text_frame, [
        ("Cấu trúc mạch:", "Mạch in 1 lớp đơn, toàn bộ đường mạch đi ở mặt đáy bo mạch."),
        ("Cầu nối dây:", "5 cầu nối dây mặt trên để vượt chéo đường mạch đơn giản, dễ cắm."),
        ("Đường nguồn chịu tải:", "Đường đồng lớn 1.5mm đảm bảo dẫn dòng khỏe, chống sụt áp."),
        ("Đường tín hiệu:", "Nét đồng 1.0mm rộng rãi, dễ ủi nhiệt thủ công, không sợ đứt nét."),
        ("Khoảng cách an toàn:", "Độ hở giữa các nét >= 0.5mm, chống chập chạm tuyệt đối."),
        ("Kích thước bo mạch:", "111.6mm x 72.9mm, bắt vít vừa vặn trên khung xe 4 bánh.")
    ], title="THÔNG SỐ KỸ THUẬT & TIÊU CHUẨN MẠCH", title_size=13.0, item_size=10.5, space_after=Pt(3.5))

    # ==================== SLIDE 8: SƠ ĐỒ NGUYÊN LÝ ====================
    # User enlarged Picture 86 to fill slide, keep intact!
    print("Slide 8: Full schematic layout preserved.")

    # ==================== SLIDES 9, 10, 11, 12: SƠ ĐỒ KHỐI CHỨC NĂNG ====================
    # USER CONSTRAINT: "giảm bớt chữ mô tả ngắn gọn, dễ hiểu, dễ đọc nhất giúp tôi, fix lại hình ảnh"
    
    # --- SLIDE 9: KHỐI 1 - NGUỒN ĐIỆN ---
    print("Slide 9: Harmonizing layout & concise text...")
    s9 = prs.slides[8]
    for s in s9.shapes:
        if s.name == 'Rounded Rectangle 86':
            s.left = Pt(18.0)
            s.top = Pt(78.0)
            s.width = Pt(285.0)
            s.height = Pt(285.0)
        elif s.name == 'TextBox 87':
            s.left = Pt(26.0)
            s.top = Pt(84.0)
            s.width = Pt(270.0)
            s.height = Pt(270.0)
            apply_items_to_tf(s.text_frame, [
                ("Pin nguồn chính:", "Bộ pin Li-ion 12V (5200mAh) dòng xả cao, cung cấp năng lượng toàn xe."),
                ("Bảo vệ hệ thống:", "Công tắc gạt 10A và cầu chì 7.5A chống quá dòng, chống chập cháy."),
                ("Đường động lực 12V:", "Cấp điện trực tiếp cho 2 mạch điều khiển 4 động cơ bánh xe."),
                ("Hạ áp nuôi máy tính:", "Mạch hạ áp công suất lớn 5V-5A nuôi Raspberry Pi 4 và cảm biến."),
                ("Đường mass chung:", "Một đường mass thống nhất toàn mạch, triệt tiêu nhiễu sụt áp.")
            ], title="KHỐI 1 - NGUỒN ĐIỆN", title_size=13.0, item_size=10.5, space_after=Pt(4))
        elif s.name.startswith('Picture'):
            s.left = Pt(312.0)
            s.top = Pt(84.0)
            s.width = Pt(390.0)
            s.height = Pt(265.0)

    # --- SLIDE 10: KHỐI 2 - ĐIỀU KHIỂN ---
    print("Slide 10: Harmonizing layout & concise text...")
    s10 = prs.slides[9]
    for s in s10.shapes:
        if s.name == 'Rounded Rectangle 86':
            s.left = Pt(18.0)
            s.top = Pt(78.0)
            s.width = Pt(285.0)
            s.height = Pt(285.0)
        elif s.name == 'TextBox 87':
            s.left = Pt(26.0)
            s.top = Pt(84.0)
            s.width = Pt(270.0)
            s.height = Pt(270.0)
            apply_items_to_tf(s.text_frame, [
                ("Bộ xử lý trung tâm:", "Raspberry Pi 4 (4GB RAM) chạy Linux, điều phối toàn bộ robot."),
                ("Kết nối bo mạch:", "Cáp bẹ 40 chân cắm thẳng vào mạch trung gian chắc chắn, chống tuột."),
                ("Điều khiển 4 bánh:", "4 kênh băm xung chỉnh tốc độ độc lập và 8 chân tín hiệu chọn chiều."),
                ("Chế độ chuyển động:", "Tiến, lùi, quay vòng tại chỗ và bẻ lái vòng cung linh hoạt."),
                ("Khóa an toàn khẩn cấp:", "Chân tín hiệu ngắt nguồn động cơ tức thời khi dừng chờ sự cố.")
            ], title="KHỐI 2 - ĐIỀU KHIỂN", title_size=13.0, item_size=10.5, space_after=Pt(4))
        elif s.name.startswith('Picture'):
            s.left = Pt(318.0)
            s.top = Pt(81.0)
            s.width = Pt(384.0)
            s.height = Pt(276.0)

    # --- SLIDE 11: KHỐI 3 - TÍN HIỆU & CẢM BIẾN ---
    print("Slide 11: Harmonizing layout & concise text...")
    s11 = prs.slides[10]
    for s in s11.shapes:
        if s.name == 'Rounded Rectangle 86':
            s.left = Pt(18.0)
            s.top = Pt(78.0)
            s.width = Pt(285.0)
            s.height = Pt(285.0)
        elif s.name == 'TextBox 87':
            s.left = Pt(26.0)
            s.top = Pt(84.0)
            s.width = Pt(270.0)
            s.height = Pt(270.0)
            apply_items_to_tf(s.text_frame, [
                ("Cảm biến siêu âm (2 bộ):", "Quét vật cản trước trái/phải, hạ áp tín hiệu an toàn về 3.3V."),
                ("Cảm biến bám vạch (3 mắt):", "Mắt hồng ngoại độ nhạy cao nhận diện đường đi trên sàn nhà."),
                ("Màn hình OLED 1.3\":", "Hiển thị trực quan địa chỉ IP mạng, mức pin và trạng thái xe."),
                ("Camera quan sát 5MP:", "Truyền video trực tiếp về Web Dashboard để người dùng theo dõi.")
            ], title="KHỐI 3 - TÍN HIỆU & CẢM BIẾN", title_size=13.0, item_size=10.5, space_after=Pt(4.5))
        elif s.name.startswith('Picture'):
            s.left = Pt(314.0)
            s.top = Pt(88.0)
            s.width = Pt(388.0)
            s.height = Pt(252.0)

    # --- SLIDE 12: KHỐI 4 - CÔNG SUẤT CHẤP HÀNH ---
    print("Slide 12: Harmonizing layout & concise text...")
    s12 = prs.slides[11]
    for s in s12.shapes:
        if s.name == 'Rounded Rectangle 86':
            s.left = Pt(18.0)
            s.top = Pt(78.0)
            s.width = Pt(285.0)
            s.height = Pt(285.0)
        elif s.name == 'TextBox 87':
            s.left = Pt(26.0)
            s.top = Pt(84.0)
            s.width = Pt(270.0)
            s.height = Pt(270.0)
            apply_items_to_tf(s.text_frame, [
                ("2 Mạch công suất riêng biệt:", "Tải dòng khỏe, hiệu suất cao, chia tải mát đều cho 2 bên bánh xe."),
                ("4 Động cơ giảm tốc 12V:", "Dẫn động 4 bánh độc lập (4WD), cắm giắc tiện lợi, dễ tháo lắp."),
                ("Phanh điện từ an toàn:", "Khóa chéo cực động cơ giúp xe dừng ngay tức khắc khi gặp vật cản."),
                ("Linh hoạt không gian hẹp:", "Hỗ trợ quay vòng tại chỗ không bán kính, di chuyển dễ dàng.")
            ], title="KHỐI 4 - CÔNG SUẤT CHẤP HÀNH", title_size=13.0, item_size=10.5, space_after=Pt(4.5))
        elif s.name.startswith('Picture'):
            s.left = Pt(314.0)
            s.top = Pt(86.0)
            s.width = Pt(388.0)
            s.height = Pt(256.0)

    # ==================== SLIDE 13: PHẦN MỀM ĐIỀU KHIỂN ====================
    print("Slide 13: Refining text...")
    s13 = prs.slides[12]
    apply_items_to_tf(s13.shapes[4].text_frame, [
        ("Thư viện điều khiển:", "Điều khiển trực tiếp chân tín hiệu của máy tính."),
        ("Module động cơ:", "Đóng gói lệnh tiến, lùi, quay vòng, phanh dừng."),
        ("Chế độ mô phỏng:", "Chạy thử nghiệm trên máy tính khi chưa có xe thật.")
    ], title="TẦNG 1: ĐIỀU KHIỂN PHẦN CỨNG (PYTHON)", title_size=12.0, item_size=10.0, space_after=Pt(2))

    apply_items_to_tf(s13.shapes[6].text_frame, [
        ("Máy chủ Python:", "Gọn nhẹ, khởi động nhanh, phản hồi tức thời."),
        ("Lệnh điều khiển:", "Nhận lệnh di chuyển, chỉnh tốc độ qua mạng Wi-Fi."),
        ("Độ trễ thấp:", "Phản hồi mili-giây, xe chạy mượt mà, không giật lag.")
    ], title="TẦNG 2: MÁY CHỦ & DỊCH VỤ REST API", title_size=12.0, item_size=10.0, space_after=Pt(2))

    apply_items_to_tf(s13.shapes[8].text_frame, [
        ("Giao diện hiện đại:", "Thiết kế tối màu đẹp mắt, hiển thị trực quan."),
        ("Hỗ trợ đa thiết bị:", "Dùng mượt trên cả máy tính và điện thoại."),
        ("Điều khiển linh hoạt:", "Dùng phím bấm trên màn hình hoặc bàn phím máy tính.")
    ], title="TẦNG 3: GIAO DIỆN WEB ĐIỀU KHIỂN", title_size=12.0, item_size=10.0, space_after=Pt(2))

    apply_items_to_tf(s13.shapes[10].text_frame, [
        ("Lưu trữ dữ liệu:", "Quản lý danh sách gian hàng, đơn hàng giao nhận."),
        ("Hỗ trợ khách hàng:", "Tích hợp trợ lý AI giải đáp thông tin mua sắm."),
        ("Xử lý hình ảnh:", "Nhận diện làn đường và chướng ngại vật từ camera.")
    ], title="TẦNG 4: CƠ SỞ DỮ LIỆU & TRÍ TUỆ NHÂN TẠO", title_size=12.0, item_size=10.0, space_after=Pt(2))

    # ==================== SLIDE 14: THUẬT TOÁN ĐIỀU HƯỚNG ====================
    print("Slide 14: Refining text...")
    s14 = prs.slides[13]
    apply_items_to_tf(s14.shapes[4].text_frame, [
        ("Chỉnh tốc độ mượt mà:", "Điều chỉnh linh hoạt từ 20% đến 100% công suất."),
        ("Chuyển động linh hoạt:", "Tiến, lùi, quay tròn tại chỗ, ôm cua êm ái."),
        ("Khởi động êm:", "Tăng tốc từ từ giúp chống trượt bánh, bảo vệ pin."),
        ("Phanh dừng khẩn cấp:", "Khóa động cơ dừng xe ngay lập tức khi cần thiết.")
    ], title="1. ĐIỀU KHIỂN ĐỘNG CƠ", title_size=13.0, item_size=10.5, space_after=Pt(4))

    apply_items_to_tf(s14.shapes[6].text_frame, [
        ("Vùng an toàn (> 30cm):", "Xe di chuyển bình thường theo lộ trình định sẵn."),
        ("Vùng giảm tốc (15cm - 30cm):", "Giảm 50% tốc độ, so sánh hai bên để rẽ hướng thoáng."),
        ("Vùng khẩn cấp (< 15cm):", "Phanh dừng ngay lập tức, lùi nhẹ và đổi hướng đi.")
    ], title="2. TRÁNH VẬT CẢN TỰ ĐỘNG", title_size=13.0, item_size=10.5, space_after=Pt(4))

    apply_items_to_tf(s14.shapes[8].text_frame, [
        ("Cảm biến đáy xe:", "3 mắt hồng ngoại liên tục quét vạch dẫn đường trên sàn."),
        ("Thuật toán bù lái:", "Tự động bù tốc độ hai bên bánh xe khi vào khúc cua."),
        ("Giữ đúng tâm đường:", "Xe chạy ổn định, không bị chệch khỏi làn đường quy định.")
    ], title="3. BÁM ĐƯỜNG DẪN HƯỚNG", title_size=13.0, item_size=10.5, space_after=Pt(4))

    # ==================== SLIDE 15: GIAO DIỆN WEB ====================
    print("Slide 15: Refining text...")
    s15 = prs.slides[14]
    apply_items_to_tf(s15.shapes[5].text_frame, [
        ("Thiết kế hiện đại:", "Giao diện tối màu trực quan, dùng tốt trên điện thoại và laptop."),
        ("Thao tác thuận tiện:", "Bấm nút chạm cảm ứng to rõ, hỗ trợ phím nóng bàn phím."),
        ("Thanh trượt tốc độ:", "Tăng giảm vận tốc xe linh hoạt từ 20% đến 100%."),
        ("Nút tự kiểm tra (Auto Test):", "1 nút bấm tự động chạy thử toàn bộ chuyển động của xe.")
    ], title="TÍNH NĂNG GIAO DIỆN WEB", title_size=13.5, item_size=11.0, space_after=Pt(4.5))

    # ==================== SLIDE 16: KỊCH BẢN VẬN HÀNH ====================
    print("Slide 16: Refining text...")
    s16 = prs.slides[15]
    apply_items_to_tf(s16.shapes[4].text_frame, [
        ("Bước 1 (Tạo đơn):", "Nhân viên chọn điểm gửi và điểm nhận đồ trên điện thoại."),
        ("Bước 2 (Di chuyển):", "Xe tự hành chạy theo vạch sàn đến đúng quầy gửi hàng."),
        ("Bước 3 (Nạp hàng):", "Nhân viên đặt bưu kiện vào khay và bấm xác nhận chuyển đi."),
        ("Bước 4 (Vận chuyển):", "Xe tự chạy đến nơi nhận, tự động tránh người đi bộ."),
        ("Bước 5 (Nhận hàng):", "Người nhận nhập mã xác nhận trên Web để lấy hàng hoàn tất.")
    ], title="1. GIAO NHẬN HÀNG HÓA NỘI BỘ", title_size=13.0, item_size=10.5, space_after=Pt(3.5))

    apply_items_to_tf(s16.shapes[6].text_frame, [
        ("Quét mã tương tác:", "Khách quét mã QR trên xe để trò chuyện cùng trợ lý ảo."),
        ("Hỏi đáp thông minh:", "Trợ lý AI trả lời tức thì mọi câu hỏi của khách hàng:"),
        ("• Tìm gian hàng:", "Quầy thời trang, khu ăn uống, thương hiệu yêu thích."),
        ("• Tìm tiện ích:", "Vị trí cây ATM, nhà vệ sinh, thang máy, bãi gửi xe."),
        ("• Thông tin ưu đãi:", "Các chương trình khuyến mãi đang diễn ra trong ngày."),
        ("Dẫn đường trực tiếp:", "Xe có thể chạy trước dẫn đường cho khách đến tận quầy.")
    ], title="2. HỖ TRỢ KHÁCH HÀNG & AI", title_size=13.0, item_size=10.5, space_after=Pt(2.5))

    # ==================== SLIDE 17: KẾT QUẢ ĐÃ ĐẠT ĐƯỢC ====================
    print("Slide 17: Eliminating F.Cu / B.Cu & refining text...")
    s17 = prs.slides[16]
    apply_items_to_tf(s17.shapes[4].text_frame, [
        ("Sơ đồ mạch điện tử:", "Hoàn thành 100% bản vẽ chuẩn, có màn hình OLED 1.3\"."),
        ("Bo mạch 1 lớp đồng:", "Toàn bộ đường mạch ở mặt dưới, dùng 5 cầu nối dây mặt trên."),
        ("Kiểm tra an toàn:", "Đạt tiêu chuẩn 0 lỗi, cách ly an toàn, chống chập cháy."),
        ("Hồ sơ chế tạo:", "Đầy đủ bản vẽ kích thước chuẩn, sẵn sàng gia công thực tế.")
    ], title="1. Phần cứng & Bo mạch", title_size=13.0, item_size=10.5, space_after=Pt(4))

    apply_items_to_tf(s17.shapes[6].text_frame, [
        ("Điều khiển động cơ:", "Lập trình chạy mượt các lệnh tiến, lùi, quay vòng, phanh dừng."),
        ("Chế độ mô phỏng:", "Chạy thử thuật toán trên máy tính mà không cần xe thật."),
        ("Kịch bản kiểm tra:", "Có sẵn công cụ tự động chạy thử nghiệm toàn diện xe.")
    ], title="2. Phần mềm & Điều khiển", title_size=13.0, item_size=10.5, space_after=Pt(4))

    apply_items_to_tf(s17.shapes[8].text_frame, [
        ("Máy chủ điều khiển:", "Chạy trực tiếp trên Raspberry Pi, kết nối Wi-Fi nhanh nhạy."),
        ("Giao diện Web:", "Thiết kế hiện đại, điều khiển mượt cả trên laptop và điện thoại."),
        ("Đầy đủ tính năng:", "Nút bấm lái xe, thanh trượt tốc độ, tự động kiểm tra.")
    ], title="3. Hệ thống Web Server", title_size=13.0, item_size=10.5, space_after=Pt(4))

    # ==================== SLIDE 18: KẾ HOẠCH TIẾP THEO ====================
    print("Slide 18: Refining text...")
    s18 = prs.slides[17]
    apply_items_to_tf(s18.shapes[4].text_frame, [
        ("SV. Nguyễn Phú Quý (MSSV: 22659651):", ""),
        ("• Gia công & Lắp ráp:", "Làm bo mạch thật, hàn linh kiện, lắp khung xe và cảm biến."),
        ("• Xử lý hình ảnh:", "Lập trình camera nhận diện làn đường, hoàn thiện né vật cản."),
        ("SV. Lê Minh Ngọc (MSSV: 22652411):", ""),
        ("• Dữ liệu & Quản lý:", "Xây dựng cơ sở dữ liệu quản lý gian hàng và đơn giao nhận."),
        ("• Trợ lý ảo AI:", "Tích hợp AI hỏi đáp khách hàng, hoàn thiện Web và báo cáo.")
    ], title="PHÂN CÔNG NHIỆM VỤ 2 SINH VIÊN", title_size=13.0, item_size=10.0, space_after=Pt(3))

    apply_items_to_tf(s18.shapes[6].text_frame, [
        ("Tháng 06/2026:", "Khảo sát thực tế trung tâm thương mại, chốt yêu cầu đề tài."),
        ("Tháng 07/2026:", "Vẽ sơ đồ mạch điện, lập trình điều khiển động cơ ban đầu."),
        ("Tháng 08/2026:", "Lắp cảm biến siêu âm né vật cản, cảm biến bám vạch sàn."),
        ("Tháng 09/2026:", "Xây dựng giao diện Web điều khiển qua mạng Wi-Fi."),
        ("Tháng 10/2026:", "Tích hợp trợ lý AI hỏi đáp, hoàn thiện thiết kế bo mạch 1 lớp."),
        ("Tháng 11/2026:", "Gia công mạch thật, hàn linh kiện, lắp ráp hoàn chỉnh xe."),
        ("Tháng 12/2026:", "Chạy thử thực tế, đo đạc sai số, hoàn thiện thuyết minh tốt nghiệp.")
    ], title="TIẾN ĐỘ THỜI GIAN THỰC HIỆN", title_size=13.0, item_size=10.0, space_after=Pt(2.5))

    prs.save(pptx_path)
    print("Saved refined presentation successfully!")

if __name__ == '__main__':
    main()

