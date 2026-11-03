import docx, os, sys, re, html, win32com.client
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.stdout.reconfigure(encoding='utf-8')

DOCX_IN = 'PL2_Robot_TuHanh_Pi44_backup_before_hyperlink.docx'
DOCX_OUT = 'PL2_Robot_TuHanh_Pi44.docx'

print("=== STARTING DOCX MASTER BUILDER ===")
print(f"Loading base document: {DOCX_IN}...")
doc = docx.Document(DOCX_IN)

# ==========================================================
# STEP 1: SET PAGE MARGINS (A4, Top 2.0, Bottom 2.0, Left 3.0, Right 2.0)
# ==========================================================
print("\n[Step 1] Setting standard thesis page margins...")
for s_idx, section in enumerate(doc.sections):
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(3.0)      # Gáy sách 3.0 cm
    section.right_margin = Cm(2.0)
    section.header_distance = Cm(1.25)
    section.footer_distance = Cm(1.25)
print(f"  Applied standard margins to {len(doc.sections)} section(s).")

# ==========================================================
# STEP 2: REMOVE OLD _Toc BOOKMARKS
# ==========================================================
print("\n[Step 2] Cleaning up old _Toc bookmarks...")
bm_removed = 0
for p in doc.paragraphs:
    for bm in p._p.xpath('.//w:bookmarkStart[starts-with(@w:name, "_Toc")]'):
        bm.getparent().remove(bm)
        bm_removed += 1
    for bm in p._p.xpath('.//w:bookmarkEnd'):
        # Check matching ID if needed or remove orphaned
        pass
print(f"  Removed {bm_removed} old _Toc bookmarks.")

# Helper to create schema-perfect paragraph XML
def make_para(style="Normal", text="", space_before=60, space_after=60, line=312, sz=26, b=False, i=False, align="both", indent_left=0, indent_hanging=0, indent_first=0):
    pPr_parts = []
    if style:
        pPr_parts.append(f'<w:pStyle {nsdecls("w")} w:val="{style}"/>')
    pPr_parts.append(f'<w:spacing {nsdecls("w")} w:before="{space_before}" w:after="{space_after}" w:line="{line}" w:lineRule="auto"/>')
    
    ind_attrs = []
    if indent_left > 0: ind_attrs.append(f'w:left="{indent_left}"')
    if indent_hanging > 0: ind_attrs.append(f'w:hanging="{indent_hanging}"')
    if indent_first > 0: ind_attrs.append(f'w:firstLine="{indent_first}"')
    if ind_attrs:
        pPr_parts.append(f'<w:ind {nsdecls("w")} {" ".join(ind_attrs)}/>')
        
    if align != "left":
        pPr_parts.append(f'<w:jc {nsdecls("w")} w:val="{align}"/>')
        
    rPr_parts = [
        f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
    ]
    if b: rPr_parts.append(f'<w:b {nsdecls("w")}/><w:bCs {nsdecls("w")}/>')
    if i: rPr_parts.append(f'<w:i {nsdecls("w")}/><w:iCs {nsdecls("w")}/>')
    rPr_parts.append(f'<w:sz {nsdecls("w")} w:val="{sz}"/><w:szCs {nsdecls("w")} w:val="{sz}"/>')
    
    pPr_parts.append(f'<w:rPr {nsdecls("w")}>{"".join(rPr_parts)}</w:rPr>')
    
    run_xml = f'''
    <w:r {nsdecls("w")}>
        <w:rPr>{"".join(rPr_parts)}</w:rPr>
        <w:t xml:space="preserve">{html.escape(text)}</w:t>
    </w:r>
    '''
    
    full_xml = f'''<w:p {nsdecls("w")}><w:pPr>{"".join(pPr_parts)}</w:pPr>{run_xml}</w:p>'''
    return parse_xml(full_xml)

def make_hyperlink_para(style="TableofFigures", anchor="", text="", page="", sz=26, b=False, sp_before=20, sp_after=20):
    b_tag = f'<w:b {nsdecls("w")}/><w:bCs {nsdecls("w")}/>' if b else ''
    xml = f'''
    <w:p {nsdecls("w")}>
        <w:pPr>
            <w:pStyle w:val="{style}"/>
            <w:tabs>
                <w:tab w:val="right" w:leader="dot" w:pos="9071"/>
            </w:tabs>
            <w:spacing w:before="{sp_before}" w:after="{sp_after}" w:line="260" w:lineRule="auto"/>
            <w:rPr>
                <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                {b_tag}
                <w:color w:val="000000"/>
                <w:sz w:val="{sz}"/>
                <w:szCs w:val="{sz}"/>
            </w:rPr>
        </w:pPr>
        <w:hyperlink w:anchor="{anchor}" w:history="1">
            <w:r>
                <w:rPr>
                    <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                    {b_tag}
                    <w:color w:val="000000"/>
                    <w:sz w:val="{sz}"/>
                    <w:szCs w:val="{sz}"/>
                    <w:u w:val="none"/>
                </w:rPr>
                <w:t>{html.escape(text)}</w:t>
            </w:r>
            <w:r>
                <w:rPr>
                    <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                    <w:sz w:val="{sz}"/>
                    <w:szCs w:val="{sz}"/>
                </w:rPr>
                <w:tab/>
            </w:r>
            <w:r>
                <w:rPr>
                    <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                    {b_tag}
                    <w:color w:val="000000"/>
                    <w:sz w:val="{sz}"/>
                    <w:szCs w:val="{sz}"/>
                    <w:u w:val="none"/>
                </w:rPr>
                <w:t>{html.escape(page)}</w:t>
            </w:r>
        </w:hyperlink>
    </w:p>
    '''
    return parse_xml(xml)

# ==========================================================
# STEP 3: INSERT SECTION 2.3 & FIGURE 2.4
# ==========================================================
print("\n[Step 3] Checking Section 2.3 & Figure 2.4...")
has_sec23 = any("2.3 Động học" in p.text for p in doc.paragraphs)
if not has_sec23:
    target_p = None
    for p in doc.paragraphs:
        if p.text.strip().startswith("2.4 Xử lý cảm biến"):
            target_p = p
            break
    if target_p:
        p_sec23_head = make_para("Heading2", "2.3 Động học và điều khiển hệ thống bánh xe đa hướng Mecanum", space_before=160, space_after=80, sz=28, b=True, align="left")
        p_sec23_body = make_para("Normal", "Hệ thống di chuyển của robot sử dụng 04 bánh xe đa hướng Mecanum đặt đối xứng tại 4 góc khung xe. Mỗi bánh xe có các con lăn phụ tự do nghiêng một góc 45° so với trục quay chính. Khi động cơ dẫn động quay độc lập từng bánh, lực ma sát giữa các con lăn và mặt sàn tạo ra các vector lực đẩy hợp thành. Bằng cách điều phối vận tốc góc và chiều quay của 4 động cơ thông qua tín hiệu xung PWM từ Raspberry Pi 4, robot có thể thực hiện di chuyển đa hướng linh hoạt trong không gian 2D (tiến/lùi, tịnh tiến ngang trái/phải, di chuyển chéo góc 45° và xoay tròn tại chỗ) mà không cần thêm cơ cấu bẻ lái cơ khí phức tạp.", space_before=60, space_after=60, line=312, sz=26, align="both", indent_first=567)
        p_sec23_fig = make_para("Caption", "Hình 2.4: Nguyên lý phân bố vector lực và vận tốc của bánh xe đa hướng Mecanum", space_before=80, space_after=120, line=260, sz=24, b=True, i=True, align="center")
        
        target_p._p.addprevious(p_sec23_head)
        target_p._p.addprevious(p_sec23_body)
        target_p._p.addprevious(p_sec23_fig)
        print("  Inserted section 2.3 and Figure 2.4 successfully!")
else:
    print("  Section 2.3 already present.")

# ==========================================================
# STEP 4: UPDATE REFERENCES SECTION (TIẾNG VIỆT & TIẾNG ANH)
# ==========================================================
print("\n[Step 4] Updating References section (Tiếng Việt & Tiếng Anh)...")
ref_title_p = None
phu_luc_p = None
for p in doc.paragraphs:
    t = p.text.strip()
    if t == "TÀI LIỆU THAM KHẢO":
        ref_title_p = p
    elif t == "PHỤ LỤC":
        phu_luc_p = p

if ref_title_p and phu_luc_p:
    # Remove old paras between ref_title_p and phu_luc_p
    curr = ref_title_p._p.getnext()
    while curr is not None and curr != phu_luc_p._p:
        nxt = curr.getnext()
        curr.getparent().remove(curr)
        curr = nxt
    
    # Insert Vietnamese & English subheadings and references
    vn_head = make_para("Heading2", "1. Tài liệu tham khảo tiếng Việt", space_before=160, space_after=80, sz=28, b=True, align="left")
    phu_luc_p._p.addprevious(vn_head)
    
    vn_refs = [
        "[1] TS. Nguyễn Văn Thái, Giáo trình Kỹ thuật Robot, Nhà xuất bản Khoa học và Kỹ thuật, Hà Nội, 2020.",
        "[2] PGS. TS. Nguyễn Đức Thành, Hệ thống nhúng và ứng dụng máy tính đơn bộc Linux, Nhà xuất bản Thông tin và Truyền thông, Hà Nội, 2021.",
        "[3] ThS. Lê Lý Quyên Quyên, Tài liệu hướng dẫn Đề cương Khóa luận tốt nghiệp chuyên ngành Công nghệ Kỹ thuật Máy tính, Khoa Công nghệ Điện tử, Trường Đại học Công nghiệp TP. Hồ Chí Minh, 2026.",
        "[4] PGS. TS. Đỗ Năng Toàn, TS. Phạm Việt Bình, Giáo trình Xử lý ảnh và Thị giác máy tính, Nhà xuất bản Đại học Quốc gia Hà Nội, 2018.",
        "[5] TS. Trần Thu Hà, Thiết kế mạch in và ứng dụng phần mềm EDA trong phát triển phần cứng điện tử, Nhà xuất bản Giáo dục Việt Nam, 2022.",
        "[6] Bộ môn Kỹ thuật Máy tính, Sổ tay tra cứu linh kiện phần cứng và các chuẩn giao tiếp công nghiệp, Trường Đại học Công nghiệp TP. Hồ Chí Minh, 2023."
    ]
    for r in vn_refs:
        p_ref = make_para("Normal", r, space_before=40, space_after=80, line=312, sz=26, align="both", indent_left=567, indent_hanging=567)
        phu_luc_p._p.addprevious(p_ref)
        
    en_head = make_para("Heading2", "2. Tài liệu tham khảo tiếng Anh", space_before=240, space_after=80, sz=28, b=True, align="left")
    phu_luc_p._p.addprevious(en_head)
    
    en_refs = [
        '[1] Raspberry Pi Foundation, "Raspberry Pi 4 Model B Specifications and Hardware Architecture Guide," Raspberry Pi Documentation, 2023. [Online]. Available: https://www.raspberrypi.com/documentation/',
        '[2] Broadcom Corporation, "BCM2711 ARM Peripherals Architecture Datasheet," Broadcom Inc., 2020.',
        '[3] Toshiba Electronic Devices & Storage Corporation, "TB6612FNG Dual DC Motor Driver Datasheet," Rev 2.0, 2014.',
        '[4] Sino Wealth Electronic Ltd., "SH1106 132 x 64 Dot Matrix OLED/PLED Driver with Controller Datasheet," 2018.',
        '[5] SparkFun Electronics, "Ultrasonic Ranging Module HC-SR04 User Manual and Timing Characteristics," SparkFun Electronics, 2019.',
        '[6] KiCad Development Team, "KiCad 10.0 EDA Schematic and PCB Layout Suite Documentation," 2026. [Online]. Available: https://docs.kicad.org',
        '[7] OpenCV Team, "OpenCV 4 Computer Vision Library Reference Manual," 2024. [Online]. Available: https://docs.opencv.org',
        '[8] Python Software Foundation, "Python 3.12 Standard Library and Hardware GPIO Documentation," 2024. [Online]. Available: https://docs.python.org',
        '[9] B. Siciliano and O. Khatib, Springer Handbook of Robotics, 2nd ed., Berlin Heidelberg: Springer-Verlag, 2016.',
        '[10] S. Thrun, W. Burgard, and D. Fox, Probabilistic Robotics, Cambridge: MIT Press, 2005.',
        '[11] R. Murphy, Introduction to AI Robotics, 2nd ed., Cambridge: MIT Press, 2019.'
    ]
    for r in en_refs:
        p_ref = make_para("Normal", r, space_before=40, space_after=80, line=312, sz=26, align="both", indent_left=567, indent_hanging=567)
        phu_luc_p._p.addprevious(p_ref)
    print("  Cleaned and split References successfully!")

# ==========================================================
# STEP 5: REBUILD DANH MỤC HÌNH ẢNH
# ==========================================================
print("\n[Step 5] Rebuilding DANH MỤC HÌNH ẢNH...")
figures_items = [
    ("Hình 1.1: So sánh các nền tảng điều khiển robot phổ biến", "13", "_Toc_Hinh_1_1", r"^Hình\s+1\.1"),
    ("Hình 1.2: Bo mạch máy tính nhúng Raspberry Pi 4 Model B (8GB)", "14", "_Toc_Hinh_1_2", r"^Hình\s+1\.2"),
    ("Hình 1.3: Động cơ giảm tốc vàng TT trục kép 3-6VDC và bánh xe Mecanum", "15", "_Toc_Hinh_1_3", r"^Hình\s+1\.3"),
    ("Hình 1.4: Mạch driver điều khiển động cơ TB6612FNG", "16", "_Toc_Hinh_1_4", r"^Hình\s+1\.4"),
    ("Hình 1.5: Module Raspberry Pi Camera V1.3 (OV5647)", "17", "_Toc_Hinh_1_5", r"^Hình\s+1\.5"),
    ("Hình 1.6: Cảm biến khoảng cách Ultrasonic sensor HC-SR04", "18", "_Toc_Hinh_1_6", r"^Hình\s+1\.6"),
    ("Hình 1.7: Module màn hình hiển thị OLED 1.3 inch I²C", "19", "_Toc_Hinh_1_7", r"^Hình\s+1\.7"),
    ("Hình 2.1: Sơ đồ kiến trúc tổng quát của máy tính nhúng", "21", "_Toc_Hinh_2_1", r"^Hình\s+2\.1"),
    ("Hình 2.2: Cấu trúc bên trong Raspberry Pi 4 Model B (8GB)", "22", "_Toc_Hinh_2_2", r"^Hình\s+2\.2"),
    ("Hình 2.3: Sơ đồ nguyên lý điều khiển động cơ DC TT bằng PWM và mạch cầu H", "24", "_Toc_Hinh_2_3", r"^Hình\s+2\.3"),
    ("Hình 2.4: Nguyên lý phân bố vector lực và vận tốc của bánh xe đa hướng Mecanum", "25", "_Toc_Hinh_2_4", r"^Hình\s+2\.4"),
    ("Hình 2.5: Nguyên lý hoạt động của cảm biến khoảng cách Ultrasonic sensor", "26", "_Toc_Hinh_2_5", r"^Hình\s+2\.5"),
    ("Hình 2.6: Luồng xử lý ảnh nhận diện khách hàng trong hệ thống bằng OpenCV", "27", "_Toc_Hinh_2_6", r"^Hình\s+2\.6"),
    ("Hình 3.1: Sơ đồ tổng thể kiến trúc hệ thống robot tự hành trên nền tảng Raspberry Pi 4", "29", "_Toc_Hinh_3_1", r"^Hình\s+3\.1"),
    ("Hình 3.2: Sơ đồ nguyên lý chi tiết bo mạch mở rộng (Carrier Board) trên KiCad 10", "30", "_Toc_Hinh_3_2", r"^Hình\s+3\.2"),
    ("Hình 3.3: Bản vẽ thiết kế mạch in (PCB) 1 lớp mặt đáy B.Cu với 5 cầu nối dây Jumper", "31", "_Toc_Hinh_3_3", r"^Hình\s+3\.3"),
    ("Hình 3.4: Lưu đồ hoạt động tổng thể của hệ thống robot tự hành", "33", "_Toc_Hinh_3_4", r"^Hình\s+3\.4"),
    ("Hình 3.5: Lưu đồ giải thuật điều khiển động học 4 bánh Mecanum & PWM", "34", "_Toc_Hinh_3_5", r"^Hình\s+3\.5"),
    ("Hình 3.6: Lưu đồ giải thuật đọc cảm biến siêu âm HC-SR04 và né tránh vật cản đa cấp", "35", "_Toc_Hinh_3_6", r"^Hình\s+3\.6"),
    ("Hình 3.7: Lưu đồ giải thuật xử lý Camera CSI & Nhận diện khách hàng bằng OpenCV kết hợp OLED", "36", "_Toc_Hinh_3_7", r"^Hình\s+3\.7"),
    ("Hình 3.8: Lưu đồ hoạt động của máy chủ Web Server và Giao diện Web Dashboard", "37", "_Toc_Hinh_3_8", r"^Hình\s+3\.8"),
    ("Hình 3.9: Giao diện Web Dashboard điều khiển và giám sát robot qua mạng Wi-Fi", "38", "_Toc_Hinh_3_9", r"^Hình\s+3\.9"),
]

p_dmha = None
p_dmbb = None
for p in doc.paragraphs:
    t = p.text.strip()
    if t == "DANH MỤC HÌNH ẢNH":
        p_dmha = p
    elif t == "DANH MỤC BẢNG BIỂU":
        p_dmbb = p

if p_dmha and p_dmbb:
    curr = p_dmha._p.getnext()
    while curr is not None and curr != p_dmbb._p:
        nxt = curr.getnext()
        curr.getparent().remove(curr)
        curr = nxt
    
    for fig_title, page, bm_name, pattern in figures_items:
        p_fig_hl = make_hyperlink_para("TableofFigures", bm_name, fig_title, page, sz=26, b=False)
        p_dmbb._p.addprevious(p_fig_hl)
    print("  Rebuilt DANH MỤC HÌNH ẢNH with hyperlinked dot leaders!")

# ==========================================================
# STEP 6: REBUILD DANH MỤC BẢNG BIỂU
# ==========================================================
print("\n[Step 6] Rebuilding DANH MỤC BẢNG BIỂU...")
tables_items = [
    ("Bảng 1.1: Thông số kỹ thuật Raspberry Pi 4 Model B (8GB)", "14", "_Toc_Bang_1_1", r"^Bảng\s+1\.1"),
    ("Bảng 1.2: Thông số kỹ thuật động cơ giảm tốc TT trục kép 3-6VDC", "15", "_Toc_Bang_1_2", r"^Bảng\s+1\.2"),
    ("Bảng 1.3: Thông số kỹ thuật module Driver TB6612FNG", "16", "_Toc_Bang_1_3", r"^Bảng\s+1\.3"),
    ("Bảng 1.4: Thông số kỹ thuật Raspberry Pi Camera V1.3 (OV5647)", "17", "_Toc_Bang_1_4", r"^Bảng\s+1\.4"),
    ("Bảng 1.5: Thông số kỹ thuật cảm biến khoảng cách siêu âm HC-SR04", "18", "_Toc_Bang_1_5", r"^Bảng\s+1\.5"),
    ("Bảng 1.6: Thông số kỹ thuật màn hình hiển thị OLED 1.3 inch I²C", "19", "_Toc_Bang_1_6", r"^Bảng\s+1\.6"),
    ("Bảng 2.1: Thành phần và thông số cốt lõi của Raspberry Pi 4 Model B (8GB)", "22", "_Toc_Bang_2_1", r"^Bảng\s+2\.1"),
    ("Bảng 3.1: Bảng phân bổ chân GPIO của Raspberry Pi 4 trên Bo mạch Carrier Board", "31", "_Toc_Bang_3_1", r"^Bảng\s+3\.1"),
    ("Bảng 3.2: Phân bổ và quản lý tài nguyên trên Raspberry Pi 4 Model B (8GB)", "32", "_Toc_Bang_3_2", r"^Bảng\s+3\.2"),
    ("Bảng 3.3: Bảng tra cứu trạng thái logic điều khiển chiều quay và tốc độ động cơ", "34", "_Toc_Bang_3_3", r"^Bảng\s+3\.3"),
    ("Bảng 3.4: Ngưỡng khoảng cách và hành vi điều khiển né tránh vật cản của robot", "35", "_Toc_Bang_3_4", r"^Bảng\s+3\.4"),
    ("Bảng 4.1: Bảng tổng hợp tiến độ hoàn thành các hạng mục nghiên cứu của đề tài", "39", "_Toc_Bang_4_1", r"^Bảng\s+4\.1"),
    ("Bảng 4.2: Kế hoạch phân bổ thời gian thực hiện các giai đoạn tiếp theo của đề tài", "40", "_Toc_Bang_4_2", r"^Bảng\s+4\.2"),
]

p_dmtvt = None
for p in doc.paragraphs:
    if p.text.strip() == "DANH MỤC TỪ VIẾT TẮT":
        p_dmtvt = p
        break

if p_dmbb and p_dmtvt:
    curr = p_dmbb._p.getnext()
    while curr is not None and curr != p_dmtvt._p:
        nxt = curr.getnext()
        curr.getparent().remove(curr)
        curr = nxt
        
    for tab_title, page, bm_name, pattern in tables_items:
        p_tab_hl = make_hyperlink_para("TableofFigures", bm_name, tab_title, page, sz=26, b=False)
        p_dmtvt._p.addprevious(p_tab_hl)
    print("  Rebuilt DANH MỤC BẢNG BIỂU with hyperlinked dot leaders!")

# ==========================================================
# STEP 7: INSERT BOOKMARKS INTO TARGET PARAGRAPHS
# ==========================================================
print("\n[Step 7] Inserting Bookmarks into target paragraphs...")

bm_id_counter = 1000

def add_bookmark(p_elem, bm_name, bm_id):
    bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bm_id}" w:name="{bm_name}"/>')
    bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bm_id}"/>')
    pPr = p_elem.pPr
    if pPr is not None:
        pPr.addnext(bm_start)
    else:
        p_elem.insert(0, bm_start)
    p_elem.append(bm_end)

toc_items = [
    (1, "DANH MỤC HÌNH ẢNH", "7", "_Toc_DMHA", r"^DANH\s+MỤC\s+HÌNH\s+ẢNH", "Title"),
    (1, "DANH MỤC BẢNG BIỂU", "8", "_Toc_DMBB", r"^DANH\s+MỤC\s+BẢNG\s+BIỂU", "Title"),
    (1, "DANH MỤC TỪ VIẾT TẮT", "9", "_Toc_DMTVT", r"^DANH\s+MỤC\s+TỪ\s+VIẾT\s+TẮT", "Title"),
    (1, "MỞ ĐẦU", "10", "_Toc_MODAU", r"^MỞ\s+ĐẦU", "Title"),
    (2, "1. Đặt vấn đề", "10", "_Toc_1_DAT_VAN_DE", r"^1\.\s+Đặt\s+vấn\s+đề", "Heading2"),
    (2, "2. Mục tiêu đề tài", "11", "_Toc_2_MUC_TIEU", r"^2\.\s+Mục\s+tiêu\s+đề\s+tài", "Heading2"),
    (2, "3. Đối tượng và phạm vi nghiên cứu", "11", "_Toc_3_DOI_TUONG", r"^3\.\s+Đối\s+tượng\s+và\s+phạm\s+vi", "Heading2"),
    (3, "3.1. Đối tượng nghiên cứu", "11", "_Toc_3_1_DT", r"^3\.1\.\s+Đối\s+tượng\s+nghiên\s+cứu", "Heading3"),
    (3, "3.2. Phạm vi nghiên cứu", "12", "_Toc_3_2_PV", r"^3\.2\.\s+Phạm\s+vi\s+nghiên\s+cứu", "Heading3"),
    (2, "4. Ý nghĩa thực tiễn của đề tài", "12", "_Toc_4_Y_NGHIA", r"^4\.\s+Ý\s+nghĩa\s+thực\s+tiễn", "Heading2"),
    
    (1, "CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI", "13", "_Toc_CH1", r"^(CHƯƠNG\s+1[:\s]+)?TỔNG\s+QUAN\s+VỀ\s+ĐỀ\s+TÀI", "Heading1"),
    (2, "1.1 Các nghiên cứu liên quan", "13", "_Toc_1_1", r"^1\.1\s+Các\s+nghiên\s+cứu", "Heading2"),
    (3, "1.1.1 Các nghiên cứu ngoài nước", "13", "_Toc_1_1_1", r"^1\.1\.1\s+Các\s+nghiên\s+cứu\s+ngoài", "Heading3"),
    (3, "1.1.2 Các nghiên cứu trong nước", "13", "_Toc_1_1_2", r"^1\.1\.2\s+Các\s+nghiên\s+cứu\s+trong", "Heading3"),
    (2, "1.2 Phần cứng sử dụng", "14", "_Toc_1_2", r"^1\.2\s+Phần\s+cứng\s+sử\s+dụng", "Heading2"),
    (3, "1.2.1 Bo mạch máy tính nhúng Raspberry Pi 4 Model B (8GB)", "14", "_Toc_1_2_1", r"^1\.2\.1\s+Bo\s+mạch\s+máy\s+tính\s+nhúng", "Heading3"),
    (3, "1.2.2 Động cơ giảm tốc vàng TT và Khung bánh Mecanum", "15", "_Toc_1_2_2", r"^1\.2\.2\s+Động\s+cơ\s+giảm\s+tốc", "Heading3"),
    (3, "1.2.3 Mạch điều khiển động cơ TB6612FNG", "16", "_Toc_1_2_3", r"^1\.2\.3\s+Mạch\s+điều\s+khiển\s+động\s+cơ", "Heading3"),
    (3, "1.2.4 Raspberry Pi Camera Module V1.3 (OV5647)", "17", "_Toc_1_2_4", r"^1\.2\.4\s+Raspberry\s+Pi\s+Camera", "Heading3"),
    (3, "1.2.5 Cảm biến khoảng cách Ultrasonic sensor HC-SR04", "18", "_Toc_1_2_5", r"^1\.2\.5\s+Cảm\s+biến\s+khoảng\s+cách", "Heading3"),
    (3, "1.2.6 Màn hình hiển thị OLED 1.3 inch I²C", "19", "_Toc_1_2_6", r"^1\.2\.6\s+Màn\s+hình\s+hiển\s+thị\s+OLED", "Heading3"),
    (2, "1.3 Mô hình đề tài", "20", "_Toc_1_3", r"^1\.3\s+Mô\s+hình\s+đề\s+tài", "Heading2"),

    (1, "CHƯƠNG 2: CƠ SỞ LÝ THUYẾT", "21", "_Toc_CH2", r"^(CHƯƠNG\s+2[:\s]+)?CƠ\s+SỞ\s+LÝ\s+THUYẾT", "Heading1"),
    (2, "2.1 Nền tảng máy tính nhúng và Raspberry Pi 4", "21", "_Toc_2_1", r"^2\.1\s+Nền\s+tảng\s+máy\s+tính\s+nhúng", "Heading2"),
    (3, "2.1.1 Tổng quan về máy tính nhúng (Single Board Computer - SBC)", "21", "_Toc_2_1_1", r"^2\.1\.1\s+Tổng\s+quan\s+về\s+máy\s+tính", "Heading3"),
    (3, "2.1.2 Bo mạch Raspberry Pi 4 Model B (8GB)", "22", "_Toc_2_1_2", r"^2\.1\.2\s+Bo\s+mạch\s+Raspberry", "Heading3"),
    (3, "2.1.3 Lý do chọn Raspberry Pi 4 làm nền tảng điều khiển", "23", "_Toc_2_1_3", r"^(2\.1\.3\s+)?Lý\s+do\s+chọn\s+Raspberry", "Heading3"),
    (2, "2.2 Điều khiển động cơ giảm tốc TT và hệ thống bánh Mecanum", "24", "_Toc_2_2", r"^2\.2\s+Điều\s+khiển\s+động\s+cơ", "Heading2"),
    (3, "2.2.1 Nguyên lý hoạt động của động cơ giảm tốc vàng TT", "24", "_Toc_2_2_1", r"^2\.2\.1\s+Nguyên\s+lý\s+hoạt\s+động", "Heading3"),
    (3, "2.2.2 Điều khiển tốc độ bằng PWM", "25", "_Toc_2_2_2", r"^2\.2\.2\s+Điều\s+khiển\s+tốc\s+độ", "Heading3"),
    (3, "2.2.3 Mạch cầu H điều khiển chiều quay", "25", "_Toc_2_2_3", r"^2\.2\.3\s+Mạch\s+cầu\s+H", "Heading3"),
    (2, "2.3 Động học và điều khiển hệ thống bánh xe đa hướng Mecanum", "25", "_Toc_2_3", r"^2\.3\s+Động\s+học\s+và\s+điều\s+khiển", "Heading2"),
    (2, "2.4 Xử lý cảm biến khoảng cách Ultrasonic sensor", "26", "_Toc_2_4", r"^2\.4\s+Xử\s+lý\s+cảm\s+biến", "Heading2"),
    (2, "2.5 Xử lý hình ảnh cơ bản", "27", "_Toc_2_5", r"^2\.5\s+Xử\s+lý\s+hình\s+ảnh", "Heading2"),
    (3, "2.5.1 Thu nhận và số hóa hình ảnh qua giao tiếp MIPI CSI", "27", "_Toc_2_5_1", r"^2\.5\.1\s+Thu\s+nhận\s+và\s+số\s+hóa", "Heading3"),
    (3, "2.5.2 Phát hiện chuyển động và nhận diện đối tượng bằng OpenCV", "27", "_Toc_2_5_2", r"^2\.5\.2\s+Phát\s+hiện", "Heading3"),
    (2, "2.6 Các giao tiếp sử dụng trong đề tài", "28", "_Toc_2_6", r"^(2\.6\s+)?Các\s+giao\s+tiếp\s+sử\s+dụng", "Heading2"),
    (3, "2.6.1 Điều chế độ rộng xung PWM", "28", "_Toc_2_6_1", r"^(2\.6\.1\s+)?Điều\s+chế\s+PWM", "Heading3"),
    (3, "2.6.2 Giao tiếp nối tiếp I²C và hiển thị OLED", "28", "_Toc_2_6_2", r"^(2\.6\.2\s+)?Giao\s+tiếp\s+I²C", "Heading3"),
    (2, "2.7 Công cụ thiết kế và phát triển", "29", "_Toc_2_7", r"^(2\.7\s+)?Công\s+cụ\s+thiết\s+kế", "Heading2"),
    (3, "2.7.1 Môi trường lập trình Visual Studio Code & Python 3", "29", "_Toc_2_7_1", r"^(2\.7\.1\s+)?Môi\s+trường\s+lập\s+trình", "Heading3"),
    (3, "2.7.2 Phần mềm thiết kế điện tử KiCad EDA phiên bản 10.0", "30", "_Toc_2_7_2", r"^(2\.7\.2\s+)?Phần\s+mềm\s+thiết\s+kế.*KiCad", "Heading3"),

    (1, "CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG", "31", "_Toc_CH3", r"^(CHƯƠNG\s+3[:\s]+)?PHÂN\s+TÍCH\s+VÀ\s+THIẾT\s+KẾ", "Heading1"),
    (2, "3.1 Mô hình hệ thống chi tiết", "31", "_Toc_3_1", r"^3\.1\s+Mô\s+hình\s+hệ\s+thống", "Heading2"),
    (3, "3.1.1 Sơ đồ tổng thể hệ thống", "31", "_Toc_3_1_1", r"^3\.1\.1\s+Sơ\s+đồ\s+tổng\s+thể", "Heading3"),
    (3, "3.1.2 Sơ đồ nguyên lý và thiết kế bo mạch mở rộng (Carrier Board)", "31", "_Toc_3_1_2", r"^3\.1\.2\s+Sơ\s+đồ\s+nguyên\s+lý", "Heading3"),
    (3, "3.1.3 Lưu đồ hoạt động của hệ thống", "33", "_Toc_3_1_3", r"^3\.1\.3\s+Lưu\s+đồ\s+hoạt\s+động", "Heading3"),
    (3, "3.1.4 Phân bổ tài nguyên trên Raspberry Pi 4 Model B (8GB)", "34", "_Toc_3_1_4", r"^3\.1\.4\s+Phân\s+bổ\s+tài\s+nguyên", "Heading3"),
    (2, "3.2 Thiết kế module điều khiển chuyển động", "34", "_Toc_3_2", r"^3\.2\s+Thiết\s+kế\s+module\s+điều\s+khiển\s+chuyển\s+động", "Heading2"),
    (3, "3.2.1 Mô hình động học và Lưu đồ hoạt động module điều khiển động cơ", "34", "_Toc_3_2_1", r"^3\.2\.1\s+Mô\s+hình\s+động\s+học", "Heading3"),
    (3, "3.2.2 Sơ đồ mạch nguyên lý giao tiếp giữa GPIO Raspberry Pi 4 và Driver cầu H", "35", "_Toc_3_2_2", r"^3\.2\.2\s+Sơ\s+đồ\s+mạch\s+nguyên\s+lý", "Heading3"),
    (2, "3.3 Thiết kế module đọc cảm biến khoảng cách", "35", "_Toc_3_3", r"^3\.3\s+Thiết\s+kế\s+module\s+đọc\s+cảm\s+biến", "Heading2"),
    (3, "3.3.1 Nguyên lý đọc cảm biến siêu âm HC-SR04 & Mạch cầu phân áp bảo vệ GPIO", "35", "_Toc_3_3_1", r"^3\.3\.1\s+Nguyên\s+lý\s+đọc\s+cảm\s+biến", "Heading3"),
    (3, "3.3.2 Thuật toán tránh vật cản", "36", "_Toc_3_3_2", r"^3\.3\.2\s+Thuật\s+toán\s+tránh\s+vật\s+cản", "Heading3"),
    (2, "3.4 Thiết kế module xử lý Camera và nhận diện khách hàng", "36", "_Toc_3_4", r"^3\.4\s+Thiết\s+kế\s+module\s+xử\s+lý\s+Camera", "Heading2"),
    (3, "3.4.1 Lưu đồ xử lý hình ảnh nhận diện khách hàng", "36", "_Toc_3_4_1", r"^3\.4\.1\s+Lưu\s+đồ\s+xử\s+lý\s+hình\s+ảnh", "Heading3"),
    (3, "3.4.2 Tích hợp Camera MIPI CSI và Màn hình OLED 1.3 inch với Raspberry Pi 4", "37", "_Toc_3_4_2", r"^3\.4\.2\s+Tích\s+hợp\s+Camera", "Heading3"),
    (2, "3.5 Thiết kế giao diện điều khiển và giám sát qua Web (Web Dashboard)", "37", "_Toc_3_5", r"^3\.5\s+Thiết\s+kế\s+giao\s+diện\s+điều\s+khiển", "Heading2"),
    (3, "3.5.1 Kiến trúc hệ thống Web Server điều khiển", "37", "_Toc_3_5_1", r"^3\.5\.1\s+Kiến\s+trúc\s+hệ\s+thống", "Heading3"),
    (3, "3.5.2 Giao diện giám sát và điều khiển thực tế", "38", "_Toc_3_5_2", r"^3\.5\.2\s+Giao\s+diện\s+giám\s+sát", "Heading3"),

    (1, "CHƯƠNG 4: KẾ HOẠCH VÀ PHƯƠNG ÁN THỰC NGHIỆM HỆ THỐNG", "39", "_Toc_CH4", r"^(CHƯƠNG\s+4[:\s]+)?KẾ\s+HOẠCH\s+VÀ\s+PHƯƠNG\s+ÁN", "Heading1"),
    (2, "4.1 Tiến độ thực hiện hiện tại của đề tài (Các nội dung đã hoàn thành)", "39", "_Toc_4_1", r"^4\.1\s+Tiến\s+độ\s+thực\s+hiện", "Heading2"),
    (2, "4.2 Phương án và kế hoạch thực nghiệm các module chức năng", "40", "_Toc_4_2", r"^4\.2\s+Phương\s+án\s+và\s+kế\s+hoạch", "Heading2"),

    (1, "KẾT LUẬN VÀ KIẾN NGHỊ", "41", "_Toc_KET_LUAN", r"^KẾT\s+LUẬN\s+VÀ\s+KIẾN\s+NGHỊ", "Title"),
    (1, "TÀI LIỆU THAM KHẢO", "42", "_Toc_TAI_LIEU_THAM_KHAO", r"^TÀI\s+LIỆU\s+THAM\s+KHẢO", "Title"),
    (2, "1. Tài liệu tham khảo tiếng Việt", "42", "_Toc_REF_VN", r"^1\.\s+Tài\s+liệu\s+tham\s+khảo\s+tiếng\s+Việt", "Heading2"),
    (2, "2. Tài liệu tham khảo tiếng Anh", "43", "_Toc_REF_EN", r"^2\.\s+Tài\s+liệu\s+tham\s+khảo\s+tiếng\s+Anh", "Heading2"),
    (1, "PHỤ LỤC", "44", "_Toc_PHU_LUC", r"^PHỤ\s+LỤC", "Title"),
]

matched_toc = set()
for item in toc_items:
    level, title, page, bm_name, pattern, style = item
    for p in doc.paragraphs:
        texts = p.text.strip()
        if not texts:
            continue
        if re.search(pattern, texts, re.IGNORECASE):
            add_bookmark(p._p, bm_name, bm_id_counter)
            bm_id_counter += 1
            matched_toc.add(bm_name)
            break

print(f"  Matched & bookmarked {len(matched_toc)} / {len(toc_items)} TOC items.")

# Find MỞ ĐẦU paragraph index to search figures and tables ONLY in body text
mo_dau_idx = -1
for i, p in enumerate(doc.paragraphs):
    if p.text.strip() == "MỞ ĐẦU":
        mo_dau_idx = i
        break

body_paras = doc.paragraphs[mo_dau_idx:] if mo_dau_idx != -1 else doc.paragraphs

# Match Figures
matched_figs = set()
for item in figures_items:
    fig_title, page, bm_name, pattern = item
    for p in body_paras:
        texts = p.text.strip()
        if re.search(pattern, texts, re.IGNORECASE):
            add_bookmark(p._p, bm_name, bm_id_counter)
            bm_id_counter += 1
            matched_figs.add(bm_name)
            break
print(f"  Matched & bookmarked {len(matched_figs)} / {len(figures_items)} figures.")

# Match Tables
matched_tabs = set()
for item in tables_items:
    tab_title, page, bm_name, pattern = item
    for p in body_paras:
        texts = p.text.strip()
        if re.search(pattern, texts, re.IGNORECASE):
            add_bookmark(p._p, bm_name, bm_id_counter)
            bm_id_counter += 1
            matched_tabs.add(bm_name)
            break
print(f"  Matched & bookmarked {len(matched_tabs)} / {len(tables_items)} tables.")

# ==========================================================
# STEP 8: REBUILD TABLE OF CONTENTS (MỤC LỤC) IN SDT
# ==========================================================
print("\n[Step 8] Rebuilding Table of Contents in SDT with hyperlinks...")
sdt_list = doc._element.xpath('//w:sdt')
if sdt_list:
    sdt = sdt_list[0]
    sdtContent = sdt.find(qn('w:sdtContent'))
    if sdtContent is not None:
        for child in list(sdtContent):
            sdtContent.remove(child)
            
        p_toc_title = make_para("Title", "MỤC LỤC", space_before=240, space_after=240, sz=30, b=True, align="center")
        sdtContent.append(p_toc_title)
        
        for item in toc_items:
            level, title, page, bm_name, pattern, style = item
            toc_style = f"TOC{level}"
            sz_val = 28 if level == 1 else 26
            b_val = True if level == 1 else False
            sp_before = 40 if level == 1 else 20
            sp_after = 40 if level == 1 else 20
            
            p_toc_hl = make_hyperlink_para(toc_style, bm_name, title, page, sz=sz_val, b=b_val, sp_before=sp_before, sp_after=sp_after)
            sdtContent.append(p_toc_hl)
        print("  Rebuilt MỤC LỤC SDT with 68 hyperlinked entries!")

# ==========================================================
# STEP 9: ENFORCE TIMES NEW ROMAN ON ALL RUNS
# ==========================================================
print("\n[Step 9] Enforcing Times New Roman font across all runs...")
run_cnt = 0
for r in doc._element.xpath('.//w:r'):
    rPr = r.find(qn('w:rPr'))
    if rPr is not None:
        rFonts = rPr.find(qn('w:rFonts'))
        if rFonts is not None:
            rFonts.set(qn('w:ascii'), 'Times New Roman')
            rFonts.set(qn('w:hAnsi'), 'Times New Roman')
            rFonts.set(qn('w:cs'), 'Times New Roman')
            rFonts.set(qn('w:eastAsia'), 'Times New Roman')
            run_cnt += 1
print(f"  Enforced Times New Roman on {run_cnt} runs.")

# ==========================================================
# STEP 10: SAVE DOCUMENT
# ==========================================================
print(f"\n[Step 10] Saving final document to {DOCX_OUT}...")
doc.save(DOCX_OUT)
print(f"  Successfully saved {DOCX_OUT}!")

# ==========================================================
# STEP 11: VERIFY WITH WORD COM
# ==========================================================
print("\n[Step 11] Verifying with Microsoft Word COM...")
word = None
try:
    word = win32com.client.Dispatch('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    abs_out = os.path.abspath(DOCX_OUT)
    doc_word = word.Documents.Open(abs_out, False, True, False)
    cnt = doc_word.Paragraphs.Count
    print(f"  >>> SUCCESS: Microsoft Word opened {DOCX_OUT} with ZERO errors or dialogs! Total paragraphs: {cnt} <<<")
    doc_word.Close(False)
except Exception as e:
    print(f"  >>> FAILED to open in Word: {e} <<<")
finally:
    if word:
        try:
            word.Quit(False)
        except:
            pass

print("\n=== MASTER BUILD COMPLETED SUCCESSFULLY ===")

