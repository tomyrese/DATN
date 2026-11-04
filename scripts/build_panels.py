import os, re, uuid

def offset_footprint(fp_text, dx, dy):
    fp_text = re.sub(r'\(uuid\s+"[^"]+"\)', lambda m: f'(uuid "{uuid.uuid4()}")', fp_text)
    if dx == 0 and dy == 0:
        return fp_text

    def replace_fp_at(match):
        prefix = match.group(1)
        x = float(match.group(2)) + dx
        y = float(match.group(3)) + dy
        rot = match.group(4) if match.group(4) else ""
        return f"{prefix}{x:.6f} {y:.6f}{rot})"

    fp_text = re.sub(
        r'(\t\t\(at\s+)([0-9\.\-]+)\s+([0-9\.\-]+)(\s+[0-9\.\-]+|\s+\([^)]+\))?\)',
        replace_fp_at,
        fp_text,
        count=1
    )
    return fp_text

def offset_other_element(el_text, dx, dy):
    el_text = re.sub(r'\(uuid\s+"[^"]+"\)', lambda m: f'(uuid "{uuid.uuid4()}")', el_text)
    if dx == 0 and dy == 0:
        return el_text

    el_text = re.sub(
        r'\(start\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)',
        lambda m: f"(start {float(m.group(1))+dx:.6f} {float(m.group(2))+dy:.6f})",
        el_text
    )
    el_text = re.sub(
        r'\(end\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)',
        lambda m: f"(end {float(m.group(1))+dx:.6f} {float(m.group(2))+dy:.6f})",
        el_text
    )
    el_text = re.sub(
        r'\(mid\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)',
        lambda m: f"(mid {float(m.group(1))+dx:.6f} {float(m.group(2))+dy:.6f})",
        el_text
    )
    el_text = re.sub(
        r'(\(at\s+)([0-9\.\-]+)\s+([0-9\.\-]+)(\s+[0-9\.\-]+|\s+\([^)]+\))?\)',
        lambda m: f"{m.group(1)}{float(m.group(2))+dx:.6f} {float(m.group(3))+dy:.6f}{m.group(4) if m.group(4) else ''})",
        el_text
    )
    el_text = re.sub(
        r'\(center\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)',
        lambda m: f"(center {float(m.group(1))+dx:.6f} {float(m.group(2))+dy:.6f})",
        el_text
    )
    el_text = re.sub(
        r'\(xy\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)',
        lambda m: f"(xy {float(m.group(1))+dx:.6f} {float(m.group(2))+dy:.6f})",
        el_text
    )
    return el_text

def split_elements(pcb_path):
    with open(pcb_path, 'r', encoding='utf-8') as f:
        text = f.read()

    m = re.search(r'\n\t\((?:footprint|segment|via|gr_line|gr_text|gr_rect|gr_circle|zone)\b', text)
    if not m:
        raise ValueError("Could not find start of board elements")
    
    header = text[:m.start()]
    body = text[m.start():]
    
    body = body.rstrip()
    if body.endswith(')'):
        body = body[:-1].rstrip()

    raw_elements = re.split(r'\n(?=\t\()', body)
    elements = [el for el in raw_elements if el.strip()]
    return header, elements

def create_panel(single_path, out_path, offsets, panel_title):
    header, elements = split_elements(single_path)
    
    if '(title_block' in header:
        header = re.sub(r'\(title\s+"[^"]*"\)', f'(title "{panel_title}")', header)
    else:
        title_block = f'\t(title_block\n\t\t(title "{panel_title}")\n\t)\n'
        header = header.replace('\n\t(layers\n', '\n' + title_block + '\t(layers\n', 1)

    out_chunks = []
    for dx, dy in offsets:
        for el in elements:
            if el.startswith('\t(footprint '):
                out_chunks.append(offset_footprint(el, dx, dy))
            else:
                out_chunks.append(offset_other_element(el, dx, dy))

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(header)
        for chunk in out_chunks:
            f.write('\n' + chunk)
        f.write("\n)\n")
    print(f"Created {out_path} with {len(offsets)} boards.")

def main():
    single = 'Pi4_Robot_Carrier_1Layer.kicad_pcb'
    # Panel 2x: 2 boards vertically
    create_panel(
        single,
        'Pi4_Robot_Carrier_Panel_2x_A4.kicad_pcb',
        [(0.0, 0.0), (0.0, 78.0)],
        "Robot 4WD Carrier - Panel 2x A4"
    )

    # Panel 4x: 2x2 grid
    create_panel(
        single,
        'Pi4_Robot_Carrier_Panel_4x_A4.kicad_pcb',
        [(0.0, 0.0), (0.0, 78.0), (116.0, 0.0), (116.0, 78.0)],
        "Robot 4WD Carrier - Panel 4x A4"
    )

if __name__ == '__main__':
    main()
