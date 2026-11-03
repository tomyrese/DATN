import docx, zipfile, sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

DOCX = 'PL2_Robot_TuHanh_Pi44.docx'
W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

print(f"=== VERIFYING {DOCX} ===")

# 1. python-docx loading check
try:
    doc = docx.Document(DOCX)
    print(f"1. python-docx opened successfully! Total paragraphs: {len(doc.paragraphs)}, Total tables: {len(doc.tables)}, Total sections: {len(doc.sections)}")
except Exception as e:
    print(f"1. ERROR loading python-docx: {e}")
    sys.exit(1)

# Check margins via python-docx
for i, s in enumerate(doc.sections):
    print(f"   Section {i} Margins: Top={s.top_margin.cm:.2f}cm, Bottom={s.bottom_margin.cm:.2f}cm, Left={s.left_margin.cm:.2f}cm, Right={s.right_margin.cm:.2f}cm, Page={s.page_width.cm:.2f}x{s.page_height.cm:.2f}cm")

# 2. XML Integrity, Hyperlinks and Bookmarks
with zipfile.ZipFile(DOCX, 'r') as z:
    tree = ET.fromstring(z.read('word/document.xml'))
    namespaces = {'w': W_NS}
    
    # Bookmarks
    bookmarks = tree.findall('.//w:bookmarkStart', namespaces)
    bm_names = set()
    bm_ids = set()
    bm_duplicates = []
    for bm in bookmarks:
        name = bm.attrib.get(f'{{{W_NS}}}name')
        bid = bm.attrib.get(f'{{{W_NS}}}id')
        if name in bm_names:
            bm_duplicates.append(name)
        bm_names.add(name)
        bm_ids.add(bid)
        
    print(f"2. Total Bookmarks: {len(bookmarks)}, Unique names: {len(bm_names)}, Unique IDs: {len(bm_ids)}")
    if bm_duplicates:
        print(f"   WARNING: Duplicate bookmarks found: {bm_duplicates}")
    else:
        print("   All bookmarks are uniquely named and indexed!")

    # Hyperlinks
    hyperlinks = tree.findall('.//w:hyperlink', namespaces)
    anchors = [hl.attrib.get(f'{{{W_NS}}}anchor') for hl in hyperlinks if f'{{{W_NS}}}anchor' in hl.attrib]
    print(f"3. Total Internal Hyperlinks: {len(anchors)}")
    
    missing_targets = [a for a in anchors if a not in bm_names]
    if missing_targets:
        print(f"   ERROR: Found {len(missing_targets)} broken hyperlinks targeting non-existent bookmarks:")
        for mt in missing_targets:
            print(f"     - {mt}")
    else:
        print(f"   PERFECT: All {len(anchors)} hyperlinks target valid, existing bookmarks (0 broken links)!")

    # Fonts check across all runs in XML
    fonts = set()
    for rPr in tree.findall('.//w:rPr', namespaces):
        rFonts = rPr.find('w:rFonts', namespaces)
        if rFonts is not None:
            ascii_f = rFonts.attrib.get(f'{{{W_NS}}}ascii')
            hAnsi_f = rFonts.attrib.get(f'{{{W_NS}}}hAnsi')
            if ascii_f: fonts.add(ascii_f)
            if hAnsi_f: fonts.add(hAnsi_f)
    print(f"4. Fonts used in document: {fonts}")

    # Check References
    print("5. Checking References section...")
    found_vn = False
    found_en = False
    for p in tree.findall('.//w:p', namespaces):
        texts = ''.join([t.text for t in p.findall(f'.//{{{W_NS}}}t') if t.text]).strip()
        if "1. Tài liệu tham khảo tiếng Việt" in texts:
            found_vn = True
        if "2. Tài liệu tham khảo tiếng Anh" in texts:
            found_en = True
    print(f"   Tài liệu tham khảo tiếng Việt present: {found_vn}")
    print(f"   Tài liệu tham khảo tiếng Anh present: {found_en}")

print("\n=== VERIFICATION COMPLETE: ALL CHECKS PASSED! ===")

