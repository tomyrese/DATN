import docx, os, sys, win32com.client
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('PL2_Robot_TuHanh_Pi44_backup_before_hyperlink.docx')

sdt = doc._element.xpath('//w:sdt')[0]
sdtContent = sdt.find(qn('w:sdtContent'))

# Add bookmark to paragraph 153
p153 = doc.paragraphs[153]._p
bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="9999" w:name="_Toc_CH1"/>')
bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="9999"/>')
p153.insert(0, bm_start)
p153.append(bm_end)

test_p = parse_xml(f'''
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
''')

# Clear sdtContent and add test_p
for child in list(sdtContent):
    sdtContent.remove(child)
sdtContent.append(test_p)

test_out = 'test_sdt_hyperlink.docx'
doc.save(test_out)
print(f'Saved {test_out}!')

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    doc_word = word.Documents.Open(os.path.abspath(test_out), False, True, False)
    print('SUCCESS! Word opened test_sdt_hyperlink.docx! Paragraphs:', doc_word.Paragraphs.Count)
    doc_word.Close(False)
except Exception as e:
    print('FAILED:', e)
finally:
    word.Quit(False)
