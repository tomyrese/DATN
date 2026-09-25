import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class RobotConfig:
    PWM_FREQ: int = int(os.getenv("PWM_FREQ", "1000"))
    DEFAULT_SPEED: float = float(os.getenv("DEFAULT_SPEED", "0.35"))
    MOTOR_ENABLED: bool = os.getenv("MOTOR_ENABLED", "true").lower() in ("true", "1", "yes")
    SIMULATION_MODE: bool = os.getenv("SIMULATION_MODE", "false").lower() in ("true", "1", "yes")
    DEBUG_PREVIEW: bool = os.getenv("DEBUG_PREVIEW", "false").lower() in ("true", "1", "yes")

    STBY_L: int = int(os.getenv("STBY_L", "27"))
    AIN1_L: int = int(os.getenv("AIN1_L", "5"))
    AIN2_L: int = int(os.getenv("AIN2_L", "6"))
    PWMA_L: int = int(os.getenv("PWMA_L", "13"))
    BIN1_L: int = int(os.getenv("BIN1_L", "26"))
    BIN2_L: int = int(os.getenv("BIN2_L", "22"))
    PWMB_L: int = int(os.getenv("PWMB_L", "19"))

    STBY_R: int = int(os.getenv("STBY_R", "21"))
    PWMA_R: int = int(os.getenv("PWMA_R", "12"))
    AIN1_R: int = int(os.getenv("AIN1_R", "16"))
    AIN2_R: int = int(os.getenv("AIN2_R", "20"))
    PWMB_R: int = int(os.getenv("PWMB_R", "18"))
    BIN1_R: int = int(os.getenv("BIN1_R", "23"))
    BIN2_R: int = int(os.getenv("BIN2_R", "24"))

    OLED_ENABLED: bool = os.getenv("OLED_ENABLED", "true").lower() in ("true", "1", "yes")
    OLED_DRIVER: str = os.getenv("OLED_DRIVER", "sh1106").lower()
    OLED_ADDRESS: int = int(os.getenv("OLED_ADDRESS", "0x3C"), 16) if os.getenv("OLED_ADDRESS", "0x3C").startswith("0x") else int(os.getenv("OLED_ADDRESS", "60"))
    OLED_BUS: int = int(os.getenv("OLED_BUS", "1"))
    OLED_WIDTH: int = int(os.getenv("OLED_WIDTH", "128"))
    OLED_HEIGHT: int = int(os.getenv("OLED_HEIGHT", "64"))
    OLED_FPS: float = float(os.getenv("OLED_FPS", "5.0"))

    CAMERA_ENABLED: bool = os.getenv("CAMERA_ENABLED", "true").lower() in ("true", "1", "yes")
    CAMERA_WIDTH: int = int(os.getenv("CAMERA_WIDTH", "640"))
    CAMERA_HEIGHT: int = int(os.getenv("CAMERA_HEIGHT", "480"))
    CAMERA_FPS: int = int(os.getenv("CAMERA_FPS", "30"))
    CAMERA_BACKEND: str = os.getenv("CAMERA_BACKEND", "picamera2").lower()

    MODEL_PATH: str = os.getenv("MODEL_PATH", str(Path(__file__).resolve().parent.parent / "models" / "mobilenet_ssd_v2_coco.tflite"))
    LABELS_PATH: str = os.getenv("LABELS_PATH", str(Path(__file__).resolve().parent.parent / "models" / "coco_labels.txt"))
    PERSON_CONFIDENCE_THRESHOLD: float = float(os.getenv("PERSON_CONFIDENCE_THRESHOLD", "0.55"))
    PERSON_MIN_AREA_RATIO: float = float(os.getenv("PERSON_MIN_AREA_RATIO", "0.03"))
    STOP_ZONE_X_MIN: float = float(os.getenv("STOP_ZONE_X_MIN", "0.20"))
    STOP_ZONE_X_MAX: float = float(os.getenv("STOP_ZONE_X_MAX", "0.80"))
    PERSON_CLEAR_DELAY: float = float(os.getenv("PERSON_CLEAR_DELAY", "1.5"))
    PERSON_DETECTED_CONFIRM_FRAMES: int = int(os.getenv("PERSON_DETECTED_CONFIRM_FRAMES", "2"))
    AUTO_RESUME_AFTER_PERSON_CLEAR: bool = os.getenv("AUTO_RESUME_AFTER_PERSON_CLEAR", "false").lower() in ("true", "1", "yes")
    CAMERA_WATCHDOG_TIMEOUT: float = float(os.getenv("CAMERA_WATCHDOG_TIMEOUT", "2.0"))
    PERSON_DETECTION_MOCK: bool = os.getenv("PERSON_DETECTION_MOCK", "false").lower() in ("true", "1", "yes")

    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8765"))
    PUBLIC_URL: str = os.getenv("PUBLIC_URL", "")
    ROBOT_ID: str = os.getenv("ROBOT_ID", "RBT01")
    ROBOT_NAME: str = os.getenv("ROBOT_NAME", "Pi Robot")
    PAIRING_ENABLED: bool = os.getenv("PAIRING_ENABLED", "true").lower() in ("true", "1", "yes")
    PAIRING_CODE_TTL: float = float(os.getenv("PAIRING_CODE_TTL", "120.0"))
    DRIVE_COMMAND_TIMEOUT: float = float(os.getenv("DRIVE_COMMAND_TIMEOUT", "0.35"))
    DRIVE_COMMAND_INTERVAL: float = float(os.getenv("DRIVE_COMMAND_INTERVAL", "0.10"))
    HEARTBEAT_INTERVAL: float = float(os.getenv("HEARTBEAT_INTERVAL", "0.50"))
    CONNECTION_TIMEOUT: float = float(os.getenv("CONNECTION_TIMEOUT", "3.50"))
    TELEMETRY_INTERVAL: float = float(os.getenv("TELEMETRY_INTERVAL", "0.25"))
    CAMERA_STREAM_FPS: float = float(os.getenv("CAMERA_STREAM_FPS", "8.0"))
    CAMERA_STREAM_WIDTH: int = int(os.getenv("CAMERA_STREAM_WIDTH", "640"))
    CAMERA_STREAM_HEIGHT: int = int(os.getenv("CAMERA_STREAM_HEIGHT", "480"))
    CAMERA_JPEG_QUALITY: int = int(os.getenv("CAMERA_JPEG_QUALITY", "70"))
    STREAM_TICKET_TTL: float = float(os.getenv("STREAM_TICKET_TTL", "30.0"))

config = RobotConfig()
