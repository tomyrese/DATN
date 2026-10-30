"""
Lớp điều khiển 2 Động cơ bên trái qua Driver TB6612 (U_TB1)
Tự động nhận diện môi trường Raspberry Pi hoặc chế độ Giả lập (Simulation trên PC).
"""

import time
import sys

# Đảm bảo in ký tự tiếng Việt an toàn trên cả Windows terminal và Linux/Raspberry Pi
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config import LEFT_MOTORS_CONFIG, PWM_FREQUENCY_HZ, DEFAULT_SPEED

# Kiểm tra thư viện điều khiển GPIO trên Raspberry Pi
HAVE_RPI_GPIO = False
try:
    import RPi.GPIO as GPIO
    HAVE_RPI_GPIO = True
except (ImportError, RuntimeError):
    HAVE_RPI_GPIO = False


class TB6612LeftMotors:
    """
    Điều khiển 2 động cơ bên trái (Front-Left & Rear-Left)
    kết nối chung qua kênh A và B của Driver TB6612 (U_TB1).
    """

    def __init__(self, pwm_pin=None, in1_pin=None, in2_pin=None, stby_pin=None, freq=PWM_FREQUENCY_HZ):
        self.pwm_pin = pwm_pin or LEFT_MOTORS_CONFIG["PWM_PIN"]
        self.in1_pin = in1_pin or LEFT_MOTORS_CONFIG["IN1_PIN"]
        self.in2_pin = in2_pin or LEFT_MOTORS_CONFIG["IN2_PIN"]
        self.stby_pin = stby_pin or LEFT_MOTORS_CONFIG["STBY_PIN"]
        self.freq = freq
        
        self.current_speed = 0
        self.current_direction = "STOP"
        self.is_enabled = False
        self.pwm = None
        self.is_simulated = not HAVE_RPI_GPIO

        self._setup_hardware()

    def _setup_hardware(self):
        """Khởi tạo chân GPIO hoặc kích hoạt chế độ Giả lập"""
        if not self.is_simulated:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)

                # Cấu hình các chân điều khiển làm OUTPUT
                GPIO.setup(self.in1_pin, GPIO.OUT, initial=GPIO.LOW)
                GPIO.setup(self.in2_pin, GPIO.OUT, initial=GPIO.LOW)
                GPIO.setup(self.stby_pin, GPIO.OUT, initial=GPIO.LOW)
                GPIO.setup(self.pwm_pin, GPIO.OUT, initial=GPIO.LOW)

                # Khởi tạo đối tượng PWM
                self.pwm = GPIO.PWM(self.pwm_pin, self.freq)
                self.pwm.start(0)
                print("[HARDWARE] Đã kết nối thành công GPIO Raspberry Pi 4!")
                print(f"           STBY=BCM{self.stby_pin}, PWM=BCM{self.pwm_pin}, IN1=BCM{self.in1_pin}, IN2=BCM{self.in2_pin}")
            except Exception as e:
                print(f"[CẢNH BÁO] Không thể khởi tạo RPi.GPIO: {e}. Chuyển sang chế độ GIẢ LẬP.")
                self.is_simulated = True

        if self.is_simulated:
            print("[SIMULATION] Đang chạy ở chế độ GIẢ LẬP (PC). Không có phần cứng Pi 4.")
            print(f"             Mô phỏng chân: STBY=BCM{self.stby_pin}, PWM=BCM{self.pwm_pin}, IN1=BCM{self.in1_pin}, IN2=BCM{self.in2_pin}")

    def enable(self):
        """Bật Driver (Kéo STBY lên HIGH)"""
        self.is_enabled = True
        if not self.is_simulated:
            GPIO.output(self.stby_pin, GPIO.HIGH)
        print(f"[TB6612] ENABLED (STBY = HIGH)")

    def disable(self):
        """Tắt Driver (Kéo STBY về LOW) để tiết kiệm điện và ngắt công suất"""
        self.stop()
        self.is_enabled = False
        if not self.is_simulated:
            GPIO.output(self.stby_pin, GPIO.LOW)
        print(f"[TB6612] DISABLED (STBY = LOW)")

    def _set_pwm(self, duty):
        """Thiết lập độ rộng xung PWM (0 - 100%)"""
        duty = max(0, min(100, duty))
        self.current_speed = duty
        if not self.is_simulated and self.pwm:
            self.pwm.ChangeDutyCycle(duty)

    def forward(self, speed=DEFAULT_SPEED):
        """
        Quay TIẾN 2 bánh bên trái (M1 & M2 cùng tiến)
        Bảng trạng thái: STBY=1, IN1=1, IN2=0, PWM=speed
        """
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

        print(f"[BÁNH TRÁI] >> TIẾN (FORWARD) | Tốc độ: {speed:3d}% | IN1=HIGH, IN2=LOW")

    def reverse(self, speed=DEFAULT_SPEED):
        """
        Quay LÙI 2 bánh bên trái (M1 & M2 cùng lùi)
        Bảng trạng thái: STBY=1, IN1=0, IN2=1, PWM=speed
        """
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

        print(f"[BÁNH TRÁI] << LÙI  (REVERSE) | Tốc độ: {speed:3d}% | IN1=LOW, IN2=HIGH")

    def brake(self):
        """
        HÃM DỪNG NHANH (Short Brake)
        Bảng trạng thái: STBY=1, IN1=1, IN2=1, PWM=100
        Ngắn mạch 2 cực động cơ để sinh lực hãm quán tính.
        """
        self.current_direction = "BRAKE"
        if not self.is_simulated:
            GPIO.output(self.in1_pin, GPIO.HIGH)
            GPIO.output(self.in2_pin, GPIO.HIGH)
            self._set_pwm(100)
        else:
            self._set_pwm(100)

        print(f"[BÁNH TRÁI] == HÃM CỨNG (BRAKE) | IN1=HIGH, IN2=HIGH")

    def stop(self):
        """
        DỪNG TỰ NHIÊN / THẢ TRÔI (Coast / Stop)
        Bảng trạng thái: IN1=0, IN2=0, PWM=0
        """
        self.current_direction = "STOP"
        self._set_pwm(0)
        if not self.is_simulated:
            GPIO.output(self.in1_pin, GPIO.LOW)
            GPIO.output(self.in2_pin, GPIO.LOW)

        print(f"[BÁNH TRÁI] -- DỪNG TRÔI (COAST) | IN1=LOW, IN2=LOW, PWM=0%")

    def cleanup(self):
        """Giải phóng tài nguyên chân GPIO an toàn khi thoát"""
        self.stop()
        self.disable()
        if not self.is_simulated:
            try:
                if self.pwm:
                    self.pwm.stop()
                GPIO.cleanup([self.pwm_pin, self.in1_pin, self.in2_pin, self.stby_pin])
            except Exception:
                GPIO.cleanup()
        print("[TB6612] Đã giải phóng toàn bộ chân GPIO an toàn.")
