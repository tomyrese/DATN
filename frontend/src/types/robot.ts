import { RobotStateType, SafetyStateType, TelemetryData, PointOfInterest, DeliveryOrder, EscortTask } from './protocol';

export type UserRole = 'customer' | 'staff';

export type ConnectionStatus =
  | 'DISCONNECTED'
  | 'CONNECTING'
  | 'AUTHENTICATING'
  | 'CONNECTED'
  | 'RECONNECTING'
  | 'FAILED';

export interface PairedRobotInfo {
  robotId: string;
  robotName: string;
  host: string;
  port: number;
  token: string;
  lastConnected: number;
}

export interface AppSettings {
  defaultSpeed: number;
  enableCameraPreview: boolean;
  autoReconnect: boolean;
  mjpegQuality: number;
  remoteTunnelUrl?: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  time: string;
  suggestedPoiId?: string | null;
  suggestedPoiName?: string | null;
}

export interface RobotStoreState {
  userRole: UserRole;
  connectionStatus: ConnectionStatus;
  pairedRobot: PairedRobotInfo | null;
  settings: AppSettings;
  telemetry: TelemetryData | null;
  robotState: RobotStateType;
  safetyState: SafetyStateType;
  personDetected: boolean;
  personConfidence: number;
  isEmergencyStopped: boolean;
  isSafetyBlocked: boolean;
  lastError: string | null;
  logs: string[];
  latencyMs: number;
  pois: PointOfInterest[];
  deliveryOrders: DeliveryOrder[];
  activeEscort: EscortTask | null;
  chatMessages: ChatMessage[];
}

