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
RESOLUTION = 0.5  # 0.5 mm
ORIGIN_X = 48.0
ORIGIN_Y = 36.0
MAX_X = 162.0
MAX_Y = 111.0

WIDTH = int((MAX_X - ORIGIN_X) / RESOLUTION) + 1
HEIGHT = int((MAX_Y - ORIGIN_Y) / RESOLUTION) + 1

# Grid: 0 = free, >0 = occupied by net_id, -1 = obstacle (boundary/pad of other net)
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

# Mark board edges as blocked (X < 49.5, X > 159.5, Y < 37.8, Y > 109.2)
for gx in range(WIDTH):
    for gy in range(HEIGHT):
        wx, wy = to_world(gx, gy)
        if wx < 49.8 or wx > 159.5 or wy < 38.0 or wy > 109.0:
            grid[gx][gy] = -1

# All pads with their target nets
all_pads = []
for ref, pads in wp.items():
    for p_num, p_info in pads.items():
        all_pads.append((ref, p_num, p_info['x'], p_info['y'], p_info['net']))

# Helper for A* routing
def astar(starts, goals, net_id, pad_targets=[]):
    # starts and goals are sets of (gx, gy)
    # returns list of (gx, gy)
    open_set = []
    came_from = {}
    g_score = {}
    
    # Precompute min heuristic for starts
    def h(pos):
        return min(math.hypot(pos[0]-g[0], pos[1]-g[1]) for g in goals)
    
    for s in starts:
        g_score[s] = 0
        heapq.heappush(open_set, (h(s), s))
        
    closed_set = set()
    
    while open_set:
        f, current = heapq.heappop(open_set)
        if current in closed_set:
            continue
        closed_set.add(current)
        
        if current in goals:
            # Reconstruct path
            path = []
            curr = current
            while curr in came_from:
                path.append(curr)
                curr = came_from[curr]
            path.append(curr)
            path.reverse()
            return path
            
        cx, cy = current
        # 8 directions with bend penalty
        neighbors = [
            (cx+1, cy, 1.0), (cx-1, cy, 1.0), (cx, cy+1, 1.0), (cx, cy-1, 1.0),
            (cx+1, cy+1, 1.414), (cx-1, cy+1, 1.414), (cx+1, cy-1, 1.414), (cx-1, cy-1, 1.414)
        ]
        
        for nx, ny, cost in neighbors:
            if not (0 <= nx < WIDTH and 0 <= ny < HEIGHT):
                continue
            val = grid[nx][ny]
            # Free or already part of same net or is one of the goal pad cells
            if val != 0 and val != net_id and (nx, ny) not in goals:
                continue
                
            tentative_g = g_score[current] + cost
            if tentative_g < g_score.get((nx, ny), float('inf')):
                came_from[(nx, ny)] = current
                g_score[(nx, ny)] = tentative_g
                heapq.heappush(open_set, (tentative_g + h((nx, ny)), (nx, ny)))
                
    return None

print("A* engine initialized.")
