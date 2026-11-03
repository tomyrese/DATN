import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = docx.Document()
p = doc.add_paragraph("Hello World")
bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="1" w:name="bm1"/>')
bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="1"/>')
if p._p.pPr is not None:
    p._p.pPr.addnext(bm_start)
else:
    p._p.insert(0, bm_start)
p._p.append(bm_end)

print("Paragraph children:", [c.tag.split("}")[-1] for c in p._p])

