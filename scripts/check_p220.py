import docx, sys
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('PL2_Robot_TuHanh_Pi44.docx')
for i in range(220, 235):
    print(f"P[{i}]: [{doc.paragraphs[i].style.name}] {repr(doc.paragraphs[i].text)}")

