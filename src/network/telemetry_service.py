import time
import os
from typing import Optional, Dict, Any, List
import psutil
from src.config import RobotConfig, config
from src.network.protocol import TelemetryMessage

class TelemetryService:
    def __init__(self, cfg: Optional[RobotConfig] = None):
        self.cfg = cfg or config
        self.start_time = time.monotonic()
        self.last_sys_metrics_time = 0.0
        self.cached_cpu_usage: Optional[float] = None
        self.cached_memory_usage: Optional[float] = None
        self.cached_cpu_temp: Optional[float] = None

    def _read_cpu_temperature(self) -> Optional[float]:
        try:
            if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
                with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                    return float(f.read().strip()) / 1000.0
        except Exception:
            pass
        return None

    def _update_system_metrics(self):
        now = time.monotonic()
        if now - self.last_sys_metrics_time >= 1.0:
            try:
                self.cached_cpu_usage = float(psutil.cpu_percent(interval=None))
                self.cached_memory_usage = float(psutil.virtual_memory().percent)
                self.cached_cpu_temp = self._read_cpu_temperature()
            except Exception:
                pass
            self.last_sys_metrics_time = now

    def build_telemetry(
        self,
        robot_state: str,
        safety_state: str,
        target_speed: float,
        motor_speeds: Dict[int, float],
        person_detected: bool,
        person_confidence: float,
        camera_ok: bool,
        detector_ok: bool,
        oled_ok: bool,
        motor_ok: bool,
        camera_fps: float,
        inferenceFps: float,
        person_bbox: Optional[List[float]] = None,
        odometry_x: Optional[float] = None,
        odometry_y: Optional[float] = None,
        odometry_heading: Optional[float] = None,
        odometry_confidence: Optional[float] = None,
        is_estimated: Optional[bool] = True,
        ultrasonic_left: Optional[float] = None,
        ultrasonic_right: Optional[float] = None,
        obstacle_state: Optional[str] = None,
        nav_status: Optional[str] = None
    ) -> TelemetryMessage:
        self._update_system_metrics()
        now = time.time()
        uptime = time.monotonic() - self.start_time

        m1 = motor_speeds.get(1, 0.0)
        m2 = motor_speeds.get(2, 0.0)
        m3 = motor_speeds.get(3, 0.0)
        m4 = motor_speeds.get(4, 0.0)

        left_speed = (m1 + m2) / 2.0
        right_speed = (m3 + m4) / 2.0

        return TelemetryMessage(
            robotState=robot_state,
            safetyState=safety_state,
            speed=target_speed,
            leftSpeed=left_speed,
            rightSpeed=right_speed,
            m1=m1,
            m2=m2,
            m3=m3,
            m4=m4,
            personDetected=person_detected,
            personConfidence=person_confidence,
            cameraOk=camera_ok,
            detectorOk=detector_ok,
            oledOk=oled_ok,
            motorOk=motor_ok,
            cameraFps=camera_fps,
            inferenceFps=inferenceFps,
            cpuTemp=self.cached_cpu_temp,
            cpuUsage=self.cached_cpu_usage,
            memoryUsage=self.cached_memory_usage,
            wifiSignal=None,
            uptime=uptime,
            timestamp=now,
            personBbox=person_bbox,
            odometryX=odometry_x,
            odometryY=odometry_y,
            odometryHeading=odometry_heading,
            odometryConfidence=odometry_confidence,
            isEstimated=is_estimated,
            ultrasonicLeft=ultrasonic_left,
            ultrasonicRight=ultrasonic_right,
            obstacleState=obstacle_state,
            navStatus=nav_status
        )
