import zipfile, sys
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

with zipfile.ZipFile('PL2_Robot_TuHanh_Pi44.docx') as z:
    tree = ET.fromstring(z.read('word/document.xml'))
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    body = tree.find('w:body', namespaces)
    paras = body.findall('w:p', namespaces)
    print("Paragraph 72 XML:")
    print(ET.tostring(paras[72], encoding='unicode'))

