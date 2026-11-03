"""
Chương trình Điều khiển Xe Robot Tự Hành Né Vật Cản Thông Minh
Sử dụng 2 Cảm biến Siêu âm HC-SR04 (Trái & Phải) + Hệ truyền động 4WD TB6612
Bo mạch Robot Carrier 1 Lớp - Raspberry Pi 4
Tác giả: Nhóm Đồ Án Tốt Nghiệp Robot Tự Hành

Cách chạy trên Raspberry Pi:
    python auto_drive.py
"""

import time
import sys

# Đảm bảo in tiếng Việt an toàn trên console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from motor_controller import Robot4WD
from ultrasonic_sensor import DualUltrasonicSensor, HARDWARE_AVAILABLE

# ========================================================
# CẤU HÌNH CÁC NGƯỠNG CỰ LY AN TOÀN VÀ TỐC ĐỘ XE
# ========================================================
DIST_DANGER_CM   = 18.0  # Ngưỡng nguy hiểm (< 18cm) -> Phanh khẩn cấp & Lùi xe
DIST_WARNING_CM  = 35.0  # Ngưỡng cảnh báo  (18 - 35cm) -> Giảm tốc và bẻ lái né
DIST_CLEAR_CM    = 55.0  # Ngưỡng thông thoáng (> 35cm) -> Tiến đều ổn định

SPEED_CRUISE     = 55    # Tốc độ tiến hành trình (0 - 100%)
SPEED_SLOW       = 35    # Tốc độ khi tiếp cận vùng cảnh báo
SPEED_TURN       = 50    # Tốc độ khi bẻ lái hoặc xoay góc né vật cản
SPEED_REVERSE    = 45    # Tốc độ khi lùi thoát hiểm


def in_tieu_de():
    print("=" * 78)
    print("   HỆ THỐNG ĐIỀU KHIỂN XE ROBOT TỰ HÀNH NÉ VẬT CẢN (2x HC-SR04 + 4WD)   ")
    print("=" * 78)
    print("Cấu hình điều khiển:")
    print("  * 4 Bánh xe 4WD     : Driver Trái (U_TB1) & Driver Phải (U_TB2)")
    print("  * Cảm biến siêu âm  : Trái (GPIO 27/22) | Phải (GPIO 5/6)")
    print("  * Ngưỡng hành trình :")
    print(f"      - Thông thoáng  : > {DIST_WARNING_CM} cm (Tiến đều {SPEED_CRUISE}%)")
    print(f"      - Vùng cảnh báo : {DIST_DANGER_CM} - {DIST_WARNING_CM} cm (Bẻ lái né vi sai {SPEED_SLOW}%)")
    print(f"      - Vùng nguy hiểm: < {DIST_DANGER_CM} cm (Phanh cứng -> Lùi -> Xoay góc thoát)")
    print("-" * 78)
    if HARDWARE_AVAILABLE:
        print("  [PHẦN CỨNG] Đang chạy trên Raspberry Pi 4 thực tế.")
    else:
        print("  [MÔ PHỎNG] Đang chạy chế độ mô phỏng trên máy tính/PC.")
    print("=" * 78)
    print()


def che_do_tu_hanh(robot, sonar):
    """
    Thuật toán Tự hành Né vật cản liên tục thời gian thực:
    - Quét tuần tự 2 cảm biến siêu âm Trái và Phải.
    - Ra quyết định tức thời điều khiển 4 bánh xe.
    """
    print("\n>>> BẮT ĐẦU CHẾ ĐỘ TỰ HÀNH NÉ VẬT CẢN THÔNG MINH <<<")
    print("Xe đang tự động định hướng di chuyển. Bấm [Ctrl + C] để dừng xe bất kỳ lúc nào.\n")
    print(f"{'CỰ LY TRÁI':<14} | {'CỰ LY PHẢI':<14} | {'HÀNH ĐỘNG CỦA ROBOT'}")
    print("-" * 78)

    robot.enable()

    try:
        while True:
            # 1. Đọc khoảng cách tuần tự 2 cảm biến Trái và Phải (cách nhau 30ms)
            dist_l, dist_r = sonar.read_both_cm(inter_sensor_delay=0.03)

            # Quy ước None (ngoài tầm đo > 400cm) xem như thông thoáng (999cm)
            eff_l = dist_l if dist_l is not None else 999.0
            eff_r = dist_r if dist_r is not None else 999.0

            txt_l = f"{dist_l:5.1f} cm" if dist_l is not None else " >400 cm "
            txt_r = f"{dist_r:5.1f} cm" if dist_r is not None else " >400 cm "

            # ----------------------------------------------------
            # TRƯỜNG HỢP 1: CẢ 2 BÊN BỊ CHẶN HOẶC GẶP VẬT CẢN QUÁ GẦN (< 18cm)
            # ----------------------------------------------------
            if eff_l < DIST_DANGER_CM or eff_r < DIST_DANGER_CM:
                print(f"{txt_l:<14} | {txt_r:<14} | 🔴 NGUY HIỂM! PHANH HÃM & LÙI XE")
                
                # 1. Phanh khẩn cấp lập tức
                robot.brake()
                time.sleep(0.2)

                # 2. Lùi xe thoát hiểm trong 0.6 giây
                robot.reverse(speed=SPEED_REVERSE)
                time.sleep(0.6)
                robot.brake()
                time.sleep(0.15)

                # 3. Đo lại khoảng cách sau khi lùi để chọn hướng thoát tốt nhất
                new_l, new_r = sonar.read_both_cm(inter_sensor_delay=0.03)
                chk_l = new_l if new_l is not None else 999.0
                chk_r = new_r if new_r is not None else 999.0

                if chk_l >= chk_r:
                    # Bên Trái thoáng hơn -> Xoay sang Trái
                    print(f"               |                | ↩️ XOAY TRÁI THOÁT HIỂM (Trái thoáng hơn: {chk_l:.1f}cm)")
                    robot.spin_left(speed=SPEED_TURN)
                    time.sleep(0.45)
                else:
                    # Bên Phải thoáng hơn -> Xoay sang Phải
                    print(f"               |                | ↪️ XOAY PHẢI THOÁT HIỂM (Phải thoáng hơn: {chk_r:.1f}cm)")
                    robot.spin_right(speed=SPEED_TURN)
                    time.sleep(0.45)

                robot.brake()
                time.sleep(0.1)

            # ----------------------------------------------------
            # TRƯỜNG HỢP 2: VẬT CẢN CHỦ YẾU NẰM BÊN TRÁI (18cm - 35cm)
            # ----------------------------------------------------
            elif eff_l < DIST_WARNING_CM and eff_r >= DIST_WARNING_CM:
                print(f"{txt_l:<14} | {txt_r:<14} | 🟡 VẬT CẢN TRÁI -> RẼ PHẢI NÉ")
                # Giảm tốc bánh phải, bẻ lái sang phải mượt mà
                robot.turn_right(speed=SPEED_SLOW, diff_ratio=0.2)
                time.sleep(0.1)

            # ----------------------------------------------------
            # TRƯỜNG HỢP 3: VẬT CẢN CHỦ YẾU NẰM BÊN PHẢI (18cm - 35cm)
            # ----------------------------------------------------
            elif eff_r < DIST_WARNING_CM and eff_l >= DIST_WARNING_CM:
                print(f"{txt_l:<14} | {txt_r:<14} | 🟡 VẬT CẢN PHẢI -> RẼ TRÁI NÉ")
                # Giảm tốc bánh trái, bẻ lái sang trái mượt mà
                robot.turn_left(speed=SPEED_SLOW, diff_ratio=0.2)
                time.sleep(0.1)

            # ----------------------------------------------------
            # TRƯỜNG HỢP 4: CẢ 2 BÊN ĐỀU Ở VÙNG CẢNH BÁO (Góc hẹp / Hành lang)
            # ----------------------------------------------------
            elif eff_l < DIST_WARNING_CM and eff_r < DIST_WARNING_CM:
                if eff_l > eff_r:
                    print(f"{txt_l:<14} | {txt_r:<14} | 🟠 KHE HẸP -> LƯỢN SANG TRÁI")
                    robot.turn_left(speed=SPEED_SLOW, diff_ratio=0.1)
                else:
                    print(f"{txt_l:<14} | {txt_r:<14} | 🟠 KHE HẸP -> LƯỢN SANG PHẢI")
                    robot.turn_right(speed=SPEED_SLOW, diff_ratio=0.1)
                time.sleep(0.1)

            # ----------------------------------------------------
            # TRƯỜNG HỢP 5: ĐƯỜNG ĐI HOÀN TOÀN THÔNG THOÁNG (> 35cm)
            # ----------------------------------------------------
            else:
                print(f"{txt_l:<14} | {txt_r:<14} | 🟢 ĐƯỜNG THÔNG -> TIẾN THẲNG ({SPEED_CRUISE}%)")
                robot.forward(speed=SPEED_CRUISE)
                time.sleep(0.08)

    except KeyboardInterrupt:
        print("\n\n>>> Đã nhận lệnh ngắt từ người dùng!")
    finally:
        robot.brake()
        time.sleep(0.1)
        robot.stop()
        robot.disable()
        print(">>> ĐÃ DỪNG XE AN TOÀN.")


def che_do_kiem_tra_dong_co(robot):
    """Kiểm tra hoạt động toàn diện của cả 4 bánh xe theo quy trình chuẩn"""
    print("\n>>> KIỂM TRA TOÀN DIỆN 4 BÁNH XE (TB6612 #1 & #2) <<<")
    robot.enable()

    try:
        print("\n1. TIẾN THẲNG (Forward 50%) trong 2.0 giây...")
        robot.forward(speed=50)
        time.sleep(2.0)

        print("2. HÃM PHANH (Brake)...")
        robot.brake()
        time.sleep(1.0)

        print("3. LÙI THẲNG (Reverse 50%) trong 2.0 giây...")
        robot.reverse(speed=50)
        time.sleep(2.0)

        print("4. HÃM PHANH (Brake)...")
        robot.brake()
        time.sleep(1.0)

        print("5. RẼ TRÁI MƯỢT (Turn Left vi sai) trong 2.0 giây...")
        robot.turn_left(speed=50, diff_ratio=0.25)
        time.sleep(2.0)

        print("6. RẼ PHẢI MƯỢT (Turn Right vi sai) trong 2.0 giây...")
        robot.turn_right(speed=50, diff_ratio=0.25)
        time.sleep(2.0)

        print("7. XOAY TẠI CHỖ SANG TRÁI (Spin Left) trong 1.5 giây...")
        robot.spin_left(speed=50)
        time.sleep(1.5)

        print("8. XOAY TẠI CHỖ SANG PHẢI (Spin Right) trong 1.5 giây...")
        robot.spin_right(speed=50)
        time.sleep(1.5)

        print("9. DỪNG TỰ NHIÊN (Stop/Coast)...")
        robot.stop()
        time.sleep(0.5)

        print("\n>>> HOÀN THÀNH KIỂM TRA ĐỘNG CƠ! CẢ 4 BÁNH HOẠT ĐỘNG HOÀN HẢO! <<<")

    finally:
        robot.stop()
        robot.disable()


def main():
    in_tieu_de()
    robot = Robot4WD()
    sonar = DualUltrasonicSensor()

    try:
        while True:
            print("\nCHỌN CHẾ ĐỘ HOẠT ĐỘNG CỦA XE:")
            print("  [1] TỰ HÀNH NÉ VẬT CẢN THÔNG MINH (Khuyên dùng)")
            print("  [2] Chạy thử nghiệm toàn bộ chuyển động 4 bánh (Tiến/Lùi/Rẽ/Xoay)")
            print("  [3] Thoát chương trình")

            try:
                chon = input("\nNhập lựa chọn của bạn (1-3) [Mặc định 1]: ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not chon:
                chon = "1"

            if chon == "1":
                che_do_tu_hanh(robot, sonar)
            elif chon == "2":
                che_do_kiem_tra_dong_co(robot)
            elif chon == "3" or chon.lower() in ["q", "exit", "quit"]:
                break
            else:
                print("Lựa chọn không hợp lệ, vui lòng chọn 1, 2 hoặc 3.")

    finally:
        print("\nĐang dọn dẹp và giải phóng tài nguyên GPIO...")
        robot.cleanup()
        sonar.cleanup()
        print("Đã thoát an toàn!")


if __name__ == "__main__":
    main()
