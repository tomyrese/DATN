import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace rotation of LEFT and RIGHT from 90 to 270
def repl_fp_rot(content, ref_name):
    pattern = r'(\(footprint\s+"Module_TB6612FNG_Breakout"[\s\S]*?\(at\s+([-\d.]+)\s+([-\d.]+))\s+90([\s\S]*?\(property\s+"Reference"\s+"' + ref_name + r'")'
    match = re.search(pattern, content)
    if match:
        old_str = match.group(0)
        new_str = old_str.replace(' 90\n', ' 270\n').replace(' 90)', ' 270)')
        content = content.replace(old_str, new_str)
        print(f"Updated rotation for {ref_name} to 270!")
    else:
        print(f"Pattern not found for {ref_name}!")
    return content

text = repl_fp_rot(text, 'LEFT')
text = repl_fp_rot(text, 'RIGHT')

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved updated Pi4_Robot_Carrier_1Layer.kicad_pcb with rot=270!")

