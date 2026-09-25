import asyncio
import collections
import threading
import time
from typing import Optional, Tuple, List, Dict, Any
import uvicorn
from src.config import RobotConfig, config
from src.state import RobotState, MovementCommand
from src.hardware.motor_controller import MotorController
from src.hardware.camera_service import CameraService
from src.hardware.oled_controller import OLEDController
from src.vision.person_detector import PersonDetector
from src.safety.safety_controller import SafetyController
from src.safety.camera_watchdog import CameraWatchdog
from src.safety.system_watchdog import SystemWatchdog
from src.network.auth_manager import AuthManager
from src.network.pairing_manager import PairingManager
from src.network.camera_stream import CameraStreamManager
from src.network.telemetry_service import TelemetryService
from src.network.websocket_manager import WebSocketManager
from src.network.api_server import create_api_server
from src.utils.network import get_ip_address
from src.services.logging_service import logger
from src.services.mall_service import MallService

class RobotController:
    def __init__(self, cfg: Optional[RobotConfig] = None):
        self.cfg = cfg or config
        self.state = RobotState.BOOTING
        self.current_motion = RobotState.STOPPED
        self.running = False
        self.ip_address = get_ip_address()

        self.mall = MallService()
        self.motor = MotorController(self.cfg)
        self.oled = OLEDController(self.cfg)
        self.camera = CameraService(self.cfg)
        self.detector = PersonDetector(self.cfg)
        self.safety = SafetyController(self.cfg)
        self.camera_watchdog = CameraWatchdog(self.cfg)
        self.system_watchdog = SystemWatchdog(self.cfg)

        self.auth_manager = AuthManager()
        self.pairing_manager = PairingManager(self.cfg)
        self.camera_stream = CameraStreamManager(self.camera, self.cfg)
        self.telemetry_service = TelemetryService(self.cfg)
        self.websocket_manager = WebSocketManager(self, self.auth_manager, self.cfg)

        self.recent_logs = collections.deque(maxlen=60)
        self.api_app = create_api_server(
            self, self.auth_manager, self.pairing_manager,
            self.websocket_manager, self.camera_stream, self.cfg
        )

        self.server_thread: Optional[threading.Thread] = None
        self.uvicorn_server: Optional[uvicorn.Server] = None
        self.loop_thread: Optional[threading.Thread] = None
        self.async_loop: Optional[asyncio.AbstractEventLoop] = None
        self.last_perf_log_time = time.monotonic()
        self.last_telemetry_time = 0.0
        self.was_person_active = False

    def log_event(self, message: str):
        now_str = time.strftime("%H:%M:%S")
        self.recent_logs.append(f"[{now_str}] {message}")

    def get_recent_logs(self) -> List[str]:
        return list(self.recent_logs)

    def trigger_pairing_mode(self):
        code, payload = self.pairing_manager.start_pairing(self.ip_address, self.cfg.SERVER_PORT)
        self.state = RobotState.PAIRING
        qr_img = self.pairing_manager.generate_qr_image(56)
        self.oled.update_state(RobotState.PAIRING, {
            "qr_image": qr_img,
            "pair_code": code,
            "ip": self.ip_address,
            "remaining_sec": self.pairing_manager.get_remaining_seconds()
        })
        self.log_event(f"Pairing mode started (Code: {code})")

    def handle_pairing_success(self):
        self.state = RobotState.CONNECTED
        self.oled.update_state(RobotState.CONNECTED, {"ip": self.ip_address, "speed": self.cfg.DEFAULT_SPEED})
        self.log_event("Pairing completed with client")

    def start(self, start_server: bool = True) -> bool:
        self.oled.update_state(RobotState.BOOTING)
        logger.info("Starting Robot Controller...")
        self.log_event("Robot system booting")

        camera_ok = self.camera.start()
        if not camera_ok and self.cfg.CAMERA_ENABLED and not self.cfg.SIMULATION_MODE:
            self.state = RobotState.CAMERA_ERROR
            self.safety.set_camera_error(True)
            self.oled.update_state(RobotState.CAMERA_ERROR)
            logger.error("Camera failed to start. Motor movement is locked.")
            self.log_event("Camera start failed - Movement locked")
            return False

        self.motor.enable()
        self.state = RobotState.READY
        self.current_motion = RobotState.STOPPED

        if self.cfg.PAIRING_ENABLED and not self.auth_manager.has_paired_clients():
            self.trigger_pairing_mode()
        else:
            self.oled.update_state(RobotState.READY, {"ip": self.ip_address})

        self.running = True
        if start_server:
            self._start_server_thread()

        self.loop_thread = threading.Thread(target=self._main_orchestration_loop, daemon=True)
        self.loop_thread.start()
        logger.info("Robot Controller started successfully")
        self.log_event("Robot controller ready")
        return True

    def _start_server_thread(self):
        uvicorn_cfg = uvicorn.Config(
            app=self.api_app,
            host=self.cfg.SERVER_HOST,
            port=self.cfg.SERVER_PORT,
            log_level="warning",
            access_log=False
        )
        self.uvicorn_server = uvicorn.Server(uvicorn_cfg)

        def run_uvicorn():
            self.async_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.async_loop)
            try:
                self.async_loop.run_until_complete(self.uvicorn_server.serve())
            except Exception:
                pass

        self.server_thread = threading.Thread(target=run_uvicorn, daemon=True)
        self.server_thread.start()
        logger.info(f"API & WebSocket Server listening on {self.cfg.SERVER_HOST}:{self.cfg.SERVER_PORT}")

    def _main_orchestration_loop(self):
        while self.running:
            try:
                self.system_watchdog.heartbeat()
                frame, frame_time = self.camera.get_latest_frame()
                is_moving = self.motor.is_moving()

                if frame is not None and frame_time > 0:
                    self.camera_watchdog.feed_frame(frame_time)

                watchdog_ok = self.camera_watchdog.check(is_moving)
                if not watchdog_ok:
                    self.safety.set_camera_error(True)
                    if is_moving:
                        self.motor.stop()
                        self.current_motion = RobotState.STOPPED
                        self.state = RobotState.CAMERA_ERROR
                        self.oled.update_state(RobotState.CAMERA_ERROR)
                        self._schedule_async(self.websocket_manager.broadcast_safety_event("camera_error"))
                        self.log_event("Camera watchdog failure")
                else:
                    if self.safety.has_camera_error:
                        self.safety.set_camera_error(False)

                detections = self.detector.detect(frame)
                self.camera_watchdog.feed_inference(detections.timestamp)

                should_stop = self.safety.update_vision_safety(detections, is_moving)
                if should_stop:
                    self.motor.stop()
                    self.current_motion = RobotState.STOPPED
                    self.state = RobotState.SAFETY_STOP
                    self.oled.update_state(RobotState.PERSON_DETECTED, {"confidence": detections.max_confidence_in_stop_zone})
                    self.log_event(f"Safety stop: Person detected (conf={detections.max_confidence_in_stop_zone:.2f})")

                if self.safety.person_active and not self.was_person_active:
                    self.was_person_active = True
                    self._schedule_async(self.websocket_manager.broadcast_safety_event("person_detected", detections.max_confidence_in_stop_zone))
                elif not self.safety.person_active and self.was_person_active:
                    self.was_person_active = False
                    self._schedule_async(self.websocket_manager.broadcast_safety_event("person_clear"))
                    self.log_event("Person cleared from safety zone")

                if not self.safety.person_active and self.state == RobotState.SAFETY_STOP:
                    if not self.cfg.AUTO_RESUME_AFTER_PERSON_CLEAR:
                        self.state = RobotState.STOPPED
                        if self.websocket_manager.is_client_connected():
                            self.oled.update_state(RobotState.CONNECTED, {"ip": self.ip_address, "speed": self.cfg.DEFAULT_SPEED})
                        else:
                            self.oled.update_state(RobotState.STOPPED, {"ip": self.ip_address})

                conn_alive, drive_valid = self.websocket_manager.connection_watchdog.check()
                if not drive_valid and is_moving:
                    self.motor.stop()
                    self.current_motion = RobotState.STOPPED
                    if self.safety.can_move():
                        self.state = RobotState.CONNECTED if self.websocket_manager.is_client_connected() else RobotState.STOPPED
                        self.oled.update_state(self.state, {"ip": self.ip_address, "speed": self.cfg.DEFAULT_SPEED})
                    self.log_event("Drive command lease expired - Motor stopped")

                effective_state = self.safety.get_effective_robot_state(self.current_motion)
                if self.state != effective_state and self.state != RobotState.PAIRING:
                    self.state = effective_state
                    self.oled.update_state(self.state, {
                        "ip": self.ip_address,
                        "speed": self.cfg.DEFAULT_SPEED,
                        "confidence": detections.max_confidence_in_stop_zone
                    })

                if self.state == RobotState.PAIRING:
                    if self.pairing_manager.is_pairing_active():
                        qr_img = self.pairing_manager.generate_qr_image(56)
                        self.oled.update_state(RobotState.PAIRING, {
                            "qr_image": qr_img,
                            "pair_code": self.pairing_manager.current_code,
                            "ip": self.ip_address,
                            "remaining_sec": self.pairing_manager.get_remaining_seconds()
                        })
                    else:
                        self.state = RobotState.READY
                        self.oled.update_state(RobotState.READY, {"ip": self.ip_address})

                now = time.monotonic()
                if now - self.last_telemetry_time >= self.cfg.TELEMETRY_INTERVAL:
                    self._broadcast_telemetry_snapshot(detections)
                    self.last_telemetry_time = now

                if now - self.last_perf_log_time >= 5.0:
                    avg_inf = self.detector.get_average_inference_time_ms()
                    logger.info(f"STATUS state={self.state.value} cam_fps={self.camera.get_fps():.1f} inf_time={avg_inf:.1f}ms moving={is_moving}")
                    self.last_perf_log_time = now

                time.sleep(0.01)
            except Exception as e:
                critical = self.system_watchdog.record_error(e)
                if critical:
                    self.safety.set_system_error(True)
                    self.motor.emergency_stop()
                    self.state = RobotState.SYSTEM_ERROR
                    self.oled.update_state(RobotState.SYSTEM_ERROR, {"error": str(e)})
                    self.log_event(f"Critical system error: {e}")
                time.sleep(0.05)

    def _schedule_async(self, coro):
        if self.async_loop and self.async_loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, self.async_loop)
        else:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(coro)
                else:
                    coro.close()
            except Exception:
                try:
                    coro.close()
                except Exception:
                    pass

    def _broadcast_telemetry_snapshot(self, detections: Any):
        if not self.websocket_manager.is_client_connected():
            return

        bbox = None
        if detections.detections:
            bbox = list(detections.detections[0].bbox)

        telemetry = self.telemetry_service.build_telemetry(
            robot_state=self.state.value,
            safety_state=self.safety.safety_state.value,
            target_speed=self.cfg.DEFAULT_SPEED,
            motor_speeds=self.motor.get_speeds(),
            person_detected=self.safety.person_active,
            person_confidence=detections.max_confidence_in_stop_zone,
            camera_ok=self.camera.is_alive(),
            detector_ok=self.detector.runtime != "none",
            oled_ok=self.oled.available,
            motor_ok=self.motor.enabled,
            camera_fps=self.camera.get_fps(),
            inference_fps=1000.0 / max(1.0, detections.inference_time_ms) if detections.inference_time_ms > 0 else 0.0,
            person_bbox=bbox
        )
        self._schedule_async(self.websocket_manager.send_message(telemetry))

    def get_telemetry_snapshot(self) -> Dict[str, Any]:
        return {
            "robotState": self.state.value,
            "safetyState": self.safety.safety_state.value,
            "motorSpeeds": self.motor.get_speeds(),
            "personDetected": self.safety.person_active,
            "cameraOk": self.camera.is_alive(),
            "detectorOk": self.detector.runtime != "none",
            "oledOk": self.oled.available,
            "motorOk": self.motor.enabled,
            "cameraFps": self.camera.get_fps(),
            "ip": self.ip_address
        }

    def handle_remote_drive(self, direction: str, speed: float) -> Tuple[bool, Optional[str]]:
        if not self.safety.can_move():
            reason = "PERSON_DETECTED" if self.safety.person_active else "SAFETY_BLOCKED"
            if self.safety.is_emergency_stopped:
                reason = "EMERGENCY_ACTIVE"
            elif self.safety.has_camera_error:
                reason = "CAMERA_ERROR"
            return False, reason

        target_speed = max(-1.0, min(1.0, speed))
        dir_lower = direction.lower()

        if dir_lower == "forward":
            self.motor.forward(target_speed)
            self.current_motion = RobotState.FORWARD
            self.state = RobotState.FORWARD
        elif dir_lower == "backward":
            self.motor.backward(target_speed)
            self.current_motion = RobotState.BACKWARD
            self.state = RobotState.BACKWARD
        elif dir_lower == "left":
            self.motor.turn_left(target_speed)
            self.current_motion = RobotState.TURN_LEFT
            self.state = RobotState.TURN_LEFT
        elif dir_lower == "right":
            self.motor.turn_right(target_speed)
            self.current_motion = RobotState.TURN_RIGHT
            self.state = RobotState.TURN_RIGHT
        else:
            return False, f"Unknown direction: {direction}"

        self.oled.update_state(self.state, {"speed": target_speed})
        return True, None

    def handle_remote_tank_drive(self, left: float, right: float) -> Tuple[bool, Optional[str]]:
        if not self.safety.can_move():
            reason = "PERSON_DETECTED" if self.safety.person_active else "SAFETY_BLOCKED"
            return False, reason

        clamped_left = max(-1.0, min(1.0, left))
        clamped_right = max(-1.0, min(1.0, right))
        self.motor.drive(clamped_left, clamped_right)
        self.current_motion = RobotState.FORWARD if clamped_left >= 0 and clamped_right >= 0 else RobotState.BACKWARD
        self.state = self.current_motion
        return True, None

    def handle_remote_stop(self):
        self.motor.stop()
        self.current_motion = RobotState.STOPPED
        if self.safety.can_move():
            self.state = RobotState.CONNECTED if self.websocket_manager.is_client_connected() else RobotState.STOPPED
            self.oled.update_state(self.state, {"ip": self.ip_address, "speed": self.cfg.DEFAULT_SPEED})

    def handle_remote_emergency_stop(self):
        self.safety.trigger_emergency_stop()
        self.motor.emergency_stop()
        self.current_motion = RobotState.STOPPED
        self.state = RobotState.SAFETY_STOP
        self.oled.update_state(RobotState.SAFETY_STOP)
        self._schedule_async(self.websocket_manager.broadcast_safety_event("emergency_stop"))
        self.log_event("Emergency stop triggered")

    def handle_remote_emergency_reset(self) -> Tuple[bool, Optional[str]]:
        if not self.safety.reset_emergency_stop():
            reason = "PERSON_DETECTED" if self.safety.person_active else "SYSTEM_ERROR"
            return False, reason

        self.motor.enable()
        self.current_motion = RobotState.STOPPED
        self.state = RobotState.CONNECTED if self.websocket_manager.is_client_connected() else RobotState.STOPPED
        self.oled.update_state(self.state, {"ip": self.ip_address, "speed": self.cfg.DEFAULT_SPEED})
        self.log_event("Emergency stop reset successful")
        return True, None

    def handle_remote_motor_test(self, motor_idx: int, speed: float) -> Tuple[bool, Optional[str]]:
        if not self.safety.can_move():
            return False, "SAFETY_BLOCKED"
        clamped_speed = max(-1.0, min(1.0, speed))
        self.motor.drive_motor(motor_idx, clamped_speed)
        return True, None

    def handle_remote_disconnect(self):
        self.motor.stop()
        self.current_motion = RobotState.STOPPED
        if self.safety.can_move():
            self.state = RobotState.DISCONNECTED
            self.oled.update_state(RobotState.DISCONNECTED)
        self.log_event("Remote controller disconnected - Motor stopped")

    def handle_command(self, cmd: MovementCommand, speed: Optional[float] = None) -> bool:
        target_speed = speed if speed is not None else self.cfg.DEFAULT_SPEED

        if cmd == MovementCommand.EMERGENCY_STOP:
            self.handle_remote_emergency_stop()
            return True

        if cmd == MovementCommand.STOP:
            self.handle_remote_stop()
            return True

        if not self.safety.can_move():
            logger.warning(f"Movement command {cmd.value} rejected due to safety lock")
            return False

        dir_map = {
            MovementCommand.FORWARD: "forward",
            MovementCommand.BACKWARD: "backward",
            MovementCommand.TURN_LEFT: "left",
            MovementCommand.TURN_RIGHT: "right",
        }
        if cmd in dir_map:
            accepted, _ = self.handle_remote_drive(dir_map[cmd], target_speed)
            return accepted
        return False

    def reset_emergency_stop(self) -> bool:
        accepted, _ = self.handle_remote_emergency_reset()
        return accepted

    def shutdown(self):
        logger.info("Shutting down RobotController...")
        self.running = False
        self.motor.emergency_stop()
        self.motor.cleanup()

        if self.uvicorn_server is not None:
            self.uvicorn_server.should_exit = True

        if self.async_loop and self.async_loop.is_running():
            try:
                self.async_loop.call_soon_threadsafe(self.async_loop.stop)
            except Exception:
                pass

        if self.loop_thread and self.loop_thread.is_alive():
            self.loop_thread.join(timeout=0.2)

        self.state = RobotState.SHUTTING_DOWN
        self.camera.stop()
        self.oled.cleanup()

        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=0.2)

        logger.info("RobotController clean shutdown completed")
