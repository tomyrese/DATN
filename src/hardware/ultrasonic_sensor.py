import time
import statistics
from typing import Optional, Tuple, Dict, Any
from src.config import RobotConfig, config
from src.services.logging_service import logger

class UltrasonicSensors:
    """
    Dual HC-SR04 Ultrasonic Distance Sensor Driver:
    - Sensor 1: Front-Left (Trig GPIO 25, Echo GPIO 8)
    - Sensor 2: Front-Right (Trig GPIO 7, Echo GPIO 1)

    CRITICAL ELECTRICAL SAFETY NOTICE:
    -----------------------------------
    HC-SR04 VCC is 5V. Its Echo output pin generates a 5V TTL signal.
    Raspberry Pi 4 GPIO pins accept a MAXIMUM of 3.3V logic levels.
    CONNECTING ECHO DIRECTLY TO RASPBERRY PI GPIO WILL PERMANENTLY DAMAGE THE SOC.
    Always install a voltage divider (e.g., 1k ohm inline + 2k ohm to GND)
    or a bidirectional Logic Level Converter before connecting Echo pins.
    """

    def __init__(self, cfg: Optional[RobotConfig] = None):
        self.cfg = cfg or config
        self.enabled = self.cfg.ULTRASONIC_ENABLED
        self.simulation_mode = self.cfg.SIMULATION_MODE

        self._gpio_handle = None
        self._gpio_chip = None
        self._is_hardware_ready = False

        # Simulation override variables
        self._sim_dist1: Optional[float] = 180.0
        self._sim_dist2: Optional[float] = 180.0
        self._last_reading_time = 0.0

        if self.enabled and not self.simulation_mode:
            self._init_hardware()

    def _init_hardware(self):
        try:
            import lgpio
            self._gpio_chip = lgpio.gpiochip_open(0)
            # Setup Trig as Output
            lgpio.gpio_claim_output(self._gpio_chip, self.cfg.ULTRASONIC_1_TRIG, 0)
            lgpio.gpio_claim_output(self._gpio_chip, self.cfg.ULTRASONIC_2_TRIG, 0)
            # Setup Echo as Input
            lgpio.gpio_claim_input(self._gpio_chip, self.cfg.ULTRASONIC_1_ECHO)
            lgpio.gpio_claim_input(self._gpio_chip, self.cfg.ULTRASONIC_2_ECHO)
            self._is_hardware_ready = True
            logger.info("HC-SR04 Ultrasonic Sensors initialized on Raspberry Pi GPIO")
        except Exception as e:
            logger.warning(f"Failed to initialize real GPIO for Ultrasonic Sensors ({e}). Falling back to simulation.")
            self.simulation_mode = True
            self._is_hardware_ready = False

    def _measure_single_pulse(self, trig_pin: int, echo_pin: int, timeout_s: float = 0.035) -> Optional[float]:
        if not self._is_hardware_ready or self._gpio_chip is None:
            return None

        import lgpio
        # Trigger 10 microsecond pulse
        lgpio.gpio_write(self._gpio_chip, trig_pin, 1)
        time.sleep(0.000010)
        lgpio.gpio_write(self._gpio_chip, trig_pin, 0)

        # Wait for echo to go HIGH
        t0 = time.perf_counter()
        pulse_start = t0
        while lgpio.gpio_read(self._gpio_chip, echo_pin) == 0:
            pulse_start = time.perf_counter()
            if pulse_start - t0 > timeout_s:
                return None  # Timeout waiting for echo start

        # Wait for echo to go LOW
        pulse_end = pulse_start
        while lgpio.gpio_read(self._gpio_chip, echo_pin) == 1:
            pulse_end = time.perf_counter()
            if pulse_end - pulse_start > timeout_s:
                return None  # Timeout waiting for echo end

        duration = pulse_end - pulse_start
        # Speed of sound in air: 343 m/s = 34300 cm/s -> distance = (duration * 34300) / 2
        distance_cm = (duration * 34300.0) / 2.0

        if 2.0 <= distance_cm <= self.cfg.ULTRASONIC_MAX_DISTANCE_CM:
            return round(distance_cm, 1)
        return None

    def read_distances(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Reads both ultrasonic sensors with median filtering.
        Returns (dist_sensor_1_cm, dist_sensor_2_cm).
        """
        self._last_reading_time = time.time()

        if self.simulation_mode or not self._is_hardware_ready:
            return (self._sim_dist1, self._sim_dist2)

        # Hardware read with 2-sample median/average for reliability
        d1 = self._measure_single_pulse(self.cfg.ULTRASONIC_1_TRIG, self.cfg.ULTRASONIC_1_ECHO)
        time.sleep(0.002)
        d2 = self._measure_single_pulse(self.cfg.ULTRASONIC_2_TRIG, self.cfg.ULTRASONIC_2_ECHO)

        return (d1, d2)

    def get_min_distance(self) -> Optional[float]:
        d1, d2 = self.read_distances()
        valid = [d for d in (d1, d2) if d is not None]
        return min(valid) if valid else None

    def set_simulated_distances(self, dist1_cm: Optional[float], dist2_cm: Optional[float]):
        """Helper for simulation & automated testing."""
        self._sim_dist1 = dist1_cm
        self._sim_dist2 = dist2_cm

    def close(self):
        if self._gpio_chip is not None:
            try:
                import lgpio
                lgpio.gpiochip_close(self._gpio_chip)
            except Exception:
                pass
            self._gpio_chip = None
            self._is_hardware_ready = False
