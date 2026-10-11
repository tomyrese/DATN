from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class HelloMessage(BaseModel):
    type: Literal["hello"] = "hello"
    protocol: int = 1
    client: str = "android"
    appVersion: str = "1.0.0"

class HelloAckMessage(BaseModel):
    type: Literal["hello_ack"] = "hello_ack"
    protocol: int = 1
    robotId: str
    robotName: str
    state: str

class DriveMessage(BaseModel):
    type: Literal["drive"] = "drive"
    direction: Literal["forward", "backward", "left", "right"]
    speed: float = Field(ge=-1.0, le=1.0)
    seq: Optional[int] = None

class TankDriveMessage(BaseModel):
    type: Literal["tank_drive"] = "tank_drive"
    left: float = Field(ge=-1.0, le=1.0)
    right: float = Field(ge=-1.0, le=1.0)
    seq: Optional[int] = None

class StopMessage(BaseModel):
    type: Literal["stop"] = "stop"
    seq: Optional[int] = None

class EmergencyStopMessage(BaseModel):
    type: Literal["emergency_stop"] = "emergency_stop"

class EmergencyResetMessage(BaseModel):
    type: Literal["emergency_reset"] = "emergency_reset"

class MotorTestMessage(BaseModel):
    type: Literal["motor_test"] = "motor_test"
    motor: int = Field(ge=1, le=4)
    speed: float = Field(ge=-1.0, le=1.0)

class HeartbeatMessage(BaseModel):
    type: Literal["heartbeat"] = "heartbeat"
    timestamp: Optional[float] = None

class HeartbeatAckMessage(BaseModel):
    type: Literal["heartbeat_ack"] = "heartbeat_ack"
    timestamp: float

class CommandAckMessage(BaseModel):
    type: Literal["command_ack"] = "command_ack"
    seq: Optional[int] = None
    accepted: bool
    reason: Optional[str] = None

class SafetyEventMessage(BaseModel):
    type: Literal["safety_event"] = "safety_event"
    event: Literal["person_detected", "person_clear", "emergency_stop", "camera_error", "connection_lost"]
    confidence: Optional[float] = None

class TelemetryMessage(BaseModel):
    type: Literal["telemetry"] = "telemetry"
    robotState: str
    safetyState: str
    speed: float
    leftSpeed: float
    rightSpeed: float
    m1: float
    m2: float
    m3: float
    m4: float
    personDetected: bool
    personConfidence: float
    cameraOk: bool
    detectorOk: bool
    oledOk: bool
    motorOk: bool
    cameraFps: float
    inferenceFps: float
    cpuTemp: Optional[float] = None
    cpuUsage: Optional[float] = None
    memoryUsage: Optional[float] = None
    wifiSignal: Optional[int] = None
    uptime: float = 0.0
    timestamp: float = 0.0
    personBbox: Optional[List[float]] = None
    odometryX: Optional[float] = None
    odometryY: Optional[float] = None
    odometryHeading: Optional[float] = None
    odometryConfidence: Optional[float] = None
    isEstimated: Optional[bool] = True
    ultrasonicLeft: Optional[float] = None
    ultrasonicRight: Optional[float] = None
    obstacleState: Optional[str] = None
    navStatus: Optional[str] = None

class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    code: str
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    user: Optional[dict] = None
    message: Optional[str] = None

class PairRequest(BaseModel):
    pairCode: str
    clientInfo: Optional[str] = "Android Device"

class PairResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    robotId: str
    robotName: str
    message: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    robotState: str
    safetyState: str
    camera: bool
    detector: bool
    motor: bool
    oled: bool
    server: bool

class InfoResponse(BaseModel):
    robotId: str
    robotName: str
    apiVersion: str
    protocolVersion: int
    hostname: str
    serverVersion: str
    paired: bool
