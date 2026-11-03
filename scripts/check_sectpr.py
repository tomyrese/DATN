import zipfile, sys
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

with zipfile.ZipFile('PL2_Robot_TuHanh_Pi44.docx') as z:
    tree = ET.fromstring(z.read('word/document.xml'))
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    sectPrs = tree.findall('.//w:sectPr', namespaces)
    print(f"Total sectPr elements: {len(sectPrs)}")
    for i, sp in enumerate(sectPrs):
        pgMar = sp.find('w:pgMar', namespaces)
        pgSz = sp.find('w:pgSz', namespaces)
        print(f"sectPr[{i}]: pgMar={pgMar.attrib if pgMar is not None else None}, pgSz={pgSz.attrib if pgSz is not None else None}")

