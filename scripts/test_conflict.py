# Pi 4 40-Pin Header Definition:
# Standard Raspberry Pi 4 Pinout:
pi_pins = {
    1: ("+3V3", "POWER"),
    2: ("+5V", "POWER"),
    3: ("GPIO2_SDA", "I/O 3.3V"),
    4: ("+5V", "POWER"),
    5: ("GPIO3_SCL", "I/O 3.3V"),
    6: ("GND", "POWER"),
    7: ("GPIO4", "I/O 3.3V"),
    8: ("GPIO14_TXD", "I/O 3.3V"),
    9: ("GND", "POWER"),
    10: ("GPIO15_RXD", "I/O 3.3V"),
    11: ("GPIO17", "I/O 3.3V"),
    12: ("GPIO18_PWM0", "I/O 3.3V"),
    13: ("GPIO27", "I/O 3.3V"),
    14: ("GND", "POWER"),
    15: ("GPIO22", "I/O 3.3V"),
    16: ("GPIO23", "I/O 3.3V"),
    17: ("+3V3", "POWER"),
    18: ("GPIO24", "I/O 3.3V"),
    19: ("GPIO10_MOSI", "I/O 3.3V"),
    20: ("GND", "POWER"),
    21: ("GPIO9_MISO", "I/O 3.3V"),
    22: ("GPIO25", "I/O 3.3V"),
    23: ("GPIO11_SCLK", "I/O 3.3V"),
    24: ("GPIO8_CE0", "I/O 3.3V"),
    25: ("GND", "POWER"),
    26: ("GPIO7_CE1", "I/O 3.3V"),
    27: ("ID_SD", "I2C ID"),
    28: ("ID_SC", "I2C ID"),
    29: ("GPIO5", "I/O 3.3V"),
    30: ("GND", "POWER"),
    31: ("GPIO6", "I/O 3.3V"),
    32: ("GPIO12_PWM0", "I/O 3.3V"),
    33: ("GPIO13_PWM1", "I/O 3.3V"),
    34: ("GND", "POWER"),
    35: ("GPIO19_PWM1", "I/O 3.3V"),
    36: ("GPIO16", "I/O 3.3V"),
    37: ("GPIO26", "I/O 3.3V"),
    38: ("GPIO20", "I/O 3.3V"),
    39: ("GND", "POWER"),
    40: ("GPIO21", "I/O 3.3V")
}

# Current Carrier Board Net Assignment:
current_nets = {
    1: "unconnected",
    2: "/+5V_PWR",
    3: "/PWMA_L",
    4: "/+5V_PWR",
    5: "/AIN2_L",
    6: "GND",
    7: "/AIN1_L",
    8: "unconnected",
    9: "unconnected",
    10: "unconnected",
    11: "/STBY_L",
    12: "unconnected",
    13: "/TRIG_L",
    14: "unconnected",
    15: "/ECHO_L",
    16: "unconnected",
    17: "/+3V3_LOGIC",
    18: "unconnected",
    19: "/LINE_L",
    20: "unconnected",
    21: "/LINE_C",
    22: "unconnected",
    23: "/LINE_R",
    24: "unconnected",
    25: "GND",
    26: "unconnected",
    27: "/I2C_SDA",
    28: "/I2C_SCL",
    29: "/TRIG_R",
    30: "unconnected",
    31: "/ECHO_R",
    32: "unconnected",
    33: "/PWMA_R",
    34: "unconnected",
    35: "/AIN2_R",
    36: "unconnected",
    37: "/AIN1_R",
    38: "/STBY_R",
    39: "unconnected",
    40: "unconnected"
}

print("=== ANALYSIS OF INTERPRETATION 2 (IF NETS WERE SWAPPED ON PHYSICAL PI PINS) ===")
for p in range(1, 41):
    p_swap = (40 - p) if (p % 2 == 1) else (42 - p)
    net_received = current_nets[p_swap]
    pi_name, pi_type = pi_pins[p]
    # Check for lethal conflicts:
    conflict = ""
    if net_received == "/+5V_PWR" and pi_type != "POWER" and "5V" not in pi_name:
        conflict = "CRITICAL ERROR: 5V CONNECTED TO " + pi_name + " (DESTROYS PI!)"
    elif net_received == "GND" and "5V" in pi_name:
        conflict = "CRITICAL ERROR: SHORT CIRCUIT GND TO 5V!"
    elif net_received == "/+3V3_LOGIC" and "GND" in pi_name:
        conflict = "CRITICAL ERROR: SHORT CIRCUIT 3.3V TO GND!"
    print(f"Pi Pin {p:2d} ({pi_name:13s}): gets net '{net_received}' (from old pin {p_swap:2d}) {conflict}")

