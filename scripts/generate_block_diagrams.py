import os
import fitz

os.makedirs('extracted_imgs/block_diagrams', exist_ok=True)

def render_svg_to_png(svg_str, output_path, dpi=300):
    doc = fitz.open(stream=svg_str.encode('utf-8'), filetype='svg')
    page = doc[0]
    pix = page.get_pixmap(dpi=dpi)
    pix.save(output_path)
    print(f"Rendered {output_path}: {pix.width} x {pix.height}")

# ==============================================================================
# 1. SLIDE 5: SƠ ĐỒ KHỐI TỔNG THỂ HỆ THỐNG ROBOT (OVERALL ARCHITECTURE)
# Tối giản, chỉ giữ các khối chức năng chính, loại bỏ mô tả rườm rà
# ==============================================================================
svg_slide5 = """<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="800" viewBox="0 0 1100 800">
  <defs>
    <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a73e8"/>
    </marker>
    <marker id="arr-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#d93025"/>
    </marker>
    <marker id="arr-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2b8a3e"/>
    </marker>
    <marker id="arr-orange" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#e8590c"/>
    </marker>
    <filter id="shadow" x="-4%" y="-4%" width="108%" height="108%">
      <feDropShadow dx="0" dy="3" stdDeviation="3" flood-opacity="0.10"/>
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff" rx="16" stroke="#cfd8dc" stroke-width="2"/>

  <!-- Diagram Title -->
  <rect x="30" y="20" width="1040" height="46" rx="8" fill="#0f2b48"/>
  <text x="550" y="51" font-family="Times New Roman" font-size="20" font-weight="bold" fill="#ffffff" text-anchor="middle" letter-spacing="1">
    SƠ ĐỒ KHỐI TỔNG THỂ HỆ THỐNG ROBOT TỰ HÀNH
  </text>

  <!-- ================= TOP: KHỐI NGUỒN ================= -->
  <g filter="url(#shadow)">
    <rect x="40" y="86" width="1020" height="96" rx="10" fill="#fff5f5" stroke="#d93025" stroke-width="2.5"/>
    <rect x="40" y="86" width="220" height="28" rx="8" fill="#d93025"/>
    <text x="150" y="105" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">KHỐI NGUỒN NĂNG LƯỢNG</text>
    
    <!-- Pin 12V -->
    <rect x="60" y="124" width="210" height="44" rx="6" fill="#ffffff" stroke="#e03131" stroke-width="1.5"/>
    <text x="165" y="151" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c92a2a" text-anchor="middle">Pin Li-ion 3S2P (12V)</text>

    <line x1="270" y1="146" x2="310" y2="146" stroke="#d93025" stroke-width="2.5" marker-end="url(#arr-red)"/>

    <!-- SW & Fuse -->
    <rect x="310" y="124" width="200" height="44" rx="6" fill="#ffffff" stroke="#e03131" stroke-width="1.5"/>
    <text x="410" y="151" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c92a2a" text-anchor="middle">Công tắc 10A &amp; Cầu chì 7.5A</text>

    <!-- Split Arrow -->
    <line x1="510" y1="146" x2="550" y2="146" stroke="#d93025" stroke-width="2.5" marker-end="url(#arr-red)"/>

    <!-- Buck -->
    <rect x="550" y="124" width="200" height="44" rx="6" fill="#ffffff" stroke="#e03131" stroke-width="1.5"/>
    <text x="650" y="151" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c92a2a" text-anchor="middle">Hạ Áp Buck (5V - 5A)</text>

    <!-- 2 Rails -->
    <rect x="780" y="124" width="260" height="20" rx="4" fill="#fa5252"/>
    <text x="910" y="139" font-family="Times New Roman" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">Ray Động Lực: 12V (Động cơ)</text>

    <rect x="780" y="148" width="260" height="20" rx="4" fill="#fd7e14"/>
    <text x="910" y="163" font-family="Times New Roman" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">Ray Điều Khiển: 5V - 5A (Pi 4 &amp; Cảm biến)</text>
  </g>

  <!-- ================= CENTER: RASPBERRY PI 4 ================= -->
  <g filter="url(#shadow)">
    <rect x="370" y="220" width="360" height="360" rx="12" fill="#e8f0fe" stroke="#1a73e8" stroke-width="3"/>
    <rect x="370" y="220" width="360" height="36" rx="10" fill="#1a73e8"/>
    <text x="550" y="244" font-family="Times New Roman" font-size="16" font-weight="bold" fill="#ffffff" text-anchor="middle">
      BỘ XỬ LÝ TRUNG TÂM (RASPBERRY PI 4)
    </text>

    <!-- Sub-blocks inside Pi 4 -->
    <rect x="395" y="275" width="310" height="56" rx="6" fill="#ffffff" stroke="#1a73e8" stroke-width="1.5"/>
    <text x="550" y="300" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#1864ab" text-anchor="middle">Thuật toán Điều hướng &amp; Né vật cản</text>
    <text x="550" y="318" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Xử lý khoảng cách siêu âm &amp; Bám vạch sàn</text>

    <rect x="395" y="345" width="310" height="56" rx="6" fill="#ffffff" stroke="#1a73e8" stroke-width="1.5"/>
    <text x="550" y="370" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#1864ab" text-anchor="middle">Điều khiển Động cơ (4 Kênh PWM)</text>
    <text x="550" y="388" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Chỉnh tốc độ, hướng quay &amp; Phanh dừng tức thời</text>

    <rect x="395" y="415" width="310" height="56" rx="6" fill="#ffffff" stroke="#1a73e8" stroke-width="1.5"/>
    <text x="550" y="440" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#1864ab" text-anchor="middle">Máy chủ Web Server &amp; REST API</text>
    <text x="550" y="458" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Xử lý lệnh di chuyển &amp; Nhận diện hình ảnh</text>

    <rect x="395" y="485" width="310" height="72" rx="6" fill="#1a73e8"/>
    <text x="550" y="512" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">Bo Mạch Kết Nối Trung Gian (Carrier)</text>
    <text x="550" y="534" font-family="Times New Roman" font-size="12" fill="#e8f0fe" text-anchor="middle">Cáp bẹ 40 chân cắm thẳng • Mạch in 1 lớp chống rung lắc</text>
  </g>

  <!-- ================= LEFT: CẢM BIẾN & THỊ GIÁC ================= -->
  <g filter="url(#shadow)">
    <rect x="40" y="220" width="270" height="360" rx="12" fill="#ebfbee" stroke="#2b8a3e" stroke-width="2.5"/>
    <rect x="40" y="220" width="270" height="34" rx="10" fill="#2b8a3e"/>
    <text x="175" y="243" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#ffffff" text-anchor="middle">CẢM BIẾN &amp; THỊ GIÁC</text>

    <!-- HC-SR04 -->
    <rect x="55" y="275" width="240" height="75" rx="6" fill="#ffffff" stroke="#40c057" stroke-width="1.5"/>
    <text x="175" y="303" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2b8a3e" text-anchor="middle">2x Cảm biến Siêu âm</text>
    <text x="175" y="325" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Phát hiện vật cản Trái / Phải</text>

    <!-- TCRT5000 -->
    <rect x="55" y="365" width="240" height="75" rx="6" fill="#ffffff" stroke="#40c057" stroke-width="1.5"/>
    <text x="175" y="393" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2b8a3e" text-anchor="middle">Cảm biến Dò Line (3 Mắt)</text>
    <text x="175" y="415" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Bám vạch dẫn đường trên sàn</text>

    <!-- Camera CSI -->
    <rect x="55" y="455" width="240" height="75" rx="6" fill="#ffffff" stroke="#40c057" stroke-width="1.5"/>
    <text x="175" y="483" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2b8a3e" text-anchor="middle">Camera Góc Rộng 5MP</text>
    <text x="175" y="505" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Truyền video thời gian thực</text>
  </g>

  <!-- Connectors Left to Pi4 -->
  <line x1="295" y1="312" x2="370" y2="312" stroke="#2b8a3e" stroke-width="2.5" marker-end="url(#arr-green)"/>
  <text x="332" y="305" font-family="Times New Roman" font-size="10.5" font-weight="bold" fill="#2b8a3e" text-anchor="middle">Trig/Echo</text>

  <line x1="295" y1="402" x2="370" y2="402" stroke="#2b8a3e" stroke-width="2.5" marker-end="url(#arr-green)"/>
  <text x="332" y="395" font-family="Times New Roman" font-size="10.5" font-weight="bold" fill="#2b8a3e" text-anchor="middle">3x Line</text>

  <line x1="295" y1="492" x2="370" y2="492" stroke="#2b8a3e" stroke-width="2.5" marker-end="url(#arr-green)"/>
  <text x="332" y="485" font-family="Times New Roman" font-size="10.5" font-weight="bold" fill="#2b8a3e" text-anchor="middle">Video</text>

  <!-- ================= RIGHT: CHẤP HÀNH & HIỂN THỊ ================= -->
  <g filter="url(#shadow)">
    <rect x="790" y="220" width="270" height="360" rx="12" fill="#fff9db" stroke="#f59f00" stroke-width="2.5"/>
    <rect x="790" y="220" width="270" height="34" rx="10" fill="#f59f00"/>
    <text x="925" y="243" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#ffffff" text-anchor="middle">CHẤP HÀNH &amp; HIỂN THỊ</text>

    <!-- OLED -->
    <rect x="805" y="275" width="240" height="75" rx="6" fill="#ffffff" stroke="#f59f00" stroke-width="1.5"/>
    <text x="925" y="303" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#d9480f" text-anchor="middle">Màn hình OLED 1.3" I2C</text>
    <text x="925" y="325" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Báo IP, Pin &amp; Trạng thái xe</text>

    <!-- TB6612 -->
    <rect x="805" y="365" width="240" height="75" rx="6" fill="#ffffff" stroke="#f59f00" stroke-width="1.5"/>
    <text x="925" y="393" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#d9480f" text-anchor="middle">2 Mạch Công Suất Động Cơ</text>
    <text x="925" y="415" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Hiệu suất cao, không sinh nhiệt</text>

    <!-- 4 DC Motors -->
    <rect x="805" y="455" width="240" height="75" rx="6" fill="#ffffff" stroke="#f59f00" stroke-width="1.5"/>
    <text x="925" y="483" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#d9480f" text-anchor="middle">4 Động Cơ DC Giảm Tốc (4WD)</text>
    <text x="925" y="505" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Dẫn động 4 bánh xe linh hoạt</text>
  </g>

  <!-- Connectors Pi4 to Right -->
  <line x1="730" y1="312" x2="805" y2="312" stroke="#702283" stroke-width="2.5" marker-end="url(#arr-blue)"/>
  <text x="765" y="305" font-family="Times New Roman" font-size="10.5" font-weight="bold" fill="#702283" text-anchor="middle">I2C Bus</text>

  <line x1="730" y1="402" x2="805" y2="402" stroke="#1a73e8" stroke-width="2.5" marker-end="url(#arr-blue)"/>
  <text x="765" y="395" font-family="Times New Roman" font-size="10.5" font-weight="bold" fill="#1a73e8" text-anchor="middle">PWM + DIR</text>

  <line x1="925" y1="440" x2="925" y2="455" stroke="#f59f00" stroke-width="2.5" marker-end="url(#arr-orange)"/>

  <!-- ================= BOTTOM: NỀN TẢNG DỊCH VỤ SỐ & AI ================= -->
  <g filter="url(#shadow)">
    <rect x="40" y="615" width="1020" height="150" rx="10" fill="#f8f9fa" stroke="#0f2b48" stroke-width="2"/>
    <rect x="40" y="615" width="1020" height="28" rx="8" fill="#0f2b48"/>
    <text x="550" y="634" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">
      GIAO TIẾP KHÔNG DÂY (WI-FI) &amp; NỀN TẢNG ĐIỀU KHIỂN
    </text>

    <!-- Card 1: Web -->
    <rect x="65" y="655" width="295" height="75" rx="6" fill="#ffffff" stroke="#adb5bd" stroke-width="1.2"/>
    <text x="212" y="683" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#1864ab" text-anchor="middle">Web Dashboard Cyber</text>
    <text x="212" y="705" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Điều khiển hướng &amp; Chỉnh tốc độ</text>

    <!-- Card 2: DB -->
    <rect x="402" y="655" width="295" height="75" rx="6" fill="#ffffff" stroke="#adb5bd" stroke-width="1.2"/>
    <text x="550" y="683" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#1864ab" text-anchor="middle">Quản Lý Đơn Giao Nhận</text>
    <text x="550" y="705" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Cơ sở dữ liệu lưu trữ lịch sử đơn</text>

    <!-- Card 3: AI -->
    <rect x="740" y="655" width="295" height="75" rx="6" fill="#ffffff" stroke="#adb5bd" stroke-width="1.2"/>
    <text x="887" y="683" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#1864ab" text-anchor="middle">Trợ Lý Ảo Thông Minh (AI)</text>
    <text x="887" y="705" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Hỏi đáp &amp; Chỉ dẫn khách mua sắm</text>
  </g>
</svg>"""

render_svg_to_png(svg_slide5, 'extracted_imgs/block_diagrams/block_diagram_slide5_overall.png', dpi=300)

# ==============================================================================
# 2. SLIDE 9: KHỐI 1 - NGUỒN ĐIỆN (POWER SUBSYSTEM)
# Loại bỏ bảng chú thích mass rườm rà, tập trung luồng phân phối năng lượng
# ==============================================================================
svg_slide9 = """<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="650" viewBox="0 0 1000 650">
  <defs>
    <marker id="arr-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#d93025"/>
    </marker>
    <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a73e8"/>
    </marker>
    <filter id="shadow" x="-4%" y="-4%" width="108%" height="108%">
      <feDropShadow dx="0" dy="3" stdDeviation="3" flood-opacity="0.10"/>
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff" rx="14" stroke="#cfd8dc" stroke-width="2"/>

  <!-- Title Banner -->
  <rect x="25" y="20" width="950" height="44" rx="8" fill="#d93025"/>
  <text x="500" y="49" font-family="Times New Roman" font-size="19" font-weight="bold" fill="#ffffff" text-anchor="middle">
    SƠ ĐỒ KHỐI CHỨC NĂNG: KHỐI 1 - NGUỒN ĐIỆN
  </text>

  <!-- Block 1: Pin 12V -->
  <g filter="url(#shadow)">
    <rect x="40" y="110" width="240" height="110" rx="8" fill="#fff5f5" stroke="#d93025" stroke-width="2.5"/>
    <rect x="40" y="110" width="240" height="28" rx="6" fill="#d93025"/>
    <text x="160" y="130" font-family="Times New Roman" font-size="13.5" font-weight="bold" fill="#ffffff" text-anchor="middle">NGUỒN CẤP CHÍNH</text>
    <text x="160" y="165" font-family="Times New Roman" font-size="16" font-weight="bold" fill="#c92a2a" text-anchor="middle">Pin Li-ion 3S2P</text>
    <text x="160" y="192" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Điện áp 12V • Dung lượng cao</text>
  </g>

  <!-- Arrow -->
  <line x1="280" y1="165" x2="350" y2="165" stroke="#d93025" stroke-width="3" marker-end="url(#arr-red)"/>
  <text x="315" y="155" font-family="Times New Roman" font-size="12" font-weight="bold" fill="#d93025" text-anchor="middle">12V</text>

  <!-- Block 2: Bảo vệ -->
  <g filter="url(#shadow)">
    <rect x="350" y="110" width="240" height="110" rx="8" fill="#fff5f5" stroke="#d93025" stroke-width="2.5"/>
    <rect x="350" y="110" width="240" height="28" rx="6" fill="#d93025"/>
    <text x="470" y="130" font-family="Times New Roman" font-size="13.5" font-weight="bold" fill="#ffffff" text-anchor="middle">BẢO VỆ &amp; ĐÓNG CẮT</text>
    <text x="470" y="165" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#c92a2a" text-anchor="middle">Công Tắc 10A &amp; Cầu Chì 7.5A</text>
    <text x="470" y="192" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Bảo vệ quá dòng &amp; Chống chập</text>
  </g>

  <!-- Branching Lines -->
  <line x1="590" y1="165" x2="650" y2="165" stroke="#d93025" stroke-width="3"/>
  <circle cx="650" cy="165" r="5" fill="#d93025"/>

  <!-- Path to VM (Up) -->
  <path d="M 650 165 L 650 120 L 710 120" fill="none" stroke="#d93025" stroke-width="3" marker-end="url(#arr-red)"/>
  <text x="680" y="112" font-family="Times New Roman" font-size="12" font-weight="bold" fill="#d93025">12V VM</text>

  <g filter="url(#shadow)">
    <rect x="710" y="80" width="250" height="90" rx="8" fill="#fff5f5" stroke="#fa5252" stroke-width="2"/>
    <rect x="710" y="80" width="250" height="26" rx="6" fill="#fa5252"/>
    <text x="835" y="98" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">NGUỒN ĐỘNG LỰC (12V)</text>
    <text x="835" y="128" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#c92a2a" text-anchor="middle">Cấp 2 Mạch Động Cơ</text>
    <text x="835" y="150" font-family="Times New Roman" font-size="12.5" fill="#495057" text-anchor="middle">Nuôi 4 động cơ DC bánh xe</text>
  </g>

  <!-- Path to Buck (Down) -->
  <path d="M 650 165 L 650 260 L 710 260" fill="none" stroke="#d93025" stroke-width="3" marker-end="url(#arr-red)"/>
  <text x="680" y="252" font-family="Times New Roman" font-size="12" font-weight="bold" fill="#d93025">12V IN</text>

  <g filter="url(#shadow)">
    <rect x="710" y="215" width="250" height="100" rx="8" fill="#fff9db" stroke="#f59f00" stroke-width="2"/>
    <rect x="710" y="215" width="250" height="26" rx="6" fill="#f59f00"/>
    <text x="835" y="233" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">MẠCH HẠ ÁP (BUCK DC-DC)</text>
    <text x="835" y="265" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#d9480f" text-anchor="middle">Hạ Áp 5V - 5A Hiệu Suất Cao</text>
    <text x="835" y="290" font-family="Times New Roman" font-size="12.5" fill="#495057" text-anchor="middle">Hiệu suất 94%, không gây nóng</text>
  </g>

  <!-- Arrow from Buck to 5V Consumers -->
  <path d="M 835 315 L 835 375 L 750 375" fill="none" stroke="#1a73e8" stroke-width="3" marker-end="url(#arr-blue)"/>
  <text x="800" y="365" font-family="Times New Roman" font-size="12" font-weight="bold" fill="#1a73e8">5V - 5A</text>

  <!-- 5V Consumers Box -->
  <g filter="url(#shadow)">
    <rect x="230" y="340" width="520" height="110" rx="8" fill="#e8f0fe" stroke="#1a73e8" stroke-width="2"/>
    <rect x="230" y="340" width="520" height="28" rx="6" fill="#1a73e8"/>
    <text x="490" y="360" font-family="Times New Roman" font-size="13.5" font-weight="bold" fill="#ffffff" text-anchor="middle">THIẾT BỊ SỬ DỤNG NGUỒN 5V</text>
    <text x="490" y="395" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#1864ab" text-anchor="middle">1. Máy tính Raspberry Pi 4 Model B (Dòng tải 3A)</text>
    <text x="490" y="425" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#1864ab" text-anchor="middle">2. Hệ thống Cảm biến Siêu âm &amp; Mạch điều khiển</text>
  </g>

  <!-- 3.3V Step-down -->
  <line x1="230" y1="395" x2="160" y2="395" stroke="#7950f2" stroke-width="2.5" marker-end="url(#arr-blue)"/>
  <g filter="url(#shadow)">
    <rect x="40" y="340" width="120" height="110" rx="8" fill="#f3f0ff" stroke="#7950f2" stroke-width="1.8"/>
    <text x="100" y="375" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#6741d9" text-anchor="middle">RAY 3.3V</text>
    <text x="100" y="405" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">• OLED 1.3"</text>
    <text x="100" y="430" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">• Dò Line</text>
  </g>

  <!-- Clean Bottom GND Bar -->
  <rect x="40" y="500" width="920" height="60" rx="8" fill="#f1f3f5" stroke="#495057" stroke-width="2"/>
  <text x="500" y="526" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#212529" text-anchor="middle">
    ĐƯỜNG MASS THỐNG NHẤT (COMMON GROUND)
  </text>
  <text x="500" y="546" font-family="Times New Roman" font-size="12.5" fill="#495057" text-anchor="middle">
    Tất cả các khối dùng chung một mức điện áp chuẩn 0V để chống sụt áp và triệt tiêu nhiễu động cơ
  </text>
</svg>"""

render_svg_to_png(svg_slide9, 'extracted_imgs/block_diagrams/block_diagram_slide9_power.png', dpi=300)

# ==============================================================================
# 3. SLIDE 10: KHỐI 2 - ĐIỀU KHIỂN TRUNG TÂM (CONTROL SUBSYSTEM)
# Bỏ phần footer dài, chỉ giữ dòng vào - bộ xử lý - dòng ra rõ ràng
# ==============================================================================
svg_slide10 = """<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="650" viewBox="0 0 1000 650">
  <defs>
    <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a73e8"/>
    </marker>
    <marker id="arr-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2b8a3e"/>
    </marker>
    <marker id="arr-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#702283"/>
    </marker>
    <filter id="shadow" x="-4%" y="-4%" width="108%" height="108%">
      <feDropShadow dx="0" dy="3" stdDeviation="3" flood-opacity="0.10"/>
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff" rx="14" stroke="#cfd8dc" stroke-width="2"/>

  <!-- Title Banner -->
  <rect x="25" y="20" width="950" height="44" rx="8" fill="#1a73e8"/>
  <text x="500" y="49" font-family="Times New Roman" font-size="19" font-weight="bold" fill="#ffffff" text-anchor="middle">
    SƠ ĐỒ KHỐI CHỨC NĂNG: KHỐI 2 - ĐIỀU KHIỂN TRUNG TÂM
  </text>

  <!-- Left: Inputs -->
  <g filter="url(#shadow)">
    <!-- 1. Sensors -->
    <rect x="40" y="90" width="250" height="120" rx="8" fill="#ebfbee" stroke="#2b8a3e" stroke-width="2"/>
    <rect x="40" y="90" width="250" height="26" rx="6" fill="#2b8a3e"/>
    <text x="165" y="108" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">TÍN HIỆU CẢM BIẾN</text>
    <text x="165" y="138" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2b8a3e" text-anchor="middle">• 2x Cảm biến Siêu âm</text>
    <text x="165" y="160" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">(Tín hiệu Trig / Echo)</text>
    <text x="165" y="184" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2b8a3e" text-anchor="middle">• Cảm biến Dò Line (3 Kênh)</text>
    <text x="165" y="200" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">(Tín hiệu số Trái, Giữa, Phải)</text>

    <!-- 2. Camera -->
    <rect x="40" y="235" width="250" height="85" rx="8" fill="#ebfbee" stroke="#2b8a3e" stroke-width="2"/>
    <rect x="40" y="235" width="250" height="26" rx="6" fill="#2b8a3e"/>
    <text x="165" y="253" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">THỊ GIÁC MÁY TÍNH</text>
    <text x="165" y="285" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2b8a3e" text-anchor="middle">Camera Pi CSI 5MP</text>
    <text x="165" y="305" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Truyền luồng hình ảnh trực tiếp</text>

    <!-- 3. Nguon & Wifi -->
    <rect x="40" y="345" width="250" height="85" rx="8" fill="#fff5f5" stroke="#e03131" stroke-width="2"/>
    <rect x="40" y="345" width="250" height="26" rx="6" fill="#e03131"/>
    <text x="165" y="363" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">NGUỒN CẤP HOẠT ĐỘNG</text>
    <text x="165" y="395" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c92a2a" text-anchor="middle">5VDC - 5A từ Mạch Buck</text>
    <text x="165" y="415" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Cấp nguồn ổn định, chống sập</text>

    <!-- 4. Wifi -->
    <rect x="40" y="455" width="250" height="85" rx="8" fill="#f8f9fa" stroke="#495057" stroke-width="2"/>
    <rect x="40" y="455" width="250" height="26" rx="6" fill="#495057"/>
    <text x="165" y="473" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">KẾT NỐI KHÔNG DÂY</text>
    <text x="165" y="505" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#212529" text-anchor="middle">Mạng Wi-Fi Nội Bộ</text>
    <text x="165" y="525" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Nhận lệnh điều khiển Web &amp; AI</text>
  </g>

  <!-- Left Arrows to Center -->
  <line x1="290" y1="150" x2="350" y2="150" stroke="#2b8a3e" stroke-width="2.5" marker-end="url(#arr-green)"/>
  <line x1="290" y1="277" x2="350" y2="277" stroke="#2b8a3e" stroke-width="2.5" marker-end="url(#arr-green)"/>
  <line x1="290" y1="387" x2="350" y2="387" stroke="#e03131" stroke-width="2.5" marker-end="url(#arr-blue)"/>
  <line x1="290" y1="497" x2="350" y2="497" stroke="#495057" stroke-width="2.5" marker-end="url(#arr-blue)"/>

  <!-- Center: Pi 4 Core -->
  <g filter="url(#shadow)">
    <rect x="350" y="90" width="300" height="450" rx="12" fill="#e8f0fe" stroke="#1a73e8" stroke-width="3"/>
    <rect x="350" y="90" width="300" height="36" rx="10" fill="#1a73e8"/>
    <text x="500" y="114" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#ffffff" text-anchor="middle">
      BỘ XỬ LÝ TRUNG TÂM
    </text>
    <text x="500" y="150" font-family="Times New Roman" font-size="17" font-weight="bold" fill="#0f2b48" text-anchor="middle">
      Raspberry Pi 4 Model B
    </text>
    <text x="500" y="170" font-family="Times New Roman" font-size="13" fill="#5f6368" text-anchor="middle">
      RAM 4GB • Hệ điều hành Linux
    </text>

    <!-- Sub-boxes -->
    <rect x="370" y="195" width="260" height="65" rx="6" fill="#ffffff" stroke="#1a73e8" stroke-width="1.2"/>
    <text x="500" y="222" font-family="Times New Roman" font-size="13.5" font-weight="bold" fill="#1a73e8" text-anchor="middle">Xử lý Tín hiệu &amp; Né vật cản</text>
    <text x="500" y="244" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Tính khoảng cách &amp; Độ lệch tâm vạch</text>

    <rect x="370" y="275" width="260" height="65" rx="6" fill="#ffffff" stroke="#1a73e8" stroke-width="1.2"/>
    <text x="500" y="302" font-family="Times New Roman" font-size="13.5" font-weight="bold" fill="#1a73e8" text-anchor="middle">Điều khiển Động cơ (PWM)</text>
    <text x="500" y="324" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Băm xung tốc độ &amp; Đảo chiều quay</text>

    <rect x="370" y="355" width="260" height="65" rx="6" fill="#ffffff" stroke="#1a73e8" stroke-width="1.2"/>
    <text x="500" y="382" font-family="Times New Roman" font-size="13.5" font-weight="bold" fill="#1a73e8" text-anchor="middle">Máy chủ Web &amp; REST API</text>
    <text x="500" y="404" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Xử lý lệnh di chuyển qua Wi-Fi</text>

    <rect x="370" y="435" width="260" height="85" rx="6" fill="#1a73e8"/>
    <text x="500" y="462" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">Bo Mạch Kết Nối (Carrier Board)</text>
    <text x="500" y="484" font-family="Times New Roman" font-size="12" fill="#e8f0fe" text-anchor="middle">Cáp bẹ 40 chân cắm thẳng chắc chắn</text>
    <text x="500" y="504" font-family="Times New Roman" font-size="12" fill="#e8f0fe" text-anchor="middle">Tách biệt đường công suất và tín hiệu</text>
  </g>

  <!-- Right: Outputs -->
  <g filter="url(#shadow)">
    <!-- 1. Banh trai -->
    <rect x="710" y="100" width="250" height="120" rx="8" fill="#e3fafc" stroke="#0c8599" stroke-width="2"/>
    <rect x="710" y="100" width="250" height="26" rx="6" fill="#0c8599"/>
    <text x="835" y="118" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">ĐIỀU KHIỂN CỤM BÁNH TRÁI</text>
    <text x="835" y="148" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#0c8599" text-anchor="middle">Mạch Công Suất 1</text>
    <text x="835" y="170" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">2 Kênh xung PWM + 4 Tín hiệu hướng</text>
    <text x="835" y="195" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#087f5b" text-anchor="middle">➔ 2 Động cơ Bánh Trái (Trước/Sau)</text>

    <!-- 2. Banh phai -->
    <rect x="710" y="240" width="250" height="120" rx="8" fill="#e3fafc" stroke="#0c8599" stroke-width="2"/>
    <rect x="710" y="240" width="250" height="26" rx="6" fill="#0c8599"/>
    <text x="835" y="258" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">ĐIỀU KHIỂN CỤM BÁNH PHẢI</text>
    <text x="835" y="288" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#0c8599" text-anchor="middle">Mạch Công Suất 2</text>
    <text x="835" y="310" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">2 Kênh xung PWM + 4 Tín hiệu hướng</text>
    <text x="835" y="335" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#087f5b" text-anchor="middle">➔ 2 Động cơ Bánh Phải (Trước/Sau)</text>

    <!-- 3. OLED -->
    <rect x="710" y="380" width="250" height="110" rx="8" fill="#f3f0ff" stroke="#702283" stroke-width="2"/>
    <rect x="710" y="380" width="250" height="26" rx="6" fill="#702283"/>
    <text x="835" y="398" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">HIỂN THỊ THÔNG SỐ</text>
    <text x="835" y="428" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#702283" text-anchor="middle">Màn hình OLED 1.3" I2C</text>
    <text x="835" y="450" font-family="Times New Roman" font-size="12" fill="#495057" text-anchor="middle">Giao tiếp 2 dây (SDA, SCL)</text>
    <text x="835" y="472" font-family="Times New Roman" font-size="12.5" font-weight="bold" fill="#5c7cfa" text-anchor="middle">Báo IP, Mức Pin, Trạng thái</text>
  </g>

  <!-- Right Arrows from Center -->
  <line x1="650" y1="160" x2="710" y2="160" stroke="#0c8599" stroke-width="2.5" marker-end="url(#arr-blue)"/>
  <line x1="650" y1="300" x2="710" y2="300" stroke="#0c8599" stroke-width="2.5" marker-end="url(#arr-blue)"/>
  <line x1="650" y1="435" x2="710" y2="435" stroke="#702283" stroke-width="2.5" marker-end="url(#arr-purple)"/>

  <!-- Bottom Strip -->
  <rect x="40" y="565" width="920" height="50" rx="8" fill="#f8f9fa" stroke="#ced4da" stroke-width="1.5"/>
  <text x="500" y="596" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#1864ab" text-anchor="middle">
    Kiến trúc điều khiển tập trung, phản hồi tức thời mili-giây, chống nhiễu tuyệt đối
  </text>
</svg>"""

render_svg_to_png(svg_slide10, 'extracted_imgs/block_diagrams/block_diagram_slide10_control.png', dpi=300)

# ==============================================================================
# 4. SLIDE 11: KHỐI 3 - TÍN HIỆU & CẢM BIẾN (SENSOR & DISPLAY)
# 3 cột thông thoáng, bỏ toàn bộ tọa độ và mô tả dài dòng
# ==============================================================================
svg_slide11 = """<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="620" viewBox="0 0 1000 620">
  <defs>
    <filter id="shadow" x="-4%" y="-4%" width="108%" height="108%">
      <feDropShadow dx="0" dy="3" stdDeviation="3" flood-opacity="0.10"/>
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff" rx="14" stroke="#cfd8dc" stroke-width="2"/>

  <!-- Title Banner -->
  <rect x="25" y="20" width="950" height="44" rx="8" fill="#2b8a3e"/>
  <text x="500" y="49" font-family="Times New Roman" font-size="19" font-weight="bold" fill="#ffffff" text-anchor="middle">
    SƠ ĐỒ KHỐI CHỨC NĂNG: KHỐI 3 - TÍN HIỆU &amp; CẢM BIẾN
  </text>

  <!-- 3 Main Columns -->
  <!-- Col 1: Siêu âm -->
  <g filter="url(#shadow)">
    <rect x="40" y="90" width="290" height="400" rx="10" fill="#ebfbee" stroke="#2b8a3e" stroke-width="2.5"/>
    <rect x="40" y="90" width="290" height="34" rx="8" fill="#2b8a3e"/>
    <text x="185" y="113" font-family="Times New Roman" font-size="14.5" font-weight="bold" fill="#ffffff" text-anchor="middle">CẢM BIẾN SIÊU ÂM (2 BỘ)</text>

    <!-- Sub 1 -->
    <rect x="55" y="145" width="260" height="95" rx="6" fill="#ffffff" stroke="#40c057" stroke-width="1.5"/>
    <text x="185" y="175" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#2b8a3e" text-anchor="middle">2 Cảm Biến Trái &amp; Phải</text>
    <text x="185" y="200" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Khoảng cách đo: 2cm đến 400cm</text>
    <text x="185" y="222" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Góc quét rộng, phát hiện chướng ngại vật</text>

    <!-- Sub 2: Bảo vệ -->
    <rect x="55" y="260" width="260" height="95" rx="6" fill="#fff9db" stroke="#f59f00" stroke-width="1.5"/>
    <text x="185" y="290" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#d9480f" text-anchor="middle">Mạch Phân Áp Bảo Vệ</text>
    <text x="185" y="315" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#d9480f" text-anchor="middle">Hạ điện áp Echo: 5V ➔ 3.3V</text>
    <text x="185" y="337" font-family="Times New Roman" font-size="12.5" fill="#495057" text-anchor="middle">Bảo vệ an toàn chân tín hiệu máy tính</text>

    <!-- Role summary -->
    <rect x="55" y="375" width="260" height="95" rx="6" fill="#ffffff" stroke="#ced4da" stroke-width="1.2"/>
    <text x="185" y="405" font-family="Times New Roman" font-size="13.5" font-weight="bold" fill="#1864ab" text-anchor="middle">Tín hiệu gửi về Raspberry Pi</text>
    <text x="185" y="430" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">• Tín hiệu phát: Trig_L, Trig_R</text>
    <text x="185" y="452" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">• Tín hiệu nhận: Echo_L, Echo_R</text>
  </g>

  <!-- Col 2: Dò line -->
  <g filter="url(#shadow)">
    <rect x="355" y="90" width="290" height="400" rx="10" fill="#ebfbee" stroke="#2b8a3e" stroke-width="2.5"/>
    <rect x="355" y="90" width="290" height="34" rx="8" fill="#2b8a3e"/>
    <text x="500" y="113" font-family="Times New Roman" font-size="14.5" font-weight="bold" fill="#ffffff" text-anchor="middle">CẢM BIẾN DÒ LINE (3 MẮT)</text>

    <!-- Sub 1 -->
    <rect x="370" y="145" width="260" height="95" rx="6" fill="#ffffff" stroke="#40c057" stroke-width="1.5"/>
    <text x="500" y="175" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#2b8a3e" text-anchor="middle">3 Mắt Quang Hồng Ngoại</text>
    <text x="500" y="200" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Mắt Trái • Mắt Giữa • Mắt Phải</text>
    <text x="500" y="222" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Gắn dưới gầm xe, hướng mặt sàn</text>

    <!-- Sub 2 -->
    <rect x="370" y="260" width="260" height="95" rx="6" fill="#ffffff" stroke="#40c057" stroke-width="1.5"/>
    <text x="500" y="290" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#2b8a3e" text-anchor="middle">Nhận Diện Đường Đi</text>
    <text x="500" y="315" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Phân biệt vạch đen / sàn trắng</text>
    <text x="500" y="337" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Độ nhạy cao, không phụ thuộc ánh sáng</text>

    <!-- Sub 3 -->
    <rect x="370" y="375" width="260" height="95" rx="6" fill="#ffffff" stroke="#ced4da" stroke-width="1.2"/>
    <text x="500" y="405" font-family="Times New Roman" font-size="13.5" font-weight="bold" fill="#1864ab" text-anchor="middle">Tín hiệu gửi về Raspberry Pi</text>
    <text x="500" y="430" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">• 3 Ngõ ra số 3.3V (Line_L, C, R)</text>
    <text x="500" y="452" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">• Bù tốc độ 2 bên bánh để xe vào cua</text>
  </g>

  <!-- Col 3: OLED -->
  <g filter="url(#shadow)">
    <rect x="670" y="90" width="290" height="400" rx="10" fill="#f3f0ff" stroke="#702283" stroke-width="2.5"/>
    <rect x="670" y="90" width="290" height="34" rx="8" fill="#702283"/>
    <text x="815" y="113" font-family="Times New Roman" font-size="14.5" font-weight="bold" fill="#ffffff" text-anchor="middle">MÀN HÌNH OLED 1.3" I2C</text>

    <!-- Sub 1 -->
    <rect x="685" y="145" width="260" height="95" rx="6" fill="#ffffff" stroke="#702283" stroke-width="1.5"/>
    <text x="815" y="175" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#702283" text-anchor="middle">Màn Hình Đồ Họa 1.3"</text>
    <text x="815" y="200" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Độ phân giải 128x64 sắc nét</text>
    <text x="815" y="222" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Góc nhìn rộng, tiết kiệm điện năng</text>

    <!-- Sub 2 -->
    <rect x="685" y="260" width="260" height="95" rx="6" fill="#ffffff" stroke="#702283" stroke-width="1.5"/>
    <text x="815" y="290" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#702283" text-anchor="middle">Giao Tiếp 2 Dây (I2C)</text>
    <text x="815" y="315" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Dây dữ liệu: SDA (Chân 27)</text>
    <text x="815" y="337" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Dây xung nhịp: SCL (Chân 28)</text>

    <!-- Sub 3 -->
    <rect x="685" y="375" width="260" height="95" rx="6" fill="#ffffff" stroke="#ced4da" stroke-width="1.2"/>
    <text x="815" y="405" font-family="Times New Roman" font-size="13.5" font-weight="bold" fill="#1864ab" text-anchor="middle">Nội Dung Hiển Thị</text>
    <text x="815" y="430" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">• Địa chỉ IP truy cập Web (Wi-Fi)</text>
    <text x="815" y="452" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">• Phần trăm pin &amp; Trạng thái xe</text>
  </g>

  <!-- Bottom summary banner -->
  <rect x="40" y="520" width="920" height="60" rx="8" fill="#f8f9fa" stroke="#495057" stroke-width="1.5"/>
  <text x="500" y="546" font-family="Times New Roman" font-size="14.5" font-weight="bold" fill="#0f2b48" text-anchor="middle">
    Cung cấp đầy đủ thông tin môi trường để xe tự hành an toàn và người dùng tiện theo dõi
  </text>
  <text x="500" y="566" font-family="Times New Roman" font-size="12.5" fill="#495057" text-anchor="middle">
    Tất cả các đường tín hiệu được bảo vệ an toàn cho máy tính trên bo mạch Carrier
  </text>
</svg>"""

render_svg_to_png(svg_slide11, 'extracted_imgs/block_diagrams/block_diagram_slide11_sensor.png', dpi=300)

# ==============================================================================
# 5. SLIDE 12: KHỐI 4 - CÔNG SUẤT CHẤP HÀNH (ACTUATION SUBSYSTEM)
# 3 bước: Tín hiệu Pi -> 2 Driver -> 4 Động cơ, bỏ văn bản dài dòng ở đáy
# ==============================================================================
svg_slide12 = """<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="640" viewBox="0 0 1000 640">
  <defs>
    <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a73e8"/>
    </marker>
    <marker id="arr-orange" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#d9480f"/>
    </marker>
    <filter id="shadow" x="-4%" y="-4%" width="108%" height="108%">
      <feDropShadow dx="0" dy="3" stdDeviation="3" flood-opacity="0.10"/>
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff" rx="14" stroke="#cfd8dc" stroke-width="2"/>

  <!-- Title Banner -->
  <rect x="25" y="20" width="950" height="44" rx="8" fill="#0c8599"/>
  <text x="500" y="49" font-family="Times New Roman" font-size="19" font-weight="bold" fill="#ffffff" text-anchor="middle">
    SƠ ĐỒ KHỐI CHỨC NĂNG: KHỐI 4 - CÔNG SUẤT CHẤP HÀNH
  </text>

  <!-- Stage 1: Tín hiệu từ Pi 4 -->
  <g filter="url(#shadow)">
    <rect x="40" y="90" width="260" height="420" rx="10" fill="#e8f0fe" stroke="#1a73e8" stroke-width="2.5"/>
    <rect x="40" y="90" width="260" height="34" rx="8" fill="#1a73e8"/>
    <text x="170" y="113" font-family="Times New Roman" font-size="14.5" font-weight="bold" fill="#ffffff" text-anchor="middle">TÍN HIỆU TỪ RASPBERRY PI</text>

    <!-- Sub 1 -->
    <rect x="55" y="145" width="230" height="100" rx="6" fill="#ffffff" stroke="#1a73e8" stroke-width="1.2"/>
    <text x="170" y="175" font-family="Times New Roman" font-size="14.5" font-weight="bold" fill="#1a73e8" text-anchor="middle">Điều Khiển Cụm Bánh Trái</text>
    <text x="170" y="200" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">• 2 Kênh xung PWM tốc độ</text>
    <text x="170" y="222" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">• 4 Chân chọn chiều tiến/lùi</text>

    <!-- Sub 2 -->
    <rect x="55" y="260" width="230" height="100" rx="6" fill="#ffffff" stroke="#1a73e8" stroke-width="1.2"/>
    <text x="170" y="290" font-family="Times New Roman" font-size="14.5" font-weight="bold" fill="#1a73e8" text-anchor="middle">Điều Khiển Cụm Bánh Phải</text>
    <text x="170" y="315" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">• 2 Kênh xung PWM tốc độ</text>
    <text x="170" y="337" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">• 4 Chân chọn chiều tiến/lùi</text>

    <!-- Sub 3 -->
    <rect x="55" y="375" width="230" height="110" rx="6" fill="#fff5f5" stroke="#e03131" stroke-width="1.2"/>
    <text x="170" y="405" font-family="Times New Roman" font-size="14.5" font-weight="bold" fill="#c92a2a" text-anchor="middle">Khóa An Toàn Khẩn Cấp</text>
    <text x="170" y="430" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">• Chân STBY ngắt mạch</text>
    <text x="170" y="452" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">• Dừng khẩn cấp khi gặp sự cố</text>
    <text x="170" y="472" font-family="Times New Roman" font-size="12" font-style="italic" fill="#c92a2a" text-anchor="middle">Điện áp tín hiệu 3.3V chuẩn</text>
  </g>

  <!-- Arrows 1 -> 2 -->
  <line x1="300" y1="195" x2="365" y2="195" stroke="#1a73e8" stroke-width="2.5" marker-end="url(#arr-blue)"/>
  <line x1="300" y1="310" x2="365" y2="310" stroke="#1a73e8" stroke-width="2.5" marker-end="url(#arr-blue)"/>
  <line x1="300" y1="430" x2="365" y2="430" stroke="#e03131" stroke-width="2.5" marker-end="url(#arr-blue)"/>

  <!-- Stage 2: 2 Module Driver TB6612 -->
  <g filter="url(#shadow)">
    <rect x="365" y="90" width="280" height="420" rx="10" fill="#e3fafc" stroke="#0c8599" stroke-width="2.5"/>
    <rect x="365" y="90" width="280" height="34" rx="8" fill="#0c8599"/>
    <text x="505" y="113" font-family="Times New Roman" font-size="14.5" font-weight="bold" fill="#ffffff" text-anchor="middle">2 MẠCH CÔNG SUẤT TB6612</text>

    <!-- Driver 1 -->
    <rect x="380" y="145" width="250" height="145" rx="6" fill="#ffffff" stroke="#0c8599" stroke-width="1.5"/>
    <text x="505" y="175" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#0c8599" text-anchor="middle">Mạch Công Suất 1 (Bánh Trái)</text>
    <text x="505" y="200" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Nguồn nuôi động cơ: 12V từ Pin</text>
    <text x="505" y="222" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Dòng tải khỏe, không sụt áp</text>
    <rect x="395" y="235" width="220" height="40" rx="4" fill="#e6fcf5"/>
    <text x="505" y="260" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#087f5b" text-anchor="middle">➔ Ngõ ra Động cơ Trái (FL, RL)</text>

    <!-- Driver 2 -->
    <rect x="380" y="315" width="250" height="145" rx="6" fill="#ffffff" stroke="#0c8599" stroke-width="1.5"/>
    <text x="505" y="345" font-family="Times New Roman" font-size="15" font-weight="bold" fill="#0c8599" text-anchor="middle">Mạch Công Suất 2 (Bánh Phải)</text>
    <text x="505" y="370" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Nguồn nuôi động cơ: 12V từ Pin</text>
    <text x="505" y="392" font-family="Times New Roman" font-size="13" fill="#495057" text-anchor="middle">Dòng tải khỏe, không sụt áp</text>
    <rect x="395" y="405" width="220" height="40" rx="4" fill="#e6fcf5"/>
    <text x="505" y="430" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#087f5b" text-anchor="middle">➔ Ngõ ra Động cơ Phải (FR, RR)</text>

    <text x="505" y="490" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#0c8599" text-anchor="middle">Có chế độ Phanh điện từ dừng tức thời</text>
  </g>

  <!-- Arrows 2 -> 3 -->
  <line x1="645" y1="230" x2="710" y2="230" stroke="#0c8599" stroke-width="2.5" marker-end="url(#arr-blue)"/>
  <line x1="645" y1="380" x2="710" y2="380" stroke="#0c8599" stroke-width="2.5" marker-end="url(#arr-blue)"/>

  <!-- Stage 3: 4 DC Motors & Chassis -->
  <g filter="url(#shadow)">
    <rect x="710" y="90" width="250" height="420" rx="10" fill="#fff9db" stroke="#f59f00" stroke-width="2.5"/>
    <rect x="710" y="90" width="250" height="34" rx="8" fill="#f59f00"/>
    <text x="835" y="113" font-family="Times New Roman" font-size="14.5" font-weight="bold" fill="#ffffff" text-anchor="middle">4 ĐỘNG CƠ DC &amp; KHUNG XE</text>

    <!-- Motor 1 & 2 -->
    <rect x="725" y="145" width="220" height="60" rx="6" fill="#ffffff" stroke="#f59f00" stroke-width="1.2"/>
    <text x="835" y="170" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#d9480f" text-anchor="middle">M1: Bánh Trước Trái (FL)</text>
    <text x="835" y="190" font-family="Times New Roman" font-size="12.5" fill="#495057" text-anchor="middle">Động cơ DC 12V giảm tốc</text>

    <rect x="725" y="215" width="220" height="60" rx="6" fill="#ffffff" stroke="#f59f00" stroke-width="1.2"/>
    <text x="835" y="240" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#d9480f" text-anchor="middle">M2: Bánh Sau Trái (RL)</text>
    <text x="835" y="260" font-family="Times New Roman" font-size="12.5" fill="#495057" text-anchor="middle">Động cơ DC 12V giảm tốc</text>

    <!-- Motor 3 & 4 -->
    <rect x="725" y="285" width="220" height="60" rx="6" fill="#ffffff" stroke="#f59f00" stroke-width="1.2"/>
    <text x="835" y="310" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#d9480f" text-anchor="middle">M3: Bánh Trước Phải (FR)</text>
    <text x="835" y="330" font-family="Times New Roman" font-size="12.5" fill="#495057" text-anchor="middle">Động cơ DC 12V giảm tốc</text>

    <rect x="725" y="355" width="220" height="60" rx="6" fill="#ffffff" stroke="#f59f00" stroke-width="1.2"/>
    <text x="835" y="380" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#d9480f" text-anchor="middle">M4: Bánh Sau Phải (RR)</text>
    <text x="835" y="400" font-family="Times New Roman" font-size="12.5" fill="#495057" text-anchor="middle">Động cơ DC 12V giảm tốc</text>

    <!-- Motion Modes -->
    <rect x="725" y="425" width="220" height="70" rx="6" fill="#f8f9fa" stroke="#495057" stroke-width="1"/>
    <text x="835" y="450" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#212529" text-anchor="middle">CHUYỂN ĐỘNG 4 BÁNH</text>
    <text x="835" y="475" font-family="Times New Roman" font-size="12.5" font-weight="bold" fill="#087f5b" text-anchor="middle">Tiến • Lùi • Quay tại chỗ • Phanh</text>
  </g>

  <!-- Bottom summary strip -->
  <rect x="40" y="540" width="920" height="65" rx="8" fill="#f8f9fa" stroke="#0c8599" stroke-width="1.5"/>
  <text x="500" y="567" font-family="Times New Roman" font-size="14.5" font-weight="bold" fill="#0c8599" text-anchor="middle">
    Phân tải đều 2 bên bánh xe, không quá nhiệt, hỗ trợ quay vòng tại chỗ linh hoạt trong lối đi hẹp
  </text>
  <text x="500" y="589" font-family="Times New Roman" font-size="12.5" fill="#495057" text-anchor="middle">
    Chế độ phanh điện từ giúp xe dừng tức thời an toàn khi phát hiện vật cản gần
  </text>
</svg>"""

render_svg_to_png(svg_slide12, 'extracted_imgs/block_diagrams/block_diagram_slide12_motor.png', dpi=300)

print("Generated all 5 minimalist, clean block diagrams!")
