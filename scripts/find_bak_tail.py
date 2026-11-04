with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

# Let's inspect where the last segment/via ends
# We can find all segments and vias and Edge.Cuts in bak
idx = 0
last_item_end = 0
while True:
    pos_seg = bak.find('(segment', idx)
    pos_via = bak.find('(via', idx)
    positions = [p for p in [pos_seg, pos_via] if p != -1]
    if not positions:
        break
    m = min(positions)
    # find closing ) for this item
    # simple balance
    lvl = 0
    i = m
    while i < len(bak):
        if bak[i] == '(':
            lvl += 1
        elif bak[i] == ')':
            lvl -= 1
            if lvl == 0:
                last_item_end = i + 1
                break
        i += 1
    idx = last_item_end

print(f"Last track/via ends at {last_item_end}")
print("What comes after last track/via in bak:")
print(repr(bak[last_item_end:]))

