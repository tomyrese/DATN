import docx, os, sys, subprocess, html, re
from docx.shared import Cm
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

DOCX_IN = 'PL2_Robot_TuHanh_Pi44_backup_before_hyperlink.docx'

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

def make_para(style="Normal", text="", space_before=60, space_after=60, line=312, sz=26, b=False, i=False, align="both", indent_left=0, indent_hanging=0, indent_first=0):
    pPr_parts = []
    if style:
        pPr_parts.append(f'<w:pStyle {nsdecls("w")} w:val="{style}"/>')
    pPr_parts.append(f'<w:spacing {nsdecls("w")} w:before="{space_before}" w:after="{space_after}" w:line="{line}" w:lineRule="auto"/>')
    
    ind_attrs = []
    if indent_left > 0: ind_attrs.append(f'w:left="{indent_left}"')
    if indent_hanging > 0: ind_attrs.append(f'w:hanging="{indent_hanging}"')
    if indent_first > 0: ind_attrs.append(f'w:firstLine="{indent_first}"')
    if ind_attrs:
        pPr_parts.append(f'<w:ind {nsdecls("w")} {" ".join(ind_attrs)}/>')
        
    if align != "left":
        pPr_parts.append(f'<w:jc {nsdecls("w")} w:val="{align}"/>')
        
    rPr_parts = [
        f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
    ]
    if b: rPr_parts.append(f'<w:b {nsdecls("w")}/><w:bCs {nsdecls("w")}/>')
    if i: rPr_parts.append(f'<w:i {nsdecls("w")}/><w:iCs {nsdecls("w")}/>')
    rPr_parts.append(f'<w:sz {nsdecls("w")} w:val="{sz}"/><w:szCs {nsdecls("w")} w:val="{sz}"/>')
    
    pPr_parts.append(f'<w:rPr {nsdecls("w")}>{"".join(rPr_parts)}</w:rPr>')
    
    run_xml = f'''
    <w:r {nsdecls("w")}>
        <w:rPr>{"".join(rPr_parts)}</w:rPr>
        <w:t xml:space="preserve">{html.escape(text)}</w:t>
    </w:r>
    '''
    
    full_xml = f'''<w:p {nsdecls("w")}><w:pPr>{"".join(pPr_parts)}</w:pPr>{run_xml}</w:p>'''
    return parse_xml(full_xml)

doc = docx.Document(DOCX_IN)

# Step 1: Margins
for section in doc.sections:
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.0)

# Step 2: Remove old bookmarks
for p in doc.paragraphs:
    for bm in p._p.xpath('.//w:bookmarkStart[starts-with(@w:name, "_Toc")]'):
        bm.getparent().remove(bm)
doc.save('test_step2.docx')
print("Step 2 (Remove old bm):", test_file_with_word('test_step2.docx'))

# Step 3: Insert Section 2.3 & Figure 2.4
target_p = None
for p in doc.paragraphs:
    if p.text.strip().startswith("2.4 Xử lý cảm biến"):
        target_p = p
        break
if target_p:
    p_sec23_head = make_para("Heading2", "2.3 Động học và điều khiển hệ thống bánh xe đa hướng Mecanum", space_before=160, space_after=80, sz=28, b=True, align="left")
    p_sec23_body = make_para("Normal", "Hệ thống di chuyển của robot sử dụng 04 bánh xe đa hướng Mecanum...", space_before=60, space_after=60, line=312, sz=26, align="both", indent_first=567)
    p_sec23_fig = make_para("Caption", "Hình 2.4: Nguyên lý phân bố vector lực và vận tốc của bánh xe đa hướng Mecanum", space_before=80, space_after=120, line=260, sz=24, b=True, i=True, align="center")
    target_p._p.addprevious(p_sec23_head)
    target_p._p.addprevious(p_sec23_body)
    target_p._p.addprevious(p_sec23_fig)
doc.save('test_step3.docx')
print("Step 3 (Insert 2.3 & Fig 2.4):", test_file_with_word('test_step3.docx'))

# Step 4: References
ref_title_p = None
phu_luc_p = None
for p in doc.paragraphs:
    t = p.text.strip()
    if t == "TÀI LIỆU THAM KHẢO": ref_title_p = p
    elif t == "PHỤ LỤC": phu_luc_p = p
if ref_title_p and phu_luc_p:
    curr = ref_title_p._p.getnext()
    while curr is not None and curr != phu_luc_p._p:
        nxt = curr.getnext()
        curr.getparent().remove(curr)
        curr = nxt
    vn_head = make_para("Heading2", "1. Tài liệu tham khảo tiếng Việt", space_before=160, space_after=80, sz=28, b=True, align="left")
    phu_luc_p._p.addprevious(vn_head)
    p_ref1 = make_para("Normal", "[1] Giáo trình Kỹ thuật Robot.", space_before=40, space_after=80, line=312, sz=26, align="both")
    phu_luc_p._p.addprevious(p_ref1)
    en_head = make_para("Heading2", "2. Tài liệu tham khảo tiếng Anh", space_before=240, space_after=80, sz=28, b=True, align="left")
    phu_luc_p._p.addprevious(en_head)
    p_ref2 = make_para("Normal", "[1] Raspberry Pi Foundation Guide.", space_before=40, space_after=80, line=312, sz=26, align="both")
    phu_luc_p._p.addprevious(p_ref2)
doc.save('test_step4.docx')
print("Step 4 (References):", test_file_with_word('test_step4.docx'))
