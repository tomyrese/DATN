import { RobotStateType, SafetyStateType, TelemetryData, PointOfInterest, DeliveryOrder, EscortTask, Promotion } from './protocol';

export type UserRole = 'guest' | 'customer' | 'staff' | 'admin';

export type ConnectionStatus =
  | 'DISCONNECTED'
  | 'CONNECTING'
  | 'AUTHENTICATING'
  | 'CONNECTED'
  | 'RECONNECTING'
  | 'FAILED';

export interface AuthUser {
  id: string;
  username: string;
  fullName: string;
  role: 'guest' | 'customer' | 'staff' | 'admin';
  assignedStoreIds: string[];
  token: string;
}

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
  currentUser: AuthUser | null;
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
  promotions: Promotion[];
  deliveryOrders: DeliveryOrder[];
  activeEscort: EscortTask | null;
  chatMessages: ChatMessage[];
}

