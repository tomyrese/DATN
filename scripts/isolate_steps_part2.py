import docx, os, sys, subprocess, html, re
from docx.shared import Cm
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

DOCX_IN = 'test_step4.docx'

def test_file_with_word(docx_path):
    cmd = [
        'python', '-c',
        f'''
import win32com.client, os, sys
word = win32com.client.Dispatch('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(os.path.abspath(r"{docx_path}"), False, True, False)
    print("OK:", doc.Paragraphs.Count)
    doc.Close(False)
except Exception as e:
    print("ERR:", e)
finally:
    word.Quit(False)
'''
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
        return res.stdout.strip()
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/F', '/IM', 'WINWORD.EXE'], capture_output=True)
        return "TIMEOUT (Dialog Prompt!)"

def make_hyperlink_para(style="TableofFigures", anchor="", text="", page="", sz=26, b=False, sp_before=20, sp_after=20):
    b_tag = f'<w:b {nsdecls("w")}/><w:bCs {nsdecls("w")}/>' if b else ''
    xml = f'''
    <w:p {nsdecls("w")}>
        <w:pPr>
            <w:pStyle w:val="{style}"/>
            <w:tabs>
                <w:tab w:val="right" w:leader="dot" w:pos="9071"/>
            </w:tabs>
            <w:spacing w:before="{sp_before}" w:after="{sp_after}" w:line="260" w:lineRule="auto"/>
            <w:rPr>
                <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                {b_tag}
                <w:color w:val="000000"/>
                <w:sz w:val="{sz}"/>
                <w:szCs w:val="{sz}"/>
            </w:rPr>
        </w:pPr>
        <w:hyperlink w:anchor="{anchor}" w:history="1">
            <w:r>
                <w:rPr>
                    <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                    {b_tag}
                    <w:color w:val="000000"/>
                    <w:sz w:val="{sz}"/>
                    <w:szCs w:val="{sz}"/>
                    <w:u w:val="none"/>
                </w:rPr>
                <w:t>{html.escape(text)}</w:t>
            </w:r>
            <w:r>
                <w:rPr>
                    <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                    <w:sz w:val="{sz}"/>
                    <w:szCs w:val="{sz}"/>
                </w:rPr>
                <w:tab/>
            </w:r>
            <w:r>
                <w:rPr>
                    <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                    {b_tag}
                    <w:color w:val="000000"/>
                    <w:sz w:val="{sz}"/>
                    <w:szCs w:val="{sz}"/>
                    <w:u w:val="none"/>
                </w:rPr>
                <w:t>{html.escape(page)}</w:t>
            </w:r>
        </w:hyperlink>
    </w:p>
    '''
    return parse_xml(xml)

doc = docx.Document(DOCX_IN)

# Step 5: Danh mục hình ảnh
figures_items = [
    ("Hình 1.1: So sánh các nền tảng điều khiển robot phổ biến", "13", "_Toc_Hinh_1_1"),
    ("Hình 1.2: Bo mạch máy tính nhúng Raspberry Pi 4 Model B (8GB)", "14", "_Toc_Hinh_1_2"),
    ("Hình 1.3: Động cơ giảm tốc vàng TT trục kép 3-6VDC và bánh xe Mecanum", "15", "_Toc_Hinh_1_3"),
]
p_dmha = None
p_dmbb = None
for p in doc.paragraphs:
    if p.text.strip() == "DANH MỤC HÌNH ẢNH": p_dmha = p
    elif p.text.strip() == "DANH MỤC BẢNG BIỂU": p_dmbb = p
if p_dmha and p_dmbb:
    curr = p_dmha._p.getnext()
    while curr is not None and curr != p_dmbb._p:
        nxt = curr.getnext()
        curr.getparent().remove(curr)
        curr = nxt
    for fig_title, page, bm_name in figures_items:
        p_fig_hl = make_hyperlink_para("TableofFigures", bm_name, fig_title, page, sz=26, b=False)
        p_dmbb._p.addprevious(p_fig_hl)

doc.save('test_step5.docx')
print("Step 5 (Figures):", test_file_with_word('test_step5.docx'))

# Step 7: Bookmarks
bm_id_counter = 1000
def add_bookmark(p_elem, bm_name, bm_id):
    bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bm_id}" w:name="{bm_name}"/>')
    bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bm_id}"/>')
    pPr = p_elem.pPr
    if pPr is not None:
        pPr.addnext(bm_start)
    else:
        p_elem.insert(0, bm_start)
    p_elem.append(bm_end)

add_bookmark(doc.paragraphs[150]._p, "_Toc_Hinh_1_1", 1001)
doc.save('test_step7.docx')
print("Step 7 (Bookmarks):", test_file_with_word('test_step7.docx'))

