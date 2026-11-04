# Analyze the new pin locations and connections
# Rasp_PI4 header center: X = 103.19, Y = 94.8275

# Pin mapping:
# For pin P:
# if P is odd: old x_rel was -24.13 + (P-1)/2 * 2.54
# new x_rel is negated: - (-24.13 + (P-1)/2 * 2.54) = 24.13 - (P-1)/2 * 2.54
# which is equal to the old position of pin (40 - P)!
# if P is even: old x_rel was -24.13 + (P-2)/2 * 2.54
# new x_rel is negated: 24.13 - (P-2)/2 * 2.54
# which is equal to the old position of pin (42 - P)!

pins = {}
for p in range(1, 41):
    if p % 2 == 1:
        # odd row: y_rel = -1.27
        col = (p - 1) // 2
        old_x = -24.13 + col * 2.54
        new_x = -old_x
        pins[p] = (new_x + 103.19, -1.27 + 94.8275)
    else:
        # even row: y_rel = 1.27
        col = (p - 2) // 2
        old_x = -24.13 + col * 2.54
        new_x = -old_x
        pins[p] = (new_x + 103.19, 1.27 + 94.8275)

print("Pi 4 Header Pins (World Coordinates):")
for p in sorted(pins.keys()):
    print(f"Pin {p:2d}: ({pins[p][0]:.2f}, {pins[p][1]:.2f})")

