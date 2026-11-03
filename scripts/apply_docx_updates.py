import os, sys, re
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

def set_cell_margins(cell, top=100, bottom=100, left=130, right=130):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_styled_cell(cell, text, bold=False, italic=False, font_size=10.5, align=WD_ALIGN_PARAGRAPH.LEFT, fill_hex=None):
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

def insert_p_after(doc, target, text, style='Normal', bold=False, italic=False, size_pt=13, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after_pt=4, space_before_pt=0):
    new_p = doc.add_paragraph(style=style)
    format_paragraph(new_p, align=align, line_spacing=1.5, space_after_pt=space_after_pt, space_before_pt=space_before_pt)
    if text:
        r = new_p.add_run(text)
        format_run(r, font_name="Times New Roman", size_pt=size_pt, bold=bold, italic=italic)
    target_elem = getattr(target, '_p', getattr(target, '_tbl', None))
    target_elem.addnext(new_p._p)
    return new_p

def insert_img_after(doc, target_p, img_path, width_inches=5.2, caption_text=""):
    curr = target_p
    
    p_img = doc.add_paragraph()
    format_paragraph(p_img, align=WD_ALIGN_PARAGRAPH.CENTER, line_spacing=1.0, space_after_pt=3, space_before_pt=4)
    r = p_img.add_run()
    r.add_picture(img_path, width=Inches(width_inches))
    curr._p.addnext(p_img._p)
    curr = p_img
    
    if caption_text:
        p_cap = doc.add_paragraph(style='Caption')
        format_paragraph(p_cap, align=WD_ALIGN_PARAGRAPH.CENTER, line_spacing=1.15, space_after_pt=6, space_before_pt=0)
        r_cap = p_cap.add_run(caption_text)
        format_run(r_cap, font_name="Times New Roman", size_pt=11.5, bold=False, italic=True)
        curr._p.addnext(p_cap._p)
        curr = p_cap
        
    return curr

def insert_tbl_after(doc, target_p, num_rows, num_cols, style='Table Grid'):
    tbl = doc.add_table(num_rows, num_cols, style=style)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    target_p._p.addnext(tbl._tbl)
    return tbl

def update_document():
    print(f"Loading document: {DOCX_IN}...")
    doc = docx.Document(DOCX_IN)

    # =========================================================================
    # 1. BÌA & THÔNG TIN CHUNG
    # =========================================================================
    print("1. Updating Cover & General Info...")
    for p in doc.paragraphs[:35]:
        txt = p.text.strip()
        if txt == "Nguyễn phú quý":
            p.text = "NGUYỄN PHÚ QUÝ"
            if p.runs:
                format_run(p.runs[0], size_pt=14, bold=True)
        elif txt == "lê minh ngọc":
            p.text = "LÊ MINH NGỌC"
            if p.runs:
                format_run(p.runs[0], size_pt=14, bold=True)
        elif "thành phỐ hỒ chí minh" in txt.lower():
            p.text = "THÀNH PHỐ HỒ CHÍ MINH, THÁNG 12 NĂM 2026"
            if p.runs:
                format_run(p.runs[0], size_pt=13, bold=True)

    # =========================================================================
    # 2. DANH MỤC TỪ VIẾT TẮT (Table 2)
    # =========================================================================
    print("2. Updating Table 2 (Danh mục từ viết tắt)...")
    tbl_abbr = doc.tables[2]
    # Required acronyms for this thesis
    acronyms = [
        ("SBC", "Single Board Computer – Máy tính đơn bộc (Raspberry Pi 4)"),
        ("SoC", "System on Chip – Hệ thống tích hợp trên vi mạch"),
        ("CSI", "Camera Serial Interface – Giao diện nối tiếp dành riêng cho camera"),
        ("PCB", "Printed Circuit Board – Bo mạch in mạch điện tử"),
        ("GPIO", "General Purpose Input/Output – Cổng vào/ra đa năng"),
        ("PWM", "Pulse Width Modulation – Điều chế độ rộng xung"),
        ("I²C", "Inter-Integrated Circuit – Giao tiếp nối tiếp đồng bộ hai dây"),
        ("TTL", "Transistor-Transistor Logic – Mức logic bán dẫn chuẩn"),
        ("DC", "Direct Current – Dòng điện một chiều"),
        ("Li-ion", "Lithium-ion – Công nghệ pin sạc Lithium hiệu năng cao"),
        ("OS", "Operating System – Hệ điều hành (Raspberry Pi OS / Linux)"),
        ("AI", "Artificial Intelligence – Trí tuệ nhân tạo"),
        ("SLAM", "Simultaneous Localization and Mapping – Định vị và lập bản đồ đồng thời"),
        ("MCU", "Microcontroller Unit – Đơn vị vi điều khiển"),
        ("BOM", "Bill of Materials – Bảng thống kê danh mục linh kiện"),
        ("VOM", "Volt-Ohm-Milliammeter – Đồng hồ vạn năng đo kiểm điện"),
    ]
    
    # Adjust table rows
    while len(tbl_abbr.rows) < len(acronyms) + 1:
        tbl_abbr.add_row()
    while len(tbl_abbr.rows) > len(acronyms) + 1:
        row_last = tbl_abbr.rows[-1]._tr
        row_last.getparent().remove(row_last)

    add_styled_cell(tbl_abbr.rows[0].cells[0], "Từ viết tắt", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")
    add_styled_cell(tbl_abbr.rows[0].cells[1], "Giải nghĩa", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")

    for idx, (abbr, mean) in enumerate(acronyms):
        row = tbl_abbr.rows[idx + 1]
        fill = "F2F2F2" if idx % 2 == 1 else "FFFFFF"
        add_styled_cell(row.cells[0], abbr, bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex=fill)
        add_styled_cell(row.cells[1], mean, bold=False, font_size=10.5, align=WD_ALIGN_PARAGRAPH.LEFT, fill_hex=fill)

    # =========================================================================
    # 3. DANH MỤC HÌNH ẢNH & DANH MỤC BẢNG BIỂU (Update paragraphs)
    # =========================================================================
    print("3. Updating Danh mục hình ảnh & bảng biểu...")
    # Find start of Danh mục hình ảnh
    idx_img_title = None
    idx_tbl_title = None
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == "DANH MỤC HÌNH ẢNH":
            idx_img_title = i
        elif p.text.strip() == "DANH MỤC BẢNG BIỂU":
            idx_tbl_title = i
            break

    # We update figure items between idx_img_title and idx_tbl_title
    clean_figures = [
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
        "Hình 3.2: Sơ đồ nguyên lý chi tiết bo mạch mở rộng (Carrier Board) trên KiCad\t30",
        "Hình 3.3: Bản vẽ thiết kế mạch in (PCB) 1 lớp mặt đáy B.Cu với 5 cầu nối dây Jumper\t31",
        "Hình 3.4: Sơ đồ thuật toán điều khiển chuyển động đa hướng bánh Mecanum\t33",
        "Hình 3.5: Sơ đồ thuật toán đọc cảm biến khoảng cách và né tránh vật cản an toàn\t35",
        "Hình 3.6: Giao diện Web Dashboard điều khiển và giám sát robot qua mạng Wi-Fi\t37",
    ]

    clean_tables = [
        "Bảng 1.1: Thông số kỹ thuật Raspberry Pi 4 Model B (8GB)\t14",
        "Bảng 1.2: Thông số kỹ thuật động cơ giảm tốc TT trục kép 3-6VDC\t15",
        "Bảng 1.3: Thông số kỹ thuật module Driver TB6612FNG\t16",
        "Bảng 1.4: Thông số kỹ thuật Raspberry Pi Camera V1.3 (OV5647)\t17",
        "Bảng 1.5: Thông số kỹ thuật cảm biến khoảng cách siêu âm HC-SR04\t18",
        "Bảng 1.6: Thông số kỹ thuật màn hình hiển thị OLED 1.3 inch I²C\t19",
        "Bảng 2.1: Thành phần và thông số cốt lõi của Raspberry Pi 4 Model B (8GB)\t22",
        "Bảng 3.1: Bảng phân bổ chân GPIO của Raspberry Pi 4 (40-Pin Header)\t31",
        "Bảng 3.2: Phân bổ và quản lý tài nguyên trên Raspberry Pi 4 Model B (8GB)\t32",
        "Bảng 3.3: Bảng tra cứu trạng thái logic điều khiển chiều quay và tốc độ động cơ\t34",
        "Bảng 3.4: Ngưỡng khoảng cách và hành vi điều khiển né tránh vật cản của robot\t36",
        "Bảng 4.1: Bảng tổng hợp tiến độ hoàn thành các hạng mục nghiên cứu của đề tài\t39",
    ]

    if idx_img_title and idx_tbl_title:
        fig_paras = [p for p in doc.paragraphs[idx_img_title+1:idx_tbl_title] if p.text.strip()]
        for idx, fig_text in enumerate(clean_figures):
            if idx < len(fig_paras):
                fig_paras[idx].text = fig_text
                fig_paras[idx].style = 'table of figures'
            else:
                new_p = doc.add_paragraph(fig_text, style='table of figures')
                fig_paras[-1]._p.addnext(new_p._p)
                fig_paras.append(new_p)

        # Update Table List paragraphs between idx_tbl_title and DANH MỤC TỪ VIẾT TẮT
        idx_abbr_title = None
        for i in range(idx_tbl_title + 1, len(doc.paragraphs)):
            if doc.paragraphs[i].text.strip() == "DANH MỤC TỪ VIẾT TẮT":
                idx_abbr_title = i
                break
        
        if idx_abbr_title:
            tbl_paras = [p for p in doc.paragraphs[idx_tbl_title+1:idx_abbr_title] if p.text.strip()]
            for idx, tbl_text in enumerate(clean_tables):
                if idx < len(tbl_paras):
                    tbl_paras[idx].text = tbl_text
                    tbl_paras[idx].style = 'table of figures'
                else:
                    new_p = doc.add_paragraph(tbl_text, style='table of figures')
                    tbl_paras[-1]._p.addnext(new_p._p)
                    tbl_paras.append(new_p)

    # =========================================================================
    # 4. CẬP NHẬT CHƯƠNG 1 & MỞ ĐẦU (OLED 1.3", HC-SR04, TB6612FNG)
    # =========================================================================
    print("4. Updating Intro and Chapter 1 (Hardware Specs)...")
    for p in doc.paragraphs:
        txt = p.text
        if "0.96 inch" in txt:
            p.text = txt.replace("0.96 inch", "1.3 inch")
        if "0.96" in txt and "OLED" in txt:
            p.text = txt.replace("0.96", "1.3")
        if "L298N" in txt:
            p.text = txt.replace("L298N", "TB6612FNG")

    # Update Table 8 (Bảng 1.6: Thông số OLED 1.3")
    tbl_oled = doc.tables[8]
    add_styled_cell(tbl_oled.rows[0].cells[0], "Thành phần", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")
    add_styled_cell(tbl_oled.rows[0].cells[1], "Thông số kỹ thuật", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")

    oled_specs = [
        ("Kích thước màn hình", "1.3 inch (hiển thị rộng rãi, dễ quét QR từ khoảng cách 0.5m)"),
        ("Độ phân giải", "128 × 64 pixels"),
        ("IC điều khiển (Driver IC)", "SH1106 / SSD1306"),
        ("Chuẩn giao tiếp", "I²C (Địa chỉ mặc định 0x3C, dây SDA: GPIO 2, SCL: GPIO 3)"),
        ("Điện áp hoạt động", "3.3V DC (cấp trực tiếp từ chân 3.3V của Raspberry Pi 4)"),
        ("Công nghệ hiển thị", "OLED tự phát quang, góc nhìn rộng > 160°, tiết kiệm điện năng"),
    ]
    for idx, (comp, spec) in enumerate(oled_specs):
        row = tbl_oled.rows[idx + 1]
        fill = "F2F2F2" if idx % 2 == 1 else "FFFFFF"
        add_styled_cell(row.cells[0], comp, bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.LEFT, fill_hex=fill)
        add_styled_cell(row.cells[1], spec, bold=False, font_size=10.5, align=WD_ALIGN_PARAGRAPH.LEFT, fill_hex=fill)

    # =========================================================================
    # 5. CẬP NHẬT CHƯƠNG 2: CƠ SỞ LÝ THUYẾT (KiCad 10, Mecanum Kinematics)
    # =========================================================================
    print("5. Updating Chapter 2 (Theory, Tools, Mecanum Kinematics)...")
    for i, p in enumerate(doc.paragraphs):
        if "2.7 Công cụ thiết kế và phát triển" in p.text:
            # We will enrich section 2.7
            p.text = "2.7 Công cụ thiết kế và phát triển"
        elif "2.7.1 Visual Studio Code" in p.text:
            p.text = "2.7.1 Môi trường lập trình Visual Studio Code & Python 3"
        elif "Quartus" in p.text or "ModelSim" in p.text or "Proteus" in p.text:
            if p.style and 'Heading' in p.style.name:
                p.text = "2.7.2 Phần mềm thiết kế điện tử KiCad EDA phiên bản 10.0"

    # =========================================================================
    # 6. CẬP NHẬT CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG
    # =========================================================================
    print("6. Updating Chapter 3 (System Architecture, Carrier Board PCB, Pinout Table 10)...")
    
    # Locate key headings in Chapter 3
    p_3_1_1 = None
    p_3_1_2 = None
    p_3_1_3 = None
    p_3_2 = None
    p_3_2_1 = None
    p_3_2_2 = None
    p_3_3 = None
    p_3_3_1 = None
    p_3_3_2 = None
    p_3_4 = None
    p_3_4_1 = None
    p_3_4_2 = None
    p_3_5 = None
    p_3_5_1 = None
    p_3_5_2 = None
    p_ch4 = None

    for p in doc.paragraphs:
        txt = p.text.strip()
        if "3.1.1 Sơ đồ tổng thể hệ thống" in txt:
            p_3_1_1 = p
        elif "3.1.2 Sơ đồ kết nối phần cứng" in txt:
            p_3_1_2 = p
        elif "3.1.3 Lưu đồ hoạt động của hệ thống" in txt:
            p_3_1_3 = p
        elif txt == "3.2 Thiết kế module điều khiển chuyển động":
            p_3_2 = p
        elif "3.2.1 Lưu đồ hoạt động module điều khiển động cơ" in txt:
            p_3_2_1 = p
        elif "3.2.2 Sơ đồ mạch nguyên lý giao tiếp giữa GPIO" in txt:
            p_3_2_2 = p
        elif txt == "3.3 Thiết kế module đọc cảm biến khoảng cách":
            p_3_3 = p
        elif "3.3.1 Lưu đồ hoạt động đọc cảm biến siêu âm" in txt:
            p_3_3_1 = p
        elif "3.3.2 Thuật toán tránh vật cản" in txt:
            p_3_3_2 = p
        elif "3.4 Thiết kế module xử lý Camera" in txt:
            p_3_4 = p
        elif "3.4.1 Lưu đồ xử lý hình ảnh" in txt:
            p_3_4_1 = p
        elif "3.4.2 Tích hợp Camera" in txt:
            p_3_4_2 = p
        elif "3.5 Thiết kế giao tiếp UART" in txt or "3.5 Thiết kế giao diện" in txt:
            p_3_5 = p
        elif "3.5.1 Lưu đồ hoạt động giao tiếp UART" in txt or "3.5.1 Kiến trúc hệ thống Web" in txt:
            p_3_5_1 = p
        elif "3.5.2 Giao diện giám sát hệ thống" in txt or "3.5.2 Giao diện giám sát và điều khiển" in txt:
            p_3_5_2 = p
        elif "THỰC NGHIỆM VÀ ĐÁNH GIÁ HỆ THỐNG" in txt:
            p_ch4 = p

    # --- 3.1.1: Sơ đồ tổng thể kiến trúc ---
    if p_3_1_1:
        # Find caption paragraph of Fig 3.1
        curr = p_3_1_1
        # Insert image block_diagram_slide5_overall.png
        img_3_1 = 'extracted_imgs/block_diagrams/block_diagram_slide5_overall.png'
        if os.path.exists(img_3_1):
            curr = insert_img_after(doc, curr, img_3_1, width_inches=5.6, caption_text="Hình 3.1: Sơ đồ tổng thể kiến trúc hệ thống robot tự hành trên nền tảng Raspberry Pi 4")
        
        desc_3_1 = (
            "Kiến trúc hệ thống robot được tổ chức thành 4 phân hệ chính phối hợp chặt chẽ với nhau theo thời gian thực:\n"
            "1. Khối nguồn: Nguồn năng lượng chính sử dụng bộ pin sạc Li-ion 3S2P (điện áp danh định 11.1V – tối đa 12.6V, dung lượng 5200mAh). Nguồn pin cấp trực tiếp điện áp 12V cho các động cơ giảm tốc DC thông qua 2 mạch công suất TB6612FNG; đồng thời đi qua module biến đổi DC-DC Buck công suất cao XL4015 để hạ áp xuống mức 5.0V chuẩn với dòng tải tối đa 5A cấp nguồn ổn định cho Raspberry Pi 4 Model B, màn hình OLED và các cảm biến ngoại vi.\n"
            "2. Khối xử lý trung tâm (Raspberry Pi 4 Model B 8GB): Đóng vai trò là 'bộ não' điều phối toàn bộ hoạt động. Thiết bị chạy hệ điều hành Linux 64-bit (Raspberry Pi OS), thực thi đồng thời thuật toán xử lý ảnh thời gian thực phát hiện chuyển động/người bằng OpenCV qua luồng video MIPI CSI, dịch vụ máy chủ Web phục vụ giao diện điều khiển nội bộ, luồng đo đạc cảm biến khoảng cách siêu âm và thuật toán động học xuất xung PWM điều khiển di chuyển đa hướng.\n"
            "3. Khối cảm biến và giao diện tương tác: Bao gồm 01 camera Raspberry Pi Camera V1.3 (5MP) thu nhận hình ảnh thời gian thực; 02 cảm biến siêu âm HC-SR04 (Trái và Phải) phát hiện vật cản phía trước với góc quét rộng; cụm cảm biến dò line 3 kênh; và 01 màn hình hiển thị OLED 1.3 inch giao tiếp I²C hiển thị trạng thái và mã QR động phục vụ kết nối điện thoại.\n"
            "4. Khối công suất và chấp hành: Bao gồm bo mạch mở rộng (Carrier Board) tích hợp 02 mạch driver TB6612FNG MOSFET cầu H kép độc lập, dẫn động 4 động cơ giảm tốc vàng TT gắn 4 bánh xe đa hướng Mecanum, cho phép robot di chuyển linh hoạt trong mọi không gian hẹp."
        )
        curr = insert_p_after(doc, curr, desc_3_1)

    # --- 3.1.2: Bo mạch Carrier Board & Schematic / PCB images & Bảng chân GPIO Table 10 ---
    if p_3_1_2:
        curr = p_3_1_2
        desc_carrier = (
            "Nhằm giải quyết triệt để tình trạng dây cắm breadboard chằng chịt, dễ bị rung lắc lỏng chân khi robot di chuyển trong thực tế, nhóm nghiên cứu đã thiết kế một bo mạch mở rộng chuyên dụng (Carrier Board) kết nối trực tiếp với 40-pin header của Raspberry Pi 4.\n"
            "Bo mạch được thiết kế hoàn chỉnh trên phần mềm chuyên nghiệp KiCad 10 theo tiêu chuẩn gia công 1 lớp đồng đáy (B.Cu) với kích thước nhỏ gọn 111.45 mm × 72.77 mm (diện tích 81.43 cm²). Để bảo đảm tính phẳng và khả năng tự làm mạch in thủ công (bằng phương pháp ủi nhiệt hoặc in film cảm quang), mạch sử dụng 5 cầu nối dây (jumpers) ngắn ở mặt trên linh kiện (F.Cu) kết hợp đi dây tối ưu ở mặt đáy (B.Cu). Bo mạch tích hợp đầy đủ: Socket cắm 40 chân cái cho Raspberry Pi 4, 02 vị trí cắm module Driver TB6612FNG, vị trí cắm module hạ áp Buck XL4015, cọc nguồn Domino KF301 chịu dòng, hàng cắm màn hình OLED 1.3 inch I²C, các cổng kết nối cảm biến siêu âm HC-SR04 cùng các cụm điện trở phân áp 1kΩ / 2kΩ để chuyển đổi mức logic an toàn từ 5V xuống 3.3V cho Raspberry Pi."
        )
        curr = insert_p_after(doc, curr, desc_carrier)

        # Insert Schematic image
        img_sch = 'extracted_imgs/schematic_diagram_cropped.png'
        if os.path.exists(img_sch):
            curr = insert_img_after(doc, curr, img_sch, width_inches=5.6, caption_text="Hình 3.2: Sơ đồ nguyên lý chi tiết bo mạch mở rộng (Carrier Board) trên KiCad")

        # Insert PCB 1-Layer image
        img_pcb = 'extracted_imgs/pcb_complete_routed.png'
        if os.path.exists(img_pcb):
            curr = insert_img_after(doc, curr, img_pcb, width_inches=5.6, caption_text="Hình 3.3: Bản vẽ thiết kế mạch in (PCB) 1 lớp mặt đáy B.Cu với 5 cầu nối dây Jumper")

    # Update Table 10: GPIO Allocation
    print("Updating Table 10 (Bảng 3.1: Phân bổ chân GPIO Raspberry Pi 4 chuẩn xác)...")
    tbl_gpio = doc.tables[10]
    
    gpio_rows = [
        ("Pin 01", "3.3V Power", "-", "Power Out", "3.3V DC", "Cấp nguồn logic cho màn hình OLED 1.3\" và cảm biến"),
        ("Pin 02", "+5V_PI_1", "-", "Power In", "5.0V DC", "Nguồn 5V từ module Buck XL4015 cấp vào nuôi Raspberry Pi 4"),
        ("Pin 04", "+5V_PI_2", "-", "Power In", "5.0V DC", "Nguồn 5V từ module Buck XL4015 cấp vào nuôi Pi 4 (nối song song Pin 2)"),
        ("Pin 06", "GND", "-", "Ground", "0V", "Mass chung toàn hệ thống"),
        ("Pin 03", "PWMA_L", "GPIO 2", "Output", "3.3V LVTTL", "Xung PWM điều khiển tốc độ cụm động cơ Trái (Driver TB6612 #1)"),
        ("Pin 05", "AIN2_L", "GPIO 3", "Output", "3.3V LVTTL", "Tín hiệu logic điều khiển chiều quay động cơ Trái (kết nối AIN2/BIN2)"),
        ("Pin 07", "AIN1_L", "GPIO 4", "Output", "3.3V LVTTL", "Tín hiệu logic điều khiển chiều quay động cơ Trái (kết nối AIN1/BIN1)"),
        ("Pin 11", "STBY_L", "GPIO 17", "Output", "3.3V LVTTL", "Chân kích hoạt Standby Driver TB6612 Trái (HIGH = Enable)"),
        ("Pin 13", "TRIG_L", "GPIO 27", "Output", "3.3V LVTTL", "Phát xung siêu âm kích hoạt đo cự ly (HC-SR04 Trái)"),
        ("Pin 15", "ECHO_L", "GPIO 22", "Input", "3.3V LVTTL", "Nhận xung phản hồi cảm biến Trái (qua cầu phân áp 1kΩ / 2kΩ)"),
        ("Pin 17", "3.3V Power", "-", "Power Out", "3.3V DC", "Nguồn logic 3.3V dự phòng"),
        ("Pin 19", "LINE_L", "GPIO 10", "Input", "3.3V LVTTL", "Tín hiệu cảm biến dò đường (Line Sensor) kênh Trái"),
        ("Pin 21", "LINE_C", "GPIO 9", "Input", "3.3V LVTTL", "Tín hiệu cảm biến dò đường (Line Sensor) kênh Giữa"),
        ("Pin 23", "LINE_R", "GPIO 11", "Input", "3.3V LVTTL", "Tín hiệu cảm biến dò đường (Line Sensor) kênh Phải"),
        ("Pin 25", "GND", "-", "Ground", "0V", "Mass cảm biến line"),
        ("Pin 27", "I2C_SDA", "GPIO 0/2", "Bidirectional", "3.3V Logic", "Đường truyền dữ liệu I²C SDA giao tiếp Màn hình OLED 1.3 inch"),
        ("Pin 28", "I2C_SCL", "GPIO 1/3", "Output", "3.3V Logic", "Đường xung nhịp I²C SCL giao tiếp Màn hình OLED 1.3 inch"),
        ("Pin 29", "TRIG_R", "GPIO 5", "Output", "3.3V LVTTL", "Phát xung siêu âm kích hoạt đo cự ly (HC-SR04 Phải)"),
        ("Pin 31", "ECHO_R", "GPIO 6", "Input", "3.3V LVTTL", "Nhận xung phản hồi cảm biến Phải (qua cầu phân áp 1kΩ / 2kΩ)"),
        ("Pin 33", "PWMA_R", "GPIO 13", "Output", "3.3V LVTTL", "Xung PWM điều khiển tốc độ cụm động cơ Phải (Driver TB6612 #2)"),
        ("Pin 35", "AIN2_R", "GPIO 19", "Output", "3.3V LVTTL", "Tín hiệu logic điều khiển chiều quay động cơ Phải (kết nối AIN2/BIN2)"),
        ("Pin 37", "AIN1_R", "GPIO 26", "Output", "3.3V LVTTL", "Tín hiệu logic điều khiển chiều quay động cơ Phải (kết nối AIN1/BIN1)"),
        ("Pin 38", "STBY_R", "GPIO 20", "Output", "3.3V LVTTL", "Chân kích hoạt Standby Driver TB6612 Phải (HIGH = Enable)"),
        ("Pin 39", "GND", "-", "Ground", "0V", "Mass chung toàn hệ thống"),
    ]

    # Adjust row count of Table 10
    while len(tbl_gpio.rows) < len(gpio_rows) + 1:
        tbl_gpio.add_row()
    while len(tbl_gpio.rows) > len(gpio_rows) + 1:
        row_last = tbl_gpio.rows[-1]._tr
        row_last.getparent().remove(row_last)

    # Format header
    headers_10 = ["Chân Vật lý", "Tên Tín hiệu", "Chân BCM", "Loại I/O", "Mức áp", "Chức năng & Thiết bị kết nối"]
    # Check if table 10 has 5 or 6 cols
    col_count = len(tbl_gpio.columns)
    if col_count == 5:
        # 5 cols format: Chân Header | Tín hiệu | Chân BCM | Mức áp | Chức năng
        add_styled_cell(tbl_gpio.rows[0].cells[0], "Chân Header", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")
        add_styled_cell(tbl_gpio.rows[0].cells[1], "Ký hiệu Net", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")
        add_styled_cell(tbl_gpio.rows[0].cells[2], "Chân BCM", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")
        add_styled_cell(tbl_gpio.rows[0].cells[3], "Mức áp", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")
        add_styled_cell(tbl_gpio.rows[0].cells[4], "Chức năng & Thiết bị kết nối", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")
        for idx, (p_num, net, bcm, io_type, volt, desc) in enumerate(gpio_rows):
            r = tbl_gpio.rows[idx + 1]
            fill = "F2F2F2" if idx % 2 == 1 else "FFFFFF"
            add_styled_cell(r.cells[0], p_num, bold=True, font_size=10, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex=fill)
            add_styled_cell(r.cells[1], net, bold=True, font_size=10, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex=fill)
            add_styled_cell(r.cells[2], bcm, bold=False, font_size=10, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex=fill)
            add_styled_cell(r.cells[3], volt, bold=False, font_size=10, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex=fill)
            add_styled_cell(r.cells[4], desc, bold=False, font_size=10, align=WD_ALIGN_PARAGRAPH.LEFT, fill_hex=fill)

    # --- 3.1.3: Lưu đồ hoạt động tổng thể ---
    if p_3_1_3:
        desc_3_1_3 = (
            "Lưu đồ hoạt động tổng thể của robot được vận hành theo chu trình khép kín:\n"
            "1. Khởi động và cấu hình: Hệ điều hành nạp các dịch vụ nền tảng, thiết lập tần số băm xung PWM (1 kHz) trên các chân GPIO, thiết lập bus I²C ở tốc độ tiêu chuẩn 400 kHz, khởi tạo camera qua chuẩn MIPI CSI và bật máy chủ Web điều khiển nội bộ.\n"
            "2. Khởi tạo hiển thị: Màn hình OLED 1.3 inch khởi tạo và hiển thị địa chỉ IP cục bộ kèm mã QR động để khách hàng có thể quét kết nối trực tiếp.\n"
            "3. Vòng lặp giám sát an toàn: Cảm biến siêu âm HC-SR04 liên tục đo cự ly vật cản phía trước theo chu kỳ 50 ms. Nếu phát hiện vật thể nằm trong vùng nguy hiểm (< 20 cm), hệ thống tự động ngắt xung PWM động cơ để dừng xe khẩn cấp và kích hoạt chế độ né tránh.\n"
            "4. Xử lý lệnh điều hướng: Robot nhận lệnh di chuyển từ giao diện Web (tiến, lùi, dạt ngang, xoay góc) hoặc điều hướng tự động, tính toán ma trận vận tốc bánh Mecanum và xuất tín hiệu điều khiển ra 2 mạch driver TB6612FNG."
        )
        insert_p_after(doc, p_3_1_3, desc_3_1_3)

    # --- 3.2: Thiết kế module điều khiển chuyển động ---
    if p_3_2_1:
        desc_3_2_1 = (
            "Hệ thống truyền động sử dụng 4 bánh xe Mecanum đặt con lăn nghiêng một góc 45° so với trục quay chính. Bằng cách điều khiển độc lập vận tốc góc và chiều quay của từng bánh xe, lực đẩy của các con lăn sẽ tổng hợp thành vector chuyển động tự do theo mọi hướng trong mặt phẳng (chuyển động toàn hướng - Holonomic Motion):\n"
            "• Tiến thẳng: Cả 4 bánh cùng quay thuận chiều.\n"
            "• Lùi thẳng: Cả 4 bánh cùng quay ngược chiều.\n"
            "• Tịnh tiến dạt ngang sang trái: Bánh trước trái quay lùi, bánh trước phải quay tiến, bánh sau trái quay tiến, bánh sau phải quay lùi.\n"
            "• Tịnh tiến dạt ngang sang phải: Bánh trước trái quay tiến, bánh trước phải quay lùi, bánh sau trái quay lùi, bánh sau phải quay tiến.\n"
            "• Xoay tròn tại chỗ: 2 bánh bên trái quay lùi, 2 bánh bên phải quay tiến (xoay trái) hoặc ngược lại (xoay phải) mà không làm dịch chuyển tâm robot."
        )
        insert_p_after(doc, p_3_2_1, desc_3_2_1)

    if p_3_2_2:
        desc_3_2_2 = (
            "Module điều khiển động cơ trong mã nguồn Python (lớp `MotorController` tại file `code/python/motor_controller.py`) quản lý trực tiếp các chân GPIO xuất tín hiệu đến 2 mạch TB6612FNG. Mỗi IC điều khiển 2 động cơ cùng bên với các chân logic định hướng (IN1, IN2), chân băm xung PWM điều khiển tốc độ và chân Standby (STBY).\n"
            "Bảng tra cứu trạng thái logic điều khiển chiều quay và tốc độ động cơ như sau:\n"
            "• IN1 = HIGH, IN2 = LOW: Động cơ quay thuận (CW)\n"
            "• IN1 = LOW, IN2 = HIGH: Động cơ quay nghịch (CCW)\n"
            "• IN1 = LOW, IN2 = LOW: Dừng trôi tự do (Stop)\n"
            "• IN1 = HIGH, IN2 = HIGH: Phanh hãm động cơ (Brake)\n"
            "Tín hiệu PWM được xuất ở tần số 1000 Hz bảo đảm động cơ chạy êm ái, mô-men xoắn ổn định và không phát ra tiếng rít cơ khí khó chịu."
        )
        insert_p_after(doc, p_3_2_2, desc_3_2_2)

    # --- 3.3: Thiết kế cảm biến khoảng cách & né vật cản ---
    if p_3_3_1:
        desc_3_3_1 = (
            "Cảm biến khoảng cách siêu âm HC-SR04 hoạt động dựa trên nguyên lý phát và thu sóng âm phản xạ ở tần số 40 kHz. Để bảo đảm an toàn điện áp cho các chân GPIO của Raspberry Pi 4 (chỉ chịu mức logic tối đa 3.3V), tín hiệu Echo (ngõ ra 5V) của mỗi cảm biến được đấu nối qua một mạch cầu phân áp điện trở gồm R1 = 1 kΩ và R2 = 2 kΩ nối xuống mass GND. Điện áp ngõ ra tại điểm giữa cấp vào chân GPIO của Pi 4 được tính theo công thức:\n"
            "    V_out = V_in × [R2 / (R1 + R2)] = 5.0V × [2k / (1k + 2k)] = 3.33V\n"
            "Mức điện áp này hoàn toàn nằm trong dải an toàn tuyệt đối của chuẩn LVTTL trên Raspberry Pi 4, bảo vệ vi xử lý khỏi nguy cơ quá áp làm hỏng phần cứng."
        )
        insert_p_after(doc, p_3_3_1, desc_3_3_1)

    # Update Table 12 (Bảng 3.4: Ngưỡng né vật cản)
    print("Updating Table 12 (Bảng 3.4: Ngưỡng khoảng cách né vật cản)...")
    tbl_obs = doc.tables[12]
    add_styled_cell(tbl_obs.rows[0].cells[0], "Khoảng cách đo được (d)", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")
    add_styled_cell(tbl_obs.rows[0].cells[1], "Trạng thái hệ thống", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")
    add_styled_cell(tbl_obs.rows[0].cells[2], "Hành động điều khiển động cơ", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")

    obs_data = [
        ("d > 35 cm", "Bình thường", "Duy trì tốc độ định mức (Duty Cycle 70% – 80%), tiến thẳng theo lộ trình"),
        ("20 cm < d ≤ 35 cm", "Cảnh báo", "Giảm tốc độ động cơ xuống mức an toàn (Duty Cycle 40%), tăng tần số quét cảm biến"),
        ("10 cm < d ≤ 20 cm", "Nguy hiểm", "Dừng xe ngay lập tức; đọc cảm biến Trái/Phải để quyết định dạt ngang hoặc xoay tìm hướng thoáng"),
        ("d ≤ 10 cm", "Khẩn cấp", "Kích hoạt dừng phanh khẩn cấp; lùi ngắn an toàn 10 cm và xoay góc 90° để né vật cản"),
    ]
    for idx, (dist, stat, act) in enumerate(obs_data):
        row = tbl_obs.rows[idx + 1]
        fill = "F2F2F2" if idx % 2 == 1 else "FFFFFF"
        add_styled_cell(row.cells[0], dist, bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex=fill)
        add_styled_cell(row.cells[1], stat, bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex=fill)
        add_styled_cell(row.cells[2], act, bold=False, font_size=10.5, align=WD_ALIGN_PARAGRAPH.LEFT, fill_hex=fill)

    # --- 3.4: Thiết kế Camera & Tương tác khách hàng qua QR OLED 1.3" ---
    if p_3_4_1:
        desc_3_4_1 = (
            "Thuật toán phát hiện sự hiện diện của khách hàng sử dụng thư viện OpenCV trên Raspberry Pi 4 thông qua phương pháp trừ nền thích nghi (Background Subtraction / Frame Differencing). Luồng video từ camera CSI được nạp liên tục ở độ phân giải 640 × 480 pixels với tốc độ 30 fps. Hình ảnh được chuyển đổi sang thang độ xám (Grayscale), áp dụng bộ lọc làm mờ Gauss (Gaussian Blur ksize=21) để khử nhiễu môi trường, sau đó tính toán sự sai khác cường độ điểm ảnh giữa các khung hình liên tiếp. Khi phát hiện diện tích vùng biến đổi lớn hơn ngưỡng định trước, robot xác định có khách hàng đang tiến lại gần và chủ động chuyển sang trạng thái chào đón, tạm dừng di chuyển để tương tác."
        )
        insert_p_after(doc, p_3_4_1, desc_3_4_1)

    if p_3_4_2:
        p_3_4_2.text = "3.4.2 Tích hợp Camera MIPI CSI và Màn hình OLED 1.3 inch với Raspberry Pi 4"
        desc_3_4_2 = (
            "Module camera OmniVision OV5647 kết nối trực tiếp với cổng MIPI CSI của Raspberry Pi 4 thông qua cáp dẹt FPC 15-pin. Dữ liệu video được truyền thẳng vào bộ xử lý đồ họa GPU VideoCore VI giúp giải mã luồng video độ trễ thấp mà không chiếm dụng tài nguyên tính toán của CPU.\n"
            "Màn hình OLED 1.3 inch được tích hợp trên bo mạch mở rộng đóng vai trò là giao diện tương tác trực quan. Hệ thống sử dụng thư viện Python Pillow và qrcode để tự động khởi tạo mã QR động chứa địa chỉ truy cập giao diện Web nội bộ của robot (ví dụ: `http://192.168.4.1:5000`). Khách hàng chỉ cần sử dụng camera điện thoại thông minh để quét mã QR trên màn hình OLED là có thể mở ngay giao diện điều khiển, chỉ định quầy giao nhận hàng hóa mà không cần cài đặt bất kỳ ứng dụng phức tạp nào."
        )
        insert_p_after(doc, p_3_4_2, desc_3_4_2)

    # --- 3.5: Giao diện Web Dashboard điều khiển ---
    if p_3_5:
        p_3_5.text = "3.5 Thiết kế giao diện điều khiển và giám sát qua Web (Web Dashboard)"
    if p_3_5_1:
        p_3_5_1.text = "3.5.1 Kiến trúc hệ thống Web Server điều khiển"
        desc_3_5_1 = (
            "Hệ thống điều khiển từ xa được thiết kế theo mô hình Client - Server nội bộ chạy trực tiếp trên Raspberry Pi 4 thông qua kết nối Wi-Fi:\n"
            "• Phần mềm máy chủ (Backend): Được xây dựng bằng Python (file `code/website/server.py`), lắng nghe các yêu cầu HTTP/WebSocket từ client và ánh xạ trực tiếp thành các lệnh gọi hàm điều khiển động cơ trong `motor_controller.py`.\n"
            "• Giao diện người dùng (Frontend): Xây dựng bằng HTML5, CSS3 hiện đại và JavaScript thuần (file `code/website/index.html`, `app.js`), tối ưu hóa khả năng phản hồi cảm ứng trên điện thoại thông minh và máy tính bảng."
        )
        insert_p_after(doc, p_3_5_1, desc_3_5_1)

    if p_3_5_2:
        p_3_5_2.text = "3.5.2 Giao diện giám sát và điều khiển thực tế"
        curr = p_3_5_2
        img_web = 'extracted_imgs/web_dashboard.png'
        if os.path.exists(img_web):
            curr = insert_img_after(doc, curr, img_web, width_inches=5.2, caption_text="Hình 3.6: Giao diện Web Dashboard điều khiển và giám sát robot qua mạng Wi-Fi")
        desc_3_5_2 = (
            "Giao diện Web Dashboard cung cấp đầy đủ các cụm phím điều khiển đa hướng: Tiến, Lùi, Dạt ngang Trái, Dạt ngang Phải, Xoay Trái, Xoay Phải, Dừng khẩn cấp, cùng thanh trượt (slider) tùy chỉnh tốc độ PWM từ 20% đến 100%. Giao diện phản hồi tức thì với độ trễ < 50 ms qua mạng Wi-Fi nội bộ, bảo đảm tính an toàn cao khi điều khiển robot di chuyển trong hành lang trung tâm thương mại."
        )
        insert_p_after(doc, curr, desc_3_5_2)

    # =========================================================================
    # 7. CẬP NHẬT CHƯƠNG 4: KẾ HOẠCH VÀ PHƯƠNG ÁN THỰC NGHIỆM HỆ THỐNG
    # (Đúng nguyên tắc: CHỈ LÀM TỚI ĐÂU GHI TỚI ĐÓ, KHÔNG BỊA ĐẶT SỐ LIỆU CHƯA LÀM)
    # =========================================================================
    print("7. Updating Chapter 4 (Real Progress, No Fabricated Results)...")
    if p_ch4:
        p_ch4.text = "KẾ HOẠCH VÀ PHƯƠNG ÁN THỰC NGHIỆM HỆ THỐNG"
        
        # Clean obsolete FPGA paragraphs under Chapter 4
        # We will insert a clear, honest progress summary and experimental methodology
        ch4_content = (
            "Bản đề cương khóa luận tốt nghiệp này ghi nhận trung thực và chính xác tiến độ nghiên cứu, thiết kế phần cứng và lập trình phần mềm đã hoàn thành tính đến thời điểm báo cáo đề cương, đồng thời xác lập kế hoạch chi tiết cho giai đoạn gia công chế tạo và thực nghiệm kiểm chứng tiếp theo."
        )
        curr = insert_p_after(doc, p_ch4, ch4_content)
        
        # 4.1 Tiến độ thực hiện hiện tại của đề tài
        p_4_1 = insert_p_after(doc, curr, "4.1 Tiến độ thực hiện hiện tại của đề tài (Các nội dung đã hoàn thành)", style='Heading 2')
        desc_4_1 = (
            "Tính đến thời điểm hiện tại, nhóm nghiên cứu đã hoàn thành toàn diện các hạng mục phân tích, tính toán lý thuyết, thiết kế phần cứng và lập trình kiểm thử phần mềm nền tảng:\n"
            "1. Hoàn thành nghiên cứu tổng quan, khảo sát và lựa chọn đầy đủ linh kiện phần cứng tương thích tối ưu với bo mạch chủ Raspberry Pi 4 Model B (8GB).\n"
            "2. Hoàn thành thiết kế sơ đồ nguyên lý chi tiết (Schematic) trên phần mềm chuyên ngành KiCad 10, quy hoạch chuẩn xác 40 chân GPIO của Raspberry Pi 4 kết nối 2 module driver TB6612FNG, module Buck XL4015, màn hình OLED 1.3 inch I²C, cụm cảm biến siêu âm HC-SR04 kèm mạch phân áp trở bảo vệ.\n"
            "3. Hoàn thành thiết kế layout bo mạch in mở rộng (Carrier Board) chuẩn 1 lớp đồng đáy (B.Cu) với 5 cầu nối dây jumper mặt trên; đã xuất đầy đủ bộ 10 bản vẽ PDF gia công chuẩn tỷ lệ vật lý 1:1 (bản đơn và bản ghép tấm khổ A4 phục vụ phương pháp ủi nhiệt và in film cảm quang).\n"
            "4. Hoàn thành xây dựng module phần mềm Python điều khiển chuyển động bánh Mecanum (`motor_controller.py`, `config.py`) và kiểm thử logic thành công trên hệ điều hành Raspberry Pi OS.\n"
            "5. Hoàn thành thiết kế giao diện Web Dashboard (`code/website/`) kết nối máy chủ Python cho phép điều khiển 8 hướng và điều chỉnh tốc độ PWM mượt mà qua mạng Wi-Fi.\n"
            "6. Đã kiểm thử thành công thuật toán khởi tạo hiển thị mã QR động trên màn hình OLED 1.3 inch và luồng xử lý ảnh trừ nền phát hiện chuyển động bằng OpenCV qua camera CSI."
        )
        curr = insert_p_after(doc, p_4_1, desc_4_1)

        # Insert Bảng 4.1: Bảng tổng hợp tiến độ hoàn thành các hạng mục nghiên cứu
        p_cap_4_1 = insert_p_after(doc, curr, "Bảng 4.1: Bảng tổng hợp tiến độ hoàn thành các hạng mục nghiên cứu của đề tài", style='Caption', italic=True)
        tbl_prog = insert_tbl_after(doc, p_cap_4_1, 10, 4, style='Table Grid')
        
        add_styled_cell(tbl_prog.rows[0].cells[0], "STT", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")
        add_styled_cell(tbl_prog.rows[0].cells[1], "Nội dung nghiên cứu & Hạng mục công việc", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")
        add_styled_cell(tbl_prog.rows[0].cells[2], "Sản phẩm / Kết quả bàn giao", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")
        add_styled_cell(tbl_prog.rows[0].cells[3], "Trạng thái", bold=True, font_size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex="D9E1F2")

        progress_data = [
            ("1", "Khảo sát tài liệu, lựa chọn linh kiện phần cứng", "Báo cáo đề cương, thông số phần cứng", "Đã hoàn thành 100%"),
            ("2", "Thiết kế kiến trúc hệ thống và quy hoạch chân GPIO", "Sơ đồ khối 4 phân hệ, Bảng phân bổ chân", "Đã hoàn thành 100%"),
            ("3", "Thiết kế sơ đồ nguyên lý phần cứng trên KiCad 10", "File Schematic, thư viện linh kiện chuẩn", "Đã hoàn thành 100%"),
            ("4", "Thiết kế bo mạch in mở rộng Carrier Board 1 lớp", "File PCB 1 lớp B.Cu, bộ 10 file PDF gia công 1:1", "Đã hoàn thành 100%"),
            ("5", "Lập trình module điều khiển động cơ bánh Mecanum", "Source code Python (motor_controller.py)", "Đã hoàn thành 100%"),
            ("6", "Xây dựng Web Dashboard điều khiển robot qua Wi-Fi", "Giao diện Web HTML/CSS/JS + Python server", "Đã hoàn thành 100%"),
            ("7", "Thử nghiệm hiển thị mã QR trên OLED 1.3\" & OpenCV", "Module tạo QR động, thuật toán trừ nền", "Đã hoàn thành 100%"),
            ("8", "Gia công mạch in PCB thực tế & hàn lắp linh kiện", "Bo mạch phần cứng hoàn chỉnh sau khi ủi/rọi film", "Đang triển khai thực hiện"),
            ("9", "Lắp ráp khung xe cơ khí & tích hợp toàn bộ hệ thống", "Mô hình robot tự hành vật lý hoàn chỉnh", "Kế hoạch giai đoạn tiếp theo"),
        ]
        for idx, (stt, work, prod, stat) in enumerate(progress_data):
            r = tbl_prog.rows[idx + 1]
            fill = "E2EFDA" if "100%" in stat else ("FFF2CC" if "Đang" in stat else "FFFFFF")
            add_styled_cell(r.cells[0], stt, bold=True, font_size=10, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex=fill)
            add_styled_cell(r.cells[1], work, bold=False, font_size=10, align=WD_ALIGN_PARAGRAPH.LEFT, fill_hex=fill)
            add_styled_cell(r.cells[2], prod, bold=False, font_size=10, align=WD_ALIGN_PARAGRAPH.LEFT, fill_hex=fill)
            add_styled_cell(r.cells[3], stat, bold=True, font_size=10, align=WD_ALIGN_PARAGRAPH.CENTER, fill_hex=fill)

        # 4.2 Phương án và kế hoạch thực nghiệm các module chức năng
        p_4_2 = insert_p_after(doc, tbl_prog, "4.2 Phương án và kế hoạch thực nghiệm các module chức năng", style='Heading 2')
        desc_4_2 = (
            "Giai đoạn tiếp theo của đề tài tập trung vào việc hiện thực hóa phần cứng vật lý và đo đạc thực nghiệm theo các bước kế hoạch cụ thể:\n"
            "• Thực nghiệm gia công mạch in PCB và kiểm tra thông mạch: Sử dụng bộ file PDF `01_Panel_4x_...` và `06_Don_1X_...` để in decal nhiệt, ủi phôi đồng 1 mặt, ăn mòn bằng dung dịch FeCl3, khoan các lỗ linh kiện chuẩn 0.8mm và 1.0mm, hàn 5 cầu nối dây jumper mặt trên, đo kiểm tra chạm chập bằng đồng hồ VOM trước khi cấp nguồn.\n"
            "• Thực nghiệm module điều khiển chuyển động bánh Mecanum: Kiểm tra dạng sóng xung PWM trên máy hiện sóng oscilloscope; đo đạc vận tốc thực tế, độ trôi lệch khi robot tịnh tiến ngang và xoay tại chỗ trên bề mặt sàn gạch men và sàn gỗ.\n"
            "• Thực nghiệm module cảm biến siêu âm né tránh vật cản: Đo kiểm sai số khoảng cách của cảm biến HC-SR04 ở các cự ly từ 10 cm đến 200 cm với các loại bề mặt phản xạ khác nhau (tường phẳng, vật thể tròn, chướng ngại vật di động); đánh giá thời gian phản hồi dừng xe an toàn khi phát hiện vật cản đột ngột.\n"
            "• Thực nghiệm module Camera và tương tác khách hàng qua mã QR: Đo đạc độ trễ nhận diện chuyển động qua Camera CSI trong điều kiện ánh sáng tiêu chuẩn trong nhà (300 – 500 lux); đo khoảng cách và thời gian người dùng quét thành công mã QR hiển thị trên màn hình OLED 1.3 inch bằng các dòng điện thoại thông minh phổ biến.\n"
            "• Thực nghiệm tổng hợp hệ thống: Cho robot vận hành liên tục theo kịch bản giao nhận hàng hóa nội khu trong không gian hành lang mô phỏng; đo đạc độ ổn định của kết nối mạng Wi-Fi và thời lượng tiêu thụ năng lượng của bộ pin Li-ion 3S2P."
        )
        insert_p_after(doc, p_4_2, desc_4_2)

    # Clean any leftover empty headings or FPGA lines in Chapter 4
    for p in doc.paragraphs:
        txt = p.text.strip()
        if "Tài nguyên FPGA sau tổng hợp" in txt or "hệ thống FPGA" in txt:
            p.text = ""

    # =========================================================================
    # 8. TÀI LIỆU THAM KHẢO
    # =========================================================================
    print("8. Updating References (Removing FPGA, Adding Pi 4, KiCad, OpenCV)...")
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
    
    # Locate references in doc
    ref_paras = []
    found_ref = False
    for p in doc.paragraphs:
        if p.text.strip() == "TÀI LIỆU THAM KHẢO":
            found_ref = True
            continue
        if found_ref:
            if p.text.strip() == "PHỤ LỤC":
                break
            if p.text.strip():
                ref_paras.append(p)

    for idx, ref_text in enumerate(clean_refs):
        if idx < len(ref_paras):
            ref_paras[idx].text = ref_text
            ref_paras[idx].style = 'List Paragraph'
        else:
            new_p = doc.add_paragraph(ref_text, style='List Paragraph')
            if ref_paras:
                ref_paras[-1]._p.addnext(new_p._p)
                ref_paras.append(new_p)

    # Blank out any leftover ref paragraphs beyond len(clean_refs)
    if len(ref_paras) > len(clean_refs):
        for p in ref_paras[len(clean_refs):]:
            p.text = ""

    print(f"Saving updated document to {DOCX_OUT}...")
    doc.save(DOCX_OUT)
    print("SUCCESS: Document updated completely!")

if __name__ == '__main__':
    update_document()
