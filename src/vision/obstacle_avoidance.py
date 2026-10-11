import time
from enum import Enum
from typing import Optional, Tuple, Dict, Any
from src.config import RobotConfig, config
from src.services.logging_service import logger

class ObstacleState(Enum):
    CLEAR = "CLEAR"
    OBSTACLE_DETECTED = "OBSTACLE_DETECTED"
    SLOWING_DOWN = "SLOWING_DOWN"
    STOPPED_FOR_OBSTACLE = "STOPPED_FOR_OBSTACLE"
    AVOIDING = "AVOIDING"
    REJOINING_ROUTE = "REJOINING_ROUTE"
    BLOCKED = "BLOCKED"
    SENSOR_ERROR = "SENSOR_ERROR"
    EMERGENCY_STOP = "EMERGENCY_STOP"

class ObstacleAvoidanceController:
    """
    Finite State Machine for Real-time Obstacle Detection, Deceleration,
    Emergency Stop, and Autonomous Route Recovery.
    Fuses dual ultrasonic distance metrics with camera vision perception.
    """

    def __init__(self, cfg: Optional[RobotConfig] = None):
        self.cfg = cfg or config
        self.state = ObstacleState.CLEAR
        self.last_state_change = time.time()
        self.avoid_direction = "right"  # "left" or "right"
        self.avoid_start_time = 0.0
        self.blocked_retry_count = 0
        self.last_valid_dist = 200.0

    def update(
        self,
        dist_left_cm: Optional[float],
        dist_right_cm: Optional[float],
        has_person_vision: bool,
        is_e_stopped: bool = False
    ) -> ObstacleState:
        now = time.time()

        if is_e_stopped:
            self._set_state(ObstacleState.EMERGENCY_STOP)
            return self.state

        # Check sensor validity
        if dist_left_cm is None and dist_right_cm is None:
            # Both sensors timed out or disconnected
            self._set_state(ObstacleState.SENSOR_ERROR)
            return self.state

        min_dist = min([d for d in (dist_left_cm, dist_right_cm) if d is not None])
        self.last_valid_dist = min_dist

        # State Transitions
        if self.state in (ObstacleState.CLEAR, ObstacleState.SLOWING_DOWN, ObstacleState.OBSTACLE_DETECTED):
            if min_dist <= self.cfg.ULTRASONIC_STOP_DISTANCE_CM or has_person_vision:
                self._set_state(ObstacleState.STOPPED_FOR_OBSTACLE)
            elif min_dist <= self.cfg.ULTRASONIC_SLOW_DISTANCE_CM:
                self._set_state(ObstacleState.SLOWING_DOWN)
            else:
                self._set_state(ObstacleState.CLEAR)

        elif self.state == ObstacleState.STOPPED_FOR_OBSTACLE:
            # Check if obstacle cleared
            if min_dist > self.cfg.ULTRASONIC_STOP_DISTANCE_CM and not has_person_vision:
                self._set_state(ObstacleState.CLEAR)
            else:
                # If stopped for > 3.0s, decide avoidance strategy or declare BLOCKED
                if now - self.last_state_change > 3.0:
                    d_left = dist_left_cm if dist_left_cm is not None else 0.0
                    d_right = dist_right_cm if dist_right_cm is not None else 0.0

                    # Choose whichever side has greater clearance
                    if max(d_left, d_right) > self.cfg.ULTRASONIC_SLOW_DISTANCE_CM:
                        self.avoid_direction = "left" if d_left > d_right else "right"
                        self.avoid_start_time = now
                        self._set_state(ObstacleState.AVOIDING)
                    else:
                        self._set_state(ObstacleState.BLOCKED)

        elif self.state == ObstacleState.AVOIDING:
            # Avoiding lasts max 2.5s before attempting route rejoining
            if now - self.avoid_start_time > 2.5:
                self._set_state(ObstacleState.REJOINING_ROUTE)
            elif min_dist <= self.cfg.ULTRASONIC_STOP_DISTANCE_CM:
                # If during avoidance a new obstacle is met, stop immediately
                self._set_state(ObstacleState.STOPPED_FOR_OBSTACLE)

        elif self.state == ObstacleState.REJOINING_ROUTE:
            if min_dist > self.cfg.ULTRASONIC_SLOW_DISTANCE_CM:
                self._set_state(ObstacleState.CLEAR)
            elif min_dist <= self.cfg.ULTRASONIC_STOP_DISTANCE_CM:
                self._set_state(ObstacleState.STOPPED_FOR_OBSTACLE)

        elif self.state == ObstacleState.BLOCKED:
            if min_dist > self.cfg.ULTRASONIC_SLOW_DISTANCE_CM and not has_person_vision:
                self._set_state(ObstacleState.CLEAR)

        elif self.state == ObstacleState.SENSOR_ERROR:
            if dist_left_cm is not None or dist_right_cm is not None:
                self._set_state(ObstacleState.CLEAR)

        return self.state

    def _set_state(self, new_state: ObstacleState):
        if self.state != new_state:
            logger.info(f"ObstacleAvoidance: {self.state.value} -> {new_state.value}")
            self.state = new_state
            self.last_state_change = time.time()
