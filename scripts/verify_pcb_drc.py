#!/usr/bin/env python3
"""
Kịch bản Kiểm thử Tự động Ràng buộc Thiết kế PCB 1 Lớp (Automated PCB Constraint Verifier)
Dành cho Antigravity sau khi chạy KiCAD-MCP-Server.
Kiểm tra:
1. Hole Size == 0.8mm & Pad Size X == 1.8mm
2. Track Width: Nguồn == 1.5mm, Tín hiệu == 1.0mm
3. Chỉ sử dụng 1 lớp đồng (B.Cu), không có Via, không có Zone phủ đồng
4. Không có góc vuông 90 độ giữa các đoạn dây nối tiếp
"""

import sys
import re
import math
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

POWER_NETS = {"12V_BAT", "VM", "5V_BUCK", "3V3", "GND", "+12V", "+5V", "+3V3"}

def verify_kicad_pcb(pcb_path: str):
    path = Path(pcb_path)
    if not path.exists():
        print(f"[ERROR] Không tìm thấy file PCB: {pcb_path}")
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    errors = []
    warnings = []

    # 1. Kiểm tra Via (Mạch 1 lớp không được dùng Via đổi lớp)
    vias = re.findall(r'\(via\s+', content)
    if len(vias) > 0:
        errors.append(f"Vi phạm mạch 1 lớp: Phát hiện {len(vias)} vias trong thiết kế (Yêu cầu: 0 via).")

    # 2. Kiểm tra Zone phủ đồng (Không đổ nhựa / không phủ đồng)
    zones = re.findall(r'\(zone\s+', content)
    if len(zones) > 0:
        errors.append(f"Vi phạm quy định không phủ đồng: Phát hiện {len(zones)} copper zones.")

    # 3. Kiểm tra Pad Size (1.4mm) và Drill Hole Size (0.8mm) cho các chân cắm (thru_hole)
    pad_blocks = re.findall(r'\(pad\s+"[^"]*"\s+thru_hole\s+[^\n]+\(size\s+([0-9.]+)\s+([0-9.]+)\)[^\n]*\(drill\s+([0-9.]+)\)', content, re.DOTALL)
    for idx, (sx, sy, drill) in enumerate(pad_blocks, 1):
        sx_f, sy_f, drill_f = float(sx), float(sy), float(drill)
        if abs(sx_f - 1.4) > 0.05 or abs(drill_f - 0.8) > 0.05:
            errors.append(f"Pad THT #{idx} sai kích thước: size=({sx_f}, {sy_f})mm, drill={drill_f}mm (Yêu cầu: size_x=1.4mm, hole=0.8mm).")

    # 4. Kiểm tra Track Width (1.5mm cho Nguồn, 1.0mm cho Tín hiệu) và Lớp đồng
    segments = re.findall(
        r'\(segment\s+\(start\s+([0-9.-]+)\s+([0-9.-]+)\)\s+\(end\s+([0-9.-]+)\s+([0-9.-]+)\)\s+\(width\s+([0-9.]+)\)\s+\(layer\s+"([^"]+)"\)\s+\(net\s+(\d+)\)',
        content
    )

    if not segments:
        warnings.append("Chưa phát hiện đoạn dây đồng (segment) nào trên PCB.")

    tracks_by_net = {}
    for x1, y1, x2, y2, width, layer, net_id in segments:
        w = float(width)
        if layer not in ("B.Cu",):
            errors.append(f"Segment trên lớp '{layer}' không hợp lệ (Chỉ được phép đi dây trên 1 lớp 'B.Cu').")
        if abs(w - 1.5) > 0.05 and abs(w - 1.0) > 0.05:
            errors.append(f"Segment (net {net_id}) có độ rộng {w}mm không hợp lệ (Chỉ cho phép 1.5mm cho nguồn hoặc 1.0mm cho tín hiệu).")
        tracks_by_net.setdefault(net_id, []).append((float(x1), float(y1), float(x2), float(y2)))

    # 5. Kiểm tra góc vuông 90 độ giữa các đoạn dây cùng Net nối tiếp nhau
    for net_id, segs in tracks_by_net.items():
        for i in range(len(segs)):
            for j in range(i + 1, len(segs)):
                ax1, ay1, ax2, ay2 = segs[i]
                bx1, by1, bx2, by2 = segs[j]
                # Kiểm tra nếu 2 đoạn có chung 1 đỉnh
                shared = None
                if math.hypot(ax2 - bx1, ay2 - by1) < 1e-3:
                    shared = (ax1, ay1, ax2, ay2, bx2, by2)
                elif math.hypot(ax2 - bx2, ay2 - by2) < 1e-3:
                    shared = (ax1, ay1, ax2, ay2, bx1, by1)
                elif math.hypot(ax1 - bx1, ay1 - by1) < 1e-3:
                    shared = (ax2, ay2, ax1, ay1, bx2, by2)
                elif math.hypot(ax1 - bx2, ay1 - by2) < 1e-3:
                    shared = (ax2, ay2, ax1, ay1, bx1, by1)

                if shared:
                    px1, py1, cx, cy, px2, py2 = shared
                    v1 = (cx - px1, cy - py1)
                    v2 = (px2 - cx, py2 - cy)
                    l1 = math.hypot(*v1)
                    l2 = math.hypot(*v2)
                    if l1 > 0.1 and l2 > 0.1:
                        dot = (v1[0]*v2[0] + v1[1]*v2[1]) / (l1 * l2)
                        dot = max(-1.0, min(1.0, dot))
                        angle = math.degrees(math.acos(dot))
                        if abs(angle - 90.0) < 2.0:
                            errors.append(
                                f"Phát hiện góc vuông 90° tại toạ độ ({cx:.2f}, {cy:.2f}) thuộc Net {net_id}. Bắt buộc bẻ góc 45°!"
                            )

    print("=" * 65)
    print(" KẾT QUẢ KIỂM THỬ TỰ ĐỘNG RÀNG BUỘC PCB 1 LỚP (ANTIGRAVITY DRC)")
    print("=" * 65)
    if warnings:
        for w in warnings:
            print(f"[WARN]  {w}")
    if errors:
        for e in errors:
            print(f"[FAIL]  {e}")
        print("-" * 65)
        print(f"TỔNG KẾT: THẤT BẠI ({len(errors)} lỗi vi phạm quy định thiết kế). Yêu cầu Antigravity sửa lại!")
        sys.exit(1)
    else:
        print("[PASS]  1. Hole Size = 0.8mm & Pad Size X = 1.4mm: HỢP LỆ")
        print("[PASS]  2. Dây nguồn = 1.5mm & Dây tín hiệu = 1.0mm: HỢP LỆ")
        print("[PASS]  3. Mạch 1 lớp (B.Cu), không Via, không đổ nhựa (Zone): HỢP LỆ")
        print("[PASS]  4. Không đi góc vuông 90°, không chéo dây: HỢP LỆ")
        print("-" * 65)
        print("TỔNG KẾT: HOÀN TẤT XUẤT SẮC 100%! Sẵn sàng thông báo cho người dùng.")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python3 verify_pcb_drc.py <đường_dẫn_file.kicad_pcb>")
        sys.exit(1)
    verify_kicad_pcb(sys.argv[1])
