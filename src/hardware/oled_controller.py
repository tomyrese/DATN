import threading
import time
import unicodedata
from typing import Optional, Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
import qrcode
from src.config import RobotConfig, config
from src.state import RobotState
from src.services.logging_service import logger

def remove_accents(input_str: str) -> str:
    """Removes Vietnamese diacritics and converts to plain ASCII for bitmap OLED display."""
    if not input_str:
        return ""
    s = str(input_str).replace("đ", "d").replace("Đ", "D")
    nfkd_form = unicodedata.normalize('NFKD', s)
    ascii_bytes = nfkd_form.encode('ASCII', 'ignore')
    return ascii_bytes.decode('utf-8')

class OLEDController:
    def __init__(self, cfg: Optional[RobotConfig] = None):
        self.cfg = cfg or config
        self.device = None
        self.available = False
        self.lock = threading.Lock()
        self.font = ImageFont.load_default()
        self.last_render_time = 0.0
        self.qr_image: Optional[Image.Image] = None
        self.current_ip: str = ""

        if self.cfg.OLED_ENABLED and not self.cfg.SIMULATION_MODE:
            self._init_hardware()
        else:
            logger.info("OLEDController running in simulated/disabled mode")

    def _init_hardware(self):
        try:
            from luma.core.interface.serial import i2c
            from luma.oled.device import sh1106, ssd1306

            serial = i2c(port=self.cfg.OLED_BUS, address=self.cfg.OLED_ADDRESS)
            if self.cfg.OLED_DRIVER.lower() == "ssd1306":
                self.device = ssd1306(serial, width=self.cfg.OLED_WIDTH, height=self.cfg.OLED_HEIGHT)
            else:
                self.device = sh1106(serial, width=self.cfg.OLED_WIDTH, height=self.cfg.OLED_HEIGHT)

            self.available = True
            logger.info(f"OLEDController successfully connected ({self.cfg.OLED_DRIVER.upper()} at 0x{self.cfg.OLED_ADDRESS:02X})")
            self.show_boot()
        except Exception as e:
            self.available = False
            logger.warning(f"OLED display not detected or failed to initialize: {e}. Robot will continue without OLED.")

    def set_qr_url(self, url: str, target_size: int = 56):
        """Generates and caches a high-contrast QR code for continuous on-screen display."""
        if not url:
            return
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=1,
                border=1,
            )
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white").convert("1")
            self.qr_image = img.resize((target_size, target_size), resample=Image.NEAREST)
        except Exception as e:
            logger.warning(f"Failed to generate OLED QR code: {e}")

    def _render_image(self, img: Image.Image):
        if not self.available or self.device is None:
            return

        now = time.monotonic()
        if now - self.last_render_time < (1.0 / self.cfg.OLED_FPS):
            return

        with self.lock:
            try:
                self.device.display(img)
                self.last_render_time = now
            except Exception as e:
                logger.warning(f"Error rendering to OLED: {e}")
                self.available = False

    def draw_interactive_screen(self, title: str, lines: List[str], custom_qr: Optional[Image.Image] = None):
        """
        Renders a user-friendly split display:
        - Left: Persistent QR code so anyone can scan and connect at any moment.
        - Right: Clean, unaccented human-readable Vietnamese interaction messages.
        """
        img = Image.new("1", (self.cfg.OLED_WIDTH, self.cfg.OLED_HEIGHT), 0)
        draw = ImageDraw.Draw(img)

        qr = custom_qr or self.qr_image

        if qr is not None:
            # Paste QR on the left side
            qr_w, qr_h = qr.size
            pos_x = 1
            pos_y = max(0, (self.cfg.OLED_HEIGHT - qr_h) // 2)
            img.paste(qr, (pos_x, pos_y))

            # Vertical separator line
            draw.line([(58, 2), (58, 62)], fill=255)

            # Right Side: Header + Interactive Lines
            text_x = 61
            clean_title = remove_accents(title)[:11].upper()
            draw.text((text_x, 2), clean_title, font=self.font, fill=255)
            draw.line([(text_x, 13), (self.cfg.OLED_WIDTH, 13)], fill=255)

            y = 16
            for line in lines:
                if y >= self.cfg.OLED_HEIGHT:
                    break
                clean_line = remove_accents(str(line))[:11]
                draw.text((text_x, y), clean_line, font=self.font, fill=255)
                y += 11
        else:
            # Full width fallback
            clean_title = remove_accents(title)[:20].upper()
            draw.text((0, 2), clean_title, font=self.font, fill=255)
            draw.line([(0, 13), (self.cfg.OLED_WIDTH, 13)], fill=255)

            y = 16
            for line in lines:
                if y >= self.cfg.OLED_HEIGHT:
                    break
                clean_line = remove_accents(str(line))[:21]
                draw.text((0, y), clean_line, font=self.font, fill=255)
                y += 11

        self._render_image(img)

    def show_boot(self):
        self.draw_interactive_screen("KHOI DONG", ["Vui long doi", "Dang khoi tao", "He thong..."])

    def show_ready(self, ip: str = ""):
        self.draw_interactive_screen("ROBOT TTTM", ["SAN SANG", "Quet ma QR", "De su dung", ip[-11:] if ip else ""])

    def show_connected(self, ip: str = "", speed: float = 0.35):
        self.draw_interactive_screen("ROBOT TTTM", ["DA KET NOI", "San sang", f"Toc do:{int(speed*100)}%", "Chuc vui ve!"])

    def show_moving(self, direction: str, speed: float):
        self.draw_interactive_screen("DI CHUYEN", [f"{direction.upper()}", f"Toc do:{int(speed*100)}%", "Chu y", "An toan"])

    def show_person_detected(self, confidence: float = 0.0):
        self.draw_interactive_screen("CANH BAO", ["CO NGUOI", "Phia truoc", "Tam dung xe", "Nhuong duong"])

    def show_safety_stop(self):
        self.draw_interactive_screen("TAM DUNG", ["CO VAT CAN", "Phia truoc", "Xe tam dung", "Cho duong trong"])

    def show_camera_error(self):
        self.draw_interactive_screen("TAM DUNG", ["KIEM TRA", "Cam bien", "Tam dung an toan"])

    def show_motor_error(self):
        self.draw_interactive_screen("TAM DUNG", ["DONG CO", "Kiem tra", "Phan cung"])

    def show_system_error(self, err: str = ""):
        self.draw_interactive_screen("SU CO", ["HE THONG", "Dang khoi phuc", "Vui long doi"])

    def show_shutdown(self):
        self.draw_interactive_screen("TAT MAY", ["ROBOT NGHI", "Tam biet", "Quy khach!"])

    def show_custom(self, title: str, lines: list):
        self.draw_interactive_screen(title, lines)

    def update_state(self, state: RobotState, info: Optional[Dict[str, Any]] = None):
        info_dict = info or {}
        ip = info_dict.get("ip", self.current_ip)
        if ip and ip != self.current_ip:
            self.current_ip = ip
            self.set_qr_url(f"http://{ip}:{self.cfg.SERVER_PORT}")

        if "qr_image" in info_dict and info_dict["qr_image"] is not None:
            self.qr_image = info_dict["qr_image"]

        if state == RobotState.BOOTING:
            self.show_boot()
        elif state == RobotState.PAIRING:
            self.draw_interactive_screen(
                "QUET MA",
                ["QUET QR WEB", f"PIN:{info_dict.get('pair_code', '')}", f"EXP:{info_dict.get('remaining_sec', 0)}s", ip[-11:] if ip else ""],
                custom_qr=info_dict.get("qr_image")
            )
        elif state in (RobotState.READY, RobotState.STOPPED):
            self.show_ready(ip)
        elif state == RobotState.CONNECTED:
            self.show_connected(ip, info_dict.get("speed", self.cfg.DEFAULT_SPEED))
        elif state == RobotState.DISCONNECTED:
            self.show_ready(ip)
        elif state in (RobotState.FORWARD, RobotState.BACKWARD, RobotState.TURN_LEFT, RobotState.TURN_RIGHT):
            self.show_moving(state.value, info_dict.get("speed", self.cfg.DEFAULT_SPEED))
        elif state == RobotState.PERSON_DETECTED:
            self.show_person_detected(info_dict.get("confidence", 0.0))
        elif state == RobotState.SAFETY_STOP:
            self.show_safety_stop()
        elif state == RobotState.CAMERA_ERROR:
            self.show_camera_error()
        elif state == RobotState.MOTOR_ERROR:
            self.show_motor_error()
        elif state == RobotState.SYSTEM_ERROR:
            self.show_system_error(info_dict.get("error", ""))
        elif state == RobotState.SHUTTING_DOWN:
            self.show_shutdown()

    def clear(self):
        if self.available and self.device is not None:
            try:
                self.device.clear()
            except Exception:
                pass

    def cleanup(self):
        self.show_shutdown()
        time.sleep(0.2)
        self.clear()
