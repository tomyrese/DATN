import docx, re, sys
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('PL2_Robot_TuHanh_Pi44.docx')
mo_dau_idx = -1
for i, p in enumerate(doc.paragraphs):
    if p.text.strip() == "MỞ ĐẦU":
        mo_dau_idx = i
        break

print(f"MỞ ĐẦU is at paragraph {mo_dau_idx}")

print("\nFigures after MỞ ĐẦU:")
for i, p in enumerate(doc.paragraphs[mo_dau_idx:], start=mo_dau_idx):
    t = p.text.strip()
    if re.match(r'^Hình\s+\d+\.\d+', t):
        print(f"P[{i}]: {t[:60]}")

print("\nTables after MỞ ĐẦU:")
for i, p in enumerate(doc.paragraphs[mo_dau_idx:], start=mo_dau_idx):
    t = p.text.strip()
    if re.match(r'^Bảng\s+\d+\.\d+', t):
        print(f"P[{i}]: {t[:60]}")

