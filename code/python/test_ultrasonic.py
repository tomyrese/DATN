"""
Kịch bản kiểm tra toàn diện 2 Cảm biến Siêu âm HC-SR04 (Trái & Phải)
Bo mạch Robot Carrier 1 Lớp - Raspberry Pi 4
Tác giả: Nhóm Đồ Án Tốt Nghiệp Robot Tự Hành

Cách chạy trên Raspberry Pi:
    python test_ultrasonic.py
"""

import time
import sys
import math

# Đảm bảo in tiếng Việt an toàn trên console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config import ULTRASONIC_CONFIG, ULTRASONIC_PHYSICAL_PINS
from ultrasonic_sensor import DualUltrasonicSensor, HARDWARE_AVAILABLE


def in_tieu_de():
    print("=" * 78)
    print("   CHƯƠNG TRÌNH TEST 2 CẢM BIẾN SIÊU ÂM HC-SR04 (TRÁI & PHẢI)   ")
    print("=" * 78)
    print("Sơ đồ đấu nối chân trên Bo mạch Carrier 1 Lớp (Raspberry Pi 4):")
    print("  1. CẢM BIẾN TRÁI (U_US1 - Sensor Left):")
    print(f"     * TRIG_L (Phát) : Physical Pin {ULTRASONIC_PHYSICAL_PINS['TRIG_L']:2d} -> BCM GPIO {ULTRASONIC_CONFIG['LEFT']['TRIG_PIN']:2d} (Output 3.3V)")
    print(f"     * ECHO_L (Thu)  : Physical Pin {ULTRASONIC_PHYSICAL_PINS['ECHO_L']:2d} -> BCM GPIO {ULTRASONIC_CONFIG['LEFT']['ECHO_PIN']:2d} (Input qua cầu 1k/2k)")
    print("  2. CẢM BIẾN PHẢI (U_US2 - Sensor Right):")
    print(f"     * TRIG_R (Phát) : Physical Pin {ULTRASONIC_PHYSICAL_PINS['TRIG_R']:2d} -> BCM GPIO {ULTRASONIC_CONFIG['RIGHT']['TRIG_PIN']:2d} (Output 3.3V)")
    print(f"     * ECHO_R (Thu)  : Physical Pin {ULTRASONIC_PHYSICAL_PINS['ECHO_R']:2d} -> BCM GPIO {ULTRASONIC_CONFIG['RIGHT']['ECHO_PIN']:2d} (Input qua cầu 1k/2k)")
    print("-" * 78)
    if HARDWARE_AVAILABLE:
        print("  [PHẦN CỨNG] Đã phát hiện thư viện RPi.GPIO -> Chạy trên phần cứng thực tế.")
    else:
        print("  [MÔ PHỎNG] Không có phần cứng Raspberry Pi -> Chạy ở chế độ mô phỏng kiểm thử.")
    print("=" * 78)
    print()


def tao_thanh_do(dist_cm, max_bar=18):
    """Tạo thanh biểu đồ trực quan ASCII cho cự ly"""
    if dist_cm is None:
        return "[ > 400 cm / Trống ]"
    
    # Chuẩn hóa trong khoảng 0 - 100cm
    filled = min(max_bar, int((dist_cm / 100.0) * max_bar))
    bar = "█" * filled + "░" * (max_bar - filled)
    return f"[{bar}]"


def danh_gia_canh_bao(dist_cm):
    """Đánh giá mức độ an toàn theo khoảng cách"""
    if dist_cm is None or dist_cm > 60.0:
        return "🟢 An toàn"
    elif dist_cm > 30.0:
        return "🟡 Cảnh báo"
    elif dist_cm > 15.0:
        return "🟠 Giảm tốc"
    else:
        return "🔴 DỪNG GẤP!"


def che_do_quet_lien_tuc(sensor):
    """Chế độ 1: Quét trực quan thời gian thực (Live Dashboard 10Hz)"""
    print("\n>>> BẮT ĐẦU QUÉT LIÊN TỤC 2 CẢM BIẾN THỜI GIAN THỰC <<<")
    print("Nhấn [Ctrl + C] bất kỳ lúc nào để dừng lại.\n")
    print(f"{'CẢM BIẾN TRÁI':<36} | {'CẢM BIẾN PHẢI':<36}")
    print("-" * 78)

    sample_count = 0
    try:
        while True:
            # Đo tuần tự với giãn cách 30ms chống dội sóng âm chéo
            dist_l, dist_r = sensor.read_both_cm(inter_sensor_delay=0.03)
            sample_count += 1

            txt_l = f"{dist_l:5.1f} cm" if dist_l is not None else "  None "
            txt_r = f"{dist_r:5.1f} cm" if dist_r is not None else "  None "

            bar_l = tao_thanh_do(dist_l, max_bar=12)
            bar_r = tao_thanh_do(dist_r, max_bar=12)

            warn_l = danh_gia_canh_bao(dist_l)
            warn_r = danh_gia_canh_bao(dist_r)

            # In kết quả dạng bảng sạch sẽ
            print(f"L: {txt_l} {bar_l} {warn_l:<10} | R: {txt_r} {bar_r} {warn_r:<10}")

            # Tần số quét 10 lần/giây (chu kỳ 100ms)
            time.sleep(0.07)

    except KeyboardInterrupt:
        print("\n\n>>> Đã dừng quét liên tục (Tổng số mẫu đã đo: {}).".format(sample_count))


def che_do_kiem_tra_on_dinh(sensor):
    """Chế độ 2: Kiểm tra độ ổn định và độ lệch chuẩn của cảm biến"""
    print("\n>>> BẮT ĐẦU ĐO 15 MẪU ĐỂ ĐÁNH GIÁ ĐỘ ỔN ĐỊNH VÀ SAI SỐ <<<")
    print("Vui lòng đặt vật cản cố định phía trước robot trong khoảng 20 - 50 cm...\n")

    time.sleep(1.0)
    samples_l = []
    samples_r = []

    for i in range(1, 16):
        l, r = sensor.read_both_cm(inter_sensor_delay=0.035)
        txt_l = f"{l:5.1f} cm" if l is not None else "Timeout"
        txt_r = f"{r:5.1f} cm" if r is not None else "Timeout"

        if l is not None: samples_l.append(l)
        if r is not None: samples_r.append(r)

        print(f"  Mẫu {i:02d}/15 -> Trái: {txt_l:<10} | Phải: {txt_r:<10}")
        time.sleep(0.1)

    print("\n" + "=" * 50)
    print("          KẾT QUẢ PHÂN TÍCH THỐNG KÊ")
    print("=" * 50)

    for side, data in [("CẢM BIẾN TRÁI", samples_l), ("CẢM BIẾN PHẢI", samples_r)]:
        print(f"\n* {side}:")
        if data:
            avg = sum(data) / len(data)
            min_v = min(data)
            max_v = max(data)
            variance = sum((x - avg) ** 2 for x in data) / len(data)
            std_dev = math.sqrt(variance)
            success_rate = (len(data) / 15.0) * 100.0

            print(f"   - Tỷ lệ bắt sóng thành công : {success_rate:.1f}% ({len(data)}/15 mẫu)")
            print(f"   - Khoảng cách trung bình    : {avg:.2f} cm")
            print(f"   - Giá trị nhỏ nhất / lớn nhất: {min_v:.1f} cm / {max_v:.1f} cm")
            print(f"   - Độ lệch chuẩn (Noise)    : ±{std_dev:.2f} cm")
            if std_dev < 1.0:
                print("   -> Đánh giá: RẤT TỐT (Tín hiệu sạch, ít nhiễu)")
            elif std_dev < 3.0:
                print("   -> Đánh giá: KHÁ (Phù hợp dùng cho điều hướng xe)")
            else:
                print("   -> Đánh giá: DAO ĐỘNG CAO (Nên kiểm tra dây cắm hoặc mạch phân áp)")
        else:
            print("   -> Không nhận được tín hiệu phản hồi nào! Kiểm tra dây TRIG/ECHO/VCC/GND.")

    print("\n" + "=" * 50)


def che_do_test_rieng_tung_ben(sensor):
    """Chế độ 3: Bắn xung riêng biệt từng bên để cô lập kiểm tra dây cáp"""
    print("\n>>> KIỂM TRA ĐỘC LẬP TỪNG BÊN CẢM BIẾN <<<")
    print("1. Kiểm tra Cảm biến TRÁI trong 5 giây...")
    for _ in range(10):
        d = sensor.read_left_cm()
        print(f"   [Chỉ phát Trái] Khoảng cách = {d} cm")
        time.sleep(0.3)

    print("\n2. Kiểm tra Cảm biến PHẢI trong 5 giây...")
    for _ in range(10):
        d = sensor.read_right_cm()
        print(f"   [Chỉ phát Phải] Khoảng cách = {d} cm")
        time.sleep(0.3)
    print("\nĐã hoàn thành kiểm tra riêng biệt.")


def main():
    in_tieu_de()
    sensor = DualUltrasonicSensor()

    try:
        while True:
            print("\nCHỌN CHẾ ĐỘ THỬ NGHIỆM:")
            print("  [1] Quét liên tục thời gian thực (Live Dashboard - 10Hz)")
            print("  [2] Đo kiểm 15 mẫu đánh giá độ ổn định và sai số")
            print("  [3] Thử nghiệm riêng biệt từng cảm biến (Cô lập lỗi dây)")
            print("  [4] Thoát chương trình")

            try:
                chon = input("\nNhập lựa chọn của bạn (1-4) [Mặc định 1]: ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not chon:
                chon = "1"

            if chon == "1":
                che_do_quet_lien_tuc(sensor)
            elif chon == "2":
                che_do_kiem_tra_on_dinh(sensor)
            elif chon == "3":
                che_do_test_rieng_tung_ben(sensor)
            elif chon == "4" or chon.lower() in ["q", "exit", "quit"]:
                break
            else:
                print("Lựa chọn không hợp lệ, vui lòng chọn từ 1 đến 4.")

    finally:
        print("\nĐang dọn dẹp và giải phóng tài nguyên chân GPIO...")
        sensor.cleanup()
        print("Đã thoát an toàn!")


if __name__ == "__main__":
    main()

