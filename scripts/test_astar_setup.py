import json, math, heapq, re, uuid

def gen_uuid():
    return str(uuid.uuid4())

# Grid parameters
# Board bounds: X in [49.0, 160.5], Y in [37.2, 110.0]
# Cell size: 0.5 mm
RESOLUTION = 0.5
ORIGIN_X = 48.0
ORIGIN_Y = 36.0
MAX_X = 162.0
MAX_Y = 111.0

WIDTH_CELLS = int((MAX_X - ORIGIN_X) / RESOLUTION) + 1
HEIGHT_CELLS = int((MAX_Y - ORIGIN_Y) / RESOLUTION) + 1

def to_grid(x, y):
    gx = int(round((x - ORIGIN_X) / RESOLUTION))
    gy = int(round((y - ORIGIN_Y) / RESOLUTION))
    return (gx, gy)

def to_world(gx, gy):
    x = ORIGIN_X + gx * RESOLUTION
    y = ORIGIN_Y + gy * RESOLUTION
    return (round(x, 4), round(y, 4))

print(f"Grid dimensions: {WIDTH_CELLS} x {HEIGHT_CELLS} ({WIDTH_CELLS * HEIGHT_CELLS} cells)")
