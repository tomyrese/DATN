import threading
import time
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
from src.config import RobotConfig, config
from src.state import RobotState
from src.services.logging_service import logger

class OLEDController:
    def __init__(self, cfg: Optional[RobotConfig] = None):
        self.cfg = cfg or config
        self.device = None
        self.available = False
        self.lock = threading.Lock()
        self.font = ImageFont.load_default()
        self.last_state: Optional[RobotState] = None
        self.last_info: Dict[str, Any] = {}
        self.last_render_time = 0.0

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

    def _draw_lines(self, title: str, lines: list):
        img = Image.new("1", (self.cfg.OLED_WIDTH, self.cfg.OLED_HEIGHT), 0)
        draw = ImageDraw.Draw(img)

        draw.text((0, 0), title[:20], font=self.font, fill=255)
        draw.line([(0, 11), (self.cfg.OLED_WIDTH, 11)], fill=255)

        y = 14
        for line in lines:
            if y >= self.cfg.OLED_HEIGHT:
                break
            draw.text((0, y), str(line)[:21], font=self.font, fill=255)
            y += 11

        self._render_image(img)

    def show_boot(self):
        self._draw_lines("ROBOT BOOTING...", ["CAM: INIT", "MOTOR: INIT", "SERVER: INIT"])

    def show_ready(self, ip: str = ""):
        lines = ["CAM: OK", "MOTOR: OK", "WAITING APP"]
        if ip:
            lines.append(f"IP:{ip}")
        self._draw_lines("ROBOT READY", lines)

    def show_pairing(self, qr_image: Optional[Image.Image], code: str, ip: str, remaining_sec: int):
        img = Image.new("1", (self.cfg.OLED_WIDTH, self.cfg.OLED_HEIGHT), 0)
        draw = ImageDraw.Draw(img)

        if qr_image is not None:
            qr_w, qr_h = qr_image.size
            pos_x = 2
            pos_y = max(0, (self.cfg.OLED_HEIGHT - qr_h) // 2)
            img.paste(qr_image, (pos_x, pos_y))

        text_x = 64
        draw.text((text_x, 2), "SCAN WEB", font=self.font, fill=255)
        draw.line([(text_x, 13), (self.cfg.OLED_WIDTH, 13)], fill=255)
        draw.text((text_x, 16), f"PIN:{code}", font=self.font, fill=255)
        draw.text((text_x, 28), f"EXP:{remaining_sec}s", font=self.font, fill=255)
        if ip:
            draw.text((text_x, 40), ip[-11:], font=self.font, fill=255)
        draw.text((text_x, 52), f":{self.cfg.SERVER_PORT}", font=self.font, fill=255)

        self._render_image(img)

    def show_connected(self, ip: str = "", speed: float = 0.35):
        lines = [f"CLIENT: CONNECTED", f"SPD: {int(speed * 100)}%", "PERSON: CLEAR"]
        if ip:
            lines.append(f"IP:{ip}")
        self._draw_lines("APP CONNECTED", lines)

    def show_disconnected(self):
        self._draw_lines("APP LOST", ["ROBOT STOPPED", "SAFE MODE", "WAIT RECONNECT"])

    def show_moving(self, direction: str, speed: float):
        self._draw_lines(f"{direction.upper()}", [f"SPD: {int(speed * 100)}%", "CAM: OK", "PERSON: CLEAR"])

    def show_person_detected(self, confidence: float = 0.0):
        conf_str = f"CONF: {int(confidence * 100)}%" if confidence > 0 else "PERSON"
        self._draw_lines("PERSON DETECTED", ["STOPPING", conf_str, "MOTOR: 0%"])

    def show_safety_stop(self):
        self._draw_lines("SAFETY STOP", ["OBSTACLE AHEAD", "MOTOR STOP", "WAITING CLEAR"])

    def show_camera_error(self):
        self._draw_lines("CAM ERROR", ["ROBOT STOPPED", "NO FRAME / TIMEOUT", "CHECK CAMERA"])

    def show_motor_error(self):
        self._draw_lines("MOTOR ERROR", ["ROBOT STOPPED", "DRIVER FAULT", "CHECK HARDWARE"])

    def show_system_error(self, err: str = ""):
        self._draw_lines("SYSTEM ERROR", ["ROBOT STOPPED", err[:20] if err else "FAIL-SAFE"])

    def show_shutdown(self):
        self._draw_lines("ROBOT SHUTDOWN", ["SYSTEM STOPPED", "POWER SAFE TO OFF"])

    def show_custom(self, title: str, lines: list):
        self._draw_lines(title, lines)

    def update_state(self, state: RobotState, info: Optional[Dict[str, Any]] = None):
        info_dict = info or {}
        if state == RobotState.BOOTING:
            self.show_boot()
        elif state == RobotState.PAIRING:
            self.show_pairing(
                info_dict.get("qr_image"),
                info_dict.get("pair_code", ""),
                info_dict.get("ip", ""),
                info_dict.get("remaining_sec", 0)
            )
        elif state == RobotState.READY or state == RobotState.STOPPED:
            self.show_ready(info_dict.get("ip", ""))
        elif state == RobotState.CONNECTED:
            self.show_connected(info_dict.get("ip", ""), info_dict.get("speed", self.cfg.DEFAULT_SPEED))
        elif state == RobotState.DISCONNECTED:
            self.show_disconnected()
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
