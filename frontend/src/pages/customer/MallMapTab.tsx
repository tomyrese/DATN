import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { PointOfInterest } from '../../types/protocol';
import {
  Navigation,
  XCircle,
  Search,
  CheckCircle2,
  Sparkles,
  MapPin,
  Clock,
  Compass,
  Zap,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Square,
  ShieldAlert,
  Layers,
} from 'lucide-react';

interface StoreMeta {
  id: string;
  name: string;
  sub: string;
  category: string;
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
}

const MALL_STORES: StoreMeta[] = [
  {
    id: 'poi_uniqlo',
    name: 'UNIQLO LifeWear',
    sub: 'Thời trang Nhật Bản',
    category: 'fashion',
    lotX: 50,
    lotY: 40,
    lotW: 320,
    lotH: 170,
    entranceX: 210,
    entranceY: 230,
    color: '#EC4899',
    borderColor: '#F472B6',
    accentBg: '#FDF2F8',
    icon: '👕',
    description: 'Trang phục thường ngày cao cấp phong cách Nhật Bản dành cho mọi lứa tuổi.',
    promo: 'Giảm 20% bộ sưu tập mùa hè',
  },
  {
    id: 'poi_kura_sushi',
    name: 'Nhà Hàng Kura Sushi',
    sub: 'Ẩm thực Nhật Bản',
    category: 'food',
    lotX: 410,
    lotY: 40,
    lotW: 180,
    lotH: 170,
    entranceX: 500,
    entranceY: 230,
    color: '#D97706',
    borderColor: '#FBBF24',
    accentBg: '#FFFBEB',
    icon: '🍣',
    description: 'Sushi băng chuyền công nghệ cao, hải sản nhập khẩu tươi ngon mỗi ngày.',
    promo: 'Tặng 1 đĩa cá hồi cho hóa đơn từ 500k',
  },
  {
    id: 'poi_zara',
    name: 'Thời Trang ZARA',
    sub: 'Thời trang Quốc tế',
    category: 'fashion',
    lotX: 630,
    lotY: 40,
    lotW: 320,
    lotH: 170,
    entranceX: 790,
    entranceY: 230,
    color: '#8B5CF6',
    borderColor: '#A78BFA',
    accentBg: '#F5F3FF',
    icon: '👗',
    description: 'Thương hiệu thời trang cao cấp Tây Ban Nha với xu hướng mới nhất toàn cầu.',
    promo: 'Ưu đãi lên đến 30% cho thành viên',
  },
  {
    id: 'poi_highlands',
    name: 'Highlands Coffee',
    sub: 'Cà phê & Bánh ngọt',
    category: 'food',
    lotX: 50,
    lotY: 260,
    lotW: 270,
    lotH: 160,
    entranceX: 340,
    entranceY: 340,
    color: '#DC2626',
    borderColor: '#F87171',
    accentBg: '#FEF2F2',
    icon: '☕',
    description: 'Cà phê pha phin truyền thống đậm đà, Freeze đá xay và trà sen vàng trứ danh.',
    promo: 'Mua 2 tặng 1 vào khung giờ 14h - 17h',
  },
  {
    id: 'poi_cgv',
    name: 'Rạp Phim CGV Cinemas',
    sub: 'Rạp chiếu phim IMAX',
    category: 'entertainment',
    lotX: 680,
    lotY: 260,
    lotW: 270,
    lotH: 160,
    entranceX: 660,
    entranceY: 340,
    color: '#9333EA',
    borderColor: '#C084FC',
    accentBg: '#FAF5FF',
    icon: '🎬',
    description: 'Cụm rạp chiếu phim màn hình lớn IMAX & 4DX hiện đại với hệ thống âm thanh Dolby Atmos.',
    promo: 'Combo bắp nước giảm 15% khi đặt vé trước',
  },
  {
    id: 'poi_elevator',
    name: 'Thang Máy & Bãi Xe',
    sub: 'Lên xuống tầng & Hầm B1',
    category: 'utility',
    lotX: 50,
    lotY: 470,
    lotW: 270,
    lotH: 170,
    entranceX: 340,
    entranceY: 530,
    color: '#16A34A',
    borderColor: '#4ADE80',
    accentBg: '#F0FDF4',
    icon: '🛗',
    description: 'Cụm thang máy kính tốc độ cao kết nối các tầng T1, T2, T3 và bãi giữ xe tầng hầm.',
  },
  {
    id: 'poi_reception',
    name: 'Lễ Tân & Trạm Sạc Robot',
    sub: 'Sảnh chính & Xuất phát',
    category: 'utility',
    lotX: 380,
    lotY: 470,
    lotW: 240,
    lotH: 170,
    entranceX: 500,
    entranceY: 510,
    color: '#2563EB',
    borderColor: '#60A5FA',
    accentBg: '#EFF6FF',
    icon: '💁',
    description: 'Quầy thông tin CSKH trung tâm và điểm xuất phát / sạc pin tự động của Robot.',
  },
  {
    id: 'poi_wc',
    name: 'Khu Vệ Sinh & Tiện Ích',
    sub: 'WC Nam / Nữ / Em Bé',
    category: 'utility',
    lotX: 680,
    lotY: 470,
    lotW: 270,
    lotH: 170,
    entranceX: 660,
    entranceY: 530,
    color: '#0D9488',
    borderColor: '#2DD4BF',
    accentBg: '#F0FDFA',
    icon: '🚻',
    description: 'Khu vệ sinh hiện đại trang bị thiết bị tự động và phòng thay tã cho mẹ & bé.',
  },
];

const CATEGORIES = [
  { id: 'all', label: 'Tất Cả' },
  { id: 'food', label: '🍔 Ăn Uống' },
  { id: 'fashion', label: '👗 Thời Trang' },
  { id: 'entertainment', label: '🎬 Rạp Phim' },
  { id: 'utility', label: '🚻 Tiện Ích' },
];

export const MallMapTab: React.FC = () => {
  const { activeEscort, pairedRobot, telemetry, currentUser } = useRobotStore();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedStoreId, setSelectedStoreId] = useState<string>('poi_cgv');
  const [searchQuery, setSearchQuery] = useState('');
  const [loadingEscort, setLoadingEscort] = useState(false);
  const [drivingManual, setDrivingManual] = useState(false);

  // Breadcrumb trajectory of real robot movements (stored as SVG coordinates)
  const [trail, setTrail] = useState<{ x: number; y: number }[]>([]);

  // Selected store details
  const currentStore = useMemo(() => {
    return MALL_STORES.find(s => s.id === selectedStoreId) || MALL_STORES[0];
  }, [selectedStoreId]);

  // Filtered stores
  const filteredStores = useMemo(() => {
    return MALL_STORES.filter(s => {
      const matchCat = selectedCategory === 'all' || s.category === selectedCategory;
      const matchSearch =
        s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.sub.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [selectedCategory, searchQuery]);

  // Coordinate Conversion: (x: 0..100, y: 0..70) -> SVG (1000 x 700)
  // Default robot start: Reception desk (x=50, y=51 -> svgX=500, svgY=510)
  const defaultRobotSvg = { x: 500, y: 510 };

  const rawOdomX = telemetry?.odometryX;
  const rawOdomY = telemetry?.odometryY;
  const odomHeading = telemetry?.odometryHeading ?? 0;
  const odomHeadingDeg = Math.round((odomHeading * 180) / Math.PI);
  const odomConfidence = Math.round((telemetry?.odometryConfidence ?? 0.95) * 100);

  // Compute live SVG position
  const robotSvgPos = useMemo(() => {
    if (rawOdomX !== undefined && rawOdomX !== null && rawOdomY !== undefined && rawOdomY !== null) {
      // Map metric (0..100) to SVG (0..1000) and (0..70) to SVG (0..700)
      const mappedX = Math.max(60, Math.min(940, rawOdomX * 10.0));
      const mappedY = Math.max(50, Math.min(650, rawOdomY * 10.0));
      return { x: mappedX, y: mappedY };
    }
    return defaultRobotSvg;
  }, [rawOdomX, rawOdomY]);

  // Record breadcrumbs trail as robot drives
  useEffect(() => {
    setTrail(prev => {
      const last = prev[prev.length - 1];
      if (!last || Math.hypot(last.x - robotSvgPos.x, last.y - robotSvgPos.y) > 12) {
        return [...prev.slice(-40), robotSvgPos];
      }
      return prev;
    });
  }, [robotSvgPos]);

  // Escort mission path (A* Corridor Waypoints Path)
  // Route: Robot -> Corridor Spine -> Target Store Entrance
  const plannedPathD = useMemo(() => {
    if (!currentStore) return '';
    const start = robotSvgPos;
    const target = { x: currentStore.entranceX, y: currentStore.entranceY };

    // Waypoint routing through central corridors
    // Corridors intersections:
    // South Atrium: (500, 510)
    // Central Cross: (500, 340)
    // North Cross: (500, 230)
    const waypoints: { x: number; y: number }[] = [start];

    // If starting near South, pass through Central Cross first
    if (start.y > 420) {
      waypoints.push({ x: 500, y: 440 });
    }

    // Pass through central atrium
    waypoints.push({ x: 500, y: 340 });

    // Branch to target entrance along corridor
    if (target.y < 300) {
      // North wing target
      waypoints.push({ x: 500, y: 230 });
      waypoints.push({ x: target.x, y: 230 });
      waypoints.push(target);
    } else if (target.y > 450) {
      // South wing target
      waypoints.push({ x: 500, y: 440 });
      waypoints.push({ x: target.x, y: target.y });
      waypoints.push(target);
    } else {
      // East/West wing target
      waypoints.push({ x: target.x, y: 340 });
      waypoints.push(target);
    }

    // Build SVG path
    return waypoints.reduce((acc, pt, idx) => {
      return idx === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`;
    }, '');
  }, [robotSvgPos, currentStore]);

  // Handlers for Escort
  const handleStartEscort = async (store: StoreMeta) => {
    const host = pairedRobot?.host || '';
    const port = pairedRobot?.port || 8765;
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

  const handleCancelEscort = async () => {
    const host = pairedRobot?.host || '';
    const port = pairedRobot?.port || 8765;
    try {
      await RobotApi.cancelEscort(host, port);
      updateGlobalState(() => ({ activeEscort: null }));
    } catch (e) {}
  };

  // Test drive control handler
  const handleDrive = async (direction: string) => {
    const host = pairedRobot?.host || '';
    const port = pairedRobot?.port || 8765;
    const token = currentUser?.token;
    setDrivingManual(true);
    await RobotApi.directDrive(host, port, direction, 0.35, token);
    setTimeout(() => setDrivingManual(false), 300);
  };

  // Poll escort status if active
  useEffect(() => {
    if (!activeEscort || activeEscort.status !== 'NAVIGATING') return;
    const host = pairedRobot?.host || '';
    const port = pairedRobot?.port || 8765;

    const interval = setInterval(async () => {
      try {
        const task = await RobotApi.getEscortStatus(host, port);
        if (task) {
          updateGlobalState(() => ({ activeEscort: task }));
          if (task.status === 'ARRIVED') {
            alert(`🎉 Robot đã dẫn quý khách đến nơi: ${task.target_name}!`);
            setTimeout(() => {
              updateGlobalState(() => ({ activeEscort: null }));
            }, 3000);
          }
        }
      } catch (err) {}
    }, 800);

    return () => clearInterval(interval);
  }, [activeEscort?.status]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', width: '100%', maxWidth: '100%' }}>
      
      {/* Top Telemetry & Status HUD Bar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '10px 16px',
        backgroundColor: '#FFFFFF',
        borderRadius: '12px',
        border: '1px solid #E2E8F0',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
        gap: '8px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: telemetry?.robotState === 'STOPPED' ? '#10B981' : '#3B82F6',
            boxShadow: '0 0 8px rgba(59,130,246,0.6)'
          }} />
          <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#1E293B' }}>
            ROBOT TỰ HÀNH: {telemetry?.robotState || 'SẴN SÀNG'}
          </span>
          <span style={{
            fontSize: '0.72rem',
            padding: '2px 8px',
            borderRadius: '99px',
            backgroundColor: '#EFF6FF',
            color: '#1D4ED8',
            fontWeight: 700
          }}>
            TẦNG 1 SẢNH CHÍNH
          </span>
        </div>

        {/* Real Odometry Metrics */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.75rem', color: '#64748B' }}>
          <span title="Tọa độ tích phân Dead-Reckoning">
            📍 <strong>X:</strong> {(rawOdomX ?? 50.0).toFixed(1)}m, <strong>Y:</strong> {(rawOdomY ?? 51.0).toFixed(1)}m
          </span>
          <span title="Góc quay Robot">
            🧭 <strong>Hướng:</strong> {odomHeadingDeg}°
          </span>
          <span title="Độ tin cậy cảm biến" style={{ color: odomConfidence > 80 ? '#059669' : '#D97706', fontWeight: 700 }}>
            ⚡ Tin cậy: {odomConfidence}%
          </span>
          <span style={{ fontSize: '0.7rem', padding: '2px 6px', borderRadius: '4px', backgroundColor: '#FEF3C7', color: '#B45309', fontWeight: 800 }}>
            [DEAD-RECKONING]
          </span>
        </div>
      </div>

      {/* Escort Active Banner */}
      {activeEscort && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 18px',
          background: 'linear-gradient(135deg, #1E40AF, #3B82F6)',
          borderRadius: '12px',
          color: '#FFFFFF',
          boxShadow: '0 4px 12px rgba(59,130,246,0.3)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
            <div style={{ fontSize: '1.8rem', animation: 'bounce 1s infinite' }}>🤖</div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <span style={{ fontWeight: 800, fontSize: '0.95rem' }}>ĐANG DẪN ĐƯỜNG ĐẾN: {activeEscort.target_name}</span>
                <span style={{ fontWeight: 800, fontSize: '0.85rem' }}>{activeEscort.current_progress}%</span>
              </div>
              <div style={{ width: '100%', height: '6px', backgroundColor: 'rgba(255,255,255,0.25)', borderRadius: '99px', overflow: 'hidden' }}>
                <div style={{ width: `${activeEscort.current_progress}%`, height: '100%', backgroundColor: '#FFFFFF', borderRadius: '99px', transition: 'width 0.3s ease' }} />
              </div>
              <span style={{ fontSize: '0.72rem', opacity: 0.9 }}>Quý khách vui lòng đi theo sau Robot, xe đang di chuyển dọc hành lang</span>
            </div>
          </div>
          <button
            onClick={handleCancelEscort}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              backgroundColor: 'rgba(255,255,255,0.2)',
              border: '1px solid rgba(255,255,255,0.4)',
              borderRadius: '8px',
              color: '#FFFFFF',
              fontWeight: 700,
              cursor: 'pointer',
              marginLeft: '14px',
            }}
          >
            <XCircle size={15} />
            <span>HỦY</span>
          </button>
        </div>
      )}

      {/* Main Architectural SVG Map Container */}
      <div style={{
        position: 'relative',
        backgroundColor: '#FFFFFF',
        borderRadius: '16px',
        border: '1px solid #CBD5E1',
        boxShadow: '0 4px 16px rgba(0,0,0,0.06)',
        overflow: 'hidden',
      }}>
        {/* Floor Title & Category Filters */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 18px',
          borderBottom: '1px solid #F1F5F9',
          gap: '10px',
        }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 800, color: '#0F172A' }}>
              SƠ ĐỒ TRUNG TÂM THƯƠNG MẠI — TẦNG 1
            </h2>
            <p style={{ margin: 0, fontSize: '0.75rem', color: '#64748B' }}>
              Mặt bằng kiến trúc thực tế, mạng lưới hành lang an toàn và vị trí định vị Robot trực tiếp
            </p>
          </div>

          {/* Category Chips */}
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {CATEGORIES.map(cat => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                style={{
                  padding: '5px 11px',
                  borderRadius: '99px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  border: selectedCategory === cat.id ? '1px solid #3B82F6' : '1px solid #E2E8F0',
                  backgroundColor: selectedCategory === cat.id ? '#EFF6FF' : '#FFFFFF',
                  color: selectedCategory === cat.id ? '#1D4ED8' : '#64748B',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* SVG Viewport */}
        <div style={{ position: 'relative', width: '100%', height: 'auto', backgroundColor: '#F8FAFC' }}>
          <svg viewBox="0 0 1000 700" preserveAspectRatio="xMidYMid meet" style={{ width: '100%', height: 'auto', display: 'block' }}>
            <defs>
              {/* Floor Tile Grid Texture */}
              <pattern id="floor-grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#F1F5F9" strokeWidth="0.8" />
              </pattern>

              {/* Corridor Tile Texture */}
              <pattern id="corridor-grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#E2E8F0" strokeWidth="1" />
              </pattern>

              {/* Laser / Radar Vision Gradient */}
              <radialGradient id="radar-beam" cx="50%" cy="100%" r="100%">
                <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.45" />
                <stop offset="60%" stopColor="#60A5FA" stopOpacity="0.15" />
                <stop offset="100%" stopColor="#93C5FD" stopOpacity="0.0" />
              </radialGradient>

              {/* Active Route Pulse Animation */}
              <linearGradient id="route-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#2563EB" />
                <stop offset="100%" stopColor="#06B6D4" />
              </linearGradient>

              {/* Store Drop Shadow */}
              <filter id="lot-shadow" x="-5%" y="-5%" width="110%" height="115%">
                <feDropShadow dx="0" dy="3" stdDeviation="4" floodColor="#0F172A" floodOpacity="0.06" />
              </filter>
            </defs>

            {/* Base Background Floor */}
            <rect width="1000" height="700" fill="#F8FAFC" />
            <rect width="1000" height="700" fill="url(#floor-grid)" />

            {/* Outer Mall Perimeter Walls */}
            <rect x="25" y="20" width="950" height="660" rx="14" fill="none" stroke="#94A3B8" strokeWidth="3" />
            <rect x="30" y="25" width="940" height="650" rx="10" fill="none" stroke="#CBD5E1" strokeWidth="1" />

            {/* ==================== WALKABLE CONCOURSE CORRIDORS ==================== */}
            {/* North-South Main Concourse */}
            <rect x="420" y="30" width="160" height="640" fill="#FFFFFF" stroke="#E2E8F0" strokeWidth="1.5" />
            <rect x="420" y="30" width="160" height="640" fill="url(#corridor-grid)" opacity="0.6" />

            {/* East-West Main Concourse */}
            <rect x="30" y="280" width="940" height="130" fill="#FFFFFF" stroke="#E2E8F0" strokeWidth="1.5" />
            <rect x="30" y="280" width="940" height="130" fill="url(#corridor-grid)" opacity="0.6" />

            {/* Central Atrium Rotunda Medallion */}
            <circle cx="500" cy="345" r="95" fill="#FFFFFF" stroke="#CBD5E1" strokeWidth="2" />
            <circle cx="500" cy="345" r="85" fill="#F8FAFC" stroke="#E2E8F0" strokeWidth="1" strokeDasharray="4 4" />
            <circle cx="500" cy="345" r="45" fill="#EFF6FF" stroke="#BFDBFE" strokeWidth="1.5" />
            <text x="500" y="342" textAnchor="middle" fill="#1E40AF" fontSize="11" fontWeight="800" letterSpacing="1">
              SẢNH TRUNG TÂM
            </text>
            <text x="500" y="356" textAnchor="middle" fill="#64748B" fontSize="9" fontWeight="600">
              ATRIUM ROTUNDA
            </text>

            {/* Concourse Corridor Labels */}
            <text x="500" y="195" textAnchor="middle" fill="#94A3B8" fontSize="11" fontWeight="800" letterSpacing="1">
              HÀNH LANG BẮC (NORTH WING)
            </text>
            <text x="500" y="475" textAnchor="middle" fill="#94A3B8" fontSize="11" fontWeight="800" letterSpacing="1">
              HÀNH LANG NAM (SOUTH CONCOURSE)
            </text>
            <text x="210" y="350" textAnchor="middle" fill="#94A3B8" fontSize="11" fontWeight="800" letterSpacing="1">
              HÀNH LANG TÂY
            </text>
            <text x="790" y="350" textAnchor="middle" fill="#94A3B8" fontSize="11" fontWeight="800" letterSpacing="1">
              HÀNH LANG ĐÔNG
            </text>

            {/* Navigation Guide Tracks (Topological Corridor Graph) */}
            <path
              d="M 500 110 L 500 580 M 170 345 L 830 345 M 210 230 L 790 230 M 210 530 L 790 530"
              fill="none"
              stroke="#CBD5E1"
              strokeWidth="1.2"
              strokeDasharray="4 4"
            />

            {/* ==================== STORE LOTS & TENANT HUBS ==================== */}
            {MALL_STORES.map(store => {
              const isSelected = selectedStoreId === store.id;
              const isTargetOfEscort = activeEscort?.target_poi_id === store.id;

              return (
                <g
                  key={store.id}
                  onClick={() => setSelectedStoreId(store.id)}
                  style={{ cursor: 'pointer' }}
                >
                  {/* Store Lot Box */}
                  <rect
                    x={store.lotX}
                    y={store.lotY}
                    width={store.lotW}
                    height={store.lotH}
                    rx="12"
                    fill={isSelected ? store.accentBg : '#FFFFFF'}
                    stroke={isSelected ? store.color : store.borderColor}
                    strokeWidth={isSelected ? 3 : 1.5}
                    filter="url(#lot-shadow)"
                    style={{ transition: 'all 0.2s ease' }}
                  />

                  {/* Store Brand Header Bar */}
                  <rect
                    x={store.lotX}
                    y={store.lotY}
                    width={store.lotW}
                    height="32"
                    rx="12"
                    fill={store.accentBg}
                    opacity="0.8"
                  />

                  {/* Icon & Store Name */}
                  <text x={store.lotX + 14} y={store.lotY + 22} fontSize="16">
                    {store.icon}
                  </text>
                  <text
                    x={store.lotX + 40}
                    y={store.lotY + 21}
                    fill="#0F172A"
                    fontSize="12.5"
                    fontWeight="800"
                  >
                    {store.name}
                  </text>

                  {/* Subtitle / Category */}
                  <text
                    x={store.lotX + 14}
                    y={store.lotY + 52}
                    fill="#64748B"
                    fontSize="10"
                    fontWeight="600"
                  >
                    {store.sub}
                  </text>

                  {/* Storefront Entrance Threshold Glass Door (Facing Corridor) */}
                  <circle
                    cx={store.entranceX}
                    cy={store.entranceY}
                    r="6"
                    fill={isSelected ? store.color : '#94A3B8'}
                    stroke="#FFFFFF"
                    strokeWidth="2"
                  />
                  <text
                    x={store.entranceX}
                    y={store.entranceY < 300 ? store.entranceY - 8 : store.entranceY + 14}
                    textAnchor="middle"
                    fill={isSelected ? store.color : '#64748B'}
                    fontSize="8.5"
                    fontWeight="800"
                  >
                    CỬA VÀO
                  </text>

                  {/* Selection / Escort Badge Indicator */}
                  {isTargetOfEscort ? (
                    <g transform={`translate(${store.lotX + store.lotW - 90}, ${store.lotY + 42})`}>
                      <rect width="82" height="20" rx="10" fill="#2563EB" />
                      <text x="41" y="13.5" textAnchor="middle" fill="#FFFFFF" fontSize="9" fontWeight="800">
                        ĐANG ĐẾN ĐÂY
                      </text>
                    </g>
                  ) : isSelected ? (
                    <g transform={`translate(${store.lotX + store.lotW - 85}, ${store.lotY + 42})`}>
                      <rect width="76" height="20" rx="10" fill={store.color} />
                      <text x="38" y="13.5" textAnchor="middle" fill="#FFFFFF" fontSize="9" fontWeight="800">
                        ĐANG CHỌN
                      </text>
                    </g>
                  ) : null}

                  {/* Promo Badge inside store */}
                  {store.promo && (
                    <g transform={`translate(${store.lotX + 14}, ${store.lotY + store.lotH - 30})`}>
                      <rect width={store.lotW - 28} height="18" rx="4" fill="#FEF3C7" stroke="#FDE68A" strokeWidth="0.8" />
                      <text x="8" y="12.5" fill="#92400E" fontSize="8.5" fontWeight="700">
                        🎁 {store.promo}
                      </text>
                    </g>
                  )}
                </g>
              );
            })}

            {/* ==================== BREADCRUMB EXECUTED TRAIL ==================== */}
            {trail.length > 1 && (
              <polyline
                points={trail.map(p => `${p.x},${p.y}`).join(' ')}
                fill="none"
                stroke="#06B6D4"
                strokeWidth="3.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity="0.65"
              />
            )}

            {/* ==================== PLANNED ESCORT A* CORRIDOR ROUTE ==================== */}
            {plannedPathD && (
              <>
                {/* Route Glow Underlay */}
                <path
                  d={plannedPathD}
                  fill="none"
                  stroke="#3B82F6"
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity="0.25"
                />
                {/* Animated Dashed Primary Route */}
                <path
                  d={plannedPathD}
                  fill="none"
                  stroke="url(#route-gradient)"
                  strokeWidth="4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeDasharray="8 6"
                />
              </>
            )}

            {/* Target Destination Flag Marker */}
            {currentStore && (
              <g transform={`translate(${currentStore.entranceX}, ${currentStore.entranceY})`}>
                <circle r="14" fill="#3B82F6" opacity="0.2" />
                <circle r="7" fill="#2563EB" stroke="#FFFFFF" strokeWidth="2" />
                <circle r="3" fill="#FFFFFF" />
              </g>
            )}

            {/* ==================== REAL ROBOT AVATAR & SENSORS ==================== */}
            <g
              transform={`translate(${robotSvgPos.x}, ${robotSvgPos.y})`}
              style={{ transition: 'transform 0.15s linear' }}
            >
              {/* Radar Vision Beam (Rotates with Heading) */}
              <g transform={`rotate(${odomHeadingDeg})`}>
                {/* Front Radar Field-of-View Cone */}
                <path
                  d="M 0 0 L -35 -70 A 80 80 0 0 1 35 -70 Z"
                  fill="url(#radar-beam)"
                />

                {/* Ultrasonic Dual Beams (Left: -15°, Right: +15°) */}
                <line x1="-12" y1="-18" x2="-26" y2="-55" stroke="#10B981" strokeWidth="1.8" strokeDasharray="3 3" opacity="0.8" />
                <line x1="12" y1="-18" x2="26" y2="-55" stroke="#10B981" strokeWidth="1.8" strokeDasharray="3 3" opacity="0.8" />

                {/* Ultrasonic Sensor Rings */}
                <circle cx="-12" cy="-18" r="3.5" fill="#10B981" stroke="#FFFFFF" strokeWidth="1" />
                <circle cx="12" cy="-18" r="3.5" fill="#10B981" stroke="#FFFFFF" strokeWidth="1" />
              </g>

              {/* Pulsing Outer Motion Aura */}
              <circle r="24" fill="#3B82F6" opacity="0.2">
                <animate attributeName="r" values="22;28;22" dur="2s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.25;0.05;0.25" dur="2s" repeatCount="indefinite" />
              </circle>

              {/* Robot Chassis (Differential Drive 4 Wheels) */}
              <g transform={`rotate(${odomHeadingDeg})`}>
                {/* 4 Wheels */}
                <rect x="-20" y="-18" width="5" height="12" rx="2" fill="#1E293B" />
                <rect x="15" y="-18" width="5" height="12" rx="2" fill="#1E293B" />
                <rect x="-20" y="6" width="5" height="12" rx="2" fill="#1E293B" />
                <rect x="15" y="6" width="5" height="12" rx="2" fill="#1E293B" />

                {/* Main Body Frame */}
                <rect x="-16" y="-18" width="32" height="36" rx="8" fill="#0F172A" stroke="#3B82F6" strokeWidth="2" />
                <rect x="-13" y="-15" width="26" height="30" rx="6" fill="#1E293B" />

                {/* Directional Front Arrow Tip */}
                <polygon points="0,-14 6,-6 -6,-6" fill="#38BDF8" />

                {/* Robot Core Light */}
                <circle cx="0" cy="4" r="5" fill="#3B82F6" />
                <circle cx="0" cy="4" r="2.5" fill="#FFFFFF" />
              </g>

              {/* Floating Name Badge */}
              <g transform="translate(0, -32)">
                <rect x="-38" y="-12" width="76" height="18" rx="9" fill="#0F172A" stroke="#38BDF8" strokeWidth="1" />
                <text x="0" y="1" textAnchor="middle" fill="#FFFFFF" fontSize="9" fontWeight="800">
                  ROBOT TTTM
                </text>
              </g>
            </g>
          </svg>
        </div>
      </div>

      {/* Manual Drive Controller & Simulation Toolbar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 18px',
        backgroundColor: '#FFFFFF',
        borderRadius: '12px',
        border: '1px solid #E2E8F0',
        gap: '12px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Compass size={18} color="#3B82F6" />
          <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#1E293B' }}>
            LÁI XE THỬ NGHIỆM TRÊN BẢN ĐỒ:
          </span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>
            (Nhấn để xe di chuyển và xoay góc trong hành lang thực tế)
          </span>
        </div>

        {/* D-Pad Manual Drive Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <button
            onMouseDown={() => handleDrive('forward')}
            style={{
              padding: '6px 12px',
              backgroundColor: drivingManual ? '#3B82F6' : '#F1F5F9',
              color: drivingManual ? '#FFFFFF' : '#1E293B',
              border: '1px solid #CBD5E1',
              borderRadius: '8px',
              fontWeight: 700,
              fontSize: '0.75rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <ArrowUp size={14} /> TIẾN
          </button>
          <button
            onMouseDown={() => handleDrive('left')}
            style={{
              padding: '6px 12px',
              backgroundColor: '#F1F5F9',
              color: '#1E293B',
              border: '1px solid #CBD5E1',
              borderRadius: '8px',
              fontWeight: 700,
              fontSize: '0.75rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <ArrowLeft size={14} /> TRÁI
          </button>
          <button
            onMouseDown={() => handleDrive('right')}
            style={{
              padding: '6px 12px',
              backgroundColor: '#F1F5F9',
              color: '#1E293B',
              border: '1px solid #CBD5E1',
              borderRadius: '8px',
              fontWeight: 700,
              fontSize: '0.75rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            PHẢI <ArrowRight size={14} />
          </button>
          <button
            onMouseDown={() => handleDrive('backward')}
            style={{
              padding: '6px 12px',
              backgroundColor: '#F1F5F9',
              color: '#1E293B',
              border: '1px solid #CBD5E1',
              borderRadius: '8px',
              fontWeight: 700,
              fontSize: '0.75rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <ArrowDown size={14} /> LÙI
          </button>
          <button
            onClick={() => handleDrive('stop')}
            style={{
              padding: '6px 12px',
              backgroundColor: '#FEE2E2',
              color: '#DC2626',
              border: '1px solid #FCA5A5',
              borderRadius: '8px',
              fontWeight: 700,
              fontSize: '0.75rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Square size={13} /> DỪNG
          </button>
        </div>
      </div>

      {/* Selected Destination Card & Call To Action */}
      {currentStore && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#FFFFFF',
          borderRadius: '16px',
          border: '1px solid #E2E8F0',
          padding: '18px 22px',
          boxShadow: '0 4px 16px rgba(0,0,0,0.04)',
          gap: '14px',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div style={{
                fontSize: '2.4rem',
                backgroundColor: currentStore.accentBg,
                width: '60px',
                height: '60px',
                borderRadius: '14px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: `1px solid ${currentStore.borderColor}`
              }}>
                {currentStore.icon}
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: '#0F172A' }}>
                    {currentStore.name}
                  </h3>
                  <span style={{
                    fontSize: '0.72rem',
                    padding: '2px 8px',
                    borderRadius: '99px',
                    backgroundColor: currentStore.accentBg,
                    color: currentStore.color,
                    fontWeight: 700,
                  }}>
                    {currentStore.sub}
                  </span>
                </div>
                <p style={{ margin: '4px 0 0', fontSize: '0.82rem', color: '#64748B' }}>
                  {currentStore.description}
                </p>
              </div>
            </div>

            {/* Big Action Escort Button */}
            <div>
              {activeEscort?.target_poi_id === currentStore.id ? (
                <button
                  onClick={handleCancelEscort}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '12px 24px',
                    backgroundColor: '#FEE2E2',
                    border: '1px solid #FCA5A5',
                    borderRadius: '12px',
                    color: '#DC2626',
                    fontWeight: 800,
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                  }}
                >
                  <XCircle size={18} />
                  <span>HỦY DẪN ĐƯỜNG</span>
                </button>
              ) : (
                <button
                  onClick={() => handleStartEscort(currentStore)}
                  disabled={loadingEscort}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '12px 24px',
                    background: 'linear-gradient(135deg, #1D4ED8, #3B82F6)',
                    border: 'none',
                    borderRadius: '12px',
                    color: '#FFFFFF',
                    fontWeight: 800,
                    fontSize: '0.9rem',
                    boxShadow: '0 4px 14px rgba(59,130,246,0.4)',
                    cursor: loadingEscort ? 'not-allowed' : 'pointer',
                  }}
                >
                  <Navigation size={18} />
                  <span>{loadingEscort ? 'ĐANG LÊN LỘ TRÌNH...' : 'ROBOT DẪN TÔI ĐẾN ĐÂY'}</span>
                </button>
              )}
            </div>
          </div>

          {/* Store Details Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '10px',
            paddingTop: '12px',
            borderTop: '1px solid #F1F5F9'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem', color: '#64748B' }}>
              <Clock size={15} color="#3B82F6" />
              <span><strong>Giờ mở cửa:</strong> 09:00 — 22:00</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem', color: '#64748B' }}>
              <MapPin size={15} color="#3B82F6" />
              <span><strong>Vị trí:</strong> Tầng 1 (Sảnh {currentStore.entranceX < 500 ? 'Tây' : 'Đông'})</span>
            </div>
            {currentStore.promo && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem', color: '#B45309' }}>
                <Sparkles size={15} color="#F59E0B" />
                <span><strong>Khuyến mãi:</strong> {currentStore.promo}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Store Quick Selection List */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
        gap: '10px',
      }}>
        {filteredStores.map(store => {
          const isSelected = selectedStoreId === store.id;
          return (
            <div
              key={store.id}
              onClick={() => setSelectedStoreId(store.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '10px 14px',
                backgroundColor: isSelected ? store.accentBg : '#FFFFFF',
                borderRadius: '12px',
                border: isSelected ? `2px solid ${store.color}` : '1px solid #E2E8F0',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              <span style={{ fontSize: '1.4rem' }}>{store.icon}</span>
              <div style={{ overflow: 'hidden' }}>
                <div style={{ fontWeight: 800, fontSize: '0.85rem', color: '#0F172A', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {store.name}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#64748B' }}>{store.sub}</div>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
};
