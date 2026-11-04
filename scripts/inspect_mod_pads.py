import glob
import re

mod_files = glob.glob('libraries/robot_electronics.pretty/*.kicad_mod')
print(f"Total .kicad_mod files: {len(mod_files)}")

for fpath in sorted(mod_files):
    name = fpath.split('\\')[-1]
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    pads = re.findall(r'\(pad\s+"?(\w+)"?\s+([^\s]+)\s+([^\s]+)\s+\(at\s+[\d\.-]+\s+[\d\.-]+\)\s+\(size\s+([\d\.-]+)\s+([\d\.-]+)\)\s+\(drill\s+([\d\.-]+)\)', text)
    print(f"  {name:<45} has {len(pads)} pads. Sample pad 1: size=({pads[0][3] if pads else '?'}, {pads[0][4] if pads else '?'}), drill={pads[0][5] if pads else '?'}")

