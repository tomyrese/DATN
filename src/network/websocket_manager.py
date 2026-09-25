import asyncio
import json
import time
from typing import Optional, Any, Set
from fastapi import WebSocket, WebSocketDisconnect
from src.config import RobotConfig, config
from src.network.auth_manager import AuthManager
from src.network.connection_watchdog import ConnectionWatchdog
from src.network.protocol import (
    HelloMessage, HelloAckMessage, DriveMessage, TankDriveMessage,
    StopMessage, EmergencyStopMessage, EmergencyResetMessage, MotorTestMessage,
    HeartbeatMessage, HeartbeatAckMessage, CommandAckMessage, SafetyEventMessage,
    TelemetryMessage, ErrorMessage
)
from src.services.logging_service import logger

class WebSocketManager:
    def __init__(self, robot_controller: Any, auth_manager: AuthManager, cfg: Optional[RobotConfig] = None):
        self.robot = robot_controller
        self.auth = auth_manager
        self.cfg = cfg or config
        self.active_websockets: Set[WebSocket] = set()
        self.connection_watchdog = ConnectionWatchdog(self.cfg)
        self.lock = asyncio.Lock()
        self.last_seq: Optional[int] = None

    def is_client_connected(self) -> bool:
        return len(self.active_websockets) > 0 and self.connection_watchdog.is_connected

    async def connect(self, websocket: WebSocket, token: Optional[str]) -> bool:
        await websocket.accept()

        # Token validation: Allow guest/anonymous/empty if pairing is disabled or guest access
        is_token_valid = (
            not self.cfg.PAIRING_ENABLED or
            not token or
            token in ("guest", "anonymous", "") or
            self.auth.validate_token(token)
        )

        if not is_token_valid:
            err = ErrorMessage(code="AUTH_INVALID", message="Invalid session token")
            await websocket.send_text(err.model_dump_json())
            await websocket.close(code=4003)
            logger.warning("WebSocket connection rejected: invalid token")
            return False

        async with self.lock:
            self.active_websockets.add(websocket)
            self.connection_watchdog.on_connected()
            logger.info(f"WebSocket client connected and authenticated (total active: {len(self.active_websockets)})")
            return True

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            if websocket in self.active_websockets:
                self.active_websockets.remove(websocket)
                logger.info(f"WebSocket client disconnected (remaining active: {len(self.active_websockets)})")

            if len(self.active_websockets) == 0:
                self.connection_watchdog.on_disconnected()
                self.robot.handle_remote_disconnect()

    async def send_message(self, message: Any):
        if not self.active_websockets:
            return

        try:
            if hasattr(message, "model_dump_json"):
                text = message.model_dump_json()
            elif isinstance(message, dict):
                text = json.dumps(message)
            else:
                text = str(message)
        except Exception:
            return

        dead_sockets = []
        for ws in list(self.active_websockets):
            try:
                await ws.send_text(text)
            except Exception:
                dead_sockets.append(ws)

        if dead_sockets:
            async with self.lock:
                for ws in dead_sockets:
                    if ws in self.active_websockets:
                        self.active_websockets.remove(ws)
                if len(self.active_websockets) == 0:
                    self.connection_watchdog.on_disconnected()
                    self.robot.handle_remote_disconnect()

    async def broadcast_safety_event(self, event_type: str, confidence: Optional[float] = None):
        msg = SafetyEventMessage(event=event_type, confidence=confidence)
        await self.send_message(msg)

    async def handle_message(self, websocket: WebSocket, text: str):
        try:
            data = json.loads(text)
        except Exception:
            err = ErrorMessage(code="INVALID_JSON", message="Payload must be valid JSON")
            await websocket.send_text(err.model_dump_json())
            return

        msg_type = data.get("type")
        seq = data.get("seq")

        if msg_type == "hello":
            try:
                hello_msg = HelloMessage(**data)
                ack = HelloAckMessage(
                    robotId=self.cfg.ROBOT_ID,
                    robotName=self.cfg.ROBOT_NAME,
                    state=self.robot.state.value
                )
                await websocket.send_text(ack.model_dump_json())
            except Exception as e:
                err = ErrorMessage(code="INVALID_HELLO", message=str(e))
                await websocket.send_text(err.model_dump_json())

        elif msg_type == "heartbeat":
            self.connection_watchdog.feed_heartbeat()
            ack = HeartbeatAckMessage(timestamp=time.time())
            await websocket.send_text(ack.model_dump_json())

        elif msg_type == "drive":
            try:
                drive_msg = DriveMessage(**data)
                self.connection_watchdog.feed_drive_command()
                accepted, reason = self.robot.handle_remote_drive(drive_msg.direction, drive_msg.speed)
                ack = CommandAckMessage(seq=seq, accepted=accepted, reason=reason)
                await websocket.send_text(ack.model_dump_json())
            except Exception as e:
                ack = CommandAckMessage(seq=seq, accepted=False, reason=str(e))
                await websocket.send_text(ack.model_dump_json())

        elif msg_type == "tank_drive":
            try:
                tank_msg = TankDriveMessage(**data)
                self.connection_watchdog.feed_drive_command()
                accepted, reason = self.robot.handle_remote_tank_drive(tank_msg.left, tank_msg.right)
                ack = CommandAckMessage(seq=seq, accepted=accepted, reason=reason)
                await websocket.send_text(ack.model_dump_json())
            except Exception as e:
                ack = CommandAckMessage(seq=seq, accepted=False, reason=str(e))
                await websocket.send_text(ack.model_dump_json())

        elif msg_type == "stop":
            self.connection_watchdog.feed_heartbeat()
            self.robot.handle_remote_stop()
            ack = CommandAckMessage(seq=seq, accepted=True)
            await websocket.send_text(ack.model_dump_json())

        elif msg_type == "emergency_stop":
            self.robot.handle_remote_emergency_stop()
            ack = CommandAckMessage(seq=seq, accepted=True)
            await websocket.send_text(ack.model_dump_json())

        elif msg_type == "emergency_reset":
            accepted, reason = self.robot.handle_remote_emergency_reset()
            ack = CommandAckMessage(seq=seq, accepted=accepted, reason=reason)
            await websocket.send_text(ack.model_dump_json())

        elif msg_type == "motor_test":
            try:
                mt_msg = MotorTestMessage(**data)
                self.connection_watchdog.feed_drive_command()
                accepted, reason = self.robot.handle_remote_motor_test(mt_msg.motor, mt_msg.speed)
                ack = CommandAckMessage(seq=seq, accepted=accepted, reason=reason)
                await websocket.send_text(ack.model_dump_json())
            except Exception as e:
                ack = CommandAckMessage(seq=seq, accepted=False, reason=str(e))
                await websocket.send_text(ack.model_dump_json())

        else:
            err = ErrorMessage(code="UNKNOWN_MESSAGE_TYPE", message=f"Type {msg_type} is not supported")
            await websocket.send_text(err.model_dump_json())
