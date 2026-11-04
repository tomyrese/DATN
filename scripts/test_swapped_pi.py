def get_swapped_pi_pad(x0, y0, pin):
    # Pin 1 swaps with 39, 2 with 40, 3 with 37, 4 with 38 ...
    # i.e. col becomes 19 - col, row stays same!
    col = (pin - 1) // 2
    row = (pin - 1) % 2
    swapped_col = 19 - col
    lx = -24.13 + swapped_col * 2.54
    ly = -1.27 if row == 0 else 1.27
    wx = x0 + lx
    wy = y0 + ly
    return round(wx, 2), round(wy, 2)

print("=== SWAPPED PI 4 (X-MIRROR) at (103.19, 94.83) ===")
for p in [1, 2, 3, 4, 5, 6, 11, 13, 16, 18, 19, 21, 23, 32, 33, 35, 36, 37, 38]:
    pos = get_swapped_pi_pad(103.19, 94.83, p)
    facing = "North" if pos[1] < 94.83 else "South"
    print(f"  Pin {p:2}: {pos} facing {facing}")

