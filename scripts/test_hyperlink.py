import docx
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

doc = docx.Document()
p = doc.add_paragraph("Target Heading")
# Add bookmark
bm_id = "101"
bm_name = "TEST_BM"
bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bm_id}" w:name="{bm_name}"/>')
bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bm_id}"/>')
p._p.insert(0, bm_start)
p._p.append(bm_end)

# Add TOC item with hyperlink
p_toc = doc.add_paragraph()
hl_xml = f'''
<w:hyperlink {nsdecls("w")} w:anchor="{bm_name}" w:history="1">
    <w:r>
        <w:rPr>
            <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
            <w:color w:val="000000"/>
            <w:sz w:val="26"/>
        </w:rPr>
        <w:t>CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI</w:t>
    </w:r>
    <w:r>
        <w:tab/>
    </w:r>
    <w:r>
        <w:rPr>
            <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
            <w:color w:val="000000"/>
            <w:sz w:val="26"/>
        </w:rPr>
        <w:t>13</w:t>
    </w:r>
</w:hyperlink>
'''
p_toc._p.append(parse_xml(hl_xml))
doc.save("test_hl.docx")
print("Saved test_hl.docx successfully!")

