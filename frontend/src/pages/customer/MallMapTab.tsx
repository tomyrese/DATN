import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { RobotSocket } from '../../services/RobotSocket';
import {
  Navigation,
  XCircle,
  Sparkles,
  MapPin,
  Clock,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Square,
  RotateCcw,
  Play,
  Gamepad2,
  Radio,
  CheckCircle2,
  Flame,
} from 'lucide-react';

export interface MallStoreMeta {
  id: string;
  lotCode: string;
  shortName: string;
  name: string;
  sub: string;
  category: 'food' | 'fashion' | 'entertainment' | 'utility';
  lotX: number;
  lotY: number;
  lotW: number;
  lotH: number;
  entranceX: number;
  entranceY: number;
  color: string;
  borderColor: string;
  accentBg: string;
  icon: string;
  description: string;
  promo?: string;
  hours: string;
  wing: string;
}

export const MALL_STORES: MallStoreMeta[] = [
  {
    id: 'poi_uniqlo',
    lotCode: 'L1-01',
    shortName: 'UNIQLO',
    name: 'UNIQLO LifeWear',
    sub: 'Thời trang Nhật Bản',
    category: 'fashion',
    lotX: 45,
    lotY: 35,
    lotW: 320,
    lotH: 170,
    entranceX: 205,
    entranceY: 235,
    color: '#EC4899',
    borderColor: '#F472B6',
    accentBg: '#FDF2F8',
    icon: '👕',
    description: 'Trang phục thường ngày cao cấp phong cách Nhật Bản dành cho mọi lứa tuổi.',
    promo: 'Giảm 20% BST mùa hè',
    hours: '09:00 — 22:00',
    wing: 'Hành lang Tây (T1)',
  },
  {
    id: 'poi_kura_sushi',
    lotCode: 'L1-02',
    shortName: 'KURA SUSHI',
    name: 'Nhà Hàng Kura Sushi',
    sub: 'Ẩm thực Nhật Bản',
    category: 'food',
    lotX: 405,
    lotY: 35,
    lotW: 190,
    lotH: 170,
    entranceX: 500,
    entranceY: 235,
    color: '#D97706',
    borderColor: '#FBBF24',
    accentBg: '#FFFBEB',
    icon: '🍣',
    description: 'Sushi băng chuyền công nghệ cao, hải sản tươi sống nhập khẩu mỗi ngày.',
    promo: 'Tặng 1 đĩa cá hồi hóa đơn > 500k',
    hours: '10:00 — 22:00',
    wing: 'Sảnh Trung Tâm (T1)',
  },
  {
    id: 'poi_zara',
    lotCode: 'L1-03',
    shortName: 'ZARA',
    name: 'Thời Trang ZARA',
    sub: 'Thời trang Quốc tế',
    category: 'fashion',
    lotX: 635,
    lotY: 35,
    lotW: 320,
    lotH: 170,
    entranceX: 795,
    entranceY: 235,
    color: '#8B5CF6',
    borderColor: '#A78BFA',
    accentBg: '#F5F3FF',
    icon: '👗',
    description: 'Thương hiệu thời trang cao cấp Tây Ban Nha với xu hướng mới nhất toàn cầu.',
    promo: 'Ưu đãi đến 30% thành viên',
    hours: '09:00 — 22:00',
    wing: 'Hành lang Đông (T1)',
  },
  {
    id: 'poi_highlands',
    lotCode: 'L1-04',
    shortName: 'HIGHLANDS',
    name: 'Highlands Coffee',
    sub: 'Cà phê & Bánh ngọt',
    category: 'food',
    lotX: 45,
    lotY: 265,
    lotW: 280,
    lotH: 160,
    entranceX: 345,
    entranceY: 345,
    color: '#DC2626',
    borderColor: '#F87171',
    accentBg: '#FEF2F2',
    icon: '☕',
    description: 'Cà phê pha phin truyền thống đậm đà, Freeze đá xay và trà sen vàng trứ danh.',
    promo: 'Mua 2 tặng 1 khung giờ 14h — 17h',
    hours: '08:00 — 22:30',
    wing: 'Hành lang Tây (T1)',
  },
  {
    id: 'poi_cgv',
    lotCode: 'L1-05',
    shortName: 'CGV CINEMAS',
    name: 'Rạp Phim CGV Cinemas',
    sub: 'Rạp chiếu phim IMAX & 4DX',
    category: 'entertainment',
    lotX: 675,
    lotY: 265,
    lotW: 280,
    lotH: 160,
    entranceX: 655,
    entranceY: 345,
    color: '#9333EA',
    borderColor: '#C084FC',
    accentBg: '#FAF5FF',
    icon: '🎬',
    description: 'Cụm rạp chiếu phim màn hình lớn IMAX & 4DX với hệ thống âm thanh Dolby Atmos.',
    promo: 'Combo bắp nước giảm 15% đặt trước',
    hours: '08:30 — 23:30',
    wing: 'Hành lang Đông (T1)',
  },
  {
    id: 'poi_elevator',
    lotCode: 'L1-06',
    shortName: 'THANG MÁY',
    name: 'Thang Máy & Bãi Xe',
    sub: 'Lên tầng & Hầm B1',
    category: 'utility',
    lotX: 45,
    lotY: 485,
    lotW: 280,
    lotH: 165,
    entranceX: 345,
    entranceY: 520,
    color: '#16A34A',
    borderColor: '#4ADE80',
    accentBg: '#F0FDF4',
    icon: '🛗',
    description: 'Cụm thang máy kính tốc độ cao kết nối các tầng T1, T2, T3 và bãi giữ xe tầng hầm.',
    hours: 'Mở cửa 24/7',
    wing: 'Hành lang Tây (T1)',
  },
  {
    id: 'poi_reception',
    lotCode: 'L1-07',
    shortName: 'LỄ TÂN & SẠC',
    name: 'Lễ Tân & Trạm Sạc Robot',
    sub: 'Sảnh chính & Xuất phát',
    category: 'utility',
    lotX: 375,
    lotY: 485,
    lotW: 250,
    lotH: 165,
    entranceX: 500,
    entranceY: 505,
    color: '#2563EB',
    borderColor: '#60A5FA',
    accentBg: '#EFF6FF',
    icon: '💁',
    description: 'Quầy thông tin CSKH trung tâm và điểm xuất phát / sạc pin tự động của Robot.',
    hours: '08:00 — 22:00',
    wing: 'Sảnh Chính (T1)',
  },
  {
    id: 'poi_wc',
    lotCode: 'L1-08',
    shortName: 'KHU VỆ SINH',
    name: 'Khu Vệ Sinh & Tiện Ích',
    sub: 'WC Nam / Nữ / Em Bé',
    category: 'utility',
    lotX: 675,
    lotY: 485,
    lotW: 280,
    lotH: 165,
    entranceX: 655,
    entranceY: 520,
    color: '#0D9488',
    borderColor: '#2DD4BF',
    accentBg: '#F0FDFA',
    icon: '🚻',
    description: 'Khu vệ sinh hiện đại trang bị thiết bị tự động và phòng thay tã cho mẹ & bé.',
    hours: 'Mở cửa 24/7',
    wing: 'Hành lang Đông (T1)',
  },
];

const CATEGORIES = [
  { id: 'all', label: 'Tất Cả' },
  { id: 'food', label: '🍔 Ăn Uống' },
  { id: 'fashion', label: '👗 Thời Trang' },
  { id: 'entertainment', label: '🎬 Rạp Phim' },
  { id: 'utility', label: '🚻 Tiện Ích' },
];

// Helper: Convert Backend Odometry Metric Coordinates to SVG ViewBox (1000 x 680)
function odomToSvg(odomX: number, odomY: number): { x: number; y: number } {
  // node_center in DB is (50, 50) -> SVG (500, 345)
  // node_west in DB is (30, 50)   -> SVG (210, 345)  (factor: 14.5)
  // node_east in DB is (70, 50)   -> SVG (790, 345)  (factor: 14.5)
  // node_north in DB is (50, 32)  -> SVG (500, 196)  (factor: 8.25)
  // node_south in DB is (50, 68)  -> SVG (500, 494)  (factor: 8.25)
  const mappedX = 500 + (odomX - 50.0) * 14.5;
  const mappedY = 345 + (odomY - 50.0) * 8.25;
  return {
    x: Math.max(50, Math.min(950, mappedX)),
    y: Math.max(50, Math.min(630, mappedY)),
  };
}

export const MallMapTab: React.FC = () => {
  const { activeEscort, pairedRobot, telemetry, connectionStatus, userRole } = useRobotStore();

  // Mode Selection: 'live' (Real Robot WebSocket) or 'virtual' (Interactive Virtual Simulation)
  const [mapMode, setMapMode] = useState<'live' | 'virtual'>('virtual');

  // Category & Selected Store
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedStoreId, setSelectedStoreId] = useState<string>('poi_cgv');
  const [loadingEscort, setLoadingEscort] = useState(false);

  // ==================== VIRTUAL SIMULATION STATE ====================
  // Virtual Robot coordinates (SVG space: 0..1000, 0..680)
  // Default start: Reception desk (x: 500, y: 510, heading: 270 deg / facing North towards Atrium)
  const [virtualPos, setVirtualPos] = useState<{ x: number; y: number }>({ x: 500, y: 505 });
  const [virtualHeading, setVirtualHeading] = useState<number>(270);
  const [isSimEscorting, setIsSimEscorting] = useState<boolean>(false);
  const [simProgress, setSimProgress] = useState<number>(0);
  const [simWaypoints, setSimWaypoints] = useState<{ x: number; y: number }[]>([]);
  const [simWaypointIdx, setSimWaypointIdx] = useState<number>(0);
  const [simSpeed, setSimSpeed] = useState<number>(3.5); // Pixels per frame
  const [drivingKey, setDrivingKey] = useState<string | null>(null);

  // Breadcrumb Trail (stores last 50 points)
  const [trail, setTrail] = useState<{ x: number; y: number }[]>([{ x: 500, y: 505 }]);

  // Selected Store Object
  const currentStore = useMemo(() => {
    return MALL_STORES.find(s => s.id === selectedStoreId) || MALL_STORES[4];
  }, [selectedStoreId]);

  // Filtered Stores
  const filteredStores = useMemo(() => {
    if (selectedCategory === 'all') return MALL_STORES;
    return MALL_STORES.filter(s => s.category === selectedCategory);
  }, [selectedCategory]);

  // ==================== REAL ROBOT COORDINATES ====================
  const rawOdomX = telemetry?.odometryX;
  const rawOdomY = telemetry?.odometryY;
  const odomHeading = telemetry?.odometryHeading ?? (3.0 * Math.PI / 2.0);
  const odomHeadingDeg = Math.round((odomHeading * 180) / Math.PI);

  const realRobotSvgPos = useMemo(() => {
    if (rawOdomX !== undefined && rawOdomX !== null && rawOdomY !== undefined && rawOdomY !== null) {
      return odomToSvg(rawOdomX, rawOdomY);
    }
    return { x: 500, y: 505 };
  }, [rawOdomX, rawOdomY]);

  // Displayed Robot Position & Heading based on active mode
  const currentRobotPos = mapMode === 'virtual' ? virtualPos : realRobotSvgPos;
  const currentRobotHeading = mapMode === 'virtual' ? virtualHeading : odomHeadingDeg;

  // Append to breadcrumb trail whenever robot moves
  useEffect(() => {
    setTrail(prev => {
      const last = prev[prev.length - 1];
      if (!last || Math.hypot(last.x - currentRobotPos.x, last.y - currentRobotPos.y) > 10) {
        return [...prev.slice(-60), currentRobotPos];
      }
      return prev;
    });
  }, [currentRobotPos.x, currentRobotPos.y]);

  // Auto-switch to Live Mode if connection is established
  useEffect(() => {
    if (connectionStatus === 'CONNECTED' && telemetry) {
      setMapMode('live');
    }
  }, [connectionStatus]);

  // ==================== TOPOLOGICAL CORRIDOR PATH PLANNER ====================
  // Generates smooth walkable path through central corridors to store entrance
  const calculateCorridorRoute = useCallback((start: { x: number; y: number }, target: { x: number; y: number }) => {
    const pts: { x: number; y: number }[] = [start];

    // Hub coordinates in SVG
    const hubCenter = { x: 500, y: 345 };
    const hubNorth = { x: 500, y: 235 };
    const hubSouth = { x: 500, y: 455 };

    // Step 1: Reach concourse spine
    if (start.y > 440) {
      pts.push(hubSouth);
    } else if (start.y < 250) {
      pts.push(hubNorth);
    }

    // Step 2: Pass through Central Atrium Rotunda
    pts.push(hubCenter);

    // Step 3: Branch to target wing
    if (target.y < 250) {
      pts.push(hubNorth);
      pts.push({ x: target.x, y: 235 });
    } else if (target.y > 440) {
      pts.push(hubSouth);
      pts.push({ x: target.x, y: 455 });
    } else {
      pts.push({ x: target.x, y: 345 });
    }

    pts.push(target);
    return pts;
  }, []);

  // SVG Path String for rendering route line
  const plannedRoutePts = useMemo(() => {
    if (!currentStore) return [];
    return calculateCorridorRoute(currentRobotPos, { x: currentStore.entranceX, y: currentStore.entranceY });
  }, [currentRobotPos, currentStore, calculateCorridorRoute]);

  const plannedPathD = useMemo(() => {
    if (plannedRoutePts.length === 0) return '';
    return plannedRoutePts.reduce((acc, pt, idx) => {
      return idx === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`;
    }, '');
  }, [plannedRoutePts]);

  // ==================== VIRTUAL ESCORT SIMULATION ENGINE ====================
  // Smoothly drives the virtual robot step-by-step along corridor waypoints
  const startVirtualEscort = () => {
    if (!currentStore) return;
    const waypoints = calculateCorridorRoute(virtualPos, { x: currentStore.entranceX, y: currentStore.entranceY });
    setSimWaypoints(waypoints);
    setSimWaypointIdx(1); // Start driving toward second waypoint
    setSimProgress(0);
    setIsSimEscorting(true);
  };

  const cancelVirtualEscort = () => {
    setIsSimEscorting(false);
    setSimWaypoints([]);
    setSimWaypointIdx(0);
    setSimProgress(0);
  };

  useEffect(() => {
    if (!isSimEscorting || simWaypoints.length === 0) return;

    const interval = setInterval(() => {
      if (simWaypointIdx >= simWaypoints.length) {
        setIsSimEscorting(false);
        setSimProgress(100);
        alert(`🎉 Robot đã dẫn quý khách đến thành công: ${currentStore.name}!`);
        return;
      }

      const targetWp = simWaypoints[simWaypointIdx];
      const dx = targetWp.x - virtualPos.x;
      const dy = targetWp.y - virtualPos.y;
      const dist = Math.hypot(dx, dy);

      if (dist < 8) {
        // Waypoint reached, advance to next
        const nextIdx = simWaypointIdx + 1;
        setSimWaypointIdx(nextIdx);
        const progress = Math.min(100, Math.round((nextIdx / simWaypoints.length) * 100));
        setSimProgress(progress);
      } else {
        // Move towards waypoint
        const angleRad = Math.atan2(dy, dx);
        const angleDeg = Math.round((angleRad * 180) / Math.PI);
        const step = Math.min(dist, simSpeed);

        setVirtualHeading(angleDeg);
        setVirtualPos(prev => ({
          x: prev.x + Math.cos(angleRad) * step,
          y: prev.y + Math.sin(angleRad) * step,
        }));
      }
    }, 35); // ~30 FPS smooth animation loop

    return () => clearInterval(interval);
  }, [isSimEscorting, simWaypointIdx, simWaypoints, virtualPos, simSpeed, currentStore]);

  // ==================== MANUAL VIRTUAL DRIVE ENGINE ====================
  // Moves virtual robot on map and sends to real robot if connected
  const handleVirtualDrive = (direction: 'forward' | 'backward' | 'left' | 'right' | 'stop') => {
    setDrivingKey(direction);

    // Also forward to real robot if connected
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || 8765;
    if (connectionStatus === 'CONNECTED') {
      RobotApi.directDrive(host, port, direction, 0.35);
    }

    if (direction === 'stop') {
      setTimeout(() => setDrivingKey(null), 200);
      return;
    }

    const rad = (virtualHeading * Math.PI) / 180;
    const moveDist = 18; // 18 pixels per tap

    if (direction === 'forward') {
      setVirtualPos(prev => {
        const nextX = Math.max(50, Math.min(950, prev.x + Math.cos(rad) * moveDist));
        const nextY = Math.max(50, Math.min(630, prev.y + Math.sin(rad) * moveDist));
        return { x: nextX, y: nextY };
      });
    } else if (direction === 'backward') {
      setVirtualPos(prev => {
        const nextX = Math.max(50, Math.min(950, prev.x - Math.cos(rad) * moveDist));
        const nextY = Math.max(50, Math.min(630, prev.y - Math.sin(rad) * moveDist));
        return { x: nextX, y: nextY };
      });
    } else if (direction === 'left') {
      setVirtualHeading(prev => (prev - 25 + 360) % 360);
    } else if (direction === 'right') {
      setVirtualHeading(prev => (prev + 25) % 360);
    }

    setTimeout(() => setDrivingKey(null), 200);
  };

  const handleResetVirtualRobot = () => {
    cancelVirtualEscort();
    setVirtualPos({ x: 500, y: 505 });
    setVirtualHeading(270);
    setTrail([{ x: 500, y: 505 }]);
  };

  // Keyboard navigation listener (W, A, S, D, Arrow keys)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return;

      const k = e.key.toLowerCase();
      if (k === 'w' || k === 'arrowup') {
        e.preventDefault();
        handleVirtualDrive('forward');
      } else if (k === 's' || k === 'arrowdown') {
        e.preventDefault();
        handleVirtualDrive('backward');
      } else if (k === 'a' || k === 'arrowleft') {
        e.preventDefault();
        handleVirtualDrive('left');
      } else if (k === 'd' || k === 'arrowright') {
        e.preventDefault();
        handleVirtualDrive('right');
      } else if (k === ' ') {
        e.preventDefault();
        handleVirtualDrive('stop');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [virtualHeading, connectionStatus, pairedRobot]);

  // ==================== REAL ESCORT TRIGGERS ====================
  const handleStartRealEscort = async (store: MallStoreMeta) => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    setLoadingEscort(true);
    try {
      const res = await RobotApi.requestEscort(host, port, store.id);
      if (res.success && res.task) {
        updateGlobalState(() => ({ activeEscort: res.task }));
      } else {
        alert(res.message || 'Không thể bắt đầu dẫn đường.');
      }
    } catch (e: any) {
      alert(`Lỗi: ${e.message}`);
    } finally {
      setLoadingEscort(false);
    }
  };

  const handleCancelRealEscort = async () => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    try {
      await RobotApi.cancelEscort(host, port);
      updateGlobalState(() => ({ activeEscort: null }));
    } catch (e) {}
  };

  // Primary action button trigger
  const handlePrimaryAction = () => {
    if (mapMode === 'virtual') {
      if (isSimEscorting) {
        cancelVirtualEscort();
      } else {
        startVirtualEscort();
      }
    } else {
      if (activeEscort) {
        handleCancelRealEscort();
      } else {
        handleStartRealEscort(currentStore);
      }
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', width: '100%', maxWidth: '100%' }}>
      
      {/* Interactive Mode Switcher & Real-time Live Status Bar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '10px 14px',
        backgroundColor: '#FFFFFF',
        borderRadius: '16px',
        border: '1px solid #E2E8F0',
        boxShadow: '0 2px 6px rgba(0,0,0,0.03)',
        gap: '8px'
      }}>
        {/* Mode Toggle Pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', background: '#F1F5F9', padding: '3px', borderRadius: '12px' }}>
          <button
            onClick={() => setMapMode('virtual')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              padding: '6px 12px',
              borderRadius: '9px',
              border: 'none',
              backgroundColor: mapMode === 'virtual' ? '#FFFFFF' : 'transparent',
              color: mapMode === 'virtual' ? '#2563EB' : '#64748B',
              fontWeight: 800,
              fontSize: '0.78rem',
              cursor: 'pointer',
              boxShadow: mapMode === 'virtual' ? '0 1px 4px rgba(0,0,0,0.08)' : 'none',
              transition: 'all 0.15s ease'
            }}
          >
            <Gamepad2 size={15} />
            <span>Mô Phỏng Lái Ảo</span>
          </button>

          <button
            onClick={() => setMapMode('live')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              padding: '6px 12px',
              borderRadius: '9px',
              border: 'none',
              backgroundColor: mapMode === 'live' ? '#2563EB' : 'transparent',
              color: mapMode === 'live' ? '#FFFFFF' : '#64748B',
              fontWeight: 800,
              fontSize: '0.78rem',
              cursor: 'pointer',
              boxShadow: mapMode === 'live' ? '0 2px 6px rgba(37,99,235,0.3)' : 'none',
              transition: 'all 0.15s ease'
            }}
          >
            <Radio size={15} />
            <span>Robot Thực Tế</span>
          </button>
        </div>

        {/* Live Coordinate & Status Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span
              className={`status-dot ${mapMode === 'live' ? (connectionStatus === 'CONNECTED' ? 'online' : 'connecting') : 'online'}`}
              style={{ width: '8px', height: '8px' }}
            />
            <span style={{ fontWeight: 800, color: '#0F172A' }}>
              {mapMode === 'virtual'
                ? 'XE ẢO REALTIME'
                : (connectionStatus === 'CONNECTED' ? 'PI ROBOT ĐANG NỐI' : 'CHƯA NỐI BACKEND')}
            </span>
          </div>
          <span style={{
            padding: '2px 8px',
            borderRadius: '6px',
            backgroundColor: '#EFF6FF',
            color: '#1D4ED8',
            fontWeight: 800,
            fontSize: '0.7rem'
          }}>
            X: {Math.round(currentRobotPos.x)} | Y: {Math.round(currentRobotPos.y)}
          </span>
        </div>
      </div>

      {/* Escort Active Progress Card */}
      {((mapMode === 'virtual' && isSimEscorting) || (mapMode === 'live' && activeEscort)) && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
          padding: '14px 16px',
          background: 'linear-gradient(135deg, #1E40AF, #2563EB)',
          borderRadius: '16px',
          color: '#FFFFFF',
          boxShadow: '0 8px 24px rgba(37,99,235,0.3)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '1.6rem' }}>🤖</span>
              <div>
                <div style={{ fontWeight: 800, fontSize: '0.94rem' }}>
                  {mapMode === 'virtual'
                    ? `MÔ PHỎNG DẪN ĐƯỜNG: ${currentStore.name}`
                    : `ĐANG DẪN ĐƯỜNG ĐẾN: ${activeEscort?.target_name}`}
                </div>
                <div style={{ fontSize: '0.73rem', opacity: 0.9 }}>
                  Xe đang di chuyển tự động dọc hành lang trung tâm ({mapMode === 'virtual' ? simProgress : activeEscort?.current_progress}%)
                </div>
              </div>
            </div>
            <button
              onClick={mapMode === 'virtual' ? cancelVirtualEscort : handleCancelRealEscort}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                padding: '6px 12px',
                backgroundColor: 'rgba(255,255,255,0.2)',
                border: '1px solid rgba(255,255,255,0.4)',
                borderRadius: '8px',
                color: '#FFFFFF',
                fontWeight: 700,
                fontSize: '0.76rem',
                cursor: 'pointer',
              }}
            >
              <XCircle size={14} />
              <span>DỪNG</span>
            </button>
          </div>

          {/* Smooth Real-time Progress Bar */}
          <div style={{ width: '100%', height: '6px', backgroundColor: 'rgba(255,255,255,0.25)', borderRadius: '99px', overflow: 'hidden' }}>
            <div style={{
              width: `${mapMode === 'virtual' ? simProgress : (activeEscort?.current_progress ?? 0)}%`,
              height: '100%',
              backgroundColor: '#FFFFFF',
              borderRadius: '99px',
              transition: 'width 0.3s ease',
            }} />
          </div>
        </div>
      )}

      {/* Main Architectural Floor Map Container */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderRadius: '18px',
        border: '1px solid #E2E8F0',
        boxShadow: '0 2px 10px rgba(0,0,0,0.04)',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}>
        {/* Header & Category Filters */}
        <div style={{
          padding: '12px 14px 10px',
          borderBottom: '1px solid #F1F5F9',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 style={{ margin: 0, fontSize: '1.02rem', fontWeight: 800, color: '#0F172A' }}>
                SƠ ĐỒ TRUNG TÂM THƯƠNG MẠI — TẦNG 1
              </h2>
              <span style={{ fontSize: '0.72rem', color: '#64748B' }}>
                Bản đồ mặt bằng kiến trúc, mạng lưới hành lang và định vị Robot trực tiếp
              </span>
            </div>
            <span style={{ fontSize: '0.72rem', color: '#2563EB', fontWeight: 800, background: '#EFF6FF', padding: '2px 8px', borderRadius: '6px' }}>
              8 GIAN HÀNG
            </span>
          </div>

          {/* Category Filter Chips */}
          <div style={{
            display: 'flex',
            gap: '6px',
            overflowX: 'auto',
            paddingBottom: '2px',
            scrollbarWidth: 'none',
          }}>
            {CATEGORIES.map(cat => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                style={{
                  padding: '5px 12px',
                  borderRadius: '99px',
                  fontSize: '0.74rem',
                  fontWeight: 700,
                  border: selectedCategory === cat.id ? '1px solid #2563EB' : '1px solid #E2E8F0',
                  backgroundColor: selectedCategory === cat.id ? '#EFF6FF' : '#F8FAFC',
                  color: selectedCategory === cat.id ? '#1D4ED8' : '#64748B',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.15s ease',
                }}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Lightweight, High-Performance Architectural Vector SVG Map */}
        <div style={{
          position: 'relative',
          width: '100%',
          backgroundColor: '#F8FAFC',
          userSelect: 'none',
        }}>
          <svg
            viewBox="0 0 1000 680"
            preserveAspectRatio="xMidYMid meet"
            style={{ width: '100%', height: 'auto', display: 'block' }}
          >
            {/* Base Mall Floorplate Outline */}
            <rect x="20" y="15" width="960" height="650" rx="16" fill="#F8FAFC" stroke="#CBD5E1" strokeWidth="2" />

            {/* Walkable Concourse Corridors */}
            {/* North-South Main Concourse */}
            <rect x="405" y="25" width="190" height="630" fill="#FFFFFF" stroke="#E2E8F0" strokeWidth="1" />
            
            {/* East-West Main Concourse */}
            <rect x="25" y="265" width="950" height="160" fill="#FFFFFF" stroke="#E2E8F0" strokeWidth="1" />

            {/* Central Atrium Rotunda Medallion (Marble Architectural Flooring) */}
            <circle cx="500" cy="345" r="95" fill="#FFFFFF" stroke="#CBD5E1" strokeWidth="2" />
            <circle cx="500" cy="345" r="82" fill="#F8FAFC" stroke="#E2E8F0" strokeWidth="1" strokeDasharray="4 4" />
            <circle cx="500" cy="345" r="50" fill="#EFF6FF" stroke="#BFDBFE" strokeWidth="1.5" />
            
            {/* Compass Rose Star in Center */}
            <path d="M 500 325 L 504 341 L 520 345 L 504 349 L 500 365 L 496 349 L 480 345 L 496 341 Z" fill="#93C5FD" opacity="0.7" />
            
            <text x="500" y="342" textAnchor="middle" fill="#1E40AF" fontSize="11" fontWeight="900" letterSpacing="0.8">
              SẢNH TRUNG TÂM
            </text>
            <text x="500" y="356" textAnchor="middle" fill="#64748B" fontSize="9" fontWeight="700">
              ATRIUM ROTUNDA
            </text>

            {/* Corridor Navigation Guidance Lines */}
            <path
              d="M 500 110 L 500 580 M 170 345 L 830 345 M 205 235 L 795 235 M 205 520 L 795 520"
              fill="none"
              stroke="#E2E8F0"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />

            {/* Concourse Wayfinding Labels */}
            <text x="500" y="195" textAnchor="middle" fill="#94A3B8" fontSize="10.5" fontWeight="700" letterSpacing="0.8">
              HÀNH LANG BẮC
            </text>
            <text x="500" y="455" textAnchor="middle" fill="#94A3B8" fontSize="10.5" fontWeight="700" letterSpacing="0.8">
              HÀNH LANG NAM
            </text>
            <text x="205" y="349" textAnchor="middle" fill="#94A3B8" fontSize="10" fontWeight="700">
              HÀNH LANG TÂY
            </text>
            <text x="795" y="349" textAnchor="middle" fill="#94A3B8" fontSize="10" fontWeight="700">
              HÀNH LANG ĐÔNG
            </text>

            {/* Real-time Breadcrumb Trajectory Trail */}
            {trail.length > 1 && (
              <polyline
                points={trail.map(p => `${p.x},${p.y}`).join(' ')}
                fill="none"
                stroke="#06B6D4"
                strokeWidth="4"
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity="0.65"
              />
            )}

            {/* Planned Corridor Route Path */}
            {plannedPathD && (
              <>
                <path
                  d={plannedPathD}
                  fill="none"
                  stroke="#3B82F6"
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity="0.25"
                />
                <path
                  d={plannedPathD}
                  fill="none"
                  stroke="#2563EB"
                  strokeWidth="4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeDasharray="8 6"
                />
              </>
            )}

            {/* Store Lots (Architectural Tenant Layouts) */}
            {MALL_STORES.map(store => {
              const isSelected = selectedStoreId === store.id;
              const isTargetOfEscort = activeEscort?.target_poi_id === store.id;

              return (
                <g
                  key={store.id}
                  onClick={() => setSelectedStoreId(store.id)}
                  style={{ cursor: 'pointer' }}
                >
                  {/* Lot Base Box */}
                  <rect
                    x={store.lotX}
                    y={store.lotY}
                    width={store.lotW}
                    height={store.lotH}
                    rx="14"
                    fill={isSelected ? store.accentBg : '#FFFFFF'}
                    stroke={isSelected ? '#2563EB' : store.borderColor}
                    strokeWidth={isSelected ? 3.5 : 1.5}
                  />

                  {/* Lot Header Ribbon */}
                  <rect
                    x={store.lotX}
                    y={store.lotY}
                    width={store.lotW}
                    height="38"
                    rx="14"
                    fill={store.accentBg}
                    opacity="0.9"
                  />

                  {/* Tenant Code Badge (L1-01, L1-02, etc.) */}
                  <rect
                    x={store.lotX + store.lotW - 56}
                    y={store.lotY + 8}
                    width="46"
                    height="20"
                    rx="6"
                    fill="#FFFFFF"
                    stroke={store.borderColor}
                    strokeWidth="1"
                  />
                  <text
                    x={store.lotX + store.lotW - 33}
                    y={store.lotY + 22}
                    textAnchor="middle"
                    fill="#64748B"
                    fontSize="9.5"
                    fontWeight="800"
                  >
                    {store.lotCode}
                  </text>

                  {/* Icon Circle */}
                  <circle
                    cx={store.lotX + 26}
                    cy={store.lotY + 19}
                    r="14"
                    fill="#FFFFFF"
                    stroke={isSelected ? '#2563EB' : store.borderColor}
                    strokeWidth="1.2"
                  />
                  <text
                    x={store.lotX + 26}
                    y={store.lotY + 25}
                    textAnchor="middle"
                    fontSize="15"
                  >
                    {store.icon}
                  </text>

                  {/* Brand Name */}
                  <text
                    x={store.lotX + 48}
                    y={store.lotY + 24}
                    fill="#0F172A"
                    fontSize="13.5"
                    fontWeight="900"
                  >
                    {store.shortName}
                  </text>

                  {/* Subtitle / Category */}
                  <text
                    x={store.lotX + 16}
                    y={store.lotY + 64}
                    fill="#475569"
                    fontSize="11.5"
                    fontWeight="600"
                  >
                    {store.sub}
                  </text>

                  {/* Promotion Banner inside lot */}
                  {store.promo && (
                    <g transform={`translate(${store.lotX + 14}, ${store.lotY + store.lotH - 34})`}>
                      <rect width={store.lotW - 28} height="22" rx="6" fill="#FFFBEB" stroke="#FDE68A" strokeWidth="1" />
                      <text x="8" y="15" fill="#B45309" fontSize="9.5" fontWeight="800">
                        🎁 {store.promo}
                      </text>
                    </g>
                  )}

                  {/* Storefront Entrance Threshold Beacon */}
                  <circle
                    cx={store.entranceX}
                    cy={store.entranceY}
                    r="6"
                    fill={isSelected ? '#2563EB' : '#94A3B8'}
                    stroke="#FFFFFF"
                    strokeWidth="2"
                  />
                  <text
                    x={store.entranceX}
                    y={store.entranceY < 300 ? store.entranceY - 8 : store.entranceY + 14}
                    textAnchor="middle"
                    fill={isSelected ? '#2563EB' : '#64748B'}
                    fontSize="8.5"
                    fontWeight="800"
                  >
                    LỐI VÀO
                  </text>

                  {/* Active Selection / Escort Badge Indicator */}
                  {isTargetOfEscort ? (
                    <g transform={`translate(${store.lotX + 16}, ${store.lotY + 85})`}>
                      <rect width="84" height="22" rx="11" fill="#2563EB" />
                      <text x="42" y="15" textAnchor="middle" fill="#FFFFFF" fontSize="9.5" fontWeight="900">
                        ĐANG ĐẾN
                      </text>
                    </g>
                  ) : isSelected ? (
                    <g transform={`translate(${store.lotX + 16}, ${store.lotY + 85})`}>
                      <rect width="84" height="22" rx="11" fill="#2563EB" />
                      <text x="42" y="15" textAnchor="middle" fill="#FFFFFF" fontSize="9.5" fontWeight="900">
                        ĐANG CHỌN
                      </text>
                    </g>
                  ) : null}
                </g>
              );
            })}

            {/* Target Destination Ring Beacon */}
            {currentStore && (
              <g transform={`translate(${currentStore.entranceX}, ${currentStore.entranceY})`}>
                <circle r="16" fill="#3B82F6" opacity="0.25" />
                <circle r="7" fill="#2563EB" stroke="#FFFFFF" strokeWidth="2.5" />
              </g>
            )}

            {/* ==================== REALTIME HIGH-TECH ROBOT AVATAR ==================== */}
            <g
              transform={`translate(${currentRobotPos.x}, ${currentRobotPos.y})`}
              style={{ transition: 'transform 0.12s linear' }}
            >
              {/* Rotating LiDAR Radar Field-of-View Cone */}
              <g transform={`rotate(${currentRobotHeading})`}>
                <path
                  d="M 0 0 L -40 -75 A 85 85 0 0 1 40 -75 Z"
                  fill="#3B82F6"
                  opacity="0.18"
                />
                {/* Heading Arrow Pointer */}
                <polygon points="0,-24 8,-14 -8,-14" fill="#2563EB" />

                {/* Differential Drive 4 Wheels */}
                <rect x="-18" y="-16" width="5" height="10" rx="2" fill="#1E293B" />
                <rect x="13" y="-16" width="5" height="10" rx="2" fill="#1E293B" />
                <rect x="-18" y="6" width="5" height="10" rx="2" fill="#1E293B" />
                <rect x="13" y="6" width="5" height="10" rx="2" fill="#1E293B" />
              </g>

              {/* Central AMR Robot Puck */}
              <circle r="16" fill="#2563EB" stroke="#FFFFFF" strokeWidth="3" />
              <text x="0" y="5" textAnchor="middle" fill="#FFFFFF" fontSize="13">
                🤖
              </text>

              {/* Floating Name Badge */}
              <g transform="translate(0, -28)">
                <rect x="-34" y="-10" width="68" height="16" rx="8" fill="#0F172A" />
                <text x="0" y="2" textAnchor="middle" fill="#FFFFFF" fontSize="8.5" fontWeight="900">
                  {mapMode === 'virtual' ? 'XE ẢO' : 'ROBOT'}
                </text>
              </g>
            </g>
          </svg>
        </div>

        {/* Quick Horizontal Store Switcher Chips */}
        <div style={{
          display: 'flex',
          gap: '6px',
          overflowX: 'auto',
          padding: '8px 12px',
          backgroundColor: '#F8FAFC',
          borderTop: '1px solid #F1F5F9',
          scrollbarWidth: 'none',
        }}>
          {filteredStores.map(store => {
            const isSelected = selectedStoreId === store.id;
            return (
              <button
                key={store.id}
                onClick={() => setSelectedStoreId(store.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  padding: '5px 11px',
                  borderRadius: '99px',
                  fontSize: '0.75rem',
                  fontWeight: 800,
                  border: isSelected ? '1.5px solid #2563EB' : '1px solid #E2E8F0',
                  backgroundColor: isSelected ? '#EFF6FF' : '#FFFFFF',
                  color: isSelected ? '#1D4ED8' : '#334155',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  flexShrink: 0,
                  transition: 'all 0.15s ease'
                }}
              >
                <span>{store.icon}</span>
                <span>{store.shortName}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* ==================== VIRTUAL DRIVE / SIMULATION CONTROLS TOOLBAR ==================== */}
      {mapMode === 'virtual' && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#FFFFFF',
          borderRadius: '16px',
          border: '1.5px solid #BFDBFE',
          padding: '14px 16px',
          boxShadow: '0 2px 8px rgba(37,99,235,0.06)',
          gap: '10px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Gamepad2 size={18} color="#2563EB" />
              <span style={{ fontWeight: 800, fontSize: '0.86rem', color: '#0F172A' }}>
                BẢNG ĐIỀU KHIỂN LÁI XE ẢO REALTIME:
              </span>
              <span style={{ fontSize: '0.72rem', color: '#64748B' }}>
                (Dùng nút bấm hoặc phím <strong>W, A, S, D</strong> để lái xe trên bản đồ)
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <button
                onClick={handleResetVirtualRobot}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '5px 10px',
                  backgroundColor: '#F1F5F9',
                  border: '1px solid #CBD5E1',
                  borderRadius: '8px',
                  fontSize: '0.73rem',
                  fontWeight: 700,
                  color: '#475569',
                  cursor: 'pointer'
                }}
              >
                <RotateCcw size={13} />
                <span>Về Lễ Tân</span>
              </button>
            </div>
          </div>

          {/* D-Pad Buttons Row */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <button
              onClick={() => handleVirtualDrive('forward')}
              style={{
                padding: '8px 16px',
                backgroundColor: drivingKey === 'forward' ? '#2563EB' : '#F8FAFC',
                color: drivingKey === 'forward' ? '#FFFFFF' : '#1E293B',
                border: '1.5px solid #CBD5E1',
                borderRadius: '9px',
                fontWeight: 800,
                fontSize: '0.8rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              <ArrowUp size={15} /> TIẾN (W)
            </button>
            <button
              onClick={() => handleVirtualDrive('left')}
              style={{
                padding: '8px 16px',
                backgroundColor: drivingKey === 'left' ? '#2563EB' : '#F8FAFC',
                color: drivingKey === 'left' ? '#FFFFFF' : '#1E293B',
                border: '1.5px solid #CBD5E1',
                borderRadius: '9px',
                fontWeight: 800,
                fontSize: '0.8rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              <ArrowLeft size={15} /> TRÁI (A)
            </button>
            <button
              onClick={() => handleVirtualDrive('right')}
              style={{
                padding: '8px 16px',
                backgroundColor: drivingKey === 'right' ? '#2563EB' : '#F8FAFC',
                color: drivingKey === 'right' ? '#FFFFFF' : '#1E293B',
                border: '1.5px solid #CBD5E1',
                borderRadius: '9px',
                fontWeight: 800,
                fontSize: '0.8rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              PHẢI (D) <ArrowRight size={15} />
            </button>
            <button
              onClick={() => handleVirtualDrive('backward')}
              style={{
                padding: '8px 16px',
                backgroundColor: drivingKey === 'backward' ? '#2563EB' : '#F8FAFC',
                color: drivingKey === 'backward' ? '#FFFFFF' : '#1E293B',
                border: '1.5px solid #CBD5E1',
                borderRadius: '9px',
                fontWeight: 800,
                fontSize: '0.8rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              <ArrowDown size={15} /> LÙI (S)
            </button>
            <button
              onClick={() => handleVirtualDrive('stop')}
              style={{
                padding: '8px 16px',
                backgroundColor: '#FEE2E2',
                color: '#DC2626',
                border: '1.5px solid #FCA5A5',
                borderRadius: '9px',
                fontWeight: 800,
                fontSize: '0.8rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              <Square size={14} /> DỪNG
            </button>
          </div>
        </div>
      )}

      {/* Selected Store Detail Card & Primary Call To Action */}
      {currentStore && (
        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '18px',
          border: '1px solid #E2E8F0',
          padding: '16px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.03)',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
        }}>
          {/* Store Info Row */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '54px',
              height: '54px',
              borderRadius: '14px',
              backgroundColor: currentStore.accentBg,
              border: `1.5px solid ${currentStore.borderColor}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '2.1rem',
              flexShrink: 0,
            }}>
              {currentStore.icon}
            </div>

            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                <h3 style={{ margin: 0, fontSize: '1.12rem', fontWeight: 900, color: '#0F172A' }}>
                  {currentStore.name}
                </h3>
                <span style={{
                  fontSize: '0.7rem',
                  padding: '2px 8px',
                  borderRadius: '99px',
                  backgroundColor: currentStore.accentBg,
                  color: currentStore.color,
                  fontWeight: 800,
                }}>
                  {currentStore.sub}
                </span>
              </div>
              <p style={{ margin: '3px 0 0', fontSize: '0.8rem', color: '#64748B', lineHeight: '1.3' }}>
                {currentStore.description}
              </p>
            </div>
          </div>

          {/* Location & Hours Chips */}
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px',
            paddingTop: '8px',
            borderTop: '1px solid #F8FAFC',
            fontSize: '0.75rem',
            color: '#64748B',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <MapPin size={14} color="#2563EB" />
              <span>{currentStore.wing}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={14} color="#2563EB" />
              <span>{currentStore.hours}</span>
            </div>
          </div>

          {/* Active Promotion Banner */}
          {currentStore.promo && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 12px',
              backgroundColor: '#FFFBEB',
              border: '1px solid #FDE68A',
              borderRadius: '10px',
              fontSize: '0.78rem',
              color: '#92400E',
              fontWeight: 800,
            }}>
              <Sparkles size={15} color="#D97706" style={{ flexShrink: 0 }} />
              <span>Ưu đãi: {currentStore.promo}</span>
            </div>
          )}

          {/* Primary Action Button */}
          <div>
            <button
              onClick={handlePrimaryAction}
              disabled={loadingEscort}
              style={{
                width: '100%',
                padding: '13px',
                background: (mapMode === 'virtual' ? isSimEscorting : activeEscort)
                  ? '#FEE2E2'
                  : 'linear-gradient(135deg, #1D4ED8, #2563EB)',
                border: (mapMode === 'virtual' ? isSimEscorting : activeEscort)
                  ? '1.5px solid #FCA5A5'
                  : 'none',
                borderRadius: '14px',
                color: (mapMode === 'virtual' ? isSimEscorting : activeEscort) ? '#DC2626' : '#FFFFFF',
                fontWeight: 900,
                fontSize: '0.94rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: (mapMode === 'virtual' ? isSimEscorting : activeEscort)
                  ? 'none'
                  : '0 4px 14px rgba(37,99,235,0.3)',
                cursor: loadingEscort ? 'not-allowed' : 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              {(mapMode === 'virtual' ? isSimEscorting : activeEscort) ? (
                <>
                  <XCircle size={18} />
                  <span>DỪNG DẪN ĐƯỜNG</span>
                </>
              ) : (
                <>
                  <Navigation size={18} />
                  <span>
                    {mapMode === 'virtual'
                      ? 'CHẠY DẪN ĐƯỜNG MÔ PHỎNG (VIRTUAL DRIVE)'
                      : (loadingEscort ? 'ĐANG CHUẨN BỊ LỘ TRÌNH...' : 'ROBOT DẪN TÔI ĐẾN ĐÂY')}
                  </span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

    </div>
  );
};
