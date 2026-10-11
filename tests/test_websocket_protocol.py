import json
import time
import pytest
from starlette.testclient import TestClient
from src.config import RobotConfig
from src.services.robot_controller import RobotController

@pytest.fixture
def ws_setup():
    cfg = RobotConfig(SIMULATION_MODE=True, DRIVE_COMMAND_TIMEOUT=0.1)
    robot = RobotController(cfg)
    robot.mall.db.execute("UPDATE delivery_orders SET status = 'COMPLETED' WHERE status NOT IN ('COMPLETED', 'CANCELLED')")
    robot.mall.active_order = None
    robot.mall.active_order_id = None
    robot.start(start_server=False)
    token = robot.auth_manager.create_session_token()
    tc = TestClient(robot.api_app)
    yield tc, robot, token
    robot.shutdown()

def receive_until_type(ws, target_type: str, max_tries: int = 10) -> dict:
    for _ in range(max_tries):
        msg = ws.receive_json()
        if msg.get("type") == target_type:
            return msg
    raise TimeoutError(f"Did not receive message of type {target_type}")

def test_websocket_unauthorized(ws_setup):
    tc, _, _ = ws_setup
    with tc.websocket_connect("/ws/v1/control?token=INVALID") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "error"
        assert msg["code"] == "AUTH_INVALID"

def test_websocket_hello_and_drive(ws_setup):
    tc, robot, token = ws_setup
    with tc.websocket_connect(f"/ws/v1/control?token={token}") as ws:
        ws.send_json({
            "type": "hello",
            "protocol": 1,
            "client": "android",
            "appVersion": "1.0.0"
        })
        ack = receive_until_type(ws, "hello_ack")
        assert ack["type"] == "hello_ack"
        assert ack["protocol"] == 1
        assert ack["robotId"] == "RBT01"

        ws.send_json({"type": "heartbeat", "timestamp": time.time()})
        hb_ack = receive_until_type(ws, "heartbeat_ack")
        assert hb_ack["type"] == "heartbeat_ack"

        ws.send_json({"type": "drive", "direction": "forward", "speed": 0.4, "seq": 101})
        drive_ack = receive_until_type(ws, "command_ack")
        assert drive_ack["type"] == "command_ack"
        assert drive_ack["seq"] == 101
        assert drive_ack["accepted"] is True
        assert robot.motor.is_moving()

        ws.send_json({"type": "stop", "seq": 102})
        stop_ack = receive_until_type(ws, "command_ack")
        assert stop_ack["type"] == "command_ack"
        assert stop_ack["seq"] == 102
        assert stop_ack["accepted"] is True
        assert not robot.motor.is_moving()

def test_websocket_person_safety_rejection(ws_setup):
    tc, robot, token = ws_setup
    with tc.websocket_connect(f"/ws/v1/control?token={token}") as ws:
        robot.detector.set_mock_person(True, 0.92)
        time.sleep(0.05)

        ws.send_json({"type": "drive", "direction": "forward", "speed": 0.4, "seq": 201})
        ack = receive_until_type(ws, "command_ack")
        assert ack["type"] == "command_ack"
        assert ack["accepted"] is False
        assert ack["reason"] in ("PERSON_DETECTED", "SAFETY_BLOCKED")
        assert not robot.motor.is_moving()

def test_websocket_motor_test(ws_setup):
    tc, robot, token = ws_setup
    with tc.websocket_connect(f"/ws/v1/control?token={token}") as ws:
        ws.send_json({"type": "motor_test", "motor": 2, "speed": 0.2, "seq": 301})
        ack = receive_until_type(ws, "command_ack")
        assert ack["type"] == "command_ack"
        assert ack["accepted"] is True
        assert robot.motor.get_speeds()[2] == 0.2
