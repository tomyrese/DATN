import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import config
from src.hardware.ultrasonic_sensor import UltrasonicSensors

def main():
    print("=== DUAL HC-SR04 ULTRASONIC SENSOR TEST ===")
    print("Wiring Verification on Raspberry Pi 4:")
    print("  Left Sensor : TRIG = GPIO 25, ECHO = GPIO 8  (Via 1k/2k ohm 3.3V divider)")
    print("  Right Sensor: TRIG = GPIO 7 , ECHO = GPIO 1  (Via 1k/2k ohm 3.3V divider)")
    print("Press Ctrl+C to stop.\n")

    sensors = UltrasonicSensors(config)

    try:
        while True:
            left_cm, right_cm = sensors.read_distances()
            state = sensors.get_obstacle_state()

            left_str = f"{left_cm:6.1f} cm" if left_cm is not None else "TIMEOUT "
            right_str = f"{right_cm:6.1f} cm" if right_cm is not None else "TIMEOUT "

            bar_left = "#" * int(min(left_cm or 0, 100) / 5)
            bar_right = "#" * int(min(right_cm or 0, 100) / 5)

            print(f"[HC-SR04] Left: {left_str} [{bar_left:<20}] | Right: {right_str} [{bar_right:<20}] | State: {state}")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nStopping sensor test.")
    finally:
        sensors.cleanup()

if __name__ == "__main__":
    main()
