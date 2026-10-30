"""
Kịch bản kiểm tra hoạt động của 2 Động cơ Bánh Trái (J_M1 & J_M2)
Sử dụng Driver TB6612 (U_TB1) kết nối Raspberry Pi 4 Carrier Board.

Cách chạy:
    python test_left_motors.py
"""

import time
import sys

# Đảm bảo in ký tự tiếng Việt an toàn trên cả Windows terminal và Linux/Raspberry Pi
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from motor_controller import TB6612LeftMotors
from config import LEFT_MOTORS_PHYSICAL_PINS, LEFT_MOTORS_CONFIG


def in_tieu_de():
    print("=" * 70)
    print("   CHƯƠNG TRÌNH KIỂM TRA 2 BÁNH BÊN TRÁI ROBOT 4WD (TB6612 - U_TB1)   ")
    print("=" * 70)
    print("Cấu hình kết nối phần cứng trên mạch Carrier 1 Lớp:")
    print(f"  * PWMA_L (Tốc độ)    : Pin {LEFT_MOTORS_PHYSICAL_PINS['PWMA_L']} -> BCM GPIO {LEFT_MOTORS_CONFIG['PWM_PIN']}")
    print(f"  * AIN1_L (Chiều 1)   : Pin {LEFT_MOTORS_PHYSICAL_PINS['AIN1_L']} -> BCM GPIO {LEFT_MOTORS_CONFIG['IN1_PIN']}")
    print(f"  * AIN2_L (Chiều 2)   : Pin {LEFT_MOTORS_PHYSICAL_PINS['AIN2_L']} -> BCM GPIO {LEFT_MOTORS_CONFIG['IN2_PIN']}")
    print(f"  * STBY_L (Kích hoạt) : Pin {LEFT_MOTORS_PHYSICAL_PINS['STBY_L']} -> BCM GPIO {LEFT_MOTORS_CONFIG['STBY_PIN']}")
    print("-" * 70)
    print("Động cơ được kiểm tra:")
    print("  1. J_M1: Động cơ Trước - Trái (Front-Left)")
    print("  2. J_M2: Động cơ Sau   - Trái (Rear-Left)")
    print("=" * 70)
    print()


def chay_kiem_tra_tu_dong(motor):
    """Quy trình kiểm tra tự động toàn diện các chế độ chuyển động"""
    print("\n>>> BẮT ĐẦU QUY TRÌNH KIỂM TRA TỰ ĐỘNG <<<\n")

    # 1. Bật driver
    print("[BƯỚC 1/6] Kích hoạt Driver TB6612 (STBY -> HIGH)...")
    motor.enable()
    time.sleep(1.0)

    # 2. Chạy tiến 50%
    print("\n[BƯỚC 2/6] Thử quay TIẾN 2 bánh trái ở 50% công suất trong 2.5 giây...")
    motor.forward(speed=50)
    time.sleep(2.5)

    # 3. Phanh dừng nhanh
    print("\n[BƯỚC 3/6] Thử nghiệm HÃM PHANH (Short Brake) trong 1.5 giây...")
    motor.brake()
    time.sleep(1.5)

    # 4. Chạy lùi 50%
    print("\n[BƯỚC 4/6] Thử quay LÙI 2 bánh trái ở 50% công suất trong 2.5 giây...")
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
    print("\n" + "=" * 70)
    print(">>> HOÀN THÀNH QUY TRÌNH KIỂM TRA TỰ ĐỘNG! 2 BÁNH TRÁI HOẠT ĐỘNG TỐT! <<<")
    print("=" * 70)


def che_do_dieu_khien_thu_cong(motor):
    """Chế độ điều khiển thủ công từ bàn phím"""
    print("\n>>> CHẾ ĐỘ ĐIỀU KHIỂN BẰNG BÀN PHÍM <<<")
    print("Phím điều khiển:")
    print("  [W] : Bánh trái quay TIẾN")
    print("  [S] : Bánh trái quay LÙI")
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
    motor = TB6612LeftMotors()

    try:
        print("Lựa chọn chế độ kiểm tra:")
        print("  1. Chạy bài kiểm tra tự động (Khuyến nghị cho lần chạy đầu tiên)")
        print("  2. Chế độ điều khiển thủ công bằng bàn phím")
        print("  3. Thoát")
        
        choice = input("\nChọn chế độ (1/2/3) [Mặc định: 1]: ").strip()
        if choice == '2':
            che_do_dieu_khien_thu_cong(motor)
        elif choice == '3':
            print("Đã thoát.")
        else:
            chay_kiem_tra_tu_dong(motor)

    except KeyboardInterrupt:
        print("\n[DỪNG KHẨN CẤP] Đã nhận tín hiệu ngắt (Ctrl+C).")
    finally:
        motor.cleanup()


if __name__ == "__main__":
    main()
