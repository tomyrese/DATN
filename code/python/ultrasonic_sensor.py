"""
Mô-đun điều khiển 2 Cảm biến Siêu âm HC-SR04 (Trái & Phải)
Bo mạch Robot Carrier 1 Lớp - Raspberry Pi 4
Tác giả: Nhóm Đồ Án Tốt Nghiệp Robot Tự Hành

Đặc tính kỹ thuật:
  - Cảm biến Trái (U_US1): TRIG = BCM 27 (Pin 13), ECHO = BCM 22 (Pin 15)
  - Cảm biến Phải (U_US2): TRIG = BCM 5  (Pin 29), ECHO = BCM 6  (Pin 31)
  - Bảo vệ GPIO: Tín hiệu Echo 5V qua cầu phân áp 1kΩ / 2kΩ đưa về 3.3V an toàn.
  - Chống nhiễu chéo âm học (Cross-talk): Đo xen kẽ tuần tự giữa 2 cảm biến với độ trễ nghỉ.
"""

import time
import sys
from config import ULTRASONIC_CONFIG

# Tốc độ âm thanh trong không khí ở 20°C: ~343 m/s = 34300 cm/s
# Khoảng cách = (Thời gian xung Echo * 34300) / 2 = Thời gian xung * 17150 cm/s
SOUND_SPEED_HALF = 17150.0

# Ngưỡng khoảng cách đo của cảm biến HC-SR04 (cm)
MIN_VALID_DISTANCE_CM = 2.0    # Khoảng cách tối thiểu tin cậy
MAX_VALID_DISTANCE_CM = 400.0  # Khoảng cách tối đa (4 mét)
TIMEOUT_SECONDS = 0.035        # Thời gian chờ tối đa cho 1 xung echo (~4m x 2 / 34300 + margin)

# Thử nghiệm import thư viện GPIO của Raspberry Pi
try:
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except (ImportError, RuntimeError):
    HARDWARE_AVAILABLE = False


class DualUltrasonicSensor:
    """
    Lớp quản trị và thu thập dữ liệu từ 2 cảm biến siêu âm HC-SR04 Trái và Phải.
    Hỗ trợ chế độ mô phỏng tự động khi chạy thử nghiệm trên máy tính/PC.
    """

    def __init__(self, use_hardware=True):
        self.is_hardware = HARDWARE_AVAILABLE and use_hardware
        self.left_trig = ULTRASONIC_CONFIG["LEFT"]["TRIG_PIN"]
        self.left_echo = ULTRASONIC_CONFIG["LEFT"]["ECHO_PIN"]
        self.right_trig = ULTRASONIC_CONFIG["RIGHT"]["TRIG_PIN"]
        self.right_echo = ULTRASONIC_CONFIG["RIGHT"]["ECHO_PIN"]

        if self.is_hardware:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

            # Cài đặt chân Cảm biến Trái
            GPIO.setup(self.left_trig, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.left_echo, GPIO.IN)

            # Cài đặt chân Cảm biến Phải
            GPIO.setup(self.right_trig, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.right_echo, GPIO.IN)

            # Cho phép cảm biến ổn định điện áp sau khi khởi động
            time.sleep(0.05)
        else:
            # Tham số giả lập khi chạy trên máy tính
            self._sim_left = 55.0
            self._sim_right = 62.0
            self._sim_trend = -1.5

    def _read_single_sensor(self, trig_pin, echo_pin):
        """
        Đo cự ly của 1 cảm biến HC-SR04 cụ thể.
        Trả về khoảng cách (cm) hoặc None nếu quá tầm đo (timeout).
        """
        if not self.is_hardware:
            return self._simulate_reading(trig_pin)

        # 1. Đảm bảo chân Trigger ở mức LOW trước khi phát
        GPIO.output(trig_pin, GPIO.LOW)
        time.sleep(0.000002)  # 2 micro-giây

        # 2. Phát xung kích hoạt HIGH 10 micro-giây
        GPIO.output(trig_pin, GPIO.HIGH)
        time.sleep(0.000010)  # 10 micro-giây
        GPIO.output(trig_pin, GPIO.LOW)

        # 3. Chờ chân Echo lên mức HIGH (Bắt đầu phát sóng)
        t_start = time.perf_counter()
        t_limit = t_start + TIMEOUT_SECONDS
        pulse_start = t_start

        while GPIO.input(echo_pin) == GPIO.LOW:
            pulse_start = time.perf_counter()
            if pulse_start > t_limit:
                return None  # Không nhận được phản hồi kích hoạt

        # 4. Chờ chân Echo xuống mức LOW (Đã nhận sóng dội lại)
        pulse_end = pulse_start
        t_limit = pulse_start + TIMEOUT_SECONDS

        while GPIO.input(echo_pin) == GPIO.HIGH:
            pulse_end = time.perf_counter()
            if pulse_end > t_limit:
                return None  # Vật cản ở quá xa ngoài 4 mét

        # 5. Tính toán khoảng cách
        pulse_duration = pulse_end - pulse_start
        distance_cm = pulse_duration * SOUND_SPEED_HALF

        # Lọc giới hạn vật lý của cảm biến HC-SR04
        if MIN_VALID_DISTANCE_CM <= distance_cm <= MAX_VALID_DISTANCE_CM:
            return round(distance_cm, 1)
        return None

    def read_left_cm(self):
        """Đo khoảng cách cảm biến TRÁI (U_US1)"""
        return self._read_single_sensor(self.left_trig, self.left_echo)

    def read_right_cm(self):
        """Đo khoảng cách cảm biến PHẢI (U_US2)"""
        return self._read_single_sensor(self.right_trig, self.right_echo)

    def read_both_cm(self, inter_sensor_delay=0.03):
        """
        Đo tuần tự cả 2 cảm biến Trái và Phải.
        Quan trọng: inter_sensor_delay = 30ms giúp tiêu tán hoàn toàn
        sóng siêu âm dội lại trong phòng, tránh nhiễu chéo giữa 2 cảm biến.
        Trả về: (dist_left, dist_right)
        """
        # Đo cảm biến Trái
        dist_left = self.read_left_cm()

        # Nghỉ để sóng 40kHz cảm biến trái triệt tiêu
        time.sleep(inter_sensor_delay)

        # Đo cảm biến Phải
        dist_right = self.read_right_cm()

        return dist_left, dist_right

    def read_filtered_both_cm(self, samples=3, sample_delay=0.02):
        """
        Lấy trung vị (Median Filter) từ 3 lần đọc liên tiếp.
        Loại bỏ hoàn toàn các điểm đột biến (outliers) do sóng nhiễu môi trường.
        """
        left_samples = []
        right_samples = []

        for _ in range(samples):
            l, r = self.read_both_cm(inter_sensor_delay=sample_delay)
            if l is not None:
                left_samples.append(l)
            if r is not None:
                right_samples.append(r)
            time.sleep(sample_delay)

        # Tính giá trị trung vị
        med_l = sorted(left_samples)[len(left_samples) // 2] if left_samples else None
        med_r = sorted(right_samples)[len(right_samples) // 2] if right_samples else None

        return med_l, med_r

    def _simulate_reading(self, trig_pin):
        """Giả lập biến thiên cự ly thực tế khi không có phần cứng Pi"""
        import random
        if trig_pin == self.left_trig:
            self._sim_left += random.uniform(-2.0, 2.0)
            if self._sim_left < 10: self._sim_left = 60
            if self._sim_left > 150: self._sim_left = 30
            return round(self._sim_left, 1)
        else:
            self._sim_right += random.uniform(-2.5, 2.5)
            if self._sim_right < 10: self._sim_right = 70
            if self._sim_right > 150: self._sim_right = 35
            return round(self._sim_right, 1)

    def cleanup(self):
        """Giải phóng chân GPIO an toàn khi kết thúc chương trình"""
        if self.is_hardware:
            try:
                GPIO.cleanup([self.left_trig, self.left_echo, self.right_trig, self.right_echo])
            except Exception:
                pass

