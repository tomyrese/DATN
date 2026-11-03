"""
Chương trình Chẩn Đoán Từng Chân GPIO Cụm Bánh Phải (Driver TB6612 - U_TB2)
Giúp kiểm tra chính xác tín hiệu mức logic HIGH/LOW trên từng chân vật lý bằng đồng hồ VOM hoặc mắt thường.

Cách chạy trên Raspberry Pi:
    python3 diagnose_right_pins.py
"""

import time
import sys

# Đảm bảo in tiếng Việt an toàn
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config import RIGHT_MOTORS_CONFIG, RIGHT_MOTORS_PHYSICAL_PINS

try:
    import RPi.GPIO as GPIO
    HAVE_RPI_GPIO = True
except (ImportError, RuntimeError):
    HAVE_RPI_GPIO = False


def in_tieu_de():
    print("=" * 75)
    print("   CHƯƠNG TRÌNH CHẨN ĐOÁN CHI TIẾT TỪNG CHÂN GPIO BÁNH PHẢI (U_TB2)   ")
    print("=" * 75)
    print("Bảng tra cứu chân vật lý và điểm đo trên mạch:")
    print(f"  [1] STBY_R : Pin {RIGHT_MOTORS_PHYSICAL_PINS['STBY_R']:>2} (GPIO {RIGHT_MOTORS_CONFIG['STBY_PIN']:>2}) -> Đo tại Pad 4 của Module TB6612 Phải")
    print(f"  [2] PWMA_R : Pin {RIGHT_MOTORS_PHYSICAL_PINS['PWMA_R']:>2} (GPIO {RIGHT_MOTORS_CONFIG['PWM_PIN']:>2}) -> Đo tại Pad 1 & Pad 7 của Module TB6612 Phải")
    print(f"  [3] AIN1_R : Pin {RIGHT_MOTORS_PHYSICAL_PINS['AIN1_R']:>2} (GPIO {RIGHT_MOTORS_CONFIG['IN1_PIN']:>2}) -> Đo tại Pad 3 & Pad 5 của Module TB6612 Phải")
    print(f"  [4] AIN2_R : Pin {RIGHT_MOTORS_PHYSICAL_PINS['AIN2_R']:>2} (GPIO {RIGHT_MOTORS_CONFIG['IN2_PIN']:>2}) -> Đo tại Pad 2 & Pad 6 của Module TB6612 Phải")
    print(f"  [*] VCC 5V : Pin  4               -> Đo tại Pad 10 của Module TB6612 Phải")
    print(f"  [*] VM 12V : Nguồn Pin 11.1V      -> Đo tại Pad 9 của Module TB6612 Phải")
    print("=" * 75)
    print()


def test_pin_holding(pin_name, bcm_pin, pad_name, duration=8):
    """Kéo một chân lên mức HIGH trong `duration` giây để đo đạc"""
    print(f"\n>>> ĐANG BẬT CHÂN {pin_name} (GPIO {bcm_pin} - {pad_name}) LÊN MỨC HIGH (3.3V) <<<")
    print(f"Vui lòng dùng đồng hồ VOM (thang đo DC 20V) đo giữa chân {pad_name} và GND.")
    print(f"-> Thời gian giữ mức HIGH: {duration} giây...")

    if not HAVE_RPI_GPIO:
        print("[MÔ PHỎNG] Bật HIGH thành công trên mô phỏng.")
        time.sleep(2)
        return

    try:
        GPIO.setup(bcm_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.output(bcm_pin, GPIO.HIGH)

        for remaining in range(duration, 0, -1):
            sys.stdout.write(f"\rĐang giữ HIGH... Còn {remaining}s | Điện áp đo được phải là ~3.3V ")
            sys.stdout.flush()
            time.sleep(1)

        print("\n-> Kết thúc. Kéo chân về mức LOW (0V).")
        GPIO.output(bcm_pin, GPIO.LOW)
    except Exception as e:
        print(f"\nLỗi khi xuất chân GPIO {bcm_pin}: {e}")


def force_run_all_high():
    """
    Cấp đồng thời mức HIGH cho tất cả các chân điều khiển:
    STBY = HIGH, IN1 = HIGH, IN2 = LOW, PWM = HIGH
    Nếu có nguồn 5V và 12V, động cơ BẮT BUỘC phải quay 100% công suất!
    """
    print("\n" + "=" * 75)
    print(">>> CHẾ ĐỘ KÍCH TỔNG LỰC TOÀN BỘ CHÂN BÁNH PHẢI (FORCE RUN 100%) <<<")
    print("=" * 75)
    print("Lệnh xuất tín hiệu:")
    print(f"  * STBY (GPIO {RIGHT_MOTORS_CONFIG['STBY_PIN']}) -> HIGH (3.3V)")
    print(f"  * IN1  (GPIO {RIGHT_MOTORS_CONFIG['IN1_PIN']}) -> HIGH (3.3V)")
    print(f"  * IN2  (GPIO {RIGHT_MOTORS_CONFIG['IN2_PIN']}) -> LOW  (0.0V)")
    print(f"  * PWM  (GPIO {RIGHT_MOTORS_CONFIG['PWM_PIN']}) -> HIGH (3.3V)")
    print("-" * 75)
    print(">>> ĐANG KÍCH TRỰC TIẾP TRONG 5 GIÂY! QUAN SÁT 2 BÁNH PHẢI... <<<")

    if not HAVE_RPI_GPIO:
        print("[MÔ PHỎNG] Chế độ mô phỏng hoàn tất.")
        return

    stby = RIGHT_MOTORS_CONFIG["STBY_PIN"]
    in1  = RIGHT_MOTORS_CONFIG["IN1_PIN"]
    in2  = RIGHT_MOTORS_CONFIG["IN2_PIN"]
    pwm  = RIGHT_MOTORS_CONFIG["PWM_PIN"]

    try:
        GPIO.setup(stby, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(in1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(in2, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pwm, GPIO.OUT, initial=GPIO.LOW)

        GPIO.output(stby, GPIO.HIGH)
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(pwm, GPIO.HIGH)

        for remaining in range(5, 0, -1):
            sys.stdout.write(f"\rThời gian còn: {remaining}s... ")
            sys.stdout.flush()
            time.sleep(1)

        print("\n-> Hết thời gian. Tắt toàn bộ chân.")
    finally:
        try:
            GPIO.output(pwm, GPIO.LOW)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(stby, GPIO.LOW)
        except Exception:
            pass


def main():
    in_tieu_de()

    if HAVE_RPI_GPIO:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

    try:
        while True:
            print("\nDANH MỤC THỬ NGHIỆM CHẨN ĐOÁN:")
            print("  1. Kích tổng lực toàn bộ (STBY=HIGH, IN1=HIGH, PWM=HIGH) trong 5 giây")
            print("  2. Giữ chân STBY_R (GPIO 20) mức HIGH 8 giây để đo VOM tại Pad 4")
            print("  3. Giữ chân PWMA_R (GPIO 13) mức HIGH 8 giây để đo VOM tại Pad 1 & 7")
            print("  4. Giữ chân AIN1_R (GPIO 26) mức HIGH 8 giây để đo VOM tại Pad 3 & 5")
            print("  5. Giữ chân AIN2_R (GPIO 19) mức HIGH 8 giây để đo VOM tại Pad 2 & 6")
            print("  6. Đổi chiều quay: (IN1=LOW, IN2=HIGH, PWM=HIGH, STBY=HIGH) 5 giây")
            print("  7. Thoát")

            choice = input("\nChọn bài test (1-7): ").strip()

            if choice == '1':
                force_run_all_high()
            elif choice == '2':
                test_pin_holding("STBY_R", RIGHT_MOTORS_CONFIG["STBY_PIN"], "Pad 4 (STBY)")
            elif choice == '3':
                test_pin_holding("PWMA_R", RIGHT_MOTORS_CONFIG["PWM_PIN"], "Pad 1 & 7 (PWM)")
            elif choice == '4':
                test_pin_holding("AIN1_R", RIGHT_MOTORS_CONFIG["IN1_PIN"], "Pad 3 & 5 (AIN1/BIN1)")
            elif choice == '5':
                test_pin_holding("AIN2_R", RIGHT_MOTORS_CONFIG["IN2_PIN"], "Pad 2 & 6 (AIN2/BIN2)")
            elif choice == '6':
                if HAVE_RPI_GPIO:
                    stby = RIGHT_MOTORS_CONFIG["STBY_PIN"]
                    in1  = RIGHT_MOTORS_CONFIG["IN1_PIN"]
                    in2  = RIGHT_MOTORS_CONFIG["IN2_PIN"]
                    pwm  = RIGHT_MOTORS_CONFIG["PWM_PIN"]
                    print("\n-> Đang đảo chiều (IN1=LOW, IN2=HIGH)...")
                    GPIO.output(stby, GPIO.HIGH)
                    GPIO.output(in1, GPIO.LOW)
                    GPIO.output(in2, GPIO.HIGH)
                    GPIO.output(pwm, GPIO.HIGH)
                    time.sleep(5)
                    GPIO.output(pwm, GPIO.LOW)
                    GPIO.output(in2, GPIO.LOW)
                    GPIO.output(stby, GPIO.LOW)
                    print("-> Dừng.")
            elif choice == '7':
                print("Kết thúc chẩn đoán.")
                break
            else:
                print("Lựa chọn không hợp lệ.")
    finally:
        if HAVE_RPI_GPIO:
            try:
                GPIO.cleanup()
            except Exception:
                pass


if __name__ == "__main__":
    main()

