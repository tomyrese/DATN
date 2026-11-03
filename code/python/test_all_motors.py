"""
Kịch bản kiểm tra toàn diện Hệ truyền động 4 Bánh xe (4WD Robot Carrier)
Đồng bộ cả 2 Driver TB6612 (U_TB1 Trái & U_TB2 Phải)
Bo mạch Robot Carrier 1 Lớp - Raspberry Pi 4

Cách chạy:
    python test_all_motors.py
"""

import time
import sys

# Đảm bảo in ký tự tiếng Việt an toàn trên cả Windows terminal và Linux/Raspberry Pi
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from motor_controller import Robot4WD, TB6612LeftMotors, TB6612RightMotors
from config import LEFT_MOTORS_CONFIG, RIGHT_MOTORS_CONFIG


def in_tieu_de():
    print("=" * 75)
    print("   CHƯƠNG TRÌNH KIỂM TRA ĐỒNG BỘ TOÀN BỘ 4 BÁNH XE ROBOT (4WD SYSTEM)   ")
    print("=" * 75)
    print("Sơ đồ bố trí động cơ:")
    print("       [Phía Trước Robot]")
    print("   [J_M1: Trước-Trái]    [J_M3: Trước-Phải]")
    print("   [J_M2: Sau-Trái  ]    [J_M4: Sau-Phải  ]")
    print("       [Phía Sau Robot]")
    print("-" * 75)
    print(f"Driver Trái (U_TB1): PWM={LEFT_MOTORS_CONFIG['PWM_PIN']}, IN1={LEFT_MOTORS_CONFIG['IN1_PIN']}, IN2={LEFT_MOTORS_CONFIG['IN2_PIN']}, STBY={LEFT_MOTORS_CONFIG['STBY_PIN']}")
    print(f"Driver Phải (U_TB2): PWM={RIGHT_MOTORS_CONFIG['PWM_PIN']}, IN1={RIGHT_MOTORS_CONFIG['IN1_PIN']}, IN2={RIGHT_MOTORS_CONFIG['IN2_PIN']}, STBY={RIGHT_MOTORS_CONFIG['STBY_PIN']}")
    print("=" * 75)
    print()


def chay_kiem_tra_toan_dien(robot):
    """Quy trình kiểm tra đồng bộ cả 4 bánh: Tiến, Lùi, Rẽ trái, Rẽ phải, Xoay tại chỗ"""
    print("\n>>> BẮT ĐẦU QUY TRÌNH KIỂM TRA 4WD ĐỒNG BỘ <<<\n")

    robot.enable()

    print("[BƯỚC 1/6] TIẾN THẲNG 50% trong 2.5 giây (Cả 4 bánh quay tới)...")
    robot.forward(speed=50)
    time.sleep(2.5)

    print("[BƯỚC 2/6] HÃM PHANH 1.0 giây...")
    robot.brake()
    time.sleep(1.0)

    print("[BƯỚC 3/6] LÙI THẲNG 50% trong 2.5 giây (Cả 4 bánh quay lùi)...")
    robot.reverse(speed=50)
    time.sleep(2.5)

    print("[BƯỚC 4/6] DỪNG TRÔI 1.0 giây...")
    robot.stop()
    time.sleep(1.0)

    print("[BƯỚC 5/6] XOAY TRÒN TẠI CHỖ SANG TRÁI (Tank Turn Left) 50% trong 2.0 giây...")
    robot.spin_left(speed=50)
    time.sleep(2.0)

    print("[BƯỚC 6/6] XOAY TRÒN TẠI CHỖ SANG PHẢI (Tank Turn Right) 50% trong 2.0 giây...")
    robot.spin_right(speed=50)
    time.sleep(2.0)

    robot.stop()
    robot.disable()
    print("\n" + "=" * 75)
    print(">>> HOÀN THÀNH QUY TRÌNH KIỂM TRA ĐỒNG BỘ 4WD! <<<")
    print("=" * 75)


def che_do_dieu_khien_xe_thu_cong(robot):
    """Điều khiển xe toàn diện bằng bàn phím"""
    print("\n>>> ĐIỀU KHIỂN XE ROBOT 4 BÁNH BẰNG BÀN PHÍM <<<")
    print("Phím điều khiển:")
    print("  [W] : TIẾN THẲNG")
    print("  [S] : LÙI THẲNG")
    print("  [A] : RẼ TRÁI (Vi sai)")
    print("  [D] : RẼ PHẢI (Vi sai)")
    print("  [Q] : XOAY TẠI CHỖ TRÁI (Tank Spin Left)")
    print("  [E] : XOAY TẠI CHỖ PHẢI (Tank Spin Right)")
    print("  [B] : HÃM PHANH (Brake)")
    print("  [Space/X] : DỪNG TRÔI (Stop)")
    print("  [+] / [-] : Tăng / Giảm tốc độ")
    print("  [ESC/Z]   : Thoát")
    print("-" * 50)

    speed = 60
    robot.enable()

    try:
        while True:
            cmd = input(f"\n[{robot.current_state} | Tốc độ: {speed}%] Nhập lệnh: ").strip().upper()
            if not cmd:
                continue

            if cmd == 'W':
                robot.forward(speed)
            elif cmd == 'S':
                robot.reverse(speed)
            elif cmd == 'A':
                robot.turn_left(speed)
            elif cmd == 'D':
                robot.turn_right(speed)
            elif cmd == 'Q':
                robot.spin_left(speed)
            elif cmd == 'E':
                robot.spin_right(speed)
            elif cmd == 'B':
                robot.brake()
            elif cmd in ['X', ' ']:
                robot.stop()
            elif cmd == '+':
                speed = min(100, speed + 10)
                print(f"-> Tốc độ tăng lên: {speed}%")
            elif cmd == '-':
                speed = max(20, speed - 10)
                print(f"-> Tốc độ giảm xuống: {speed}%")
            elif cmd in ['Z', 'ESC']:
                print("Đang thoát...")
                break
            else:
                print("Lệnh không hợp lệ (W/A/S/D/Q/E/B/X/+/-/Z).")
    except KeyboardInterrupt:
        print("\nNhận tín hiệu dừng từ người dùng.")


def main():
    in_tieu_de()

    while True:
        print("\nLỰA CHỌN CHẾ ĐỘ KIỂM TRA:")
        print("  1. Chạy bài kiểm tra tự động đồng bộ cả 4 bánh (Tiến/Lùi/Xoay)")
        print("  2. Điều khiển xe tự do bằng phím WASD")
        print("  3. Chỉ kiểm tra 2 bánh Trái (TB6612 Left)")
        print("  4. Chỉ kiểm tra 2 bánh Phải (TB6612 Right)")
        print("  5. Thoát")

        choice = input("\nNhập lựa chọn của bạn (1-5): ").strip()

        if choice == '1':
            robot = Robot4WD()
            try:
                chay_kiem_tra_toan_dien(robot)
            finally:
                robot.cleanup()
        elif choice == '2':
            robot = Robot4WD()
            try:
                che_do_dieu_khien_xe_thu_cong(robot)
            finally:
                robot.cleanup()
        elif choice == '3':
            from test_left_motors import chay_kiem_tra_tu_dong as test_left
            motor_l = TB6612LeftMotors()
            try:
                test_left(motor_l)
            finally:
                motor_l.cleanup()
        elif choice == '4':
            from test_right_motors import chay_kiem_tra_tu_dong as test_right
            motor_r = TB6612RightMotors()
            try:
                test_right(motor_r)
            finally:
                motor_r.cleanup()
        elif choice == '5':
            print("Đã thoát chương trình.")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn từ 1 đến 5.")


if __name__ == "__main__":
    main()
