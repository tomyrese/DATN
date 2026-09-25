import threading
import time
from typing import Optional, Tuple
import numpy as np
from src.config import RobotConfig, config
from src.services.logging_service import logger

class CameraService:
    def __init__(self, cfg: Optional[RobotConfig] = None):
        self.cfg = cfg or config
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.latest_frame: Optional[np.ndarray] = None
        self.latest_timestamp: float = 0.0
        self.frame_count = 0
        self.fps = 0.0
        self.fps_timer = time.monotonic()
        self.picam2 = None
        self.cap = None
        self.backend = "none"

    def _init_picamera2(self) -> bool:
        try:
            from picamera2 import Picamera2
            self.picam2 = Picamera2()
            cam_config = self.picam2.create_preview_configuration(
                main={"format": "BGR888", "size": (self.cfg.CAMERA_WIDTH, self.cfg.CAMERA_HEIGHT)}
            )
            self.picam2.configure(cam_config)
            self.picam2.start()
            self.backend = "picamera2"
            logger.info(f"Picamera2 initialized successfully at {self.cfg.CAMERA_WIDTH}x{self.cfg.CAMERA_HEIGHT} (BGR888)")
            return True
        except Exception as e:
            logger.warning(f"Failed to initialize Picamera2: {e}")
            if self.picam2 is not None:
                try:
                    self.picam2.stop()
                    self.picam2.close()
                except Exception:
                    pass
                self.picam2 = None
            return False

    def _init_opencv(self) -> bool:
        try:
            import cv2
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cfg.CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cfg.CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, self.cfg.CAMERA_FPS)
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.backend = "opencv"
                    logger.info("OpenCV VideoCapture(0) initialized successfully")
                    return True
                else:
                    self.cap.release()
                    self.cap = None
            return False
        except Exception as e:
            logger.warning(f"Failed to initialize OpenCV VideoCapture: {e}")
            if self.cap is not None:
                try:
                    self.cap.release()
                except Exception:
                    pass
                self.cap = None
            return False

    def _init_synthetic(self) -> bool:
        self.backend = "synthetic"
        logger.info("CameraService initialized with synthetic frames (simulation)")
        return True

    def start(self) -> bool:
        if self.running:
            return True

        if not self.cfg.CAMERA_ENABLED:
            logger.info("Camera is disabled in configuration")
            return self._init_synthetic() and self._start_thread()

        initialized = False
        if not self.cfg.SIMULATION_MODE and self.cfg.CAMERA_BACKEND == "picamera2":
            initialized = self._init_picamera2()

        if not initialized and not self.cfg.SIMULATION_MODE:
            initialized = self._init_opencv()

        if not initialized:
            if self.cfg.SIMULATION_MODE:
                initialized = self._init_synthetic()
            else:
                logger.error("No camera hardware detected and SIMULATION_MODE is false")
                return False

        return self._start_thread()

    def _start_thread(self) -> bool:
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        return True

    def _capture_loop(self):
        fps_frames = 0
        fps_start = time.monotonic()
        consecutive_errors = 0

        while self.running:
            frame = None
            timestamp = time.monotonic()

            try:
                if self.backend == "picamera2" and self.picam2 is not None:
                    frame = self.picam2.capture_array()
                    consecutive_errors = 0
                elif self.backend == "opencv" and self.cap is not None:
                    ret, bgr = self.cap.read()
                    if ret and bgr is not None:
                        frame = bgr
                        consecutive_errors = 0
                    else:
                        consecutive_errors += 1
                elif self.backend == "synthetic":
                    frame = np.zeros((self.cfg.CAMERA_HEIGHT, self.cfg.CAMERA_WIDTH, 3), dtype=np.uint8)
                    time.sleep(1.0 / max(1.0, self.cfg.CAMERA_FPS))
                    consecutive_errors = 0

                if frame is not None:
                    with self.lock:
                        self.latest_frame = frame
                        self.latest_timestamp = timestamp
                        self.frame_count += 1

                    fps_frames += 1
                    now = time.monotonic()
                    if now - fps_start >= 2.0:
                        self.fps = fps_frames / max(0.1, now - fps_start)
                        fps_frames = 0
                        fps_start = now

                    # Sleep briefly to match target FPS and not starve CPU
                    target_interval = 1.0 / max(1.0, self.cfg.CAMERA_FPS)
                    elapsed = time.monotonic() - timestamp
                    if elapsed < target_interval:
                        time.sleep(target_interval - elapsed)
                else:
                    if consecutive_errors > 20:
                        logger.warning("Camera hardware stalled, attempting recovery...")
                        time.sleep(0.5)
                        consecutive_errors = 0
                    else:
                        time.sleep(0.02)
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors % 20 == 1:
                    logger.error(f"Error in camera capture loop: {e}")
                time.sleep(0.05)

    def get_latest_frame(self) -> Tuple[Optional[np.ndarray], float]:
        with self.lock:
            if self.latest_frame is None:
                return None, 0.0
            return self.latest_frame, self.latest_timestamp

    def get_fps(self) -> float:
        return self.fps

    def is_alive(self) -> bool:
        if not self.running:
            return False
        if self.latest_timestamp == 0.0:
            return True
        return (time.monotonic() - self.latest_timestamp) < self.cfg.CAMERA_WATCHDOG_TIMEOUT

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

        if self.backend == "picamera2" and self.picam2 is not None:
            try:
                self.picam2.stop()
                self.picam2.close()
            except Exception:
                pass
            self.picam2 = None

        if self.backend == "opencv" and self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

        logger.info("CameraService stopped")
