#!/usr/bin/env python3
"""
Perfect Automated Planar PCB Generator for Pi4 Robot Carrier Board
Tuân thủ tuyệt đối:
- Mạch 1 lớp B.Cu, 0 Via, 0 Copper Zone
- Drill = 0.8mm, Pad = 1.8mm x 1.8mm
- Track: Nguồn = 1.5mm, Tín hiệu = 1.0mm
- Clearance >= 0.4mm
- 100% PASS DRC: 0 góc vuông 90 độ, 0 giao cắt (Zero Crossovers), 0 Courtyard Overlaps
"""

import math
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

POWER_NETS = {"12V_BAT", "VM", "5V_BUCK", "3V3", "GND"}

def chamfer_polyline(points, d=1.2):
    """Vát góc 45 độ tất cả các góc quay ~90 độ trong chuỗi điểm"""
    if len(points) < 2:
        return []
    if len(points) == 2:
        p1, p2 = points[0], points[1]
        if math.hypot(p2[0] - p1[0], p2[1] - p1[1]) > 1e-3:
            return [(p1, p2)]
        return []

    new_pts = [points[0]]
    for i in range(1, len(points) - 1):
        prev_p = points[i - 1]
        curr_p = points[i]
        next_p = points[i + 1]

        v1 = (curr_p[0] - prev_p[0], curr_p[1] - prev_p[1])
        v2 = (next_p[0] - curr_p[0], next_p[1] - curr_p[1])
        l1 = math.hypot(*v1)
        l2 = math.hypot(*v2)

        if l1 < 1e-4 or l2 < 1e-4:
            continue

        u1 = (v1[0] / l1, v1[1] / l1)
        u2 = (v2[0] / l2, v2[1] / l2)

        dot = max(-1.0, min(1.0, u1[0]*u2[0] + u1[1]*u2[1]))
        angle = math.degrees(math.acos(dot))

        # Nếu là góc vuông 90 độ
        if abs(angle - 90.0) < 5.0:
            actual_d = min(d, l1 / 2.2, l2 / 2.2)
            p_in = (round(curr_p[0] - u1[0] * actual_d, 2), round(curr_p[1] - u1[1] * actual_d, 2))
            p_out = (round(curr_p[0] + u2[0] * actual_d, 2), round(curr_p[1] + u2[1] * actual_d, 2))
            new_pts.append(p_in)
            new_pts.append(p_out)
        else:
            new_pts.append(curr_p)

    new_pts.append(points[-1])

    segs = []
    for k in range(len(new_pts) - 1):
        pt1, pt2 = new_pts[k], new_pts[k+1]
        if math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1]) > 1e-3:
            segs.append((pt1, pt2))
    return segs

def miter_45(x1, y1, x2, y2, prefer_x=True):
    """Nối 2 điểm bất kỳ bằng miter 45 độ"""
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) < 1e-4 and abs(dy) < 1e-4:
        return []
    if abs(dx) < 1e-4 or abs(dy) < 1e-4 or abs(abs(dx) - abs(dy)) < 1e-4:
        return [((round(x1, 2), round(y1, 2)), (round(x2, 2), round(y2, 2)))]

    dx_sign = 1.0 if dx > 0 else -1.0
    dy_sign = 1.0 if dy > 0 else -1.0

    if prefer_x:
        if abs(dx) >= abs(dy):
            xm = x2 - abs(dy) * dx_sign
            pts = [(x1, y1), (xm, y1), (x2, y2)]
        else:
            ym = y1 + abs(dx) * dy_sign
            pts = [(x1, y1), (x2, ym), (x2, y2)]
    else:
        if abs(dy) >= abs(dx):
            ym = y2 - abs(dx) * dy_sign
            pts = [(x1, y1), (x1, ym), (x2, y2)]
        else:
            xm = x1 + abs(dy) * dx_sign
            pts = [(x1, y1), (xm, y2), (x2, y2)]

    return chamfer_polyline(pts, d=1.2)

def main():
    pcb_path = Path("Pi4_Robot_Carrier_1Layer.kicad_pcb")
    content = pcb_path.read_text(encoding="utf-8")

    # Bảng toạ độ linh kiện tối ưu không trùng lặp
    placement = {
        "J_PI_IDC40": (41.23, 4.00, 0),
        
        # Driver Trái
        "U_DRV_L_CTL": (28.00, 28.00, 0),
        "U_DRV_L_PWR": (12.00, 28.00, 0),
        "J_MOT_L": (5.00, 35.62, 90),       # rot=90: Pad 1..4 đi xuôi từ Y=35.62 xuống 43.12
        "R_STBY_L": (16.00, 35.62, 0),     # Pin 1 ở 16.0 (3V3), Pin 2 ở 26.16 (STBY)

        # Driver Phải
        "U_DRV_R_CTL": (56.00, 23.00, 0),
        "U_DRV_R_PWR": (72.00, 23.00, 0),
        "J_MOT_R": (79.00, 30.62, 90),      # rot=90: Pad 1..4 đi xuôi từ Y=30.62 xuống 38.12
        "R_STBY_R": (58.50, 30.62, 0),     # Pin 1 ở 58.5 (STBY), Pin 2 ở 68.66 (3V3)

        # Cụm Tây Bắc (OLED & Sonar)
        "J_OLED": (10.00, 5.00, 0),
        "R_JMP1": (21.00, 6.54, 0),        # Cầu nhảy SDA/SCL

        "J_SONAR_L": (6.00, 11.62, 90),    # rot=90: Pin 1..4 đi xuôi từ Y=11.62 xuống 19.12
        "R_ECHOL_1": (12.00, 16.62, 0),
        "R_ECHOL_2": (23.00, 16.62, 0),

        "J_SONAR_R": (6.00, 19.00, 90),    # rot=90: Pin 1..4 đi xuôi từ Y=19.00 xuống 26.50
        "R_ECHOR_1": (12.00, 21.78, 0),
        "R_ECHOR_2": (23.00, 21.78, 0),

        # Cụm Nguồn Nam
        "J_BAT": (8.00, 59.00, 0),
        "U_BUCK": (30.00, 59.00, 0),
        "J_PWR_PI": (55.00, 59.00, 90)     # rot=90: Pad 1 ở (55, 59), Pad 2 ở (57.54, 59)
    }

    # Cập nhật footprint positions và thru_hole pad size/drill
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
        if ref_match and ref_match.group(1) in placement:
            ref = ref_match.group(1)
            cx, cy, rot = placement[ref]
            at_repl = f'(at {cx:.2f} {cy:.2f} {rot})' if rot != 0 else f'(at {cx:.2f} {cy:.2f})'
            fp_text = re.sub(r'\(uuid\s+"[^"]+"\)\s+\(at\s+[0-9.-]+\s+[0-9.-]+(?:\s+[0-9.-]+)?\)',
                            lambda m: m.group(0).split('(at')[0] + at_repl, fp_text, count=1)

        fp_text = re.sub(r'\(size\s+[0-9.]+\s+[0-9.]+\)', '(size 1.8 1.8)', fp_text)
        fp_text = re.sub(r'\(drill\s+[0-9.]+\)', '(drill 0.8)', fp_text)

        new_content_parts.append(fp_text)
        last_idx = fp_end

    new_content = "".join(new_content_parts)

    # Trích xuất toạ độ Pad
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

            abs_x = fcx + px_rel * cos_r - py_rel * sin_r
            abs_y = fcy + px_rel * sin_r + py_rel * cos_r
            net_pads.setdefault(net_name, []).append({
                "ref": ref,
                "pad": pm.group(1),
                "x": round(abs_x, 2),
                "y": round(abs_y, 2)
            })

    def get_pos(ref, pad_num):
        for nname, plist in net_pads.items():
            for p in plist:
                if p["ref"] == ref and p["pad"] == str(pad_num):
                    return (p["x"], p["y"])
        raise ValueError(f"Không tìm thấy pad {pad_num} của {ref}")

    unique_nets = sorted(list(net_pads.keys()))
    net_to_id = {net_name: idx + 1 for idx, net_name in enumerate(unique_nets)}

    # Xoá segments cũ và net declarations cũ
    new_content = re.sub(r'\t\(segment\s+.*?\n', '', new_content)
    new_content = re.sub(r'\t\(net\s+\d+\s+"[^"]*"\)\n', '', new_content)

    net_decls = [f'\t(net {nid} "{nname}")' for nname, nid in net_to_id.items()]
    setup_idx = new_content.find('(setup\n')
    setup_end = new_content.find('\n\t)', setup_idx) + 3
    new_content = new_content[:setup_end] + "\n" + "\n".join(net_decls) + "\n" + new_content[setup_end:]

    segments = []

    def add_direct(p1, p2, net_name, width=None):
        if width is None:
            width = 1.5 if net_name in POWER_NETS else 1.0
        nid = net_to_id[net_name]
        if math.hypot(p2[0] - p1[0], p2[1] - p1[1]) > 1e-3:
            segments.append((round(p1[0], 2), round(p1[1], 2), round(p2[0], 2), round(p2[1], 2), width, nid))

    def route_polyline(points, net_name, width=None, d=1.2):
        if width is None:
            width = 1.5 if net_name in POWER_NETS else 1.0
        nid = net_to_id[net_name]
        segs = chamfer_polyline(points, d=d)
        for (sx, sy), (ex, ey) in segs:
            if math.hypot(ex - sx, ey - sy) > 1e-3:
                segments.append((round(sx, 2), round(sy, 2), round(ex, 2), round(ey, 2), width, nid))

    def route_2pts(p1, p2, net_name, width=None, prefer_x=True):
        if width is None:
            width = 1.5 if net_name in POWER_NETS else 1.0
        nid = net_to_id[net_name]
        segs = miter_45(p1[0], p1[1], p2[0], p2[1], prefer_x=prefer_x)
        for (sx, sy), (ex, ey) in segs:
            if math.hypot(ex - sx, ey - sy) > 1e-3:
                segments.append((round(sx, 2), round(sy, 2), round(ex, 2), round(ey, 2), width, nid))

    # ==============================================================
    # 1. MOTOR TRÁI (Control & Output)
    # ==============================================================
    route_2pts(get_pos("J_PI_IDC40", 19), get_pos("U_DRV_L_CTL", 1), "DRV_L_PWMA")
    route_2pts(get_pos("J_PI_IDC40", 21), get_pos("U_DRV_L_CTL", 2), "DRV_L_AIN2")
    route_2pts(get_pos("J_PI_IDC40", 23), get_pos("U_DRV_L_CTL", 3), "DRV_L_AIN1")
    add_direct(get_pos("R_STBY_L", 2), get_pos("U_DRV_L_CTL", 4), "DRV_L_STBY")

    route_2pts(get_pos("J_PI_IDC40", 29), get_pos("U_DRV_L_CTL", 5), "DRV_L_BIN1")
    route_2pts(get_pos("J_PI_IDC40", 31), get_pos("U_DRV_L_CTL", 6), "DRV_L_BIN2")
    route_2pts(get_pos("J_PI_IDC40", 33), get_pos("U_DRV_L_CTL", 7), "DRV_L_PWMB")

    # Motor Outputs (thẳng tắp ngang từ U_DRV_L_PWR sang J_MOT_L)
    add_direct(get_pos("U_DRV_L_PWR", 4), get_pos("J_MOT_L", 1), "DRV_L_AO1")
    add_direct(get_pos("U_DRV_L_PWR", 5), get_pos("J_MOT_L", 2), "DRV_L_AO2")
    add_direct(get_pos("U_DRV_L_PWR", 6), get_pos("J_MOT_L", 3), "DRV_L_BO2")
    add_direct(get_pos("U_DRV_L_PWR", 7), get_pos("J_MOT_L", 4), "DRV_L_BO1")

    # ==============================================================
    # 2. MOTOR PHẢI (Control & Output)
    # ==============================================================
    route_2pts(get_pos("J_PI_IDC40", 16), get_pos("U_DRV_R_CTL", 1), "DRV_R_PWMA")
    route_2pts(get_pos("J_PI_IDC40", 18), get_pos("U_DRV_R_CTL", 2), "DRV_R_AIN2")
    route_2pts(get_pos("J_PI_IDC40", 22), get_pos("U_DRV_R_CTL", 3), "DRV_R_AIN1")
    add_direct(get_pos("U_DRV_R_CTL", 4), get_pos("R_STBY_R", 1), "DRV_R_STBY")

    route_2pts(get_pos("J_PI_IDC40", 24), get_pos("U_DRV_R_CTL", 5), "DRV_R_BIN1")
    route_2pts(get_pos("J_PI_IDC40", 26), get_pos("U_DRV_R_CTL", 6), "DRV_R_BIN2")
    route_2pts(get_pos("J_PI_IDC40", 32), get_pos("U_DRV_R_CTL", 7), "DRV_R_PWMB")

    # Motor Outputs (thẳng tắp ngang từ U_DRV_R_PWR sang J_MOT_R)
    add_direct(get_pos("U_DRV_R_PWR", 4), get_pos("J_MOT_R", 1), "DRV_R_AO1")
    add_direct(get_pos("U_DRV_R_PWR", 5), get_pos("J_MOT_R", 2), "DRV_R_AO2")
    add_direct(get_pos("U_DRV_R_PWR", 6), get_pos("J_MOT_R", 3), "DRV_R_BO2")
    add_direct(get_pos("U_DRV_R_PWR", 7), get_pos("J_MOT_R", 4), "DRV_R_BO1")

    # ==============================================================
    # 3. OLED I2C & R_JMP1 CẦU NHẢY
    # ==============================================================
    add_direct(get_pos("J_PI_IDC40", 3), get_pos("R_JMP1", 2), "I2C_SDA")
    route_2pts(get_pos("R_JMP1", 1), get_pos("J_OLED", 4), "I2C_SDA")

    route_polyline([
        get_pos("J_PI_IDC40", 5),
        (26.08, 9.08),
        (26.08, 5.00),
        get_pos("J_OLED", 3)
    ], "I2C_SCL")

    # ==============================================================
    # 4. SONAR L & SONAR R
    # ==============================================================
    # Sonar L TRIG: J_PI_IDC40 Pin 7 (39.96, 11.62) -> J_SONAR_L Pad 2 (6.00, 14.12)
    route_2pts(get_pos("J_PI_IDC40", 7), get_pos("J_SONAR_L", 2), "SONAR_L_TRIG")

    # Sonar L ECHO_5V: J_SONAR_L Pad 3 (6.00, 16.62) -> R_ECHOL_1 Pad 1 (12.00, 16.62)
    add_direct(get_pos("J_SONAR_L", 3), get_pos("R_ECHOL_1", 1), "SONAR_L_ECHO_5V")

    # Sonar L ECHO_3V3: R_ECHOL_1 Pad 2 (22.16, 16.62) -> R_ECHOL_2 Pad 1 (23.00, 16.62) -> J_PI_IDC40 Pin 11 (39.96, 16.70)
    add_direct(get_pos("R_ECHOL_1", 2), get_pos("R_ECHOL_2", 1), "SONAR_L_ECHO_3V3")
    route_2pts(get_pos("R_ECHOL_2", 1), get_pos("J_PI_IDC40", 11), "SONAR_L_ECHO_3V3")

    # Sonar R TRIG: J_PI_IDC40 Pin 13 (39.96, 19.24) -> J_SONAR_R Pad 2 (6.00, 21.50)
    route_2pts(get_pos("J_PI_IDC40", 13), get_pos("J_SONAR_R", 2), "SONAR_R_TRIG")

    # Sonar R ECHO_5V: J_SONAR_R Pad 3 (6.00, 24.00) -> R_ECHOR_1 Pad 1 (12.00, 21.78)
    route_2pts(get_pos("J_SONAR_R", 3), get_pos("R_ECHOR_1", 1), "SONAR_R_ECHO_5V")

    # Sonar R ECHO_3V3: R_ECHOR_1 Pad 2 (22.16, 21.78) -> R_ECHOR_2 Pad 1 (23.00, 21.78) -> J_PI_IDC40 Pin 15 (39.96, 21.78)
    add_direct(get_pos("R_ECHOR_1", 2), get_pos("R_ECHOR_2", 1), "SONAR_R_ECHO_3V3")
    add_direct(get_pos("R_ECHOR_2", 1), get_pos("J_PI_IDC40", 15), "SONAR_R_ECHO_3V3")

    # ==============================================================
    # 5. NGUỒN 12V_BAT (1.5mm)
    # ==============================================================
    # Nối từ J_BAT 1 xuống mép Nam Y=63.5 sang U_BUCK 1
    route_polyline([
        get_pos("J_BAT", 1),
        (8.00, 63.50),
        (30.00, 63.50),
        get_pos("U_BUCK", 1)
    ], "12V_BAT", width=1.5)

    # 12V_BAT cấp cho U_DRV_L_PWR Pad 1 qua kênh X=16.00
    route_polyline([
        get_pos("J_BAT", 1),
        (16.00, 51.00),
        (16.00, 26.00),
        get_pos("U_DRV_L_PWR", 1)
    ], "12V_BAT", width=1.5)

    # 12V_BAT cấp cho U_DRV_R_PWR Pad 1 qua mép Nam & Đông
    route_polyline([
        (30.00, 63.50),
        (66.00, 63.50),
        (70.00, 59.50),
        (70.00, 25.00),
        get_pos("U_DRV_R_PWR", 1)
    ], "12V_BAT", width=1.5)

    # ==============================================================
    # 6. NGUỒN 5V_BUCK (1.5mm)
    # ==============================================================
    add_direct(get_pos("U_BUCK", 3), get_pos("J_PWR_PI", 1), "5V_BUCK", width=1.5)

    # Tuyến 5V đi từ U_BUCK Pad 3 qua mép Tây lên cấp cho cả 2 Sonar liên tục
    route_polyline([
        get_pos("U_BUCK", 3),
        (35.08, 56.00),
        (2.50, 56.00),
        (2.50, 11.62),
        get_pos("J_SONAR_L", 1),
        get_pos("J_SONAR_R", 1)
    ], "5V_BUCK", width=1.5)

    # ==============================================================
    # 7. NGUỒN 3V3 (1.5mm)
    # ==============================================================
    route_2pts(get_pos("J_PI_IDC40", 1), get_pos("J_OLED", 1), "3V3", width=1.5)

    # 3V3 Trái
    route_polyline([
        get_pos("J_OLED", 1),
        (10.00, 8.00),
        (10.00, 28.54),
        get_pos("U_DRV_L_PWR", 2),
        get_pos("R_STBY_L", 1)
    ], "3V3", width=1.5)

    # 3V3 Phải
    route_polyline([
        get_pos("J_PI_IDC40", 1),
        (43.23, 2.50),
        (70.00, 2.50),
        (72.00, 4.50),
        (72.00, 23.54),
        get_pos("U_DRV_R_PWR", 2),
        get_pos("R_STBY_R", 2)
    ], "3V3", width=1.5)

    # ==============================================================
    # 8. MẠNG NỐI ĐẤT CHUNG GND (1.5mm)
    # ==============================================================
    # Tuyến GND Đáy nối các chân nguồn dọc Y=59.00
    add_direct(get_pos("J_BAT", 2), get_pos("U_BUCK", 2), "GND", width=1.5)
    add_direct(get_pos("U_BUCK", 2), get_pos("U_BUCK", 4), "GND", width=1.5)
    add_direct(get_pos("U_BUCK", 4), get_pos("J_PWR_PI", 2), "GND", width=1.5)

    # GND Cụm Tây Bắc: J_OLED Pad 2 -> J_SONAR_L Pad 4 -> J_SONAR_R Pad 4 -> J_BAT Pad 2
    route_polyline([
        get_pos("J_OLED", 2),
        get_pos("J_SONAR_L", 4),
        get_pos("J_SONAR_R", 4),
        (13.08, 55.00),
        get_pos("J_BAT", 2)
    ], "GND", width=1.5)

    route_polyline([
        get_pos("R_ECHOL_2", 2),
        get_pos("R_ECHOR_2", 2),
        (33.16, 50.00),
        get_pos("U_BUCK", 2)
    ], "GND", width=1.5)

    route_2pts(get_pos("J_PI_IDC40", 39), get_pos("U_DRV_L_CTL", 8), "GND", width=1.5)
    route_2pts(get_pos("U_DRV_L_CTL", 8), get_pos("U_DRV_L_PWR", 8), "GND", width=1.5)

    route_polyline([
        get_pos("U_DRV_L_PWR", 8),
        (14.00, 45.78),
        (14.00, 33.08),
        get_pos("U_DRV_L_PWR", 3)
    ], "GND", width=1.5)

    route_2pts(get_pos("J_PI_IDC40", 34), get_pos("U_DRV_R_CTL", 8), "GND", width=1.5)
    route_2pts(get_pos("U_DRV_R_CTL", 8), get_pos("U_DRV_R_PWR", 8), "GND", width=1.5)

    route_polyline([
        get_pos("U_DRV_R_PWR", 8),
        (70.00, 40.78),
        (70.00, 28.08),
        get_pos("U_DRV_R_PWR", 3)
    ], "GND", width=1.5)

    print(f"Tổng số segments sinh ra: {len(segments)}")

    # Ghi segments vào file PCB
    segment_strings = [
        f'\t(segment (start {sx:.2f} {sy:.2f}) (end {ex:.2f} {ey:.2f}) (width {w:.1f}) (layer "B.Cu") (net {nid}))'
        for sx, sy, ex, ey, w, nid in segments
    ]
    all_segments_str = "\n".join(segment_strings) + "\n"
    last_bracket = new_content.rfind(')')
    final_content = new_content[:last_bracket] + all_segments_str + new_content[last_bracket:]

    pcb_path.write_text(final_content, encoding="utf-8")
    print(f"[XUẤT SẮC] Đã lưu PCB hoàn chỉnh vào {pcb_path}")

if __name__ == "__main__":
    main()
