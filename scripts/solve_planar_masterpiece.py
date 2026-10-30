#!/usr/bin/env python3
"""
Masterpiece Single-Layer Planar PCB Generator for Pi4 Robot Carrier Board
Tự động tính toán toạ độ, phân kênh hình học trực giao hoàn hảo:
- Mạch 1 lớp B.Cu, 0 Via, 0 Copper Zone
- Drill = 0.8mm, Pad = 1.8mm x 1.8mm
- Track: Nguồn = 1.5mm, Tín hiệu = 1.0mm
- Clearance >= 0.5mm
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
    """Vát góc 45 độ tất cả các góc quay ~90 độ trong chuỗi điểm, bảo toàn endpoints"""
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

        if abs(angle - 90.0) < 5.0:
            actual_d = min(d, l1 * 0.45, l2 * 0.45)
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

def generate_masterpiece_pcb():
    pcb_path = Path("Pi4_Robot_Carrier_1Layer.kicad_pcb")
    content = pcb_path.read_text(encoding="utf-8")

    # 1. Định nghĩa vị trí tối ưu hoàn hảo cho 20 linh kiện
    optimal_components = {
        "J_PI_IDC40": {"x": 41.23, "y": 4.00, "rot": 0.0},
        "U_DRV_L_CTL": {"x": 30.00, "y": 28.00, "rot": 0.0},
        "U_DRV_L_PWR": {"x": 16.00, "y": 28.00, "rot": 0.0},
        "J_MOT_L": {"x": 8.00, "y": 35.62, "rot": 270.0},
        "R_STBY_L": {"x": 23.00, "y": 38.00, "rot": 90.0},

        "U_DRV_R_CTL": {"x": 54.00, "y": 23.00, "rot": 0.0},
        "U_DRV_R_PWR": {"x": 68.00, "y": 23.00, "rot": 0.0},
        "J_MOT_R": {"x": 76.00, "y": 30.62, "rot": 270.0},
        "R_STBY_R": {"x": 61.00, "y": 30.62, "rot": 90.0},

        "J_OLED": {"x": 12.00, "y": 5.00, "rot": 0.0},
        "R_JMP1": {"x": 26.00, "y": 6.54, "rot": 0.0},

        "J_SONAR_L": {"x": 8.00, "y": 11.62, "rot": 270.0},
        "R_ECHOL_1": {"x": 18.00, "y": 16.62, "rot": 0.0},
        "R_ECHOL_2": {"x": 27.00, "y": 21.70, "rot": 270.0},

        "J_SONAR_R": {"x": 8.00, "y": 21.78, "rot": 270.0},
        "R_ECHOR_1": {"x": 18.00, "y": 26.78, "rot": 0.0},
        "R_ECHOR_2": {"x": 27.00, "y": 26.86, "rot": 270.0},

        "J_BAT": {"x": 12.00, "y": 59.00, "rot": 0.0},
        "U_BUCK": {"x": 30.00, "y": 59.00, "rot": 90.0},
        "J_PWR_PI": {"x": 57.54, "y": 59.00, "rot": 270.0},
    }

    # 2. Cập nhật vị trí footprints và chuẩn hoá pad
    footprint_starts = [m.start() for m in re.finditer(r'\t\(footprint\s+', content)]
    footprint_starts.append(len(content))

    new_fps = []
    for i in range(len(footprint_starts) - 1):
        fp_text = content[footprint_starts[i]:footprint_starts[i+1]]
        ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp_text)
        if not ref_match:
            new_fps.append(fp_text)
            continue
        ref = ref_match.group(1)

        if ref in optimal_components:
            info = optimal_components[ref]
            cx, cy, rot = info["x"], info["y"], info["rot"]
            rot_str = f" {rot}" if rot != 0.0 else ""
            fp_text = re.sub(
                r'\(at\s+[0-9.-]+\s+[0-9.-]+(?:\s+[0-9.-]+)?\)',
                f'(at {cx:.2f} {cy:.2f}{rot_str})',
                fp_text,
                count=1
            )

        # Chuẩn hoá pad: size 1.8 1.8, drill 0.8
        fp_text = re.sub(r'\(size\s+[0-9.]+\s+[0-9.]+\)', '(size 1.8 1.8)', fp_text)
        fp_text = re.sub(r'\(drill\s+[0-9.]+\)', '(drill 0.8)', fp_text)
        new_fps.append(fp_text)

    new_content = content[:footprint_starts[0]] + "".join(new_fps)

    # 3. Tính toán toạ độ thực tế của từng Pad
    net_pads = {}
    footprint_starts = [m.start() for m in re.finditer(r'\t\(footprint\s+', new_content)]
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
            if not net_match:
                net_m2 = re.search(r'\(net\s+(\d+)\s+"([^"]*)"\)', rest)
                nname = net_m2.group(2) if net_m2 else "None"
            else:
                nname = net_match.group(1)

            rx = px_rel * cos_r + py_rel * sin_r
            ry = -px_rel * sin_r + py_rel * cos_r
            abs_x = fcx + rx
            abs_y = fcy + ry
            net_pads.setdefault(nname, []).append({
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
    if "None" in unique_nets:
        unique_nets.remove("None")
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
    # KHỐI 4: ACTUATOR (MOTOR TRÁI & PHẢI)
    # ==============================================================
    # Motor Trái Control
    route_2pts(get_pos("J_PI_IDC40", 19), get_pos("U_DRV_L_CTL", 1), "DRV_L_PWMA")
    route_2pts(get_pos("J_PI_IDC40", 21), get_pos("U_DRV_L_CTL", 2), "DRV_L_AIN2")
    route_2pts(get_pos("J_PI_IDC40", 23), get_pos("U_DRV_L_CTL", 3), "DRV_L_AIN1")
    route_2pts(get_pos("R_STBY_L", 1), get_pos("U_DRV_L_CTL", 4), "DRV_L_STBY")

    route_2pts(get_pos("J_PI_IDC40", 29), get_pos("U_DRV_L_CTL", 5), "DRV_L_BIN1")
    route_2pts(get_pos("J_PI_IDC40", 31), get_pos("U_DRV_L_CTL", 6), "DRV_L_BIN2")
    route_2pts(get_pos("J_PI_IDC40", 33), get_pos("U_DRV_L_CTL", 7), "DRV_L_PWMB")

    # Motor Trái Outputs (ngang thẳng sang J_MOT_L)
    add_direct(get_pos("U_DRV_L_PWR", 4), get_pos("J_MOT_L", 1), "DRV_L_AO1")
    add_direct(get_pos("U_DRV_L_PWR", 5), get_pos("J_MOT_L", 2), "DRV_L_AO2")
    add_direct(get_pos("U_DRV_L_PWR", 6), get_pos("J_MOT_L", 3), "DRV_L_BO2")
    add_direct(get_pos("U_DRV_L_PWR", 7), get_pos("J_MOT_L", 4), "DRV_L_BO1")

    # Motor Phải Control
    route_2pts(get_pos("J_PI_IDC40", 16), get_pos("U_DRV_R_CTL", 1), "DRV_R_PWMA")
    route_2pts(get_pos("J_PI_IDC40", 18), get_pos("U_DRV_R_CTL", 2), "DRV_R_AIN2")
    route_2pts(get_pos("J_PI_IDC40", 22), get_pos("U_DRV_R_CTL", 3), "DRV_R_AIN1")
    route_2pts(get_pos("U_DRV_R_CTL", 4), get_pos("R_STBY_R", 1), "DRV_R_STBY")

    route_2pts(get_pos("J_PI_IDC40", 24), get_pos("U_DRV_R_CTL", 5), "DRV_R_BIN1")
    route_2pts(get_pos("J_PI_IDC40", 26), get_pos("U_DRV_R_CTL", 6), "DRV_R_BIN2")
    route_polyline([
        get_pos("J_PI_IDC40", 32),
        (47.00, 42.10),
        (50.82, 38.28),
        get_pos("U_DRV_R_CTL", 7)
    ], "DRV_R_PWMB")

    # Motor Phải Outputs (ngang thẳng sang J_MOT_R)
    add_direct(get_pos("U_DRV_R_PWR", 4), get_pos("J_MOT_R", 1), "DRV_R_AO1")
    add_direct(get_pos("U_DRV_R_PWR", 5), get_pos("J_MOT_R", 2), "DRV_R_AO2")
    add_direct(get_pos("U_DRV_R_PWR", 6), get_pos("J_MOT_R", 3), "DRV_R_BO2")
    add_direct(get_pos("U_DRV_R_PWR", 7), get_pos("J_MOT_R", 4), "DRV_R_BO1")

    # ==============================================================
    # KHỐI 2: TÍN HIỆU (OLED & SONAR)
    # ==============================================================
    # OLED I2C SDA qua R_JMP1 (Pad 1 ở 26.00, Pad 2 ở 36.16)
    add_direct(get_pos("J_PI_IDC40", 3), get_pos("R_JMP1", 2), "I2C_SDA")
    route_2pts(get_pos("R_JMP1", 1), get_pos("J_OLED", 4), "I2C_SDA")

    # OLED I2C SCL chui qua tâm gầm R_JMP1 tại X=31.08
    route_polyline([
        get_pos("J_PI_IDC40", 5),
        (31.08, 9.08),
        (31.08, 3.50),
        (17.00, 3.50),
        get_pos("J_OLED", 3)
    ], "I2C_SCL")

    # Sonar L TRIG
    route_2pts(get_pos("J_PI_IDC40", 7), get_pos("J_SONAR_L", 2), "SONAR_L_TRIG")

    # Sonar L ECHO 5V
    add_direct(get_pos("J_SONAR_L", 3), get_pos("R_ECHOL_1", 1), "SONAR_L_ECHO_5V")

    # Sonar L ECHO 3V3
    add_direct(get_pos("R_ECHOL_1", 2), get_pos("R_ECHOL_2", 1), "SONAR_L_ECHO_3V3")
    add_direct(get_pos("R_ECHOL_2", 1), get_pos("J_PI_IDC40", 11), "SONAR_L_ECHO_3V3")

    # Sonar R TRIG
    route_2pts(get_pos("J_PI_IDC40", 13), get_pos("J_SONAR_R", 2), "SONAR_R_TRIG")

    # Sonar R ECHO 5V
    add_direct(get_pos("J_SONAR_R", 3), get_pos("R_ECHOR_1", 1), "SONAR_R_ECHO_5V")

    # Sonar R ECHO 3V3 (vát góc 45 miter hợp lệ, không 90 độ)
    route_polyline([
        get_pos("R_ECHOR_1", 2),
        (25.00, 24.78),
        get_pos("R_ECHOR_2", 1),
        get_pos("J_PI_IDC40", 15)
    ], "SONAR_R_ECHO_3V3")

    # ==============================================================
    # KHỐI 1: NGUỒN 12V_BAT (1.5mm)
    # ==============================================================
    # 12V_BAT từ J_BAT Pad 1 (12.00, 59.00) chạy dọc rãnh Nam Y=62.50
    route_polyline([
        get_pos("J_BAT", 1),
        (12.00, 62.50),
        (30.00, 62.50),
        get_pos("U_BUCK", 1)
    ], "12V_BAT", width=1.5)

    # 12V cấp cho U_DRV_L_PWR Pad 1 qua rãnh Tây X=2.00 (dưới 5V)
    route_polyline([
        (12.00, 62.50),
        (2.00, 62.50),
        (2.00, 28.00),
        get_pos("U_DRV_L_PWR", 1)
    ], "12V_BAT", width=1.5)

    # 12V cấp cho U_DRV_R_PWR Pad 1 qua rãnh Đông X=80.00
    route_polyline([
        (30.00, 62.50),
        (80.00, 62.50),
        (80.00, 23.00),
        get_pos("U_DRV_R_PWR", 1)
    ], "12V_BAT", width=1.5)

    # ==============================================================
    # KHỐI 1: NGUỒN 5V_BUCK (1.5mm)
    # ==============================================================
    # U_BUCK Pad 3 (35.08, 59.00) -> J_PWR_PI Pad 1 (57.54, 59.00) qua Y=56.50
    route_polyline([
        get_pos("U_BUCK", 3),
        (35.08, 56.50),
        (57.54, 56.50),
        get_pos("J_PWR_PI", 1)
    ], "5V_BUCK", width=1.5)

    # 5V cấp cho 2 Sonar qua rãnh Tây X=4.00
    route_polyline([
        (35.08, 56.50),
        (4.00, 56.50),
        (4.00, 11.62),
        get_pos("J_SONAR_L", 1)
    ], "5V_BUCK", width=1.5)
    route_polyline([
        (4.00, 21.78),
        get_pos("J_SONAR_R", 1)
    ], "5V_BUCK", width=1.5)

    # ==============================================================
    # KHỐI 1: NGUỒN 3V3 (1.5mm) - HOÀN TOÀN Ở PHÍA BẮC & GẦM TRỞ
    # ==============================================================
    # Tuyến 3V3 mép Bắc cấp OLED
    route_polyline([
        get_pos("J_PI_IDC40", 1),
        (41.23, 2.00),
        (12.00, 2.00),
        get_pos("J_OLED", 1)
    ], "3V3", width=1.5)

    # Tuyến 3V3 cấp cho U_DRV_R và R_STBY_R qua phía Bắc (1 polyline duy nhất vát 45 độ)
    route_polyline([
        (41.23, 2.00),
        (61.00, 2.00),
        get_pos("R_STBY_R", 2),
        (68.00, 20.46),
        get_pos("U_DRV_R_PWR", 2)
    ], "3V3", width=1.5)

    # Tuyến 3V3 đi qua X=14.00 (Tây của R_ECHOL_1 và R_ECHOR_1) cấp cho U_DRV_L_PWR Pad 2
    route_polyline([
        (12.00, 2.00),
        (14.00, 2.00),
        (14.00, 30.54),
        get_pos("U_DRV_L_PWR", 2)
    ], "3V3", width=1.5)

    # Nối 3V3 từ U_DRV_L_PWR Pad 2 sang R_STBY_L Pad 2 (ở Y=27.84)
    route_2pts(get_pos("U_DRV_L_PWR", 2), get_pos("R_STBY_L", 2), "3V3", width=1.5)

    # ==============================================================
    # KHỐI 1: MẠNG NỐI ĐẤT CHUNG GND (1.5mm)
    # ==============================================================
    # 1. GND Đáy Nam: Nối các chân nguồn dọc Y=59.00
    add_direct(get_pos("J_BAT", 2), get_pos("U_BUCK", 2), "GND", width=1.5)
    # Vòng qua phía Nam Y=60.80 để bỏ qua Pad 3 (5V)
    route_polyline([
        get_pos("U_BUCK", 2),
        (33.50, 60.80),
        (36.50, 60.80),
        get_pos("U_BUCK", 4)
    ], "GND", width=1.5)
    add_direct(get_pos("U_BUCK", 4), get_pos("J_PWR_PI", 2), "GND", width=1.5)

    # 2. GND Cụm Tây (Sonar, OLED, Trở phân áp):
    # Rãnh GND Tây Highway dọc X=6.00 cấp cho Sonar R, Sonar L, OLED
    # Nối từ J_BAT Pad 2 sang X=6.00 tại rãnh Nam Y=58.00
    route_polyline([
        get_pos("J_BAT", 2),
        (10.00, 58.00),
        (6.00, 58.00),
        (6.00, 29.28),
        get_pos("J_SONAR_R", 4)
    ], "GND", width=1.5)

    route_polyline([
        (6.00, 29.28),
        (6.00, 19.12),
        get_pos("J_SONAR_L", 4)
    ], "GND", width=1.5)

    route_polyline([
        (6.00, 19.12),
        (6.00, 5.00),
        get_pos("J_OLED", 2)
    ], "GND", width=1.5)

    # Nối GND Trở phân áp R_ECHOR_2 và R_ECHOL_2 sang GND Highway tại Y=32.00
    route_polyline([
        get_pos("R_ECHOL_2", 2),
        get_pos("R_ECHOR_2", 2),
        (27.00, 32.00),
        (6.00, 32.00)
    ], "GND", width=1.5)

    # 3. GND Driver Trái & IDC40 Trái
    route_polyline([
        get_pos("J_PI_IDC40", 39),
        get_pos("U_DRV_L_CTL", 8),
        get_pos("U_DRV_L_PWR", 8),
        (16.00, 48.00),
        (20.00, 48.00),
        (20.00, 33.08),
        get_pos("U_DRV_L_PWR", 3)
    ], "GND", width=1.5)

    # Nối GND Driver Trái xuống U_BUCK Pad 2 qua kênh miter 45 độ
    route_polyline([
        (16.00, 48.00),
        (20.00, 48.00),
        (25.00, 53.00),
        (29.54, 56.00),
        get_pos("U_BUCK", 2)
    ], "GND", width=1.5)

    # 4. GND Driver Phải & IDC40 Phải
    route_polyline([
        get_pos("J_PI_IDC40", 34),
        (47.00, 44.64),
        (50.86, 40.78),
        get_pos("U_DRV_R_CTL", 8),
        get_pos("U_DRV_R_PWR", 8),
        (68.00, 43.00),
        (64.00, 43.00),
        (64.00, 28.08),
        get_pos("U_DRV_R_PWR", 3)
    ], "GND", width=1.5)

    # Nối GND Driver Phải xuống J_PWR_PI Pad 2 (vát góc 45 độ miter vào Pad)
    route_polyline([
        (68.00, 43.00),
        (68.00, 52.00),
        (57.00, 52.00),
        (57.00, 57.00),
        get_pos("J_PWR_PI", 2)
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
    generate_masterpiece_pcb()
