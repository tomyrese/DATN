import os
import fitz

os.makedirs('extracted_imgs/flowcharts', exist_ok=True)

def render_svg_to_png(svg_str, output_path, dpi=300):
    doc = fitz.open(stream=svg_str.encode('utf-8'), filetype='svg')
    page = doc[0]
    pix = page.get_pixmap(dpi=dpi)
    pix.save(output_path)
    print(f"Rendered {output_path}: {pix.width} x {pix.height}")

# ==============================================================================
# FLOWCHART 1: LƯU ĐỒ HOẠT ĐỘNG TỔNG THỂ HỆ THỐNG ROBOT TỰ HÀNH
# ==============================================================================
svg_fc1 = """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1350" viewBox="0 0 900 1350">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#1a365d"/>
    </marker>
    <marker id="arr-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#c53030"/>
    </marker>
    <marker id="arr-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#276749"/>
    </marker>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.10"/>
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff" rx="12" stroke="#cbd5e0" stroke-width="2"/>

  <!-- Title Banner -->
  <rect x="25" y="20" width="850" height="46" rx="8" fill="#1a365d"/>
  <text x="450" y="50" font-family="Times New Roman" font-size="20" font-weight="bold" fill="#ffffff" text-anchor="middle">
    LƯU ĐỒ HOẠT ĐỘNG TỔNG THỂ HỆ THỐNG ROBOT TỰ HÀNH
  </text>

  <!-- 1. BẮT ĐẦU -->
  <g filter="url(#shadow)">
    <rect x="350" y="86" width="200" height="50" rx="25" fill="#ebf8ff" stroke="#3182ce" stroke-width="2.5"/>
    <text x="450" y="117" font-family="Times New Roman" font-size="16" font-weight="bold" fill="#2b6cb0" text-anchor="middle">BẮT ĐẦU</text>
  </g>

  <line x1="450" y1="136" x2="450" y2="166" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 2. KHỞI TẠO HỆ THỐNG -->
  <g filter="url(#shadow)">
    <rect x="200" y="166" width="500" height="96" rx="8" fill="#f7fafc" stroke="#4a5568" stroke-width="2"/>
    <rect x="200" y="166" width="500" height="26" rx="8" fill="#4a5568"/>
    <text x="450" y="184" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">KHỞI TẠO HỆ THỐNG TRÊN RASPBERRY PI 4</text>
    <text x="450" y="210" font-family="Times New Roman" font-size="13" fill="#2d3748" text-anchor="middle">• Cấu hình chân BCM GPIO &amp; PWM 1 kHz cho 2 mạch driver TB6612FNG</text>
    <text x="450" y="230" font-family="Times New Roman" font-size="13" fill="#2d3748" text-anchor="middle">• Khởi tạo bus I²C (Màn hình OLED 1.3") &amp; Cổng MIPI CSI (Camera OV5647)</text>
    <text x="450" y="250" font-family="Times New Roman" font-size="13" fill="#2d3748" text-anchor="middle">• Khởi động Web Server (Port 8080) &amp; Mạng Wi-Fi điều khiển nội bộ</text>
  </g>

  <line x1="450" y1="262" x2="450" y2="292" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 3. HIỂN THỊ MÃ QR TRÊN OLED -->
  <g filter="url(#shadow)">
    <polygon points="260,292 680,292 640,356 220,356" fill="#f0fff4" stroke="#38a169" stroke-width="2"/>
    <text x="450" y="318" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#276749" text-anchor="middle">HIỂN THỊ MÃ QR ĐỘNG TRÊN MÀN HÌNH OLED 1.3"</text>
    <text x="450" y="340" font-family="Times New Roman" font-size="13" fill="#276749" text-anchor="middle">Sinh QR chứa địa chỉ IP Web Dashboard cho khách hàng quét kết nối</text>
  </g>

  <line x1="450" y1="356" x2="450" y2="386" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 4. ĐỌC DỮ LIỆU CẢM BIẾN & CAMERA -->
  <g filter="url(#shadow)">
    <rect x="220" y="386" width="460" height="74" rx="8" fill="#f7fafc" stroke="#4a5568" stroke-width="2"/>
    <text x="450" y="412" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2d3748" text-anchor="middle">THU THẬP DỮ LIỆU NGOẠI VI THEO CHU KỲ (50 ms)</text>
    <text x="450" y="432" font-family="Times New Roman" font-size="13" fill="#4a5568" text-anchor="middle">• Đọc cự ly cảm biến siêu âm HC-SR04 (Trái &amp; Phải)</text>
    <text x="450" y="450" font-family="Times New Roman" font-size="13" fill="#4a5568" text-anchor="middle">• Thu nhận khung hình từ Camera CSI &amp; Lắng nghe lệnh từ Web Server</text>
  </g>

  <line x1="450" y1="460" x2="450" y2="490" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 5. KIỂM TRA VẬT CẢN NGUY HIỂM -->
  <g filter="url(#shadow)">
    <polygon points="450,490 640,550 450,610 260,550" fill="#fffaf0" stroke="#dd6b20" stroke-width="2.5"/>
    <text x="450" y="544" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">Khoảng cách</text>
    <text x="450" y="564" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">d ≤ 20 cm?</text>
  </g>

  <!-- Nhánh Đúng: Nguy hiểm -->
  <line x1="640" y1="550" x2="710" y2="550" stroke="#c53030" stroke-width="2.5"/>
  <text x="670" y="540" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#c53030">ĐÚNG</text>
  <line x1="710" y1="550" x2="710" y2="590" stroke="#c53030" stroke-width="2.5" marker-end="url(#arr-red)"/>

  <!-- Xử lý Né Vật Cản -->
  <g filter="url(#shadow)">
    <rect x="600" y="590" width="220" height="74" rx="8" fill="#fff5f5" stroke="#e53e3e" stroke-width="2"/>
    <text x="710" y="615" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#c53030" text-anchor="middle">DỪNG PHANH KHẨN CẤP</text>
    <text x="710" y="635" font-family="Times New Roman" font-size="12" fill="#c53030" text-anchor="middle">Chuyển sang thuật toán</text>
    <text x="710" y="652" font-family="Times New Roman" font-size="12" fill="#c53030" text-anchor="middle">né tránh vật cản tự động</text>
  </g>

  <!-- Vòng lặp từ Né vật cản quay về Main Loop -->
  <line x1="710" y1="664" x2="710" y2="1240" stroke="#c53030" stroke-width="2"/>
  <line x1="710" y1="1240" x2="450" y2="1240" stroke="#c53030" stroke-width="2"/>

  <!-- Nhánh Sai: An toàn -->
  <line x1="450" y1="610" x2="450" y2="646" stroke="#276749" stroke-width="2.5" marker-end="url(#arr-green)"/>
  <text x="460" y="630" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#276749">SAI</text>

  <!-- 6. PHÁT HIỆN KHÁCH HÀNG / NGƯỜI TIẾP CẬN -->
  <g filter="url(#shadow)">
    <polygon points="450,646 630,706 450,766 270,706" fill="#fffaf0" stroke="#dd6b20" stroke-width="2.5"/>
    <text x="450" y="698" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">Phát hiện người /</text>
    <text x="450" y="718" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">Khách hàng tiếp cận?</text>
  </g>

  <!-- Nhánh Đúng: Có người -->
  <line x1="270" y1="706" x2="190" y2="706" stroke="#2b6cb0" stroke-width="2.5"/>
  <text x="215" y="696" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#2b6cb0">ĐÚNG</text>
  <line x1="190" y1="706" x2="190" y2="746" stroke="#2b6cb0" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- Tương tác khách hàng -->
  <g filter="url(#shadow)">
    <rect x="80" y="746" width="220" height="74" rx="8" fill="#ebf8ff" stroke="#3182ce" stroke-width="2"/>
    <text x="190" y="771" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#2b6cb0" text-anchor="middle">TƯƠNG TÁC KHÁCH HÀNG</text>
    <text x="190" y="791" font-family="Times New Roman" font-size="12" fill="#2b6cb0" text-anchor="middle">Dừng xe, OLED chào đón</text>
    <text x="190" y="808" font-family="Times New Roman" font-size="12" fill="#2b6cb0" text-anchor="middle">Chờ khách quét QR đặt hàng</text>
  </g>

  <line x1="190" y1="820" x2="190" y2="1240" stroke="#2b6cb0" stroke-width="2"/>
  <line x1="190" y1="1240" x2="450" y2="1240" stroke="#2b6cb0" stroke-width="2"/>

  <!-- Nhánh Sai: Không có khách hàng -->
  <line x1="450" y1="766" x2="450" y2="802" stroke="#276749" stroke-width="2.5" marker-end="url(#arr-green)"/>
  <text x="460" y="786" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#276749">SAI</text>

  <!-- 7. KIỂM TRA LỆNH ĐIỀU KHIỂN TỪ WEB -->
  <g filter="url(#shadow)">
    <polygon points="450,802 630,862 450,922 270,862" fill="#fffaf0" stroke="#dd6b20" stroke-width="2.5"/>
    <text x="450" y="854" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">Nhận lệnh điều khiển</text>
    <text x="450" y="874" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">từ Web Dashboard?</text>
  </g>

  <!-- Nhánh Đúng: Có lệnh -->
  <line x1="450" y1="922" x2="450" y2="956" stroke="#276749" stroke-width="2.5" marker-end="url(#arr-green)"/>
  <text x="460" y="940" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#276749">ĐÚNG</text>

  <!-- 8. TÍNH TOÁN ĐỘNG HỌC MECANUM -->
  <g filter="url(#shadow)">
    <rect x="230" y="956" width="440" height="64" rx="8" fill="#f7fafc" stroke="#4a5568" stroke-width="2"/>
    <text x="450" y="982" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2d3748" text-anchor="middle">GIẢI MÃ ĐỘNG HỌC 4 BÁNH MECANUM</text>
    <text x="450" y="1004" font-family="Times New Roman" font-size="13" fill="#4a5568" text-anchor="middle">Tính vận tốc góc (ω₁, ω₂, ω₃, ω₄) theo hướng di chuyển yêu cầu</text>
  </g>

  <line x1="450" y1="1020" x2="450" y2="1050" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 9. XUẤT PWM VÀ LOGIC CHIỀU QUAY -->
  <g filter="url(#shadow)">
    <rect x="230" y="1050" width="440" height="74" rx="8" fill="#ebf8ff" stroke="#3182ce" stroke-width="2"/>
    <text x="450" y="1076" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2b6cb0" text-anchor="middle">XUẤT XUNG PWM VÀ LOGIC CHIỀU QUAY (IN1, IN2)</text>
    <text x="450" y="1098" font-family="Times New Roman" font-size="13" fill="#2b6cb0" text-anchor="middle">Cấp xung tới 2 IC driver TB6612FNG dẫn động 4 động cơ giảm tốc TT</text>
    <text x="450" y="1114" font-family="Times New Roman" font-size="12" fill="#4a5568" text-anchor="middle">(Tiến, Lùi, Dạt ngang Trái/Phải, Xoay tại chỗ, Phanh hãm)</text>
  </g>

  <!-- Nhánh Sai của kiểm tra lệnh Web: Dừng hoặc giữ trạng thái -->
  <line x1="630" y1="862" x2="680" y2="862" stroke="#4a5568" stroke-width="2"/>
  <text x="645" y="852" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#4a5568">SAI</text>
  <line x1="680" y1="862" x2="680" y2="1160" stroke="#4a5568" stroke-width="2"/>

  <line x1="450" y1="1124" x2="450" y2="1160" stroke="#1a365d" stroke-width="2.5"/>
  <line x1="680" y1="1160" x2="450" y2="1160" stroke="#4a5568" stroke-width="2"/>

  <!-- ĐIỂM HỘI TỤ CHU KỲ -->
  <circle cx="450" cy="1160" r="4" fill="#1a365d"/>
  <line x1="450" y1="1160" x2="450" y2="1200" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 10. ĐỒNG BỘ TRẠNG THÁI & LIVE LOGS -->
  <g filter="url(#shadow)">
    <rect x="270" y="1200" width="360" height="44" rx="8" fill="#f0fff4" stroke="#38a169" stroke-width="2"/>
    <text x="450" y="1228" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#276749" text-anchor="middle">Đồng bộ Live Logs lên Web Dashboard &amp; OLED</text>
  </g>

  <!-- VÒNG LẶP QUAY LẠI BƯỚC 4 -->
  <line x1="450" y1="1244" x2="450" y2="1275" stroke="#1a365d" stroke-width="2.5"/>
  <line x1="450" y1="1275" x2="50" y2="1275" stroke="#1a365d" stroke-width="2.5"/>
  <line x1="50" y1="1275" x2="50" y2="423" stroke="#1a365d" stroke-width="2.5"/>
  <line x1="50" y1="423" x2="220" y2="423" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>
  <text x="60" y="850" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#1a365d" transform="rotate(-90 60 850)">VÒNG LẶP CHU KỲ ĐIỀU KHIỂN (50 ms)</text>

</svg>
"""

# ==============================================================================
# FLOWCHART 2: LƯU ĐỒ GIẢI THUẬT ĐIỀU KHIỂN ĐỘNG HỌC 4 BÁNH MECANUM
# ==============================================================================
svg_fc2 = """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1200" viewBox="0 0 900 1200">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#1a365d"/>
    </marker>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.10"/>
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff" rx="12" stroke="#cbd5e0" stroke-width="2"/>

  <!-- Title Banner -->
  <rect x="25" y="20" width="850" height="46" rx="8" fill="#1a365d"/>
  <text x="450" y="50" font-family="Times New Roman" font-size="20" font-weight="bold" fill="#ffffff" text-anchor="middle">
    LƯU ĐỒ GIẢI THUẬT ĐIỀU KHIỂN ĐỘNG HỌC 4 BÁNH MECANUM &amp; PWM
  </text>

  <!-- 1. BẮT ĐẦU -->
  <g filter="url(#shadow)">
    <rect x="350" y="86" width="200" height="46" rx="23" fill="#ebf8ff" stroke="#3182ce" stroke-width="2.5"/>
    <text x="450" y="115" font-family="Times New Roman" font-size="16" font-weight="bold" fill="#2b6cb0" text-anchor="middle">BẮT ĐẦU</text>
  </g>

  <line x1="450" y1="132" x2="450" y2="162" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 2. NHẬN VECTOR VẬN TỐC YÊU CẦU -->
  <g filter="url(#shadow)">
    <polygon points="230,162 710,162 670,226 190,226" fill="#f0fff4" stroke="#38a169" stroke-width="2"/>
    <text x="450" y="188" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#276749" text-anchor="middle">NHẬN VECTOR LỆNH VẬN TỐC (Vx, Vy, ωz) &amp; SPEED PWM</text>
    <text x="450" y="210" font-family="Times New Roman" font-size="13" fill="#276749" text-anchor="middle">Nhận từ Web Dashboard: Tiến, Lùi, Dạt ngang Trái/Phải, Xoay tròn, Phanh</text>
  </g>

  <line x1="450" y1="226" x2="450" y2="256" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 3. KIỂM TRA LỆNH PHANH / DỪNG -->
  <g filter="url(#shadow)">
    <polygon points="450,256 620,310 450,364 280,310" fill="#fffaf0" stroke="#dd6b20" stroke-width="2.5"/>
    <text x="450" y="306" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">Lệnh Dừng / Phanh</text>
    <text x="450" y="324" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">(Brake / Stop)?</text>
  </g>

  <!-- Nhánh Đúng: Phanh hãm -->
  <line x1="620" y1="310" x2="690" y2="310" stroke="#c53030" stroke-width="2.5"/>
  <text x="640" y="300" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#c53030">ĐÚNG</text>
  <line x1="690" y1="310" x2="690" y2="344" stroke="#c53030" stroke-width="2.5" marker-end="url(#arr)"/>

  <g filter="url(#shadow)">
    <rect x="580" y="344" width="220" height="66" rx="8" fill="#fff5f5" stroke="#e53e3e" stroke-width="2"/>
    <text x="690" y="368" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#c53030" text-anchor="middle">THIẾT LẬP PHANH (BRAKE)</text>
    <text x="690" y="388" font-family="Times New Roman" font-size="12" fill="#c53030" text-anchor="middle">• IN1 = HIGH, IN2 = HIGH</text>
    <text x="690" y="403" font-family="Times New Roman" font-size="12" fill="#c53030" text-anchor="middle">• Duty Cycle PWM = 0%</text>
  </g>

  <line x1="690" y1="410" x2="690" y2="990" stroke="#c53030" stroke-width="2"/>
  <line x1="690" y1="990" x2="450" y2="990" stroke="#c53030" stroke-width="2"/>

  <!-- Nhánh Sai: Di chuyển -->
  <line x1="450" y1="364" x2="450" y2="394" stroke="#276749" stroke-width="2.5" marker-end="url(#arr)"/>
  <text x="460" y="380" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#276749">SAI</text>

  <!-- 4. TÍNH MA TRẬN ĐỘNG HỌC NGHỊCH (INVERSE KINEMATICS) -->
  <g filter="url(#shadow)">
    <rect x="180" y="394" width="540" height="136" rx="8" fill="#f7fafc" stroke="#4a5568" stroke-width="2"/>
    <rect x="180" y="394" width="540" height="26" rx="8" fill="#4a5568"/>
    <text x="450" y="412" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">MÔ HÌNH ĐỘNG HỌC TOÀN HƯỚNG 4 BÁNH MECANUM</text>
    <text x="450" y="440" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#1a365d" text-anchor="middle">• Bánh Trước Trái (FL - U_TB1 Ch A):   ω₁ = (1/R) · [ Vx - Vy - (Lx + Ly)·ωz ]</text>
    <text x="450" y="465" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#1a365d" text-anchor="middle">• Bánh Trước Phải (FR - U_TB2 Ch A):  ω₂ = (1/R) · [ Vx + Vy + (Lx + Ly)·ωz ]</text>
    <text x="450" y="490" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#1a365d" text-anchor="middle">• Bánh Sau Trái (RL - U_TB1 Ch B):     ω₃ = (1/R) · [ Vx + Vy - (Lx + Ly)·ωz ]</text>
    <text x="450" y="515" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#1a365d" text-anchor="middle">• Bánh Sau Phải (RR - U_TB2 Ch B):    ω₄ = (1/R) · [ Vx - Vy + (Lx + Ly)·ωz ]</text>
  </g>

  <line x1="450" y1="530" x2="450" y2="560" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 5. CHUẨN HÓA VẬN TỐC (NORMALIZATION) -->
  <g filter="url(#shadow)">
    <rect x="220" y="560" width="460" height="70" rx="8" fill="#f7fafc" stroke="#4a5568" stroke-width="2"/>
    <text x="450" y="586" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2d3748" text-anchor="middle">CHUẨN HÓA VẬN TỐC VỀ DẢI ĐIỀU KHIỂN</text>
    <text x="450" y="608" font-family="Times New Roman" font-size="13" fill="#4a5568" text-anchor="middle">Nếu max(|ωᵢ|) &gt; ω_max: Chuẩn hóa tỉ lệ ωᵢ = (ωᵢ / max(|ωᵢ|)) × Speed</text>
  </g>

  <line x1="450" y1="630" x2="450" y2="660" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 6. XÁC ĐỊNH CHIỀU QUAY VÀ TÍNH DUTY CYCLE CHO TỪNG BÁNH -->
  <g filter="url(#shadow)">
    <rect x="180" y="660" width="540" height="150" rx="8" fill="#ebf8ff" stroke="#3182ce" stroke-width="2"/>
    <rect x="180" y="660" width="540" height="26" rx="8" fill="#3182ce"/>
    <text x="450" y="678" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">XÁC ĐỊNH MỨC LOGIC CHIỀU QUAY &amp; ĐỘ RỘNG XUNG PWM</text>
    <text x="210" y="708" font-family="Times New Roman" font-size="13" fill="#2d3748">• Nếu ωᵢ &gt; 0 (Quay tiến):</text>
    <text x="420" y="708" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#276749">AIN1 = HIGH, AIN2 = LOW (CW)</text>
    <text x="210" y="732" font-family="Times New Roman" font-size="13" fill="#2d3748">• Nếu ωᵢ &lt; 0 (Quay lùi):</text>
    <text x="420" y="732" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#c53030">AIN1 = LOW, AIN2 = HIGH (CCW)</text>
    <text x="210" y="756" font-family="Times New Roman" font-size="13" fill="#2d3748">• Nếu ωᵢ = 0 (Dừng tự do):</text>
    <text x="420" y="756" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#718096">AIN1 = LOW, AIN2 = LOW (Coast)</text>
    <text x="210" y="784" font-family="Times New Roman" font-size="13" fill="#2d3748">• Độ rộng xung Duty Cycle:</text>
    <text x="420" y="784" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#2b6cb0">PWM_Duty = (|ωᵢ| / ω_max) × 100% (20% – 100%)</text>
  </g>

  <line x1="450" y1="810" x2="450" y2="840" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 7. KÍCH HOẠT VÀ XUẤT TÍN HIỆU ĐẾN 2 DRIVER TB6612FNG -->
  <g filter="url(#shadow)">
    <rect x="200" y="840" width="500" height="90" rx="8" fill="#f0fff4" stroke="#38a169" stroke-width="2"/>
    <text x="450" y="866" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#276749" text-anchor="middle">XUẤT TÍN HIỆU RA 2 IC DRIVER TB6612FNG</text>
    <text x="450" y="888" font-family="Times New Roman" font-size="13" fill="#276749" text-anchor="middle">• Đặt STBY_L = HIGH (GPIO 17) &amp; STBY_R = HIGH (GPIO 20) để kích hoạt driver</text>
    <text x="450" y="908" font-family="Times New Roman" font-size="13" fill="#276749" text-anchor="middle">• Xuất xung Hardware PWM 1 kHz đến PWMA_L (GPIO 2) &amp; PWMA_R (GPIO 13)</text>
  </g>

  <line x1="450" y1="930" x2="450" y2="990" stroke="#1a365d" stroke-width="2.5"/>
  <circle cx="450" cy="990" r="4" fill="#1a365d"/>
  <line x1="450" y1="990" x2="450" y2="1030" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 8. KẾT THÚC / LẶP LẠI -->
  <g filter="url(#shadow)">
    <rect x="350" y="1030" width="200" height="46" rx="23" fill="#ebf8ff" stroke="#3182ce" stroke-width="2.5"/>
    <text x="450" y="1059" font-family="Times New Roman" font-size="16" font-weight="bold" fill="#2b6cb0" text-anchor="middle">KẾT THÚC CHU KỲ</text>
  </g>

</svg>
"""

# ==============================================================================
# FLOWCHART 3: LƯU ĐỒ GIẢI THUẬT ĐỌC SIÊU ÂM & NÉ VẬT CẢN ĐA CẤP
# ==============================================================================
svg_fc3 = """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1250" viewBox="0 0 900 1250">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#1a365d"/>
    </marker>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.10"/>
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff" rx="12" stroke="#cbd5e0" stroke-width="2"/>

  <!-- Title Banner -->
  <rect x="25" y="20" width="850" height="46" rx="8" fill="#1a365d"/>
  <text x="450" y="50" font-family="Times New Roman" font-size="20" font-weight="bold" fill="#ffffff" text-anchor="middle">
    LƯU ĐỒ GIẢI THUẬT ĐỌC SIÊU ÂM HC-SR04 &amp; NÉ VẬT CẢN ĐA CẤP
  </text>

  <!-- 1. BẮT ĐẦU -->
  <g filter="url(#shadow)">
    <rect x="350" y="86" width="200" height="46" rx="23" fill="#ebf8ff" stroke="#3182ce" stroke-width="2.5"/>
    <text x="450" y="115" font-family="Times New Roman" font-size="16" font-weight="bold" fill="#2b6cb0" text-anchor="middle">BẮT ĐẦU</text>
  </g>

  <line x1="450" y1="132" x2="450" y2="162" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 2. PHÁT XUNG TRIGGER -->
  <g filter="url(#shadow)">
    <rect x="220" y="162" width="460" height="66" rx="8" fill="#f7fafc" stroke="#4a5568" stroke-width="2"/>
    <text x="450" y="188" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2d3748" text-anchor="middle">PHÁT XUNG KÍCH HOẠT TRIGGER (HC-SR04)</text>
    <text x="450" y="210" font-family="Times New Roman" font-size="13" fill="#4a5568" text-anchor="middle">Kéo chân TRIG lên mức HIGH trong 10 µs, sau đó hạ xuống LOW</text>
  </g>

  <line x1="450" y1="228" x2="450" y2="258" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 3. THU NHẬN XUNG ECHO VÀ TÍNH KHOẢNG CÁCH -->
  <g filter="url(#shadow)">
    <polygon points="200,258 740,258 700,332 160,332" fill="#f0fff4" stroke="#38a169" stroke-width="2"/>
    <text x="450" y="284" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#276749" text-anchor="middle">THU NHẬN XUNG ECHO QUA CẦU PHÂN ÁP (1kΩ / 2kΩ - 3.3V)</text>
    <text x="450" y="304" font-family="Times New Roman" font-size="13" fill="#276749" text-anchor="middle">• Đo độ rộng xung phản hồi Echo (Δt)</text>
    <text x="450" y="322" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#276749" text-anchor="middle">• Tính cự ly: d = (Δt × 34300) / 2  (cm) - Lọc trung bình động 3 mẫu</text>
  </g>

  <line x1="450" y1="332" x2="450" y2="362" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 4. SO SÁNH PHÂN TẦNG VÙNG NGUY HIỂM -->
  <g filter="url(#shadow)">
    <polygon points="450,362 620,416 450,470 280,416" fill="#fffaf0" stroke="#dd6b20" stroke-width="2.5"/>
    <text x="450" y="410" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">Khoảng cách</text>
    <text x="450" y="430" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">d &gt; 35 cm?</text>
  </g>

  <!-- Nhánh Đúng: Vùng an toàn -->
  <line x1="620" y1="416" x2="710" y2="416" stroke="#276749" stroke-width="2.5"/>
  <text x="640" y="406" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#276749">ĐÚNG</text>
  <line x1="710" y1="416" x2="710" y2="450" stroke="#276749" stroke-width="2.5" marker-end="url(#arr)"/>

  <g filter="url(#shadow)">
    <rect x="610" y="450" width="200" height="66" rx="8" fill="#f0fff4" stroke="#38a169" stroke-width="2"/>
    <text x="710" y="474" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#276749" text-anchor="middle">VÙNG AN TOÀN</text>
    <text x="710" y="494" font-family="Times New Roman" font-size="12" fill="#276749" text-anchor="middle">Duy trì tốc độ định mức</text>
    <text x="710" y="508" font-family="Times New Roman" font-size="12" fill="#276749" text-anchor="middle">(70% – 80% PWM)</text>
  </g>

  <line x1="710" y1="516" x2="710" y2="1080" stroke="#276749" stroke-width="2"/>
  <line x1="710" y1="1080" x2="450" y2="1080" stroke="#276749" stroke-width="2"/>

  <!-- Nhánh Sai: Kiểm tra tiếp ngưỡng 20-35cm -->
  <line x1="450" y1="470" x2="450" y2="506" stroke="#c05621" stroke-width="2.5" marker-end="url(#arr)"/>
  <text x="460" y="490" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#c05621">SAI</text>

  <g filter="url(#shadow)">
    <polygon points="450,506 630,560 450,614 270,560" fill="#fffaf0" stroke="#dd6b20" stroke-width="2.5"/>
    <text x="450" y="554" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">20 cm &lt; d ≤ 35 cm?</text>
    <text x="450" y="574" font-family="Times New Roman" font-size="12" fill="#c05621" text-anchor="middle">(Vùng Cảnh Báo)</text>
  </g>

  <!-- Nhánh Đúng: Cảnh báo -->
  <line x1="630" y1="560" x2="710" y2="560" stroke="#dd6b20" stroke-width="2.5"/>
  <text x="645" y="550" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#dd6b20">ĐÚNG</text>
  <line x1="710" y1="560" x2="710" y2="594" stroke="#dd6b20" stroke-width="2.5" marker-end="url(#arr)"/>

  <g filter="url(#shadow)">
    <rect x="610" y="594" width="200" height="66" rx="8" fill="#fffaf0" stroke="#dd6b20" stroke-width="2"/>
    <text x="710" y="618" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#c05621" text-anchor="middle">VÙNG CẢNH BÁO</text>
    <text x="710" y="638" font-family="Times New Roman" font-size="12" fill="#c05621" text-anchor="middle">Giảm tốc độ xuống 40%</text>
    <text x="710" y="652" font-family="Times New Roman" font-size="12" fill="#c05621" text-anchor="middle">Tăng tần số quét cảm biến</text>
  </g>

  <line x1="710" y1="660" x2="710" y2="1080" stroke="#dd6b20" stroke-width="2"/>

  <!-- Nhánh Sai: Kiểm tra tiếp ngưỡng 10-20cm -->
  <line x1="450" y1="614" x2="450" y2="650" stroke="#c53030" stroke-width="2.5" marker-end="url(#arr)"/>
  <text x="460" y="634" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#c53030">SAI</text>

  <g filter="url(#shadow)">
    <polygon points="450,650 630,704 450,758 270,704" fill="#fffaf0" stroke="#dd6b20" stroke-width="2.5"/>
    <text x="450" y="698" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">10 cm &lt; d ≤ 20 cm?</text>
    <text x="450" y="718" font-family="Times New Roman" font-size="12" fill="#c05621" text-anchor="middle">(Vùng Nguy Hiểm)</text>
  </g>

  <!-- Nhánh Đúng: Nguy hiểm -> Dạt ngang né vật cản -->
  <line x1="270" y1="704" x2="190" y2="704" stroke="#c53030" stroke-width="2.5"/>
  <text x="215" y="694" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#c53030">ĐÚNG</text>
  <line x1="190" y1="704" x2="190" y2="740" stroke="#c53030" stroke-width="2.5" marker-end="url(#arr)"/>

  <g filter="url(#shadow)">
    <rect x="70" y="740" width="240" height="96" rx="8" fill="#fff5f5" stroke="#e53e3e" stroke-width="2"/>
    <text x="190" y="764" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#c53030" text-anchor="middle">VÙNG NGUY HIỂM</text>
    <text x="190" y="784" font-family="Times New Roman" font-size="12" fill="#2d3748" text-anchor="middle">Dừng xe; So sánh d_Trái &amp; d_Phải:</text>
    <text x="190" y="802" font-family="Times New Roman" font-size="12" font-weight="bold" fill="#2b6cb0" text-anchor="middle">• Nếu d_L &gt; d_R: Dạt ngang Trái</text>
    <text x="190" y="820" font-family="Times New Roman" font-size="12" font-weight="bold" fill="#2b6cb0" text-anchor="middle">• Nếu d_R ≥ d_L: Dạt ngang Phải</text>
  </g>

  <line x1="190" y1="836" x2="190" y2="1080" stroke="#c53030" stroke-width="2"/>
  <line x1="190" y1="1080" x2="450" y2="1080" stroke="#c53030" stroke-width="2"/>

  <!-- Nhánh Sai: d <= 10cm (Khẩn cấp) -->
  <line x1="450" y1="758" x2="450" y2="820" stroke="#c53030" stroke-width="2.5" marker-end="url(#arr)"/>
  <text x="460" y="790" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#c53030">d ≤ 10 cm (KHẨN CẤP)</text>

  <g filter="url(#shadow)">
    <rect x="250" y="820" width="400" height="110" rx="8" fill="#fff5f5" stroke="#9b2c2c" stroke-width="2.5"/>
    <rect x="250" y="820" width="400" height="26" rx="8" fill="#9b2c2c"/>
    <text x="450" y="838" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">HÀNH ĐỘNG DỪNG PHANH KHẨN CẤP (BRAKE)</text>
    <text x="450" y="866" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#c53030" text-anchor="middle">1. Phanh cứng tức thời 4 bánh (Short Brake - 100 ms)</text>
    <text x="450" y="888" font-family="Times New Roman" font-size="13" fill="#2d3748" text-anchor="middle">2. Lùi an toàn 10 cm (4 bánh quay lùi 30% PWM)</text>
    <text x="450" y="910" font-family="Times New Roman" font-size="13" fill="#2d3748" text-anchor="middle">3. Xoay góc 90° tìm hướng thoáng để tiếp tục hành trình</text>
  </g>

  <line x1="450" y1="930" x2="450" y2="980" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 5. CẬP NHẬT TRẠNG THÁI RA MÀN HÌNH OLED & WEB -->
  <g filter="url(#shadow)">
    <rect x="260" y="980" width="380" height="54" rx="8" fill="#f7fafc" stroke="#4a5568" stroke-width="2"/>
    <text x="450" y="1006" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#2d3748" text-anchor="middle">GỬI CẢNH BÁO LÊN OLED &amp; WEB DASHBOARD</text>
    <text x="450" y="1024" font-family="Times New Roman" font-size="12" fill="#4a5568" text-anchor="middle">Cập nhật khoảng cách d và trạng thái né vật cản thời gian thực</text>
  </g>

  <line x1="450" y1="1034" x2="450" y2="1080" stroke="#1a365d" stroke-width="2.5"/>
  <circle cx="450" cy="1080" r="4" fill="#1a365d"/>
  <line x1="450" y1="1080" x2="450" y2="1120" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 6. KẾT THÚC CHU KỲ -->
  <g filter="url(#shadow)">
    <rect x="350" y="1120" width="200" height="46" rx="23" fill="#ebf8ff" stroke="#3182ce" stroke-width="2.5"/>
    <text x="450" y="1149" font-family="Times New Roman" font-size="16" font-weight="bold" fill="#2b6cb0" text-anchor="middle">KẾT THÚC CHU KỲ</text>
  </g>

</svg>
"""

# ==============================================================================
# FLOWCHART 4: LƯU ĐỒ XỬ LÝ CAMERA OPENCV & TƯƠNG TÁC QR OLED
# ==============================================================================
svg_fc4 = """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1200" viewBox="0 0 900 1200">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#1a365d"/>
    </marker>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.10"/>
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff" rx="12" stroke="#cbd5e0" stroke-width="2"/>

  <!-- Title Banner -->
  <rect x="25" y="20" width="850" height="46" rx="8" fill="#1a365d"/>
  <text x="450" y="50" font-family="Times New Roman" font-size="20" font-weight="bold" fill="#ffffff" text-anchor="middle">
    LƯU ĐỒ XỬ LÝ CAMERA OPENCV &amp; TƯƠNG TÁC MÃ QR TRÊN OLED 1.3"
  </text>

  <!-- 1. BẮT ĐẦU -->
  <g filter="url(#shadow)">
    <rect x="350" y="86" width="200" height="46" rx="23" fill="#ebf8ff" stroke="#3182ce" stroke-width="2.5"/>
    <text x="450" y="115" font-family="Times New Roman" font-size="16" font-weight="bold" fill="#2b6cb0" text-anchor="middle">BẮT ĐẦU</text>
  </g>

  <line x1="450" y1="132" x2="450" y2="162" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 2. THU NHẬN FRAME TỪ CAMERA CSI -->
  <g filter="url(#shadow)">
    <polygon points="220,162 720,162 680,226 180,226" fill="#f0fff4" stroke="#38a169" stroke-width="2"/>
    <text x="450" y="188" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#276749" text-anchor="middle">THU NHẬN KHUNG HÌNH TỪ CAMERA MIPI CSI (OV5647)</text>
    <text x="450" y="210" font-family="Times New Roman" font-size="13" fill="#276749" text-anchor="middle">Luồng video 640 × 480 pixels @ 30 fps nạp vào bộ đệm bộ nhớ GPU VideoCore VI</text>
  </g>

  <line x1="450" y1="226" x2="450" y2="256" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 3. TIỀN XỬ LÝ ẢNH -->
  <g filter="url(#shadow)">
    <rect x="200" y="256" width="500" height="80" rx="8" fill="#f7fafc" stroke="#4a5568" stroke-width="2"/>
    <text x="450" y="282" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2d3748" text-anchor="middle">TIỀN XỬ LÝ ẢNH BẰNG THƯ VIỆN OPENCV</text>
    <text x="450" y="304" font-family="Times New Roman" font-size="13" fill="#4a5568" text-anchor="middle">• Chuyển ảnh màu RGB sang ảnh xám: I_gray = cv2.cvtColor(frame, BGR2GRAY)</text>
    <text x="450" y="324" font-family="Times New Roman" font-size="13" fill="#4a5568" text-anchor="middle">• Làm mờ Gauss khử nhiễu môi trường: cv2.GaussianBlur(ksize=(21, 21))</text>
  </g>

  <line x1="450" y1="336" x2="450" y2="366" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 4. TRỪ NỀN THÍCH NGHI VÀ PHÂN NGƯỠNG -->
  <g filter="url(#shadow)">
    <rect x="200" y="366" width="500" height="86" rx="8" fill="#ebf8ff" stroke="#3182ce" stroke-width="2"/>
    <text x="450" y="392" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2b6cb0" text-anchor="middle">PHÁT HIỆN BIẾN ĐỔI CHUYỂN ĐỘNG (FRAME DIFFERENCING)</text>
    <text x="450" y="414" font-family="Times New Roman" font-size="13" fill="#2d3748" text-anchor="middle">• Tính độ lệch cường độ: ΔI = |I_current - I_background|</text>
    <text x="450" y="434" font-family="Times New Roman" font-size="13" fill="#2d3748" text-anchor="middle">• Phân ngưỡng nhị phân (Threshold = 25) &amp; Phép giãn ảnh (Dilation 2 lần)</text>
  </g>

  <line x1="450" y1="452" x2="450" y2="482" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 5. TÌM CONTOURS VÀ TÍNH DIỆN TÍCH -->
  <g filter="url(#shadow)">
    <polygon points="450,482 630,536 450,590 270,536" fill="#fffaf0" stroke="#dd6b20" stroke-width="2.5"/>
    <text x="450" y="530" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">Diện tích vùng biến đổi</text>
    <text x="450" y="550" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">Area &gt; 5000 pixels?</text>
  </g>

  <!-- Nhánh Đúng: Có người -->
  <line x1="450" y1="590" x2="450" y2="626" stroke="#276749" stroke-width="2.5" marker-end="url(#arr)"/>
  <text x="460" y="608" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#276749">ĐÚNG (PHÁT HIỆN KHÁCH HÀNG)</text>

  <!-- 6. KÍCH HOẠT CHẾ ĐỘ CHÀO ĐÓN VÀ TƯƠNG TÁC -->
  <g filter="url(#shadow)">
    <rect x="180" y="626" width="540" height="110" rx="8" fill="#f0fff4" stroke="#38a169" stroke-width="2"/>
    <rect x="180" y="626" width="540" height="26" rx="8" fill="#38a169"/>
    <text x="450" y="644" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">CHUYỂN SANG CHẾ ĐỘ TƯƠNG TÁC KHÁCH HÀNG</text>
    <text x="450" y="674" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#276749" text-anchor="middle">1. Giảm tốc độ và dừng robot an toàn (Brake)</text>
    <text x="450" y="696" font-family="Times New Roman" font-size="13" fill="#2d3748" text-anchor="middle">2. Màn hình OLED hiển thị: "XIN CHÀO! HÃY QUÉT MÃ QR ĐỂ GIAO HÀNG"</text>
    <text x="450" y="718" font-family="Times New Roman" font-size="13" fill="#2d3748" text-anchor="middle">3. Bật còi buzzer / đèn LED thông báo sự hiện diện</text>
  </g>

  <line x1="450" y1="736" x2="450" y2="766" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 7. KHÁCH HÀNG QUÉT MÃ QR TƯƠNG TÁC -->
  <g filter="url(#shadow)">
    <polygon points="210,766 730,766 690,830 170,830" fill="#ebf8ff" stroke="#3182ce" stroke-width="2"/>
    <text x="450" y="792" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2b6cb0" text-anchor="middle">KHÁCH HÀNG DÙNG CAMERA ĐIỆN THOẠI QUÉT MÃ QR TRÊN OLED</text>
    <text x="450" y="812" font-family="Times New Roman" font-size="13" fill="#2b6cb0" text-anchor="middle">Mở giao diện Web Dashboard trên trình duyệt điện thoại để chỉ định quầy giao hàng</text>
  </g>

  <!-- Nhánh Sai của kiểm tra diện tích: Không có người -> Cập nhật nền -->
  <line x1="630" y1="536" x2="720" y2="536" stroke="#4a5568" stroke-width="2"/>
  <text x="645" y="526" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#4a5568">SAI</text>
  <line x1="720" y1="536" x2="720" y2="870" stroke="#4a5568" stroke-width="2"/>

  <line x1="450" y1="830" x2="450" y2="870" stroke="#1a365d" stroke-width="2.5"/>
  <line x1="720" y1="870" x2="450" y2="870" stroke="#4a5568" stroke-width="2"/>
  <circle cx="450" cy="870" r="4" fill="#1a365d"/>

  <line x1="450" y1="870" x2="450" y2="900" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 8. CẬP NHẬT ẢNH NỀN THÍCH NGHI -->
  <g filter="url(#shadow)">
    <rect x="230" y="900" width="440" height="60" rx="8" fill="#f7fafc" stroke="#4a5568" stroke-width="2"/>
    <text x="450" y="924" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2d3748" text-anchor="middle">CẬP NHẬT MÔ HÌNH NỀN THÍCH NGHI (ADAPTIVE BG)</text>
    <text x="450" y="944" font-family="Times New Roman" font-size="13" fill="#4a5568" text-anchor="middle">cv2.accumulateWeighted(I_gray, I_background, alpha=0.05)</text>
  </g>

  <line x1="450" y1="960" x2="450" y2="1000" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 9. KẾT THÚC CHU KỲ FRAME -->
  <g filter="url(#shadow)">
    <rect x="350" y="1000" width="200" height="46" rx="23" fill="#ebf8ff" stroke="#3182ce" stroke-width="2.5"/>
    <text x="450" y="1029" font-family="Times New Roman" font-size="16" font-weight="bold" fill="#2b6cb0" text-anchor="middle">KẾT THÚC FRAME</text>
  </g>

</svg>
"""

# ==============================================================================
# FLOWCHART 5: LƯU ĐỒ HOẠT ĐỘNG WEB SERVER & DASHBOARD ĐIỀU KHIỂN TỪ XA
# ==============================================================================
svg_fc5 = """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1150" viewBox="0 0 900 1150">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#1a365d"/>
    </marker>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.10"/>
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="#ffffff" rx="12" stroke="#cbd5e0" stroke-width="2"/>

  <!-- Title Banner -->
  <rect x="25" y="20" width="850" height="46" rx="8" fill="#1a365d"/>
  <text x="450" y="50" font-family="Times New Roman" font-size="20" font-weight="bold" fill="#ffffff" text-anchor="middle">
    LƯU ĐỒ HOẠT ĐỘNG CỦA WEB SERVER &amp; GIAO DIỆN WEB DASHBOARD
  </text>

  <!-- 1. BẮT ĐẦU -->
  <g filter="url(#shadow)">
    <rect x="350" y="86" width="200" height="46" rx="23" fill="#ebf8ff" stroke="#3182ce" stroke-width="2.5"/>
    <text x="450" y="115" font-family="Times New Roman" font-size="16" font-weight="bold" fill="#2b6cb0" text-anchor="middle">BẮT ĐẦU</text>
  </g>

  <line x1="450" y1="132" x2="450" y2="162" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 2. KHỞI CHẠY WEB SERVER TRÊN PI 4 -->
  <g filter="url(#shadow)">
    <rect x="200" y="162" width="500" height="74" rx="8" fill="#f7fafc" stroke="#4a5568" stroke-width="2"/>
    <text x="450" y="188" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2d3748" text-anchor="middle">KHỞI ĐỘNG MÁY CHỦ PYTHON SERVER (server.py)</text>
    <text x="450" y="210" font-family="Times New Roman" font-size="13" fill="#4a5568" text-anchor="middle">Lắng nghe cổng HTTP 8080 &amp; Khởi tạo lớp điều khiển MotorController</text>
    <text x="450" y="226" font-family="Times New Roman" font-size="12" fill="#718096" text-anchor="middle">(Hỗ trợ chạy độc lập trực tiếp không phụ thuộc Flask/Django)</text>
  </g>

  <line x1="450" y1="236" x2="450" y2="266" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 3. CLIENT KẾT NỐI VÀ TẢI GIAO DIỆN -->
  <g filter="url(#shadow)">
    <polygon points="210,266 730,266 690,336 170,336" fill="#f0fff4" stroke="#38a169" stroke-width="2"/>
    <text x="450" y="292" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#276749" text-anchor="middle">CLIENT TRUY CẬP ĐỊA CHỈ: http://&lt;IP_Pi4&gt;:8080</text>
    <text x="450" y="312" font-family="Times New Roman" font-size="13" fill="#276749" text-anchor="middle">Server phản hồi các tài nguyên tĩnh: index.html, style.css, app.js</text>
    <text x="450" y="328" font-family="Times New Roman" font-size="12" fill="#276749" text-anchor="middle">(Hiển thị giao diện Dark mode, cụm nút điều khiển 8 hướng &amp; thanh trượt PWM)</text>
  </g>

  <line x1="450" y1="336" x2="450" y2="366" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 4. LẮNG NGHE SỰ KIỆN TƯƠNG TÁC TỪ NGƯỜI DÙNG -->
  <g filter="url(#shadow)">
    <polygon points="450,366 630,420 450,474 270,420" fill="#fffaf0" stroke="#dd6b20" stroke-width="2.5"/>
    <text x="450" y="414" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">Có sự kiện tương tác</text>
    <text x="450" y="434" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#c05621" text-anchor="middle">cảm ứng / bàn phím?</text>
  </g>

  <!-- Nhánh Sai: Tiếp tục lắng nghe -->
  <line x1="630" y1="420" x2="710" y2="420" stroke="#4a5568" stroke-width="2"/>
  <text x="645" y="410" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#4a5568">SAI</text>
  <line x1="710" y1="420" x2="710" y2="351" stroke="#4a5568" stroke-width="2"/>
  <line x1="710" y1="351" x2="450" y2="351" stroke="#4a5568" stroke-width="2"/>

  <!-- Nhánh Đúng: Có sự kiện -->
  <line x1="450" y1="474" x2="450" y2="506" stroke="#276749" stroke-width="2.5" marker-end="url(#arr)"/>
  <text x="460" y="492" font-family="Times New Roman" font-size="13" font-weight="bold" fill="#276749">ĐÚNG</text>

  <!-- 5. PHÂN LOẠI YÊU CẦU API TỪ CLIENT -->
  <g filter="url(#shadow)">
    <rect x="180" y="506" width="540" height="110" rx="8" fill="#ebf8ff" stroke="#3182ce" stroke-width="2"/>
    <rect x="180" y="506" width="540" height="26" rx="8" fill="#3182ce"/>
    <text x="450" y="524" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">CLIENT GỬI REQUEST API HTTP POST /api/control</text>
    <text x="210" y="552" font-family="Times New Roman" font-size="13" fill="#2d3748">• Lệnh di chuyển: action = 'forward' | 'backward' | 'strafe_left' | 'strafe_right'</text>
    <text x="210" y="574" font-family="Times New Roman" font-size="13" fill="#2d3748">• Lệnh xoay &amp; dừng: action = 'turn_left' | 'turn_right' | 'brake' | 'stop'</text>
    <text x="210" y="596" font-family="Times New Roman" font-size="13" fill="#2d3748">• Lệnh điều tốc &amp; test: action = 'set_speed' (speed=value) | 'auto_test'</text>
  </g>

  <line x1="450" y1="616" x2="450" y2="646" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 6. BACKEND THỰC THI QUA MOTOR_CONTROLLER -->
  <g filter="url(#shadow)">
    <rect x="200" y="646" width="500" height="84" rx="8" fill="#f7fafc" stroke="#4a5568" stroke-width="2"/>
    <text x="450" y="672" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2d3748" text-anchor="middle">XỬ LÝ LỆNH TẠI BACKEND PYTHON (server.py)</text>
    <text x="450" y="694" font-family="Times New Roman" font-size="13" fill="#4a5568" text-anchor="middle">• Ánh xạ lệnh và gọi phương thức trong motor_controller.py</text>
    <text x="450" y="714" font-family="Times New Roman" font-size="13" fill="#4a5568" text-anchor="middle">• Cập nhật trạng thái phần cứng và chu kỳ nhiệm vụ PWM trên các chân GPIO</text>
  </g>

  <line x1="450" y1="730" x2="450" y2="760" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 7. PHẢN HỒI JSON DỮ LIỆU VỀ CLIENT -->
  <g filter="url(#shadow)">
    <polygon points="210,760 730,760 690,830 170,830" fill="#f0fff4" stroke="#38a169" stroke-width="2"/>
    <text x="450" y="786" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#276749" text-anchor="middle">SERVER TRẢ VỀ DỮ LIỆU PHẢN HỒI (JSON STATUS: 200 OK)</text>
    <text x="450" y="806" font-family="Times New Roman" font-size="13" fill="#276749" text-anchor="middle">{ "status": "success", "action": "forward", "speed": 70, "logs": "Quay tiến 70% PWM" }</text>
    <text x="450" y="822" font-family="Times New Roman" font-size="12" fill="#276749" text-anchor="middle">Độ trễ truyền nhận cực thấp &lt; 50 ms qua mạng Wi-Fi cục bộ</text>
  </g>

  <line x1="450" y1="830" x2="450" y2="860" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 8. CẬP NHẬT GIAO DIỆN DASHBOARD (app.js) -->
  <g filter="url(#shadow)">
    <rect x="220" y="860" width="460" height="70" rx="8" fill="#f7fafc" stroke="#4a5568" stroke-width="2"/>
    <text x="450" y="886" font-family="Times New Roman" font-size="14" font-weight="bold" fill="#2d3748" text-anchor="middle">CẬP NHẬT GIAO DIỆN THỜI GIAN THỰC (FRONTEND)</text>
    <text x="450" y="908" font-family="Times New Roman" font-size="13" fill="#4a5568" text-anchor="middle">Hiển thị dòng thông báo mới nhất trên bảng Live Logs &amp; Hiệu ứng nút bấm</text>
  </g>

  <line x1="450" y1="930" x2="450" y2="970" stroke="#1a365d" stroke-width="2.5" marker-end="url(#arr)"/>

  <!-- 9. KẾT THÚC CHU KỲ LỆNH -->
  <g filter="url(#shadow)">
    <rect x="350" y="970" width="200" height="46" rx="23" fill="#ebf8ff" stroke="#3182ce" stroke-width="2.5"/>
    <text x="450" y="999" font-family="Times New Roman" font-size="16" font-weight="bold" fill="#2b6cb0" text-anchor="middle">HOÀN TẤT LỆNH</text>
  </g>

</svg>
"""

def main():
    print("Generating 5 high-resolution flowcharts...")
    render_svg_to_png(svg_fc1, 'extracted_imgs/flowcharts/flowchart_system_main.png', dpi=300)
    render_svg_to_png(svg_fc2, 'extracted_imgs/flowcharts/flowchart_mecanum_control.png', dpi=300)
    render_svg_to_png(svg_fc3, 'extracted_imgs/flowcharts/flowchart_obstacle_avoidance.png', dpi=300)
    render_svg_to_png(svg_fc4, 'extracted_imgs/flowcharts/flowchart_camera_oled.png', dpi=300)
    render_svg_to_png(svg_fc5, 'extracted_imgs/flowcharts/flowchart_web_dashboard.png', dpi=300)
    print("All 5 flowcharts generated successfully!")

if __name__ == '__main__':
    main()

