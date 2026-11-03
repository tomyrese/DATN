import docx, sys
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('PL2_Robot_TuHanh_Pi44.docx')

font_names = set()
font_sizes = set()

for p in doc.paragraphs:
    for r in p.runs:
        if r.font.name:
            font_names.add(r.font.name)
        if r.font.size:
            font_sizes.add(r.font.size.pt)

for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    if r.font.name:
                        font_names.add(r.font.name)
                    if r.font.size:
                        font_sizes.add(r.font.size.pt)

print("Unique font names across document:", font_names)
print("Unique font sizes across document:", sorted(list(font_sizes)))

