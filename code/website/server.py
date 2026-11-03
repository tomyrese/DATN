"""
Máy chủ Dịch vụ Robot Phục Vụ Thông Minh "Bé Robi" - TTTM MegaMall
Phiên bản Giao diện Sáng Thân Thiện Người Dùng Phổ Thông (Non-tech)
Hỗ trợ định tuyến đa trang URL: /home, /nhan-hang, /map, /chat, /dieu-hanh, /cai-dat
Tích hợp Rào chắn Bảo mật AI & Phân quyền Truy cập Dữ liệu theo Vai trò
"""

import sys
import os
import json
import time
import math
import secrets
import datetime
import urllib.parse
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

# Đảm bảo in UTF-8 an toàn
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
MISSIONS_FILE = os.path.join(DATA_DIR, "missions.json")
AI_CONFIG_FILE = os.path.join(DATA_DIR, "ai_config.json")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")

def add_system_log(category, message, level="INFO"):
    try:
        logs = load_json(LOGS_FILE, [])
        now = datetime.datetime.now().strftime("%H:%M:%S")
        logs.insert(0, {
            "id": f"LOG-{int(time.time()*1000)%1000000:06d}",
            "time": now,
            "category": category,
            "message": message,
            "level": level
        })
        save_json(LOGS_FILE, logs[:100])
    except Exception:
        pass

# Kết nối Hardware motor controller nếu có
PYTHON_CODE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "python"))
if PYTHON_CODE_DIR not in sys.path:
    sys.path.insert(0, PYTHON_CODE_DIR)

try:
    from motor_controller import TB6612LeftMotors
    left_motors = TB6612LeftMotors()
except Exception:
    left_motors = None

# Trạng thái Robot thân thiện người dùng
robot_state = {
    "name": "Bé Robi",
    "status_text": "Đang sẵn sàng phục vụ",
    "direction": "Đứng yên",
    "speed": 60,
    "battery_percent": 88,
    "battery_voltage": 11.85,
    "emotion": "happy",          # happy, laughing, waving, thinking, talking, love
    "compartment_1": "ĐANG KHÓA",
    "compartment_2": "ĐANG KHÓA",
    "current_location": "Sảnh Trung Tâm (Tầng 1)",
    "obstacle_status": "An toàn",
    "obstacle_cm": 42.5,
    "map_x": 480.0,
    "map_y": 280.0,
    "heading": 0.0,
    "target_store": None,
    "last_command_time": time.time()
}

# Tiện ích đọc / ghi JSON
def load_json(filepath, default):
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def save_json(filepath, data):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

active_sessions = load_json(SESSIONS_FILE, {})

# ========================================================
# RÀO CHẮN BẢO MẬT & PHÂN QUYỀN DỮ LIỆU CHO AI (GUARDRAILS)
# ========================================================
INJECTION_KEYWORDS = [
    "bỏ qua các chỉ dẫn", "ignore instructions", "jailbreak", "đóng vai kẻ tấn công",
    "cho tôi xem mật khẩu", "in api key", "dump database", "hack", "xóa dữ liệu",
    "lộ danh sách người dùng", "thông tin tài khoản admin"
]

def check_ai_security(query):
    """Kiểm duyệt ngăn chặn Prompt Injection và bảo vệ dữ liệu nội bộ"""
    q_lower = query.lower()
    for kw in INJECTION_KEYWORDS:
        if kw in q_lower:
            return False, "Dạ em Robi chỉ hỗ trợ thông tin hướng dẫn mua sắm, ẩm thực và hỗ trợ nhận hàng tại MegaMall thôi ạ. Em không được phép thảo luận hay chia sẻ các thông tin kỹ thuật hoặc dữ liệu nội bộ đâu nhé anh/chị!"
    return True, ""

def build_scoped_ai_context(role, query):
    """Xây dựng phạm vi dữ liệu được phép nhìn thấy cho AI tùy theo vai trò"""
    # 1. Dữ liệu công cộng (Public Knowledge) - Cả 3 vai trò đều xem được
    public_mall_info = (
        "- Tầng B1: Siêu thị WinMart+, Nhà thuốc An Khang, Tủ gửi đồ tự động và Bãi đỗ xe ô tô/xe máy.\n"
        "- Tầng 1: Sảnh chính, Thời trang quốc tế Zara, Uniqlo, Quầy Cà phê Highlands Coffee, Quầy dịch vụ khách hàng.\n"
        "- Tầng 2: Mỹ phẩm Innisfree, Guardian, Trà sữa Phúc Long Tea, Phụ kiện thời trang.\n"
        "- Tầng 3: Khu vui chơi trẻ em TiNiWorld, Thời trang KidsPlaza, Nhà sách Fahasa, Lego Store.\n"
        "- Tầng 4: Thiên đường ẩm thực: Lẩu Haidilao, Buffet King BBQ, Gà rán KFC, Pizza 4P's, Trà hoa quả tươi.\n"
        "- Tầng 5: Cụm rạp chiếu phim CGV Cinemas IMAX, Khu trò chơi DreamGames.\n"
        "- Tiện ích: Nhà vệ sinh (WC) ở cuối hành lang mỗi tầng, thang máy cạnh quầy Highlands Coffee."
    )

    # 2. Xử lý theo từng vai trò
    if role == "guest":
        # Khách hàng CHỈ được xem thông tin công cộng.
        # Nếu khách hỏi về đơn hàng mà CÓ cung cấp mã OTP 6 số: tra đúng đơn đó.
        import re
        otp_match = re.search(r'\b\d{6}\b', query)
        order_info = ""
        if otp_match:
            otp = otp_match.group(0)
            missions = load_json(MISSIONS_FILE, [])
            matched = next((m for m in missions if m.get("otp") == otp), None)
            if matched:
                order_info = f"\nThông tin đơn hàng của quý khách: Món hàng '{matched.get('item')}' từ '{matched.get('store')}' đang ở trạng thái '{matched.get('status')}'. Khi robot đến vị trí, quý khách nhập mã {otp} để mở hộc số {matched.get('compartment')} nhé ạ!"
            else:
                order_info = f"\nDạ mã OTP {otp} hiện không tìm thấy đơn hàng nào đang chờ giao. Quý khách vui lòng kiểm tra lại tin nhắn hoặc liên hệ quầy dịch vụ Tầng 1 ạ."
        else:
            if any(k in query.lower() for k in ["đơn hàng", "món của tôi", "đồ ăn của tôi", "giao đến đâu rồi"]):
                order_info = "\nDạ để kiểm tra đơn hàng, quý khách vui lòng đọc giúp em mã OTP 6 chữ số mà quý khách nhận được qua tin nhắn nhé ạ!"

        return f"THÔNG TIN MEGA MALL DÀNH CHO KHÁCH HÀNG:\n{public_mall_info}{order_info}\n(LƯU Ý: Không bao giờ tiết lộ số điện thoại hoặc tên của khách hàng khác)."

    elif role == "manager":
        # Nhân viên Quản lý: Được xem tóm tắt các đơn hàng đang hoạt động trong TTTM
        missions = load_json(MISSIONS_FILE, [])
        active_list = [f"- Đơn {m.get('id')}: {m.get('store')} gửi {m.get('customer')} ({m.get('destination')}), Hộc #{m.get('compartment')}, Trạng thái: {m.get('status')}" for m in missions if m.get('status') in ['EN_ROUTE', 'ARRIVED', 'PENDING']]
        summary = "\n".join(active_list) if active_list else "Hiện không có đơn giao hàng nào đang chờ."
        return f"THÔNG TIN VẬN HÀNH DÀNH CHO NHÂN VIÊN QUẢN LÝ:\n{public_mall_info}\n\nDANH SÁCH ĐƠN HÀNG ĐANG ĐIỀU PHỐI:\n{summary}"

    elif role == "admin":
        # Quản trị viên: Có góc nhìn toàn diện
        users = load_json(USERS_FILE, [])
        mgr_count = len([u for u in users if u.get("role") == "manager"])
        return f"THÔNG TIN QUẢN TRỊ VIÊN:\n{public_mall_info}\n\nTổng số nhân viên quản lý đang hoạt động: {mgr_count} người. Pin Robot: {robot_state['battery_percent']}%. Vị trí: {robot_state['current_location']}."

    return public_mall_info

def generate_robi_reply(role, query):
    """Trợ lý Bé Robi phản hồi 100% tiếng Việt thân thiện, đáng yêu, lễ phép"""
    is_safe, refusal = check_ai_security(query)
    if not is_safe:
        return {"reply": refusal, "emotion": "thinking"}

    q = query.lower().strip()

    # Chào hỏi
    if any(k in q for k in ["chào", "hello", "hi", "bạn tên gì", "em tên gì", "bé là ai", "ai đấy"]):
        return {
            "reply": "Dạ em chào anh/chị ạ! Em là Bé Robi - robot phục vụ đáng yêu của MegaMall. Em có thể chỉ đường tới các gian hàng, tư vấn món ăn ngon và mang đồ ăn đến tận bàn cho anh/chị. Em có thể giúp gì cho anh/chị hôm nay ạ?",
            "emotion": "waving"
        }

    # Hướng dẫn nhận hàng
    if any(k in q for k in ["nhận hàng", "mở hộc", "lấy đồ", "mở tủ", "mã otp", "nhập mã"]):
        return {
            "reply": "Dạ để nhận đồ, anh/chị chỉ cần chọn mục 'Nhận Đồ Ăn / Hàng Hóa' trên màn hình của em, sau đó bấm 6 số mã OTP mà quán đã gửi. Hộc tủ tương ứng sẽ tự động bật mở ra ngay ạ!",
            "emotion": "happy"
        }

    # Ẩm thực, ăn uống
    if any(k in q for k in ["ăn", "uống", "đói", "lẩu", "haidilao", "kfc", "cà phê", "highlands", "trà sữa", "phúc long"]):
        return {
            "reply": "Dạ ở MegaMall có rất nhiều món ngon luôn ạ! Tầng 4 có đại tiệc Lẩu Haidilao múa mì siêu vui và khu ẩm thực Á - Âu. Còn nếu anh/chị muốn thưởng thức cà phê thì ghé Highlands Coffee ở ngay Tầng 1 cạnh thang máy, hoặc trà sữa Phúc Long ở Tầng 2 nhé ạ!",
            "emotion": "laughing"
        }

    # Mua sắm, quần áo, thời trang
    if any(k in q for k in ["mua sắm", "quần áo", "thời trang", "zara", "uniqlo", "váy", "mỹ phẩm"]):
        return {
            "reply": "Dạ khu mua sắm thời trang hot nhất nằm ở Tầng 1 với hai cửa hàng siêu to là Zara và Uniqlo ạ. Nếu anh/chị muốn tìm mỹ phẩm dưỡng da thì Tầng 2 có Innisfree và Guardian luôn sẵn sàng phục vụ ạ!",
            "emotion": "talking"
        }

    # Rạp chiếu phim
    if any(k in q for k in ["phim", "cgv", "cinema", "rạp"]):
        return {
            "reply": "Dạ rạp chiếu phim CGV Cinemas IMAX nằm trọn vẹn tại Tầng 5 ạ. Anh/chị có thể đi thang máy trung tâm lên thẳng Tầng 5 để mua vé và thưởng thức bắp rang bơ thơm phức nhé!",
            "emotion": "happy"
        }

    # Trẻ em
    if any(k in q for k in ["trẻ em", "em bé", "tiniworld", "vui chơi", "đồ chơi"]):
        return {
            "reply": "Dạ cả thiên đường vui chơi cho các bé nằm ở Tầng 3 ạ! Ở đó có khu TiNiWorld nhiều trò chơi vận động, nhà sách Fahasa và cửa hàng xếp hình Lego Store nữa ạ.",
            "emotion": "waving"
        }

    # Nhà vệ sinh, thang máy, tiện ích
    if any(k in q for k in ["nhà vệ sinh", "toilet", "wc", "thang máy", "thang cuốn", "atm"]):
        return {
            "reply": "Dạ nhà vệ sinh (WC) nằm ở cuối hành lang phía Đông và Tây của tất cả các tầng ạ. Thang máy trung tâm thì ở ngay cạnh quầy Highlands Coffee Tầng 1. Anh/chị cần em Robi dẫn đường tới đó không ạ?",
            "emotion": "happy"
        }

    # Tình trạng của Robi
    if any(k in q for k in ["khỏe không", "pin", "robot", "mệt không", "đang ở đâu"]):
        return {
            "reply": f"Dạ em Robi đang tràn đầy năng lượng luôn ạ! Mức pin hiện tại đạt {robot_state['battery_percent']}%, hai khoang chứa đồ đã sẵn sàng và em đang đứng tại {robot_state['current_location']} để chờ đón quý khách đây ạ!",
            "emotion": "love"
        }

    # Câu hỏi về đơn hàng của khách (kiểm tra OTP)
    import re
    otp_found = re.search(r'\b\d{6}\b', q)
    if otp_found:
        otp = otp_found.group(0)
        missions = load_json(MISSIONS_FILE, [])
        m = next((item for item in missions if item.get("otp") == otp), None)
        if m:
            return {
                "reply": f"Dạ em tìm thấy đơn rồi ạ! Món '{m.get('item')}' do quán '{m.get('store')}' gửi cho anh/chị đang ở trạng thái '{m.get('status')}'. Khi em Robi tới bàn, anh/chị chỉ cần nhập lại mã {otp} để hộc số {m.get('compartment')} mở ra nhé!",
                "emotion": "happy"
            }
        else:
            return {
                "reply": f"Dạ em đã kiểm tra mã {otp} nhưng chưa thấy có đơn hàng nào khớp trên hệ thống. Anh/chị kiểm tra lại tin nhắn hoặc hỏi quầy thu ngân giúp em nhé ạ!",
                "emotion": "thinking"
            }

    # Phản hồi mặc định nếu chưa hiểu rõ
    return {
        "reply": f"Dạ em Robi đã nghe câu hỏi: '{query}' rồi ạ! Anh/chị có thể hỏi em về gian hàng mua sắm, các quán ăn ngon ở Tầng 4, rạp phim Tầng 5 hoặc bấm vào các nút gợi ý bên dưới để em hướng dẫn nhanh nhé ạ!",
        "emotion": "talking"
    }


# ========================================================
# HTTP REQUEST HANDLER PHỤC VỤ ĐA TRANG & API
# ========================================================
class RobiServerHandler(SimpleHTTPRequestHandler):

    def address_string(self):
        # Tăng tốc độ phản hồi bằng cách tắt DNS lookup ngược cho localhost
        return self.client_address[0]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=CURRENT_DIR, **kwargs)

    def _send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                raw_data = self.rfile.read(content_length).decode("utf-8")
                return json.loads(raw_data)
        except Exception:
            pass
        return {}

    def _get_auth_user(self):
        auth_header = self.headers.get("Authorization", "")
        token = ""
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        elif hasattr(self, "_current_body") and isinstance(self._current_body, dict) and self._current_body.get("token"):
            token = str(self._current_body.get("token", "")).strip()
        else:
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            token = qs.get("token", [""])[0]

        if token and token in active_sessions:
            return active_sessions[token]
        return None

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # ----------------------------------------------------
        # 1. ĐỊNH TUYẾN CÁC TRANG WEB SẠCH (Clean Web Routes)
        # ----------------------------------------------------
        PAGE_ROUTES = [
            "/", "/home", "/trang-chu",
            "/nhan-hang",
            "/map", "/ban-do",
            "/chat", "/tro-chuyen",
            "/don-hang", "/tao-don",
            "/dieu-hanh", "/quan-ly",
            "/logs", "/nhat-ky", "/camera",
            "/cai-dat", "/he-thong"
        ]

        if path in PAGE_ROUTES:
            # Phục vụ index.html cho toàn bộ các route này (SPA Client Router)
            index_file_path = os.path.join(CURRENT_DIR, "index.html")
            try:
                with open(index_file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            except Exception as e:
                self.send_error(500, f"Lỗi đọc index.html: {e}")
                return

        # ----------------------------------------------------
        # 2. CÁC API DỮ LIỆU
        # ----------------------------------------------------
        if path in ["/api/status", "/api/telemetry", "/api/state"]:
            # Giả lập biến động nhẹ
            dist = round(40.0 + (time.time() % 6) * 1.5, 1)
            robot_state["obstacle_cm"] = dist
            robot_state["obstacle_status"] = "Nguy hiểm" if dist < 15 else ("Cảnh báo" if dist < 30 else "An toàn")

            missions = load_json(MISSIONS_FILE, [])
            pending_count = len([m for m in missions if m.get("status") in ["EN_ROUTE", "ARRIVED", "PENDING"]])

            resp_data = dict(robot_state)
            resp_data.update({
                "status": "online",
                "robot": dict(robot_state),
                "active_missions": pending_count,
                "server_time": datetime.datetime.now().strftime("%H:%M:%S")
            })
            self._send_json(resp_data)
            return

        elif path == "/api/auth/me":
            user = self._get_auth_user()
            if user:
                self._send_json({"authenticated": True, "user": user})
            else:
                self._send_json({"authenticated": False, "role": "guest", "fullName": "Khách Vãng Lai"})
            return

        elif path == "/api/missions":
            user = self._get_auth_user()
            missions = load_json(MISSIONS_FILE, [])

            # Nếu là Khách hàng: KHÔNG trả về số điện thoại và mã OTP của khách khác (Bảo vệ thông tin cá nhân)
            if not user or user.get("role") == "guest":
                sanitized = []
                for m in missions:
                    sanitized.append({
                        "id": m.get("id"),
                        "store": m.get("store"),
                        "destination": m.get("destination"),
                        "status": m.get("status"),
                        "compartment": m.get("compartment"),
                        "item": m.get("item")
                        # Ẩn customer, phone và otp đối với khách vãng lai
                    })
                self._send_json({"missions": sanitized})
            else:
                # Quản lý & Admin được xem đầy đủ để điều phối
                self._send_json({"missions": missions})
            return

        elif path in ["/api/users", "/api/admin/users"]:
            user = self._get_auth_user()
            if not user or user.get("role") != "admin":
                self._send_json({"error": "Chỉ Quản trị viên mới được xem danh sách nhân viên."}, 403)
                return
            users = load_json(USERS_FILE, [])
            sanitized = [{k: v for k, v in u.items() if k != "password"} for u in users]
            self._send_json({"users": sanitized})
            return

        elif path == "/api/logs":
            logs = load_json(LOGS_FILE, [])
            self._send_json({"logs": logs})
            return

        elif path == "/api/ai/config":
            user = self._get_auth_user()
            config = load_json(AI_CONFIG_FILE, {})
            if not user or user.get("role") != "admin":
                config["apiKey"] = "********" if config.get("apiKey") else ""
            self._send_json(config)
            return

        # Phục vụ file tĩnh thông thường (style.css, app.js, ảnh...)
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()
        self._current_body = body

        # 1. Đăng nhập
        if path == "/api/auth/login":
            username = body.get("username", "").strip()
            password = body.get("password", "").strip()

            users = load_json(USERS_FILE, [])
            matched = next((u for u in users if u.get("username") == username and u.get("password") == password), None)

            if matched:
                if not matched.get("isActive", True):
                    self._send_json({"error": "Tài khoản của bạn đang tạm khóa. Vui lòng liên hệ Quản trị viên."}, 403)
                    return
                token = secrets.token_hex(20)
                session = {
                    "id": matched.get("id"),
                    "username": matched.get("username"),
                    "role": matched.get("role"),
                    "fullName": matched.get("fullName"),
                    "token": token
                }
                active_sessions[token] = session
                save_json(SESSIONS_FILE, active_sessions)
                add_system_log("HỆ THỐNG", f"{matched.get('fullName')} đăng nhập thành công.", "SUCCESS")
                self._send_json({"status": "success", "success": True, "message": f"Chào mừng {matched.get('fullName')}!", "token": token, "user": session})
            else:
                self._send_json({"error": "Tên đăng nhập hoặc mật khẩu không chính xác.", "success": False, "message": "Tên đăng nhập hoặc mật khẩu không đúng."}, 401)
            return

        # 2. Đăng xuất
        elif path == "/api/auth/logout":
            token = body.get("token") or self._get_auth_token_from_header()
            if token in active_sessions:
                del active_sessions[token]
                save_json(SESSIONS_FILE, active_sessions)
            self._send_json({"status": "success", "message": "Đã đăng xuất thành công."})
            return

        # 3. Trò chuyện Trí tuệ Nhân tạo cùng Bé Robi
        elif path == "/api/ai/chat":
            user_msg = (body.get("message") or body.get("query") or "").strip()
            if not user_msg:
                self._send_json({"error": "Tin nhắn không được để trống.", "success": False}, 400)
                return

            user = self._get_auth_user()
            role = body.get("role") or (user.get("role") if user else "guest")

            # Kiểm duyệt bảo mật query
            is_safe, refusal = check_ai_security(user_msg)
            if not is_safe:
                self._send_json({"status": "refused", "success": True, "reply": refusal, "emotion": "thinking"})
                return

            config = load_json(AI_CONFIG_FILE, {})
            api_key = config.get("apiKey", "").strip()
            provider = config.get("provider", "gemini")

            # Nếu có cấu hình Cloud AI API
            if api_key and provider in ["gemini", "openai"]:
                try:
                    scoped_context = build_scoped_ai_context(role, user_msg)
                    system_prompt = (
                        "Bạn là Bé Robi, robot phục vụ thông minh, đáng yêu tại TTTM MegaMall. "
                        "Luôn dùng 100% tiếng Việt thân thiện, vui vẻ, xưng hô 'em' hoặc 'Robi' và gọi khách là 'anh/chị' hoặc 'quý khách'. "
                        "Trả lời súc tích trong 2 đến 3 câu. "
                        f"DỮ LIỆU ĐƯỢC PHÉP TRUY CẬP CHO VAI TRÒ {role.upper()}:\n{scoped_context}"
                    )
                    if provider == "gemini":
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.get('model', 'gemini-1.5-flash')}:generateContent?key={api_key}"
                        payload = {"contents": [{"parts": [{"text": f"HƯỚNG DẪN: {system_prompt}\n\nCÂU HỎI: {user_msg}\n\nROBI TRẢ LỜI:"}]}]}
                        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
                        with urllib.request.urlopen(req, timeout=7) as res:
                            data = json.loads(res.read().decode("utf-8"))
                            ans = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                            robot_state["emotion"] = "happy"
                            self._send_json({"status": "success", "success": True, "reply": ans, "emotion": "happy"})
                            return
                except Exception as e:
                    print(f"[AI] Gọi cloud thất bại: {e}. Chuyển sang phản hồi nội bộ.")

            # Trợ lý nội bộ Bé Robi (Hoạt động ổn định 100% không lo rớt mạng)
            res = generate_robi_reply(role, user_msg)
            robot_state["emotion"] = res.get("emotion", "happy")
            self._send_json({"status": "success", "success": True, "reply": res["reply"], "emotion": res["emotion"]})
            return

        # 4. Mở hộc nhận hàng bằng mã OTP (Dành cho khách hàng)
        elif path == "/api/missions/unlock":
            input_otp = str(body.get("otp", "")).strip()
            if not input_otp or len(input_otp) != 6:
                self._send_json({"error": "Vui lòng nhập đúng 6 số mã OTP.", "success": False}, 400)
                return

            missions = load_json(MISSIONS_FILE, [])
            matched = next((m for m in missions if m.get("otp") == input_otp and m.get("status") in ["EN_ROUTE", "ARRIVED", "PENDING"]), None)

            if matched:
                matched["status"] = "COMPLETED"
                matched["completedAt"] = datetime.datetime.now().isoformat()
                save_json(MISSIONS_FILE, missions)

                comp = matched.get("compartment", 1)
                if comp == 1: robot_state["compartment_1"] = "ĐÃ MỞ"
                else: robot_state["compartment_2"] = "ĐÃ MỞ"
                robot_state["emotion"] = "laughing"

                add_system_log("HỘC CHỨA", f"Khách nhập đúng mã PIN {input_otp}, mở hộc {comp} ({matched.get('item')}).", "SUCCESS")

                self._send_json({
                    "status": "success",
                    "success": True,
                    "message": f"Mã chính xác! Khoang số {comp} đã mở. Em Robi chúc quý khách nhận đồ vui vẻ ạ!",
                    "compartment": comp,
                    "store": matched.get("store"),
                    "item": matched.get("item")
                })
            else:
                self._send_json({"error": "Mã OTP không đúng hoặc đơn hàng đã nhận rồi ạ.", "success": False, "message": "Mã PIN không đúng hoặc đơn hàng đã hoàn tất trước đó."}, 404)
            return

        # 5. Tạo đơn giao hàng mới (Quản lý)
        elif path in ["/api/missions/create", "/api/missions"]:
            user = self._get_auth_user()
            if not user or user.get("role") not in ["admin", "manager"]:
                self._send_json({"error": "Chỉ Quản lý mới có quyền tạo đơn giao hàng."}, 403)
                return

            store = body.get("store", "").strip()
            destination = body.get("destination", "").strip()
            customer = body.get("customer", "").strip()
            item = body.get("item", "").strip()
            compartment = int(body.get("compartment", 1))

            if not store or not destination or not item:
                self._send_json({"error": "Vui lòng nhập đầy đủ gian hàng, nơi nhận và món đồ."}, 400)
                return

            otp = str(secrets.randbelow(900000) + 100000)
            missions = load_json(MISSIONS_FILE, [])

            new_m = {
                "id": f"ĐƠN-{len(missions)+1:03d}",
                "store": store,
                "destination": destination,
                "customer": customer or "Khách tại bàn",
                "phone": body.get("phone", ""),
                "item": item,
                "otp": otp,
                "compartment": compartment,
                "status": "EN_ROUTE",
                "createdAt": datetime.datetime.now().strftime("%H:%M - %d/%m/%Y")
            }
            missions.insert(0, new_m)
            save_json(MISSIONS_FILE, missions)

            if compartment == 1: robot_state["compartment_1"] = "ĐANG KHÓA"
            else: robot_state["compartment_2"] = "ĐANG KHÓA"

            add_system_log("GIAO HÀNG", f"Cửa hàng '{store}' tạo đơn #{new_m['id']}: {item} -> {destination} (Hộc {compartment}, Mã PIN: {otp}).", "INFO")

            self._send_json({"status": "success", "success": True, "message": f"Đã giao việc cho Robi! Mã nhận đồ: {otp}", "mission": new_m})
            return

        # 6. Điều khiển di chuyển Robot & Mở hộc khẩn cấp
        elif path in ["/api/control", "/api/motor/control"]:
            user = self._get_auth_user()
            if not user or user.get("role") not in ["admin", "manager"]:
                self._send_json({"error": "Chỉ Quản lý mới có quyền điều khiển di chuyển robot."}, 403)
                return

            action = body.get("action", "stop").lower()

            if action == "unlock_compartment":
                comp = int(body.get("compartment", 1))
                if comp == 1: robot_state["compartment_1"] = "ĐÃ MỞ"
                else: robot_state["compartment_2"] = "ĐÃ MỞ"
                add_system_log("HỘC CHỨA", f"Nhân viên mở khẩn cấp hộc chứa số {comp}.", "WARNING")
                self._send_json({"status": "ok", "success": True, "message": f"Đã mở khẩn cấp hộc {comp}."})
                return

            # Điều hướng tự động tới gian hàng đích
            if action == "navigate_to":
                target = body.get("target", "Highlands Coffee")
                target_coords = body.get("coords")
                if not target_coords:
                    STORE_COORDS = {
                        "Highlands Coffee": (170, 125),
                        "Phúc Long Tea": (170, 320),
                        "Zara Quốc Tế": (770, 125),
                        "Uniqlo LifeWear": (770, 315),
                        "Siêu Thị MegaMarket": (770, 490),
                        "Quầy Lễ Tân": (480, 475),
                        "Bàn A-01": (340, 160),
                        "Bàn A-02": (440, 160),
                        "Bàn A-03": (540, 160),
                        "Bàn A-10": (340, 320),
                        "Bàn A-11": (440, 320),
                        "Bàn A-12": (540, 320),
                        "Trạm Sạc": (480, 280)
                    }
                    target_coords = STORE_COORDS.get(target, (480, 280))
                
                tx, ty = target_coords
                robot_state["target_store"] = target
                robot_state["map_x"] = float(tx)
                robot_state["map_y"] = float(ty)
                robot_state["current_location"] = f"Cạnh {target}"
                robot_state["direction"] = f"Đến {target}"
                add_system_log("ĐIỀU HƯỚNG", f"Bé Robi hoàn thành lộ trình di chuyển tới: {target}.", "SUCCESS")
                self._send_json({
                    "status": "ok",
                    "success": True,
                    "direction": robot_state["direction"],
                    "map_x": tx,
                    "map_y": ty,
                    "heading": robot_state["heading"],
                    "location": robot_state["current_location"]
                })
                return

            speed = int(body.get("speed", robot_state["speed"]))
            speed = max(20, min(100, speed))
            robot_state["speed"] = speed

            dir_map = {
                "forward": "Đang tiến",
                "backward": "Đang lùi",
                "reverse": "Đang lùi",
                "turn_left": "Đang rẽ trái",
                "turn_right": "Đang rẽ phải",
                "strafe_left": "Dạt sang trái",
                "strafe_right": "Dạt sang phải",
                "stop": "Đứng yên",
                "brake": "Đã phanh"
            }
            robot_state["direction"] = dir_map.get(action, "Đang di chuyển")

            # Cập nhật vị trí và góc quay hướng trên bản đồ 2D siêu thị
            step = (speed / 100.0) * 18.0
            heading = robot_state.get("heading", 0.0)
            map_x = robot_state.get("map_x", 480.0)
            map_y = robot_state.get("map_y", 280.0)

            if action == "turn_left":
                heading = (heading - 25.0) % 360.0
            elif action == "turn_right":
                heading = (heading + 25.0) % 360.0
            elif action == "forward":
                rad = math.radians(heading)
                map_x += math.sin(rad) * step
                map_y -= math.cos(rad) * step
            elif action in ["backward", "reverse"]:
                rad = math.radians(heading)
                map_x -= math.sin(rad) * (step * 0.7)
                map_y += math.cos(rad) * (step * 0.7)
            elif action == "strafe_left":
                rad = math.radians(heading)
                map_x -= math.cos(rad) * (step * 0.7)
                map_y -= math.sin(rad) * (step * 0.7)
            elif action == "strafe_right":
                rad = math.radians(heading)
                map_x += math.cos(rad) * (step * 0.7)
                map_y += math.sin(rad) * (step * 0.7)

            # Giới hạn trong khuôn viên siêu thị (50 <= x <= 910, 50 <= y <= 550)
            map_x = max(50.0, min(910.0, map_x))
            map_y = max(50.0, min(550.0, map_y))

            robot_state["heading"] = round(heading, 1)
            robot_state["map_x"] = round(map_x, 1)
            robot_state["map_y"] = round(map_y, 1)

            # Cập nhật nhãn vị trí hiển thị
            if map_x < 300 and map_y < 230:
                robot_state["current_location"] = "Khu Highlands Coffee (Tầng 1)"
            elif map_x < 300 and map_y >= 230:
                robot_state["current_location"] = "Khu Phúc Long Tea (Tầng 1)"
            elif map_x > 640 and map_y < 230:
                robot_state["current_location"] = "Khu Thời Trang Zara (Tầng 1)"
            elif map_x > 640 and map_y < 420:
                robot_state["current_location"] = "Khu Uniqlo LifeWear (Tầng 1)"
            elif map_x > 640 and map_y >= 420:
                robot_state["current_location"] = "Khu Siêu Thị MegaMarket (Tầng 1)"
            elif map_y > 450:
                robot_state["current_location"] = "Sảnh Lễ Tân & Cổng Chính (Tầng 1)"
            else:
                robot_state["current_location"] = "Sảnh Trung Tâm & Bàn Ăn (Tầng 1)"

            if action != "stop" and (time.time() - robot_state.get("last_log_drive", 0) > 4):
                robot_state["last_log_drive"] = time.time()
                add_system_log("ĐIỀU HƯỚNG", f"{robot_state['direction']} ({speed}%).", "INFO")

            if left_motors:
                if action == "forward": left_motors.forward(speed)
                elif action in ["backward", "reverse"]: left_motors.reverse(speed)
                elif action == "stop": left_motors.stop()
                elif action == "brake": left_motors.brake()

            self._send_json({
                "status": "ok",
                "success": True,
                "direction": robot_state["direction"],
                "speed": speed,
                "map_x": robot_state["map_x"],
                "map_y": robot_state["map_y"],
                "heading": robot_state["heading"],
                "location": robot_state["current_location"]
            })
            return

        # 7. Dừng khẩn cấp
        elif path == "/api/motor/emergency":
            robot_state["direction"] = "DỪNG KHẨN CẤP"
            robot_state["status_text"] = "Tạm dừng khẩn cấp"
            if left_motors: left_motors.disable()
            self._send_json({"status": "ok", "message": "Đã dừng robot an toàn."})
            return

        # 8. Quản lý tài khoản (Admin)
        elif path == "/api/users/create":
            user = self._get_auth_user()
            if not user or user.get("role") != "admin":
                self._send_json({"error": "Chỉ Quản trị viên mới có quyền tạo tài khoản."}, 403)
                return

            username = body.get("username", "").strip()
            password = body.get("password", "").strip()
            fullName = body.get("fullName", "").strip()
            if not username or not password or not fullName:
                self._send_json({"error": "Vui lòng điền đủ thông tin."}, 400)
                return

            users = load_json(USERS_FILE, [])
            if any(u.get("username") == username for u in users):
                self._send_json({"error": "Tên đăng nhập đã tồn tại."}, 400)
                return

            new_u = {
                "id": f"usr_{secrets.token_hex(3)}",
                "username": username,
                "password": password,
                "role": body.get("role", "manager"),
                "fullName": fullName,
                "phone": body.get("phone", ""),
                "isActive": True,
                "createdAt": datetime.datetime.now().strftime("%d/%m/%Y")
            }
            users.append(new_u)
            save_json(USERS_FILE, users)
            self._send_json({"status": "success", "message": "Đã thêm nhân viên thành công!"})
            return

        # 9. Bật/Khóa tài khoản
        elif path == "/api/users/toggle":
            user = self._get_auth_user()
            if not user or user.get("role") != "admin":
                self._send_json({"error": "Chỉ Quản trị viên mới có quyền."}, 403)
                return

            uid = body.get("userId")
            users = load_json(USERS_FILE, [])
            for u in users:
                if u.get("id") == uid:
                    if u.get("role") == "admin":
                        self._send_json({"error": "Không thể khóa Admin gốc."}, 400)
                        return
                    u["isActive"] = not u.get("isActive", True)
                    save_json(USERS_FILE, users)
                    self._send_json({"status": "success", "isActive": u["isActive"]})
                    return
            self._send_json({"error": "Không tìm thấy tài khoản."}, 404)
            return

        # 10. Lưu cấu hình AI (Admin)
        elif path == "/api/ai/config":
            user = self._get_auth_user()
            if not user or user.get("role") != "admin":
                self._send_json({"error": "Chỉ Admin mới có quyền cấu hình AI."}, 403)
                return

            config = load_json(AI_CONFIG_FILE, {})
            if "provider" in body: config["provider"] = body["provider"]
            if "model" in body: config["model"] = body["model"]
            if "apiKey" in body and body["apiKey"] != "********":
                config["apiKey"] = body["apiKey"]
            save_json(AI_CONFIG_FILE, config)
            self._send_json({"status": "success", "message": "Đã lưu thiết lập AI thành công!"})
            return

        self._send_json({"error": "Không tìm thấy yêu cầu."}, 404)

    def _get_auth_token_from_header(self):
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[7:].strip()
        return ""


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def run_server(port=8080):
    server_address = ("", port)
    httpd = ThreadedHTTPServer(server_address, RobiServerHandler)
    print("=" * 65)
    print("✨ MÁY CHỦ BÉ ROBI - ROBOT PHỤC VỤ THÔNG MINH MEGAMALL")
    print(f"🌐 Truy cập ngay tại: http://localhost:{port}")
    print(f"📱 Các đường dẫn: /home, /nhan-hang, /map, /chat, /dieu-hanh, /cai-dat")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nĐang tắt máy chủ...")
        httpd.server_close()


if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
