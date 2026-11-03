import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import win32com.client, os, sys

sys.stdout.reconfigure(encoding='utf-8')

# Create test doc
doc = docx.Document()
p_head = doc.add_paragraph("CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI")
# Add bookmark
bm_id = "100"
bm_name = "_Toc_CH1"
bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bm_id}" w:name="{bm_name}"/>')
bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bm_id}"/>')
p_head._p.insert(0, bm_start)
p_head._p.append(bm_end)

# Add TOC entry with hyperlink containing only w:r
p_toc = doc.add_paragraph()
hl_xml = f'''
<w:hyperlink {nsdecls("w")} w:anchor="{bm_name}" w:history="1">
    <w:r>
        <w:rPr>
            <w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
            <w:color {nsdecls("w")} w:val="000000"/>
            <w:sz {nsdecls("w")} w:val="28"/>
            <w:szCs {nsdecls("w")} w:val="28"/>
        </w:rPr>
        <w:t {nsdecls("w")}>CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI</w:t>
    </w:r>
    <w:r>
        <w:tab {nsdecls("w")}/>
    </w:r>
    <w:r>
        <w:rPr>
            <w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
            <w:color {nsdecls("w")} w:val="000000"/>
            <w:sz {nsdecls("w")} w:val="28"/>
            <w:szCs {nsdecls("w")} w:val="28"/>
        </w:rPr>
        <w:t {nsdecls("w")}>13</w:t>
    </w:r>
</w:hyperlink>
'''
p_toc._p.append(parse_xml(hl_xml))
test_file = os.path.abspath("test_clean_hl.docx")
doc.save(test_file)
print("Saved test_clean_hl.docx!")

# Test with Word COM
word = None
try:
    word = win32com.client.Dispatch('Word.Application')
    word.Visible = False
    doc_word = word.Documents.Open(test_file, False, True, False)
    print("SUCCESS: Word opened test_clean_hl.docx cleanly! Paragraphs:", doc_word.Paragraphs.Count)
    doc_word.Close(False)
except Exception as e:
    print("Error:", e)
finally:
    if word:
        try: word.Quit(False)
        except: pass

