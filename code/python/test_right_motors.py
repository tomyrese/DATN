"""
Kịch bản kiểm tra hoạt động của 2 Động cơ Bánh Phải (J_M3 & J_M4)
Sử dụng Driver TB6612 (U_TB2) kết nối Raspberry Pi 4 Carrier Board.

Cách chạy:
    python test_right_motors.py
"""

import time
import sys

# Đảm bảo in ký tự tiếng Việt an toàn trên cả Windows terminal và Linux/Raspberry Pi
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from motor_controller import TB6612RightMotors, HAVE_RPI_GPIO
from config import RIGHT_MOTORS_PHYSICAL_PINS, RIGHT_MOTORS_CONFIG

if HAVE_RPI_GPIO:
    import RPi.GPIO as GPIO


def in_tieu_de():
    print("=" * 75)
    print("   CHƯƠNG TRÌNH CHẨN ĐOÁN & KIỂM TRA 2 BÁNH BÊN PHẢI (TB6612 - U_TB2)   ")
    print("=" * 75)
    print("Cấu hình kết nối phần cứng trên mạch Carrier 1 Lớp:")
    print(f"  * PWMA_R (Tốc độ)    : Header Pin {RIGHT_MOTORS_PHYSICAL_PINS['PWMA_R']} -> BCM GPIO {RIGHT_MOTORS_CONFIG['PWM_PIN']}")
    print(f"  * AIN1_R (Chiều 1)   : Header Pin {RIGHT_MOTORS_PHYSICAL_PINS['AIN1_R']} -> BCM GPIO {RIGHT_MOTORS_CONFIG['IN1_PIN']}")
    print(f"  * AIN2_R (Chiều 2)   : Header Pin {RIGHT_MOTORS_PHYSICAL_PINS['AIN2_R']} -> BCM GPIO {RIGHT_MOTORS_CONFIG['IN2_PIN']}")
    print(f"  * STBY_R (Kích hoạt) : Header Pin {RIGHT_MOTORS_PHYSICAL_PINS['STBY_R']} -> BCM GPIO {RIGHT_MOTORS_CONFIG['STBY_PIN']}")
    print(f"  * Logic VCC (Pad 10) : Header Pin 4 (+5V_PI_2)")
    print(f"  * Motor VM (Pad 9)   : Nguồn Pin 11.1V từ công tắc nguồn")
    print("-" * 75)
    print("Động cơ được kiểm tra:")
    print("  1. J_M3: Động cơ Trước - Phải (Front-Right)")
    print("  2. J_M4: Động cơ Sau   - Phải (Rear-Right)")
    print("=" * 75)
    print()


def kiem_tra_truc_tiep_khong_pwm():
    """
    Chế độ chẩn đoán mức phần cứng (Hardware Diagnostic Bypass):
    Đặt trực tiếp các chân GPIO lên mức HIGH/LOW độc lập, KHÔNG thông qua bộ băm xung PWM.
    Giúp xác định 100% nguyên nhân là do:
      - Phần cứng / Nguồn 5V / Dây nối hay
      - Phần mềm băm xung PWM trên Raspberry Pi
    """
    print("\n" + "=" * 75)
    print(">>> CHẾ ĐỘ 1: CHẨN ĐOÁN TRỰC TIẾP KHÔNG DÙNG PWM (BYPASS TEST) <<<")
    print("=" * 75)

    if not HAVE_RPI_GPIO:
        print("[MÔ PHỎNG] Không có thư viện RPi.GPIO trên máy tính này.")
        return

    pwm_pin = RIGHT_MOTORS_CONFIG["PWM_PIN"]
    in1_pin = RIGHT_MOTORS_CONFIG["IN1_PIN"]
    in2_pin = RIGHT_MOTORS_CONFIG["IN2_PIN"]
    stby_pin = RIGHT_MOTORS_CONFIG["STBY_PIN"]

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        print(f"1. Khởi tạo chân: STBY={stby_pin}, IN1={in1_pin}, IN2={in2_pin}, PWM={pwm_pin}")
        GPIO.setup(stby_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(in1_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(in2_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pwm_pin, GPIO.OUT, initial=GPIO.LOW)

        print("2. Kích hoạt STBY -> HIGH (Bật Driver U_TB2)...")
        GPIO.output(stby_pin, GPIO.HIGH)
        time.sleep(0.5)

        print("3. Đặt chiều quay: IN1=HIGH, IN2=LOW...")
        GPIO.output(in1_pin, GPIO.HIGH)
        GPIO.output(in2_pin, GPIO.LOW)

        print("4. BẬT TRỰC TIẾP PWM -> HIGH (100% công suất không băm xung)...")
        print("   >>> HÃY QUAN SÁT 2 BÁNH PHẢI CÓ QUAY KHÔNG TRONG 3 GIÂY! <<<")
        GPIO.output(pwm_pin, GPIO.HIGH)
        time.sleep(3.0)

        print("5. Dừng động cơ (PWM -> LOW)...")
        GPIO.output(pwm_pin, GPIO.LOW)
        time.sleep(1.0)

        print("6. Đảo chiều quay: IN1=LOW, IN2=HIGH, PWM=HIGH trong 3 giây...")
        GPIO.output(in1_pin, GPIO.LOW)
        GPIO.output(in2_pin, GPIO.HIGH)
        GPIO.output(pwm_pin, GPIO.HIGH)
        time.sleep(3.0)

        print("7. Tắt toàn bộ driver...")
        GPIO.output(pwm_pin, GPIO.LOW)
        GPIO.output(in1_pin, GPIO.LOW)
        GPIO.output(in2_pin, GPIO.LOW)
        GPIO.output(stby_pin, GPIO.LOW)

        print("\n" + "-" * 75)
        print("KẾT QUẢ CHẨN ĐOÁN:")
        print("  * NẾU 2 BÁNH PHẢI ĐÃ QUAY: Phần cứng, nguồn 5V và Driver U_TB2 hoàn toàn TỐT!")
        print("    -> Vấn đề chỉ nằm ở xung PWM hoặc phần mềm điều phối.")
        print("  * NẾU 2 BÁNH PHẢI VẪN KHÔNG QUAY:")
        print("    -> Cần kiểm tra ngay 3 điểm phần cứng vật lý:")
        print("       1. Chân số 4 trên Header Pi 4 (+5V_PI_2): Đo đồng hồ VOM xem Pad 10 của U_TB2 có 5V không.")
        print("       2. Nguồn VM (Pad 9 của U_TB2): Đo xem có nguồn pin 11.1V / 12V không.")
        print("       3. Siết chặt ốc vít cọc đấu dây động cơ J_M3 và J_M4.")
        print("-" * 75)

    except Exception as e:
        print(f"Lỗi trong quá trình kiểm tra trực tiếp: {e}")
    finally:
        try:
            GPIO.cleanup([pwm_pin, in1_pin, in2_pin, stby_pin])
        except Exception:
            pass


def chay_kiem_tra_tu_dong(motor):
    """Quy trình kiểm tra tự động toàn diện các chế độ chuyển động"""
    print("\n>>> BẮT ĐẦU QUY TRÌNH KIỂM TRA TỰ ĐỘNG BÁNH PHẢI <<<\n")

    # 1. Bật driver
    print("[BƯỚC 1/6] Kích hoạt Driver TB6612 Bên Phải (STBY -> HIGH)...")
    motor.enable()
    time.sleep(1.0)

    # 2. Chạy tiến 50%
    print("\n[BƯỚC 2/6] Thử quay TIẾN 2 bánh phải ở 50% công suất trong 2.5 giây...")
    motor.forward(speed=50)
    time.sleep(2.5)

    # 3. Phanh dừng nhanh
    print("\n[BƯỚC 3/6] Thử nghiệm HÃM PHANH (Short Brake) trong 1.5 giây...")
    motor.brake()
    time.sleep(1.5)

    # 4. Chạy lùi 50%
    print("\n[BƯỚC 4/6] Thử quay LÙI 2 bánh phải ở 50% công suất trong 2.5 giây...")
    motor.reverse(speed=50)
    time.sleep(2.5)

    # 5. Dừng tự nhiên
    print("\n[BƯỚC 5/6] Dừng trôi (Coast) trong 1.0 giây...")
    motor.stop()
    time.sleep(1.0)

    # 6. Thử nghiệm tăng giảm tốc mượt (Speed Ramp)
    print("\n[BƯỚC 6/6] Thử nghiệm TĂNG TỐC DẦN (0% -> 100%) và GIẢM TỐC DẦN (100% -> 0%)...")
    print("  -> Tăng tốc tiến dần:")
    for spd in range(20, 101, 10):
        motor.forward(speed=spd)
        time.sleep(0.3)
    
    time.sleep(0.5)

    print("  -> Giảm tốc dần:")
    for spd in range(100, 10, -10):
        motor.forward(speed=spd)
        time.sleep(0.3)

    # Hoàn thành
    motor.stop()
    motor.disable()
    print("\n" + "=" * 75)
    print(">>> HOÀN THÀNH QUY TRÌNH KIỂM TRA TỰ ĐỘNG! <<<")
    print("=" * 75)


def che_do_dieu_khien_thu_cong(motor):
    """Chế độ điều khiển thủ công từ bàn phím"""
    print("\n>>> CHẾ ĐỘ ĐIỀU KHIỂN BÁNH PHẢI BẰNG BÀN PHÍM <<<")
    print("Phím điều khiển:")
    print("  [W] : Bánh phải quay TIẾN")
    print("  [S] : Bánh phải quay LÙI")
    print("  [B] : HÃM PHANH (Brake)")
    print("  [Space/X] : DỪNG TRÔI (Stop)")
    print("  [+] / [-] : Tăng / Giảm tốc độ 10%")
    print("  [Q] : Thoát chương trình")
    print("-" * 50)

    speed = 60
    motor.enable()

    try:
        while True:
            cmd = input(f"\n[Tốc độ hiện tại: {speed}%] Nhập lệnh (W/S/B/X/+/-/Q): ").strip().upper()
            if not cmd:
                continue

            if cmd == 'W':
                motor.forward(speed)
            elif cmd == 'S':
                motor.reverse(speed)
            elif cmd == 'B':
                motor.brake()
            elif cmd in ['X', ' ']:
                motor.stop()
            elif cmd == '+':
                speed = min(100, speed + 10)
                print(f"-> Đã tăng tốc độ lên: {speed}%")
                if motor.current_direction == "FORWARD":
                    motor.forward(speed)
                elif motor.current_direction == "REVERSE":
                    motor.reverse(speed)
            elif cmd == '-':
                speed = max(20, speed - 10)
                print(f"-> Đã giảm tốc độ xuống: {speed}%")
                if motor.current_direction == "FORWARD":
                    motor.forward(speed)
                elif motor.current_direction == "REVERSE":
                    motor.reverse(speed)
            elif cmd == 'Q':
                print("Đang thoát...")
                break
            else:
                print("Lệnh không hợp lệ! Vui lòng nhập W, S, B, X, +, - hoặc Q.")
    except KeyboardInterrupt:
        print("\nNhận tín hiệu dừng từ người dùng.")


def main():
    in_tieu_de()

    while True:
        print("\nLỰA CHỌN CHẾ ĐỘ KIỂM TRA:")
        print("  1. Chẩn đoán TRỰC TIẾP KHÔNG DÙNG PWM (Khuyến nghị số 1 để xác định ngay phần cứng)")
        print("  2. Chạy bài kiểm tra tự động với băm xung PWM (Tiến/Lùi/Phanh/Tăng tốc)")
        print("  3. Chế độ điều khiển thủ công bằng phím (W/S/B/X)")
        print("  4. Thoát")

        choice = input("\nNhập lựa chọn của bạn (1-4): ").strip()

        if choice == '1':
            kiem_tra_truc_tiep_khong_pwm()
        elif choice == '2':
            motor = TB6612RightMotors()
            try:
                chay_kiem_tra_tu_dong(motor)
            finally:
                motor.cleanup()
        elif choice == '3':
            motor = TB6612RightMotors()
            try:
                che_do_dieu_khien_thu_cong(motor)
            finally:
                motor.cleanup()
        elif choice == '4':
            print("Đã thoát chương trình kiểm tra bánh phải.")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn từ 1 đến 4.")


if __name__ == "__main__":
    main()

