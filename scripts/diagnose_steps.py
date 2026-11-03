import os, sys, zipfile, shutil, html, re, win32com.client
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

DOCX_ORIG = 'PL2_Robot_TuHanh_Pi44_backup_before_hyperlink.docx'
TEMP_DIR = 'temp_diag'
W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

ET.register_namespace('w', W_NS)
ET.register_namespace('r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
ET.register_namespace('m', 'http://schemas.openxmlformats.org/officeDocument/2006/math')
ET.register_namespace('v', 'urn:schemas-microsoft-com:vml')
ET.register_namespace('wp', 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing')
ET.register_namespace('w14', 'http://schemas.microsoft.com/office/word/2010/wordml')
ET.register_namespace('w15', 'http://schemas.microsoft.com/office/word/2012/wordml')

def qn(tag):
    return f"{{{W_NS}}}{tag}"

def save_and_test(tree, step_name):
    doc_xml_path = os.path.join(TEMP_DIR, 'word', 'document.xml')
    tree.write(doc_xml_path, xml_declaration=True, encoding='utf-8')
    test_out = f"test_{step_name}.docx"
    with zipfile.ZipFile(test_out, 'w', zipfile.ZIP_DEFLATED) as z_out:
        for foldername, subfolders, filenames in os.walk(TEMP_DIR):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, TEMP_DIR)
                z_out.write(file_path, arcname)
    
    word = None
    try:
        word = win32com.client.Dispatch('Word.Application')
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(os.path.abspath(test_out), False, True, False)
        cnt = doc.Paragraphs.Count
        doc.Close(False)
        print(f"Step '{step_name}': SUCCESS! Paragraphs: {cnt}")
        return True
    except Exception as e:
        print(f"Step '{step_name}': FAILED! {e}")
        return False
    finally:
        if word:
            try: word.Quit(False)
            except: pass

if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)
os.makedirs(TEMP_DIR)
with zipfile.ZipFile(DOCX_ORIG, 'r') as z:
    z.extractall(TEMP_DIR)

doc_xml_path = os.path.join(TEMP_DIR, 'word', 'document.xml')
tree = ET.parse(doc_xml_path)
root = tree.getroot()
body = root.find(qn('body'))

# Step 1: Just parse & save without changes
save_and_test(tree, "01_resave")

# Step 2: Margins
for sectPr in body.iter(qn('sectPr')):
    pgMar = sectPr.find(qn('pgMar'))
    if pgMar is not None:
        pgMar.set(qn('top'), '1134')
        pgMar.set(qn('bottom'), '1134')
        pgMar.set(qn('left'), '1701')
        pgMar.set(qn('right'), '1134')
        pgMar.set(qn('header'), '709')
        pgMar.set(qn('footer'), '709')
        pgMar.set(qn('gutter'), '0')
    pgSz = sectPr.find(qn('pgSz'))
    if pgSz is not None:
        pgSz.set(qn('w'), '11906')
        pgSz.set(qn('h'), '16838')
save_and_test(tree, "02_margins")

# Step 3: Remove old bookmarks
for p in body.iter(qn('p')):
    for bm in list(p.findall(qn('bookmarkStart'))):
        p.remove(bm)
    for bm in list(p.findall(qn('bookmarkEnd'))):
        p.remove(bm)
for bm in list(body.findall(qn('bookmarkEnd'))):
    body.remove(bm)
save_and_test(tree, "03_remove_old_bm")
