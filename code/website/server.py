"""
Web Server điều khiển Robot 4WD Raspberry Pi 4 qua giao diện trình duyệt.
Sử dụng thư viện chuẩn của Python (http.server) - chạy ngay trên Pi 4 không cần cài đặt thêm thư viện!
Tích hợp API điều khiển động cơ và phục vụ file giao diện Web.
"""

import sys
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Đảm bảo in UTF-8 an toàn
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Thêm đường dẫn thư mục python vào sys.path để import motor_controller
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_CODE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "python"))
if PYTHON_CODE_DIR not in sys.path:
    sys.path.insert(0, PYTHON_CODE_DIR)

try:
    from motor_controller import TB6612LeftMotors
    left_motors = TB6612LeftMotors()
except Exception as e:
    print(f"[CẢNH BÁO] Không thể tải motor_controller: {e}")
    left_motors = None


class RobotWebHandler(SimpleHTTPRequestHandler):
    """Xử lý yêu cầu HTTP phục vụ Website và API REST điều khiển Robot"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=CURRENT_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        # API Điều khiển 2 Bánh Trái: /api/motor/left?action=forward&speed=60
        if parsed.path == "/api/motor/left":
            params = urllib.parse.parse_qs(parsed.query)
            action = params.get("action", ["stop"])[0].lower()
            speed = int(params.get("speed", ["60"])[0])

            status = "ok"
            msg = f"Lệnh bánh trái: {action} ({speed}%)"

            if left_motors:
                if action == "forward":
                    left_motors.forward(speed)
                elif action == "reverse":
                    left_motors.reverse(speed)
                elif action == "brake":
                    left_motors.brake()
                elif action == "stop":
                    left_motors.stop()
                elif action == "enable":
                    left_motors.enable()
                elif action == "disable":
                    left_motors.disable()
                else:
                    status = "error"
                    msg = f"Hành động không xác định: {action}"
            else:
                msg = "[Giả lập] Không có driver"

            response = {
                "status": status,
                "message": msg,
                "action": action,
                "speed": speed,
                "direction": left_motors.current_direction if left_motors else "UNKNOWN",
                "enabled": left_motors.is_enabled if left_motors else False
            }
            self._send_json(response)
            return

        # API Trạng thái hệ thống: /api/status
        elif parsed.path == "/api/status":
            response = {
                "status": "online",
                "system": "Raspberry Pi 4 - Carrier Board 1-Layer",
                "left_motors": {
                    "direction": left_motors.current_direction if left_motors else "N/A",
                    "speed": left_motors.current_speed if left_motors else 0,
                    "enabled": left_motors.is_enabled if left_motors else False
                }
            }
            self._send_json(response)
            return

        # Phục vụ file tĩnh (HTML, CSS, JS)
        super().do_GET()

    def _send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        """Tắt log mặc định quá dài dòng, chỉ in ngắn gọn"""
        pass


def run_server(port=8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, RobotWebHandler)
    print("=" * 65)
    print(f"   ROBOT CARRIER WEB CONTROL SERVER IS RUNNING ON PORT {port}   ")
    print("=" * 65)
    print(f" Truy cập giao diện điều khiển robot qua trình duyệt:")
    print(f"   * Trên máy tính:  http://localhost:{port}")
    print(f"   * Từ điện thoại:  http://<IP_RASPBERRY_PI>:{port}")
    print(" Nhấn Ctrl+C để dừng máy chủ.")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nĐang tắt máy chủ...")
    finally:
        if left_motors:
            left_motors.cleanup()
        httpd.server_close()
        print("Máy chủ đã dừng an toàn.")


if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
