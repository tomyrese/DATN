"""
Cấu hình chân GPIO Raspberry Pi 4 cho Bo mạch Robot Carrier (Chuẩn 1 Lớp - Single Layer PCB)
Đã đồng bộ 100% với sơ đồ nguyên lý Pi4_Robot_Carrier_1Layer.kicad_sch và PCB robot_electronics.kicad_pcb
Hỗ trợ đảo chân footprint TB6612 (PWMA..GND hàng 1, VM..GND hàng 2) và gương ngang socket Pi 4 (1<->39, 2<->40).
"""

# ==============================================================================
# BẢNG ÁNH XẠ CHÂN ĐIỀU KHIỂN DRIVER TB6612 BÊN TRÁI (U_TB1)
# Điều khiển đồng thời 2 bánh bên trái:
#   - Động cơ trước trái (J_M1 - Motor Front Left)
#   - Động cơ sau trái   (J_M2 - Motor Rear Left)
# ==============================================================================

# Chân BCM GPIO trên Raspberry Pi 4 (nằm ở phía Tây bo mạch)
LEFT_MOTORS_CONFIG = {
    # Chân băm xung PWM điều khiển tốc độ (Kênh A & B nối song song)
    # Header Pi 4 Pin 37 -> BCM GPIO 26
    "PWM_PIN": 26,
    
    # Chân định hướng 1 (AIN1 & BIN1 nối song song)
    # Header Pi 4 Pin 33 -> BCM GPIO 13
    "IN1_PIN": 13,
    
    # Chân định hướng 2 (AIN2 & BIN2 nối song song)
    # Header Pi 4 Pin 35 -> BCM GPIO 19
    "IN2_PIN": 19,
    
    # Chân kích hoạt Standby (STBY = HIGH để cho phép driver hoạt động)
    # Header Pi 4 Pin 38 -> BCM GPIO 20
    "STBY_PIN": 20,
}

# ==============================================================================
# BẢNG ÁNH XẠ CHÂN ĐIỀU KHIỂN DRIVER TB6612 BÊN PHẢI (U_TB2)
# Điều khiển đồng thời 2 bánh bên phải:
#   - Động cơ trước phải (J_M3 - Motor Front Right)
#   - Động cơ sau phải   (J_M4 - Motor Rear Right)
# ==============================================================================

# Chân BCM GPIO trên Raspberry Pi 4 (nằm ở phía Đông bo mạch)
RIGHT_MOTORS_CONFIG = {
    # Chân băm xung PWM điều khiển tốc độ (Kênh A & B nối song song)
    # Header Pi 4 Pin 3 -> BCM GPIO 2
    "PWM_PIN": 2,
    
    # Chân định hướng 1 (AIN1 & BIN1 nối song song)
    # Header Pi 4 Pin 7 -> BCM GPIO 4
    "IN1_PIN": 4,
    
    # Chân định hướng 2 (AIN2 & BIN2 nối song song)
    # Header Pi 4 Pin 5 -> BCM GPIO 3
    "IN2_PIN": 3,
    
    # Chân kích hoạt Standby (STBY = HIGH để cho phép driver hoạt động)
    # Header Pi 4 Pin 11 -> BCM GPIO 17
    "STBY_PIN": 17,
}

# ==============================================================================
# BẢNG ÁNH XẠ CHÂN 2 CẢM BIẾN SIÊU ÂM HC-SR04 (TRÁI & PHẢI)
# Bảo vệ chân Echo 5V qua cầu phân áp 1kΩ / 2kΩ xuống mức an toàn 3.3V cho Pi 4
# ==============================================================================
ULTRASONIC_CONFIG = {
    # Cảm biến siêu âm Trái (U_US1)
    "LEFT": {
        "TRIG_PIN": 6,   # Physical Pin 31 (BCM GPIO 6)  - Output 3.3V phát xung
        "ECHO_PIN": 5,   # Physical Pin 29 (BCM GPIO 5)  - Input 3.3V nhận xung phản hồi
    },
    # Cảm biến siêu âm Phải (U_US2)
    "RIGHT": {
        "TRIG_PIN": 22,  # Physical Pin 15 (BCM GPIO 22) - Output 3.3V phát xung
        "ECHO_PIN": 27,  # Physical Pin 13 (BCM GPIO 27) - Input 3.3V nhận xung phản hồi
    }
}

# ==============================================================================
# BẢNG ÁNH XẠ CẢM BIẾN DÒ LINE (TCRT5000 3 KÊNH)
# ==============================================================================
LINE_SENSOR_CONFIG = {
    "LEFT_PIN": 10,   # Physical Pin 19 (BCM GPIO 10)
    "CENTER_PIN": 9,  # Physical Pin 21 (BCM GPIO 9)
    "RIGHT_PIN": 11,  # Physical Pin 23 (BCM GPIO 11)
}

# ==============================================================================
# BẢNG THAM CHIẾU CHÂN VẬT LÝ (PHYSICAL PIN HEADER 2x20)
# ==============================================================================
LEFT_MOTORS_PHYSICAL_PINS = {
    "PWMA_L": 37,  # Physical Pin 37 (BCM GPIO 26)
    "AIN2_L": 35,  # Physical Pin 35 (BCM GPIO 19)
    "AIN1_L": 33,  # Physical Pin 33 (BCM GPIO 13)
    "STBY_L": 38,  # Physical Pin 38 (BCM GPIO 20)
}

RIGHT_MOTORS_PHYSICAL_PINS = {
    "PWMA_R": 3,   # Physical Pin 3  (BCM GPIO 2)
    "AIN2_R": 5,   # Physical Pin 5  (BCM GPIO 3)
    "AIN1_R": 7,   # Physical Pin 7  (BCM GPIO 4)
    "STBY_R": 11,  # Physical Pin 11 (BCM GPIO 17)
}

ULTRASONIC_PHYSICAL_PINS = {
    "TRIG_L": 31,  # Physical Pin 31 (BCM GPIO 6)
    "ECHO_L": 29,  # Physical Pin 29 (BCM GPIO 5)
    "TRIG_R": 15,  # Physical Pin 15 (BCM GPIO 22)
    "ECHO_R": 13,  # Physical Pin 13 (BCM GPIO 27)
}

# ==============================================================================
# THÔNG SỐ VẬN HÀNH PWM
# ==============================================================================
PWM_FREQUENCY_HZ = 1000  # Tần số băm xung 1 kHz (êm ái, không rít motor)
