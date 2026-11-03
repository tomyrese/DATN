import docx, os, sys, subprocess, html, re
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

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

def make_para(style="Normal", text="", space_before=60, space_after=60, line=312, sz=26, b=False, i=False, align="both"):
    rPr_parts = [
        f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
    ]
    if b: rPr_parts.append(f'<w:b {nsdecls("w")}/><w:bCs {nsdecls("w")}/>')
    rPr_parts.append(f'<w:sz {nsdecls("w")} w:val="{sz}"/><w:szCs {nsdecls("w")} w:val="{sz}"/>')
    
    run_xml = f'''
    <w:r {nsdecls("w")}>
        <w:rPr>{"".join(rPr_parts)}</w:rPr>
        <w:t xml:space="preserve">{html.escape(text)}</w:t>
    </w:r>
    '''
    full_xml = f'''
    <w:p {nsdecls("w")}>
        <w:pPr>
            <w:pStyle w:val="{style}"/>
            <w:spacing w:before="{space_before}" w:after="{space_after}" w:line="{line}" w:lineRule="auto"/>
            <w:jc w:val="{align}"/>
            <w:rPr>{"".join(rPr_parts)}</w:rPr>
        </w:pPr>
        {run_xml}
    </w:p>
    '''
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

toc_items = [
    (1, "DANH MỤC HÌNH ẢNH", "7", "_Toc_DMHA"),
    (1, "DANH MỤC BẢNG BIỂU", "8", "_Toc_DMBB"),
    (1, "DANH MỤC TỪ VIẾT TẮT", "9", "_Toc_DMTVT"),
    (1, "MỞ ĐẦU", "10", "_Toc_MODAU"),
    (2, "1. Đặt vấn đề", "10", "_Toc_1_DAT_VAN_DE"),
    (2, "2. Mục tiêu đề tài", "11", "_Toc_2_MUC_TIEU"),
    (2, "3. Đối tượng và phạm vi nghiên cứu", "11", "_Toc_3_DOI_TUONG"),
    (3, "3.1. Đối tượng nghiên cứu", "11", "_Toc_3_1_DT"),
    (3, "3.2. Phạm vi nghiên cứu", "12", "_Toc_3_2_PV"),
    (2, "4. Ý nghĩa thực tiễn của đề tài", "12", "_Toc_4_Y_NGHIA"),
    (1, "CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI", "13", "_Toc_CH1"),
    (2, "1.1 Các nghiên cứu liên quan", "13", "_Toc_1_1"),
    (3, "1.1.1 Các nghiên cứu ngoài nước", "13", "_Toc_1_1_1"),
    (3, "1.1.2 Các nghiên cứu trong nước", "13", "_Toc_1_1_2"),
    (2, "1.2 Phần cứng sử dụng", "14", "_Toc_1_2"),
    (3, "1.2.1 Bo mạch máy tính nhúng Raspberry Pi 4 Model B (8GB)", "14", "_Toc_1_2_1"),
    (3, "1.2.2 Động cơ giảm tốc vàng TT và Khung bánh Mecanum", "15", "_Toc_1_2_2"),
    (3, "1.2.3 Mạch điều khiển động cơ TB6612FNG", "16", "_Toc_1_2_3"),
    (3, "1.2.4 Raspberry Pi Camera Module V1.3 (OV5647)", "17", "_Toc_1_2_4"),
    (3, "1.2.5 Cảm biến khoảng cách Ultrasonic sensor HC-SR04", "18", "_Toc_1_2_5"),
    (3, "1.2.6 Màn hình hiển thị OLED 1.3 inch I²C", "19", "_Toc_1_2_6"),
    (2, "1.3 Mô hình đề tài", "20", "_Toc_1_3"),
    (1, "CHƯƠNG 2: CƠ SỞ LÝ THUYẾT", "21", "_Toc_CH2"),
    (2, "2.1 Nền tảng máy tính nhúng và Raspberry Pi 4", "21", "_Toc_2_1"),
    (3, "2.1.1 Tổng quan về máy tính nhúng (Single Board Computer - SBC)", "21", "_Toc_2_1_1"),
    (3, "2.1.2 Bo mạch Raspberry Pi 4 Model B (8GB)", "22", "_Toc_2_1_2"),
    (3, "2.1.3 Lý do chọn Raspberry Pi 4 làm nền tảng điều khiển", "23", "_Toc_2_1_3"),
    (2, "2.2 Điều khiển động cơ giảm tốc TT và hệ thống bánh Mecanum", "24", "_Toc_2_2"),
    (3, "2.2.1 Nguyên lý hoạt động của động cơ giảm tốc vàng TT", "24", "_Toc_2_2_1"),
    (3, "2.2.2 Điều khiển tốc độ bằng PWM", "25", "_Toc_2_2_2"),
    (3, "2.2.3 Mạch cầu H điều khiển chiều quay", "25", "_Toc_2_2_3"),
    (2, "2.3 Động học và điều khiển hệ thống bánh xe đa hướng Mecanum", "25", "_Toc_2_3"),
    (2, "2.4 Xử lý cảm biến khoảng cách Ultrasonic sensor", "26", "_Toc_2_4"),
    (2, "2.5 Xử lý hình ảnh cơ bản", "27", "_Toc_2_5"),
    (3, "2.5.1 Thu nhận và số hóa hình ảnh qua giao tiếp MIPI CSI", "27", "_Toc_2_5_1"),
    (3, "2.5.2 Phát hiện chuyển động và nhận diện đối tượng bằng OpenCV", "27", "_Toc_2_5_2"),
    (2, "2.6 Các giao tiếp sử dụng trong đề tài", "28", "_Toc_2_6"),
    (3, "2.6.1 Điều chế độ rộng xung PWM", "28", "_Toc_2_6_1"),
    (3, "2.6.2 Giao tiếp nối tiếp I²C và hiển thị OLED", "28", "_Toc_2_6_2"),
    (2, "2.7 Công cụ thiết kế và phát triển", "29", "_Toc_2_7"),
    (3, "2.7.1 Môi trường lập trình Visual Studio Code & Python 3", "29", "_Toc_2_7_1"),
    (3, "2.7.2 Phần mềm thiết kế điện tử KiCad EDA phiên bản 10.0", "30", "_Toc_2_7_2"),
    (1, "CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG", "31", "_Toc_CH3"),
    (2, "3.1 Mô hình hệ thống chi tiết", "31", "_Toc_3_1"),
    (3, "3.1.1 Sơ đồ tổng thể hệ thống", "31", "_Toc_3_1_1"),
    (3, "3.1.2 Sơ đồ nguyên lý và thiết kế bo mạch mở rộng (Carrier Board)", "31", "_Toc_3_1_2"),
    (3, "3.1.3 Lưu đồ hoạt động của hệ thống", "33", "_Toc_3_1_3"),
    (3, "3.1.4 Phân bổ tài nguyên trên Raspberry Pi 4 Model B (8GB)", "34", "_Toc_3_1_4"),
    (2, "3.2 Thiết kế module điều khiển chuyển động", "34", "_Toc_3_2"),
    (3, "3.2.1 Mô hình động học và Lưu đồ hoạt động module điều khiển động cơ", "34", "_Toc_3_2_1"),
    (3, "3.2.2 Sơ đồ mạch nguyên lý giao tiếp giữa GPIO Raspberry Pi 4 và Driver cầu H", "35", "_Toc_3_2_2"),
    (2, "3.3 Thiết kế module đọc cảm biến khoảng cách", "35", "_Toc_3_3"),
    (3, "3.3.1 Nguyên lý đọc cảm biến siêu âm HC-SR04 & Mạch cầu phân áp bảo vệ GPIO", "35", "_Toc_3_3_1"),
    (3, "3.3.2 Thuật toán tránh vật cản", "36", "_Toc_3_3_2"),
    (2, "3.4 Thiết kế module xử lý Camera và nhận diện khách hàng", "36", "_Toc_3_4"),
    (3, "3.4.1 Lưu đồ xử lý hình ảnh nhận diện khách hàng", "36", "_Toc_3_4_1"),
    (3, "3.4.2 Tích hợp Camera MIPI CSI và Màn hình OLED 1.3 inch với Raspberry Pi 4", "37", "_Toc_3_4_2"),
    (2, "3.5 Thiết kế giao diện điều khiển và giám sát qua Web (Web Dashboard)", "37", "_Toc_3_5"),
    (3, "3.5.1 Kiến trúc hệ thống Web Server điều khiển", "37", "_Toc_3_5_1"),
    (3, "3.5.2 Giao diện giám sát và điều khiển thực tế", "38", "_Toc_3_5_2"),
    (1, "CHƯƠNG 4: KẾ HOẠCH VÀ PHƯƠNG ÁN THỰC NGHIỆM HỆ THỐNG", "39", "_Toc_CH4"),
    (2, "4.1 Tiến độ thực hiện hiện tại của đề tài (Các nội dung đã hoàn thành)", "39", "_Toc_4_1"),
    (2, "4.2 Phương án và kế hoạch thực nghiệm các module chức năng", "40", "_Toc_4_2"),
    (1, "KẾT LUẬN VÀ KIẾN NGHỊ", "41", "_Toc_KET_LUAN"),
    (1, "TÀI LIỆU THAM KHẢO", "42", "_Toc_TAI_LIEU_THAM_KHAO"),
    (2, "1. Tài liệu tham khảo tiếng Việt", "42", "_Toc_REF_VN"),
    (2, "2. Tài liệu tham khảo tiếng Anh", "43", "_Toc_REF_EN"),
    (1, "PHỤ LỤC", "44", "_Toc_PHU_LUC"),
]

# Test B: Add all 68 items to SDT TOC
docB = docx.Document('test_A_fig_tab.docx')
sdt_list = docB._element.xpath('//w:sdt')
sdt = sdt_list[0]
sdtContent = sdt.find(qn('w:sdtContent'))
for child in list(sdtContent):
    sdtContent.remove(child)

p_toc_title = make_para("Title", "MỤC LỤC", space_before=240, space_after=240, sz=30, b=True, align="center")
sdtContent.append(p_toc_title)

for item in toc_items:
    level, title, page, bm_name = item
    toc_style = f"TOC{level}"
    sz_val = 28 if level == 1 else 26
    b_val = True if level == 1 else False
    sp_before = 40 if level == 1 else 20
    sp_after = 40 if level == 1 else 20
    p_hl = make_hyperlink_para(toc_style, bm_name, title, page, sz=sz_val, b=b_val, sp_before=sp_before, sp_after=sp_after)
    sdtContent.append(p_hl)

docB.save('test_B_sdt_all.docx')
print("Test B (All 68 SDT entries):", test_file('test_B_sdt_all.docx'))
