import React, { useState, useEffect, useMemo } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import {
  Navigation,
  XCircle,
  Sparkles,
  MapPin,
  Clock,
  CheckCircle2,
  Tag,
  ArrowRight,
  Info,
} from 'lucide-react';

export interface MallStoreMeta {
  id: string;
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
    shortName: 'UNIQLO',
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
    hours: '09:00 — 22:00',
    wing: 'Hành lang Tây (Tầng 1)',
  },
  {
    id: 'poi_kura_sushi',
    shortName: 'KURA SUSHI',
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
    description: 'Sushi băng chuyền công nghệ cao, hải sản tươi ngon nhập khẩu mỗi ngày.',
    promo: 'Tặng 1 đĩa cá hồi cho hóa đơn từ 500k',
    hours: '10:00 — 22:00',
    wing: 'Sảnh Trung Tâm (Tầng 1)',
  },
  {
    id: 'poi_zara',
    shortName: 'ZARA',
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
    hours: '09:00 — 22:00',
    wing: 'Hành lang Đông (Tầng 1)',
  },
  {
    id: 'poi_highlands',
    shortName: 'HIGHLANDS',
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
    promo: 'Mua 2 tặng 1 vào khung giờ 14h — 17h',
    hours: '08:00 — 22:30',
    wing: 'Hành lang Tây (Tầng 1)',
  },
  {
    id: 'poi_cgv',
    shortName: 'CGV CINEMAS',
    name: 'Rạp Phim CGV Cinemas',
    sub: 'Rạp chiếu phim IMAX & 4DX',
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
    hours: '08:30 — 23:30',
    wing: 'Hành lang Đông (Tầng 1)',
  },
  {
    id: 'poi_elevator',
    shortName: 'THANG MÁY',
    name: 'Thang Máy & Bãi Xe',
    sub: 'Lên tầng & Hầm B1',
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
    hours: 'Mở cửa 24/7',
    wing: 'Hành lang Tây (Tầng 1)',
  },
  {
    id: 'poi_reception',
    shortName: 'LỄ TÂN & SẠC',
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
    hours: '08:00 — 22:00',
    wing: 'Sảnh Chính Trung Tâm (Tầng 1)',
  },
  {
    id: 'poi_wc',
    shortName: 'KHU VỆ SINH',
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
    hours: 'Mở cửa 24/7',
    wing: 'Hành lang Đông (Tầng 1)',
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
  const { activeEscort, pairedRobot, telemetry, connectionStatus } = useRobotStore();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedStoreId, setSelectedStoreId] = useState<string>('poi_cgv');
  const [loadingEscort, setLoadingEscort] = useState(false);

  // Selected store details
  const currentStore = useMemo(() => {
    return MALL_STORES.find(s => s.id === selectedStoreId) || MALL_STORES[0];
  }, [selectedStoreId]);

  // Stores filtered by category
  const filteredStores = useMemo(() => {
    if (selectedCategory === 'all') return MALL_STORES;
    return MALL_STORES.filter(s => s.category === selectedCategory);
  }, [selectedCategory]);

  // Coordinate Conversion: Metric (x: 0..100, y: 0..70) -> SVG (1000 x 680)
  const rawOdomX = telemetry?.odometryX;
  const rawOdomY = telemetry?.odometryY;
  const odomHeading = telemetry?.odometryHeading ?? 0;
  const odomHeadingDeg = Math.round((odomHeading * 180) / Math.PI);

  const robotSvgPos = useMemo(() => {
    if (rawOdomX !== undefined && rawOdomX !== null && rawOdomY !== undefined && rawOdomY !== null) {
      const mappedX = Math.max(60, Math.min(940, rawOdomX * 10.0));
      const mappedY = Math.max(50, Math.min(630, rawOdomY * 10.0));
      return { x: mappedX, y: mappedY };
    }
    // Default: Reception desk
    return { x: 500, y: 510 };
  }, [rawOdomX, rawOdomY]);

  // Planned corridor route path (SVG Path D)
  const plannedPathD = useMemo(() => {
    if (!currentStore) return '';
    const start = robotSvgPos;
    const target = { x: currentStore.entranceX, y: currentStore.entranceY };

    const waypoints: { x: number; y: number }[] = [start];

    if (start.y > 420) {
      waypoints.push({ x: 500, y: 440 });
    }
    waypoints.push({ x: 500, y: 340 });

    if (target.y < 300) {
      waypoints.push({ x: 500, y: 230 });
      waypoints.push({ x: target.x, y: 230 });
      waypoints.push(target);
    } else if (target.y > 450) {
      waypoints.push({ x: 500, y: 440 });
      waypoints.push({ x: target.x, y: target.y });
      waypoints.push(target);
    } else {
      waypoints.push({ x: target.x, y: 340 });
      waypoints.push(target);
    }

    return waypoints.reduce((acc, pt, idx) => {
      return idx === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`;
    }, '');
  }, [robotSvgPos, currentStore]);

  // Friendly status determination for mall guests
  const getFriendlyRobotStatus = () => {
    if (connectionStatus !== 'CONNECTED') {
      return {
        dotClass: 'connecting',
        text: 'Robot đang kết nối máy chủ...',
        subtext: 'Sảnh chính Tầng 1',
      };
    }
    if (activeEscort) {
      return {
        dotClass: 'online',
        text: `Robot đang dẫn đường đến: ${activeEscort.target_name}`,
        subtext: `Tiến độ: ${activeEscort.current_progress}%`,
      };
    }
    const rState = telemetry?.robotState;
    if (rState && ['FORWARD', 'BACKWARD', 'TURN_LEFT', 'TURN_RIGHT'].includes(rState)) {
      return {
        dotClass: 'online',
        text: 'Robot đang di chuyển phục vụ khách',
        subtext: 'Đang di chuyển dọc hành lang',
      };
    }
    if (telemetry?.personDetected || rState === 'PERSON_DETECTED' || rState === 'SAFETY_STOP') {
      return {
        dotClass: 'connecting',
        text: 'Robot đang tạm dừng quan sát phía trước',
        subtext: 'Đảm bảo an toàn cho khách đi bộ',
      };
    }
    return {
      dotClass: 'online',
      text: 'Robot sẵn sàng phục vụ quý khách',
      subtext: 'Trực tại Sảnh chính Tầng 1',
    };
  };

  const friendlyStatus = getFriendlyRobotStatus();

  // Escort Handlers
  const handleStartEscort = async (store: MallStoreMeta) => {
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

  const handleCancelEscort = async () => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    try {
      await RobotApi.cancelEscort(host, port);
      updateGlobalState(() => ({ activeEscort: null }));
    } catch (e) {}
  };

  // Poll escort status if active
  useEffect(() => {
    if (!activeEscort || activeEscort.status !== 'NAVIGATING') return;
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);

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
    }, 1000);

    return () => clearInterval(interval);
  }, [activeEscort?.status]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', width: '100%', maxWidth: '100%' }}>
      
      {/* Friendly Guest Status Bar (NO raw engineering coordinates or technical terms) */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '10px 14px',
        backgroundColor: '#FFFFFF',
        borderRadius: '14px',
        border: '1px solid #E2E8F0',
        boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
        gap: '8px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
          <span className={`status-dot ${friendlyStatus.dotClass}`} style={{ flexShrink: 0, width: '9px', height: '9px' }} />
          <div style={{ minWidth: 0 }}>
            <div style={{ fontSize: '0.82rem', fontWeight: 800, color: '#0F172A', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {friendlyStatus.text}
            </div>
            <div style={{ fontSize: '0.72rem', color: '#64748B' }}>
              {friendlyStatus.subtext}
            </div>
          </div>
        </div>

        <span style={{
          fontSize: '0.72rem',
          padding: '3px 10px',
          borderRadius: '99px',
          backgroundColor: '#EFF6FF',
          color: '#1D4ED8',
          fontWeight: 800,
          whiteSpace: 'nowrap',
          flexShrink: 0,
        }}>
          TẦNG 1
        </span>
      </div>

      {/* Escort Active Card (If actively leading customer) */}
      {activeEscort && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
          padding: '14px 16px',
          background: 'linear-gradient(135deg, #1E40AF, #2563EB)',
          borderRadius: '16px',
          color: '#FFFFFF',
          boxShadow: '0 8px 20px rgba(37,99,235,0.25)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.4rem' }}>🤖</span>
              <div>
                <div style={{ fontWeight: 800, fontSize: '0.92rem' }}>
                  ĐANG DẪN ĐƯỜNG ĐẾN: {activeEscort.target_name}
                </div>
                <div style={{ fontSize: '0.72rem', opacity: 0.9 }}>
                  Vui lòng đi theo sau Robot dọc theo hành lang
                </div>
              </div>
            </div>
            <button
              onClick={handleCancelEscort}
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
                fontSize: '0.75rem',
                cursor: 'pointer',
              }}
            >
              <XCircle size={14} />
              <span>HỦY</span>
            </button>
          </div>

          {/* Progress bar */}
          <div style={{ width: '100%', height: '6px', backgroundColor: 'rgba(255,255,255,0.25)', borderRadius: '99px', overflow: 'hidden' }}>
            <div style={{
              width: `${activeEscort.current_progress}%`,
              height: '100%',
              backgroundColor: '#FFFFFF',
              borderRadius: '99px',
              transition: 'width 0.4s ease',
            }} />
          </div>
        </div>
      )}

      {/* Main Architectural Floor Map Card */}
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
              <h2 style={{ margin: 0, fontSize: '0.98rem', fontWeight: 800, color: '#0F172A' }}>
                SƠ ĐỒ TRUNG TÂM THƯƠNG MẠI
              </h2>
              <span style={{ fontSize: '0.72rem', color: '#64748B' }}>
                Chạm gian hàng để xem thông tin và yêu cầu dẫn đường
              </span>
            </div>
            <span style={{ fontSize: '0.72rem', color: '#94A3B8', fontWeight: 600 }}>
              {filteredStores.length} địa điểm
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
                  padding: '5px 11px',
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

        {/* Lightweight, High-Performance Architectural SVG Canvas */}
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

            {/* Walkable Concourse Corridors (High contrast, smooth vector shapes) */}
            {/* North-South Concourse */}
            <rect x="410" y="25" width="180" height="630" fill="#FFFFFF" stroke="#E2E8F0" strokeWidth="1" />
            
            {/* East-West Concourse */}
            <rect x="25" y="270" width="950" height="150" fill="#FFFFFF" stroke="#E2E8F0" strokeWidth="1" />

            {/* Central Atrium Rotunda Medallion */}
            <circle cx="500" cy="345" r="85" fill="#FFFFFF" stroke="#CBD5E1" strokeWidth="2" />
            <circle cx="500" cy="345" r="75" fill="#F8FAFC" stroke="#E2E8F0" strokeWidth="1" strokeDasharray="4 4" />
            <circle cx="500" cy="345" r="42" fill="#EFF6FF" stroke="#BFDBFE" strokeWidth="1.5" />
            <text x="500" y="342" textAnchor="middle" fill="#1E40AF" fontSize="11" fontWeight="800" letterSpacing="0.5">
              SẢNH CHÍNH
            </text>
            <text x="500" y="356" textAnchor="middle" fill="#64748B" fontSize="9" fontWeight="700">
              ROTUNDA
            </text>

            {/* Corridor Navigation Tracks */}
            <path
              d="M 500 110 L 500 580 M 170 345 L 830 345 M 210 230 L 790 230 M 210 530 L 790 530"
              fill="none"
              stroke="#E2E8F0"
              strokeWidth="1.5"
              strokeDasharray="4 4"
            />

            {/* Corridor Directional Labels */}
            <text x="500" y="190" textAnchor="middle" fill="#94A3B8" fontSize="10.5" fontWeight="700" letterSpacing="0.8">
              HÀNH LANG BẮC
            </text>
            <text x="500" y="460" textAnchor="middle" fill="#94A3B8" fontSize="10.5" fontWeight="700" letterSpacing="0.8">
              HÀNH LANG NAM
            </text>
            <text x="210" y="349" textAnchor="middle" fill="#94A3B8" fontSize="10" fontWeight="700">
              HÀNH LANG TÂY
            </text>
            <text x="790" y="349" textAnchor="middle" fill="#94A3B8" fontSize="10" fontWeight="700">
              HÀNH LANG ĐÔNG
            </text>

            {/* Planned Route Line (Robot to Target Entrance) */}
            {plannedPathD && (
              <>
                <path
                  d={plannedPathD}
                  fill="none"
                  stroke="#3B82F6"
                  strokeWidth="7"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity="0.25"
                />
                <path
                  d={plannedPathD}
                  fill="none"
                  stroke="#2563EB"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeDasharray="7 5"
                />
              </>
            )}

            {/* Store Lots */}
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
                    rx="12"
                    fill={isSelected ? store.accentBg : '#FFFFFF'}
                    stroke={isSelected ? '#2563EB' : store.borderColor}
                    strokeWidth={isSelected ? 3 : 1.5}
                  />

                  {/* Top Header Strip */}
                  <rect
                    x={store.lotX}
                    y={store.lotY}
                    width={store.lotW}
                    height="36"
                    rx="12"
                    fill={store.accentBg}
                    opacity="0.85"
                  />

                  {/* Icon Circle */}
                  <circle
                    cx={store.lotX + 24}
                    cy={store.lotY + 18}
                    r="12"
                    fill="#FFFFFF"
                    stroke={isSelected ? '#2563EB' : store.borderColor}
                    strokeWidth="1"
                  />
                  <text
                    x={store.lotX + 24}
                    y={store.lotY + 23}
                    textAnchor="middle"
                    fontSize="13"
                  >
                    {store.icon}
                  </text>

                  {/* Bold Brand Name (Crisp & Readable) */}
                  <text
                    x={store.lotX + 44}
                    y={store.lotY + 23}
                    fill="#0F172A"
                    fontSize="13"
                    fontWeight="800"
                  >
                    {store.shortName}
                  </text>

                  {/* Subtitle / Category */}
                  <text
                    x={store.lotX + 16}
                    y={store.lotY + 62}
                    fill="#475569"
                    fontSize="11"
                    fontWeight="600"
                  >
                    {store.sub}
                  </text>

                  {/* Entrance Door Indicator */}
                  <circle
                    cx={store.entranceX}
                    cy={store.entranceY}
                    r="5"
                    fill={isSelected ? '#2563EB' : '#94A3B8'}
                    stroke="#FFFFFF"
                    strokeWidth="2"
                  />

                  {/* Selection Status Badge */}
                  {isTargetOfEscort ? (
                    <g transform={`translate(${store.lotX + store.lotW - 84}, ${store.lotY + 8})`}>
                      <rect width="76" height="20" rx="10" fill="#2563EB" />
                      <text x="38" y="14" textAnchor="middle" fill="#FFFFFF" fontSize="9.5" fontWeight="800">
                        ĐANG ĐẾN
                      </text>
                    </g>
                  ) : isSelected ? (
                    <g transform={`translate(${store.lotX + store.lotW - 84}, ${store.lotY + 8})`}>
                      <rect width="76" height="20" rx="10" fill="#2563EB" />
                      <text x="38" y="14" textAnchor="middle" fill="#FFFFFF" fontSize="9.5" fontWeight="800">
                        ĐANG CHỌN
                      </text>
                    </g>
                  ) : null}
                </g>
              );
            })}

            {/* Target Destination Pin Marker */}
            {currentStore && (
              <g transform={`translate(${currentStore.entranceX}, ${currentStore.entranceY})`}>
                <circle r="12" fill="#3B82F6" opacity="0.25" />
                <circle r="6" fill="#2563EB" stroke="#FFFFFF" strokeWidth="2" />
              </g>
            )}

            {/* Robot Puck Avatar & Heading Indicator */}
            <g
              transform={`translate(${robotSvgPos.x}, ${robotSvgPos.y})`}
              style={{ transition: 'transform 0.2s linear' }}
            >
              {/* Heading cone / pointer */}
              <g transform={`rotate(${odomHeadingDeg})`}>
                <polygon points="0,-22 7,-14 -7,-14" fill="#2563EB" />
              </g>

              {/* Robot Puck Circle */}
              <circle r="16" fill="#2563EB" stroke="#FFFFFF" strokeWidth="2.5" />
              <text x="0" y="5" textAnchor="middle" fill="#FFFFFF" fontSize="13">
                🤖
              </text>

              {/* Name Badge */}
              <g transform="translate(0, -28)">
                <rect x="-32" y="-10" width="64" height="16" rx="8" fill="#0F172A" />
                <text x="0" y="2" textAnchor="middle" fill="#FFFFFF" fontSize="8.5" fontWeight="800">
                  ROBOT
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
                  padding: '5px 10px',
                  borderRadius: '99px',
                  fontSize: '0.74rem',
                  fontWeight: 700,
                  border: isSelected ? '1.5px solid #2563EB' : '1px solid #E2E8F0',
                  backgroundColor: isSelected ? '#EFF6FF' : '#FFFFFF',
                  color: isSelected ? '#1D4ED8' : '#334155',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  flexShrink: 0,
                }}
              >
                <span>{store.icon}</span>
                <span>{store.shortName}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Store Detail Sheet & Navigation Trigger (Clean, Elegant, Thumb-Friendly) */}
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
              width: '52px',
              height: '52px',
              borderRadius: '14px',
              backgroundColor: currentStore.accentBg,
              border: `1px solid ${currentStore.borderColor}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '2rem',
              flexShrink: 0,
            }}>
              {currentStore.icon}
            </div>

            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                <h3 style={{ margin: 0, fontSize: '1.08rem', fontWeight: 800, color: '#0F172A' }}>
                  {currentStore.name}
                </h3>
                <span style={{
                  fontSize: '0.68rem',
                  padding: '2px 7px',
                  borderRadius: '99px',
                  backgroundColor: currentStore.accentBg,
                  color: currentStore.color,
                  fontWeight: 700,
                }}>
                  {currentStore.sub}
                </span>
              </div>
              <p style={{ margin: '3px 0 0', fontSize: '0.78rem', color: '#64748B', lineHeight: '1.3' }}>
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
            fontSize: '0.74rem',
            color: '#64748B',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <MapPin size={13} color="#2563EB" />
              <span>{currentStore.wing}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={13} color="#2563EB" />
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
              fontSize: '0.76rem',
              color: '#92400E',
              fontWeight: 700,
            }}>
              <Sparkles size={14} color="#D97706" style={{ flexShrink: 0 }} />
              <span>Ưu đãi: {currentStore.promo}</span>
            </div>
          )}

          {/* Primary Action Button (Big & Thumb-Friendly) */}
          <div>
            {activeEscort?.target_poi_id === currentStore.id ? (
              <button
                onClick={handleCancelEscort}
                style={{
                  width: '100%',
                  padding: '13px',
                  backgroundColor: '#FEE2E2',
                  border: '1px solid #FCA5A5',
                  borderRadius: '12px',
                  color: '#DC2626',
                  fontWeight: 800,
                  fontSize: '0.9rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  cursor: 'pointer',
                }}
              >
                <XCircle size={17} />
                <span>HỦY DẪN ĐƯỜNG</span>
              </button>
            ) : (
              <button
                onClick={() => handleStartEscort(currentStore)}
                disabled={loadingEscort}
                style={{
                  width: '100%',
                  padding: '13px',
                  background: 'linear-gradient(135deg, #1D4ED8, #2563EB)',
                  border: 'none',
                  borderRadius: '12px',
                  color: '#FFFFFF',
                  fontWeight: 800,
                  fontSize: '0.92rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 12px rgba(37,99,235,0.3)',
                  cursor: loadingEscort ? 'not-allowed' : 'pointer',
                }}
              >
                <Navigation size={17} />
                <span>{loadingEscort ? 'Đang chuẩn bị lộ trình...' : 'ROBOT DẪN TÔI ĐẾN ĐÂY'}</span>
              </button>
            )}
          </div>
        </div>
      )}

    </div>
  );
};
