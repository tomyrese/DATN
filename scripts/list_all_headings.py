import docx, sys
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('PL2_Robot_TuHanh_Pi44.docx')

print("Paragraphs in doc:")
for idx, p in enumerate(doc.paragraphs):
    st = p.style.name
    t = p.text.strip()
    if not t:
        continue
    if st.startswith('Heading') or st in ['Title', 'Subtitle'] or any(t.startswith(k) for k in ['CHƯƠNG', 'MỞ ĐẦU', 'KẾT LUẬN', 'TÀI LIỆU', 'PHỤ LỤC', 'DANH MỤC', '1.', '2.', '3.', '4.', 'Bảng', 'Hình']):
        print(f"{idx:3d} | style={st:15s} | {t[:80]}")

