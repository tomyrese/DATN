import re

def swap_tb6612_rows(fp_text):
    def replace_pad(m):
        p_body = m.group(0)
        at_m = re.search(r'\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)', p_body)
        if at_m:
            x, y, rot = float(at_m.group(1)), float(at_m.group(2)), at_m.group(3)
            new_x = -x
            rot_str = f" {rot}" if rot else ""
            new_at = f"(at {new_x:.2f} {y:.2f}{rot_str})"
            p_body = re.sub(r'\(at\s+[-\d\.]+\s+[-\d\.]+(?:\s+[-\d\.]+)?\)', new_at, p_body)
        return p_body

    fp_text = re.sub(r'\(pad\s+"([0-9]+)"[\s\S]*?\n\t\t\)', replace_pad, fp_text)

    def replace_fp_text(m):
        t_body = m.group(0)
        at_m = re.search(r'\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)', t_body)
        if at_m:
            x, y, rot = float(at_m.group(1)), float(at_m.group(2)), at_m.group(3)
            if abs(x) > 3.0:
                new_x = -x
                rot_str = f" {rot}" if rot else ""
                new_at = f"(at {new_x:.1f} {y:.2f}{rot_str})"
                t_body = re.sub(r'\(at\s+[-\d\.]+\s+[-\d\.]+(?:\s+[-\d\.]+)?\)', new_at, t_body)
        return t_body

    fp_text = re.sub(r'\(fp_text\s+user\s+"[^"]+"[\s\S]*?\n\t\t\)', replace_fp_text, fp_text)
    return fp_text

def mirror_pi4_header(fp_text):
    def replace_pad(m):
        p_body = m.group(0)
        at_m = re.search(r'\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)', p_body)
        if at_m:
            x, y, rot = float(at_m.group(1)), float(at_m.group(2)), at_m.group(3)
            new_x = -x
            rot_str = f" {rot}" if rot else ""
            new_at = f"(at {new_x:.2f} {y:.2f}{rot_str})"
            p_body = re.sub(r'\(at\s+[-\d\.]+\s+[-\d\.]+(?:\s+[-\d\.]+)?\)', new_at, p_body)
        return p_body

    fp_text = re.sub(r'\(pad\s+"([0-9]+)"[\s\S]*?\n\t\t\)', replace_pad, fp_text)

    def replace_silk_text(m):
        t_body = m.group(0)
        at_m = re.search(r'\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)', t_body)
        if at_m:
            x, y, rot = float(at_m.group(1)), float(at_m.group(2)), at_m.group(3)
            new_x = -x
            rot_str = f" {rot}" if rot else ""
            new_at = f"(at {new_x:.1f} {y:.2f}{rot_str})"
            t_body = re.sub(r'\(at\s+[-\d\.]+\s+[-\d\.]+(?:\s+[-\d\.]+)?\)', new_at, t_body)
        return t_body

    fp_text = re.sub(r'\(fp_text\s+user\s+"(1|40)"[\s\S]*?\n\t\t\)', replace_silk_text, fp_text)
    return fp_text
