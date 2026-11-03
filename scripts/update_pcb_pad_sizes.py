import os, sys, re

sys.stdout.reconfigure(encoding='utf-8')

PCBS = ['Pi4_Robot_Carrier_1Layer.kicad_pcb', 'robot_electronics.kicad_pcb']

def update_pcb(file_path):
    print(f"Updating {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update pad sizes (size 2.2 2.2) -> (size 2.1 2.1)
    pad_count = len(re.findall(r'\(size\s+2\.2\s+2\.2\)', content))
    content = re.sub(r'\(size\s+2\.2\s+2\.2\)', '(size 2.1 2.1)', content)

    # 2. Update via sizes
    def replace_via(m):
        return m.group(0).replace('(size 2.2)', '(size 2.1)')

    via_count = len(re.findall(r'\(via\b.*?\n\t\)', content, re.DOTALL))
    content = re.sub(r'\(via\b.*?\n\t\)', replace_via, content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Updated {pad_count} pads to (size 2.1 2.1)")
    print(f"  Updated {via_count} vias to (size 2.1)")

def main():
    for pcb in PCBS:
        if os.path.exists(pcb):
            update_pcb(pcb)
        else:
            print(f"Warning: {pcb} not found!")

if __name__ == '__main__':
    main()
