import { useState, useEffect } from 'react';
import { TelemetryData, SafetyEventData, CommandAckData, PointOfInterest, DeliveryOrder, EscortTask } from '../types/protocol';
import { RobotStoreState, PairedRobotInfo, AppSettings, UserRole, ChatMessage } from '../types/robot';
import { RobotSocket } from '../services/RobotSocket';
import { StorageService } from '../services/StorageService';
import { RobotApi } from '../services/RobotApi';

const DEFAULT_POIS: PointOfInterest[] = [
  { id: 'poi_reception', name: 'Quầy Lễ Tân & CSKH', category: 'utility', floor: 'T1', x: 50.0, y: 85.0, description: 'Sảnh chính trung tâm, hỗ trợ đổi quà và hướng dẫn.' },
  { id: 'poi_highlands', name: 'Highlands Coffee', category: 'food', floor: 'T1', x: 20.0, y: 75.0, description: 'Cà phê, bánh ngọt, không gian mở view sảnh.' },
  { id: 'poi_zara', name: 'Cửa hàng Thời trang ZARA', category: 'fashion', floor: 'T1', x: 80.0, y: 60.0, description: 'Thời trang nam, nữ và trẻ em cao cấp.' },
  { id: 'poi_uniqlo', name: 'UNIQLO LifeWear', category: 'fashion', floor: 'T1', x: 25.0, y: 40.0, description: 'Quần áo thời trang tiện dụng Nhật Bản.' },
  { id: 'poi_wc_t1', name: 'Nhà Vệ Sinh Tầng 1', category: 'utility', floor: 'T1', x: 88.0, y: 85.0, description: 'Nhà vệ sinh nam/nữ, phòng em bé.' },
  { id: 'poi_elevator_t1', name: 'Cụm Thang Máy T1', category: 'utility', floor: 'T1', x: 50.0, y: 50.0, description: 'Thang máy lên các tầng B1, T2, T3.' },
  { id: 'poi_phuclong', name: 'Trà Sữa Phúc Long', category: 'food', floor: 'T2', x: 30.0, y: 70.0, description: 'Trà đào, trà sữa và cà phê truyền thống.' },
  { id: 'poi_kura_sushi', name: 'Nhà Hàng Kura Sushi', category: 'food', floor: 'T2', x: 70.0, y: 35.0, description: 'Sushi băng chuyền công nghệ cao.' },
  { id: 'poi_adidas', name: 'Adidas Originals Store', category: 'fashion', floor: 'T2', x: 20.0, y: 35.0, description: 'Giày thể thao, phụ kiện chính hãng.' },
  { id: 'poi_wc_t2', name: 'Nhà Vệ Sinh Tầng 2', category: 'utility', floor: 'T2', x: 88.0, y: 85.0, description: 'Khu vệ sinh tiện nghi.' },
  { id: 'poi_cgv', name: 'Rạp Chiếu Phim CGV Cinemas', category: 'entertainment', floor: 'T3', x: 50.0, y: 30.0, description: 'Phòng chiếu IMAX, Starium và quầy bắp nước.' },
  { id: 'poi_arcade', name: 'Khu Vui Chơi TimeZone Arcade', category: 'entertainment', floor: 'T3', x: 25.0, y: 60.0, description: 'Máy game thùng, bắn súng, gắp thú.' },
  { id: 'poi_wc_t3', name: 'Nhà Vệ Sinh Tầng 3', category: 'utility', floor: 'T3', x: 88.0, y: 85.0, description: 'Nhà vệ sinh tầng 3.' },
  { id: 'poi_warehouse_b1', name: 'Kho Vận Hàng Hóa Trung Tâm', category: 'staff', floor: 'B1', x: 15.0, y: 20.0, description: 'Khu vực xuất nhập và phân loại hàng hóa.', is_staff_only: true },
  { id: 'poi_staff_counter', name: 'Quầy Giao Nhận Nội Bộ T1', category: 'staff', floor: 'T1', x: 85.0, y: 20.0, description: 'Điểm tiếp nhận đơn hàng chuyển phát nhanh nội bộ.', is_staff_only: true },
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
