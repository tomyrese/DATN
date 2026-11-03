import docx, os, sys, subprocess, html
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

DOCX_IN = 'test_step7.docx'

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

def make_para(style="Normal", text="", space_before=60, space_after=60, line=312, sz=26, b=False, i=False, align="both"):
    rPr_parts = [
        f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
    ]
    if b: rPr_parts.append(f'<w:b {nsdecls("w")}/><w:bCs {nsdecls("w")}/>')
    rPr_parts.append(f'<w:sz {nsdecls("w")} w:val="{sz}"/><w:szCs {nsdecls("w")} w:val="{sz}"/>')
    
    run_xml = f'''
    <w:r {nsdecls("w")}>
        <w:rPr>{"".join(rPr_parts)}</w:rPr>
        <w:t xml:space="preserve">{html.escape(text)}</w:t>
    </w:r>
    '''
    full_xml = f'''
    <w:p {nsdecls("w")}>
        <w:pPr>
            <w:pStyle w:val="{style}"/>
            <w:spacing w:before="{space_before}" w:after="{space_after}" w:line="{line}" w:lineRule="auto"/>
            <w:jc w:val="{align}"/>
            <w:rPr>{"".join(rPr_parts)}</w:rPr>
        </w:pPr>
        {run_xml}
    </w:p>
    '''
    return parse_xml(full_xml)

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

# Step 8: SDT TOC
sdt_list = doc._element.xpath('//w:sdt')
sdt = sdt_list[0]
sdtContent = sdt.find(qn('w:sdtContent'))
for child in list(sdtContent):
    sdtContent.remove(child)

p_toc_title = make_para("Title", "MỤC LỤC", space_before=240, space_after=240, sz=30, b=True, align="center")
sdtContent.append(p_toc_title)

p_hl = make_hyperlink_para("TOC1", "_Toc_Hinh_1_1", "DANH MỤC HÌNH ẢNH", "7", sz=28, b=True)
sdtContent.append(p_hl)

doc.save('test_step8.docx')
print("Step 8 (SDT TOC):", test_file_with_word('test_step8.docx'))

# Step 9: Font enforcement
for r in doc._element.xpath('.//w:r'):
    rPr = r.find(qn('w:rPr'))
    if rPr is not None:
        rFonts = rPr.find(qn('w:rFonts'))
        if rFonts is not None:
            rFonts.set(qn('w:ascii'), 'Times New Roman')
            rFonts.set(qn('w:hAnsi'), 'Times New Roman')
            rFonts.set(qn('w:cs'), 'Times New Roman')
            rFonts.set(qn('w:eastAsia'), 'Times New Roman')

doc.save('test_step9.docx')
print("Step 9 (Font enforcement):", test_file_with_word('test_step9.docx'))

