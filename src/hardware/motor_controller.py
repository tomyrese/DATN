import threading
from typing import Optional, Dict
from src.config import RobotConfig, config
from src.services.logging_service import logger

class MotorController:
    def __init__(self, cfg: Optional[RobotConfig] = None):
        self.cfg = cfg or config
        self.enabled = False
        self.is_simulation = self.cfg.SIMULATION_MODE or not self.cfg.MOTOR_ENABLED
        self.gpio_available = False
        self.gpio = None
        self.pwm_objects: Dict[str, any] = {}
        self.motor_speeds = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
        self.lock = threading.Lock()

        if not self.is_simulation:
            try:
                import RPi.GPIO as GPIO
                self.gpio = GPIO
                self.gpio.setmode(self.gpio.BCM)
                self.gpio.setwarnings(False)
                self._setup_pins()
                self.gpio_available = True
                logger.info("MotorController initialized with hardware GPIO")
            except Exception as e:
                logger.warning(f"Failed to initialize RPi.GPIO: {e}. Falling back to simulation mode.")
                self.is_simulation = True
        else:
            logger.info("MotorController initialized in simulation mode")

        self.disable()

    def _setup_pins(self):
        output_pins = [
            self.cfg.STBY_L, self.cfg.AIN1_L, self.cfg.AIN2_L, self.cfg.PWMA_L,
            self.cfg.BIN1_L, self.cfg.BIN2_L, self.cfg.PWMB_L,
            self.cfg.STBY_R, self.cfg.PWMA_R, self.cfg.AIN1_R, self.cfg.AIN2_R,
            self.cfg.PWMB_R, self.cfg.BIN1_R, self.cfg.BIN2_R
        ]
        for pin in output_pins:
            self.gpio.setup(pin, self.gpio.OUT)
            self.gpio.output(pin, self.gpio.LOW)

        self.pwm_objects["PWMA_L"] = self.gpio.PWM(self.cfg.PWMA_L, self.cfg.PWM_FREQ)
        self.pwm_objects["PWMB_L"] = self.gpio.PWM(self.cfg.PWMB_L, self.cfg.PWM_FREQ)
        self.pwm_objects["PWMA_R"] = self.gpio.PWM(self.cfg.PWMA_R, self.cfg.PWM_FREQ)
        self.pwm_objects["PWMB_R"] = self.gpio.PWM(self.cfg.PWMB_R, self.cfg.PWM_FREQ)

        for pwm in self.pwm_objects.values():
            pwm.start(0)

    def enable(self):
        with self.lock:
            self.enabled = True
            if self.gpio_available:
                self.gpio.output(self.cfg.STBY_L, self.gpio.HIGH)
                self.gpio.output(self.cfg.STBY_R, self.gpio.HIGH)
            logger.info("MotorController enabled (STBY HIGH)")

    def disable(self):
        with self.lock:
            for i in range(1, 5):
                self.motor_speeds[i] = 0.0
            self.enabled = False
            if self.gpio_available:
                self.gpio.output(self.cfg.STBY_L, self.gpio.LOW)
                self.gpio.output(self.cfg.STBY_R, self.gpio.LOW)
            logger.info("MotorController disabled (STBY LOW)")

    def _set_channel(self, in1_pin: int, in2_pin: int, pwm_name: str, speed: float):
        clamped_speed = max(-1.0, min(1.0, speed))
        duty_cycle = abs(clamped_speed) * 100.0

        if clamped_speed > 0:
            in1_val, in2_val = 1, 0
        elif clamped_speed < 0:
            in1_val, in2_val = 0, 1
        else:
            in1_val, in2_val = 0, 0
            duty_cycle = 0.0

        if self.gpio_available and self.enabled:
            self.gpio.output(in1_pin, self.gpio.HIGH if in1_val else self.gpio.LOW)
            self.gpio.output(in2_pin, self.gpio.HIGH if in2_val else self.gpio.LOW)
            self.pwm_objects[pwm_name].ChangeDutyCycle(duty_cycle)

    def drive_motor(self, motor_index: int, speed: float):
        with self.lock:
            clamped_speed = max(-1.0, min(1.0, speed))
            self.motor_speeds[motor_index] = clamped_speed

            if motor_index == 1:
                self._set_channel(self.cfg.AIN1_L, self.cfg.AIN2_L, "PWMA_L", clamped_speed)
            elif motor_index == 2:
                self._set_channel(self.cfg.BIN1_L, self.cfg.BIN2_L, "PWMB_L", clamped_speed)
            elif motor_index == 3:
                self._set_channel(self.cfg.AIN1_R, self.cfg.AIN2_R, "PWMA_R", clamped_speed)
            elif motor_index == 4:
                self._set_channel(self.cfg.BIN1_R, self.cfg.BIN2_R, "PWMB_R", clamped_speed)
            else:
                raise ValueError(f"Invalid motor index: {motor_index}. Must be 1, 2, 3, or 4.")

    def set_left(self, speed: float):
        self.drive_motor(1, speed)
        self.drive_motor(2, speed)

    def set_right(self, speed: float):
        self.drive_motor(3, speed)
        self.drive_motor(4, speed)

    def drive(self, left_speed: float, right_speed: float):
        self.set_left(left_speed)
        self.set_right(right_speed)

    def forward(self, speed: Optional[float] = None):
        target_speed = self.cfg.DEFAULT_SPEED if speed is None else speed
        self.drive(target_speed, target_speed)

    def backward(self, speed: Optional[float] = None):
        target_speed = self.cfg.DEFAULT_SPEED if speed is None else speed
        self.drive(-target_speed, -target_speed)

    def turn_left(self, speed: Optional[float] = None):
        target_speed = self.cfg.DEFAULT_SPEED if speed is None else speed
        self.drive(-target_speed, target_speed)

    def turn_right(self, speed: Optional[float] = None):
        target_speed = self.cfg.DEFAULT_SPEED if speed is None else speed
        self.drive(target_speed, -target_speed)

    def stop(self):
        with self.lock:
            for i in range(1, 5):
                self.motor_speeds[i] = 0.0
            if self.gpio_available and self.enabled:
                self._set_channel(self.cfg.AIN1_L, self.cfg.AIN2_L, "PWMA_L", 0.0)
                self._set_channel(self.cfg.BIN1_L, self.cfg.BIN2_L, "PWMB_L", 0.0)
                self._set_channel(self.cfg.AIN1_R, self.cfg.AIN2_R, "PWMA_R", 0.0)
                self._set_channel(self.cfg.BIN1_R, self.cfg.BIN2_R, "PWMB_R", 0.0)

    def emergency_stop(self):
        self.disable()
        logger.warning("MotorController emergency stop triggered")

    def is_moving(self) -> bool:
        with self.lock:
            return any(abs(spd) > 1e-4 for spd in self.motor_speeds.values())

    def get_speeds(self) -> Dict[int, float]:
        with self.lock:
            return self.motor_speeds.copy()

    def get_wheel_speeds(self) -> tuple:
        with self.lock:
            left = (self.motor_speeds[1] + self.motor_speeds[2]) / 2.0
            right = (self.motor_speeds[3] + self.motor_speeds[4]) / 2.0
            return (left, right)

    def cleanup(self):
        self.emergency_stop()
        if self.gpio_available:
            try:
                for pwm in self.pwm_objects.values():
                    pwm.stop()
                self.gpio.cleanup()
            except Exception as e:
                logger.error(f"Error during GPIO cleanup: {e}")
        logger.info("MotorController cleanup complete")
