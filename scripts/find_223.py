import docx, re, sys
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('PL2_Robot_TuHanh_Pi44.docx')
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if '2.2.3' in t:
        print(f"2.2.3 found at P[{i}]: {t}")
    if '2.4' in t:
        print(f"2.4 found at P[{i}]: {t}")

