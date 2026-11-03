import os, sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def apply_items_to_tf(tf, items, title=None, title_size=13.5, item_size=11.0, space_after=Pt(3.5), line_spacing=1.15):
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.08)
    tf.margin_bottom = Inches(0.08)
    tf.word_wrap = True
    
    # Remove all paragraphs except first
    while len(tf.paragraphs) > 1:
        p_last = tf.paragraphs[-1]._p
        p_last.getparent().remove(p_last)
    
    p0 = tf.paragraphs[0]
    p0.text = ""
    
    if title:
        p0.text = title
        p0.line_spacing = line_spacing
        p0.space_after = Pt(5)
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
    prs = Presentation('KLTN_DeCuong_NguyenPhuQuy_LeMinhNgoc.pptx')
    print(f"Loaded presentation with {len(prs.slides)} slides.")

    # ==================== SLIDE 5: SƠ ĐỒ KHỐI TỔNG THỂ ====================
    print("Updating Slide 5...")
    s5 = prs.slides[4]
    # Adjust left card & textbox
    for s in s5.shapes:
        if s.name == 'Rounded Rectangle 4':
            s.width = Pt(315)
        elif s.name == 'TextBox 5':
            s.left = Pt(50)
            s.top = Pt(88)
            s.width = Pt(295)
            s.height = Pt(285)
            apply_items_to_tf(s.text_frame, [
                ("1. Khối Xử lý Trung tâm:", "Raspberry Pi 4 (4GB RAM) chạy Linux OS, điều phối đa luồng, máy chủ REST API, thuật toán điều hướng tự hành và giao tiếp AI."),
                ("2. Khối Cảm biến Đầu vào:", "Cặp siêu âm HC-SR04 quét chướng ngại vật trái/phải, TCRT5000 3 kênh bám vạch, Camera Pi CSI nhận diện hình ảnh trực tiếp."),
                ("3. Khối Chấp hành & Hiển thị:", "2 module TB6612FNG điều khiển 4 động cơ DC 12V 4WD, màn hình OLED 1.3\" I2C hiển thị thông số và trạng thái robot."),
                ("4. Khối Nguồn Năng lượng:", "Pin Li-ion 3S2P (11.1V - 12.6V), Buck XL4015 5A hạ áp 5V, bảo vệ bằng công tắc SW 10A và cầu chì Fuse 7.5A an toàn.")
            ], title="CẤU TRÚC 4 PHÂN HỆ CHÍNH", title_size=13.5, item_size=10.5, space_after=Pt(4))
        elif s.name == 'TextBox 2':
            set_title(s, "SƠ ĐỒ KHỐI TỔNG THỂ HỆ THỐNG ROBOT", size=18)
        elif s.name == 'Picture 6':
            elem = s._element
            elem.getparent().remove(elem)
    
    # Add new block diagram image on Slide 5
    s5.shapes.add_picture(
        'extracted_imgs/block_diagrams/block_diagram_slide5_overall.png',
        left=Pt(366),
        top=Pt(86),
        width=Pt(338),
        height=Pt(283)
    )

    # ==================== SLIDE 8: SƠ ĐỒ NGUYÊN LÝ TOÀN MẠCH ====================
    print("Updating Slide 8 (Cleaning duplicate shapes)...")
    s8 = prs.slides[7]
    for s in s8.shapes:
        if s.name == 'TextBox 84':
            set_title(s, "SƠ ĐỒ NGUYÊN LÝ TOÀN MẠCH KICAD", size=18)
    
    # Remove duplicate pictures/textboxes if any
    pics = [s for s in s8.shapes if s.name.startswith('Picture')]
    if len(pics) > 1:
        # keep first, remove rest
        for p in pics[1:]:
            elem = p._element
            elem.getparent().remove(elem)
    
    tboxes = [s for s in s8.shapes if s.name.startswith('TextBox') and s.top.pt > 300]
    if len(tboxes) > 1:
        for tb in tboxes[1:]:
            elem = tb._element
            elem.getparent().remove(elem)

    # ==================== SLIDE 9: KHỐI 1 - NGUỒN ĐIỆN ====================
    print("Updating Slide 9...")
    s9 = prs.slides[8]
    for s in list(s9.shapes):
        if s.name == 'TextBox 84':
            set_title(s, "SƠ ĐỒ KHỐI CHỨC NĂNG - KHỐI 1: NGUỒN ĐIỆN", size=18)
        elif s.name == 'TextBox 87':
            s.left = Pt(50)
            s.top = Pt(88)
            s.width = Pt(288)
            s.height = Pt(285)
            apply_items_to_tf(s.text_frame, [
                ("Nguồn cấp chính:", "Pin Li-ion 3S2P (11.1V ~ 12.6V, 5200mAh) xả cao, kết nối qua Header J_BAT chắc chắn."),
                ("Bảo vệ hệ thống:", "Công tắc SW 10A đóng cắt an toàn, cầu chì Fuse 7.5A chống ngắn mạch và bảo vệ quá dòng."),
                ("Ray động lực VM (12V):", "Cấp trực tiếp cho 2 module driver TB6612FNG qua đường đồng lớn 1.5mm."),
                ("Ray logic VCC (5V-5A):", "Module Buck XL4015 hiệu suất cao nuôi vi máy tính Pi 4 và hệ thống cảm biến ngoại vi."),
                ("Mạng Mass thống nhất:", "1 mặt phẳng GND chung toàn hệ thống, triệt tiêu xung nhiễu và chống sụt áp.")
            ], title="KHỐI 1 - NGUỒN ĐIỆN", title_size=13.5, item_size=10.5, space_after=Pt(4))
        elif s.name.startswith('Picture'):
            elem = s._element
            elem.getparent().remove(elem)

    s9.shapes.add_picture(
        'extracted_imgs/block_diagrams/block_diagram_slide9_power.png',
        left=Pt(356),
        top=Pt(114),
        width=Pt(348),
        height=Pt(237)
    )

    # ==================== SLIDE 10: KHỐI 2 - ĐIỀU KHIỂN ====================
    print("Updating Slide 10...")
    s10 = prs.slides[9]
    for s in list(s10.shapes):
        if s.name == 'TextBox 84':
            set_title(s, "SƠ ĐỒ KHỐI CHỨC NĂNG - KHỐI 2: ĐIỀU KHIỂN", size=18)
        elif s.name == 'TextBox 87':
            s.left = Pt(50)
            s.top = Pt(88)
            s.width = Pt(288)
            s.height = Pt(285)
            apply_items_to_tf(s.text_frame, [
                ("Bộ não xử lý trung tâm:", "Raspberry Pi 4 Model B (4GB RAM, CPU 4 nhân 1.5GHz) chạy Linux OS mượt mà."),
                ("Giao tiếp mở rộng:", "Header IDC 40-Pin tiêu chuẩn 2.54mm cắm cáp bẹ kết nối trực tiếp bo mạch Carrier."),
                ("4 Kênh băm xung PWM:", "GPIO12, GPIO13, GPIO18, GPIO19 điều khiển vận tốc độc lập từng cụm bánh xe."),
                ("8 Chân logic hướng quay:", "Điều khiển chiều quay tiến, lùi, quay vòng tại chỗ và phanh dừng chủ động."),
                ("Chân bảo vệ an toàn STBY:", "GPIO26 kích hoạt ngắt khẩn cấp driver TB6612FNG khi gặp sự cố hoặc dừng chờ.")
            ], title="KHỐI 2 - ĐIỀU KHIỂN", title_size=13.5, item_size=10.5, space_after=Pt(4))
        elif s.name.startswith('Picture'):
            elem = s._element
            elem.getparent().remove(elem)

    s10.shapes.add_picture(
        'extracted_imgs/block_diagrams/block_diagram_slide10_control.png',
        left=Pt(356),
        top=Pt(107),
        width=Pt(348),
        height=Pt(251)
    )

    # ==================== SLIDE 11: KHỐI 3 - TÍN HIỆU & CẢM BIẾN ====================
    print("Updating Slide 11...")
    s11 = prs.slides[10]
    for s in list(s11.shapes):
        if s.name == 'TextBox 84':
            set_title(s, "SƠ ĐỒ KHỐI CHỨC NĂNG - KHỐI 3: TÍN HIỆU & CẢM BIẾN", size=18)
        elif s.name == 'TextBox 87':
            s.left = Pt(50)
            s.top = Pt(88)
            s.width = Pt(288)
            s.height = Pt(285)
            apply_items_to_tf(s.text_frame, [
                ("Cảm biến siêu âm (2x HC-SR04):", "Quét vật cản trái/phải; tích hợp cầu trở 1kΩ/2kΩ hạ áp Echo từ 5V xuống 3.3V bảo vệ GPIO."),
                ("Cảm biến dò line (TCRT5000 3-CH):", "3 kênh quang hồng ngoại nhận diện vạch dẫn đường trên sàn hành lang với bộ so sánh độ nhạy cao."),
                ("Màn hình OLED 1.3\" I2C:", "Giao tiếp bus I2C 2 dây (SDA Pin 27, SCL Pin 28, 3.3V), hiển thị trực quan địa chỉ IP, trạng thái và pin."),
                ("Camera Pi CSI 5MP:", "Cáp ribbon phẳng kết nối trực tiếp cổng CSI, truyền video thời gian thực về Dashboard.")
            ], title="KHỐI 3 - TÍN HIỆU & CẢM BIẾN", title_size=13.5, item_size=10.5, space_after=Pt(4))
        elif s.name.startswith('Picture'):
            elem = s._element
            elem.getparent().remove(elem)

    s11.shapes.add_picture(
        'extracted_imgs/block_diagrams/block_diagram_slide11_sensor.png',
        left=Pt(355),
        top=Pt(118),
        width=Pt(350),
        height=Pt(228)
    )

    # ==================== SLIDE 12: KHỐI 4 - CÔNG SUẤT CHẤP HÀNH ====================
    print("Updating Slide 12...")
    s12 = prs.slides[11]
    for s in list(s12.shapes):
        if s.name == 'TextBox 84':
            set_title(s, "SƠ ĐỒ KHỐI CHỨC NĂNG - KHỐI 4: CÔNG SUẤT CHẤP HÀNH", size=18)
        elif s.name == 'TextBox 87':
            s.left = Pt(50)
            s.top = Pt(88)
            s.width = Pt(288)
            s.height = Pt(285)
            apply_items_to_tf(s.text_frame, [
                ("2 Module TB6612FNG:", "Cầu H MOSFET điều khiển độc lập 4 động cơ giảm tốc DC 12V qua 4 cọc header XH2.54 riêng biệt."),
                ("Dòng tải & Hiệu suất:", "Chịu dòng 1.2A liên tục (đỉnh 3.2A)/kênh, nội trở thấp, không sụt áp 2V như IC L298N cũ."),
                ("Chế độ phanh điện từ:", "Khóa chéo 2 cực động cơ giúp robot dừng xe tức thời khi phát hiện vật cản dưới 15cm."),
                ("Động học 4WD đa hướng:", "Hỗ trợ tiến / lùi tuyến tính, quay vòng tại chỗ (Zero-turn radius) linh hoạt trong không gian hẹp.")
            ], title="KHỐI 4 - CÔNG SUẤT CHẤP HÀNH", title_size=13.5, item_size=10.5, space_after=Pt(4))
        elif s.name.startswith('Picture'):
            elem = s._element
            elem.getparent().remove(elem)

    s12.shapes.add_picture(
        'extracted_imgs/block_diagrams/block_diagram_slide12_motor.png',
        left=Pt(355),
        top=Pt(116),
        width=Pt(350),
        height=Pt(231)
    )

    prs.save('KLTN_DeCuong_NguyenPhuQuy_LeMinhNgoc.pptx')
    print("Saved KLTN_DeCuong_NguyenPhuQuy_LeMinhNgoc.pptx successfully!")

if __name__ == '__main__':
    main()

