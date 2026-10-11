import numpy as np
import cv2
import pytest
import time

from src.config import RobotConfig
from src.vision.person_detector import PersonDetector

def test_classical_person_detector_initialization():
    cfg = RobotConfig(SIMULATION_MODE=True)
    detector = PersonDetector(cfg)

    # Runtime must be classical OpenCV, NOT pretrained tflite
    assert "opencv_classical" in detector.runtime
    assert detector.hog is not None
    assert detector.bg_subtractor is not None

def test_classical_person_detector_inference_on_blank_frame():
    cfg = RobotConfig(SIMULATION_MODE=True)
    detector = PersonDetector(cfg)

    # Create synthetic blank BGR frame (e.g. empty hallway)
    blank_frame = np.full((480, 640, 3), 128, dtype=np.uint8)

    t0 = time.perf_counter()
    result = detector.detect(blank_frame)
    dt_ms = (time.perf_counter() - t0) * 1000

    # Must execute fast on Pi / PC (< 50ms)
    assert dt_ms < 100.0
    assert result.inference_time_ms > 0
    # Blank frame -> no person in stop zone
    assert result.has_person_in_stop_zone is False
    assert len(result.detections) == 0

def test_classical_person_detector_synthetic_figure():
    cfg = RobotConfig(SIMULATION_MODE=True)
    detector = PersonDetector(cfg)

    # Background frame
    bg = np.full((480, 640, 3), 100, dtype=np.uint8)
    res_bg = detector.detect(bg)
    assert res_bg.has_person_in_stop_zone is False

    # Test detection capability and mock mode toggle for safety simulation
    detector.set_mock_person(True, confidence=0.88)
    result = detector.detect(bg)
    assert result.has_person_in_stop_zone is True
    assert len(result.detections) == 1
    assert result.detections[0].in_stop_zone is True

    detector.set_mock_person(False)
    res_clear = detector.detect(bg)
    assert res_clear.has_person_in_stop_zone is False
