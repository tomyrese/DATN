import docx, re, sys
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('PL2_Robot_TuHanh_Pi44.docx')

print("=== DANH MỤC HÌNH ẢNH in DOC (p[72:94]) ===")
for i in range(72, 94):
    print(f"{i}: {repr(doc.paragraphs[i].text)}")

print("\n=== DANH MỤC BẢNG BIỂU in DOC (p[97:110]) ===")
for i in range(97, 110):
    print(f"{i}: {repr(doc.paragraphs[i].text)}")

print("\n=== FIGURES IN BODY ===")
for i, p in enumerate(doc.paragraphs):
    if i >= 114 and re.match(r'^Hình\s+\d+\.\d+', p.text.strip()):
        print(f"P[{i}]: {repr(p.text.strip())}")

print("\n=== TABLES IN BODY ===")
for i, p in enumerate(doc.paragraphs):
    if i >= 114 and re.match(r'^Bảng\s+\d+\.\d+', p.text.strip()):
        print(f"P[{i}]: {repr(p.text.strip())}")

