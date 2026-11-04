import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

junk_texts = re.findall(r'\(gr_text\s+"([^"]+)"', text)
print(f"Total gr_text found: {len(junk_texts)}")
for t in junk_texts:
    print(" ", t)

dash_lines = re.findall(r'\(type\s+dash\)', text)
print(f"Total dash lines found: {len(dash_lines)}")

