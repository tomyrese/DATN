import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = docx.Document()
p = doc.add_paragraph("Target Heading")
bm_id = "101"
bm_name = "TEST_BM"
p._p.insert(0, parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bm_id}" w:name="{bm_name}"/>'))
p._p.append(parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bm_id}"/>'))

p_toc = doc.add_paragraph()
hl_xml = f'''
<w:hyperlink {nsdecls("w")} w:anchor="{bm_name}" w:history="1">
    <w:r>
        <w:rPr>
            <w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
            <w:color {nsdecls("w")} w:val="000000"/>
            <w:sz {nsdecls("w")} w:val="26"/>
            <w:szCs {nsdecls("w")} w:val="26"/>
        </w:rPr>
        <w:t {nsdecls("w")}>CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI</w:t>
    </w:r>
    <w:r>
        <w:rPr>
            <w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
            <w:color {nsdecls("w")} w:val="000000"/>
            <w:sz {nsdecls("w")} w:val="26"/>
            <w:szCs {nsdecls("w")} w:val="26"/>
        </w:rPr>
        <w:tab {nsdecls("w")}/>
    </w:r>
    <w:fldSimple {nsdecls("w")} w:instr="PAGEREF {bm_name} \h">
        <w:r>
            <w:rPr>
                <w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
                <w:color {nsdecls("w")} w:val="000000"/>
                <w:sz {nsdecls("w")} w:val="26"/>
                <w:szCs {nsdecls("w")} w:val="26"/>
            </w:rPr>
            <w:t {nsdecls("w")}>13</w:t>
        </w:r>
    </w:fldSimple>
</w:hyperlink>
'''
p_toc._p.append(parse_xml(hl_xml))
doc.save("test_hl2.docx")
print("Saved test_hl2.docx successfully!")

