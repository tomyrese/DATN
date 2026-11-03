import os, sys, zipfile, re, shutil
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

DOCX_IN = 'PL2_Robot_TuHanh_Pi44.docx'
DOCX_OUT = 'PL2_Robot_TuHanh_Pi44.docx'
TEMP_DIR = 'temp_docx_extract'

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
ET.register_namespace('w', W_NS)
ET.register_namespace('r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
ET.register_namespace('m', 'http://schemas.openxmlformats.org/officeDocument/2006/math')
ET.register_namespace('v', 'urn:schemas-microsoft-com:vml')
ET.register_namespace('wp', 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing')
ET.register_namespace('w14', 'http://schemas.microsoft.com/office/word/2010/wordml')
ET.register_namespace('w15', 'http://schemas.microsoft.com/office/word/2012/wordml')

def qn(tag):
    return f"{{{W_NS}}}{tag}"

print("Extracting docx...")
if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)
os.makedirs(TEMP_DIR)

with zipfile.ZipFile(DOCX_IN, 'r') as z:
    z.extractall(TEMP_DIR)

doc_xml_path = os.path.join(TEMP_DIR, 'word', 'document.xml')
tree = ET.parse(doc_xml_path)
root = tree.getroot()
body = root.find(qn('body'))

print("Step 1: Setting page margins to 2.0cm, 2.0cm, 3.0cm, 2.0cm...")
# 2.0cm = 1134 dxa, 3.0cm = 1701 dxa
for sectPr in body.iter(qn('sectPr')):
    pgMar = sectPr.find(qn('pgMar'))
    if pgMar is not None:
        pgMar.set(qn('top'), '1134')      # 2.0 cm
        pgMar.set(qn('bottom'), '1134')   # 2.0 cm
        pgMar.set(qn('left'), '1701')     # 3.0 cm (gáy đóng sách)
        pgMar.set(qn('right'), '1134')    # 2.0 cm
        pgMar.set(qn('header'), '709')
        pgMar.set(qn('footer'), '709')
        pgMar.set(qn('gutter'), '0')
    pgSz = sectPr.find(qn('pgSz'))
    if pgSz is not None:
        pgSz.set(qn('w'), '11906')        # A4 width: 21.0 cm
        pgSz.set(qn('h'), '16838')        # A4 height: 29.7 cm

print("Step 2: Removing old _Toc bookmarks...")
# Remove old bookmarkStart and bookmarkEnd
for p in body.iter(qn('p')):
    for bm in list(p.findall(qn('bookmarkStart'))):
        p.remove(bm)
    for bm in list(p.findall(qn('bookmarkEnd'))):
        p.remove(bm)

# Also remove any standalone bookmarkEnd directly under body
for bm in list(body.findall(qn('bookmarkEnd'))):
    body.remove(bm)

print("Step 3: Defining complete TOC mapping with unique bookmarks...")

toc_items = [
    # (Level, Title, Page, BookmarkName, BodyPattern, ExactStyle)
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

print("Step 4: Updating References section in body...")
# Find TÀI LIỆU THAM KHẢO and replace existing list paragraphs with structured VN & EN sections
all_body_paras = list(body.findall(qn('p')))
ref_title_p = None
ref_title_idx = -1
for i, p in enumerate(all_body_paras):
    texts = ''.join([t.text for t in p.findall(f'.//{qn("t")}') if t.text])
    if re.search(r'^TÀI\s+LIỆU\s+THAM\s+KHẢO', texts.strip()):
        ref_title_p = p
        ref_title_idx = i
        break

print(f"Found TÀI LIỆU THAM KHẢO at index {ref_title_idx}")

# Vietnamese references
vn_refs = [
    "[1] TS. Nguyễn Văn Thái, Giáo trình Kỹ thuật Robot, Nhà xuất bản Khoa học và Kỹ thuật, Hà Nội, 2020.",
    "[2] PGS. TS. Nguyễn Đức Thành, Hệ thống nhúng và ứng dụng máy tính đơn bộc Linux, Nhà xuất bản Thông tin và Truyền thông, Hà Nội, 2021.",
    "[3] ThS. Lê Lý Quyên Quyên, Tài liệu hướng dẫn Đề cương Khóa luận tốt nghiệp chuyên ngành Công nghệ Kỹ thuật Máy tính, Khoa Công nghệ Điện tử, Trường Đại học Công nghiệp TP. Hồ Chí Minh, 2026.",
    "[4] PGS. TS. Đỗ Năng Toàn, TS. Phạm Việt Bình, Giáo trình Xử lý ảnh và Thị giác máy tính, Nhà xuất bản Đại học Quốc gia Hà Nội, 2018.",
    "[5] TS. Trần Thu Hà, Thiết kế mạch in và ứng dụng phần mềm EDA trong phát triển phần cứng điện tử, Nhà xuất bản Giáo dục Việt Nam, 2022.",
    "[6] Bộ môn Kỹ thuật Máy tính, Sổ tay tra cứu linh kiện phần cứng và các chuẩn giao tiếp công nghiệp, Trường Đại học Công nghiệp TP. Hồ Chí Minh, 2023."
]

# English references
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

# Helper to build a clean paragraph XML
def make_para(style_name, text, space_before=60, space_after=60, line=312, sz=26, b=False, i=False, align="both", indent_left=0, indent_hanging=0, indent_first=0):
    p = ET.Element(qn('p'))
    pPr = ET.SubElement(p, qn('pPr'))
    if style_name:
        pStyle = ET.SubElement(pPr, qn('pStyle'))
        pStyle.set(qn('val'), style_name)
    if align != "left":
        jc = ET.SubElement(pPr, qn('jc'))
        jc.set(qn('val'), align)
    spacing = ET.SubElement(pPr, qn('spacing'))
    spacing.set(qn('before'), str(space_before))
    spacing.set(qn('after'), str(space_after))
    spacing.set(qn('line'), str(line))
    spacing.set(qn('lineRule'), 'auto')
    
    if indent_left > 0 or indent_hanging > 0 or indent_first > 0:
        ind = ET.SubElement(pPr, qn('ind'))
        if indent_left > 0:
            ind.set(qn('left'), str(indent_left))
        if indent_hanging > 0:
            ind.set(qn('hanging'), str(indent_hanging))
        if indent_first > 0:
            ind.set(qn('firstLine'), str(indent_first))
            
    rPr_p = ET.SubElement(pPr, qn('rPr'))
    rFonts_p = ET.SubElement(rPr_p, qn('rFonts'))
    rFonts_p.set(qn('ascii'), 'Times New Roman')
    rFonts_p.set(qn('hAnsi'), 'Times New Roman')
    rFonts_p.set(qn('cs'), 'Times New Roman')
    if b:
        ET.SubElement(rPr_p, qn('b'))
        ET.SubElement(rPr_p, qn('bCs'))
    if i:
        ET.SubElement(rPr_p, qn('i'))
        ET.SubElement(rPr_p, qn('iCs'))
    sz_p = ET.SubElement(rPr_p, qn('sz'))
    sz_p.set(qn('val'), str(sz))
    szCs_p = ET.SubElement(rPr_p, qn('szCs'))
    szCs_p.set(qn('val'), str(sz))

    r = ET.SubElement(p, qn('r'))
    rPr = ET.SubElement(r, qn('rPr'))
    rFonts = ET.SubElement(rPr, qn('rFonts'))
    rFonts.set(qn('ascii'), 'Times New Roman')
    rFonts.set(qn('hAnsi'), 'Times New Roman')
    rFonts.set(qn('cs'), 'Times New Roman')
    if b:
        ET.SubElement(rPr, qn('b'))
        ET.SubElement(rPr, qn('bCs'))
    if i:
        ET.SubElement(rPr, qn('i'))
        ET.SubElement(rPr, qn('iCs'))
    sz_el = ET.SubElement(rPr, qn('sz'))
    sz_el.set(qn('val'), str(sz))
    szCs_el = ET.SubElement(rPr, qn('szCs'))
    szCs_el.set(qn('val'), str(sz))
    t = ET.SubElement(r, qn('t'))
    t.text = text
    return p

# Find index of PHỤ LỤC
phu_luc_idx = -1
for i, p in enumerate(all_body_paras):
    texts = ''.join([t.text for t in p.findall(f'.//{qn("t")}') if t.text])
    if re.search(r'^PHỤ\s+LỤC', texts.strip()):
        phu_luc_idx = i
        break

print(f"Found PHỤ LỤC at index {phu_luc_idx}")

# Remove old paragraphs between TÀI LIỆU THAM KHẢO and PHỤ LỤC
if ref_title_idx != -1 and phu_luc_idx > ref_title_idx:
    old_paras_to_remove = all_body_paras[ref_title_idx+1:phu_luc_idx]
    for p in old_paras_to_remove:
        body.remove(p)

# Insert the clean structured references after ref_title_p
insert_pos = list(body).index(ref_title_p) + 1

# Subheading 1: Tiếng Việt
p_vn_head = make_para("Heading2", "1. Tài liệu tham khảo tiếng Việt", space_before=160, space_after=80, sz=28, b=True, align="left")
body.insert(insert_pos, p_vn_head)
insert_pos += 1

for ref in vn_refs:
    p_ref = make_para("Normal", ref, space_before=40, space_after=80, line=312, sz=26, align="both", indent_left=567, indent_hanging=567)
    body.insert(insert_pos, p_ref)
    insert_pos += 1

# Subheading 2: Tiếng Anh
p_en_head = make_para("Heading2", "2. Tài liệu tham khảo tiếng Anh", space_before=240, space_after=80, sz=28, b=True, align="left")
body.insert(insert_pos, p_en_head)
insert_pos += 1

for ref in en_refs:
    p_ref = make_para("Normal", ref, space_before=40, space_after=80, line=312, sz=26, align="both", indent_left=567, indent_hanging=567)
    body.insert(insert_pos, p_ref)
    insert_pos += 1

print("Step 5: Inserting Bookmarks into all target paragraphs in body...")
# Re-fetch body paragraphs after references insertion
all_body_paras = list(body.findall(qn('p')))

bm_id_counter = 1000

# Function to add bookmark to paragraph
def add_bookmark(p, bm_name, bm_id):
    bm_start = ET.Element(qn('bookmarkStart'))
    bm_start.set(qn('id'), str(bm_id))
    bm_start.set(qn('name'), bm_name)
    bm_end = ET.Element(qn('bookmarkEnd'))
    bm_end.set(qn('id'), str(bm_id))
    
    # insert bookmarkStart right after pPr if exists, else at index 0
    pPr = p.find(qn('pPr'))
    if pPr is not None:
        idx = list(p).index(pPr) + 1
    else:
        idx = 0
    p.insert(idx, bm_start)
    p.append(bm_end)

# Match TOC items to body paragraphs
matched_toc = set()
for item in toc_items:
    level, title, page, bm_name, pattern, style = item
    # search in body paragraphs
    for p in all_body_paras:
        texts = ''.join([t.text for t in p.findall(f'.//{qn("t")}') if t.text]).strip()
        if not texts:
            continue
        if re.search(pattern, texts, re.IGNORECASE):
            add_bookmark(p, bm_name, bm_id_counter)
            bm_id_counter += 1
            matched_toc.add(bm_name)
            # Ensure proper Heading style if needed
            pPr = p.find(qn('pPr'))
            if pPr is not None:
                pStyle = pPr.find(qn('pStyle'))
                if pStyle is not None and style:
                    pStyle.set(qn('val'), style)
            break

print(f"Matched {len(matched_toc)} / {len(toc_items)} TOC items to body paragraphs.")
unmatched = [item[1] for item in toc_items if item[3] not in matched_toc]
if unmatched:
    print(f"  Unmatched TOC items: {unmatched}")

# Match Figures to body paragraphs
matched_figs = set()
for item in figures_items:
    fig_title, page, bm_name, pattern = item
    for p in all_body_paras:
        texts = ''.join([t.text for t in p.findall(f'.//{qn("t")}') if t.text]).strip()
        if not texts:
            continue
        if re.search(pattern, texts, re.IGNORECASE):
            add_bookmark(p, bm_name, bm_id_counter)
            bm_id_counter += 1
            matched_figs.add(bm_name)
            break

print(f"Matched {len(matched_figs)} / {len(figures_items)} figures to body paragraphs.")

# Match Tables to body paragraphs
matched_tabs = set()
for item in tables_items:
    tab_title, page, bm_name, pattern = item
    for p in all_body_paras:
        texts = ''.join([t.text for t in p.findall(f'.//{qn("t")}') if t.text]).strip()
        if not texts:
            continue
        if re.search(pattern, texts, re.IGNORECASE):
            add_bookmark(p, bm_name, bm_id_counter)
            bm_id_counter += 1
            matched_tabs.add(bm_name)
            break

print(f"Matched {len(matched_tabs)} / {len(tables_items)} tables to body paragraphs.")

print("Step 6: Rebuilding Table of Contents (<w:sdt>) with Ctrl+Click Hyperlinks...")
sdt = body.find(f'.//{qn("sdt")}')
if sdt is not None:
    sdtContent = sdt.find(qn('sdtContent'))
    if sdtContent is not None:
        # Clear existing children in sdtContent
        for child in list(sdtContent):
            sdtContent.remove(child)
        
        # Add Title: MỤC LỤC
        p_toc_title = make_para("Title", "MỤC LỤC", space_before=240, space_after=240, sz=30, b=True, align="center")
        sdtContent.append(p_toc_title)
        
        # Add hyperlinked entries
        for item in toc_items:
            level, title, page, bm_name, pattern, style = item
            toc_style = f"TOC{level}"
            sz_val = 28 if level == 1 else 26
            b_val = True if level == 1 else False
            sp_before = 40 if level == 1 else 20
            sp_after = 40 if level == 1 else 20
            
            p_entry = ET.Element(qn('p'))
            pPr = ET.SubElement(p_entry, qn('pPr'))
            pStyle = ET.SubElement(pPr, qn('pStyle'))
            pStyle.set(qn('val'), toc_style)
            
            tabs = ET.SubElement(pPr, qn('tabs'))
            tab = ET.SubElement(tabs, qn('tab'))
            tab.set(qn('val'), 'right')
            tab.set(qn('leader'), 'dot')
            tab.set(qn('pos'), '9071') # 16.0cm
            
            spacing = ET.SubElement(pPr, qn('spacing'))
            spacing.set(qn('before'), str(sp_before))
            spacing.set(qn('after'), str(sp_after))
            spacing.set(qn('line'), '260')
            spacing.set(qn('lineRule'), 'auto')
            
            rPr_p = ET.SubElement(pPr, qn('rPr'))
            rFonts_p = ET.SubElement(rPr_p, qn('rFonts'))
            rFonts_p.set(qn('ascii'), 'Times New Roman')
            rFonts_p.set(qn('hAnsi'), 'Times New Roman')
            rFonts_p.set(qn('cs'), 'Times New Roman')
            if b_val:
                ET.SubElement(rPr_p, qn('b'))
                ET.SubElement(rPr_p, qn('bCs'))
            sz_el = ET.SubElement(rPr_p, qn('sz'))
            sz_el.set(qn('val'), str(sz_val))
            szCs_el = ET.SubElement(rPr_p, qn('szCs'))
            szCs_el.set(qn('val'), str(sz_val))

            # Hyperlink element
            hl = ET.SubElement(p_entry, qn('hyperlink'))
            hl.set(qn('anchor'), bm_name)
            hl.set(qn('history'), '1')
            
            # Run 1: Title text
            r1 = ET.SubElement(hl, qn('r'))
            r1Pr = ET.SubElement(r1, qn('rPr'))
            rf1 = ET.SubElement(r1Pr, qn('rFonts'))
            rf1.set(qn('ascii'), 'Times New Roman')
            rf1.set(qn('hAnsi'), 'Times New Roman')
            rf1.set(qn('cs'), 'Times New Roman')
            c1 = ET.SubElement(r1Pr, qn('color'))
            c1.set(qn('val'), '000000')
            u1 = ET.SubElement(r1Pr, qn('u'))
            u1.set(qn('val'), 'none')
            if b_val:
                ET.SubElement(r1Pr, qn('b'))
                ET.SubElement(r1Pr, qn('bCs'))
            sz1 = ET.SubElement(r1Pr, qn('sz'))
            sz1.set(qn('val'), str(sz_val))
            sz1Cs = ET.SubElement(r1Pr, qn('szCs'))
            sz1Cs.set(qn('val'), str(sz_val))
            t1 = ET.SubElement(r1, qn('t'))
            t1.text = title
            
            # Run 2: Tab
            r2 = ET.SubElement(hl, qn('r'))
            r2Pr = ET.SubElement(r2, qn('rPr'))
            rf2 = ET.SubElement(r2Pr, qn('rFonts'))
            rf2.set(qn('ascii'), 'Times New Roman')
            rf2.set(qn('hAnsi'), 'Times New Roman')
            sz2 = ET.SubElement(r2Pr, qn('sz'))
            sz2.set(qn('val'), str(sz_val))
            ET.SubElement(r2, qn('tab'))
            
            # Run 3: Page Number with PAGEREF
            fld = ET.SubElement(hl, qn('fldSimple'))
            fld.set(qn('instr'), f'PAGEREF {bm_name} \\h')
            r3 = ET.SubElement(fld, qn('r'))
            r3Pr = ET.SubElement(r3, qn('rPr'))
            rf3 = ET.SubElement(r3Pr, qn('rFonts'))
            rf3.set(qn('ascii'), 'Times New Roman')
            rf3.set(qn('hAnsi'), 'Times New Roman')
            rf3.set(qn('cs'), 'Times New Roman')
            c3 = ET.SubElement(r3Pr, qn('color'))
            c3.set(qn('val'), '000000')
            u3 = ET.SubElement(r3Pr, qn('u'))
            u3.set(qn('val'), 'none')
            if b_val:
                ET.SubElement(r3Pr, qn('b'))
                ET.SubElement(r3Pr, qn('bCs'))
            sz3 = ET.SubElement(r3Pr, qn('sz'))
            sz3.set(qn('val'), str(sz_val))
            sz3Cs = ET.SubElement(r3Pr, qn('szCs'))
            sz3Cs.set(qn('val'), str(sz_val))
            t3 = ET.SubElement(r3, qn('t'))
            t3.text = page

            sdtContent.append(p_entry)

print("Step 7: Rebuilding DANH MỤC HÌNH ẢNH with Ctrl+Click Hyperlinks...")
# Find DANH MỤC HÌNH ẢNH in body
all_body_paras = list(body.findall(qn('p')))
fig_list_head_idx = -1
for i, p in enumerate(all_body_paras):
    texts = ''.join([t.text for t in p.findall(f'.//{qn("t")}') if t.text]).strip()
    if texts == "DANH MỤC HÌNH ẢNH":
        fig_list_head_idx = i
        break

table_list_head_idx = -1
for i, p in enumerate(all_body_paras):
    texts = ''.join([t.text for t in p.findall(f'.//{qn("t")}') if t.text]).strip()
    if texts == "DANH MỤC BẢNG BIỂU":
        table_list_head_idx = i
        break

print(f"DANH MỤC HÌNH ẢNH at {fig_list_head_idx}, DANH MỤC BẢNG BIỂU at {table_list_head_idx}")

if fig_list_head_idx != -1 and table_list_head_idx > fig_list_head_idx:
    # remove old figure list paragraphs
    old_fig_paras = all_body_paras[fig_list_head_idx+1:table_list_head_idx]
    for p in old_fig_paras:
        body.remove(p)
    
    # insert new hyperlinked figure entries
    cur_pos = list(body).index(all_body_paras[fig_list_head_idx]) + 1
    for fig_title, page, bm_name, pattern in figures_items:
        p_entry = ET.Element(qn('p'))
        pPr = ET.SubElement(p_entry, qn('pPr'))
        pStyle = ET.SubElement(pPr, qn('pStyle'))
        pStyle.set(qn('val'), 'TableofFigures')
        tabs = ET.SubElement(pPr, qn('tabs'))
        tab = ET.SubElement(tabs, qn('tab'))
        tab.set(qn('val'), 'right')
        tab.set(qn('leader'), 'dot')
        tab.set(qn('pos'), '9071')
        spacing = ET.SubElement(pPr, qn('spacing'))
        spacing.set(qn('before'), '20')
        spacing.set(qn('after'), '20')
        spacing.set(qn('line'), '260')
        spacing.set(qn('lineRule'), 'auto')
        
        hl = ET.SubElement(p_entry, qn('hyperlink'))
        hl.set(qn('anchor'), bm_name)
        hl.set(qn('history'), '1')
        
        r1 = ET.SubElement(hl, qn('r'))
        r1Pr = ET.SubElement(r1, qn('rPr'))
        rf1 = ET.SubElement(r1Pr, qn('rFonts'))
        rf1.set(qn('ascii'), 'Times New Roman')
        rf1.set(qn('hAnsi'), 'Times New Roman')
        c1 = ET.SubElement(r1Pr, qn('color'))
        c1.set(qn('val'), '000000')
        u1 = ET.SubElement(r1Pr, qn('u'))
        u1.set(qn('val'), 'none')
        sz1 = ET.SubElement(r1Pr, qn('sz'))
        sz1.set(qn('val'), '26')
        t1 = ET.SubElement(r1, qn('t'))
        t1.text = fig_title
        
        r2 = ET.SubElement(hl, qn('r'))
        ET.SubElement(r2, qn('tab'))
        
        fld = ET.SubElement(hl, qn('fldSimple'))
        fld.set(qn('instr'), f'PAGEREF {bm_name} \\h')
        r3 = ET.SubElement(fld, qn('r'))
        r3Pr = ET.SubElement(r3, qn('rPr'))
        rf3 = ET.SubElement(r3Pr, qn('rFonts'))
        rf3.set(qn('ascii'), 'Times New Roman')
        rf3.set(qn('hAnsi'), 'Times New Roman')
        c3 = ET.SubElement(r3Pr, qn('color'))
        c3.set(qn('val'), '000000')
        u3 = ET.SubElement(r3Pr, qn('u'))
        u3.set(qn('val'), 'none')
        sz3 = ET.SubElement(r3Pr, qn('sz'))
        sz3.set(qn('val'), '26')
        t3 = ET.SubElement(r3, qn('t'))
        t3.text = page
        
        body.insert(cur_pos, p_entry)
        cur_pos += 1

print("Step 8: Rebuilding DANH MỤC BẢNG BIỂU with Ctrl+Click Hyperlinks...")
all_body_paras = list(body.findall(qn('p')))
table_list_head_idx = -1
for i, p in enumerate(all_body_paras):
    texts = ''.join([t.text for t in p.findall(f'.//{qn("t")}') if t.text]).strip()
    if texts == "DANH MỤC BẢNG BIỂU":
        table_list_head_idx = i
        break

abbrev_list_head_idx = -1
for i, p in enumerate(all_body_paras):
    texts = ''.join([t.text for t in p.findall(f'.//{qn("t")}') if t.text]).strip()
    if texts == "DANH MỤC TỪ VIẾT TẮT":
        abbrev_list_head_idx = i
        break

print(f"DANH MỤC BẢNG BIỂU at {table_list_head_idx}, DANH MỤC TỪ VIẾT TẮT at {abbrev_list_head_idx}")

if table_list_head_idx != -1 and abbrev_list_head_idx > table_list_head_idx:
    old_tab_paras = all_body_paras[table_list_head_idx+1:abbrev_list_head_idx]
    for p in old_tab_paras:
        body.remove(p)
        
    cur_pos = list(body).index(all_body_paras[table_list_head_idx]) + 1
    for tab_title, page, bm_name, pattern in tables_items:
        p_entry = ET.Element(qn('p'))
        pPr = ET.SubElement(p_entry, qn('pPr'))
        pStyle = ET.SubElement(pPr, qn('pStyle'))
        pStyle.set(qn('val'), 'TableofFigures')
        tabs = ET.SubElement(pPr, qn('tabs'))
        tab = ET.SubElement(tabs, qn('tab'))
        tab.set(qn('val'), 'right')
        tab.set(qn('leader'), 'dot')
        tab.set(qn('pos'), '9071')
        spacing = ET.SubElement(pPr, qn('spacing'))
        spacing.set(qn('before'), '20')
        spacing.set(qn('after'), '20')
        spacing.set(qn('line'), '260')
        spacing.set(qn('lineRule'), 'auto')
        
        hl = ET.SubElement(p_entry, qn('hyperlink'))
        hl.set(qn('anchor'), bm_name)
        hl.set(qn('history'), '1')
        
        r1 = ET.SubElement(hl, qn('r'))
        r1Pr = ET.SubElement(r1, qn('rPr'))
        rf1 = ET.SubElement(r1Pr, qn('rFonts'))
        rf1.set(qn('ascii'), 'Times New Roman')
        rf1.set(qn('hAnsi'), 'Times New Roman')
        c1 = ET.SubElement(r1Pr, qn('color'))
        c1.set(qn('val'), '000000')
        u1 = ET.SubElement(r1Pr, qn('u'))
        u1.set(qn('val'), 'none')
        sz1 = ET.SubElement(r1Pr, qn('sz'))
        sz1.set(qn('val'), '26')
        t1 = ET.SubElement(r1, qn('t'))
        t1.text = tab_title
        
        r2 = ET.SubElement(hl, qn('r'))
        ET.SubElement(r2, qn('tab'))
        
        fld = ET.SubElement(hl, qn('fldSimple'))
        fld.set(qn('instr'), f'PAGEREF {bm_name} \\h')
        r3 = ET.SubElement(fld, qn('r'))
        r3Pr = ET.SubElement(r3, qn('rPr'))
        rf3 = ET.SubElement(r3Pr, qn('rFonts'))
        rf3.set(qn('ascii'), 'Times New Roman')
        rf3.set(qn('hAnsi'), 'Times New Roman')
        c3 = ET.SubElement(r3Pr, qn('color'))
        c3.set(qn('val'), '000000')
        u3 = ET.SubElement(r3Pr, qn('u'))
        u3.set(qn('val'), 'none')
        sz3 = ET.SubElement(r3Pr, qn('sz'))
        sz3.set(qn('val'), '26')
        t3 = ET.SubElement(r3, qn('t'))
        t3.text = page
        
        body.insert(cur_pos, p_entry)
        cur_pos += 1

print("Step 9: Enforcing Times New Roman font and thesis styles across all runs...")
for r in body.iter(qn('r')):
    rPr = r.find(qn('rPr'))
    if rPr is not None:
        rFonts = rPr.find(qn('rFonts'))
        if rFonts is not None:
            rFonts.set(qn('ascii'), 'Times New Roman')
            rFonts.set(qn('hAnsi'), 'Times New Roman')
            rFonts.set(qn('cs'), 'Times New Roman')
            rFonts.set(qn('eastAsia'), 'Times New Roman')

# Save modified XML
tree.write(doc_xml_path, xml_declaration=True, encoding='utf-8')
print("Wrote modified document.xml successfully!")

# Re-pack docx
print("Repacking docx...")
with zipfile.ZipFile(DOCX_OUT, 'w', zipfile.ZIP_DEFLATED) as z_out:
    for foldername, subfolders, filenames in os.walk(TEMP_DIR):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            arcname = os.path.relpath(file_path, TEMP_DIR)
            z_out.write(file_path, arcname)

print("PL2_Robot_TuHanh_Pi44.docx updated successfully!")

