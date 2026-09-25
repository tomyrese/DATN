export type RobotStateType =
  | 'BOOTING'
  | 'READY'
  | 'PAIRING'
  | 'CONNECTED'
  | 'FORWARD'
  | 'BACKWARD'
  | 'TURN_LEFT'
  | 'TURN_RIGHT'
  | 'STOPPED'
  | 'PERSON_DETECTED'
  | 'SAFETY_STOP'
  | 'CAMERA_ERROR'
  | 'MOTOR_ERROR'
  | 'SYSTEM_ERROR'
  | 'DISCONNECTED'
  | 'SHUTTING_DOWN';

export type SafetyStateType = 'CLEAR' | 'PERSON_DETECTED' | 'SAFETY_STOP' | 'ERROR_STOP';

export interface TelemetryData {
  type: 'telemetry';
  robotState: RobotStateType;
  safetyState: SafetyStateType;
  speed: number;
  leftSpeed: number;
  rightSpeed: number;
  m1: number;
  m2: number;
  m3: number;
  m4: number;
  personDetected: boolean;
  personConfidence: number;
  cameraOk: boolean;
  detectorOk: boolean;
  oledOk: boolean;
  motorOk: boolean;
  cameraFps: number;
  inferenceFps: number;
  cpuTemp?: number | null;
  cpuUsage?: number | null;
  memoryUsage?: number | null;
  wifiSignal?: number | null;
  uptime: number;
  timestamp: number;
  personBbox?: [number, number, number, number] | null;
}

export interface SafetyEventData {
  type: 'safety_event';
  event: 'person_detected' | 'person_clear' | 'emergency_stop' | 'camera_error' | 'connection_lost';
  confidence?: number;
}

export interface CommandAckData {
  type: 'command_ack';
  seq?: number;
  accepted: boolean;
  reason?: string;
}

export interface HelloAckData {
  type: 'hello_ack';
  protocol: number;
  robotId: string;
  robotName: string;
  state: RobotStateType;
}

export interface PairResponse {
  success: boolean;
  token?: string;
  robotId: string;
  robotName: string;
  message?: string;
}

export interface HealthResponse {
  status: string;
  robotState: RobotStateType;
  safetyState: SafetyStateType;
  camera: boolean;
  detector: boolean;
  motor: boolean;
  oled: boolean;
  server: boolean;
}

export interface InfoResponse {
  robotId: string;
  robotName: string;
  apiVersion: string;
  protocolVersion: number;
  hostname: string;
  serverVersion: string;
  paired: boolean;
}

export interface PointOfInterest {
  id: string;
  name: string;
  category: 'food' | 'fashion' | 'entertainment' | 'utility' | 'staff';
  floor: 'B1' | 'T1' | 'T2' | 'T3';
  x: number; // 0 - 100 percentage
  y: number;
  description: string;
  is_staff_only?: boolean;
}

export interface DeliveryOrder {
  order_id: string;
  creator_name: string;
  pickup_poi_id: string;
  pickup_poi_name: string;
  dropoff_poi_id: string;
  dropoff_poi_name: string;
  item_description: string;
  status: 'PENDING' | 'MOVING_TO_PICKUP' | 'ARRIVED_AT_PICKUP' | 'DELIVERING' | 'ARRIVED_AT_DROPOFF' | 'COMPLETED' | 'CANCELLED';
  created_at: number;
  updated_at: number;
  current_progress: number;
}

export interface EscortTask {
  task_id: string;
  target_poi_id: string;
  target_name: string;
  target_floor: string;
  status: 'IDLE' | 'NAVIGATING' | 'ARRIVED' | 'CANCELLED';
  started_at: number;
  estimated_seconds: number;
  current_progress: number;
}

export interface AskAssistantResponse {
  answer: string;
  suggested_poi_id?: string | null;
  suggested_poi_name?: string | null;
}

