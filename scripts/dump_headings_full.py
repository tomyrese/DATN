import docx, sys
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('PL2_Robot_TuHanh_Pi44.docx')

print(f"Total paragraphs: {len(doc.paragraphs)}")
for i, p in enumerate(doc.paragraphs):
    st = p.style.name
    t = p.text.strip()
    if st.startswith('Heading') or st in ['Title', 'Subtitle'] or 'CHƯƠNG' in t.upper() or 'MỞ ĐẦU' in t.upper() or 'KẾT LUẬN' in t.upper() or 'TÀI LIỆU THAM KHẢO' in t.upper():
        print(f"P[{i:3d}] [{st}]: {t[:80]}")

