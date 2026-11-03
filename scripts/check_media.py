import zipfile, sys
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

with zipfile.ZipFile('PL2_Robot_TuHanh_Pi44.docx') as z:
    media_files = [f for f in z.namelist() if f.startswith('word/media/')]
    print(f"Total media files in docx: {len(media_files)}")
    for mf in media_files:
        info = z.getinfo(mf)
        print(f"  {mf}: {info.file_size} bytes")

    tree = ET.fromstring(z.read('word/document.xml'))
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    drawings = tree.findall('.//w:drawing', namespaces)
    print(f"Total w:drawing elements: {len(drawings)}")

