import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from src.database.db import Database, get_db
from src.navigation.graph import NavigationGraph, MapNode
from src.services.logging_service import logger

@dataclass
class PatrolWaypoint:
    node_id: str
    sequence_order: int
    dwell_seconds: int

class PatrolController:
    """
    Automated 5-Minute Idle Concourse Patrol Controller.
    - Tracks inactivity timer.
    - Triggers cyclic autonomous patrol through predefined waypoints when idle >= 300s.
    - Yields immediately upon arrival of higher-priority tasks (Escort, Delivery, E-Stop).
    """

    def __init__(self, graph: NavigationGraph, db: Optional[Database] = None, idle_timeout_s: float = 300.0):
        self.graph = graph
        self.db = db or get_db()
        self.idle_timeout_s = idle_timeout_s

        self.last_activity_time = time.time()
        self.is_patrolling = False
        self.current_route_id: Optional[str] = None
        self.current_waypoint_index = 0
        self.waypoints: List[PatrolWaypoint] = []
        self.dwell_start_time = 0.0
        self.is_dwelling = False

        self._load_active_route()

    def _load_active_route(self):
        row = self.db.fetchone("SELECT id, name FROM patrol_routes WHERE is_active = 1 LIMIT 1")
        if not row:
            return

        self.current_route_id = row["id"]
        wp_rows = self.db.fetchall("""
            SELECT node_id, sequence_order, dwell_seconds
            FROM patrol_route_waypoints
            WHERE route_id = ?
            ORDER BY sequence_order ASC
        """, (self.current_route_id,))

        self.waypoints = [
            PatrolWaypoint(
                node_id=r["node_id"],
                sequence_order=r["sequence_order"],
                dwell_seconds=r["dwell_seconds"]
            )
            for r in wp_rows
        ]
        logger.info(f"Loaded active patrol route '{row['name']}' with {len(self.waypoints)} waypoints")

    def record_activity(self):
        """Called whenever any task, movement command, or customer interaction occurs."""
        self.last_activity_time = time.time()
        if self.is_patrolling:
            self.stop_patrol(reason="User activity detected")

    def check_idle_trigger(self, robot_is_idle: bool, safety_can_move: bool) -> bool:
        """
        Evaluates whether the 5-minute inactivity condition has elapsed.
        Returns True if patrol should begin.
        """
        if self.is_patrolling:
            return False

        if not robot_is_idle or not safety_can_move:
            self.last_activity_time = time.time()
            return False

        elapsed_idle = time.time() - self.last_activity_time
        if elapsed_idle >= self.idle_timeout_s and len(self.waypoints) > 0:
            return self.start_patrol()

        return False

    def start_patrol(self) -> bool:
        if len(self.waypoints) == 0:
            self._load_active_route()
            if len(self.waypoints) == 0:
                return False

        self.is_patrolling = True
        self.current_waypoint_index = 0
        self.is_dwelling = False
        logger.info(f"5-Minute Idle Concourse Patrol initiated (Route: {self.current_route_id})")
        return True

    def stop_patrol(self, reason: str = "Interrupted"):
        if self.is_patrolling:
            logger.info(f"Patrol terminated: {reason}")
            self.is_patrolling = False
            self.is_dwelling = False
            self.last_activity_time = time.time()

    def get_current_patrol_target(self) -> Optional[MapNode]:
        if not self.is_patrolling or len(self.waypoints) == 0:
            return None

        wp = self.waypoints[self.current_waypoint_index]
        return self.graph.nodes.get(wp.node_id)

    def on_reached_waypoint(self) -> bool:
        """
        Called when robot arrives at current patrol waypoint.
        Handles dwell time and advances to next waypoint.
        """
        if not self.is_patrolling:
            return False

        now = time.time()
        wp = self.waypoints[self.current_waypoint_index]

        if not self.is_dwelling:
            self.is_dwelling = True
            self.dwell_start_time = now
            logger.info(f"Patrol arrived at waypoint {wp.sequence_order} ('{wp.node_id}'). Dwelling for {wp.dwell_seconds}s...")
            return False

        # Check dwell completion
        if now - self.dwell_start_time >= wp.dwell_seconds:
            self.is_dwelling = False
            self.current_waypoint_index = (self.current_waypoint_index + 1) % len(self.waypoints)
            next_wp = self.waypoints[self.current_waypoint_index]
            logger.info(f"Patrol advancing to next waypoint: {next_wp.node_id} (#{next_wp.sequence_order})")
            return True

        return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_patrolling": self.is_patrolling,
            "idle_elapsed_s": round(time.time() - self.last_activity_time, 1),
            "idle_timeout_s": self.idle_timeout_s,
            "current_route_id": self.current_route_id,
            "waypoint_index": self.current_waypoint_index,
            "total_waypoints": len(self.waypoints),
            "is_dwelling": self.is_dwelling
        }
