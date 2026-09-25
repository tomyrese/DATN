import React, { useState, useEffect } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { PointOfInterest } from '../../types/protocol';
import {
  Navigation,
  Navigation2,
  XCircle,
  Search,
  CheckCircle2,
  Sparkles,
  Bot,
  MapPin,
} from 'lucide-react';

const CATEGORIES = [
  { id: 'all', label: 'Tất Cả' },
  { id: 'food', label: '🍔 Ăn Uống & Cafe' },
  { id: 'fashion', label: '👗 Thời Trang' },
  { id: 'entertainment', label: '🎬 Rạp Phim' },
  { id: 'utility', label: '🚻 Nhà Vệ Sinh & Tiện Ích' },
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

  // Filter out staff-only POIs for customer view
  const customerPois = pois.filter(p => !p.is_staff_only);

  const filteredPois = customerPois.filter(p => {
    const matchCat = selectedCategory === 'all' || p.category === selectedCategory;
    const matchSearch =
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchCat && matchSearch;
  });

  // Select first POI by default if none selected
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
      alert(`Lỗi kết nối: ${e.message}`);
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

  // Live polling for escort status
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

  // Coordinates for the 1-Floor Map SVG Layout (1100 x 660)
  const storeCoords: Record<string, { x: number; y: number; w: number; h: number; fill: string; stroke: string; label: string }> = {
    poi_uniqlo: { x: 80, y: 70, w: 260, h: 140, fill: '#FDF2F8', stroke: '#F472B6', label: 'UNIQLO Fashion' },
    poi_kura_sushi: { x: 420, y: 70, w: 260, h: 140, fill: '#FFFBEB', stroke: '#FBBF24', label: 'Kura Sushi & Lẩu' },
    poi_zara: { x: 760, y: 70, w: 260, h: 140, fill: '#F5F3FF', stroke: '#A78BFA', label: 'ZARA Store' },
    poi_highlands: { x: 80, y: 270, w: 260, h: 140, fill: '#FEF2F2', stroke: '#F87171', label: 'Highlands Coffee' },
    poi_cgv: { x: 760, y: 270, w: 260, h: 140, fill: '#FAF5FF', stroke: '#C084FC', label: 'CGV Cinemas' },
    poi_elevator: { x: 80, y: 470, w: 260, h: 130, fill: '#F0FDF4', stroke: '#4ADE80', label: 'Thang Máy & Cửa Ra' },
    poi_reception: { x: 420, y: 470, w: 260, h: 130, fill: '#EFF6FF', stroke: '#60A5FA', label: 'Lễ Tân & Robot Dock' },
    poi_wc: { x: 760, y: 470, w: 260, h: 130, fill: '#F0FDFA', stroke: '#2DD4BF', label: 'Khu Vệ Sinh (WC)' },
  };

  // Calculate live robot marker position along corridor
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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      
      {/* Active Escort Banner */}
      {activeEscort && (
        <div className="active-escort-card">
          <div className="escort-left">
            <div className="escort-robot-icon">🤖</div>
            <div className="escort-info">
              <h3>ROBOT ĐANG DẪN ĐƯỜNG ĐẾN: {activeEscort.target_name}</h3>
              <p>
                Quý khách vui lòng đi theo sau robot • Tiến độ: {activeEscort.current_progress}% • Tốc độ: {telemetry?.speed?.toFixed(2) || '0.35'} m/s
              </p>
            </div>
          </div>
          <button className="btn-cancel-escort-clean" onClick={handleCancelEscort}>
            <XCircle size={18} />
            <span>HỦY DẪN ĐƯỜNG</span>
          </button>
        </div>
      )}

      {/* Main 2-Column Map Layout */}
      <div className="map-view-layout">
        
        {/* Left Side: Interactive 1-Floor Map */}
        <div className="map-card-wrapper">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 800 }}>SƠ ĐỒ TẦNG 1 (TRUNG TÂM THƯƠNG MẠI)</h2>
              <p style={{ fontSize: '0.85rem', color: '#64748B' }}>Chạm vào bất kỳ cửa hàng nào trên bản đồ để xem và yêu cầu Robot dẫn đường</p>
            </div>
            {selectedPoi && (
              <button
                className="btn-solid-blue"
                onClick={() => handleStartEscort(selectedPoi)}
                disabled={loadingEscort || activeEscort?.target_poi_id === selectedPoi.id}
                style={{ padding: '10px 18px', fontSize: '0.9rem' }}
              >
                <Navigation size={16} />
                <span>{activeEscort?.target_poi_id === selectedPoi.id ? 'Đang Dẫn Đường' : `Dẫn Tôi Đến ${selectedPoi.name}`}</span>
              </button>
            )}
          </div>

          <div className="map-svg-container">
            <svg viewBox="0 0 1100 660" preserveAspectRatio="xMidYMid meet">
              <defs>
                <pattern id="mall-tile" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#F1F5F9" strokeWidth="1" />
                </pattern>
              </defs>

              {/* Floor Background */}
              <rect width="1100" height="660" fill="#FFFFFF" />
              <rect width="1100" height="660" fill="url(#mall-tile)" />

              {/* Main Corridors (Hành Lang Đi Bộ) */}
              <rect x="360" y="40" width="380" height="580" fill="#F8FAFC" rx="16" stroke="#E2E8F0" strokeWidth="1.5" />
              <rect x="40" y="230" width="1020" height="220" fill="#F8FAFC" rx="16" stroke="#E2E8F0" strokeWidth="1.5" />

              {/* Corridor Labels */}
              <text x="550" y="255" textAnchor="middle" fill="#94A3B8" fontSize="13" fontWeight="700" letterSpacing="1">
                HÀNH LANG TRUNG TÂM (MAIN CONCOURSE)
              </text>

              {/* Navigation Route Path (if a target is selected) */}
              {currentTargetId && storeCoords[currentTargetId] && (
                <g>
                  <path
                    d={`M 550 430 Q 550 ${storeCoords[currentTargetId].y + storeCoords[currentTargetId].h / 2} ${storeCoords[currentTargetId].x + storeCoords[currentTargetId].w / 2} ${storeCoords[currentTargetId].y + storeCoords[currentTargetId].h / 2}`}
                    fill="none"
                    stroke="#2563EB"
                    strokeWidth="4"
                    strokeDasharray="8 6"
                  />
                </g>
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
                      rx="16"
                      fill={isTarget ? '#EFF6FF' : box.fill}
                      stroke={isTarget ? '#2563EB' : (isSelected ? '#2563EB' : box.stroke)}
                      strokeWidth={isSelected || isTarget ? '3' : '1.5'}
                      filter={isSelected || isTarget ? 'drop-shadow(0 4px 12px rgba(37,99,235,0.25))' : 'none'}
                    />
                    {/* Store Emoji */}
                    <text x={box.x + 24} y={box.y + 40} fontSize="26">
                      {STORE_EMOJIS[poiId] || '🏪'}
                    </text>
                    {/* Store Name */}
                    <text
                      x={box.x + 60}
                      y={box.y + 38}
                      fontSize="16"
                      fontWeight="800"
                      fill="#0F172A"
                    >
                      {box.label.split(' ')[0]}
                    </text>
                    {/* Sub description */}
                    <text
                      x={box.x + 24}
                      y={box.y + 70}
                      fontSize="12"
                      fontWeight="500"
                      fill="#64748B"
                    >
                      {matchingPoi?.description?.substring(0, 26) || box.label}
                    </text>

                    {/* Touch to Select Button Inside Box */}
                    <rect
                      x={box.x + 24}
                      y={box.y + 90}
                      width={box.w - 48}
                      height="30"
                      rx="8"
                      fill={isSelected ? '#2563EB' : '#FFFFFF'}
                      stroke={isSelected ? '#2563EB' : '#E2E8F0'}
                    />
                    <text
                      x={box.x + box.w / 2}
                      y={box.y + 110}
                      textAnchor="middle"
                      fontSize="12"
                      fontWeight="700"
                      fill={isSelected ? '#FFFFFF' : '#2563EB'}
                    >
                      {isTarget ? 'Đang Dẫn Tới Đây 📍' : (isSelected ? 'Đã Chọn • Dẫn Đường 👉' : 'Chạm để Chọn')}
                    </text>
                  </g>
                );
              })}

              {/* Robot Live Marker */}
              <g transform={`translate(${liveRobotPos.x}, ${liveRobotPos.y})`}>
                <circle r="22" fill="#2563EB" opacity="0.25">
                  <animate attributeName="r" values="22;30;22" dur="2s" repeatCount="indefinite" />
                  <animate attributeName="opacity" values="0.25;0;0.25" dur="2s" repeatCount="indefinite" />
                </circle>
                <circle r="18" fill="#2563EB" stroke="#FFFFFF" strokeWidth="3" filter="drop-shadow(0 4px 8px rgba(0,0,0,0.2))" />
                <text x="0" y="6" textAnchor="middle" fontSize="14">🤖</text>
                <rect x="-35" y="-36" width="70" height="20" rx="6" fill="#0F172A" />
                <text x="0" y="-22" textAnchor="middle" fill="#FFFFFF" fontSize="10" fontWeight="700">ROBOT AI</text>
              </g>
            </svg>
          </div>
        </div>

        {/* Right Side: Quick Shop Directory & Escort Triggers */}
        <div className="shop-sidebar">
          
          {/* Quick Search */}
          <div className="quick-search-box">
            <Search size={18} />
            <input
              type="text"
              className="quick-search-input"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm quán cafe, rạp phim, WC..."
            />
          </div>

          {/* Category Filter Pills */}
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

          {/* Selected POI Spotlight Card */}
          {selectedPoi && (
            <div className="card-clean" style={{ padding: '18px', border: '1.5px solid #2563EB' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                <span style={{ fontSize: '24px' }}>{STORE_EMOJIS[selectedPoi.id] || '📍'}</span>
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 800 }}>{selectedPoi.name}</h3>
                  <span style={{ fontSize: '0.78rem', color: '#2563EB', fontWeight: 700 }}>Tầng 1 • Khu Mua Sắm</span>
                </div>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#64748B', marginBottom: '14px' }}>
                {selectedPoi.description}
              </p>
              <button
                className="btn-solid-blue"
                style={{ width: '100%' }}
                onClick={() => handleStartEscort(selectedPoi)}
                disabled={loadingEscort || activeEscort?.target_poi_id === selectedPoi.id}
              >
                <Navigation size={16} />
                <span>{activeEscort?.target_poi_id === selectedPoi.id ? 'ROBOT ĐANG DẪN ĐƯỜNG' : 'DẪN TÔI ĐẾN ĐÂY'}</span>
              </button>
            </div>
          )}

          {/* POI List */}
          <div className="poi-cards-list">
            {filteredPois.map(poi => {
              const isSelected = selectedPoi?.id === poi.id;
              return (
                <div
                  key={poi.id}
                  className={`poi-list-item ${isSelected ? 'selected' : ''}`}
                  onClick={() => setSelectedPoi(poi)}
                >
                  <div className="poi-item-left">
                    <div className="poi-item-emoji">{STORE_EMOJIS[poi.id] || '🏬'}</div>
                    <div className="poi-item-text">
                      <h4>{poi.name}</h4>
                      <p>{poi.description.substring(0, 32)}...</p>
                    </div>
                  </div>
                  <Navigation size={16} color={isSelected ? '#2563EB' : '#94A3B8'} />
                </div>
              );
            })}
          </div>

        </div>

      </div>
    </div>
  );
};
