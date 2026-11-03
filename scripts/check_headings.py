import zipfile, sys
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

with zipfile.ZipFile('PL2_Robot_TuHanh_Pi44.docx') as z:
    tree = ET.fromstring(z.read('word/styles.xml'))
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    for style in tree.findall('.//w:style', namespaces):
        sid = style.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId')
        if sid in ['Heading1', 'Heading2', 'Heading3']:
            print(f'Style: {sid}')
            numPr = style.find('.//w:numPr', namespaces)
            print('  numPr:', numPr is not None)
            rPr = style.find('.//w:rPr', namespaces)
            if rPr is not None:
                sz = rPr.find('w:sz', namespaces)
                rFonts = rPr.find('w:rFonts', namespaces)
                b = rPr.find('w:b', namespaces)
                print(f'  sz={sz.attrib if sz is not None else None}, b={b is not None}, fonts={rFonts.attrib if rFonts is not None else None}')

