import pytest
from src.config import RobotConfig
from src.hardware.ultrasonic_sensor import UltrasonicSensors
from src.vision.obstacle_avoidance import ObstacleAvoidanceController, ObstacleState

def test_ultrasonic_sensor_simulation_and_filtering():
    cfg = RobotConfig(SIMULATION_MODE=True)
    sensors = UltrasonicSensors(cfg)
    assert sensors.simulation_mode is True

    # Default clear reading
    d1, d2 = sensors.read_distances()
    assert d1 == 180.0
    assert d2 == 180.0

    # Override simulation distances
    sensors.set_simulated_distances(dist1_cm=20.0, dist2_cm=45.0)
    d1_up, d2_up = sensors.read_distances()
    assert d1_up == 20.0
    assert d2_up == 45.0
    assert sensors.get_min_distance() == 20.0

def test_obstacle_avoidance_state_machine_transitions():
    cfg = RobotConfig(SIMULATION_MODE=True)
    obs = ObstacleAvoidanceController(cfg)

    # 1. Clear state (> 50cm, no person)
    st = obs.update(dist_left_cm=150.0, dist_right_cm=150.0, has_person_vision=False)
    assert st == ObstacleState.CLEAR

    # 2. Slowing down threshold (< 50cm, > 25cm)
    st = obs.update(dist_left_cm=40.0, dist_right_cm=42.0, has_person_vision=False)
    assert st == ObstacleState.SLOWING_DOWN

    # 3. Emergency stop threshold (< 25cm or person in path)
    st = obs.update(dist_left_cm=18.0, dist_right_cm=19.0, has_person_vision=False)
    assert st == ObstacleState.STOPPED_FOR_OBSTACLE

    # 4. Sensor disconnected (both None) -> SENSOR_ERROR
    st = obs.update(dist_left_cm=None, dist_right_cm=None, has_person_vision=False)
    assert st == ObstacleState.SENSOR_ERROR

    # 5. E-stop override
    st = obs.update(dist_left_cm=150.0, dist_right_cm=150.0, has_person_vision=False, is_e_stopped=True)
    assert st == ObstacleState.EMERGENCY_STOP
