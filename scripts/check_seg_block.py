with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

# In Pi4_Robot_Carrier_1Layer.kicad_pcb.bak:
# Where do segments start?
import re
seg_start = text.find('\t(segment')
if seg_start != -1:
    before_segs = text[:seg_start]
    after_segs = text[text.rfind('\n\t)') + 4:]
    print("Found segment block from index", seg_start)
    print("Before segs length:", len(before_segs))
    print("After segs length:", len(after_segs))
