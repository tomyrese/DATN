import re

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace labels on U_PI4:
# We match by exact position!
replacements = [
    # Pin 3: was PWMA_L -> now PWMA_R
    (r'\(label\s+"PWMA_L"\s+\(at\s+53\.34\s+137\.16\s+180\)', '(label "PWMA_R" (at 53.34 137.16 180)'),
    # Pin 5: was AIN2_L -> now AIN2_R
    (r'\(label\s+"AIN2_L"\s+\(at\s+53\.34\s+142\.24\s+180\)', '(label "AIN2_R" (at 53.34 142.24 180)'),
    # Pin 7: was AIN1_L -> now AIN1_R
    (r'\(label\s+"AIN1_L"\s+\(at\s+53\.34\s+147\.32\s+180\)', '(label "AIN1_R" (at 53.34 147.32 180)'),
    # Pin 11: was STBY_L -> now STBY_R
    (r'\(label\s+"STBY_L"\s+\(at\s+53\.34\s+157\.48\s+180\)', '(label "STBY_R" (at 53.34 157.48 180)'),
    # Pin 13: was TRIG_L -> now TRIG_R
    (r'\(label\s+"TRIG_L"\s+\(at\s+53\.34\s+162\.56\s+180\)', '(label "TRIG_R" (at 53.34 162.56 180)'),
    # Pin 15: was ECHO_L -> now ECHO_R
    (r'\(label\s+"ECHO_L"\s+\(at\s+53\.34\s+167\.64\s+180\)', '(label "ECHO_R" (at 53.34 167.64 180)'),
    # Pin 29: was TRIG_R -> now TRIG_L
    (r'\(label\s+"TRIG_R"\s+\(at\s+53\.34\s+203\.2\s+180\)', '(label "TRIG_L" (at 53.34 203.2 180)'),
    # Pin 31: was ECHO_R -> now ECHO_L
    (r'\(label\s+"ECHO_R"\s+\(at\s+53\.34\s+208\.28\s+180\)', '(label "ECHO_L" (at 53.34 208.28 180)'),
    # Pin 33: was PWMA_R -> now PWMA_L
    (r'\(label\s+"PWMA_R"\s+\(at\s+53\.34\s+213\.36\s+180\)', '(label "PWMA_L" (at 53.34 213.36 180)'),
    # Pin 35: was AIN2_R -> now AIN2_L
    (r'\(label\s+"AIN2_R"\s+\(at\s+53\.34\s+218\.44\s+180\)', '(label "AIN2_L" (at 53.34 218.44 180)'),
    # Pin 37: was AIN1_R -> now AIN1_L
    (r'\(label\s+"AIN1_R"\s+\(at\s+53\.34\s+223\.52\s+180\)', '(label "AIN1_L" (at 53.34 223.52 180)'),
    # Pin 38: was STBY_R -> now STBY_L
    (r'\(label\s+"STBY_R"\s+\(at\s+157\.48\s+223\.52\s+0\)', '(label "STBY_L" (at 157.48 223.52 0)')
]

for pat, repl in replacements:
    new_text, count = re.subn(pat, repl, text)
    if count == 0:
        print(f"Warning: pattern {pat} not found!")
    text = new_text

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(text)

with open('robot_electronics.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated schematic files successfully!")

