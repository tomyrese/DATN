import asyncio
import io
import time
from typing import Optional, AsyncGenerator
import numpy as np
from PIL import Image
from src.config import RobotConfig, config
from src.hardware.camera_service import CameraService
from src.services.logging_service import logger

class CameraStreamManager:
    def __init__(self, camera_service: CameraService, cfg: Optional[RobotConfig] = None):
        self.camera_service = camera_service
        self.cfg = cfg or config
        self.stream_fps = self.cfg.CAMERA_STREAM_FPS
        self.quality = self.cfg.CAMERA_JPEG_QUALITY

    def encode_frame_to_jpeg(self, frame: Optional[np.ndarray]) -> bytes:
        if frame is None:
            frame = np.zeros((self.cfg.CAMERA_STREAM_HEIGHT, self.cfg.CAMERA_STREAM_WIDTH, 3), dtype=np.uint8)

        try:
            import cv2
            # Resize if necessary
            target_size = (self.cfg.CAMERA_STREAM_WIDTH, self.cfg.CAMERA_STREAM_HEIGHT)
            if (frame.shape[1], frame.shape[0]) != target_size:
                frame_resized = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
            else:
                frame_resized = frame

            # Convert RGB to BGR for cv2 encoding
            bgr = cv2.cvtColor(frame_resized, cv2.COLOR_RGB2BGR)
            encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), int(self.quality)]
            success, encoded_img = cv2.imencode('.jpg', bgr, encode_params)
            if success:
                return encoded_img.tobytes()
        except Exception:
            pass

        # Fallback to PIL
        img = Image.fromarray(frame)
        if img.size != (self.cfg.CAMERA_STREAM_WIDTH, self.cfg.CAMERA_STREAM_HEIGHT):
            img = img.resize((self.cfg.CAMERA_STREAM_WIDTH, self.cfg.CAMERA_STREAM_HEIGHT), resample=Image.BILINEAR)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=self.quality, optimize=False)
        return buf.getvalue()

    def get_snapshot(self) -> bytes:
        frame, _ = self.camera_service.get_latest_frame()
        return self.encode_frame_to_jpeg(frame)

    async def generate_mjpeg_stream(self) -> AsyncGenerator[bytes, None]:
        frame_interval = 1.0 / max(1.0, self.stream_fps)
        try:
            while True:
                start_time = time.monotonic()
                frame, _ = self.camera_service.get_latest_frame()
                jpeg_bytes = self.encode_frame_to_jpeg(frame)

                header = (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: " + str(len(jpeg_bytes)).encode("utf-8") + b"\r\n\r\n"
                )
                yield header + jpeg_bytes + b"\r\n"

                elapsed = time.monotonic() - start_time
                sleep_time = max(0.01, frame_interval - elapsed)
                await asyncio.sleep(sleep_time)
        except (asyncio.CancelledError, GeneratorExit):
            pass
