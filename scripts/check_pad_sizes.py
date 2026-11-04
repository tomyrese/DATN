from load_footprints import fps

for name, p_dict in sorted(fps.items()):
    for p_num, p in p_dict.items():
        if p['sx'] != 2.0 or p['sy'] != 2.0 or p['drill'] != 0.8:
            print(f"Footprint {name} Pad {p_num}: size=({p['sx']}, {p['sy']}), drill={p['drill']}")

