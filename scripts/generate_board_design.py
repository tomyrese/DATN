#!/usr/bin/env python3
"""
Toàn diện kịch bản tạo PCB 1 Lớp cho Pi4 Robot Carrier Board
Thiết kế chính xác theo các thông số kỹ thuật trong design_rules.json & pinout_mapping.json
"""

import math
import re
import sys
from pathlib import Path

# Đảm bảo console UTF-8 trên Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

POWER_NETS = {"12V_BAT", "VM", "5V_BUCK", "3V3", "GND"}

def miter_45_path(x1, y1, x2, y2, prefer_x_first=True):
    """
    Tạo danh sách các đoạn thẳng nối từ (x1, y1) đến (x2, y2)
    sử dụng CHỈ góc bẻ 45 độ (không bao giờ tạo góc vuông 90 độ).
    """
    # Nếu cùng toạ độ
    if abs(x1 - x2) < 1e-4 and abs(y1 - y2) < 1e-4:
        return []
    # Đoạn thẳng ngang
    if abs(y1 - y2) < 1e-4:
        return [((x1, y1), (x2, y2))]
    # Đoạn thẳng dọc
    if abs(x1 - x2) < 1e-4:
        return [((x1, y1), (x2, y2))]

    dx = x2 - x1
    dy = y2 - y1
    dx_sign = 1.0 if dx > 0 else -1.0
    dy_sign = 1.0 if dy > 0 else -1.0

    if prefer_x_first:
        if abs(dx) >= abs(dy):
            # Đi ngang rồi bẻ 45 độ
            xm = x2 - abs(dy) * dx_sign
            segs = []
            if abs(xm - x1) > 1e-3:
                segs.append(((x1, y1), (xm, y1)))
            segs.append(((xm, y1), (x2, y2)))
            return segs
        else:
            # Đi 45 độ rồi đi dọc
            ym = y1 + abs(dx) * dy_sign
            return [
                ((x1, y1), (x2, ym)),
                ((x2, ym), (x2, y2))
            ]
    else:
        if abs(dy) >= abs(dx):
            # Đi dọc rồi bẻ 45 độ
            ym = y2 - abs(dx) * dy_sign
            segs = []
            if abs(ym - y1) > 1e-3:
                segs.append(((x1, y1), (x1, ym)))
            segs.append(((x1, ym), (x2, y2)))
            return segs
        else:
            # Đi 45 độ rồi đi ngang
            xm = x1 + abs(dy) * dx_sign
            return [
                ((x1, y1), (xm, y2)),
                ((xm, y2), (x2, y2))
            ]

def generate_pcb():
    pcb_path = Path("Pi4_Robot_Carrier_1Layer.kicad_pcb")
    content = pcb_path.read_text(encoding="utf-8")

    # 1. Bảng toạ độ đặt linh kiện (Placement Map)
    # (cx, cy, rotation_degrees)
    placement = {
        "J_PI_IDC40": (41.23, 6.00, 0),
        
        "U_DRV_L_CTL": (27.00, 28.86, 0),
        "U_DRV_L_PWR": (12.00, 28.86, 0),
        "J_MOT_L": (5.00, 36.48, 270),
        "R_STBY_L": (27.00, 21.00, 0),

        "U_DRV_R_CTL": (58.00, 23.78, 0),
        "U_DRV_R_PWR": (73.00, 23.78, 0),
        "J_MOT_R": (80.00, 31.40, 270),
        "R_STBY_R": (58.00, 16.00, 0),

        "J_OLED": (12.00, 6.00, 0),
        "R_JMP1": (23.00, 8.54, 0),

        "J_SONAR_L": (6.00, 13.62, 0),
        "R_ECHOL_1": (17.00, 15.00, 0),
        "R_ECHOL_2": (28.00, 15.00, 0),

        "J_SONAR_R": (6.00, 21.24, 0),
        "R_ECHOR_1": (17.00, 22.00, 0),
        "R_ECHOR_2": (28.00, 22.00, 0),

        "J_BAT": (10.00, 58.00, 0),
        "U_BUCK": (33.00, 58.00, 270),
        "J_PWR_PI": (55.00, 58.00, 0)
    }

    # Cập nhật vị trí footprints trong file content
    # Cấu trúc: (footprint ... (at <x> <y> [<rot>]) ... (property "Reference" "<REF>"))
    footprint_starts = [m.start() for m in re.finditer(r'\(footprint\s+"', content)]
    footprint_starts.append(len(content))

    new_content_parts = []
    last_idx = 0

    for i in range(len(footprint_starts) - 1):
        fp_start = footprint_starts[i]
        fp_end = footprint_starts[i+1]
        new_content_parts.append(content[last_idx:fp_start])
        fp_text = content[fp_start:fp_end]

        ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp_text)
        if ref_match:
            ref = ref_match.group(1)
            if ref in placement:
                cx, cy, rot = placement[ref]
                # Thay thế (at <x> <y> [<rot>])
                # Lưu ý: chỉ thay thế (at ...) ở cấp footprint đầu tiên (sau uuid)
                at_repl = f'(at {cx:.2f} {cy:.2f} {rot})' if rot != 0 else f'(at {cx:.2f} {cy:.2f})'
                fp_text = re.sub(r'\(uuid\s+"[^"]+"\)\s+\(at\s+[0-9.-]+\s+[0-9.-]+(?:\s+[0-9.-]+)?\)',
                                lambda m: m.group(0).split('(at')[0] + at_repl, fp_text, count=1)

        # 2. Cập nhật Pad Size (1.8mm x 1.8mm) và Drill (0.8mm) cho TOÀN BỘ thru_hole pad
        fp_text = re.sub(r'\(size\s+[0-9.]+\s+[0-9.]+\)', '(size 1.8 1.8)', fp_text)
        fp_text = re.sub(r'\(drill\s+[0-9.]+\)', '(drill 0.8)', fp_text)

        new_content_parts.append(fp_text)
        last_idx = fp_end

    new_content = "".join(new_content_parts)

    # 3. Trích xuất danh sách tất cả các Pad tuyệt đối cùng Net
    # Map: net_name -> list of (x, y)
    net_pads = {}
    footprint_starts = [m.start() for m in re.finditer(r'\(footprint\s+"', new_content)]
    footprint_starts.append(len(new_content))

    for i in range(len(footprint_starts) - 1):
        fp_text = new_content[footprint_starts[i]:footprint_starts[i+1]]
        ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp_text)
        if not ref_match: continue
        ref = ref_match.group(1)

        at_match = re.search(r'\(at\s+([0-9.-]+)\s+([0-9.-]+)(?:\s+([0-9.-]+))?\)', fp_text)
        if not at_match: continue
        fcx = float(at_match.group(1))
        fcy = float(at_match.group(2))
        frot = float(at_match.group(3)) if at_match.group(3) else 0.0

        rad = math.radians(frot)
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)

        pad_matches = re.finditer(r'\(pad\s+"([^"]+)"\s+\w+\s+\w+\s+\(at\s+([0-9.-]+)\s+([0-9.-]+)[^\)]*\)(.*?)\n\t\t\)', fp_text, re.DOTALL)
        for pm in pad_matches:
            px_rel = float(pm.group(2))
            py_rel = float(pm.group(3))
            rest = pm.group(4)
            net_match = re.search(r'\(net\s+"([^"]+)"\)', rest)
            if not net_match: continue
            net_name = net_match.group(1)

            # Tính toạ độ tuyệt đối
            abs_x = fcx + px_rel * cos_r - py_rel * sin_r
            abs_y = fcy + px_rel * sin_r + py_rel * cos_r

            net_pads.setdefault(net_name, []).append({
                "ref": ref,
                "pad": pm.group(1),
                "x": round(abs_x, 2),
                "y": round(abs_y, 2)
            })

    # Xoá toàn bộ các segment cũ nếu có
    new_content = re.sub(r'\t\(segment\s+.*?\n', '', new_content)

    # 4. Tạo các đường mạch đi dây (Routing Segments)
    segments = []

    # Map tên Net sang Net ID (số) để verify_pcb_drc.py đọc
    # Lấy danh sách net duy nhất
    unique_nets = sorted(list(net_pads.keys()))
    net_to_id = {net_name: idx + 1 for idx, net_name in enumerate(unique_nets)}

    # Cập nhật danh sách Net ở đầu PCB nếu chưa có
    net_decls = []
    for net_name, nid in net_to_id.items():
        net_decls.append(f'\t(net {nid} "{net_name}")')
    net_decl_str = "\n".join(net_decls) + "\n"

    # Thêm vào sau (setup ...)
    setup_idx = new_content.find('(setup\n')
    if setup_idx != -1:
        setup_end = new_content.find('\n\t)', setup_idx) + 3
        # Xoá các net decl cũ nếu có
        new_content = re.sub(r'\t\(net\s+\d+\s+"[^"]*"\)\n', '', new_content)
        setup_idx = new_content.find('(setup\n')
        setup_end = new_content.find('\n\t)', setup_idx) + 3
        new_content = new_content[:setup_end] + "\n" + net_decl_str + new_content[setup_end:]

    def add_route(p1, p2, net_name, width=None, prefer_x_first=True):
        if width is None:
            width = 1.5 if net_name in POWER_NETS else 1.0
        nid = net_to_id[net_name]
        segs = miter_45_path(p1[0], p1[1], p2[0], p2[1], prefer_x_first=prefer_x_first)
        for (sx, sy), (ex, ey) in segs:
            if math.hypot(ex - sx, ey - sy) > 1e-3:
                segments.append((sx, sy, ex, ey, width, nid))

    def add_waypoint_route(points, net_name, width=None):
        if width is None:
            width = 1.5 if net_name in POWER_NETS else 1.0
        nid = net_to_id[net_name]
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i+1]
            # Nếu điểm liền kề chênh nhau x và y, kiểm tra xem có phải 45 độ không
            dx = abs(p2[0] - p1[0])
            dy = abs(p2[1] - p1[1])
            if dx > 1e-3 and dy > 1e-3 and abs(dx - dy) > 1e-3:
                # Cần bẻ miter 45 độ
                segs = miter_45_path(p1[0], p1[1], p2[0], p2[1])
                for (sx, sy), (ex, ey) in segs:
                    if math.hypot(ex - sx, ey - sy) > 1e-3:
                        segments.append((sx, sy, ex, ey, width, nid))
            else:
                segments.append((p1[0], p1[1], p2[0], p2[1], width, nid))

    # Helper tìm toạ độ pad của linh kiện
    def get_pad_pos(ref, pad_num):
        for p in net_pads.get(ref, []):
            if p["pad"] == str(pad_num):
                return (p["x"], p["y"])
        # Tìm trong tất cả nets
        for nname, plist in net_pads.items():
            for p in plist:
                if p["ref"] == ref and p["pad"] == str(pad_num):
                    return (p["x"], p["y"])
        raise ValueError(f"Không tìm thấy pad {pad_num} của {ref}")

    print("--- Bắt đầu định tuyến tự động cho toàn bộ Nets ---")

    # A. CÁC TÍN HIỆU ĐIỀU KHIỂN MOTOR TRÁI (U_DRV_L_CTL <- J_PI_IDC40)
    # 1. DRV_L_PWMA
    p_src = get_pad_pos("J_PI_IDC40", 19)
    p_dst = get_pad_pos("U_DRV_L_CTL", 1)
    add_route(p_src, p_dst, "DRV_L_PWMA")

    # 2. DRV_L_AIN2
    p_src = get_pad_pos("J_PI_IDC40", 21)
    p_dst = get_pad_pos("U_DRV_L_CTL", 2)
    add_route(p_src, p_dst, "DRV_L_AIN2")

    # 3. DRV_L_AIN1
    p_src = get_pad_pos("J_PI_IDC40", 23)
    p_dst = get_pad_pos("U_DRV_L_CTL", 3)
    add_route(p_src, p_dst, "DRV_L_AIN1")

    # 4. DRV_L_STBY -> R_STBY_L Pin 1
    p_src = get_pad_pos("U_DRV_L_CTL", 4)
    p_dst = get_pad_pos("R_STBY_L", 1)
    add_route(p_src, p_dst, "DRV_L_STBY")

    # 5. DRV_L_BIN1
    p_src = get_pad_pos("J_PI_IDC40", 29)
    p_dst = get_pad_pos("U_DRV_L_CTL", 5)
    add_route(p_src, p_dst, "DRV_L_BIN1")

    # 6. DRV_L_BIN2
    p_src = get_pad_pos("J_PI_IDC40", 31)
    p_dst = get_pad_pos("U_DRV_L_CTL", 6)
    add_route(p_src, p_dst, "DRV_L_BIN2")

    # 7. DRV_L_PWMB
    p_src = get_pad_pos("J_PI_IDC40", 33)
    p_dst = get_pad_pos("U_DRV_L_CTL", 7)
    add_route(p_src, p_dst, "DRV_L_PWMB")

    # B. CÁC TÍN HIỆU CÔNG SUẤT MOTOR TRÁI (U_DRV_L_PWR -> J_MOT_L)
    add_route(get_pad_pos("U_DRV_L_PWR", 4), get_pad_pos("J_MOT_L", 1), "DRV_L_AO1")
    add_route(get_pad_pos("U_DRV_L_PWR", 5), get_pad_pos("J_MOT_L", 2), "DRV_L_AO2")
    add_route(get_pad_pos("U_DRV_L_PWR", 6), get_pad_pos("J_MOT_L", 3), "DRV_L_BO2")
    add_route(get_pad_pos("U_DRV_L_PWR", 7), get_pad_pos("J_MOT_L", 4), "DRV_L_BO1")

    # C. CÁC TÍN HIỆU ĐIỀU KHIỂN MOTOR PHẢI (U_DRV_R_CTL <- J_PI_IDC40)
    # 1. DRV_R_PWMA
    add_route(get_pad_pos("J_PI_IDC40", 16), get_pad_pos("U_DRV_R_CTL", 1), "DRV_R_PWMA")
    # 2. DRV_R_AIN2
    add_route(get_pad_pos("J_PI_IDC40", 18), get_pad_pos("U_DRV_R_CTL", 2), "DRV_R_AIN2")
    # 3. DRV_R_AIN1
    add_route(get_pad_pos("J_PI_IDC40", 22), get_pad_pos("U_DRV_R_CTL", 3), "DRV_R_AIN1")
    # 4. DRV_R_STBY -> R_STBY_R Pin 1
    add_route(get_pad_pos("U_DRV_R_CTL", 4), get_pad_pos("R_STBY_R", 1), "DRV_R_STBY")
    # 5. DRV_R_BIN1
    add_route(get_pad_pos("J_PI_IDC40", 24), get_pad_pos("U_DRV_R_CTL", 5), "DRV_R_BIN1")
    # 6. DRV_R_BIN2
    add_route(get_pad_pos("J_PI_IDC40", 26), get_pad_pos("U_DRV_R_CTL", 6), "DRV_R_BIN2")
    # 7. DRV_R_PWMB
    add_route(get_pad_pos("J_PI_IDC40", 32), get_pad_pos("U_DRV_R_CTL", 7), "DRV_R_PWMB")

    # D. CÁC TÍN HIỆU CÔNG SUẤT MOTOR PHẢI (U_DRV_R_PWR -> J_MOT_R)
    add_route(get_pad_pos("U_DRV_R_PWR", 4), get_pad_pos("J_MOT_R", 1), "DRV_R_AO1")
    add_route(get_pad_pos("U_DRV_R_PWR", 5), get_pad_pos("J_MOT_R", 2), "DRV_R_AO2")
    add_route(get_pad_pos("U_DRV_R_PWR", 6), get_pad_pos("J_MOT_R", 3), "DRV_R_BO2")
    add_route(get_pad_pos("U_DRV_R_PWR", 7), get_pad_pos("J_MOT_R", 4), "DRV_R_BO1")

    # E. I2C (OLED 1.3")
    # I2C_SDA: J_PI_IDC40 Pin 3 -> R_JMP1 Pin 2 -> R_JMP1 Pin 1 -> J_OLED Pin 4
    p_pi_sda = get_pad_pos("J_PI_IDC40", 3)
    p_jmp_2 = get_pad_pos("R_JMP1", 2)
    p_jmp_1 = get_pad_pos("R_JMP1", 1)
    p_oled_sda = get_pad_pos("J_OLED", 4)
    add_route(p_pi_sda, p_jmp_2, "I2C_SDA")
    add_route(p_jmp_1, p_oled_sda, "I2C_SDA")

    # I2C_SCL: J_PI_IDC40 Pin 5 -> J_OLED Pin 3 (chui qua gầm R_JMP1)
    p_pi_scl = get_pad_pos("J_PI_IDC40", 5)
    p_oled_scl = get_pad_pos("J_OLED", 3)
    # Đường đi chui qua giữa 2 chân R_JMP1 tại x=28.08, y=10.5
    under_jmp = (28.08, 10.54)
    add_route(p_pi_scl, under_jmp, "I2C_SCL")
    add_route(under_jmp, p_oled_scl, "I2C_SCL")

    # F. CẢM BIẾN SIÊU ÂM TRÁI (J_SONAR_L)
    # SONAR_L_TRIG: J_PI_IDC40 Pin 7 -> J_SONAR_L Pin 2
    add_route(get_pad_pos("J_PI_IDC40", 7), get_pad_pos("J_SONAR_L", 2), "SONAR_L_TRIG")

    # SONAR_L_ECHO_5V: J_SONAR_L Pin 3 -> R_ECHOL_1 Pin 1
    add_route(get_pad_pos("J_SONAR_L", 3), get_pad_pos("R_ECHOL_1", 1), "SONAR_L_ECHO_5V")

    # SONAR_L_ECHO_3V3: R_ECHOL_1 Pin 2 -> R_ECHOL_2 Pin 1 -> J_PI_IDC40 Pin 11
    p_r1_2 = get_pad_pos("R_ECHOL_1", 2)
    p_r2_1 = get_pad_pos("R_ECHOL_2", 1)
    p_pi_echo_l = get_pad_pos("J_PI_IDC40", 11)
    add_route(p_r1_2, p_r2_1, "SONAR_L_ECHO_3V3")
    add_route(p_r2_1, p_pi_echo_l, "SONAR_L_ECHO_3V3")

    # G. CẢM BIẾN SIÊU ÂM PHẢI (J_SONAR_R)
    # SONAR_R_TRIG: J_PI_IDC40 Pin 13 -> J_SONAR_R Pin 2
    add_route(get_pad_pos("J_PI_IDC40", 13), get_pad_pos("J_SONAR_R", 2), "SONAR_R_TRIG")

    # SONAR_R_ECHO_5V: J_SONAR_R Pin 3 -> R_ECHOR_1 Pin 1
    add_route(get_pad_pos("J_SONAR_R", 3), get_pad_pos("R_ECHOR_1", 1), "SONAR_R_ECHO_5V")

    # SONAR_R_ECHO_3V3: R_ECHOR_1 Pin 2 -> R_ECHOR_2 Pin 1 -> J_PI_IDC40 Pin 15
    p_r1_r2 = get_pad_pos("R_ECHOR_1", 2)
    p_r2_r1 = get_pad_pos("R_ECHOR_2", 1)
    p_pi_echo_r = get_pad_pos("J_PI_IDC40", 15)
    add_route(p_r1_r2, p_r2_r1, "SONAR_R_ECHO_3V3")
    add_route(p_r2_r1, p_pi_echo_r, "SONAR_R_ECHO_3V3")

    # H. CÁC ĐƯỜNG NGUỒN CÔNG SUẤT (1.5mm)
    # 1. 12V_BAT (J_BAT Pin 1 -> U_BUCK Pin 1 -> U_DRV_L_PWR Pin 1 & U_DRV_R_PWR Pin 1)
    p_bat_in = get_pad_pos("J_BAT", 1)
    p_buck_in = get_pad_pos("U_BUCK", 1)
    p_drv_l_vm = get_pad_pos("U_DRV_L_PWR", 1)
    p_drv_r_vm = get_pad_pos("U_DRV_R_PWR", 1)
    add_route(p_bat_in, p_buck_in, "12V_BAT", width=1.5)
    add_route(p_bat_in, p_drv_l_vm, "12V_BAT", width=1.5)
    # Tuyến 12V_BAT chạy dọc đáy sang driver phải
    way_12v_r = [(33.0, 62.0), (73.0, 62.0), p_drv_r_vm]
    add_waypoint_route(way_12v_r, "12V_BAT", width=1.5)

    # 2. 5V_BUCK (U_BUCK Pin 3 -> J_PWR_PI Pin 1 & J_SONAR_L Pin 1 & J_SONAR_R Pin 1)
    p_buck_out = get_pad_pos("U_BUCK", 3)
    p_pi_pwr = get_pad_pos("J_PWR_PI", 1)
    p_sonar_l_vcc = get_pad_pos("J_SONAR_L", 1)
    p_sonar_r_vcc = get_pad_pos("J_SONAR_R", 1)
    add_route(p_buck_out, p_pi_pwr, "5V_BUCK", width=1.5)
    add_route(p_sonar_l_vcc, p_sonar_r_vcc, "5V_BUCK", width=1.5)
    # Nối từ Sonar L xuống nguồn 5V_BUCK
    add_route(p_sonar_r_vcc, (6.0, 50.0), "5V_BUCK", width=1.5)
    add_route((6.0, 50.0), p_buck_out, "5V_BUCK", width=1.5)

    # 3. 3V3 (J_PI_IDC40 Pin 1 -> J_OLED Pin 1 -> R_STBY_L Pin 2 & U_DRV_L_PWR Pin 2 & R_STBY_R Pin 2 & U_DRV_R_PWR Pin 2)
    p_pi_3v3 = get_pad_pos("J_PI_IDC40", 1)
    p_oled_3v3 = get_pad_pos("J_OLED", 1)
    p_stby_l_3v3 = get_pad_pos("R_STBY_L", 2)
    p_drv_l_3v3 = get_pad_pos("U_DRV_L_PWR", 2)
    p_stby_r_3v3 = get_pad_pos("R_STBY_R", 2)
    p_drv_r_3v3 = get_pad_pos("U_DRV_R_PWR", 2)
    add_route(p_pi_3v3, p_oled_3v3, "3V3", width=1.5)
    add_route(p_oled_3v3, p_stby_l_3v3, "3V3", width=1.5)
    add_route(p_stby_l_3v3, p_drv_l_3v3, "3V3", width=1.5)
    add_route(p_pi_3v3, p_stby_r_3v3, "3V3", width=1.5)
    add_route(p_stby_r_3v3, p_drv_r_3v3, "3V3", width=1.5)

    # 4. GND (Common Star & Bus)
    # Nối các điểm GND:
    # J_BAT/2, U_BUCK/2, U_BUCK/4, J_PWR_PI/2
    p_bat_gnd = get_pad_pos("J_BAT", 2)
    p_buck_gnd1 = get_pad_pos("U_BUCK", 2)
    p_buck_gnd2 = get_pad_pos("U_BUCK", 4)
    p_pi_pwr_gnd = get_pad_pos("J_PWR_PI", 2)
    add_route(p_bat_gnd, p_buck_gnd1, "GND", width=1.5)
    add_route(p_buck_gnd1, p_buck_gnd2, "GND", width=1.5)
    add_route(p_buck_gnd2, p_pi_pwr_gnd, "GND", width=1.5)

    # GND trên IDC 40-Pin: Pin 6, 34, 39
    p_pi_gnd6 = get_pad_pos("J_PI_IDC40", 6)
    p_pi_gnd34 = get_pad_pos("J_PI_IDC40", 34)
    p_pi_gnd39 = get_pad_pos("J_PI_IDC40", 39)
    add_route(p_pi_gnd39, p_buck_gnd1, "GND", width=1.5)
    add_route(p_pi_gnd34, (50.0, 46.64), "GND", width=1.5)
    add_route((50.0, 46.64), p_pi_pwr_gnd, "GND", width=1.5)
    add_route(p_pi_gnd6, (50.0, 11.08), "GND", width=1.5)
    add_route((50.0, 11.08), (50.0, 46.64), "GND", width=1.5)

    # GND Driver L: U_DRV_L_CTL Pin 8, U_DRV_L_PWR Pin 3 & Pin 8
    p_drv_l_gnd_ctl = get_pad_pos("U_DRV_L_CTL", 8)
    p_drv_l_gnd_pwr1 = get_pad_pos("U_DRV_L_PWR", 3)
    p_drv_l_gnd_pwr2 = get_pad_pos("U_DRV_L_PWR", 8)
    add_route(p_drv_l_gnd_ctl, p_pi_gnd39, "GND", width=1.5)
    add_route(p_drv_l_gnd_pwr2, p_drv_l_gnd_ctl, "GND", width=1.5)
    add_route(p_drv_l_gnd_pwr1, (12.0, 33.94), "GND", width=1.5)

    # GND Driver R: U_DRV_R_CTL Pin 8, U_DRV_R_PWR Pin 3 & Pin 8
    p_drv_r_gnd_ctl = get_pad_pos("U_DRV_R_CTL", 8)
    p_drv_r_gnd_pwr1 = get_pad_pos("U_DRV_R_PWR", 3)
    p_drv_r_gnd_pwr2 = get_pad_pos("U_DRV_R_PWR", 8)
    add_route(p_drv_r_gnd_ctl, p_pi_gnd34, "GND", width=1.5)
    add_route(p_drv_r_gnd_pwr2, p_drv_r_gnd_ctl, "GND", width=1.5)

    # GND Sensors & OLED:
    # J_OLED Pin 2, J_SONAR_L Pin 4, R_ECHOL_2 Pin 2, J_SONAR_R Pin 4, R_ECHOR_2 Pin 2
    p_oled_gnd = get_pad_pos("J_OLED", 2)
    p_sonarl_gnd = get_pad_pos("J_SONAR_L", 4)
    p_r2l_gnd = get_pad_pos("R_ECHOL_2", 2)
    p_sonarr_gnd = get_pad_pos("J_SONAR_R", 4)
    p_r2r_gnd = get_pad_pos("R_ECHOR_2", 2)
    add_route(p_oled_gnd, p_sonarl_gnd, "GND", width=1.5)
    add_route(p_sonarl_gnd, p_r2l_gnd, "GND", width=1.5)
    add_route(p_sonarl_gnd, p_sonarr_gnd, "GND", width=1.5)
    add_route(p_sonarr_gnd, p_r2r_gnd, "GND", width=1.5)
    add_route(p_r2r_gnd, p_bat_gnd, "GND", width=1.5)

    print(f"Tổng số đoạn segment được sinh ra: {len(segments)}")

    # Ghi toàn bộ segments vào new_content ngay trước dấu đóng ngoặc cuối file
    segment_strings = []
    for sx, sy, ex, ey, w, nid in segments:
        seg_str = f'\t(segment (start {sx:.2f} {sy:.2f}) (end {ex:.2f} {ey:.2f}) (width {w:.1f}) (layer "B.Cu") (net {nid}))'
        segment_strings.append(seg_str)

    all_segments_str = "\n".join(segment_strings) + "\n"
    last_bracket = new_content.rfind(')')
    final_content = new_content[:last_bracket] + all_segments_str + new_content[last_bracket:]

    pcb_path.write_text(final_content, encoding="utf-8")
    print(f"[THÀNH CÔNG] Đã tạo file PCB hoàn chỉnh: {pcb_path}")

if __name__ == "__main__":
    generate_pcb()
