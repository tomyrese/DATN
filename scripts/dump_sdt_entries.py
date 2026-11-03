import zipfile, sys
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

with zipfile.ZipFile('PL2_Robot_TuHanh_Pi44.docx') as z:
    tree = ET.fromstring(z.read('word/document.xml'))
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    sdt = tree.find('.//w:sdt', namespaces)
    sdtContent = sdt.find('w:sdtContent', namespaces)
    for i, p in enumerate(sdtContent.findall('w:p', namespaces)):
        pStyle = p.find('.//w:pStyle', namespaces)
        st_val = pStyle.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if pStyle is not None else 'None'
        texts = [t.text for t in p.findall('.//w:t', namespaces) if t.text]
        full_text = ''.join(texts)
        print(f"sdt[{i:2d}] [{st_val:8s}]: {full_text}")

