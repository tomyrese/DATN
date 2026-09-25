import { useState, useEffect } from 'react';
import { TelemetryData, SafetyEventData, CommandAckData, PointOfInterest, DeliveryOrder, EscortTask } from '../types/protocol';
import { RobotStoreState, PairedRobotInfo, AppSettings, UserRole, ChatMessage } from '../types/robot';
import { RobotSocket } from '../services/RobotSocket';
import { StorageService } from '../services/StorageService';
import { RobotApi } from '../services/RobotApi';

const DEFAULT_POIS: PointOfInterest[] = [
  { id: 'poi_reception', name: 'Quầy Lễ Tân & CSKH', category: 'utility', floor: 'T1', x: 50.0, y: 72.0, description: 'Sảnh chính trung tâm, hỗ trợ đổi quà, chỉ đường và thông tin.' },
  { id: 'poi_wc', name: 'Khu Vệ Sinh & Tiện Ích', category: 'utility', floor: 'T1', x: 82.0, y: 72.0, description: 'Nhà vệ sinh hiện đại Nam, Nữ và phòng chăm sóc em bé.' },
  { id: 'poi_elevator', name: 'Thang Máy & Bãi Đỗ Xe', category: 'utility', floor: 'T1', x: 18.0, y: 72.0, description: 'Cụm thang máy lồng kính và lối xuống bãi đỗ xe.' },
  { id: 'poi_uniqlo', name: 'UNIQLO LifeWear', category: 'fashion', floor: 'T1', x: 20.0, y: 24.0, description: 'Thời trang phong cách Nhật Bản, trang phục nam, nữ và trẻ em.' },
  { id: 'poi_zara', name: 'Thời Trang ZARA', category: 'fashion', floor: 'T1', x: 80.0, y: 24.0, description: 'Thương hiệu thời trang cao cấp Tây Ban Nha mới nhất.' },
  { id: 'poi_highlands', name: 'Highlands Coffee', category: 'food', floor: 'T1', x: 20.0, y: 48.0, description: 'Cà phê pha phin truyền thống, Freeze và bánh ngọt.' },
  { id: 'poi_phuclong', name: 'Trà Phúc Long', category: 'food', floor: 'T1', x: 36.0, y: 48.0, description: 'Trà sữa Ô Long, Trà đào và thức uống thanh mát.' },
  { id: 'poi_kura_sushi', name: 'Nhà Hàng Kura Sushi', category: 'food', floor: 'T1', x: 50.0, y: 24.0, description: 'Sushi băng chuyền công nghệ cao và ẩm thực Nhật.' },
  { id: 'poi_cgv', name: 'Rạp Phim CGV Cinemas', category: 'entertainment', floor: 'T1', x: 80.0, y: 48.0, description: 'Cụm rạp chiếu phim IMAX & 4DX hiện đại bậc nhất.' },
  { id: 'poi_warehouse', name: 'Kho Giao Nhận Hàng Nội Bộ', category: 'staff', floor: 'T1', x: 90.0, y: 88.0, description: 'Khu vực bốc dỡ và xuất nhập hàng hóa nội bộ.', is_staff_only: true },
];

let globalState: RobotStoreState = {
  userRole: 'customer',
  connectionStatus: 'DISCONNECTED',
  pairedRobot: null,
  settings: {
    defaultSpeed: 0.35,
    enableCameraPreview: true,
    autoReconnect: true,
    mjpegQuality: 70,
    remoteTunnelUrl: '',
  },
  telemetry: null,
  robotState: 'STOPPED',
  safetyState: 'CLEAR',
  personDetected: false,
  personConfidence: 0.0,
  isEmergencyStopped: false,
  isSafetyBlocked: false,
  lastError: null,
  logs: [],
  latencyMs: 0,
  pois: DEFAULT_POIS,
  deliveryOrders: [],
  activeEscort: null,
  chatMessages: [
    {
      id: 'msg-welcome',
      sender: 'assistant',
      text: 'Xin chào quý khách! Tôi là Robot Lễ Tân & Dẫn Đường TTTM. Quý khách cần tìm cửa hàng, nhà hàng, nhà vệ sinh hay cần tôi dẫn đường đến đâu ạ?',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ],
};

const listeners = new Set<() => void>();

function notify() {
  listeners.forEach(fn => fn());
}

export function updateGlobalState(updater: (prev: RobotStoreState) => Partial<RobotStoreState>) {
  const partial = updater(globalState);
  globalState = { ...globalState, ...partial };
  notify();
}

let isStoreInitialized = false;

export function initializeStore() {
  if (isStoreInitialized) return;
  isStoreInitialized = true;

  const paired = StorageService.getPairedRobot();
  const settings = StorageService.getSettings();
  const role = StorageService.getUserRole();

  globalState.pairedRobot = paired;
  globalState.settings = settings;
  globalState.userRole = role;

  const socket = RobotSocket.getInstance();

  socket.addStatusListener(status => {
    updateGlobalState(prev => ({
      connectionStatus: status,
      logs: status === 'CONNECTED'
        ? [`[${new Date().toLocaleTimeString()}] WebSocket connected to Pi Robot.`, ...prev.logs.slice(0, 59)]
        : prev.logs,
    }));
  });

  socket.addPingListener(latencyMs => {
    updateGlobalState(() => ({ latencyMs }));
  });

  socket.addTelemetryListener(telemetry => {
    const isEStop = telemetry.safetyState === 'ERROR_STOP' || telemetry.robotState === 'SAFETY_STOP';
    const isBlocked = telemetry.personDetected || telemetry.safetyState !== 'CLEAR';

    updateGlobalState(() => ({
      telemetry,
      robotState: telemetry.robotState,
      safetyState: telemetry.safetyState,
      personDetected: telemetry.personDetected,
      personConfidence: telemetry.personConfidence,
      isEmergencyStopped: isEStop,
      isSafetyBlocked: isBlocked,
    }));
  });

  socket.addSafetyEventListener(event => {
    if (event.event === 'person_detected') {
      updateGlobalState(prev => ({
        personDetected: true,
        personConfidence: event.confidence || 0.85,
        isSafetyBlocked: true,
        logs: [`[${new Date().toLocaleTimeString()}] PERSON DETECTED IN PATH (${Math.round((event.confidence || 0.85) * 100)}%)`, ...prev.logs.slice(0, 59)],
      }));
    } else if (event.event === 'person_clear') {
      updateGlobalState(prev => ({
        personDetected: false,
        isSafetyBlocked: false,
        logs: [`[${new Date().toLocaleTimeString()}] PERSON CLEARED FROM PATH`, ...prev.logs.slice(0, 59)],
      }));
    } else if (event.event === 'emergency_stop') {
      updateGlobalState(prev => ({
        isEmergencyStopped: true,
        isSafetyBlocked: true,
        logs: [`[${new Date().toLocaleTimeString()}] EMERGENCY STOP TRIGGERED!`, ...prev.logs.slice(0, 59)],
      }));
    }
  });

  socket.addAckListener(ack => {
    if (!ack.accepted && ack.reason) {
      updateGlobalState(prev => ({
        lastError: ack.reason || 'Command rejected',
        logs: [`[${new Date().toLocaleTimeString()}] COMMAND REJECTED: ${ack.reason}`, ...prev.logs.slice(0, 59)],
      }));
    }
  });

  // Fetch initial POIs and orders if paired
  if (paired) {
    RobotApi.getMallPois(paired.host, paired.port, true).then(pois => {
      if (pois && pois.length > 0) {
        updateGlobalState(() => ({ pois }));
      }
    });

    RobotApi.getDeliveryOrders(paired.host, paired.port).then(orders => {
      if (orders) {
        updateGlobalState(() => ({ deliveryOrders: orders }));
      }
    });
  }
}

export function useRobotStore(): RobotStoreState {
  const [state, setState] = useState<RobotStoreState>(globalState);

  useEffect(() => {
    const listener = () => setState({ ...globalState });
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }, []);

  return state;
}
