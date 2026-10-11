import time
import math
from typing import Dict, Any, Optional
from src.config import RobotConfig, config
from src.services.logging_service import logger

class DeadReckoningOdometry:
    """
    Kinematic Dead-Reckoning Odometry for 4-DC Motor Differential Drive.
    
    IMPORTANT TECHNICAL SPECIFICATION & CALIBRATION:
    ------------------------------------------------
    Current DC motors do not possess hardware optical wheel encoders.
    All location metrics are mathematically INTEGRATED via motor execution runtime (dt),
    calibrated linear velocity (v), and angular turning rate (omega).
    
    To maintain data honesty:
    - Every position update carries a 'confidence' metric (1.0 down to 0.2).
    - Status is explicitly flagged as 'is_estimated: True'.
    - Position can be re-anchored to 100% confidence when reaching known POI nodes or QR stops.
    """

    def __init__(self, cfg: Optional[RobotConfig] = None):
        self.cfg = cfg or config
        self.x: float = 50.0  # Percentage or meter coordinates
        self.y: float = 70.0
        self.heading: float = 0.0  # Radians (0 = North, pi/2 = East, etc.)
        self.floor_id: str = "floor_t1"

        self.wheel_base_m: float = self.cfg.ODOMETRY_WHEEL_BASE_M
        self.max_v: float = self.cfg.ODOMETRY_MAX_LINEAR_SPEED_M_S
        self.max_w: float = self.cfg.ODOMETRY_MAX_ANGULAR_SPEED_RAD_S

        self.linear_velocity: float = 0.0
        self.angular_velocity: float = 0.0
        self.total_distance_traveled: float = 0.0
        self.confidence: float = 1.0
        self.last_update_time: float = time.monotonic()
        self.last_anchor_time: float = time.time()
        self.last_anchored_node_id: Optional[str] = "node_center"

    def update(self, left_speed: float, right_speed: float) -> Dict[str, Any]:
        """
        Integrates differential drive kinematics over dt.
        left_speed, right_speed: normalized [-1.0, 1.0].
        """
        now = time.monotonic()
        dt = max(0.001, min(0.5, now - self.last_update_time))
        self.last_update_time = now

        # Convert normalized motor commands to physical velocity
        v_l = left_speed * self.max_v
        v_r = right_speed * self.max_v

        # Differential drive kinematic equations
        v = (v_r + v_l) / 2.0
        w = (v_r - v_l) / self.wheel_base_m

        self.linear_velocity = v
        self.angular_velocity = w

        # Position integration with Runge-Kutta 2nd order approximation
        d_theta = w * dt
        mid_theta = self.heading + (d_theta / 2.0)

        dx = v * math.cos(mid_theta) * dt
        dy = v * math.sin(mid_theta) * dt

        self.x += dx
        self.y += dy
        self.heading = (self.heading + d_theta) % (2.0 * math.pi)

        dist_step = abs(v) * dt
        self.total_distance_traveled += dist_step

        # Confidence decay: decays by 0.005 per meter traveled and 0.001 per second moving
        if abs(v) > 0.01 or abs(w) > 0.01:
            decay = (dist_step * 0.015) + (dt * 0.002)
            self.confidence = max(0.25, self.confidence - decay)

        return self.get_state()

    def anchor_to_node(self, node_id: str, x: float, y: float, heading: Optional[float] = None, confidence: float = 1.0):
        """
        Re-anchors robot position to a verified physical landmark/node,
        restoring position confidence back to 1.0.
        """
        self.x = x
        self.y = y
        if heading is not None:
            self.heading = heading
        self.confidence = confidence
        self.last_anchor_time = time.time()
        self.last_anchored_node_id = node_id
        logger.info(f"Odometry re-anchored at node '{node_id}' ({x:.1f}, {y:.1f}), confidence reset to {confidence:.2f}")

    def get_state(self) -> Dict[str, Any]:
        return {
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "heading": round(self.heading, 3),
            "heading_degrees": round(math.degrees(self.heading), 1),
            "floor_id": self.floor_id,
            "linear_velocity": round(self.linear_velocity, 2),
            "angular_velocity": round(self.angular_velocity, 2),
            "confidence": round(self.confidence, 2),
            "is_estimated": True,
            "is_confirmed": (self.confidence >= 0.90),
            "total_distance_m": round(self.total_distance_traveled, 2),
            "last_anchor_node": self.last_anchored_node_id
        }
