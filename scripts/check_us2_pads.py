import sys
sys.path.append('scripts')
from solve_planar_pcb_v3 import us2

for i, p in enumerate(us2):
    print(f"US2[{i}] = {p}")
