pi4_pins = {
    1: ("3.3V", "PWR"),
    2: ("5V", "PWR"),
    3: ("GPIO2", "I2C_SDA"),
    4: ("5V", "PWR"),
    5: ("GPIO3", "I2C_SCL"),
    6: ("GND", "GND"),
    7: ("GPIO4", "GPIO"),
    8: ("GPIO14", "UART_TX"),
    9: ("GND", "GND"),
    10: ("GPIO15", "UART_RX"),
    11: ("GPIO17", "GPIO"),
    12: ("GPIO18", "PWM0"),
    13: ("GPIO27", "GPIO"),
    14: ("GND", "GND"),
    15: ("GPIO22", "GPIO"),
    16: ("GPIO23", "GPIO"),
    17: ("3.3V", "PWR"),
    18: ("GPIO24", "GPIO"),
    19: ("GPIO10", "SPI_MOSI"),
    20: ("GND", "GND"),
    21: ("GPIO9", "SPI_MISO"),
    22: ("GPIO25", "GPIO"),
    23: ("GPIO11", "SPI_SCLK"),
    24: ("GPIO8", "SPI_CE0"),
    25: ("GND", "GND"),
    26: ("GPIO7", "SPI_CE1"),
    27: ("GPIO0", "ID_SD"),
    28: ("GPIO1", "ID_SC"),
    29: ("GPIO5", "GPIO"),
    30: ("GND", "GND"),
    31: ("GPIO6", "GPIO"),
    32: ("GPIO12", "PWM0"),
    33: ("GPIO13", "PWM1"),
    34: ("GND", "GND"),
    35: ("GPIO19", "PWM1"),
    36: ("GPIO16", "GPIO"),
    37: ("GPIO26", "GPIO"),
    38: ("GPIO20", "GPIO"),
    39: ("GND", "GND"),
    40: ("GPIO21", "GPIO")
}

print("=== ODD PINS (Row 1 - North) ===")
for p in range(1, 41, 2):
    print(f"Pin {p:2}: {pi4_pins[p][0]:8} ({pi4_pins[p][1]})")

print("\n=== EVEN PINS (Row 2 - South) ===")
for p in range(2, 42, 2):
    print(f"Pin {p:2}: {pi4_pins[p][0]:8} ({pi4_pins[p][1]})")

