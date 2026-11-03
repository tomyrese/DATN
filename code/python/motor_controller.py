"""
Mô-đun điều khiển Động cơ 4WD Robot Carrier qua 2 Driver TB6612 (U_TB1 & U_TB2)
Bo mạch Robot Carrier 1 Lớp - Raspberry Pi 4
Tác giả: Nhóm Đồ Án Tốt Nghiệp Robot Tự Hành

Đặc tính phần cứng:
  - Driver Trái (U_TB1): Điều khiển 2 bánh trái (M1 Trước-Trái & M2 Sau-Trái)
    * PWMA_L = BCM 2 (Pin 3), AIN1_L = BCM 4 (Pin 7), AIN2_L = BCM 3 (Pin 5), STBY_L = BCM 17 (Pin 11)
  - Driver Phải (U_TB2): Điều khiển 2 bánh phải (M3 Trước-Phải & M4 Sau-Phải)
    * PWMA_R = BCM 13 (Pin 33), AIN1_R = BCM 26 (Pin 37), AIN2_R = BCM 19 (Pin 35), STBY_R = BCM 20 (Pin 38)
"""

import time
import sys

# Đảm bảo in ký tự tiếng Việt an toàn trên cả Windows terminal và Linux/Raspberry Pi
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config import (
    LEFT_MOTORS_CONFIG,
    RIGHT_MOTORS_CONFIG,
    PWM_FREQUENCY_HZ,
    DEFAULT_SPEED
)

# Kiểm tra thư viện điều khiển GPIO trên Raspberry Pi
HAVE_RPI_GPIO = False
try:
    import RPi.GPIO as GPIO
    HAVE_RPI_GPIO = True
except (ImportError, RuntimeError):
    HAVE_RPI_GPIO = False


class TB6612Driver:
    """Lớp điều khiển cơ sở cho 1 cụm Driver TB6612FNG"""

    def __init__(self, name, pwm_pin, in1_pin, in2_pin, stby_pin, freq=PWM_FREQUENCY_HZ):
        self.name = name
        self.pwm_pin = pwm_pin
        self.in1_pin = in1_pin
        self.in2_pin = in2_pin
        self.stby_pin = stby_pin
        self.freq = freq

        self.current_speed = 0
        self.current_direction = "STOP"
        self.is_enabled = False
        self.pwm = None
        self.is_simulated = not HAVE_RPI_GPIO

        self._setup_hardware()

    def _setup_hardware(self):
        if not self.is_simulated:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)

                GPIO.setup(self.in1_pin, GPIO.OUT, initial=GPIO.LOW)
                GPIO.setup(self.in2_pin, GPIO.OUT, initial=GPIO.LOW)
                GPIO.setup(self.stby_pin, GPIO.OUT, initial=GPIO.LOW)
                GPIO.setup(self.pwm_pin, GPIO.OUT, initial=GPIO.LOW)

                self.pwm = GPIO.PWM(self.pwm_pin, self.freq)
                self.pwm.start(0)
            except Exception as e:
                self.is_simulated = True

    def enable(self):
        self.is_enabled = True
        if not self.is_simulated:
            GPIO.output(self.stby_pin, GPIO.HIGH)

    def disable(self):
        self.stop()
        self.is_enabled = False
        if not self.is_simulated:
            GPIO.output(self.stby_pin, GPIO.LOW)

    def _set_pwm(self, duty):
        duty = max(0, min(100, duty))
        self.current_speed = duty
        if not self.is_simulated and self.pwm:
            self.pwm.ChangeDutyCycle(duty)

    def forward(self, speed=DEFAULT_SPEED):
        if not self.is_enabled:
            self.enable()
        speed = max(0, min(100, speed))
        self.current_direction = "FORWARD"
        if not self.is_simulated:
            GPIO.output(self.in1_pin, GPIO.HIGH)
            GPIO.output(self.in2_pin, GPIO.LOW)
            self._set_pwm(speed)
        else:
            self._set_pwm(speed)

    def reverse(self, speed=DEFAULT_SPEED):
        if not self.is_enabled:
            self.enable()
        speed = max(0, min(100, speed))
        self.current_direction = "REVERSE"
        if not self.is_simulated:
            GPIO.output(self.in1_pin, GPIO.LOW)
            GPIO.output(self.in2_pin, GPIO.HIGH)
            self._set_pwm(speed)
        else:
            self._set_pwm(speed)

    def brake(self):
        self.current_direction = "BRAKE"
        if not self.is_simulated:
            GPIO.output(self.in1_pin, GPIO.HIGH)
            GPIO.output(self.in2_pin, GPIO.HIGH)
            self._set_pwm(100)
        else:
            self._set_pwm(100)

    def stop(self):
        self.current_direction = "STOP"
        self._set_pwm(0)
        if not self.is_simulated:
            GPIO.output(self.in1_pin, GPIO.LOW)
            GPIO.output(self.in2_pin, GPIO.LOW)

    def cleanup(self):
        self.stop()
        self.disable()
        if not self.is_simulated:
            try:
                if self.pwm:
                    self.pwm.stop()
                GPIO.cleanup([self.pwm_pin, self.in1_pin, self.in2_pin, self.stby_pin])
            except Exception:
                pass


class TB6612LeftMotors(TB6612Driver):
    """Điều khiển 2 động cơ bên trái (Front-Left & Rear-Left - Driver U_TB1)"""
    def __init__(self, pwm_pin=None, in1_pin=None, in2_pin=None, stby_pin=None, freq=PWM_FREQUENCY_HZ):
        super().__init__(
            name="BÁNH TRÁI",
            pwm_pin=pwm_pin or LEFT_MOTORS_CONFIG["PWM_PIN"],
            in1_pin=in1_pin or LEFT_MOTORS_CONFIG["IN1_PIN"],
            in2_pin=in2_pin or LEFT_MOTORS_CONFIG["IN2_PIN"],
            stby_pin=stby_pin or LEFT_MOTORS_CONFIG["STBY_PIN"],
            freq=freq
        )


class TB6612RightMotors(TB6612Driver):
    """Điều khiển 2 động cơ bên phải (Front-Right & Rear-Right - Driver U_TB2)"""
    def __init__(self, pwm_pin=None, in1_pin=None, in2_pin=None, stby_pin=None, freq=PWM_FREQUENCY_HZ):
        super().__init__(
            name="BÁNH PHẢI",
            pwm_pin=pwm_pin or RIGHT_MOTORS_CONFIG["PWM_PIN"],
            in1_pin=in1_pin or RIGHT_MOTORS_CONFIG["IN1_PIN"],
            in2_pin=in2_pin or RIGHT_MOTORS_CONFIG["IN2_PIN"],
            stby_pin=stby_pin or RIGHT_MOTORS_CONFIG["STBY_PIN"],
            freq=freq
        )


class Robot4WD:
    """
    Lớp điều phối vận hành toàn bộ 4 Bánh xe (Hệ thống truyền động 4WD).
    Đồng bộ cả 2 Driver TB6612 Trái và Phải.
    """

    def __init__(self, freq=PWM_FREQUENCY_HZ):
        self.left = TB6612LeftMotors(freq=freq)
        self.right = TB6612RightMotors(freq=freq)
        self.is_simulated = self.left.is_simulated or self.right.is_simulated
        self.current_state = "DỪNG"

    def enable(self):
        """Kích hoạt cả 2 Driver"""
        self.left.enable()
        self.right.enable()

    def disable(self):
        """Tắt cả 2 Driver"""
        self.left.disable()
        self.right.disable()

    def forward(self, speed=DEFAULT_SPEED):
        """TIẾN THẲNG: 4 bánh cùng quay tới"""
        self.current_state = f"TIẾN ({speed}%)"
        self.left.forward(speed)
        self.right.forward(speed)

    def reverse(self, speed=DEFAULT_SPEED):
        """LÙI THẲNG: 4 bánh cùng quay lùi"""
        self.current_state = f"LÙI ({speed}%)"
        self.left.reverse(speed)
        self.right.reverse(speed)

    def turn_left(self, speed=DEFAULT_SPEED, diff_ratio=0.3):
        """
        RẼ TRÁI MƯỢT (Cua vi sai):
        Bánh phải chạy tốc độ `speed`, bánh trái chạy chậm lại `speed * diff_ratio`.
        Xe đổi hướng êm ái, không bị khựng quán tính.
        """
        self.current_state = f"RẼ TRÁI ({speed}%)"
        left_spd = int(speed * diff_ratio)
        self.left.forward(left_spd)
        self.right.forward(speed)

    def turn_right(self, speed=DEFAULT_SPEED, diff_ratio=0.3):
        """
        RẼ PHẢI MƯỢT (Cua vi sai):
        Bánh trái chạy tốc độ `speed`, bánh phải chạy chậm lại `speed * diff_ratio`.
        """
        self.current_state = f"RẼ PHẢI ({speed}%)"
        right_spd = int(speed * diff_ratio)
        self.left.forward(speed)
        self.right.forward(right_spd)

    def spin_left(self, speed=DEFAULT_SPEED):
        """
        XOAY TRÒN TẠI CHỖ SANG TRÁI (Tank Turn / Pivot Turn):
        Bánh trái lùi, Bánh phải tiến. Quay 90° cực nhanh tại chỗ.
        """
        self.current_state = f"XOAY TRÁI ({speed}%)"
        self.left.reverse(speed)
        self.right.forward(speed)

    def spin_right(self, speed=DEFAULT_SPEED):
        """
        XOAY TRÒN TẠI CHỖ SANG PHẢI (Tank Turn / Pivot Turn):
        Bánh trái tiến, Bánh phải lùi.
        """
        self.current_state = f"XOAY PHẢI ({speed}%)"
        self.left.forward(speed)
        self.right.reverse(speed)

    def brake(self):
        """HÃM PHANH KHẨN CẤP cả 4 bánh"""
        self.current_state = "HÃM PHANH"
        self.left.brake()
        self.right.brake()

    def stop(self):
        """DỪNG TRÔI / NGẮT XUNG cả 4 bánh"""
        self.current_state = "DỪNG TRÔI"
        self.left.stop()
        self.right.stop()

    def cleanup(self):
        """Dọn dẹp và giải phóng GPIO"""
        self.left.cleanup()
        self.right.cleanup()
