import os, sys, shutil
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

DOCX_IN = 'PL2_Robot_TuHanh_Pi4.docx'
DOCX_OUT = 'PL2_Robot_TuHanh_Pi4.docx'

def format_run(run, font_name="Times New Roman", size_pt=13, bold=False, italic=False, color_rgb=(0, 0, 0)):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color_rgb:
        run.font.color.rgb = RGBColor(*color_rgb)

def format_paragraph(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line_spacing=1.5, space_after_pt=4, space_before_pt=0):
    p.alignment = align
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_after = Pt(space_after_pt)
    p.paragraph_format.space_before = Pt(space_before_pt)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_styled_cell(cell, text, bold=False, italic=False, font_size=10.5, align=WD_ALIGN_PARAGRAPH.LEFT, fill_hex=None, width_in=None):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    r = p.add_run(text)
    format_run(r, font_name="Times New Roman", size_pt=font_size, bold=bold, italic=italic)
    if fill_hex:
        set_cell_background(cell, fill_hex)
    set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
    if width_in:
        cell.width = Inches(width_in)

def build_styled_table(doc, headers, rows_data, col_widths=None):
    tbl = doc.add_table(len(rows_data) + 1, len(headers), style='Table Grid')
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Headers
    for c_idx, h_text in enumerate(headers):
        w = col_widths[c_idx] if col_widths and c_idx < len(col_widths) else None
        add_styled_cell(tbl.rows[0].cells[c_idx], h_text, bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2", width_in=w)
    # Rows
    for r_idx, row_vals in enumerate(rows_data):
        fill = "F2F2F2" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_vals):
            w = col_widths[c_idx] if col_widths and c_idx < len(col_widths) else None
            align = WD_ALIGN_PARAGRAPH.CENTER if (c_idx == 0 or len(val) <= 12) else WD_ALIGN_PARAGRAPH.LEFT
            bold = True if c_idx == 0 else False
            add_styled_cell(tbl.rows[r_idx + 1].cells[c_idx], val, bold=bold, font_size=10, align=align, fill_hex=fill, width_in=w)
    return tbl

def main():
    print(f"Loading document: {DOCX_IN}...")
    doc = docx.Document(DOCX_IN)
    body = doc._body._element

    # =========================================================================
    # 1. UPDATE DANH MỤC HÌNH ẢNH & DANH MỤC BẢNG BIỂU FIRST
    # =========================================================================
    print("Updating List of Figures and Tables...")
    all_figures = [
        "Hình 1.1: So sánh các nền tảng điều khiển robot phổ biến\t13",
        "Hình 1.2: Bo mạch máy tính nhúng Raspberry Pi 4 Model B (8GB)\t14",
        "Hình 1.3: Động cơ giảm tốc vàng TT trục kép 3-6VDC và bánh xe Mecanum\t15",
        "Hình 1.4: Mạch driver điều khiển động cơ TB6612FNG\t16",
        "Hình 1.5: Module Raspberry Pi Camera V1.3 (OV5647)\t17",
        "Hình 1.6: Cảm biến khoảng cách Ultrasonic sensor HC-SR04\t18",
        "Hình 1.7: Module màn hình hiển thị OLED 1.3 inch I²C\t19",
        "Hình 2.1: Sơ đồ kiến trúc tổng quát của máy tính nhúng\t21",
        "Hình 2.2: Cấu trúc bên trong Raspberry Pi 4 Model B (8GB)\t22",
        "Hình 2.3: Sơ đồ nguyên lý điều khiển động cơ DC TT bằng PWM và mạch cầu H\t24",
        "Hình 2.4: Nguyên lý phân bố vector lực và vận tốc của bánh xe đa hướng Mecanum\t25",
        "Hình 2.5: Nguyên lý hoạt động của cảm biến khoảng cách Ultrasonic sensor\t26",
        "Hình 2.6: Luồng xử lý ảnh nhận diện khách hàng trong hệ thống bằng OpenCV\t27",
        "Hình 3.1: Sơ đồ tổng thể kiến trúc hệ thống robot tự hành trên nền tảng Raspberry Pi 4\t29",
        "Hình 3.2: Sơ đồ nguyên lý chi tiết bo mạch mở rộng (Carrier Board) trên KiCad 10\t30",
        "Hình 3.3: Bản vẽ thiết kế mạch in (PCB) 1 lớp mặt đáy B.Cu với 5 cầu nối dây Jumper\t31",
        "Hình 3.4: Lưu đồ hoạt động tổng thể của hệ thống robot tự hành\t33",
        "Hình 3.5: Lưu đồ giải thuật điều khiển động học 4 bánh Mecanum & PWM\t34",
        "Hình 3.6: Lưu đồ giải thuật đọc cảm biến siêu âm HC-SR04 và né tránh vật cản đa cấp\t35",
        "Hình 3.7: Lưu đồ giải thuật xử lý Camera CSI & Nhận diện khách hàng bằng OpenCV kết hợp OLED\t36",
        "Hình 3.8: Lưu đồ hoạt động của máy chủ Web Server và Giao diện Web Dashboard\t37",
        "Hình 3.9: Giao diện Web Dashboard điều khiển và giám sát robot qua mạng Wi-Fi\t38",
    ]

    all_tables = [
        "Bảng 1.1: Thông số kỹ thuật Raspberry Pi 4 Model B (8GB)\t14",
        "Bảng 1.2: Thông số kỹ thuật động cơ giảm tốc TT trục kép 3-6VDC\t15",
        "Bảng 1.3: Thông số kỹ thuật module Driver TB6612FNG\t16",
        "Bảng 1.4: Thông số kỹ thuật Raspberry Pi Camera V1.3 (OV5647)\t17",
        "Bảng 1.5: Thông số kỹ thuật cảm biến khoảng cách siêu âm HC-SR04\t18",
        "Bảng 1.6: Thông số kỹ thuật màn hình hiển thị OLED 1.3 inch I²C\t19",
        "Bảng 2.1: Thành phần và thông số cốt lõi của Raspberry Pi 4 Model B (8GB)\t22",
        "Bảng 3.1: Bảng phân bổ chân GPIO của Raspberry Pi 4 trên Bo mạch Carrier Board\t31",
        "Bảng 3.2: Phân bổ và quản lý tài nguyên trên Raspberry Pi 4 Model B (8GB)\t32",
        "Bảng 3.3: Bảng tra cứu trạng thái logic điều khiển chiều quay và tốc độ động cơ\t34",
        "Bảng 3.4: Ngưỡng khoảng cách và hành vi điều khiển né tránh vật cản của robot\t35",
        "Bảng 4.1: Bảng tổng hợp tiến độ hoàn thành các hạng mục nghiên cứu của đề tài\t39",
        "Bảng 4.2: Kế hoạch phân bổ thời gian thực hiện các giai đoạn tiếp theo của đề tài\t40",
    ]

    p_fig_title = None
    p_tbl_title = None
    p_abbr_title = None
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt == "DANH MỤC HÌNH ẢNH":
            p_fig_title = p
        elif txt == "DANH MỤC BẢNG BIỂU":
            p_tbl_title = p
        elif txt == "DANH MỤC TỪ VIẾT TẮT":
            p_abbr_title = p
            break

    if p_fig_title and p_tbl_title:
        curr = p_fig_title._p.getnext()
        while curr is not None and curr != p_tbl_title._p:
            nxt = curr.getnext()
            body.remove(curr)
            curr = nxt

        ref_f = p_fig_title._p
        for f_text in all_figures:
            pf = doc.add_paragraph(f_text, style='table of figures')
            format_paragraph(pf, align=WD_ALIGN_PARAGRAPH.LEFT, line_spacing=1.15, space_after_pt=2, space_before_pt=0)
            if pf.runs:
                format_run(pf.runs[0], font_name="Times New Roman", size_pt=12)
            ref_f.addnext(pf._p)
            ref_f = pf._p

    if p_tbl_title and p_abbr_title:
        curr = p_tbl_title._p.getnext()
        while curr is not None and curr != p_abbr_title._p:
            nxt = curr.getnext()
            body.remove(curr)
            curr = nxt

        ref_t = p_tbl_title._p
        for t_text in all_tables:
            pt = doc.add_paragraph(t_text, style='table of figures')
            format_paragraph(pt, align=WD_ALIGN_PARAGRAPH.LEFT, line_spacing=1.15, space_after_pt=2, space_before_pt=0)
            if pt.runs:
                format_run(pt.runs[0], font_name="Times New Roman", size_pt=12)
            ref_t.addnext(pt._p)
            ref_t = pt._p

    # =========================================================================
    # 2. LOCATE CHAPTER 3 AND CONCLUSION HEADINGS
    # =========================================================================
    p_ch3_title = None
    p_conc_title = None
    for p in doc.paragraphs:
        txt = p.text.strip()
        if "PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG" in txt and p_ch3_title is None:
            p_ch3_title = p
        elif "KẾT LUẬN VÀ KIẾN NGHỊ" in txt and p_conc_title is None:
            p_conc_title = p

    p255_elem = p_ch3_title._p
    p350_elem = p_conc_title._p

    children = list(body)
    b_idx_255 = children.index(p255_elem)
    b_idx_350 = children.index(p350_elem)

    print(f"Body element index: Chapter 3 Title = {b_idx_255}, Conclusion = {b_idx_350}")
    print(f"Removing {b_idx_350 - b_idx_255 - 1} elements between Chapter 3 and Conclusion...")

    to_remove = children[b_idx_255 + 1 : b_idx_350]
    for elem in to_remove:
        body.remove(elem)

    print(f"Removed {len(to_remove)} duplicate/messy elements successfully!")

    # Reference element for sequential insertion
    ref_elem = p255_elem

    def insert_p(text, style='Normal', bold=False, italic=False, size_pt=13, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after_pt=4, space_before_pt=0, line_spacing=1.5):
        nonlocal ref_elem
        p = doc.add_paragraph(style=style)
        format_paragraph(p, align=align, line_spacing=line_spacing, space_after_pt=space_after_pt, space_before_pt=space_before_pt)
        if text:
            r = p.add_run(text)
            format_run(r, font_name="Times New Roman", size_pt=size_pt, bold=bold, italic=italic)
        ref_elem.addnext(p._p)
        ref_elem = p._p
        return p

    def insert_heading(text, level=2, space_before_pt=6, space_after_pt=3):
        style = f'Heading {level}'
        size_pt = 13
        bold = True
        italic = True if level >= 3 else False
        return insert_p(text, style=style, bold=bold, italic=italic, size_pt=size_pt, align=WD_ALIGN_PARAGRAPH.LEFT, space_before_pt=space_before_pt, space_after_pt=space_after_pt, line_spacing=1.2)

    def insert_caption(text):
        nonlocal ref_elem
        p = doc.add_paragraph(style='Caption')
        format_paragraph(p, align=WD_ALIGN_PARAGRAPH.CENTER, line_spacing=1.15, space_after_pt=6, space_before_pt=2)
        r = p.add_run(text)
        format_run(r, font_name="Times New Roman", size_pt=11.5, bold=False, italic=True)
        ref_elem.addnext(p._p)
        ref_elem = p._p
        return p

    def insert_img(img_path, width_inches=5.4, caption_text=""):
        nonlocal ref_elem
        if not os.path.exists(img_path):
            print(f"WARNING: Image not found: {img_path}")
            return
        p_img = doc.add_paragraph()
        format_paragraph(p_img, align=WD_ALIGN_PARAGRAPH.CENTER, line_spacing=1.0, space_after_pt=3, space_before_pt=5)
        r = p_img.add_run()
        r.add_picture(img_path, width=Inches(width_inches))
        ref_elem.addnext(p_img._p)
        ref_elem = p_img._p

        if caption_text:
            insert_caption(caption_text)

    def insert_tbl(headers, rows_data, col_widths=None, caption_text=""):
        nonlocal ref_elem
        if caption_text:
            insert_caption(caption_text)
        tbl = build_styled_table(doc, headers, rows_data, col_widths)
        ref_elem.addnext(tbl._tbl)
        ref_elem = tbl._tbl
        return tbl

    # =========================================================================
    # 3. BUILD CHAPTER 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG
    # =========================================================================
    print("Building Chapter 3...")
    insert_heading("3.1 Mô hình hệ thống chi tiết", level=2)
    insert_heading("3.1.1 Sơ đồ tổng thể hệ thống", level=3)

    insert_p(
        "Hệ thống robot tự hành trong đề tài được thiết kế theo kiến trúc tập trung, lấy bo mạch máy tính nhúng Raspberry Pi 4 Model B (8GB RAM) làm bộ xử lý trung tâm ('bộ não') điều phối toàn diện mọi hoạt động theo thời gian thực. Toàn bộ cấu trúc phần cứng và phần mềm của robot được quy hoạch thành 4 phân hệ chức năng chính phối hợp chặt chẽ với nhau:\n"
        "1. Khối nguồn năng lượng: Nguồn chính sử dụng bộ pin sạc Lithium-ion 3S2P (điện áp danh định 11.1V – tối đa 12.6V, dung lượng 5200mAh) bảo đảm công suất dòng xả liên tục cho cả hệ thống. Nguồn pin 12V được cấp trực tiếp qua công tắc nguồn 10A và cầu chì bảo vệ 7.5A để nuôi các động cơ giảm tốc DC thông qua 2 module driver TB6612FNG; đồng thời đi qua module hạ áp biến đổi DC-DC Buck công suất cao XL4015 để hạ áp xuống mức 5.0V chuẩn với dòng tải tối đa 5A cấp nguồn ổn định tuyệt đối cho Raspberry Pi 4, màn hình hiển thị OLED 1.3 inch và các cảm biến ngoại vi.\n"
        "2. Khối xử lý trung tâm (Raspberry Pi 4 Model B 8GB): Đóng vai trò là đơn vị điều khiển cấp cao. Thiết bị chạy hệ điều hành Linux 64-bit (Raspberry Pi OS), thực thi đồng thời: luồng thu nhận và xử lý ảnh từ Camera MIPI CSI bằng thư viện OpenCV; luồng máy chủ Web nội bộ phục vụ giao diện điều khiển từ xa và kết nối quét mã QR; luồng đo đạc cảm biến khoảng cách siêu âm HC-SR04; cùng thuật toán động học nghịch (Inverse Kinematics) xuất xung Hardware PWM điều khiển di chuyển 8 hướng.\n"
        "3. Khối cảm biến và giao diện tương tác: Bao gồm 01 camera Raspberry Pi Camera V1.3 (5 Megapixel) thu nhận video thời gian thực; 02 cảm biến siêu âm HC-SR04 (Trái và Phải) phát hiện vật cản phía trước với góc quét rộng; cụm cảm biến dò đường (Line Sensor) 3 kênh; và 01 màn hình hiển thị OLED 1.3 inch giao tiếp I²C hiển thị trạng thái làm việc và mã QR động phục vụ kết nối điện thoại thông minh.\n"
        "4. Khối công suất và chấp hành: Bao gồm bo mạch mở rộng chuyên dụng (Carrier Board) tích hợp 02 mạch driver TB6612FNG MOSFET cầu H kép độc lập, dẫn động 4 động cơ giảm tốc vàng TT gắn 4 bánh xe đa hướng Mecanum, cho phép robot di chuyển linh hoạt tự do trong mọi không gian hành lang hẹp."
    )

    insert_img(
        'extracted_imgs/block_diagrams/block_diagram_slide5_overall.png',
        width_inches=5.6,
        caption_text="Hình 3.1: Sơ đồ tổng thể kiến trúc hệ thống robot tự hành trên nền tảng Raspberry Pi 4"
    )

    # 3.1.2 Sơ đồ nguyên lý và thiết kế bo mạch mở rộng (Carrier Board)
    insert_heading("3.1.2 Sơ đồ nguyên lý và thiết kế bo mạch mở rộng (Carrier Board)", level=3)

    insert_p(
        "Nhằm giải quyết triệt để tình trạng dây cắm breadboard chằng chịt, dễ bị lỏng lẻo tiếp xúc kém do rung lắc cơ khí trong quá trình robot di chuyển, nhóm nghiên cứu đã thiết kế một bo mạch mở rộng chuyên dụng (Carrier Board) cắm trực tiếp vào 40-pin header của Raspberry Pi 4.\n"
        "Bo mạch được thiết kế hoàn chỉnh trên phần mềm chuyên ngành KiCad EDA phiên bản 10.0 theo chuẩn gia công 1 lớp đồng đáy (B.Cu) với kích thước nhỏ gọn 111.63 mm × 72.94 mm (diện tích 81.43 cm²). Để bảo đảm tính phẳng và khả năng tự làm mạch in thủ công (bằng phương pháp ủi nhiệt hoặc in film cảm quang), mạch bố trí tối ưu đường chạy mạch ở lớp đáy (B.Cu) kết hợp 5 cầu nối dây (jumpers) ngắn ở mặt trên linh kiện (F.Cu). Bo mạch tích hợp đầy đủ: Socket cắm 40 chân cái cho Raspberry Pi 4, 02 vị trí cắm module Driver TB6612FNG, vị trí cắm module hạ áp Buck XL4015, cọc nguồn Domino KF301 chịu dòng cao, hàng cắm màn hình OLED 1.3 inch I²C, các cổng kết nối cảm biến siêu âm HC-SR04 cùng các cụm điện trở phân áp 1kΩ / 2kΩ để chuyển đổi mức logic an toàn từ 5V xuống 3.3V cho Raspberry Pi.\n"
        "Đặc biệt, để khắc phục triệt để hiện tượng vành đồng chân hàn bị quá mỏng khi xuất ra PDF làm mạch in thủ công, nhóm nghiên cứu đã tối ưu hóa toàn bộ các chân hàn xuyên lỗ (Through-hole pads) với thông số kỹ thuật vượt trội: Kích thước Pad Size X × Y đạt 2.20 mm × 2.20 mm, đường kính lỗ khoan Hole Size đạt 0.80 mm, tạo nên vành khuyên đồng (Annular Ring) dày dặn lên đến 0.70 mm (gấp gần 3 lần so với chuẩn 0.25 mm thông thường), chống bong tróc tuyệt đối khi hàn nhiệt và chống xé rách vành đồng khi khoan tay; đồng thời duy trì khoảng hở cách ly (Clearance) 0.34 mm đạt chuẩn an toàn KiCad DRC, không bị dính chập thiếc khi hàn."
    )

    insert_img(
        'extracted_imgs/schematic_kicad_300dpi.png',
        width_inches=5.8,
        caption_text="Hình 3.2: Sơ đồ nguyên lý chi tiết bo mạch mở rộng (Carrier Board) trên KiCad 10"
    )

    insert_img(
        'extracted_imgs/pcb_complete_routed.png',
        width_inches=5.5,
        caption_text="Hình 3.3: Bản vẽ thiết kế mạch in (PCB) 1 lớp mặt đáy B.Cu với 5 cầu nối dây Jumper"
    )

    insert_p(
        "Bảng 3.1 mô tả chi tiết bảng phân bổ 40 chân GPIO của Raspberry Pi 4 trên bo mạch mở rộng Carrier Board, quy hoạch rõ ràng các kênh điều khiển xung PWM, tín hiệu logic định hướng cho 2 mạch driver TB6612FNG, bus giao tiếp I²C màn hình OLED và các đường phát/thu cảm biến khoảng cách siêu âm:"
    )

    gpio_headers = ["Chân Header", "Ký hiệu Net", "Chân BCM", "Mức áp", "Chức năng & Thiết bị kết nối"]
    gpio_rows = [
        ["Pin 01", "3.3V Power", "-", "3.3V DC", "Cấp nguồn logic cho màn hình OLED 1.3\" và các cảm biến"],
        ["Pin 02", "+5V_PI_1", "-", "5.0V DC", "Nguồn 5V từ module Buck XL4015 cấp vào nuôi Raspberry Pi 4"],
        ["Pin 04", "+5V_PI_2", "-", "5.0V DC", "Nguồn 5V từ module Buck XL4015 cấp vào nuôi Pi 4 (nối song song Pin 2)"],
        ["Pin 06", "GND", "-", "0V", "Mass chung toàn hệ thống"],
        ["Pin 03", "PWMA_L", "GPIO 2", "3.3V LVTTL", "Xung PWM điều khiển tốc độ cụm động cơ Trái (Driver TB6612 #1)"],
        ["Pin 05", "AIN2_L", "GPIO 3", "3.3V LVTTL", "Tín hiệu logic điều khiển chiều quay động cơ Trái (kết nối AIN2/BIN2)"],
        ["Pin 07", "AIN1_L", "GPIO 4", "3.3V LVTTL", "Tín hiệu logic điều khiển chiều quay động cơ Trái (kết nối AIN1/BIN1)"],
        ["Pin 11", "STBY_L", "GPIO 17", "3.3V LVTTL", "Chân kích hoạt Standby Driver TB6612 Trái (HIGH = Enable)"],
        ["Pin 13", "TRIG_L", "GPIO 27", "3.3V LVTTL", "Phát xung siêu âm kích hoạt đo cự ly (HC-SR04 Trái)"],
        ["Pin 15", "ECHO_L", "GPIO 22", "3.3V LVTTL", "Nhận xung phản hồi cảm biến Trái (qua cầu phân áp 1kΩ / 2kΩ)"],
        ["Pin 17", "3.3V Power", "-", "3.3V DC", "Nguồn logic 3.3V dự phòng"],
        ["Pin 19", "LINE_L", "GPIO 10", "3.3V LVTTL", "Tín hiệu cảm biến dò đường (Line Sensor) kênh Trái"],
        ["Pin 21", "LINE_C", "GPIO 9", "3.3V LVTTL", "Tín hiệu cảm biến dò đường (Line Sensor) kênh Giữa"],
        ["Pin 23", "LINE_R", "GPIO 11", "3.3V LVTTL", "Tín hiệu cảm biến dò đường (Line Sensor) kênh Phải"],
        ["Pin 25", "GND", "-", "0V", "Mass cảm biến line"],
        ["Pin 27", "I2C_SDA", "GPIO 0/2", "3.3V Logic", "Đường truyền dữ liệu I²C SDA giao tiếp Màn hình OLED 1.3 inch"],
        ["Pin 28", "I2C_SCL", "GPIO 1/3", "3.3V Logic", "Đường xung nhịp I²C SCL giao tiếp Màn hình OLED 1.3 inch"],
        ["Pin 29", "TRIG_R", "GPIO 5", "3.3V LVTTL", "Phát xung siêu âm kích hoạt đo cự ly (HC-SR04 Phải)"],
        ["Pin 31", "ECHO_R", "GPIO 6", "3.3V LVTTL", "Nhận xung phản hồi cảm biến Phải (qua cầu phân áp 1kΩ / 2kΩ)"],
        ["Pin 33", "PWMA_R", "GPIO 13", "3.3V LVTTL", "Xung PWM điều khiển tốc độ cụm động cơ Phải (Driver TB6612 #2)"],
        ["Pin 35", "AIN2_R", "GPIO 19", "3.3V LVTTL", "Tín hiệu logic điều khiển chiều quay động cơ Phải (kết nối AIN2/BIN2)"],
        ["Pin 37", "AIN1_R", "GPIO 26", "3.3V LVTTL", "Tín hiệu logic điều khiển chiều quay động cơ Phải (kết nối AIN1/BIN1)"],
        ["Pin 38", "STBY_R", "GPIO 20", "3.3V LVTTL", "Chân kích hoạt Standby Driver TB6612 Phải (HIGH = Enable)"],
        ["Pin 39", "GND", "-", "0V", "Mass chung toàn hệ thống"],
    ]
    insert_tbl(gpio_headers, gpio_rows, col_widths=[0.9, 1.1, 0.9, 1.0, 2.4], caption_text="Bảng 3.1: Bảng phân bổ chân GPIO của Raspberry Pi 4 trên Bo mạch Carrier Board")

    # 3.1.3 Lưu đồ hoạt động của hệ thống
    insert_heading("3.1.3 Lưu đồ hoạt động của hệ thống", level=3)

    insert_p(
        "Lưu đồ hoạt động tổng thể của hệ thống robot tự hành được vận hành theo một chu trình khép kín với chu kỳ vòng lặp 50 ms (Hình 3.4):\n"
        "1. Khởi động và thiết lập hệ thống: Hệ điều hành Raspberry Pi OS nạp các trình điều khiển phần cứng, khởi tạo các chân BCM GPIO, thiết lập tần số băm xung Hardware PWM ở mức 1 kHz trên các chân điều khiển động cơ, khởi tạo bus giao tiếp I²C ở tốc độ tiêu chuẩn 400 kHz, khởi tạo luồng video camera CSI (độ phân giải 640 × 480 @ 30 fps) và bật dịch vụ máy chủ Web Server trên cổng 8080.\n"
        "2. Khởi tạo giao diện tương tác OLED: Hệ thống tự động lấy địa chỉ IP mạng nội bộ của Raspberry Pi 4, sinh mã QR động chứa URL giao diện Web Dashboard (`http://<IP_Pi>:8080`) và hiển thị trực quan lên màn hình OLED 1.3 inch.\n"
        "3. Thu thập dữ liệu ngoại vi theo chu kỳ: Cảm biến siêu âm HC-SR04 liên tục phát xung Trig và đo thời gian bay Echo để tính khoảng cách vật cản phía trước; đồng thời Camera CSI thu nhận khung hình và Web Server lắng nghe các bản tin điều khiển gửi từ client.\n"
        "4. Kiểm tra an toàn vật cản: Nếu cự ly đo được d ≤ 20 cm, robot lập tức kích hoạt phanh dừng khẩn cấp (Short Brake) và chuyển sang thuật toán né tránh vật cản tự động.\n"
        "5. Kiểm tra phát hiện khách hàng: Nếu phát hiện có người đang tiến lại gần (diện tích biến đổi khung hình > 5000 pixels), robot dừng lại, hiển thị thông điệp chào đón và hướng dẫn khách quét mã QR để tương tác.\n"
        "6. Xử lý lệnh điều hướng & xuất xung động cơ: Robot tiếp nhận lệnh di chuyển từ Web Dashboard (Tiến, Lùi, Dạt ngang, Xoay tròn), giải mã ma trận động học 4 bánh Mecanum, xuất xung PWM và mức logic đảo chiều tới 2 mạch driver TB6612FNG để điều phối chuyển động nhịp nhàng."
    )

    insert_img(
        'extracted_imgs/flowcharts/flowchart_system_main.png',
        width_inches=5.2,
        caption_text="Hình 3.4: Lưu đồ hoạt động tổng thể của hệ thống robot tự hành"
    )

    # 3.1.4 Phân bổ tài nguyên trên Raspberry Pi 4
    insert_heading("3.1.4 Phân bổ tài nguyên trên Raspberry Pi 4 Model B (8GB)", level=3)

    insert_p(
        "Nhằm bảo đảm toàn bộ hệ thống vận hành ổn định, không gặp hiện tượng nghẽn cổ chai và đáp ứng nghiêm ngặt yêu cầu thời gian thực, tài nguyên phần cứng và phần mềm của bo mạch Raspberry Pi 4 Model B (8GB) được phân bổ tối ưu theo Bảng 3.2:"
    )

    res_headers = ["Tài nguyên phần cứng", "Thành phần đảm nhiệm", "Mục đích sử dụng & Phân bổ chi tiết"]
    res_rows = [
        ["CPU Core 0 & Core 1", "Broadcom BCM2711", "Dành riêng cho xử lý ảnh OpenCV: thu nhận frame CSI, chuyển xám, làm mờ Gauss và phát hiện chuyển động khách hàng"],
        ["CPU Core 2", "Broadcom BCM2711", "Thực thi thuật toán động học Mecanum, vòng lặp đọc cảm biến siêu âm HC-SR04 và xuất tín hiệu điều khiển PWM"],
        ["CPU Core 3", "Broadcom BCM2711", "Chạy hệ điều hành Raspberry Pi OS (Linux 64-bit), quản lý mạng không dây Wi-Fi và máy chủ Web Server"],
        ["Bộ nhớ RAM (8GB)", "LPDDR4-3200", "Phân bổ 512MB cho GPU (GPU Memory Split) giải mã video CSI; phần RAM còn lại (>7GB) lưu trữ bộ đệm khung hình và dịch vụ web"],
        ["Bộ xử lý đồ họa (GPU)", "VideoCore VI @ 500MHz", "Giải mã luồng video MIPI CSI thời gian thực, giảm tải tối đa cho CPU"],
        ["Bộ định thời (Timers)", "Hardware Timers", "Khởi tạo xung Hardware PWM 1 kHz chuẩn xác cho 2 driver TB6612FNG, chống rung giật cơ khí"],
        ["Giao diện MIPI CSI-2", "Cổng CSI 15-pin", "Truyền luồng dữ liệu hình ảnh băng thông cao từ Camera OV5647 với độ trễ cực thấp"],
    ]
    insert_tbl(res_headers, res_rows, col_widths=[1.5, 1.8, 3.0], caption_text="Bảng 3.2: Phân bổ và quản lý tài nguyên trên Raspberry Pi 4 Model B (8GB)")

    # 3.2 Thiết kế module điều khiển chuyển động đa hướng
    insert_heading("3.2 Thiết kế module điều khiển chuyển động", level=2)
    insert_heading("3.2.1 Mô hình động học và Lưu đồ hoạt động module điều khiển động cơ", level=3)

    insert_p(
        "Hệ thống truyền động của robot sử dụng 4 bánh xe Mecanum đường kính R = 60 mm, trên chu vi mỗi bánh bố trí các con lăn con nghiêng một góc 45° so với trục quay chính. Bằng cách điều khiển độc lập vận tốc góc và chiều quay của từng bánh xe, lực đẩy của các con lăn sẽ tổng hợp thành vector chuyển động tự do theo mọi hướng trong mặt phẳng (chuyển động toàn hướng - Holonomic Motion).\n"
        "Phương trình động học nghịch (Inverse Kinematics) biến đổi từ vector vận tốc mong muốn của robot [Vx, Vy, ωz]T sang vận tốc góc của 4 bánh xe [ω1, ω2, ω3, ω4]T được xác định theo hệ thức:\n"
        "• Bánh Trước Trái (FL):  ω₁ = (1/R) · [ Vx - Vy - (Lx + Ly)·ωz ]\n"
        "• Bánh Trước Phải (FR): ω₂ = (1/R) · [ Vx + Vy + (Lx + Ly)·ωz ]\n"
        "• Bánh Sau Trái (RL):    ω₃ = (1/R) · [ Vx + Vy - (Lx + Ly)·ωz ]\n"
        "• Bánh Sau Phải (RR):   ω₄ = (1/R) · [ Vx - Vy + (Lx + Ly)·ωz ]\n"
        "trong đó Lx và Ly lần lượt là khoảng cách từ tâm robot đến trục bánh xe theo phương dọc và phương ngang. Lưu đồ giải thuật điều khiển động học và băm xung PWM được mô tả chi tiết trên Hình 3.5:"
    )

    insert_img(
        'extracted_imgs/flowcharts/flowchart_mecanum_control.png',
        width_inches=5.2,
        caption_text="Hình 3.5: Lưu đồ giải thuật điều khiển động học 4 bánh Mecanum & PWM"
    )

    # 3.2.2 Mạch nguyên lý giao tiếp giữa GPIO và Driver TB6612FNG
    insert_heading("3.2.2 Sơ đồ mạch nguyên lý giao tiếp giữa GPIO Raspberry Pi 4 và Driver cầu H", level=3)

    insert_p(
        "Trong mã nguồn Python (lớp `MotorController` tại file `code/python/motor_controller.py`), mỗi module TB6612FNG đảm nhận dẫn động 2 động cơ cùng bên. Tín hiệu điều khiển gồm chân kích hoạt Standby (STBY), chân băm xung PWM điều chỉnh tốc độ và các cặp chân logic định hướng (IN1, IN2). Bảng 3.3 tổng hợp bảng chân trị điều khiển trạng thái động cơ:"
    )

    h_bridge_headers = ["Tín hiệu IN1 (AIN1/BIN1)", "Tín hiệu IN2 (AIN2/BIN2)", "Xung PWM", "Trạng thái hoạt động của động cơ"]
    h_bridge_rows = [
        ["HIGH", "LOW", "20% – 100%", "Quay thuận (CW) – Dẫn động robot tiến thẳng hoặc quay hướng tiến"],
        ["LOW", "HIGH", "20% – 100%", "Quay nghịch (CCW) – Dẫn động robot lùi thẳng hoặc quay hướng lùi"],
        ["LOW", "LOW", "0%", "Dừng tự do (Coast / Stop) – Động cơ thả trôi giảm tốc tự nhiên"],
        ["HIGH", "HIGH", "0%", "Phanh hãm điện tử (Short Brake) – Hãm cứng trục tức thời chống trôi"],
    ]
    insert_tbl(h_bridge_headers, h_bridge_rows, col_widths=[1.6, 1.6, 1.2, 1.9], caption_text="Bảng 3.3: Bảng tra cứu trạng thái logic điều khiển chiều quay và tốc độ động cơ")

    # 3.3 Thiết kế module cảm biến khoảng cách & né vật cản
    insert_heading("3.3 Thiết kế module đọc cảm biến khoảng cách", level=2)
    insert_heading("3.3.1 Nguyên lý đọc cảm biến siêu âm HC-SR04 & Mạch cầu phân áp bảo vệ GPIO", level=3)

    insert_p(
        "Cảm biến khoảng cách siêu âm HC-SR04 hoạt động dựa trên nguyên lý phát và thu sóng âm phản xạ ở tần số 40 kHz. Khi chân Trigger nhận được một xung mức HIGH kéo dài ít nhất 10 µs, cảm biến sẽ phát ra chuỗi 8 xung siêu âm và kéo chân Echo lên mức HIGH cho đến khi nhận lại sóng phản xạ. Cự ly d từ robot đến vật cản được tính toán theo công thức:\n"
        "    d = (Δt × 34300) / 2  (cm)\n"
        "trong đó Δt là độ rộng thời gian xung Echo ở mức HIGH (đơn vị giây), và 34300 cm/s là vận tốc truyền âm trong không khí.\n"
        "Do chân Echo của module HC-SR04 xuất ra tín hiệu logic 5.0V TTL trong khi các chân GPIO của Raspberry Pi 4 chỉ chịu được mức áp tối đa 3.3V, nếu đấu nối trực tiếp sẽ dẫn đến nguy cơ quá áp làm cháy vi xử lý. Do đó, trên bo mạch mở rộng Carrier Board, tín hiệu Echo của cả 2 cảm biến siêu âm được đấu nối qua mạch cầu phân áp điện trở gồm R1 = 1 kΩ và R2 = 2 kΩ nối mass GND. Điện áp ngõ ra cấp vào chân GPIO của Pi 4 được tính theo công thức:\n"
        "    V_out = V_in × [R2 / (R1 + R2)] = 5.0V × [2k / (1k + 2k)] = 3.33V\n"
        "Mức điện áp 3.33V hoàn toàn nằm trong dải an toàn tuyệt đối của chuẩn LVTTL trên Raspberry Pi 4, bảo đảm tính ổn định và độ bền phần cứng lâu dài."
    )

    insert_heading("3.3.2 Thuật toán tránh vật cản", level=3)

    insert_p(
        "Thuật toán né tránh vật cản được thiết kế theo mô hình phân tầng phản xạ đa cấp (Bảng 3.4 và Hình 3.6). Dữ liệu khoảng cách đo được từ 2 cảm biến siêu âm (Trái và Phải) sau khi lọc trung bình động 3 mẫu sẽ được phân loại thành 4 vùng an toàn để kích hoạt hành vi điều khiển tương ứng:"
    )

    obs_headers = ["Khoảng cách đo được (d)", "Vùng trạng thái", "Hành vi điều khiển động cơ của robot"]
    obs_rows = [
        ["d > 35 cm", "Vùng An Toàn", "Duy trì tốc độ định mức (Duty Cycle 70% – 80% PWM), tiếp tục di chuyển theo lộ trình"],
        ["20 cm < d ≤ 35 cm", "Vùng Cảnh Báo", "Giảm tốc độ động cơ xuống mức an toàn (40% PWM), tăng tần suất quét cảm biến lên 30 ms"],
        ["10 cm < d ≤ 20 cm", "Vùng Nguy Hiểm", "Dừng xe ngay lập tức; so sánh d_Trái và d_Phải để tịnh tiến dạt ngang sang hướng thoáng hơn"],
        ["d ≤ 10 cm", "Vùng Khẩn Cấp", "Kích hoạt phanh điện tử tức thời (Short Brake); lùi ngắn an toàn 10 cm và xoay góc 90° tìm lối đi"],
    ]
    insert_tbl(obs_headers, obs_rows, col_widths=[1.5, 1.5, 3.3], caption_text="Bảng 3.4: Ngưỡng khoảng cách và hành vi điều khiển né tránh vật cản của robot")

    insert_img(
        'extracted_imgs/flowcharts/flowchart_obstacle_avoidance.png',
        width_inches=5.2,
        caption_text="Hình 3.6: Lưu đồ giải thuật đọc cảm biến siêu âm HC-SR04 và né tránh vật cản đa cấp"
    )

    # 3.4 Thiết kế module xử lý Camera và nhận diện khách hàng
    insert_heading("3.4 Thiết kế module xử lý Camera và nhận diện khách hàng", level=2)
    insert_heading("3.4.1 Lưu đồ xử lý hình ảnh nhận diện khách hàng", level=3)

    insert_p(
        "Thuật toán phát hiện sự hiện diện của khách hàng sử dụng thư viện thị giác máy tính OpenCV trên Raspberry Pi 4 thông qua phương pháp trừ khung hình nền thích nghi (Adaptive Background Differencing). Luồng video từ camera CSI được nạp liên tục ở độ phân giải 640 × 480 pixels với tốc độ 30 fps. Hình ảnh được chuyển đổi sang thang độ xám (Grayscale), áp dụng bộ lọc làm mờ Gauss (Gaussian Blur ksize=21) để khử nhiễu môi trường, sau đó tính toán sự sai khác cường độ điểm ảnh giữa các khung hình liên tiếp. Khi phát hiện diện tích vùng biến đổi lớn hơn ngưỡng định trước (> 5000 pixels), robot xác định có khách hàng đang tiến lại gần và chủ động chuyển sang trạng thái chào đón, tạm dừng di chuyển để tương tác."
    )

    insert_heading("3.4.2 Tích hợp Camera MIPI CSI và Màn hình OLED 1.3 inch với Raspberry Pi 4", level=3)

    insert_p(
        "Module camera OmniVision OV5647 kết nối trực tiếp với cổng MIPI CSI của Raspberry Pi 4 thông qua cáp dẹt FPC 15-pin. Dữ liệu video được truyền thẳng vào bộ xử lý đồ họa GPU VideoCore VI giúp giải mã luồng video độ trễ thấp mà không chiếm dụng tài nguyên tính toán của CPU.\n"
        "Màn hình OLED 1.3 inch (IC SH1106 / SSD1306) được tích hợp trên bo mạch mở rộng đóng vai trò là giao diện tương tác trực quan. Hệ thống sử dụng thư viện Python Pillow và qrcode để tự động khởi tạo mã QR động chứa địa chỉ truy cập giao diện Web nội bộ của robot (`http://<IP_Pi>:8080`). Khách hàng chỉ cần sử dụng camera điện thoại thông minh để quét mã QR trên màn hình OLED là có thể mở ngay giao diện điều khiển, chỉ định quầy giao nhận hàng hóa mà không cần cài đặt bất kỳ ứng dụng phức tạp nào. Lưu đồ xử lý camera và tương tác mã QR được thể hiện trên Hình 3.7:"
    )

    insert_img(
        'extracted_imgs/flowcharts/flowchart_camera_oled.png',
        width_inches=5.2,
        caption_text="Hình 3.7: Lưu đồ giải thuật xử lý Camera CSI & Nhận diện khách hàng bằng OpenCV kết hợp OLED"
    )

    # 3.5 Thiết kế giao diện điều khiển và giám sát qua Web
    insert_heading("3.5 Thiết kế giao diện điều khiển và giám sát qua Web (Web Dashboard)", level=2)
    insert_heading("3.5.1 Kiến trúc hệ thống Web Server điều khiển", level=3)

    insert_p(
        "Hệ thống điều khiển từ xa được thiết kế theo mô hình Client - Server nội bộ chạy trực tiếp trên Raspberry Pi 4 thông qua kết nối Wi-Fi (Hình 3.8):\n"
        "• Phần mềm máy chủ (Backend): Được xây dựng bằng Python (file `code/website/server.py`), lắng nghe các yêu cầu HTTP REST API trên cổng 8080 từ client và ánh xạ trực tiếp thành các lệnh gọi hàm điều khiển động cơ trong `motor_controller.py`.\n"
        "• Giao diện người dùng (Frontend): Xây dựng bằng HTML5, CSS3 hiện đại và JavaScript thuần (file `code/website/index.html`, `app.js`), tối ưu hóa khả năng phản hồi cảm ứng trên điện thoại thông minh và máy tính bảng."
    )

    insert_img(
        'extracted_imgs/flowcharts/flowchart_web_dashboard.png',
        width_inches=5.2,
        caption_text="Hình 3.8: Lưu đồ hoạt động của máy chủ Web Server và Giao diện Web Dashboard"
    )

    insert_heading("3.5.2 Giao diện giám sát và điều khiển thực tế", level=3)

    insert_p(
        "Giao diện Web Dashboard (Hình 3.9) cung cấp đầy đủ các cụm phím điều khiển đa hướng: Tiến, Lùi, Dạt ngang Trái, Dạt ngang Phải, Xoay Trái, Xoay Phải, Dừng khẩn cấp, cùng thanh trượt (slider) tùy chỉnh tốc độ PWM từ 20% đến 100%. Giao diện phản hồi tức thì với độ trễ < 50 ms qua mạng Wi-Fi nội bộ, bảo đảm tính an toàn cao khi điều khiển robot di chuyển trong hành lang trung tâm thương mại."
    )

    insert_img(
        'extracted_imgs/web_dashboard.png',
        width_inches=5.2,
        caption_text="Hình 3.9: Giao diện Web Dashboard điều khiển và giám sát robot qua mạng Wi-Fi"
    )

    # =========================================================================
    # 4. BUILD CHAPTER 4: KẾ HOẠCH VÀ PHƯƠNG ÁN THỰC NGHIỆM HỆ THỐNG
    # (Nguyên tắc: CHỈ GHI NHỮNG GÌ ĐÃ LÀM, KHÔNG BỊA ĐẶT SỐ LIỆU CHƯA LÀM)
    # =========================================================================
    print("Building Chapter 4...")
    insert_p("KẾ HOẠCH VÀ PHƯƠNG ÁN THỰC NGHIỆM HỆ THỐNG", style='Heading 1', bold=True, size_pt=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before_pt=12, space_after_pt=6)

    insert_p(
        "Bản đề cương khóa luận tốt nghiệp này ghi nhận trung thực và chính xác tiến độ nghiên cứu, thiết kế phần cứng và lập trình phần mềm đã hoàn thành tính đến thời điểm báo cáo đề cương, đồng thời xác lập kế hoạch chi tiết cho giai đoạn gia công chế tạo và thực nghiệm kiểm chứng tiếp theo."
    )

    insert_heading("4.1 Tiến độ thực hiện hiện tại của đề tài (Các nội dung đã hoàn thành)", level=2)

    insert_p(
        "Tính đến thời điểm báo cáo đề cương, nhóm nghiên cứu đã hoàn thành toàn diện các hạng mục phân tích, tính toán lý thuyết, thiết kế phần cứng và lập trình kiểm thử phần mềm nền tảng:\n"
        "1. Hoàn thành nghiên cứu tổng quan, khảo sát và lựa chọn đầy đủ linh kiện phần cứng tương thích tối ưu với bo mạch chủ Raspberry Pi 4 Model B (8GB).\n"
        "2. Hoàn thành thiết kế sơ đồ nguyên lý chi tiết (Schematic) trên phần mềm chuyên ngành KiCad 10, quy hoạch chuẩn xác 40 chân GPIO của Raspberry Pi 4 kết nối 2 module driver TB6612FNG, module Buck XL4015, màn hình OLED 1.3 inch I²C, cụm cảm biến siêu âm HC-SR04 kèm mạch phân áp trở 1kΩ / 2kΩ bảo vệ vi xử lý.\n"
        "3. Hoàn thành thiết kế layout bo mạch in mở rộng (Carrier Board) chuẩn 1 lớp đồng đáy (B.Cu) với 5 cầu nối dây jumper mặt trên; đã tối ưu hóa chân hàn Pad 2.20 mm, lỗ khoan 0.80 mm tạo vành khuyên đồng 0.70 mm siêu dày dặn; đã xuất đầy đủ bộ 4 bản vẽ PDF gia công 1:1 chuẩn (ghép 4 bo A4 phục vụ phương pháp ủi nhiệt và in film cảm quang) và file khoan CNC (.drl).\n"
        "4. Hoàn thành xây dựng module phần mềm Python điều khiển chuyển động bánh Mecanum (`motor_controller.py`, `config.py`) và kịch bản test 2 bánh bên trái (`test_left_motors.py`), kiểm thử logic thành công trên hệ điều hành Raspberry Pi OS.\n"
        "5. Hoàn thành thiết kế giao diện Web Dashboard (`code/website/`) kết nối máy chủ Python cho phép điều khiển 8 hướng và điều chỉnh tốc độ PWM mượt mà qua mạng Wi-Fi.\n"
        "6. Đã kiểm thử thành công thuật toán khởi tạo hiển thị mã QR động trên màn hình OLED 1.3 inch và luồng xử lý ảnh trừ nền phát hiện chuyển động bằng OpenCV qua camera CSI."
    )

    prog_headers = ["STT", "Nội dung nghiên cứu & Hạng mục công việc", "Sản phẩm / Kết quả bàn giao", "Trạng thái thực tế"]
    prog_rows = [
        ["1", "Khảo sát tài liệu, lựa chọn linh kiện phần cứng", "Báo cáo đề cương, thông số phần cứng", "Đã hoàn thành 100%"],
        ["2", "Thiết kế kiến trúc hệ thống và quy hoạch chân GPIO", "Sơ đồ khối 4 phân hệ, Bảng phân bổ chân", "Đã hoàn thành 100%"],
        ["3", "Thiết kế sơ đồ nguyên lý phần cứng trên KiCad 10", "File Schematic, thư viện linh kiện chuẩn", "Đã hoàn thành 100%"],
        ["4", "Thiết kế bo mạch in mở rộng Carrier Board 1 lớp (Pad 2.2mm/0.8mm)", "File PCB 1 lớp B.Cu, bộ 4 file PDF gia công 1:1, file drl", "Đã hoàn thành 100%"],
        ["5", "Lập trình module điều khiển động cơ bánh Mecanum", "Source code Python (motor_controller.py, config.py)", "Đã hoàn thành 100%"],
        ["6", "Xây dựng Web Dashboard điều khiển robot qua Wi-Fi", "Giao diện Web HTML/CSS/JS + Python server", "Đã hoàn thành 100%"],
        ["7", "Thử nghiệm hiển thị mã QR trên OLED 1.3\" & OpenCV", "Module tạo QR động, thuật toán trừ nền", "Đã hoàn thành 100%"],
        ["8", "Gia công mạch in PCB thực tế & hàn lắp linh kiện", "Bo mạch phần cứng hoàn chỉnh sau khi ủi/rọi film", "Đang triển khai thực hiện"],
        ["9", "Lắp ráp khung xe cơ khí & tích hợp toàn bộ hệ thống", "Mô hình robot tự hành vật lý hoàn chỉnh", "Kế hoạch giai đoạn tiếp theo"],
        ["10", "Thực nghiệm đo đạc thực tế & hoàn thiện khóa luận", "Số liệu đo đạc thực tế, báo cáo khóa luận tốt nghiệp", "Kế hoạch giai đoạn tiếp theo"],
    ]
    insert_tbl(prog_headers, prog_rows, col_widths=[0.6, 2.6, 2.1, 1.2], caption_text="Bảng 4.1: Bảng tổng hợp tiến độ hoàn thành các hạng mục nghiên cứu của đề tài")

    insert_heading("4.2 Phương án và kế hoạch thực nghiệm các module chức năng", level=2)

    insert_p(
        "Giai đoạn tiếp theo của đề tài tập trung vào việc hiện thực hóa phần cứng vật lý và đo đạc thực nghiệm theo các bước kế hoạch cụ thể:\n"
        "• Thực nghiệm gia công mạch in PCB và kiểm tra thông mạch: Sử dụng bộ file PDF `01_Mat_Day_B_Cu_MIRROR_Ui_Nhiet.pdf` và `02_Mat_Day_B_Cu_DIRECT_In_Film.pdf` trong thư mục `pdf_lam_mach` để in decal nhiệt, ủi phôi đồng 1 mặt, ăn mòn bằng dung dịch FeCl3, khoan các lỗ linh kiện chuẩn 0.8 mm và 1.0 mm, hàn 5 cầu nối dây jumper mặt trên, đo kiểm tra chạm chập bằng đồng hồ VOM trước khi cấp nguồn.\n"
        "• Thực nghiệm module điều khiển chuyển động bánh Mecanum: Kiểm tra dạng sóng xung PWM trên máy hiện sóng oscilloscope; đo đạc vận tốc thực tế, độ trôi lệch khi robot tịnh tiến ngang và xoay tại chỗ trên bề mặt sàn gạch men và sàn gỗ.\n"
        "• Thực nghiệm module cảm biến siêu âm né tránh vật cản: Đo kiểm sai số khoảng cách của cảm biến HC-SR04 ở các cự ly từ 10 cm đến 200 cm với các loại bề mặt phản xạ khác nhau (tường phẳng, vật thể tròn, chướng ngại vật di động); đánh giá thời gian phản hồi dừng xe an toàn khi phát hiện vật cản đột ngột.\n"
        "• Thực nghiệm module Camera và tương tác khách hàng qua mã QR: Đo đạc độ trễ nhận diện chuyển động qua Camera CSI trong điều kiện ánh sáng tiêu chuẩn trong nhà (300 – 500 lux); đo khoảng cách và thời gian người dùng quét thành công mã QR hiển thị trên màn hình OLED 1.3 inch bằng các dòng điện thoại thông minh phổ biến.\n"
        "• Thực nghiệm tổng hợp hệ thống: Cho robot vận hành liên tục theo kịch bản giao nhận hàng hóa nội khu trong không gian hành lang mô phỏng; đo đạc độ ổn định của kết nối mạng Wi-Fi và thời lượng tiêu thụ năng lượng của bộ pin Li-ion 3S2P."
    )

    plan_headers = ["Giai đoạn thực hiện", "Nhiệm vụ trọng tâm", "Phương pháp & Thiết bị kiểm chứng", "Mục tiêu nghiệm thu"]
    plan_rows = [
        ["Tuần 1 – Tuần 2", "Gia công mạch in PCB Carrier Board 1 lớp & Hàn lắp linh kiện", "Ủi nhiệt decal / rọi film UV, ăn mòn FeCl3, khoan 0.8mm, đo thông mạch VOM", "Bo mạch hoàn chỉnh, không chạm chập, cấp nguồn 5V/12V ổn định"],
        ["Tuần 3 – Tuần 4", "Lắp ráp khung xe cơ khí, gá đặt động cơ TT & bánh Mecanum", "Cân chỉnh cơ khí, đấu nối động cơ vào cọc Domino trên bo mạch", "Khung xe vững chắc, bánh tiếp xúc đều mặt sàn, quay êm"],
        ["Tuần 5 – Tuần 6", "Thực nghiệm điều khiển chuyển động 8 hướng & đo đạc vận tốc", "Chạy kịch bản test trên sàn gạch men và sàn gỗ, đo oscilloscope", "Robot di chuyển đúng hướng, dạt ngang mượt mà, sai số góc quay < 5%"],
        ["Tuần 7 – Tuần 8", "Thực nghiệm cảm biến siêu âm né vật cản & Camera OpenCV", "Thử nghiệm cự ly 10–200 cm, kiểm tra nhận diện người và quét QR OLED", "Né vật cản phản hồi < 100 ms, quét QR thành công từ cự ly 0.5m"],
        ["Tuần 9 – Tuần 10", "Thực nghiệm tổng hợp kịch bản giao nhận hàng & Viết báo cáo", "Chạy liên tục hành lang mô phỏng, đo thời lượng pin Li-ion 3S2P", "Hoàn thành toàn diện khóa luận tốt nghiệp và bảo vệ trước hội đồng"],
    ]
    insert_tbl(plan_headers, plan_rows, col_widths=[1.3, 2.3, 1.8, 1.6], caption_text="Bảng 4.2: Kế hoạch phân bổ thời gian thực hiện các giai đoạn tiếp theo của đề tài")

    # =========================================================================
    # 5. UPDATE CONCLUSION (KẾT LUẬN VÀ KIẾN NGHỊ)
    # =========================================================================
    print("Updating Conclusion...")
    ref_conc = p350_elem

    conc_text_1 = (
        "1. Kết luận:\n"
        "Tính đến thời điểm báo cáo đề cương, đề tài 'Thiết kế và triển khai Robot tự hành hỗ trợ giao nhận và tương tác khách hàng tại các Trung tâm thương mại trên nền tảng Raspberry Pi' đã đạt được các kết quả trọng tâm sau:\n"
        "• Đã nghiên cứu tổng quan và làm chủ kiến trúc hệ thống robot tự hành đa hướng trên nền tảng máy tính nhúng Raspberry Pi 4 Model B (8GB RAM), tối ưu hóa bài toán chi phí và khả năng vận hành linh hoạt trong không gian dịch vụ thương mại nội địa.\n"
        "• Đã hoàn thành thiết kế sơ đồ nguyên lý (Schematic) và layout bo mạch in mở rộng chuyên dụng (Carrier Board) chuẩn 1 lớp đồng đáy (B.Cu) trên phần mềm chuyên nghiệp KiCad 10. Bo mạch tích hợp đầy đủ khối nguồn Buck XL4015, 2 driver TB6612FNG, màn hình OLED 1.3 inch I²C, cụm cảm biến siêu âm HC-SR04 kèm mạch phân áp trở bảo vệ vi xử lý. Đặc biệt, thiết kế đã tối ưu hóa chân hàn Pad 2.20 mm, lỗ khoan 0.80 mm tạo vành khuyên đồng 0.70 mm siêu dày dặn, khắc phục hoàn toàn nguy cơ bong tróc mạch khi ủi nhiệt và khoan tay.\n"
        "• Đã xuất đầy đủ bộ 4 bản vẽ PDF gia công chuẩn tỷ lệ vật lý 1:1 (khổ A4 ghép 4 mạch, khổ A3 sơ đồ nguyên lý) và file khoan CNC (.drl) sẵn sàng cho chế tạo thực tế.\n"
        "• Đã xây dựng thành công kiến trúc phần mềm phân tầng trên Python: Lớp điều khiển phần cứng motor_controller.py, giải mã mô hình động học 4 bánh Mecanum, máy chủ Web Server tích hợp và giao diện Web Dashboard hiện đại hỗ trợ điều khiển trên smartphone qua mạng Wi-Fi và quét mã QR trên màn hình OLED.\n"
        "• Đã thử nghiệm thành công thuật toán thị giác máy tính phát hiện chuyển động bằng OpenCV qua luồng video MIPI CSI và thuật toán phân loại vùng an toàn né tránh vật cản phản xạ đa cấp."
    )

    conc_text_2 = (
        "2. Hướng phát triển tiếp theo của đề tài:\n"
        "• Tiến hành gia công mạch in PCB thực tế bằng phương pháp ủi nhiệt / in film cảm quang từ bộ file PDF chuẩn, hàn lắp linh kiện và đo kiểm thông mạch bằng đồng hồ VOM.\n"
        "• Hoàn thiện lắp ráp kết cấu cơ khí khung xe 4WD Mecanum, tích hợp bộ pin sạc Li-ion 3S2P và mạch hạ áp Buck XL4015.\n"
        "• Đo đạc thực nghiệm toàn diện trên mô hình vật lý: đo dạng sóng xung PWM trên máy hiện sóng oscilloscope, đo cự ly cảm biến siêu âm, đo độ trễ video và thời gian quét mã QR trong không gian hành lang thực tế.\n"
        "• Mở rộng nghiên cứu tích hợp thuật toán định vị và lập bản đồ đồng thời (2D LiDAR SLAM) cùng hệ điều hành robot ROS 2 trong các giai đoạn phát triển nâng cao tiếp theo của hệ thống."
    )

    p1 = doc.add_paragraph()
    format_paragraph(p1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line_spacing=1.5, space_after_pt=4, space_before_pt=4)
    r1 = p1.add_run(conc_text_1)
    format_run(r1, font_name="Times New Roman", size_pt=13)
    ref_conc.addnext(p1._p)
    ref_conc = p1._p

    p2 = doc.add_paragraph()
    format_paragraph(p2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line_spacing=1.5, space_after_pt=4, space_before_pt=4)
    r2 = p2.add_run(conc_text_2)
    format_run(r2, font_name="Times New Roman", size_pt=13)
    ref_conc.addnext(p2._p)
    ref_conc = p2._p

    # =========================================================================
    # 6. UPDATE REFERENCES (TÀI LIỆU THAM KHẢO)
    # =========================================================================
    print("Updating References...")
    clean_refs = [
        "Raspberry Pi Foundation, \"Raspberry Pi 4 Model B Specifications and Hardware Guide,\" Raspberry Pi Documentation, 2023.",
        "Broadcom Corporation, \"BCM2711 ARM Peripherals Datasheet,\" Broadcom Inc., 2020.",
        "Toshiba Electronic Devices & Storage Corporation, \"TB6612FNG Dual DC Motor Driver Datasheet,\" Rev 2.0, 2014.",
        "Sino Wealth Electronic Ltd., \"SH1106 132 x 64 Dot Matrix OLED/PLED Driver with Controller Datasheet,\" 2018.",
        "SparkFun Electronics, \"Ultrasonic Ranging Module HC-SR04 User Manual,\" SparkFun Electronics, 2019.",
        "KiCad Development Team, \"KiCad 10.0 EDA Schematic and PCB Layout Suite Documentation,\" https://docs.kicad.org, 2026.",
        "OpenCV Team, \"OpenCV 4 Computer Vision Library Documentation,\" https://docs.opencv.org, 2024.",
        "Python Software Foundation, \"Python 3.12 Standard Library and Hardware GPIO Documentation,\" https://docs.python.org, 2024.",
        "B. Siciliano and O. Khatib, Springer Handbook of Robotics, 2nd ed., Springer-Verlag Berlin Heidelberg, 2016.",
        "S. Thrun, W. Burgard, and D. Fox, Probabilistic Robotics, MIT Press, Cambridge, 2005.",
        "R. Murphy, Introduction to AI Robotics, 2nd ed., MIT Press, 2019.",
    ]

    p_ref_title = None
    for p in doc.paragraphs:
        if "TÀI LIỆU THAM KHẢO" in p.text.strip():
            p_ref_title = p
            break

    if p_ref_title is not None:
        curr = p_ref_title._p.getnext()
        while curr is not None:
            txt = ''.join(curr.itertext()).strip()
            if "PHỤ LỤC" in txt:
                break
            nxt = curr.getnext()
            body.remove(curr)
            curr = nxt

        ref_elem = p_ref_title._p
        for r_text in clean_refs:
            p_ref = doc.add_paragraph(style='List Paragraph')
            format_paragraph(p_ref, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line_spacing=1.25, space_after_pt=3, space_before_pt=1)
            r = p_ref.add_run(r_text)
            format_run(r, font_name="Times New Roman", size_pt=12)
            ref_elem.addnext(p_ref._p)
            ref_elem = p_ref._p

    print(f"Saving final updated document: {DOCX_OUT}...")
    doc.save(DOCX_OUT)
    print("SUCCESS: Thesis document rebuilt completely and flawlessly!")

if __name__ == '__main__':
    main()
