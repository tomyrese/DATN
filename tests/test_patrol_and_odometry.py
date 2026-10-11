import os
import tempfile
import time
import pytest

from src.config import RobotConfig
from src.database.db import Database
from src.database.migrator import DatabaseMigrator
from src.database.seed import seed_database
from src.navigation.graph import NavigationGraph
from src.navigation.odometry import DeadReckoningOdometry
from src.navigation.patrol_controller import PatrolController

def test_dead_reckoning_odometry_kinematics():
    cfg = RobotConfig(SIMULATION_MODE=True)
    odom = DeadReckoningOdometry(cfg)
    odom.x = 10.0
    odom.y = 12.0
    odom.heading = 0.0

    state = odom.get_state()
    assert state["is_estimated"] is True
    assert state["confidence"] == 1.0

    # Moving straight forward (speed = 0.5 m/s for 1.0 second)
    odom.last_update_time = time.monotonic() - 1.0
    pose = odom.update(left_speed=0.5, right_speed=0.5)

    assert pose["x"] > 10.0
    assert pose["total_distance_m"] > 0
    # Confidence should decay over distance traveled
    assert pose["confidence"] <= 1.0

    # Landmark re-anchoring at reception desk POI
    odom.anchor_to_node("node_reception", x=10.0, y=12.0, heading=0.0, confidence=1.0)
    assert odom.x == 10.0
    assert odom.y == 12.0
    assert odom.confidence == 1.0

def test_patrol_controller_5min_idle_logic():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_patrol.db")
        db = Database(db_path=db_path)
        migrator = DatabaseMigrator(db)
        migrator.run_migrations()
        seed_database(db)

        graph = NavigationGraph(db)
        patrol = PatrolController(graph=graph, db=db, idle_timeout_s=5.0)

        assert patrol.is_patrolling is False

        # Simulate robot being idle for less than threshold
        patrol.check_idle_trigger(robot_is_idle=True, safety_can_move=True)
        assert patrol.is_patrolling is False

        # Fast forward idle activity time by 6 seconds
        patrol.last_activity_time = time.time() - 6.0
        patrol.check_idle_trigger(robot_is_idle=True, safety_can_move=True)
        # Should now start concourse patrol
        assert patrol.is_patrolling is True
        assert patrol.current_route_id is not None

        # Interrupt with higher-priority customer request
        patrol.stop_patrol(reason="Customer Escort Request")
        assert patrol.is_patrolling is False
