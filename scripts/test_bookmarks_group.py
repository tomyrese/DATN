import docx, os, sys, subprocess, re
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

sys.stdout.reconfigure(encoding='utf-8')

def test_file(docx_path):
    cmd = [
        'python', '-c',
        f'''
import win32com.client, os, sys
word = win32com.client.Dispatch('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(os.path.abspath(r"{docx_path}"), False, True, False)
    print("OK:", doc.Paragraphs.Count)
    doc.Close(False)
except Exception as e:
    print("ERR:", e)
finally:
    word.Quit(False)
'''
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
        return res.stdout.strip()
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/F', '/IM', 'WINWORD.EXE'], capture_output=True)
        return "TIMEOUT (Dialog Prompt!)"

def add_bookmark(p_elem, bm_name, bm_id):
    bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bm_id}" w:name="{bm_name}"/>')
    bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bm_id}"/>')
    pPr = p_elem.pPr
    if pPr is not None:
        pPr.addnext(bm_start)
    else:
        p_elem.insert(0, bm_start)
    p_elem.append(bm_end)

doc = docx.Document('test_C_toc_bm.docx')

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

# Find MỞ ĐẦU
mo_dau_idx = -1
for i, p in enumerate(doc.paragraphs):
    if p.text.strip() == "MỞ ĐẦU":
        mo_dau_idx = i
        break

body_paras = doc.paragraphs[mo_dau_idx:]

bm_id = 3000
for item in figures_items:
    fig_title, page, bm_name, pattern = item
    for p in body_paras:
        texts = p.text.strip()
        if re.search(pattern, texts, re.IGNORECASE):
            add_bookmark(p._p, bm_name, bm_id)
            bm_id += 1
            break

for item in tables_items:
    tab_title, page, bm_name, pattern = item
    for p in body_paras:
        texts = p.text.strip()
        if re.search(pattern, texts, re.IGNORECASE):
            add_bookmark(p._p, bm_name, bm_id)
            bm_id += 1
            break

# Also test font enforcement
for r in doc._element.xpath('.//w:r'):
    rPr = r.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
    if rPr is not None:
        rFonts = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts')
        if rFonts is not None:
            rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii', 'Times New Roman')
            rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi', 'Times New Roman')
            rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cs', 'Times New Roman')
            rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia', 'Times New Roman')

doc.save('test_D_all_bookmarks_and_fonts.docx')
print("Test D (All 103 Bookmarks + Fonts):", test_file('test_D_all_bookmarks_and_fonts.docx'))
