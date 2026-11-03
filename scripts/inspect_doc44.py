import docx, sys

sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('PL2_Robot_TuHanh_Pi44.docx')

print(f"Total paragraphs: {len(doc.paragraphs)}")
print(f"Total tables: {len(doc.tables)}")
print(f"Total sections: {len(doc.sections)}")

for i, sec in enumerate(doc.sections):
    print(f"\n--- Section {i+1} ---")
    print(f"  Page width: {sec.page_width.cm:.2f} cm, height: {sec.page_height.cm:.2f} cm")
    print(f"  Margins: top={sec.top_margin.cm:.2f} cm, bottom={sec.bottom_margin.cm:.2f} cm, left={sec.left_margin.cm:.2f} cm, right={sec.right_margin.cm:.2f} cm")

# Scan first 50 paragraphs to see titles, TOC, etc.
print("\n--- First 60 Paragraphs ---")
for i, p in enumerate(doc.paragraphs[:60]):
    txt = p.text.strip()
    if txt:
        style_name = p.style.name if p.style else 'NoStyle'
        print(f"[{i:3d}] ({style_name}): {txt[:90]}")

