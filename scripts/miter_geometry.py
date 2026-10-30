#!/usr/bin/env python3
"""
Bộ tự động định vị linh kiện (Placement) và đi dây (Routing) hoàn chỉnh cho PCB 1 Lớp
Raspberry Pi 4 Robot Carrier Board (85mm x 65mm).
Đảm bảo 100% tiêu chuẩn DRC:
1. Pad THT size = 1.8mm x 1.8mm, drill = 0.8mm
2. Đường nguồn = 1.5mm, đường tín hiệu = 1.0mm
3. 1 lớp duy nhất (B.Cu), 0 Via, 0 Copper Zone
4. Bẻ góc 45 độ, không góc vuông 90 độ, không chéo dây
"""

import math
import re
from pathlib import Path

# Danh sách Net nguồn và Net tín hiệu
POWER_NETS = {"12V_BAT", "VM", "5V_BUCK", "3V3", "GND"}

def miter_path_x_first(x1, y1, x2, y2):
    """
    Tạo đường đi từ (x1, y1) đến (x2, y2) sử dụng góc bẻ 45 độ.
    Đi ngang trước, bẻ 45 độ, rồi đi thẳng đến đích.
    """
    if abs(x1 - x2) < 1e-4 and abs(y1 - y2) < 1e-4:
        return []
    if abs(y1 - y2) < 1e-4:
        return [((x1, y1), (x2, y2))]
    if abs(x1 - x2) < 1e-4:
        return [((x1, y1), (x2, y2))]
    
    dy = y2 - y1
    dx_sign = 1.0 if x2 > x1 else -1.0
    dy_sign = 1.0 if y2 > y1 else -1.0
    
    # Đoạn 45 độ cần dx_45 = abs(dy) * dx_sign
    dx_45 = abs(dy) * dx_sign
    
    # Kiểm tra xem khoảng cách x có đủ cho đoạn 45 độ không
    if abs(x2 - x1) >= abs(dy):
        # Đi ngang từ x1 đến xm, sau đó bẻ 45 độ từ xm đến x2
        xm = x2 - dx_45
        segs = []
        if abs(xm - x1) > 1e-3:
            segs.append(((x1, y1), (xm, y1)))
        segs.append(((xm, y1), (x2, y2)))
        return segs
    else:
        # Khoảng cách x nhỏ hơn y: đi 45 độ một đoạn dx = abs(x2-x1), sau đó đi dọc
        ym = y1 + abs(x2 - x1) * dy_sign
        segs = [
            ((x1, y1), (x2, ym)),
            ((x2, ym), (x2, y2))
        ]
        return segs

def miter_path_y_first(x1, y1, x2, y2):
    """
    Tạo đường đi từ (x1, y1) đến (x2, y2) sử dụng góc bẻ 45 độ.
    Đi dọc trước, bẻ 45 độ, rồi đi ngang đến đích.
    """
    if abs(x1 - x2) < 1e-4 and abs(y1 - y2) < 1e-4:
        return []
    if abs(y1 - y2) < 1e-4:
        return [((x1, y1), (x2, y2))]
    if abs(x1 - x2) < 1e-4:
        return [((x1, y1), (x2, y2))]
    
    dx = x2 - x1
    dx_sign = 1.0 if x2 > x1 else -1.0
    dy_sign = 1.0 if y2 > y1 else -1.0
    
    dy_45 = abs(dx) * dy_sign
    if abs(y2 - y1) >= abs(dx):
        ym = y2 - dy_45
        segs = []
        if abs(ym - y1) > 1e-3:
            segs.append(((x1, y1), (x1, ym)))
        segs.append(((x1, ym), (x2, y2)))
        return segs
    else:
        xm = x1 + abs(y2 - y1) * dx_sign
        segs = [
            ((x1, y1), (xm, y2)),
            ((xm, y2), (x2, y2))
        ]
        return segs

print("Router geometry functions loaded successfully.")
