"""
Cấu hình chân GPIO Raspberry Pi 4 cho Bo mạch Robot Carrier (Chuẩn 1 Lớp)
Dựa trên sơ đồ nguyên lý Pi4_Robot_Carrier_1Layer.kicad_sch và PCB robot_electronics.kicad_pcb
"""

# ==============================================================================
# BẢNG ÁNH XẠ CHÂN ĐIỀU KHIỂN DRIVER TB6612 BÊN TRÁI (U_TB1)
# Điều khiển đồng thời 2 bánh bên trái:
#   - Động cơ trước trái (J_M1 - Motor Front Left)
#   - Động cơ sau trái   (J_M2 - Motor Rear Left)
# ==============================================================================

# Chân BCM GPIO trên Raspberry Pi 4
LEFT_MOTORS_CONFIG = {
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
# BẢNG THAM CHIẾU CHÂN VẬT LÝ (PHYSICAL PIN HEADER 2x20)
# ==============================================================================
LEFT_MOTORS_PHYSICAL_PINS = {
    "PWMA_L": 3,   # Physical Pin 3  (BCM GPIO 2)
    "AIN2_L": 5,   # Physical Pin 5  (BCM GPIO 3)
    "AIN1_L": 7,   # Physical Pin 7  (BCM GPIO 4)
    "STBY_L": 11,  # Physical Pin 11 (BCM GPIO 17)
}

# ==============================================================================
# THÔNG SỐ VẬN HÀNH PWM
# ==============================================================================
PWM_FREQUENCY_HZ = 1000  # Tần số băm xung 1 kHz (êm ái, không rít motor)
DEFAULT_SPEED = 60       # Tốc độ mặc định (0 - 100%)
MIN_SPEED = 20           # Ngưỡng tốc độ tối thiểu để motor thắng ma sát ban đầu
MAX_SPEED = 100          # Tốc độ tối đa
