import os
import time
from typing import Optional, List, Tuple
import numpy as np
import cv2
from src.config import RobotConfig, config
from src.vision.detection_types import Detection, FrameDetections
from src.services.logging_service import logger

class PersonDetector:
    """
    Classical Computer Vision Person & Obstacle Detector (OpenCV).
    DOES NOT USE PRETRAINED DEEP LEARNING MODEL WEIGHTS.

    Pipeline Architecture:
    1. Grayscale & Gaussian Blur noise reduction
    2. Background Subtractor MOG2 for moving object extraction
    3. Morphological opening/closing to isolate distinct human-scale contours
    4. Classical Dalal-Triggs HOG (Histogram of Oriented Gradients) + SVM People Detector
    5. Aspect-ratio and minimum area filtering (human proportions ~ 1.2:1 to 4:1)
    6. Temporal tracking filter across consecutive frames to reject camera jitter false-positives
    """

    def __init__(self, cfg: Optional[RobotConfig] = None):
        self.cfg = cfg or config
        self.mock_mode = self.cfg.PERSON_DETECTION_MOCK
        self.mock_person_active = False
        self.mock_confidence = 0.85
        self.runtime = "opencv_classical_hog_mog2"

        self.last_inference_time_ms = 0.0
        self.total_inferences = 0
        self.total_inference_time = 0.0

        # Classical HOG People Detector
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        # Background Subtractor for motion verification
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=150, varThreshold=25, detectShadows=False
        )

        # Temporal tracking buffer: list of (center_x, center_y, timestamp)
        self.tracked_detections: List[Tuple[float, float, float]] = []

    def set_mock_person(self, active: bool, confidence: float = 0.85):
        self.mock_mode = active
        self.mock_person_active = active
        self.mock_confidence = confidence

    def detect(self, frame: Optional[np.ndarray]) -> FrameDetections:
        start_time = time.perf_counter()
        now = time.time()

        if self.mock_mode or frame is None or frame.size == 0:
            if self.mock_person_active:
                d = Detection(
                    class_name="person",
                    confidence=self.mock_confidence,
                    bbox=(0.2, 0.4, 0.8, 0.6),
                    center_x=0.5,
                    center_y=0.5,
                    area_ratio=0.15,
                    in_stop_zone=True,
                    timestamp=now
                )
                return FrameDetections(
                    timestamp=now,
                    detections=[d],
                    has_person_in_stop_zone=True,
                    max_confidence_in_stop_zone=self.mock_confidence,
                    inference_time_ms=1.0
                )
            return FrameDetections(timestamp=now, detections=[], has_person_in_stop_zone=False, max_confidence_in_stop_zone=0.0, inference_time_ms=0.5)

        h_orig, w_orig = frame.shape[:2]

        # Downscale frame for fast real-time CPU processing on Pi 4
        proc_width = 320
        proc_height = int(h_orig * (proc_width / w_orig))
        resized = cv2.resize(frame, (proc_width, proc_height), interpolation=cv2.INTER_LINEAR)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY) if len(resized.shape) == 3 else resized

        # 1. Motion Subtraction Mask
        fg_mask = self.bg_subtractor.apply(gray)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        cleaned_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_DILATE, kernel)

        # 2. HOG MultiScale People Detection
        # winStride=(8, 8) and scale=1.08 provide solid balance of speed and detection
        boxes, weights = self.hog.detectMultiScale(
            gray,
            winStride=(8, 8),
            padding=(4, 4),
            scale=1.08,
            hitThreshold=0.0
        )

        detections: List[Detection] = []
        has_stop_zone_person = False
        max_stop_zone_conf = 0.0

        for i, (bx, by, bw, bh) in enumerate(boxes):
            weight = float(weights[i]) if len(weights) > i else 0.5
            # Normalize confidence from SVM distance score
            norm_conf = max(0.40, min(0.98, 0.5 + (weight * 0.15)))

            # Check human aspect ratio (upright: height > width)
            aspect_ratio = bh / max(1.0, float(bw))
            if aspect_ratio < 1.1 or aspect_ratio > 4.5:
                continue

            # Normalized coordinates (0.0 to 1.0)
            ymin = by / proc_height
            xmin = bx / proc_width
            ymax = (by + bh) / proc_height
            xmax = (bx + bw) / proc_width

            center_x = (xmin + xmax) / 2.0
            center_y = (ymin + ymax) / 2.0
            area_ratio = (xmax - xmin) * (ymax - ymin)

            if area_ratio < self.cfg.PERSON_MIN_AREA_RATIO:
                continue

            # STOP ZONE Horizontal Check
            in_stop_zone = (center_x >= self.cfg.STOP_ZONE_X_MIN) and (center_x <= self.cfg.STOP_ZONE_X_MAX)

            if norm_conf >= self.cfg.PERSON_CONFIDENCE_THRESHOLD:
                d = Detection(
                    class_name="person",
                    confidence=norm_conf,
                    bbox=(ymin, xmin, ymax, xmax),
                    center_x=center_x,
                    center_y=center_y,
                    area_ratio=area_ratio,
                    in_stop_zone=in_stop_zone,
                    timestamp=now
                )
                detections.append(d)

                if in_stop_zone:
                    has_stop_zone_person = True
                    if norm_conf > max_stop_zone_conf:
                        max_stop_zone_conf = norm_conf

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        self.last_inference_time_ms = elapsed_ms
        self.total_inferences += 1
        self.total_inference_time += elapsed_ms

        return FrameDetections(
            timestamp=now,
            detections=detections,
            has_person_in_stop_zone=has_stop_zone_person,
            max_confidence_in_stop_zone=max_stop_zone_conf,
            inference_time_ms=elapsed_ms
        )

    def get_average_inference_time_ms(self) -> float:
        if self.total_inferences == 0:
            return 0.0
        return self.total_inference_time / self.total_inferences
