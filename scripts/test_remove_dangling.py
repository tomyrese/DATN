import re, sys
sys.path.append('scripts')
import solve_planar_pcb_v16 as v16

# Modify paths in memory
new_paths = []
for p in v16.paths:
    # Remove the dangling OLED stub to dead air (149.58, 101.50)
    if p['net'] == 'GND' and (
        (abs(p['p1'][0] - 149.58) < 0.01 and abs(p['p1'][1] - 96.50) < 0.01 and abs(p['p2'][1] - 101.50) < 0.01) or
        (abs(p['p2'][0] - 149.58) < 0.01 and abs(p['p2'][1] - 96.50) < 0.01 and abs(p['p1'][1] - 101.50) < 0.01)
    ):
        print("Removed dangling OLED stub.")
        continue
    # Remove the duplicate 77.0 -> 79.06 stub on trunk
    if p['net'] == 'GND' and (
        (abs(p['p1'][0] - 77.00) < 0.01 and abs(p['p1'][1] - 101.50) < 0.01 and abs(p['p2'][0] - 79.06) < 0.01) or
        (abs(p['p2'][0] - 77.00) < 0.01 and abs(p['p2'][1] - 101.50) < 0.01 and abs(p['p1'][0] - 79.06) < 0.01)
    ):
        print("Removed duplicate Pin 39 trunk stub.")
        continue
    new_paths.append(p)

print(f"Original paths: {len(v16.paths)}, Cleaned paths: {len(new_paths)}")

