import zipfile, sys
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

with zipfile.ZipFile('PL2_Robot_TuHanh_Pi44.docx') as z:
    tree = ET.fromstring(z.read('word/document.xml'))
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    bookmarks = tree.findall('.//w:bookmarkStart', namespaces)
    non_toc = [b.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}name') for b in bookmarks if not b.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}name', '').startswith('_Toc')]
    print(f"Non-toc bookmarks: {non_toc}")

