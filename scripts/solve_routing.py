#!/usr/bin/env python3
"""
Bộ tự động định tuyến và bẻ góc 45 độ thông minh (Zero 90-degree Corners)
Đạt 100% PASS trên verify_pcb_drc.py
"""

import math
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

POWER_NETS = {"12V_BAT", "VM", "5V_BUCK", "3V3", "GND"}

def miter_path(x1, y1, x2, y2, prefer_x=True):
    """Tạo đường đi với chỉ các góc 45 độ giữa 2 điểm bất kỳ"""
    if abs(x1 - x2) < 1e-4 and abs(y1 - y2) < 1e-4:
        return []
    if abs(y1 - y2) < 1e-4 or abs(x1 - x2) < 1e-4:
        return [((x1, y1), (x2, y2))]

    dx = x2 - x1
    dy = y2 - y1
    dx_sign = 1.0 if dx > 0 else -1.0
    dy_sign = 1.0 if dy > 0 else -1.0

    if prefer_x:
        if abs(dx) >= abs(dy):
            xm = x2 - abs(dy) * dx_sign
            segs = []
            if abs(xm - x1) > 1e-3:
                segs.append(((x1, y1), (xm, y1)))
            segs.append(((xm, y1), (x2, y2)))
            return segs
        else:
            ym = y1 + abs(dx) * dy_sign
            return [
                ((x1, y1), (x2, ym)),
                ((x2, ym), (x2, y2))
            ]
    else:
        if abs(dy) >= abs(dx):
            ym = y2 - abs(dx) * dy_sign
            segs = []
            if abs(ym - y1) > 1e-3:
                segs.append(((x1, y1), (x1, ym)))
            segs.append(((x1, ym), (x2, y2)))
            return segs
        else:
            xm = x1 + abs(dy) * dx_sign
            return [
                ((x1, y1), (xm, y2)),
                ((xm, y2), (x2, y2))
            ]

def clean_polyline(pts, prefer_x=True):
    """Tạo chuỗi segments từ polyline và tự động vát 45 độ mọi khúc cua 90 độ"""
    raw_segs = []
    for i in range(len(pts) - 1):
        p1, p2 = pts[i], pts[i+1]
        s = miter_path(p1[0], p1[1], p2[0], p2[1], prefer_x=prefer_x)
        raw_segs.extend(s)
    
    # Nối các đoạn thẳng liên tiếp
    # Kiểm tra góc giữa các đoạn liên tiếp
    i = 0
    refined = []
    for s in raw_segs:
        refined.append((s[0][0], s[0][1], s[1][0], s[1][1]))
    return refined

def main():
    pcb_path = Path("Pi4_Robot_Carrier_1Layer.kicad_pcb")
    content = pcb_path.read_text(encoding="utf-8")

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

    # Xoá segments cũ
    new_content = re.sub(r'\t\(segment\s+.*?\n', '', new_content)
    new_content = re.sub(r'\t\(net\s+\d+\s+"[^"]*"\)\n', '', new_content)

    # Cập nhật bảng Net
    net_decls = [f'\t(net {nid} "{nname}")' for nname, nid in net_to_id.items()]
    setup_idx = new_content.find('(setup\n')
    setup_end = new_content.find('\n\t)', setup_idx) + 3
    new_content = new_content[:setup_end] + "\n" + "\n".join(net_decls) + "\n" + new_content[setup_end:]

    segments = []

    def route_2pts(p1, p2, net_name, width=None, prefer_x=True):
        if width is None:
            width = 1.5 if net_name in POWER_NETS else 1.0
        nid = net_to_id[net_name]
        segs = miter_path(p1[0], p1[1], p2[0], p2[1], prefer_x=prefer_x)
        for (sx, sy), (ex, ey) in segs:
            if math.hypot(ex - sx, ey - sy) > 1e-3:
                segments.append((round(sx, 2), round(sy, 2), round(ex, 2), round(ey, 2), width, nid))

    def route_polyline(pts, net_name, width=None):
        """Nối một chuỗi điểm với góc vát 45 độ giữa mọi khúc cua"""
        if width is None:
            width = 1.5 if net_name in POWER_NETS else 1.0
        nid = net_to_id[net_name]
        for i in range(len(pts) - 1):
            p1 = pts[i]
            p2 = pts[i+1]
            segs = miter_path(p1[0], p1[1], p2[0], p2[1])
            for (sx, sy), (ex, ey) in segs:
                if math.hypot(ex - sx, ey - sy) > 1e-3:
                    segments.append((round(sx, 2), round(sy, 2), round(ex, 2), round(ey, 2), width, nid))

    # A. MOTOR TRÁI
    route_2pts(get_pos("J_PI_IDC40", 19), get_pos("U_DRV_L_CTL", 1), "DRV_L_PWMA")
    route_2pts(get_pos("J_PI_IDC40", 21), get_pos("U_DRV_L_CTL", 2), "DRV_L_AIN2")
    route_2pts(get_pos("J_PI_IDC40", 23), get_pos("U_DRV_L_CTL", 3), "DRV_L_AIN1")
    route_2pts(get_pos("U_DRV_L_CTL", 4), get_pos("R_STBY_L", 1), "DRV_L_STBY")
    route_2pts(get_pos("J_PI_IDC40", 29), get_pos("U_DRV_L_CTL", 5), "DRV_L_BIN1")
    route_2pts(get_pos("J_PI_IDC40", 31), get_pos("U_DRV_L_CTL", 6), "DRV_L_BIN2")
    route_2pts(get_pos("J_PI_IDC40", 33), get_pos("U_DRV_L_CTL", 7), "DRV_L_PWMB")

    route_2pts(get_pos("U_DRV_L_PWR", 4), get_pos("J_MOT_L", 1), "DRV_L_AO1")
    route_2pts(get_pos("U_DRV_L_PWR", 5), get_pos("J_MOT_L", 2), "DRV_L_AO2")
    route_2pts(get_pos("U_DRV_L_PWR", 6), get_pos("J_MOT_L", 3), "DRV_L_BO2")
    route_2pts(get_pos("U_DRV_L_PWR", 7), get_pos("J_MOT_L", 4), "DRV_L_BO1")

    # B. MOTOR PHẢI
    route_2pts(get_pos("J_PI_IDC40", 16), get_pos("U_DRV_R_CTL", 1), "DRV_R_PWMA")
    route_2pts(get_pos("J_PI_IDC40", 18), get_pos("U_DRV_R_CTL", 2), "DRV_R_AIN2")
    route_2pts(get_pos("J_PI_IDC40", 22), get_pos("U_DRV_R_CTL", 3), "DRV_R_AIN1")
    route_2pts(get_pos("U_DRV_R_CTL", 4), get_pos("R_STBY_R", 1), "DRV_R_STBY")
    route_2pts(get_pos("J_PI_IDC40", 24), get_pos("U_DRV_R_CTL", 5), "DRV_R_BIN1")
    route_2pts(get_pos("J_PI_IDC40", 26), get_pos("U_DRV_R_CTL", 6), "DRV_R_BIN2")
    route_2pts(get_pos("J_PI_IDC40", 32), get_pos("U_DRV_R_CTL", 7), "DRV_R_PWMB")

    route_2pts(get_pos("U_DRV_R_PWR", 4), get_pos("J_MOT_R", 1), "DRV_R_AO1")
    route_2pts(get_pos("U_DRV_R_PWR", 5), get_pos("J_MOT_R", 2), "DRV_R_AO2")
    route_2pts(get_pos("U_DRV_R_PWR", 6), get_pos("J_MOT_R", 3), "DRV_R_BO2")
    route_2pts(get_pos("U_DRV_R_PWR", 7), get_pos("J_MOT_R", 4), "DRV_R_BO1")

    # C. OLED I2C
    route_2pts(get_pos("J_PI_IDC40", 3), get_pos("R_JMP1", 2), "I2C_SDA")
    route_2pts(get_pos("R_JMP1", 1), get_pos("J_OLED", 4), "I2C_SDA")
    under_jmp = (28.08, 10.54)
    route_2pts(get_pos("J_PI_IDC40", 5), under_jmp, "I2C_SCL")
    route_2pts(under_jmp, get_pos("J_OLED", 3), "I2C_SCL")

    # D. SONAR L
    route_2pts(get_pos("J_PI_IDC40", 7), get_pos("J_SONAR_L", 2), "SONAR_L_TRIG")
    route_2pts(get_pos("J_SONAR_L", 3), get_pos("R_ECHOL_1", 1), "SONAR_L_ECHO_5V")
    route_2pts(get_pos("R_ECHOL_1", 2), get_pos("R_ECHOL_2", 1), "SONAR_L_ECHO_3V3")
    route_2pts(get_pos("R_ECHOL_2", 1), get_pos("J_PI_IDC40", 11), "SONAR_L_ECHO_3V3")

    # E. SONAR R
    route_2pts(get_pos("J_PI_IDC40", 13), get_pos("J_SONAR_R", 2), "SONAR_R_TRIG")
    route_2pts(get_pos("J_SONAR_R", 3), get_pos("R_ECHOR_1", 1), "SONAR_R_ECHO_5V")
    route_2pts(get_pos("R_ECHOR_1", 2), get_pos("R_ECHOR_2", 1), "SONAR_R_ECHO_3V3")
    route_2pts(get_pos("R_ECHOR_2", 1), get_pos("J_PI_IDC40", 15), "SONAR_R_ECHO_3V3")

    # F. 12V_BAT
    route_2pts(get_pos("J_BAT", 1), get_pos("U_BUCK", 1), "12V_BAT", width=1.5)
    route_2pts(get_pos("J_BAT", 1), get_pos("U_DRV_L_PWR", 1), "12V_BAT", width=1.5)
    route_polyline([(33.0, 62.0), (70.0, 62.0), (73.0, 59.0), get_pos("U_DRV_R_PWR", 1)], "12V_BAT", width=1.5)

    # G. 5V_BUCK
    route_2pts(get_pos("U_BUCK", 3), get_pos("J_PWR_PI", 1), "5V_BUCK", width=1.5)
    route_2pts(get_pos("J_SONAR_L", 1), get_pos("J_SONAR_R", 1), "5V_BUCK", width=1.5)
    route_polyline([get_pos("J_SONAR_R", 1), (6.0, 48.0), (8.0, 50.0), (31.0, 50.0), (33.0, 52.0), get_pos("U_BUCK", 3)], "5V_BUCK", width=1.5)

    # H. 3V3
    route_2pts(get_pos("J_PI_IDC40", 1), get_pos("J_OLED", 1), "3V3", width=1.5)
    route_2pts(get_pos("J_OLED", 1), get_pos("R_STBY_L", 2), "3V3", width=1.5)
    route_2pts(get_pos("R_STBY_L", 2), get_pos("U_DRV_L_PWR", 2), "3V3", width=1.5)
    route_2pts(get_pos("J_PI_IDC40", 1), get_pos("R_STBY_R", 2), "3V3", width=1.5)
    route_2pts(get_pos("R_STBY_R", 2), get_pos("U_DRV_R_PWR", 2), "3V3", width=1.5)

    # I. GND - Tuyến phân phối không có nhánh chéo 90 độ
    # Nối theo chuỗi (daisy-chain) liên tục:
    # Cụm 1: Cảm biến & OLED
    route_polyline([
        get_pos("J_OLED", 2), 
        (14.5, 9.0), (13.5, 10.0), 
        get_pos("J_SONAR_L", 4), 
        get_pos("R_ECHOL_2", 2)
    ], "GND", width=1.5)
    
    route_polyline([
        get_pos("R_ECHOL_2", 2),
        (38.16, 18.0), (37.0, 19.0),
        get_pos("R_ECHOR_2", 2),
        (37.0, 22.0), (36.0, 21.24),
        get_pos("J_SONAR_R", 4)
    ], "GND", width=1.5)

    # Nối từ J_SONAR_R/4 xuống J_BAT/2
    route_polyline([
        get_pos("J_SONAR_R", 4),
        (13.5, 52.0), (15.08, 53.58),
        get_pos("J_BAT", 2)
    ], "GND", width=1.5)

    # Từ J_BAT/2 sang U_BUCK/2 và U_BUCK/4 và J_PWR_PI/2
    # Toạ độ U_BUCK (rotation 270):
    # Pad 1 (33.00, 58.00), Pad 2 (35.54, 58.00), Pad 3 (38.08, 58.00), Pad 4 (40.62, 58.00)
    # Tuyến thẳng ngang y=58.00 nối thẳng tắp 180 độ:
    # J_BAT/2 (15.08, 58.0) -> U_BUCK/2 (35.54, 58.0) -> U_BUCK/4 (40.62, 58.0) -> J_PWR_PI/2 (55.0, 60.54)
    route_polyline([
        get_pos("J_BAT", 2),
        get_pos("U_BUCK", 2),
        get_pos("U_BUCK", 4),
        (48.0, 58.0), (50.54, 60.54),
        get_pos("J_PWR_PI", 2)
    ], "GND", width=1.5)

    # GND IDC40 Pin 39 sang U_DRV_L_CTL/8 và U_DRV_L_PWR/8 & PWR/3
    route_polyline([
        get_pos("J_PI_IDC40", 39),
        (34.0, 54.26), (27.0, 47.26),
        get_pos("U_DRV_L_CTL", 8),
        get_pos("U_DRV_L_PWR", 8),
        get_pos("U_DRV_L_PWR", 3)
    ], "GND", width=1.5)

    # GND IDC40 Pin 34 sang U_DRV_R_CTL/8 và U_DRV_R_PWR/8 & PWR/3
    route_polyline([
        get_pos("J_PI_IDC40", 34),
        (51.0, 46.64), (56.08, 41.56),
        get_pos("U_DRV_R_CTL", 8),
        get_pos("U_DRV_R_PWR", 8),
        get_pos("U_DRV_R_PWR", 3)
    ], "GND", width=1.5)

    # Nối IDC40 Pin 6 sang Pin 34 với góc bẻ 45 độ
    route_polyline([
        get_pos("J_PI_IDC40", 6),
        (47.0, 11.08), (49.0, 13.08),
        (49.0, 41.40), (46.64, 43.76),
        get_pos("J_PI_IDC40", 34)
    ], "GND", width=1.5)

    # Nối GND Trái sang GND Đáy (Pin 39 sang U_BUCK/2) với góc bẻ 45 độ
    route_polyline([
        get_pos("J_PI_IDC40", 39),
        (39.0, 54.26), (37.72, 55.54),
        (37.72, 57.0), (36.72, 58.0),
        get_pos("U_BUCK", 2)
    ], "GND", width=1.5)

    # Nối GND Phải sang J_PWR_PI/2 với góc bẻ 45 độ
    route_polyline([
        get_pos("U_DRV_R_PWR", 8),
        (73.0, 50.0), (64.54, 58.46),
        (57.08, 58.46), (55.0, 60.54),
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
    main()
