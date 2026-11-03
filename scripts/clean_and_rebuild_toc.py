import os, sys, zipfile, re
import xml.etree.ElementTree as ET
import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

sys.stdout.reconfigure(encoding='utf-8')

DOCX_FILE = 'PL2_Robot_TuHanh_Pi4.docx'

def main():
    print(f"Loading document: {DOCX_FILE}...")
    doc = docx.Document(DOCX_FILE)
    body = doc._body._element

    # =========================================================================
    # 1. FIX PARAGRAPHS IN BODY TEXT
    # =========================================================================
    print("1. Cleaning obsolete text in body paragraphs...")
    for i, p in enumerate(doc.paragraphs):
        txt = p.text
        # Fix Servo in Objectives
        if "động cơ Servo" in txt or "cơ cấu nâng/mở" in txt:
            p.text = (
                "Thiết kế bo mạch mở rộng Carrier Board chuyên dụng chuẩn 1 lớp trên phần mềm KiCad 10, "
                "tích hợp khối nguồn Buck XL4015, 2 driver TB6612FNG, các cụm trở phân áp 1kΩ / 2kΩ bảo vệ mức áp 3.3V cho GPIO "
                "và xuất bộ bản vẽ PDF gia công 1:1 chuẩn phục vụ chế tạo thực tế."
            )
            print(f"  Fixed P{i}: Replaced Servo in Objectives with Carrier Board KiCad 10")
        
        # Fix FPGA in reason to choose Pi 4
        if "bo mạch FPGA" in txt:
            p.text = txt.replace(
                "vi điều khiển (MCU) hay bo mạch FPGA",
                "các nền tảng vi điều khiển truyền thống (như STM32, Arduino, ESP32) bị giới hạn về bộ nhớ và năng lực tính toán thị giác máy tính"
            )
            print(f"  Fixed P{i}: Replaced FPGA comparison in Pi 4 section")

        # Fix Servo in PWM section
        if "Đối với động cơ Servo: Tín hiệu PWM" in txt:
            p.text = (
                "Đối với hệ thống truyền động: Tín hiệu Hardware PWM được khởi tạo trên các chân GPIO chuyên dụng của Raspberry Pi 4 "
                "ở tần số 1 kHz (chu kỳ 1 ms), cấp vào chân PWMA_L và PWMA_R của 2 mạch driver TB6612FNG để điều chỉnh mượt mà "
                "chu kỳ nhiệm vụ (Duty Cycle từ 20% đến 100%), đáp ứng chuyển động ổn định và mô-men xoắn cao cho 4 động cơ giảm tốc TT."
            )
            print(f"  Fixed P{i}: Replaced Servo PWM with TB6612 Hardware PWM 1 kHz")

    # =========================================================================
    # 2. REBUILD TABLE OF CONTENTS (MỤC LỤC) INSIDE <w:sdtContent>
    # =========================================================================
    print("2. Rebuilding Table of Contents in SDT...")
    sdt = body.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sdt')
    if sdt is None:
        print("ERROR: SDT for Table of Contents not found!")
        return

    sdtContent = sdt.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sdtContent')
    if sdtContent is None:
        print("ERROR: sdtContent not found!")
        return

    # Clear all existing paragraphs in sdtContent
    sdtContent.clear()

    # Define exact, 100% accurate TOC items
    toc_items = [
        # (Level, Title, Page)
        (0, "MỤC LỤC", None),
        (1, "DANH MỤC HÌNH ẢNH", "7"),
        (1, "DANH MỤC BẢNG BIỂU", "8"),
        (1, "DANH MỤC TỪ VIẾT TẮT", "9"),
        (1, "MỞ ĐẦU", "10"),
        (2, "1. Đặt vấn đề", "10"),
        (2, "2. Mục tiêu đề tài", "11"),
        (2, "3. Đối tượng và phạm vi nghiên cứu", "11"),
        (3, "3.1. Đối tượng nghiên cứu", "11"),
        (3, "3.2. Phạm vi nghiên cứu", "12"),
        (2, "4. Ý nghĩa thực tiễn của đề tài", "12"),
        (1, "CHƯƠNG 1\tTỔNG QUAN VỀ ĐỀ TÀI", "13"),
        (2, "1.1 Các nghiên cứu liên quan", "13"),
        (3, "1.1.1 Các nghiên cứu ngoài nước", "13"),
        (3, "1.1.2 Các nghiên cứu trong nước", "13"),
        (2, "1.2 Phần cứng sử dụng", "14"),
        (3, "1.2.1 Bo mạch máy tính nhúng Raspberry Pi 4 Model B (8GB)", "14"),
        (3, "1.2.2 Động cơ giảm tốc vàng TT và Khung bánh Mecanum", "15"),
        (3, "1.2.3 Mạch điều khiển động cơ TB6612FNG", "16"),
        (3, "1.2.4 Raspberry Pi Camera Module V1.3 (OV5647)", "17"),
        (3, "1.2.5 Cảm biến khoảng cách Ultrasonic sensor HC-SR04", "18"),
        (3, "1.2.6 Màn hình hiển thị OLED 1.3 inch I²C", "19"),
        (2, "1.3 Mô hình đề tài", "20"),
        (1, "CHƯƠNG 2\tCƠ SỞ LÝ THUYẾT", "21"),
        (2, "2.1 Nền tảng máy tính nhúng và Raspberry Pi 4", "21"),
        (3, "2.1.1 Tổng quan về máy tính nhúng (Single Board Computer - SBC)", "21"),
        (3, "2.1.2 Bo mạch Raspberry Pi 4 Model B (8GB)", "22"),
        (3, "2.1.3 Lý do chọn Raspberry Pi 4 làm nền tảng điều khiển", "23"),
        (2, "2.2 Điều khiển động cơ giảm tốc TT và hệ thống bánh Mecanum", "24"),
        (3, "2.2.1 Nguyên lý hoạt động của động cơ giảm tốc vàng TT", "24"),
        (3, "2.2.2 Điều khiển tốc độ bằng PWM", "25"),
        (3, "2.2.3 Mạch cầu H điều khiển chiều quay", "25"),
        (2, "2.4 Xử lý cảm biến khoảng cách Ultrasonic sensor", "26"),
        (2, "2.5 Xử lý hình ảnh cơ bản", "27"),
        (3, "2.5.1 Thu nhận và số hóa hình ảnh qua giao tiếp MIPI CSI", "27"),
        (3, "2.5.2 Phát hiện chuyển động và nhận diện đối tượng bằng OpenCV", "27"),
        (2, "2.6 Các giao tiếp sử dụng trong đề tài", "28"),
        (3, "2.6.1 Điều chế độ rộng xung PWM", "28"),
        (3, "2.6.2 Giao tiếp nối tiếp I²C", "28"),
        (2, "2.7 Công cụ thiết kế và phát triển", "29"),
        (3, "2.7.1 Môi trường lập trình Visual Studio Code & Python 3", "29"),
        (3, "2.7.2 Phần mềm thiết kế điện tử KiCad EDA phiên bản 10.0", "30"),
        (1, "CHƯƠNG 3\tPHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG", "31"),
        (2, "3.1 Mô hình hệ thống chi tiết", "31"),
        (3, "3.1.1 Sơ đồ tổng thể hệ thống", "31"),
        (3, "3.1.2 Sơ đồ nguyên lý và thiết kế bo mạch mở rộng (Carrier Board)", "31"),
        (3, "3.1.3 Lưu đồ hoạt động của hệ thống", "33"),
        (3, "3.1.4 Phân bổ tài nguyên trên Raspberry Pi 4 Model B (8GB)", "34"),
        (2, "3.2 Thiết kế module điều khiển chuyển động", "34"),
        (3, "3.2.1 Mô hình động học và Lưu đồ hoạt động module điều khiển động cơ", "34"),
        (3, "3.2.2 Sơ đồ mạch nguyên lý giao tiếp giữa GPIO Raspberry Pi 4 và Driver cầu H", "35"),
        (2, "3.3 Thiết kế module đọc cảm biến khoảng cách", "35"),
        (3, "3.3.1 Nguyên lý đọc cảm biến siêu âm HC-SR04 & Mạch cầu phân áp bảo vệ GPIO", "35"),
        (3, "3.3.2 Thuật toán tránh vật cản", "36"),
        (2, "3.4 Thiết kế module xử lý Camera và nhận diện khách hàng", "36"),
        (3, "3.4.1 Lưu đồ xử lý hình ảnh nhận diện khách hàng", "36"),
        (3, "3.4.2 Tích hợp Camera MIPI CSI và Màn hình OLED 1.3 inch với Raspberry Pi 4", "37"),
        (2, "3.5 Thiết kế giao diện điều khiển và giám sát qua Web (Web Dashboard)", "37"),
        (3, "3.5.1 Kiến trúc hệ thống Web Server điều khiển", "37"),
        (3, "3.5.2 Giao diện giám sát và điều khiển thực tế", "38"),
        (1, "CHƯƠNG 4\tKẾ HOẠCH VÀ PHƯƠNG ÁN THỰC NGHIỆM HỆ THỐNG", "39"),
        (2, "4.1 Tiến độ thực hiện hiện tại của đề tài (Các nội dung đã hoàn thành)", "39"),
        (2, "4.2 Phương án và kế hoạch thực nghiệm các module chức năng", "40"),
        (1, "KẾT LUẬN VÀ KIẾN NGHỊ", "41"),
        (1, "TÀI LIỆU THAM KHẢO", "42"),
        (1, "PHỤ LỤC", "43"),
    ]

    for level, title, page_num in toc_items:
        if level == 0:
            # Title MỤC LỤC
            p_xml = f'''<w:p {nsdecls("w")}>
              <w:pPr>
                <w:pStyle w:val="Title"/>
                <w:jc w:val="center"/>
                <w:spacing w:before="120" w:after="240"/>
                <w:rPr>
                  <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
                  <w:b/>
                  <w:sz w:val="32"/>
                </w:rPr>
              </w:pPr>
              <w:r>
                <w:rPr>
                  <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
                  <w:b/>
                  <w:sz w:val="32"/>
                </w:rPr>
                <w:t>MỤC LỤC</w:t>
              </w:r>
            </w:p>'''
        else:
            p_style = f"TOC{level}"
            bold_xml = "<w:b/>" if level == 1 else ""
            sz_val = "24" if level <= 2 else "22"
            indent_xml = ""
            if level == 2:
                indent_xml = '<w:ind w:left="280"/>'
            elif level == 3:
                indent_xml = '<w:ind w:left="560"/>'

            # Clean XML text escape
            clean_title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

            p_xml = f'''<w:p {nsdecls("w")}>
              <w:pPr>
                <w:pStyle w:val="{p_style}"/>
                <w:tabs>
                  <w:tab w:val="right" w:leader="dot" w:pos="9061"/>
                </w:tabs>
                {indent_xml}
                <w:spacing w:line="260" w:lineRule="auto" w:after="30" w:before="30"/>
                <w:rPr>
                  <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
                  {bold_xml}
                  <w:sz w:val="{sz_val}"/>
                </w:rPr>
              </w:pPr>
              <w:r>
                <w:rPr>
                  <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
                  {bold_xml}
                  <w:sz w:val="{sz_val}"/>
                </w:rPr>
                <w:t>{clean_title}</w:t>
              </w:r>
              <w:r>
                <w:rPr>
                  <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
                  <w:sz w:val="{sz_val}"/>
                </w:rPr>
                <w:tab/>
              </w:r>
              <w:r>
                <w:rPr>
                  <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
                  {bold_xml}
                  <w:sz w:val="{sz_val}"/>
                </w:rPr>
                <w:t>{page_num}</w:t>
              </w:r>
            </w:p>'''

        new_p = parse_xml(p_xml)
        sdtContent.append(new_p)

    print(f"Rebuilt TOC with {len(toc_items)} clean items!")

    print(f"Saving updated document: {DOCX_FILE}...")
    doc.save(DOCX_FILE)
    print("SUCCESS: Body and SDT TOC updated successfully!")

if __name__ == '__main__':
    main()

