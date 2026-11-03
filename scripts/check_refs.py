import docx, sys
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('PL2_Robot_TuHanh_Pi44.docx')
for i in range(360, len(doc.paragraphs)):
    p = doc.paragraphs[i]
    print(f"P[{i}] [{p.style.name}]: {repr(p.text)}")

