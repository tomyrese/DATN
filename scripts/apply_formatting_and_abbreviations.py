import os, sys, zipfile, re, shutil
import xml.etree.ElementTree as ET
import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

DOCX_FILE = 'PL2_Robot_TuHanh_Pi4.docx'
BACKUP_FILE = 'PL2_Robot_TuHanh_Pi4_pre_formatting.docx'

# 34 comprehensive technical acronyms
ABBREVIATIONS = [
    ("SBC", "Single Board Computer – Máy tính đơn bo mạch hoàn chỉnh (Raspberry Pi 4 Model B)"),
    ("SoC", "System on Chip – Hệ thống vi mạch tích hợp toàn diện trên một chip (Broadcom BCM2711)"),
    ("CPU", "Central Processing Unit – Bộ vi xử lý trung tâm (Quad-core ARM Cortex-A72 1.5GHz)"),
    ("GPU", "Graphics Processing Unit – Bộ xử lý đồ họa tích hợp (Broadcom VideoCore VI)"),
    ("RAM", "Random Access Memory – Bộ nhớ truy xuất ngẫu nhiên (LPDDR4 dung lượng 8GB)"),
    ("LPDDR4", "Low-Power Double Data Rate 4 – Chuẩn bộ nhớ RAM thế hệ 4 tiết kiệm năng lượng"),
    ("OS", "Operating System – Hệ điều hành (Raspberry Pi OS 64-bit nhân Linux Debian)"),
    ("GPIO", "General Purpose Input/Output – Các chân tín hiệu vào/ra đa dụng của Raspberry Pi 4"),
    ("PWM", "Pulse Width Modulation – Kỹ thuật điều chế độ rộng xung điều khiển tốc độ động cơ"),
    ("I²C", "Inter-Integrated Circuit – Giao thức truyền thông nối tiếp 2 dây (SDA/SCL) cho màn hình OLED"),
    ("CSI", "Camera Serial Interface – Giao diện nối tiếp vi sai tốc độ cao chuẩn MIPI kết nối Camera"),
    ("MIPI", "Mobile Industry Processor Interface – Chuẩn giao diện công nghiệp cho bộ vi xử lý di động"),
    ("PCB", "Printed Circuit Board – Bo mạch in điện tử phần cứng"),
    ("EDA", "Electronic Design Automation – Hệ thống phần mềm tự động hóa thiết kế mạch điện tử (KiCad 10)"),
    ("DRC", "Design Rule Check – Kiểm tra quy chuẩn và ràng buộc khoảng cách an toàn thiết kế PCB"),
    ("B.Cu", "Bottom Copper – Lớp dẫn điện bằng đồng ở mặt đáy của bo mạch in 1 lớp"),
    ("F.Cu", "Front Copper – Lớp đồng mặt trên của bo mạch in (dùng làm dây nối/cầu Jumper)"),
    ("F.SilkS", "Front Silkscreen – Lớp in lụa mặt trên ghi chú tên linh kiện, vị trí và cực tính"),
    ("Edge.Cuts", "Edge Cuts – Lớp định hình đường bao viền vật lý kích thước của bo mạch PCB"),
    ("BOM", "Bill of Materials – Bảng định mức kỹ thuật và danh mục thống kê linh kiện chế tạo"),
    ("VOM", "Volt-Ohm-Milliammeter – Đồng hồ đo vạn năng kiểm tra điện áp, dòng điện và thông mạch"),
    ("DC", "Direct Current – Dòng điện và điện áp một chiều (nguồn pin 7.4V/12V, logic 5V/3.3V)"),
    ("CW", "Clockwise – Chiều quay thuận (cùng chiều kim đồng hồ) của động cơ"),
    ("CCW", "Counter-Clockwise – Chiều quay nghịch (ngược chiều kim đồng hồ) của động cơ"),
    ("Li-ion", "Lithium-ion – Công nghệ pin sạc Lithium hiệu năng cao, nội trở thấp cung cấp nguồn robot"),
    ("AI", "Artificial Intelligence – Trí tuệ nhân tạo (xử lý hình ảnh thị giác máy tính với OpenCV)"),
    ("SLAM", "Simultaneous Localization and Mapping – Định vị và thiết lập bản đồ đồng thời trong không gian"),
    ("REST API", "Representational State Transfer API – Giao diện lập trình truyền nhận dữ liệu trạng thái HTTP"),
    ("HTTP", "Hypertext Transfer Protocol – Giao thức truyền tải siêu văn bản phục vụ Web Dashboard"),
    ("OLED", "Organic Light Emitting Diode – Màn hình hiển thị đi-ốt phát quang hữu cơ (kích thước 1.3 inch)"),
    ("QR Code", "Quick Response Code – Mã phản hồi nhanh 2D dùng để quét tương tác xác thực khách hàng"),
    ("FPC", "Flexible Printed Circuit – Cáp mạch mềm 15 chân kết nối trực tiếp Camera vào cổng CSI"),
    ("TTL / LVTTL", "Transistor-Transistor Logic / Low-Voltage TTL – Chuẩn mức điện thế logic số (5V và 3.3V)"),
    ("MCU", "Microcontroller Unit – Đơn vị vi điều khiển vi xử lý nhúng"),
]

FIGURE_ITEMS = [
    ("Hình 1.1: So sánh các nền tảng điều khiển robot phổ biến", "13"),
    ("Hình 1.2: Bo mạch máy tính nhúng Raspberry Pi 4 Model B (8GB)", "14"),
    ("Hình 1.3: Động cơ giảm tốc vàng TT trục kép 3-6VDC và bánh xe Mecanum", "15"),
    ("Hình 1.4: Mạch driver điều khiển động cơ TB6612FNG", "16"),
    ("Hình 1.5: Module Raspberry Pi Camera V1.3 (OV5647)", "17"),
    ("Hình 1.6: Cảm biến khoảng cách Ultrasonic sensor HC-SR04", "18"),
    ("Hình 1.7: Module màn hình hiển thị OLED 1.3 inch I²C", "19"),
    ("Hình 2.1: Sơ đồ kiến trúc tổng quát của máy tính nhúng", "21"),
    ("Hình 2.2: Cấu trúc bên trong Raspberry Pi 4 Model B (8GB)", "22"),
    ("Hình 2.3: Sơ đồ nguyên lý điều khiển động cơ DC TT bằng PWM và mạch cầu H", "24"),
    ("Hình 2.4: Nguyên lý phân bố vector lực và vận tốc của bánh xe đa hướng Mecanum", "25"),
    ("Hình 2.5: Nguyên lý hoạt động của cảm biến khoảng cách Ultrasonic sensor", "26"),
    ("Hình 2.6: Luồng xử lý ảnh nhận diện khách hàng trong hệ thống bằng OpenCV", "27"),
    ("Hình 3.1: Sơ đồ tổng thể kiến trúc hệ thống robot tự hành trên nền tảng Raspberry Pi 4", "29"),
    ("Hình 3.2: Sơ đồ nguyên lý chi tiết bo mạch mở rộng (Carrier Board) trên KiCad 10", "30"),
    ("Hình 3.3: Bản vẽ thiết kế mạch in (PCB) 1 lớp mặt đáy B.Cu với 5 cầu nối dây Jumper", "31"),
    ("Hình 3.4: Lưu đồ hoạt động tổng thể của hệ thống robot tự hành", "33"),
    ("Hình 3.5: Lưu đồ giải thuật điều khiển động học 4 bánh Mecanum & PWM", "34"),
    ("Hình 3.6: Lưu đồ giải thuật đọc cảm biến siêu âm HC-SR04 và né tránh vật cản đa cấp", "35"),
    ("Hình 3.7: Lưu đồ giải thuật xử lý Camera CSI & Nhận diện khách hàng bằng OpenCV kết hợp OLED", "36"),
    ("Hình 3.8: Lưu đồ hoạt động của máy chủ Web Server và Giao diện Web Dashboard", "37"),
    ("Hình 3.9: Giao diện Web Dashboard điều khiển và giám sát robot qua mạng Wi-Fi", "38"),
]

TABLE_ITEMS = [
    ("Bảng 1.1: Thông số kỹ thuật Raspberry Pi 4 Model B (8GB)", "14"),
    ("Bảng 1.2: Thông số kỹ thuật động cơ giảm tốc TT trục kép 3-6VDC", "15"),
    ("Bảng 1.3: Thông số kỹ thuật module Driver TB6612FNG", "16"),
    ("Bảng 1.4: Thông số kỹ thuật Raspberry Pi Camera V1.3 (OV5647)", "17"),
    ("Bảng 1.5: Thông số kỹ thuật cảm biến khoảng cách siêu âm HC-SR04", "18"),
    ("Bảng 1.6: Thông số kỹ thuật màn hình hiển thị OLED 1.3 inch I²C", "19"),
    ("Bảng 2.1: Thành phần và thông số cốt lõi của Raspberry Pi 4 Model B (8GB)", "22"),
    ("Bảng 3.1: Bảng phân bổ chân GPIO của Raspberry Pi 4 trên Bo mạch Carrier Board", "31"),
    ("Bảng 3.2: Phân bổ và quản lý tài nguyên trên Raspberry Pi 4 Model B (8GB)", "32"),
    ("Bảng 3.3: Bảng tra cứu trạng thái logic điều khiển chiều quay và tốc độ động cơ", "34"),
    ("Bảng 3.4: Ngưỡng khoảng cách và hành vi điều khiển né tránh vật cản của robot", "35"),
    ("Bảng 4.1: Bảng tổng hợp tiến độ hoàn thành các hạng mục nghiên cứu của đề tài", "39"),
    ("Bảng 4.2: Kế hoạch phân bổ thời gian thực hiện các giai đoạn tiếp theo của đề tài", "40"),
]

TOC_ITEMS = [
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
    (1, "CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI", "13"),
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
    (1, "CHƯƠNG 2: CƠ SỞ LÝ THUYẾT", "21"),
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
    (1, "CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG", "31"),
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
    (1, "CHƯƠNG 4: KẾ HOẠCH VÀ PHƯƠNG ÁN THỰC NGHIỆM HỆ THỐNG", "39"),
    (2, "4.1 Tiến độ thực hiện hiện tại của đề tài (Các nội dung đã hoàn thành)", "39"),
    (2, "4.2 Phương án và kế hoạch thực nghiệm các module chức năng", "40"),
    (1, "KẾT LUẬN VÀ KIẾN NGHỊ", "41"),
    (1, "TÀI LIỆU THAM KHẢO", "42"),
    (1, "PHỤ LỤC", "43"),
]

def make_dot_leader_p_xml(text, page_num, font_sz="24", is_bold=False, indent_dxa=0, p_style="TableofFigures"):
    """Creates a paragraph XML with right dot tab leader at pos 9061."""
    bold_tag = "<w:b/><w:bCs/>" if is_bold else ""
    indent_tag = f'<w:ind w:left="{indent_dxa}"/>' if indent_dxa > 0 else ""
    clean_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean_page = str(page_num).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    xml = f'''<w:p {nsdecls("w")}>
      <w:pPr>
        <w:pStyle w:val="{p_style}"/>
        <w:tabs>
          <w:tab w:val="right" w:leader="dot" w:pos="9061"/>
        </w:tabs>
        {indent_tag}
        <w:spacing w:line="260" w:lineRule="auto" w:before="20" w:after="20"/>
        <w:rPr>
          <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
          {bold_tag}
          <w:sz w:val="{font_sz}"/>
          <w:szCs w:val="{font_sz}"/>
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
          {bold_tag}
          <w:sz w:val="{font_sz}"/>
          <w:szCs w:val="{font_sz}"/>
          <w:color w:val="000000"/>
        </w:rPr>
        <w:t>{clean_text}</w:t>
      </w:r>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
          <w:sz w:val="{font_sz}"/>
          <w:szCs w:val="{font_sz}"/>
        </w:rPr>
        <w:tab/>
      </w:r>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
          {bold_tag}
          <w:sz w:val="{font_sz}"/>
          <w:szCs w:val="{font_sz}"/>
          <w:color w:val="000000"/>
        </w:rPr>
        <w:t>{clean_page}</w:t>
      </w:r>
    </w:p>'''
    return parse_xml(xml)


def main():
    print(f"Creating backup: {BACKUP_FILE}...")
    shutil.copyfile(DOCX_FILE, BACKUP_FILE)

    doc = docx.Document(DOCX_FILE)
    body = doc._body._element

    # =========================================================================
    # STEP 1: UPDATE TABLE 2 (DANH MỤC TỪ VIẾT TẮT)
    # =========================================================================
    print(f"1. Updating Table 2 (DANH MỤC TỪ VIẾT TẮT) with {len(ABBREVIATIONS)} entries...")
    t2 = doc.tables[2]
    # Remove all existing rows in Table 2
    tbl_elem = t2._tbl
    for tr in tbl_elem.findall(qn('w:tr')):
        tbl_elem.remove(tr)

    # Add Header Row
    hdr_xml = f'''<w:tr {nsdecls("w")}>
      <w:trPr>
        <w:tblHeader/>
      </w:trPr>
      <w:tc>
        <w:tcPr>
          <w:tcW w:w="2500" w:type="dxa"/>
          <w:tcBorders>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="888888"/>
            <w:left w:val="single" w:sz="6" w:space="0" w:color="888888"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="888888"/>
            <w:right w:val="single" w:sz="6" w:space="0" w:color="888888"/>
          </w:tcBorders>
          <w:shd w:val="clear" w:color="auto" w:fill="D9E1F2"/>
          <w:tcMar>
            <w:top w:w="100" w:type="dxa"/>
            <w:left w:w="120" w:type="dxa"/>
            <w:bottom w:w="100" w:type="dxa"/>
            <w:right w:w="120" w:type="dxa"/>
          </w:tcMar>
        </w:tcPr>
        <w:p>
          <w:pPr>
            <w:spacing w:before="40" w:after="40" w:line="260" w:lineRule="auto"/>
            <w:jc w:val="center"/>
            <w:rPr>
              <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
              <w:b/><w:bCs/>
              <w:sz w:val="26"/><w:szCs w:val="26"/>
            </w:rPr>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
              <w:b/><w:bCs/>
              <w:sz w:val="26"/><w:szCs w:val="26"/>
            </w:rPr>
            <w:t>Từ viết tắt</w:t>
          </w:r>
        </w:p>
      </w:tc>
      <w:tc>
        <w:tcPr>
          <w:tcW w:w="6571" w:type="dxa"/>
          <w:tcBorders>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="888888"/>
            <w:left w:val="single" w:sz="6" w:space="0" w:color="888888"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="888888"/>
            <w:right w:val="single" w:sz="6" w:space="0" w:color="888888"/>
          </w:tcBorders>
          <w:shd w:val="clear" w:color="auto" w:fill="D9E1F2"/>
          <w:tcMar>
            <w:top w:w="100" w:type="dxa"/>
            <w:left w:w="120" w:type="dxa"/>
            <w:bottom w:w="100" w:type="dxa"/>
            <w:right w:w="120" w:type="dxa"/>
          </w:tcMar>
        </w:tcPr>
        <w:p>
          <w:pPr>
            <w:spacing w:before="40" w:after="40" w:line="260" w:lineRule="auto"/>
            <w:jc w:val="center"/>
            <w:rPr>
              <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
              <w:b/><w:bCs/>
              <w:sz w:val="26"/><w:szCs w:val="26"/>
            </w:rPr>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
              <w:b/><w:bCs/>
              <w:sz w:val="26"/><w:szCs w:val="26"/>
            </w:rPr>
            <w:t>Giải nghĩa</w:t>
          </w:r>
        </w:p>
      </w:tc>
    </w:tr>'''
    tbl_elem.append(parse_xml(hdr_xml))

    # Add Data Rows
    for idx, (abbr, desc) in enumerate(ABBREVIATIONS):
        bg_color = "F9FAFB" if idx % 2 == 1 else "FFFFFF"
        clean_abbr = abbr.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        clean_desc = desc.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        row_xml = f'''<w:tr {nsdecls("w")}>
          <w:tc>
            <w:tcPr>
              <w:tcW w:w="2500" w:type="dxa"/>
              <w:tcBorders>
                <w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
                <w:left w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
                <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
                <w:right w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
              </w:tcBorders>
              <w:shd w:val="clear" w:color="auto" w:fill="{bg_color}"/>
              <w:tcMar>
                <w:top w:w="70" w:type="dxa"/>
                <w:left w:w="120" w:type="dxa"/>
                <w:bottom w:w="70" w:type="dxa"/>
                <w:right w:w="120" w:type="dxa"/>
              </w:tcMar>
            </w:tcPr>
            <w:p>
              <w:pPr>
                <w:spacing w:before="30" w:after="30" w:line="260" w:lineRule="auto"/>
                <w:jc w:val="center"/>
                <w:rPr>
                  <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                  <w:b/><w:bCs/>
                  <w:sz w:val="26"/><w:szCs w:val="26"/>
                </w:rPr>
              </w:pPr>
              <w:r>
                <w:rPr>
                  <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                  <w:b/><w:bCs/>
                  <w:sz w:val="26"/><w:szCs w:val="26"/>
                </w:rPr>
                <w:t>{clean_abbr}</w:t>
              </w:r>
            </w:p>
          </w:tc>
          <w:tc>
            <w:tcPr>
              <w:tcW w:w="6571" w:type="dxa"/>
              <w:tcBorders>
                <w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
                <w:left w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
                <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
                <w:right w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
              </w:tcBorders>
              <w:shd w:val="clear" w:color="auto" w:fill="{bg_color}"/>
              <w:tcMar>
                <w:top w:w="70" w:type="dxa"/>
                <w:left w:w="120" w:type="dxa"/>
                <w:bottom w:w="70" w:type="dxa"/>
                <w:right w:w="120" w:type="dxa"/>
              </w:tcMar>
            </w:tcPr>
            <w:p>
              <w:pPr>
                <w:spacing w:before="30" w:after="30" w:line="260" w:lineRule="auto"/>
                <w:jc w:val="left"/>
                <w:rPr>
                  <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                  <w:sz w:val="26"/><w:szCs w:val="26"/>
                </w:rPr>
              </w:pPr>
              <w:r>
                <w:rPr>
                  <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                  <w:sz w:val="26"/><w:szCs w:val="26"/>
                </w:rPr>
                <w:t>{clean_desc}</w:t>
              </w:r>
            </w:p>
          </w:tc>
        </w:tr>'''
        tbl_elem.append(parse_xml(row_xml))

    # =========================================================================
    # STEP 2: REBUILD DANH MỤC HÌNH ẢNH & DANH MỤC BẢNG BIỂU IN BODY
    # =========================================================================
    print("2. Rebuilding DANH MỤC HÌNH ẢNH with exact dot leaders (12pt)...")
    # Find child indices for DANH MỤC HÌNH ẢNH, DANH MỤC BẢNG BIỂU, DANH MỤC TỪ VIẾT TẮT
    hinh_anh_idx = None
    bang_bieu_idx = None
    tu_viet_tat_idx = None

    for i, child in enumerate(body):
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(child, doc)
            txt = p.text.strip()
            if txt == 'DANH MỤC HÌNH ẢNH':
                hinh_anh_idx = i
            elif txt == 'DANH MỤC BẢNG BIỂU':
                bang_bieu_idx = i
            elif txt == 'DANH MỤC TỪ VIẾT TẮT':
                tu_viet_tat_idx = i

    print(f"  Indices found: HÌNH ẢNH={hinh_anh_idx}, BẢNG BIỂU={bang_bieu_idx}, VIẾT TẮT={tu_viet_tat_idx}")

    # Remove existing paragraphs between hinh_anh_idx and bang_bieu_idx
    # We collect elements to remove
    to_remove_hinh = []
    for i in range(hinh_anh_idx + 1, bang_bieu_idx):
        to_remove_hinh.append(body[i])
    for elem in to_remove_hinh:
        body.remove(elem)

    # Insert new FIGURE paragraphs right after hinh_anh_idx
    insert_pos = list(body).index(body[hinh_anh_idx]) + 1
    for item_text, page_num in FIGURE_ITEMS:
        p_node = make_dot_leader_p_xml(item_text, page_num, font_sz="24", is_bold=False, indent_dxa=0)
        body.insert(insert_pos, p_node)
        insert_pos += 1

    # Add an empty normal separator paragraph
    sep_xml = f'''<w:p {nsdecls("w")}><w:pPr><w:spacing w:after="120"/></w:pPr></w:p>'''
    body.insert(insert_pos, parse_xml(sep_xml))

    print("3. Rebuilding DANH MỤC BẢNG BIỂU with exact dot leaders (12pt)...")
    # Re-find bang_bieu_idx and tu_viet_tat_idx
    bang_bieu_idx = None
    tu_viet_tat_idx = None
    for i, child in enumerate(body):
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(child, doc)
            txt = p.text.strip()
            if txt == 'DANH MỤC BẢNG BIỂU':
                bang_bieu_idx = i
            elif txt == 'DANH MỤC TỪ VIẾT TẮT':
                tu_viet_tat_idx = i

    to_remove_bang = []
    for i in range(bang_bieu_idx + 1, tu_viet_tat_idx):
        to_remove_bang.append(body[i])
    for elem in to_remove_bang:
        body.remove(elem)

    insert_pos = list(body).index(body[bang_bieu_idx]) + 1
    for item_text, page_num in TABLE_ITEMS:
        p_node = make_dot_leader_p_xml(item_text, page_num, font_sz="24", is_bold=False, indent_dxa=0)
        body.insert(insert_pos, p_node)
        insert_pos += 1

    # Add an empty normal separator paragraph
    body.insert(insert_pos, parse_xml(sep_xml))

    # =========================================================================
    # STEP 3: REBUILD TABLE OF CONTENTS (MỤC LỤC) IN SDT
    # =========================================================================
    print("4. Rebuilding MỤC LỤC inside SDT...")
    sdt = body.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sdt')
    if sdt is not None:
        sdtContent = sdt.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sdtContent')
        if sdtContent is not None:
            sdtContent.clear()

            for level, title, page_num in TOC_ITEMS:
                if level == 0:
                    # MỤC LỤC Title (15pt Bold Centered)
                    p_xml = f'''<w:p {nsdecls("w")}>
                      <w:pPr>
                        <w:pStyle w:val="Title"/>
                        <w:jc w:val="center"/>
                        <w:spacing w:before="120" w:after="240"/>
                        <w:rPr>
                          <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                          <w:b/><w:bCs/>
                          <w:sz w:val="30"/><w:szCs w:val="30"/>
                        </w:rPr>
                      </w:pPr>
                      <w:r>
                        <w:rPr>
                          <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                          <w:b/><w:bCs/>
                          <w:sz w:val="30"/><w:szCs w:val="30"/>
                        </w:rPr>
                        <w:t>MỤC LỤC</w:t>
                      </w:r>
                    </w:p>'''
                    sdtContent.append(parse_xml(p_xml))
                else:
                    # Level 1: Major titles and Chapters
                    # Chapter format: "CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI .......... 13"
                    is_bold = (level == 1)
                    font_sz = "28" if level == 1 else "26"  # 14pt for Level 1, 13pt for sub-headings
                    indent_dxa = 0
                    if level == 2:
                        indent_dxa = 280
                    elif level == 3:
                        indent_dxa = 560

                    p_node = make_dot_leader_p_xml(
                        title, page_num,
                        font_sz=font_sz,
                        is_bold=is_bold,
                        indent_dxa=indent_dxa,
                        p_style=f"TOC{level}"
                    )
                    sdtContent.append(p_node)

            print(f"  Rebuilt SDT MỤC LỤC with {len(TOC_ITEMS)} clean items!")

    # =========================================================================
    # STEP 4: ENFORCE GLOBAL FONT SIZES & FONT FAMILY
    # =========================================================================
    # Hierarchy:
    # 1. Chương và các Title: 15pt (sz="30", szCs="30"), Bold
    # 2. Đề mục (Heading 2, Heading 3): 14pt (sz="28", szCs="28"), Bold
    # 3. Chú thích hình ảnh & bảng biểu (Captions in body): 12pt (sz="24", szCs="24"), Italic
    # 4. Nội dung (Normal, List Paragraph, all table cells): 13pt (sz="26", szCs="26")
    # All fonts: Times New Roman
    print("5. Enforcing global font sizes & font family...")

    TITLE_TEXTS = [
        "MỤC LỤC", "DANH MỤC HÌNH ẢNH", "DANH MỤC BẢNG BIỂU", "DANH MỤC TỪ VIẾT TẮT",
        "MỞ ĐẦU", "KẾT LUẬN VÀ KIẾN NGHỊ", "TÀI LIỆU THAM KHẢO", "PHỤ LỤC",
        "THIẾT KẾ VÀ TRIỂN KHAI ROBOT TỰ HÀNH", "ĐỀ CƯƠNG KHOÁ LUẬN TỐT NGHIỆP"
    ]

    for p in doc.paragraphs:
        txt = p.text.strip()
        st = p.style.name

        # Determine Category
        is_title_or_chapter = (
            st in ['Title', 'Heading 1'] or
            any(t in txt.upper() for t in TITLE_TEXTS) or
            txt.startswith("CHƯƠNG ")
        )
        is_heading = (
            st in ['Heading 2', 'Heading 3'] or
            (not is_title_or_chapter and re.match(r'^\d+(\.\d+)*\s+', txt))
        )
        is_caption = (
            st == 'Caption' or
            txt.startswith("Hình ") or
            txt.startswith("Bảng ")
        ) and st != 'table of figures'

        # Set target formatting
        if is_title_or_chapter:
            target_sz = "30"  # 15pt
            target_bold = True
            target_italic = False
        elif is_heading:
            target_sz = "28"  # 14pt
            target_bold = True
            target_italic = False
        elif is_caption:
            target_sz = "24"  # 12pt
            target_bold = False
            target_italic = True
        elif st == 'table of figures':
            target_sz = "24"  # 12pt
            target_bold = False
            target_italic = False
        else:
            # Normal body, list paragraphs
            target_sz = "26"  # 13pt
            target_bold = None  # preserve existing bold inline (e.g. key terms)
            target_italic = None

        # Apply to paragraph properties
        pPr = p._p.get_or_add_pPr()
        rPr_p = pPr.find(qn('w:rPr'))
        if rPr_p is None:
            rPr_p = parse_xml(f'<w:rPr {nsdecls("w")}/>')
            pPr.append(rPr_p)

        # Update rPr_p
        rFonts_p = rPr_p.find(qn('w:rFonts'))
        if rFonts_p is None:
            rFonts_p = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>')
            rPr_p.append(rFonts_p)
        else:
            rFonts_p.set(qn('w:ascii'), 'Times New Roman')
            rFonts_p.set(qn('w:hAnsi'), 'Times New Roman')
            rFonts_p.set(qn('w:cs'), 'Times New Roman')

        sz_p = rPr_p.find(qn('w:sz'))
        if sz_p is None:
            sz_p = parse_xml(f'<w:sz {nsdecls("w")} w:val="{target_sz}"/>')
            rPr_p.append(sz_p)
        else:
            sz_p.set(qn('w:val'), target_sz)

        szCs_p = rPr_p.find(qn('w:szCs'))
        if szCs_p is None:
            szCs_p = parse_xml(f'<w:szCs {nsdecls("w")} w:val="{target_sz}"/>')
            rPr_p.append(szCs_p)
        else:
            szCs_p.set(qn('w:val'), target_sz)

        # Apply to each run
        for r in p.runs:
            rPr = r._r.get_or_add_rPr()
            rFonts = rPr.find(qn('w:rFonts'))
            if rFonts is None:
                rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>')
                rPr.append(rFonts)
            else:
                rFonts.set(qn('w:ascii'), 'Times New Roman')
                rFonts.set(qn('w:hAnsi'), 'Times New Roman')
                rFonts.set(qn('w:cs'), 'Times New Roman')

            sz = rPr.find(qn('w:sz'))
            if sz is None:
                sz = parse_xml(f'<w:sz {nsdecls("w")} w:val="{target_sz}"/>')
                rPr.append(sz)
            else:
                sz.set(qn('w:val'), target_sz)

            szCs = rPr.find(qn('w:szCs'))
            if szCs is None:
                szCs = parse_xml(f'<w:szCs {nsdecls("w")} w:val="{target_sz}"/>')
                rPr.append(szCs)
            else:
                szCs.set(qn('w:val'), target_sz)

            if target_bold is True:
                if rPr.find(qn('w:b')) is None:
                    rPr.append(parse_xml(f'<w:b {nsdecls("w")}/>'))
                if rPr.find(qn('w:bCs')) is None:
                    rPr.append(parse_xml(f'<w:bCs {nsdecls("w")}/>'))
            elif target_bold is False:
                b = rPr.find(qn('w:b'))
                if b is not None:
                    rPr.remove(b)
                bCs = rPr.find(qn('w:bCs'))
                if bCs is not None:
                    rPr.remove(bCs)

            if target_italic is True:
                if rPr.find(qn('w:i')) is None:
                    rPr.append(parse_xml(f'<w:i {nsdecls("w")}/>'))
                if rPr.find(qn('w:iCs')) is None:
                    rPr.append(parse_xml(f'<w:iCs {nsdecls("w")}/>'))
            elif target_italic is False:
                i_el = rPr.find(qn('w:i'))
                if i_el is not None:
                    rPr.remove(i_el)
                iCs_el = rPr.find(qn('w:iCs'))
                if iCs_el is not None:
                    rPr.remove(iCs_el)

    # Format all Table cells (Tables 0, 1, 3..15) with 13pt Times New Roman
    print("6. Formatting all other tables to 13pt Times New Roman...")
    for t_idx, table in enumerate(doc.tables):
        if t_idx == 2:
            continue  # Table 2 already cleanly formatted
        for row_idx, row in enumerate(table.rows):
            is_hdr = (row_idx == 0)
            for cell in row.cells:
                for p in cell.paragraphs:
                    pPr = p._p.get_or_add_pPr()
                    rPr_p = pPr.find(qn('w:rPr'))
                    if rPr_p is None:
                        rPr_p = parse_xml(f'<w:rPr {nsdecls("w")}/>')
                        pPr.append(rPr_p)
                    # set 13pt
                    for sz_tag in ['w:sz', 'w:szCs']:
                        el = rPr_p.find(qn(sz_tag))
                        if el is None:
                            rPr_p.append(parse_xml(f'<{sz_tag} {nsdecls("w")} w:val="26"/>'))
                        else:
                            el.set(qn('w:val'), '26')

                    for r in p.runs:
                        rPr = r._r.get_or_add_rPr()
                        rFonts = rPr.find(qn('w:rFonts'))
                        if rFonts is None:
                            rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>')
                            rPr.append(rFonts)
                        else:
                            rFonts.set(qn('w:ascii'), 'Times New Roman')
                            rFonts.set(qn('w:hAnsi'), 'Times New Roman')
                            rFonts.set(qn('w:cs'), 'Times New Roman')

                        for sz_tag in ['w:sz', 'w:szCs']:
                            el = rPr.find(qn(sz_tag))
                            if el is None:
                                rPr.append(parse_xml(f'<{sz_tag} {nsdecls("w")} w:val="26"/>'))
                            else:
                                el.set(qn('w:val'), '26')

    # Update styles in styles.xml
    print("7. Updating style defaults in doc.styles...")
    for s in doc.styles:
        if s.name in ['Title', 'Heading 1']:
            s.font.size = docx.shared.Pt(15)
            s.font.name = 'Times New Roman'
            s.font.bold = True
        elif s.name in ['Heading 2', 'Heading 3']:
            s.font.size = docx.shared.Pt(14)
            s.font.name = 'Times New Roman'
            s.font.bold = True
        elif s.name in ['Normal', 'List Paragraph', 'ct table']:
            s.font.size = docx.shared.Pt(13)
            s.font.name = 'Times New Roman'
        elif s.name in ['Caption', 'table of figures']:
            s.font.size = docx.shared.Pt(12)
            s.font.name = 'Times New Roman'

    print(f"Saving updated document: {DOCX_FILE}...")
    doc.save(DOCX_FILE)
    print("Document saved successfully!")

    # =========================================================================
    # STEP 5: UPDATE word/numbering.xml FOR CHAPTER PREFIX (CHƯƠNG %1:)
    # =========================================================================
    print("8. Updating word/numbering.xml to use 'CHƯƠNG %1: '...")
    update_numbering_prefix(DOCX_FILE)
    print("COMPLETE: All formatting and abbreviations updated successfully!")

def update_numbering_prefix(docx_path):
    """Updates numbering.xml inside docx to ensure Heading 1 displays 'CHƯƠNG %1: '."""
    tmp_dir = 'tmp_docx_zip'
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    with zipfile.ZipFile(docx_path, 'r') as zin:
        zin.extractall(tmp_dir)

    num_path = os.path.join(tmp_dir, 'word', 'numbering.xml')
    if os.path.exists(num_path):
        with open(num_path, 'r', encoding='utf-8') as f:
            xml_str = f.read()

        # Update lvl 0 lvlText from 'CHƯƠNG %1' to 'CHƯƠNG %1: '
        if 'w:val="CHƯƠNG %1"' in xml_str:
            xml_str = xml_str.replace('w:val="CHƯƠNG %1"', 'w:val="CHƯƠNG %1: "')
            print("  Updated lvlText to 'CHƯƠNG %1: ' in numbering.xml")

        # Also ensure suff is space so colon has space
        with open(num_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)

        # Repackage zip
        with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for root, dirs, files in os.walk(tmp_dir):
                for file in files:
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, tmp_dir)
                    zout.write(full_p, rel_p)

    shutil.rmtree(tmp_dir, ignore_errors=True)
    print("  Repackaged docx with updated numbering.xml")

if __name__ == '__main__':
    main()
