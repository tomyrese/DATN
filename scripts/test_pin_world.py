from inspect_lib_symbols import lib_syms

def get_pin_world(sym_at, pin_at):
    X, Y = float(sym_at[0]), float(sym_at[1])
    rot = float(sym_at[2]) if len(sym_at) > 2 else 0.0
    px, py = float(pin_at[0]), float(pin_at[1])
    if rot == 0:
        return (round(X + px, 4), round(Y - py, 4))
    elif rot == 90:
        return (round(X - py, 4), round(Y - px, 4))
    elif rot == 180:
        return (round(X - px, 4), round(Y + py, 4))
    elif rot == 270:
        return (round(X + py, 4), round(Y + px, 4))
    return (X, Y)

# Test on U_US1 at (243.84, 48.26, 0)
print("Testing U_US1:")
for pnum, pname, ptype, pat in lib_syms['robot_electronics:Sensor_HC_SR04']:
    pw = get_pin_world(['243.84', '48.26', '0'], pat)
    print(f"  Pin {pnum} ({pname}): symbol={pat} -> world={pw}")

