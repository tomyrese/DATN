import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import win32com.client, os, sys

sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document()
# Add heading with bookmark
p_head = doc.add_paragraph("CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI")
bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="101" w:name="_Toc_CH1"/>')
bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="101"/>')
p_head._p.insert(0, bm_start)
p_head._p.append(bm_end)

# Add TOC entry
p_xml = f'''
<w:p {nsdecls("w")}>
    <w:pPr>
        <w:pStyle w:val="TOC1"/>
        <w:tabs>
            <w:tab w:val="right" w:leader="dot" w:pos="9071"/>
        </w:tabs>
        <w:spacing w:before="40" w:after="40" w:line="260" w:lineRule="auto"/>
        <w:rPr>
            <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
            <w:b/>
            <w:bCs/>
            <w:color w:val="000000"/>
            <w:sz w:val="28"/>
            <w:szCs w:val="28"/>
        </w:rPr>
    </w:pPr>
    <w:hyperlink w:anchor="_Toc_CH1" w:history="1">
        <w:r>
            <w:rPr>
                <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                <w:b/>
                <w:bCs/>
                <w:color w:val="000000"/>
                <w:sz w:val="28"/>
                <w:szCs w:val="28"/>
                <w:u w:val="none"/>
            </w:rPr>
            <w:t>CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI</w:t>
        </w:r>
        <w:r>
            <w:rPr>
                <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                <w:sz w:val="28"/>
                <w:szCs w:val="28"/>
            </w:rPr>
            <w:tab/>
        </w:r>
        <w:r>
            <w:rPr>
                <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                <w:b/>
                <w:bCs/>
                <w:color w:val="000000"/>
                <w:sz w:val="28"/>
                <w:szCs w:val="28"/>
                <w:u w:val="none"/>
            </w:rPr>
            <w:t>13</w:t>
        </w:r>
    </w:hyperlink>
</w:p>
'''
doc._body._body.append(parse_xml(p_xml))

test_file = os.path.abspath("test_schema_valid.docx")
doc.save(test_file)
print("Saved test_schema_valid.docx!")

# Test with Word COM
word = None
try:
    word = win32com.client.Dispatch('Word.Application')
    word.Visible = False
    doc_word = word.Documents.Open(test_file, False, True, False)
    print("SUCCESS: Word opened test_schema_valid.docx without any warning! Count:", doc_word.Paragraphs.Count)
    doc_word.Close(False)
except Exception as e:
    print("Word error:", e)
finally:
    if word:
        try: word.Quit(False)
        except: pass

