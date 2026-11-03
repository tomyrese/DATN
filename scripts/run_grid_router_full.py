import json, math, heapq, re, uuid

def gen_uuid():
    return str(uuid.uuid4())

# Load world pads
with open('scripts/world_pads.json', 'r', encoding='utf-8') as f:
    wp = json.load(f)

# Footprint swap logic
with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

from test_fp_swap import swap_tb6612_rows, mirror_pi4_header

def update_tb_footprint(fp_text, is_left=True):
    fp_text = swap_tb6612_rows(fp_text)
    prefix = "_L" if is_left else "_R"
    m_pref = "1" if is_left else "3"
    m_pref2 = "2" if is_left else "4"
    nets = {
        "1": f"/PWMA{prefix}",
        "2": f"/AIN2{prefix}",
        "3": f"/AIN1{prefix}",
        "4": f"/STBY{prefix}",
        "5": f"/AIN1{prefix}",
        "6": f"/AIN2{prefix}",
        "7": f"/PWMA{prefix}",
        "8": "GND",
        "9": "/VM_MOTOR",
        "10": "/+5V_PWR",
        "11": "GND",
        "12": f"/M{m_pref}_A",
        "13": f"/M{m_pref}_B",
        "14": f"/M{m_pref2}_B",
        "15": f"/M{m_pref2}_A",
        "16": "GND"
    }
    for pad_num, net_name in nets.items():
        fp_text = re.sub(rf'(\(pad\s+"{pad_num}"[\s\S]*?\(net\s+)"[^"]*"', rf'\1"{net_name}"', fp_text)
    return fp_text

def update_pi_footprint(fp_text):
    fp_text = mirror_pi4_header(fp_text)
    pi_nets = {
        "33": "/PWMA_L",
        "35": "/AIN2_L",
        "37": "/AIN1_L",
        "38": "/STBY_L",
        "31": "/TRIG_L",
        "29": "/ECHO_L",
        "3": "/PWMA_R",
        "5": "/AIN2_R",
        "7": "/AIN1_R",
        "11": "/STBY_R",
        "13": "/TRIG_R",
        "15": "/ECHO_R",
        "19": "/LINE_L",
        "21": "/LINE_C",
        "23": "/LINE_R",
        "27": "/I2C_SDA",
        "28": "/I2C_SCL",
        "2": "/+5V_PWR",
        "4": "/+5V_PWR",
        "6": "GND",
        "14": "GND",
        "20": "GND",
        "25": "GND",
        "30": "GND",
        "34": "GND",
        "39": "GND",
        "17": "/+3V3_LOGIC"
    }
    for pad_num, net_name in pi_nets.items():
        fp_text = re.sub(rf'(\(pad\s+"{pad_num}"[\s\S]*?\(net\s+)"[^"]*"', rf'\1"{net_name}"', fp_text)
    return fp_text

def update_tcrt_footprint(fp_text):
    tcrt_nets = {
        "1": "GND",
        "2": "/+3V3_LOGIC",
        "3": "/LINE_L",
        "4": "/LINE_C",
        "5": "/LINE_R"
    }
    for pad_num, net_name in tcrt_nets.items():
        fp_text = re.sub(rf'(\(pad\s+"{pad_num}"[\s\S]*?\(net\s+)"[^"]*"', rf'\1"{net_name}"', fp_text)
    return fp_text

first_seg = bak.find('(segment')
base_part = bak[:first_seg]

def fp_repl(m):
    fp = m.group(0)
    if 'TB6612_Left' in fp or 'reference "LEFT"' in fp:
        return update_tb_footprint(fp, is_left=True)
    elif 'TB6612_Right' in fp or 'reference "RIGHT"' in fp:
        return update_tb_footprint(fp, is_left=False)
    elif 'Raspberry_Pi_4_40Pin' in fp or 'reference "Rasp_PI4"' in fp:
        return update_pi_footprint(fp)
    elif 'TCRT5000_3CH' in fp or 'reference "TCRT5000"' in fp:
        return update_tcrt_footprint(fp)
    return fp

base_part = re.sub(r'\(footprint\s+"[^"]+"[\s\S]*?\n\t\)', fp_repl, base_part)

# Grid parameters
RESOLUTION = 0.25  # 0.25 mm high resolution grid
ORIGIN_X = 48.0
ORIGIN_Y = 36.0
MAX_X = 162.0
MAX_Y = 111.0

WIDTH = int((MAX_X - ORIGIN_X) / RESOLUTION) + 1
HEIGHT = int((MAX_Y - ORIGIN_Y) / RESOLUTION) + 1

grid = [[0 for _ in range(HEIGHT)] for _ in range(WIDTH)]

def to_grid(x, y):
    gx = int(round((x - ORIGIN_X) / RESOLUTION))
    gy = int(round((y - ORIGIN_Y) / RESOLUTION))
    return max(0, min(WIDTH-1, gx)), max(0, min(HEIGHT-1, gy))

def to_world(gx, gy):
    x = ORIGIN_X + gx * RESOLUTION
    y = ORIGIN_Y + gy * RESOLUTION
    return (round(x, 4), round(y, 4))

def get_pad(ref, pad_num):
    p = wp[ref][str(pad_num)]
    return (round(p['x'], 4), round(p['y'], 4))

# Mark board boundary as blocked
for gx in range(WIDTH):
    for gy in range(HEIGHT):
        wx, wy = to_world(gx, gy)
        if wx < 49.8 or wx > 159.5 or wy < 38.0 or wy > 109.0:
            grid[gx][gy] = -1

# Map each pad to its net
# Mark pad exclusion zones (radius 0.85 mm for pad + 0.3 mm clearance = 1.15 mm)
pad_clearance_cells = int(math.ceil(1.15 / RESOLUTION))

net_name_to_id = {}
current_net_id = 1

def get_net_id(name):
    global current_net_id
    if name not in net_name_to_id:
        net_name_to_id[name] = current_net_id
        current_net_id += 1
    return net_name_to_id[name]

# Collect target nets for all pads
pad_cells_by_net = {} # net_id -> set of (gx, gy)
all_pad_locs = []     # list of (gx, gy, net_id)

for ref, pads in wp.items():
    for p_num, p_info in pads.items():
        net_name = p_info['net']
        if not net_name or 'unconnected' in net_name:
            continue
        nid = get_net_id(net_name)
        gx, gy = to_grid(p_info['x'], p_info['y'])
        all_pad_locs.append((gx, gy, nid))
        if nid not in pad_cells_by_net:
            pad_cells_by_net[nid] = set()
        pad_cells_by_net[nid].add((gx, gy))

# Block all other pads for each search
pad_obstacles = {} # (gx, gy) -> nid
for px, py, nid in all_pad_locs:
    for dx in range(-pad_clearance_cells, pad_clearance_cells + 1):
        for dy in range(-pad_clearance_cells, pad_clearance_cells + 1):
            if dx*dx + dy*dy <= pad_clearance_cells*pad_clearance_cells:
                nx, ny = px + dx, py + dy
                if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                    # If cell is not the pad itself, mark obstacle
                    if (nx, ny) != (px, py):
                        pad_obstacles[(nx, ny)] = nid

def astar(start_set, goal_set, net_id):
    open_set = []
    came_from = {}
    g_score = {}
    
    def h(pos):
        return min(abs(pos[0]-g[0]) + abs(pos[1]-g[1]) for g in goal_set) * 1.001
    
    for s in start_set:
        g_score[s] = 0
        heapq.heappush(open_set, (h(s), s))
        
    closed_set = set()
    
    while open_set:
        f, current = heapq.heappop(open_set)
        if current in closed_set:
            continue
        closed_set.add(current)
        
        if current in goal_set:
            path = []
            curr = current
            while curr in came_from:
                path.append(curr)
                curr = came_from[curr]
            path.append(curr)
            path.reverse()
            return path
            
        cx, cy = current
        # 4-connected (ortho) first for clean PCB tracks, with 45-degree diagonals
        neighbors = [
            (cx+1, cy, 1.0), (cx-1, cy, 1.0), (cx, cy+1, 1.0), (cx, cy-1, 1.0),
            (cx+1, cy+1, 1.414), (cx-1, cy+1, 1.414), (cx+1, cy-1, 1.414), (cx-1, cy-1, 1.414)
        ]
        
        for nx, ny, cost in neighbors:
            if not (0 <= nx < WIDTH and 0 <= ny < HEIGHT):
                continue
            val = grid[nx][ny]
            if val == -1: # boundary
                continue
            if val != 0 and val != net_id and (nx, ny) not in goal_set:
                continue
            # Check pad obstacle
            p_nid = pad_obstacles.get((nx, ny))
            if p_nid is not None and p_nid != net_id and (nx, ny) not in goal_set:
                continue
                
            tentative_g = g_score[current] + cost
            if tentative_g < g_score.get((nx, ny), float('inf')):
                came_from[(nx, ny)] = current
                g_score[(nx, ny)] = tentative_g
                heapq.heappush(open_set, (tentative_g + h((nx, ny)), (nx, ny)))
                
    return None

def mark_path(path, net_id, width_mm=0.6):
    track_radius_cells = int(math.ceil((width_mm/2.0 + 0.25) / RESOLUTION))
    for gx, gy in path:
        for dx in range(-track_radius_cells, track_radius_cells + 1):
            for dy in range(-track_radius_cells, track_radius_cells + 1):
                if dx*dx + dy*dy <= track_radius_cells*track_radius_cells:
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                        if grid[nx][ny] == 0:
                            grid[nx][ny] = net_id

def simplify_path(path):
    if len(path) <= 2:
        return path
    simplified = [path[0]]
    for i in range(1, len(path)-1):
        prev = simplified[-1]
        curr = path[i]
        next_p = path[i+1]
        # Direction vectors
        dx1, dy1 = curr[0] - prev[0], curr[1] - prev[1]
        dx2, dy2 = next_p[0] - curr[0], next_p[1] - curr[1]
        if (dx1 * dy2 - dy1 * dx2) != 0:
            simplified.append(curr)
    simplified.append(path[-1])
    return simplified

routed_paths = [] # list of (net_name, world_points, width)

print("A* router ready to route.")

# Define nets in routing order:
# 1. Local sensor nets: Net-(U_US1-ECHO), Net-(U_US2-ECHO)
# 2. Motor outputs: M1_A, M1_B, M2_A, M2_B, M3_A, M3_B, M4_A, M4_B
# 3. Control nets: STBY_L, AIN1_L, AIN2_L, PWMA_L, STBY_R, AIN1_R, AIN2_R, PWMA_R
# 4. TCRT & US signals: LINE_R, LINE_C, LINE_L, TRIG_L, ECHO_L, TRIG_R, ECHO_R
# 5. OLED I2C_SCL
# 6. Power: +3V3_LOGIC, VM_MOTOR, +5V_PWR, GND

route_sequence = [
    # US local dividers
    ("Net-(U_US1-ECHO)", [("HC_SR04_1", 3), ("R1", 1)], 0.6),
    ("Net-(U_US2-ECHO)", [("HC_SR04_2", 3), ("R3", 1)], 0.6),
    
    # Motor outputs (0.8mm)
    ("/M1_A", [("LEFT", 12), ("MOTOR1", 1)], 0.8),
    ("/M1_B", [("LEFT", 13), ("MOTOR1", 2)], 0.8),
    ("/M2_B", [("LEFT", 14), ("MOTOR2", 1)], 0.8),
    ("/M2_A", [("LEFT", 15), ("MOTOR2", 2)], 0.8),
    ("/M3_A", [("RIGHT", 12), ("MOTOR3", 1)], 0.8),
    ("/M3_B", [("RIGHT", 13), ("MOTOR3", 2)], 0.8),
    ("/M4_B", [("RIGHT", 14), ("MOTOR4", 1)], 0.8),
    ("/M4_A", [("RIGHT", 15), ("MOTOR4", 2)], 0.8),
    
    # Left controls: tied pads first, then to Pi
    ("/AIN1_L", [("LEFT", 3), ("LEFT", 5), ("Rasp_PI4", 37)], 0.6),
    ("/AIN2_L", [("LEFT", 2), ("LEFT", 6), ("Rasp_PI4", 35)], 0.6),
    ("/PWMA_L", [("LEFT", 1), ("LEFT", 7), ("Rasp_PI4", 33)], 0.6),
    ("/STBY_L", [("LEFT", 4), ("Rasp_PI4", 38)], 0.6),
    
    # Right controls: tied pads first, then to Pi
    ("/AIN1_R", [("RIGHT", 3), ("RIGHT", 5), ("Rasp_PI4", 7)], 0.6),
    ("/AIN2_R", [("RIGHT", 2), ("RIGHT", 6), ("Rasp_PI4", 5)], 0.6),
    ("/PWMA_R", [("RIGHT", 1), ("RIGHT", 7), ("Rasp_PI4", 3)], 0.6),
    ("/STBY_R", [("RIGHT", 4), ("Rasp_PI4", 11)], 0.6),
    
    # TCRT5000 lines
    ("/LINE_R", [("TCRT5000", 5), ("Rasp_PI4", 23)], 0.6),
    ("/LINE_C", [("TCRT5000", 4), ("Rasp_PI4", 21)], 0.6),
    ("/LINE_L", [("TCRT5000", 3), ("Rasp_PI4", 19)], 0.6),
    
    # Ultrasonic lines
    ("/TRIG_L", [("HC_SR04_1", 2), ("Rasp_PI4", 31)], 0.6),
    ("/ECHO_L", [("R1", 2), ("R2", 1), ("Rasp_PI4", 29)], 0.6),
    ("/TRIG_R", [("HC_SR04_2", 2), ("Rasp_PI4", 13)], 0.6),
    ("/ECHO_R", [("R3", 2), ("R4", 1), ("Rasp_PI4", 15)], 0.6),
    
    # OLED
    ("/I2C_SCL", [("Rasp_PI4", 28), ("OLED", 3)], 0.6),
    
    # Logic 3V3
    ("/+3V3_LOGIC", [("TCRT5000", 2), ("Rasp_PI4", 17)], 0.8),
    
    # VM_MOTOR
    ("/VM_MOTOR", [("LEFT", 9), ("RIGHT", 9)], 1.0),
    
    # +5V_PWR
    ("/+5V_PWR", [("Rasp_PI4", 4), ("Rasp_PI4", 2), ("LEFT", 10), ("RIGHT", 10), ("HC_SR04_1", 1), ("HC_SR04_2", 1)], 1.0),
    
    # GND
    ("GND", [
        ("Rasp_PI4", 6), ("Rasp_PI4", 14), ("Rasp_PI4", 20), ("Rasp_PI4", 25), ("Rasp_PI4", 30), ("Rasp_PI4", 34), ("Rasp_PI4", 39),
        ("LEFT", 8), ("LEFT", 11), ("LEFT", 16),
        ("RIGHT", 8), ("RIGHT", 11), ("RIGHT", 16),
        ("OLED", 2), ("R2", 2), ("R4", 2), ("HC_SR04_1", 4), ("HC_SR04_2", 4), ("TCRT5000", 1)
    ], 1.0)
]

print(f"Beginning routing of {len(route_sequence)} nets...")

success_count = 0
fail_count = 0

for net_name, pin_list, width in route_sequence:
    nid = get_net_id(net_name)
    # Convert pins to grid coords
    pts = [to_grid(*get_pad(ref, p)) for ref, p in pin_list]
    
    # Connect in tree form: start with pts[0]
    routed_set = {pts[0]}
    
    net_failed = False
    for target in pts[1:]:
        if target in routed_set:
            continue
        path = astar(routed_set, {target}, nid)
        if path:
            mark_path(path, nid, width)
            # Add path to routed_set
            for cell in path:
                routed_set.add(cell)
            # Convert to world coords and simplify
            w_path = [to_world(gx, gy) for gx in [p[0] for p in path] for gy in [p[1] for p in path]]
            # simplify
            simp = simplify_path(path)
            w_simp = [to_world(gx, gy) for gx, gy in simp]
            # Snap endpoints to exact pad coords
            routed_paths.append((net_name, w_simp, width))
        else:
            print(f"FAILED to route net {net_name} to target {target}!")
            net_failed = True
            fail_count += 1
            break
    if not net_failed:
        success_count += 1
        print(f"Routed {net_name} successfully ({len(pin_list)} pins).")

print(f"\nRouting finished: {success_count} succeeded, {fail_count} failed.")

# Generate kicad segments
segments = []
vias = []
silk_items = []

def make_segment(x1, y1, x2, y2, width, net, layer="B.Cu"):
    return f"""\t(segment
\t\t(start {x1:.4f} {y1:.4f})
\t\t(end {x2:.4f} {y2:.4f})
\t\t(width {width})
\t\t(layer "{layer}")
\t\t(net "{net}")
\t\t(uuid "{gen_uuid()}")
\t)\n"""

def make_via(x, y, net, size=1.6, drill=0.8):
    return f"""\t(via
\t\t(at {x:.4f} {y:.4f})
\t\t(size {size})
\t\t(drill {drill})
\t\t(layers "F.Cu" "B.Cu")
\t\t(net "{net}")
\t\t(uuid "{gen_uuid()}")
\t)\n"""

def make_silk_jumper(x1, y1, x2, y2, label):
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2 - 1.2
    return f"""\t(gr_line
\t\t(start {x1:.4f} {y1:.4f})
\t\t(end {x2:.4f} {y2:.4f})
\t\t(stroke
\t\t\t(width 0.25)
\t\t\t(type dash)
\t\t)
\t\t(layer "F.SilkS")
\t\t(uuid "{gen_uuid()}")
\t)
\t(gr_circle
\t\t(center {x1:.4f} {y1:.4f})
\t\t(end {x1+0.9:.4f} {y1:.4f})
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "{gen_uuid()}")
\t)
\t(gr_circle
\t\t(center {x2:.4f} {y2:.4f})
\t\t(end {x2+0.9:.4f} {y2:.4f})
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "{gen_uuid()}")
\t)
\t(gr_text "{label}"
\t\t(at {mid_x:.4f} {mid_y:.4f})
\t\t(layer "F.SilkS")
\t\t(uuid "{gen_uuid()}")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)\n"""

# Add segments from routed_paths
for net_name, w_simp, width in routed_paths:
    for i in range(len(w_simp)-1):
        p1, p2 = w_simp[i], w_simp[i+1]
        segments.append(make_segment(p1[0], p1[1], p2[0], p2[1], width, net_name))

# Add OLED JMP1 and JMP2
p_pi27 = get_pad("Rasp_PI4", 27)
p_oled_4 = get_pad("OLED", 4)
vias.append(make_via(p_pi27[0], 89.00, "/I2C_SDA"))
vias.append(make_via(p_oled_4[0], 89.00, "/I2C_SDA"))
segments.append(make_segment(p_pi27[0], p_pi27[1], p_pi27[0], 89.00, 0.6, "/I2C_SDA"))
segments.append(make_segment(p_oled_4[0], 89.00, p_oled_4[0], p_oled_4[1], 0.6, "/I2C_SDA"))
silk_items.append(make_silk_jumper(p_pi27[0], 89.00, p_oled_4[0], 89.00, "JMP1: SDA (Wire 50mm)"))

p_pi17 = get_pad("Rasp_PI4", 17)
p_oled_1 = get_pad("OLED", 1)
vias.append(make_via(p_pi17[0], 86.50, "/+3V3_LOGIC"))
vias.append(make_via(p_oled_1[0], 86.50, "/+3V3_LOGIC"))
segments.append(make_segment(p_pi17[0], p_pi17[1], p_pi17[0], 86.50, 0.6, "/+3V3_LOGIC"))
segments.append(make_segment(p_oled_1[0], 86.50, p_oled_1[0], p_oled_1[1], 0.6, "/+3V3_LOGIC"))
silk_items.append(make_silk_jumper(p_pi17[0], 86.50, p_oled_1[0], 86.50, "JMP2: 3V3 (Wire 45mm)"))

final_pcb = base_part + "".join(vias) + "".join(segments) + "".join(silk_items) + "\t(embedded_fonts no)\n)\n"

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(final_pcb)

with open('robot_electronics.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(final_pcb)

print(f"Generated PCB: {len(segments)} segments, {len(vias)} vias.")
