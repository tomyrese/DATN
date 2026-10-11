import time
import math
from typing import List, Optional, Tuple, Dict, Any
from src.navigation.graph import NavigationGraph, MapNode
from src.navigation.planner import AStarPlanner
from src.navigation.odometry import DeadReckoningOdometry
from src.navigation.patrol_controller import PatrolController
from src.vision.obstacle_avoidance import ObstacleState
from src.config import RobotConfig, config
from src.services.logging_service import logger

class AutonomousNavigator:
    """
    High-Level Autonomous Navigation Executive:
    - Plans optimal topological routes using A*.
    - Manages waypoint tracking and differential steering calculations.
    - Tracks planned path vs executed path history.
    - Handles obstacle rerouting and route rejoining.
    - Integrates the 5-Minute Idle Patrol cycle.
    """

    def __init__(self, cfg: Optional[RobotConfig] = None):
        self.cfg = cfg or config
        self.graph = NavigationGraph()
        self.planner = AStarPlanner(self.graph)
        self.odometry = DeadReckoningOdometry(self.cfg)
        self.patrol = PatrolController(self.graph, idle_timeout_s=self.cfg.PATROL_IDLE_TIMEOUT)

        self.current_path: List[MapNode] = []
        self.current_waypoint_idx: int = 0
        self.target_poi_id: Optional[str] = None
        self.target_name: Optional[str] = None
        self.navigation_status: str = "IDLE"  # IDLE, NAVIGATING, AVOIDING, ARRIVED, BLOCKED, CANCELLED

        self.executed_path: List[Dict[str, float]] = []
        self.last_path_record_time = time.time()
        self.arrival_tolerance = 2.5  # Coordinate tolerance for waypoint arrival

    def plan_mission_to_poi(self, poi_id: str, poi_name: str, target_x: float, target_y: float) -> bool:
        """Plans path from current robot position to target POI."""
        self.patrol.record_activity()

        start_node = self.graph.get_nearest_node(self.odometry.x, self.odometry.y)
        goal_node = self.graph.get_nearest_node(target_x, target_y)

        if not start_node or not goal_node:
            logger.error(f"Cannot find nearest map node for mission to '{poi_name}'")
            self.navigation_status = "BLOCKED"
            return False

        path, total_dist = self.planner.plan(start_node.id, goal_node.id)
        if len(path) == 0:
            logger.warning(f"No path found to '{poi_name}'")
            self.navigation_status = "BLOCKED"
            return False

        self.current_path = path
        self.current_waypoint_idx = 0
        self.target_poi_id = poi_id
        self.target_name = poi_name
        self.navigation_status = "NAVIGATING"
        self.executed_path = [{"x": self.odometry.x, "y": self.odometry.y}]
        logger.info(f"Autonomous mission planned to '{poi_name}': {len(path)} waypoints, {total_dist:.1f}m")
        return True

    def update_navigation_step(self, obstacle_state: ObstacleState) -> Tuple[float, float, bool]:
        """
        Executes single navigation control step.
        Returns: (left_speed, right_speed, is_arrived)
        """
        now = time.time()
        if now - self.last_path_record_time >= 0.5:
            self.executed_path.append({"x": round(self.odometry.x, 2), "y": round(self.odometry.y, 2)})
            if len(self.executed_path) > 300:
                self.executed_path.pop(0)
            self.last_path_record_time = now

        # Handle Obstacle Avoidance State Machine
        if obstacle_state == ObstacleState.STOPPED_FOR_OBSTACLE or obstacle_state == ObstacleState.BLOCKED:
            self.navigation_status = "BLOCKED" if obstacle_state == ObstacleState.BLOCKED else "OBSTACLE_HALTED"
            return (0.0, 0.0, False)

        if obstacle_state == ObstacleState.AVOIDING:
            self.navigation_status = "AVOIDING"
            # Gentle turning maneuver around obstacle
            avoid_speed = min(0.20, self.cfg.DEFAULT_SPEED)
            return (avoid_speed * 0.4, avoid_speed)

        # Check Patrol Cycle if in IDLE
        if self.navigation_status == "IDLE":
            if self.patrol.is_patrolling:
                target_wp_node = self.patrol.get_current_patrol_target()
                if target_wp_node:
                    return self._drive_toward_point(target_wp_node.x, target_wp_node.y, is_patrol=True)
            return (0.0, 0.0, False)

        if self.navigation_status != "NAVIGATING" or len(self.current_path) == 0:
            return (0.0, 0.0, False)

        # Active Mission to POI
        target_node = self.current_path[self.current_waypoint_idx]
        left_spd, right_spd, reached = self._drive_toward_point(target_node.x, target_node.y, is_patrol=False)

        if reached:
            # Re-anchor odometry at verified node
            self.odometry.anchor_to_node(target_node.id, target_node.x, target_node.y)

            if self.current_waypoint_idx < len(self.current_path) - 1:
                self.current_waypoint_idx += 1
                logger.info(f"Advanced to waypoint {self.current_waypoint_idx + 1}/{len(self.current_path)}: '{self.current_path[self.current_waypoint_idx].name}'")
            else:
                self.navigation_status = "ARRIVED"
                logger.info(f"Robot successfully arrived at destination: '{self.target_name}'!")
                return (0.0, 0.0, True)

        return (left_spd, right_spd, False)

    def _drive_toward_point(self, goal_x: float, goal_y: float, is_patrol: bool = False) -> Tuple[float, float, bool]:
        dx = goal_x - self.odometry.x
        dy = goal_y - self.odometry.y
        dist = math.sqrt(dx**2 + dy**2)

        if dist <= self.arrival_tolerance:
            if is_patrol:
                self.patrol.on_reached_waypoint()
            return (0.0, 0.0, True)

        # Target angle
        target_heading = math.atan2(dy, dx)
        angle_diff = (target_heading - self.odometry.heading + math.pi) % (2.0 * math.pi) - math.pi

        cruise_speed = min(0.30 if is_patrol else self.cfg.DEFAULT_SPEED, 0.40)

        # Steering control
        if abs(angle_diff) > 0.45:
            # Turn in place toward target
            turn_rate = 0.25 if angle_diff > 0 else -0.25
            return (-turn_rate, turn_rate, False)
        else:
            # Drive forward with proportional turning adjustment
            kp = 0.35
            steering = angle_diff * kp
            left_spd = max(-1.0, min(1.0, cruise_speed - steering))
            right_spd = max(-1.0, min(1.0, cruise_speed + steering))
            return (left_spd, right_spd, False)

    def cancel_navigation(self):
        self.navigation_status = "CANCELLED"
        self.current_path = []
        self.target_poi_id = None
        self.target_name = None
        self.patrol.record_activity()
        logger.info("Navigation mission cancelled by operator")

    def get_progress_percent(self) -> int:
        if len(self.current_path) <= 1:
            return 100 if self.navigation_status == "ARRIVED" else 0
        return int((self.current_waypoint_idx / (len(self.current_path) - 1)) * 100)

    def get_snapshot(self) -> Dict[str, Any]:
        return {
            "status": self.navigation_status,
            "target_poi_id": self.target_poi_id,
            "target_name": self.target_name,
            "current_progress": self.get_progress_percent(),
            "odometry": self.odometry.get_state(),
            "patrol": self.patrol.get_status(),
            "planned_path": [{"id": n.id, "x": n.x, "y": n.y, "name": n.name} for n in self.current_path],
            "executed_path": self.executed_path[-80:]
        }
