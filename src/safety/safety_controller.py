import time
from typing import Optional, Tuple
from src.config import RobotConfig, config
from src.state import SafetyState, RobotState, MovementCommand
from src.vision.detection_types import FrameDetections
from src.services.logging_service import logger

class SafetyController:
    """
    Multi-Tier Safety and Hazard Prevention Engine:
    Strict Priority Hierarchy:
    [1] EMERGENCY_STOP       (Software / Physical E-Stop button)
    [2] SYSTEM_ERROR         (Loop crash / fatal unhandled exception)
    [3] SENSOR_ERROR         (Ultrasonic sensor read failure / timeout)
    [4] ULTRASONIC_OBSTACLE  (Physical obstacle < 25cm in trajectory)
    [5] CAMERA_ERROR         (CSI Camera feed failure / watchdog timeout)
    [6] VISION_PERSON        (Person detected inside STOP_ZONE)
    [7] SAFETY_STOP          (Latching safety stop before operator intervention)
    [8] CONNECTION_LOST      (Heartbeat timeout > 1.2s or lease expired)
    [9] MOVEMENT_COMMAND     (Allowed navigation or teleop drive)
    """

    def __init__(self, cfg: Optional[RobotConfig] = None):
        self.cfg = cfg or config
        self.safety_state = SafetyState.CLEAR
        self.is_emergency_stopped = False
        self.has_camera_error = False
        self.has_motor_error = False
        self.has_system_error = False
        self.has_sensor_error = False

        # Vision person tracking
        self.person_detected_frames = 0
        self.last_person_time = 0.0
        self.person_active = False

        # Ultrasonic obstacle tracking
        self.obstacle_active = False
        self.obstacle_slow_down = False
        self.last_obstacle_time = 0.0
        self.last_min_dist: Optional[float] = None

    def update_vision_safety(self, detections: FrameDetections, is_moving: bool) -> bool:
        now = time.monotonic()
        should_stop = False

        if detections.has_person_in_stop_zone:
            self.person_detected_frames += 1
            self.last_person_time = now

            if self.person_detected_frames >= self.cfg.PERSON_DETECTED_CONFIRM_FRAMES or detections.max_confidence_in_stop_zone >= self.cfg.PERSON_CONFIDENCE_THRESHOLD:
                if not self.person_active:
                    self.person_active = True
                    logger.warning(f"PERSON_DETECTED confidence={detections.max_confidence_in_stop_zone:.2f}")
                self.safety_state = SafetyState.SAFETY_STOP
                if is_moving:
                    should_stop = True
                    logger.warning("SAFETY_STOP reason=person_detected")
        else:
            self.person_detected_frames = 0
            if self.person_active:
                if now - self.last_person_time >= self.cfg.PERSON_CLEAR_DELAY:
                    self.person_active = False
                    logger.info("PERSON_CLEAR")
                    if self.safety_state == SafetyState.SAFETY_STOP and not self.obstacle_active:
                        self.safety_state = SafetyState.CLEAR

        return should_stop

    def update_ultrasonic_safety(self, min_distance_cm: Optional[float], is_moving: bool) -> Tuple[bool, bool]:
        """
        Processes distance readings from dual HC-SR04 sensors.
        Returns: (should_stop, should_slow_down)
        """
        now = time.monotonic()
        should_stop = False
        should_slow = False
        self.last_min_dist = min_distance_cm

        if min_distance_cm is None:
            # Sensor timeout or invalid reading
            if self.has_sensor_error:
                return (True, True)
            return (False, False)

        if min_distance_cm <= self.cfg.ULTRASONIC_STOP_DISTANCE_CM:
            self.last_obstacle_time = now
            if not self.obstacle_active:
                self.obstacle_active = True
                logger.warning(f"OBSTACLE_EMERGENCY_STOP distance={min_distance_cm:.1f}cm (< {self.cfg.ULTRASONIC_STOP_DISTANCE_CM}cm)")
            self.safety_state = SafetyState.SAFETY_STOP
            should_stop = True
            should_slow = True
        elif min_distance_cm <= self.cfg.ULTRASONIC_SLOW_DISTANCE_CM:
            should_slow = True
            self.obstacle_slow_down = True
            if self.obstacle_active and (now - self.last_obstacle_time >= self.cfg.PERSON_CLEAR_DELAY):
                self.obstacle_active = False
        else:
            self.obstacle_slow_down = False
            if self.obstacle_active and (now - self.last_obstacle_time >= self.cfg.PERSON_CLEAR_DELAY):
                self.obstacle_active = False
                logger.info("OBSTACLE_CLEAR")
                if self.safety_state == SafetyState.SAFETY_STOP and not self.person_active:
                    self.safety_state = SafetyState.CLEAR

        return (should_stop, should_slow)

    def set_sensor_error(self, error: bool):
        self.has_sensor_error = error
        if error:
            self.safety_state = SafetyState.ERROR_STOP

    def set_camera_error(self, error: bool):
        self.has_camera_error = error
        if error:
            self.safety_state = SafetyState.ERROR_STOP

    def set_motor_error(self, error: bool):
        self.has_motor_error = error
        if error:
            self.safety_state = SafetyState.ERROR_STOP

    def set_system_error(self, error: bool):
        self.has_system_error = error
        if error:
            self.safety_state = SafetyState.ERROR_STOP

    def trigger_emergency_stop(self):
        self.is_emergency_stopped = True
        self.safety_state = SafetyState.ERROR_STOP
        logger.warning("EMERGENCY_STOP activated")

    def reset_emergency_stop(self) -> bool:
        if self.person_active:
            logger.warning("Cannot reset emergency stop while person is in stop zone")
            return False
        if self.obstacle_active:
            logger.warning("Cannot reset emergency stop while physical obstacle is within stop zone")
            return False
        if self.has_camera_error or self.has_motor_error or self.has_system_error or self.has_sensor_error:
            logger.warning("Cannot reset emergency stop while system or sensor errors exist")
            return False

        self.is_emergency_stopped = False
        self.safety_state = SafetyState.CLEAR
        logger.info("EMERGENCY_STOP reset successful")
        return True

    def can_move(self) -> bool:
        if self.is_emergency_stopped:
            return False
        if self.has_system_error or self.has_motor_error or self.has_camera_error or self.has_sensor_error:
            return False
        if self.person_active or self.obstacle_active:
            return False
        if self.safety_state != SafetyState.CLEAR:
            return False
        return True

    def get_effective_robot_state(self, current_motion_state: RobotState) -> RobotState:
        if self.is_emergency_stopped:
            return RobotState.SAFETY_STOP
        if self.has_system_error:
            return RobotState.SYSTEM_ERROR
        if self.has_motor_error:
            return RobotState.MOTOR_ERROR
        if self.has_sensor_error:
            return RobotState.SYSTEM_ERROR
        if self.has_camera_error:
            return RobotState.CAMERA_ERROR
        if self.obstacle_active or self.person_active:
            return RobotState.PERSON_DETECTED
        if self.safety_state == SafetyState.SAFETY_STOP:
            return RobotState.SAFETY_STOP
        return current_motion_state
