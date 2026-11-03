import docx, sys
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('PL2_Robot_TuHanh_Pi44.docx')

print("=== CHECKING TOC AND HEADINGS ===")
for i, p in enumerate(doc.paragraphs[:120]):
    t = p.text.strip()
    if any(k in t for k in ['MỤC LỤC', 'DANH MỤC', 'MỞ ĐẦU', 'CHƯƠNG', 'Bảng 1.1', 'Hình 1.1']):
        print(f"P[{i}]: [{p.style.name}] {t[:80]}")

print("\n=== CHECKING REFERENCES (End of doc) ===")
for i, p in enumerate(doc.paragraphs[-35:], start=len(doc.paragraphs)-35):
    t = p.text.strip()
    if t:
        print(f"P[{i}]: [{p.style.name}] {t[:90]}")

