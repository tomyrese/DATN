import React, { useState, useEffect } from 'react';
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
} from 'lucide-react';

const CATEGORIES = [
  { id: 'all', label: 'Tất Cả' },
  { id: 'food', label: '🍔 Ăn Uống' },
  { id: 'fashion', label: '👗 Thời Trang' },
  { id: 'entertainment', label: '🎬 Rạp Phim' },
  { id: 'utility', label: '🚻 Tiện Ích' },
];

const STORE_EMOJIS: Record<string, string> = {
  poi_uniqlo: '👕',
  poi_kura_sushi: '🍣',
  poi_zara: '👗',
  poi_highlands: '☕',
  poi_cgv: '🎬',
  poi_elevator: '🛗',
  poi_reception: '💁',
  poi_wc: '🚻',
};

export const MallMapTab: React.FC = () => {
  const { pois, activeEscort, pairedRobot, telemetry } = useRobotStore();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedPoi, setSelectedPoi] = useState<PointOfInterest | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loadingEscort, setLoadingEscort] = useState(false);

  const customerPois = pois.filter(p => !p.is_staff_only);

  const filteredPois = customerPois.filter(p => {
    const matchCat = selectedCategory === 'all' || p.category === selectedCategory;
    const matchSearch =
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchCat && matchSearch;
  });

  useEffect(() => {
    if (!selectedPoi && customerPois.length > 0) {
      setSelectedPoi(customerPois[0]);
    }
  }, [customerPois, selectedPoi]);

  const handleStartEscort = async (poi: PointOfInterest) => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    setLoadingEscort(true);
    try {
      const res = await RobotApi.requestEscort(host, port, poi.id);
      if (res.success && res.task) {
        updateGlobalState(() => ({ activeEscort: res.task }));
      } else {
        alert(res.message || 'Không thể khởi động dẫn đường lúc này.');
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

  const storeCoords: Record<string, { x: number; y: number; w: number; h: number; fill: string; stroke: string; label: string; sub: string }> = {
    poi_uniqlo: { x: 70, y: 55, w: 280, h: 145, fill: '#FDF2F8', stroke: '#F472B6', label: 'UNIQLO', sub: 'Thời trang Nhật' },
    poi_kura_sushi: { x: 410, y: 55, w: 280, h: 145, fill: '#FFFBEB', stroke: '#FBBF24', label: 'Kura Sushi', sub: 'Ẩm thực Nhật Bản' },
    poi_zara: { x: 750, y: 55, w: 280, h: 145, fill: '#F5F3FF', stroke: '#A78BFA', label: 'ZARA', sub: 'Thời trang Quốc tế' },
    poi_highlands: { x: 70, y: 255, w: 280, h: 145, fill: '#FEF2F2', stroke: '#F87171', label: 'Highlands Coffee', sub: 'Cà phê & Bánh' },
    poi_cgv: { x: 750, y: 255, w: 280, h: 145, fill: '#FAF5FF', stroke: '#C084FC', label: 'CGV Cinemas', sub: 'Rạp chiếu phim' },
    poi_elevator: { x: 70, y: 455, w: 280, h: 140, fill: '#F0FDF4', stroke: '#4ADE80', label: 'Thang Máy', sub: 'Lên xuống tầng' },
    poi_reception: { x: 410, y: 455, w: 280, h: 140, fill: '#EFF6FF', stroke: '#60A5FA', label: 'Lễ Tân & Trạm Sạc', sub: 'Điểm đỗ Robot' },
    poi_wc: { x: 750, y: 455, w: 280, h: 140, fill: '#F0FDFA', stroke: '#2DD4BF', label: 'Nhà Vệ Sinh (WC)', sub: 'Tiện ích chung' },
  };

  const activeCoord = activeEscort ? storeCoords[activeEscort.target_poi_id] : null;
  const progressRatio = (activeEscort?.current_progress || 0) / 100.0;
  const robotCenter = { x: 550, y: 430 };

  const liveRobotPos = activeCoord
    ? {
        x: robotCenter.x + (activeCoord.x + activeCoord.w / 2 - robotCenter.x) * progressRatio,
        y: robotCenter.y + (activeCoord.y + activeCoord.h / 2 - robotCenter.y) * progressRatio,
      }
    : robotCenter;

  const currentTargetId = activeEscort?.target_poi_id || selectedPoi?.id;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', width: '100%', maxWidth: '100%' }}>
      
      {/* Category Pills Header */}
      <div className="category-pill-row">
        {CATEGORIES.map(cat => (
          <button
            key={cat.id}
            className={`category-pill ${selectedCategory === cat.id ? 'active' : ''}`}
            onClick={() => setSelectedCategory(cat.id)}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Active Escort Banner */}
      {activeEscort && (
        <div className="active-escort-card">
          <div className="escort-left" style={{ flex: 1 }}>
            <div className="escort-robot-icon">🤖</div>
            <div className="escort-info" style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontSize: '0.95rem' }}>DẪN ĐƯỜNG: {activeEscort.target_name}</h3>
                <span style={{ fontSize: '0.8rem', fontWeight: 800 }}>{activeEscort.current_progress}%</span>
              </div>
              {/* Progress Bar */}
              <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.3)', borderRadius: '99px', margin: '6px 0 4px', overflow: 'hidden' }}>
                <div style={{ width: `${activeEscort.current_progress}%`, height: '100%', background: '#FFFFFF', borderRadius: '99px', transition: 'width 0.3s ease' }} />
              </div>
              <p style={{ fontSize: '0.75rem', opacity: 0.9 }}>Quý khách vui lòng đi theo sau Robot</p>
            </div>
          </div>
          <button className="btn-cancel-escort-clean" onClick={handleCancelEscort} style={{ alignSelf: 'center', marginLeft: '10px' }}>
            <XCircle size={15} />
            <span>HỦY</span>
          </button>
        </div>
      )}

      {/* Interactive SVG Map Card */}
      <div className="map-card-wrapper" style={{ padding: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '1rem', fontWeight: 800 }}>SƠ ĐỒ TRUNG TÂM TẦNG 1</h2>
            <p style={{ fontSize: '0.75rem', color: '#64748B' }}>Chạm vào cửa hàng trên bản đồ để chọn điểm đến</p>
          </div>
        </div>

        <div className="map-svg-container">
          <svg viewBox="0 0 1100 660" preserveAspectRatio="xMidYMid meet" style={{ width: '100%', height: '100%', display: 'block' }}>
            <defs>
              <pattern id="mall-tile" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#F1F5F9" strokeWidth="1" />
              </pattern>
            </defs>

            <rect width="1100" height="660" fill="#FFFFFF" />
            <rect width="1100" height="660" fill="url(#mall-tile)" />

            {/* Main Corridors */}
            <rect x="360" y="25" width="380" height="610" fill="#F8FAFC" rx="16" stroke="#E2E8F0" strokeWidth="1.5" />
            <rect x="25" y="215" width="1050" height="235" fill="#F8FAFC" rx="16" stroke="#E2E8F0" strokeWidth="1.5" />

            <text x="550" y="240" textAnchor="middle" fill="#94A3B8" fontSize="13" fontWeight="800" letterSpacing="1">
              HÀNH LANG TRUNG TÂM
            </text>

            {/* Route Path */}
            {currentTargetId && storeCoords[currentTargetId] && (
              <path
                d={`M 550 430 Q 550 ${storeCoords[currentTargetId].y + storeCoords[currentTargetId].h / 2} ${storeCoords[currentTargetId].x + storeCoords[currentTargetId].w / 2} ${storeCoords[currentTargetId].y + storeCoords[currentTargetId].h / 2}`}
                fill="none"
                stroke="#2563EB"
                strokeWidth="6"
                strokeDasharray="12 6"
              />
            )}

            {/* Store Blocks */}
            {Object.entries(storeCoords).map(([poiId, box]) => {
              const isSelected = selectedPoi?.id === poiId;
              const isTarget = activeEscort?.target_poi_id === poiId;
              const matchingPoi = pois.find(p => p.id === poiId);

              return (
                <g
                  key={poiId}
                  onClick={() => matchingPoi && setSelectedPoi(matchingPoi)}
                  style={{ cursor: 'pointer' }}
                >
                  <rect
                    x={box.x}
                    y={box.y}
                    width={box.w}
                    height={box.h}
                    rx="18"
                    fill={isTarget ? '#EFF6FF' : box.fill}
                    stroke={isTarget ? '#2563EB' : (isSelected ? '#2563EB' : box.stroke)}
                    strokeWidth={isSelected || isTarget ? '3.5' : '1.5'}
                  />
                  {/* Emoji */}
                  <text x={box.x + 22} y={box.y + 48} fontSize="30">
                    {STORE_EMOJIS[poiId] || '🏪'}
                  </text>
                  {/* Store Name */}
                  <text
                    x={box.x + 68}
                    y={box.y + 42}
                    fontSize="18"
                    fontWeight="900"
                    fill="#0F172A"
                  >
                    {box.label}
                  </text>
                  {/* Store Sub */}
                  <text
                    x={box.x + 22}
                    y={box.y + 80}
                    fontSize="13"
                    fontWeight="500"
                    fill="#64748B"
                  >
                    {box.sub}
                  </text>

                  {/* Clean Selection Status Tag inside box */}
                  <rect
                    x={box.x + 22}
                    y={box.y + 98}
                    width={box.w - 44}
                    height="32"
                    rx="10"
                    fill={isSelected ? '#2563EB' : '#FFFFFF'}
                    stroke={isSelected ? '#2563EB' : '#CBD5E1'}
                  />
                  <text
                    x={box.x + box.w / 2}
                    y={box.y + 119}
                    textAnchor="middle"
                    fontSize="13"
                    fontWeight="800"
                    fill={isSelected ? '#FFFFFF' : '#475569'}
                  >
                    {isTarget ? 'Đang Dẫn Đường 📍' : (isSelected ? '✓ Đang Chọn' : 'Chạm Để Chọn')}
                  </text>
                </g>
              );
            })}

            {/* Robot Marker */}
            <g transform={`translate(${liveRobotPos.x}, ${liveRobotPos.y})`}>
              <circle r="24" fill="#2563EB" opacity="0.3" />
              <circle r="18" fill="#2563EB" stroke="#FFFFFF" strokeWidth="3" />
              <text x="0" y="6" textAnchor="middle" fontSize="14">🤖</text>
              <rect x="-32" y="-34" width="64" height="18" rx="6" fill="#0F172A" />
              <text x="0" y="-21" textAnchor="middle" fill="#FFFFFF" fontSize="9" fontWeight="800">ROBOT</text>
            </g>
          </svg>
        </div>
      </div>

      {/* Destination Spotlight & 1-Touch Action Card */}
      {selectedPoi && (
        <div className="card-clean" style={{ padding: '16px', border: '1.5px solid #2563EB', background: '#FFFFFF' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '26px' }}>{STORE_EMOJIS[selectedPoi.id] || '📍'}</span>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 900, color: '#0F172A' }}>{selectedPoi.name}</h3>
                <span style={{ fontSize: '0.75rem', color: '#2563EB', fontWeight: 700 }}>Tầng 1 • Trung Tâm Thương Mại</span>
              </div>
            </div>
            <span className="brand-badge" style={{ background: '#EFF6FF', color: '#2563EB', fontSize: '0.72rem' }}>
              ~15 Giây
            </span>
          </div>

          <p style={{ fontSize: '0.82rem', color: '#64748B', marginBottom: '12px', lineHeight: '1.4' }}>
            {selectedPoi.description}
          </p>

          <button
            className="btn-solid-blue"
            style={{ width: '100%', padding: '12px', fontSize: '0.95rem' }}
            onClick={() => handleStartEscort(selectedPoi)}
            disabled={loadingEscort || activeEscort?.target_poi_id === selectedPoi.id}
          >
            <Navigation size={18} />
            <span>
              {activeEscort?.target_poi_id === selectedPoi.id
                ? 'ROBOT ĐANG DẪN ĐƯỜNG ĐẾN ĐÂY'
                : `DẪN TÔI ĐẾN ${selectedPoi.name.toUpperCase()}`}
            </span>
          </button>
        </div>
      )}

      {/* Store Directory Quick List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div className="quick-search-box">
          <Search size={16} />
          <input
            type="text"
            className="quick-search-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Tìm kiếm gian hàng, đồ ăn, rạp phim..."
          />
        </div>

        <div className="poi-cards-list">
          {filteredPois.map(poi => {
            const isSelected = selectedPoi?.id === poi.id;
            return (
              <div
                key={poi.id}
                className={`poi-list-item ${isSelected ? 'selected' : ''}`}
                onClick={() => {
                  setSelectedPoi(poi);
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
                style={{ padding: '12px 14px' }}
              >
                <div className="poi-item-left">
                  <div className="poi-item-emoji" style={{ width: '36px', height: '36px', fontSize: '20px' }}>
                    {STORE_EMOJIS[poi.id] || '🏬'}
                  </div>
                  <div className="poi-item-text">
                    <h4 style={{ fontSize: '0.92rem' }}>{poi.name}</h4>
                    <p style={{ fontSize: '0.78rem' }}>{poi.description.substring(0, 32)}...</p>
                  </div>
                </div>
                <Navigation size={15} color={isSelected ? '#2563EB' : '#94A3B8'} />
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
};
