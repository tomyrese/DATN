import React, { useState } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { PointOfInterest } from '../../types/protocol';
import { MapPin, Navigation, Navigation2, CheckCircle2, XCircle, Coffee, ShoppingBag, Film, Info, Layers } from 'lucide-react';

export const MallMapTab: React.FC = () => {
  const { pois, activeEscort, pairedRobot, telemetry } = useRobotStore();
  const [selectedFloor, setSelectedFloor] = useState<'T1' | 'T2' | 'T3'>('T1');
  const [selectedPoi, setSelectedPoi] = useState<PointOfInterest | null>(null);
  const [loadingEscort, setLoadingEscort] = useState(false);

  // Filter POIs for current floor (excluding staff only)
  const floorPois = pois.filter(p => p.floor === selectedFloor && !p.is_staff_only);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'food':
        return <Coffee size={16} color="#F59E0B" />;
      case 'fashion':
        return <ShoppingBag size={16} color="#EC4899" />;
      case 'entertainment':
        return <Film size={16} color="#8B5CF6" />;
      default:
        return <Info size={16} color="#00E5FF" />;
    }
  };

  const handleStartEscort = async (poi: PointOfInterest) => {
    if (!pairedRobot) {
      alert('Vui lòng cấu hình kết nối đến Robot để bắt đầu dẫn đường.');
      return;
    }
    setLoadingEscort(true);
    try {
      const res = await RobotApi.requestEscort(pairedRobot.host, pairedRobot.port, poi.id);
      if (res.success && res.task) {
        updateGlobalState(() => ({ activeEscort: res.task }));
      } else {
        alert(res.message || 'Không thể khởi động chế độ dẫn đường lúc này.');
      }
    } catch (e: any) {
      alert(`Lỗi kết nối: ${e.message}`);
    } finally {
      setLoadingEscort(false);
    }
  };

  const handleCancelEscort = async () => {
    if (!pairedRobot) return;
    try {
      await RobotApi.cancelEscort(pairedRobot.host, pairedRobot.port);
      updateGlobalState(() => ({ activeEscort: null }));
    } catch (e) {}
  };

  // Simulated robot position based on floor
  const robotPos = { x: 50, y: 82 };

  return (
    <div className="tab-pane active">
      <div className="mall-map-container">
        
        {/* Active Escort HUD Banner */}
        {activeEscort && (
          <div className="escort-banner">
            <div className="escort-banner-content">
              <div className="escort-spinner">
                <Navigation2 size={24} className="spin-pulse" />
              </div>
              <div>
                <div className="escort-title">ROBOT ĐANG DẪN ĐƯỜNG ĐẾN: {activeEscort.target_name} ({activeEscort.target_floor})</div>
                <div className="escort-sub">
                  Vui lòng đi theo robot • Tốc độ an toàn: {telemetry?.speed?.toFixed(2) || '0.35'} m/s • Khoảng cách ước tính: {activeEscort.estimated_seconds}s
                </div>
              </div>
            </div>
            <button className="btn-cancel-escort" onClick={handleCancelEscort}>
              <XCircle size={16} style={{ display: 'inline', marginRight: 4 }} />
              HỦY DẪN ĐƯỜNG
            </button>
          </div>
        )}

        {/* Map Header & Floor Switcher */}
        <div className="map-toolbar">
          <div className="floor-selector">
            <Layers size={18} color="#00E5FF" />
            <span className="toolbar-label">CHỌN TẦNG:</span>
            {(['T1', 'T2', 'T3'] as const).map(f => (
              <button
                key={f}
                className={`floor-btn ${selectedFloor === f ? 'active' : ''}`}
                onClick={() => { setSelectedFloor(f); setSelectedPoi(null); }}
              >
                {f === 'T1' ? 'Tầng 1 (Sảnh Chính)' : f === 'T2' ? 'Tầng 2 (Ẩm Thực)' : 'Tầng 3 (Giải Trí)'}
              </button>
            ))}
          </div>
        </div>

        {/* Interactive SVG Floorplan Viewport */}
        <div className="map-viewport-card">
          <div className="floorplan-wrapper">
            <svg viewBox="0 0 1000 600" className="floorplan-svg">
              {/* Mall Layout Grid Background */}
              <defs>
                <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255, 255, 255, 0.04)" strokeWidth="1" />
                </pattern>
                <linearGradient id="hallwayGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#0B132B" />
                  <stop offset="100%" stopColor="#1C2541" />
                </linearGradient>
              </defs>

              <rect width="1000" height="600" fill="url(#grid)" />

              {/* Main Hallway Corridor */}
              <rect x="100" y="80" width="800" height="440" rx="20" fill="url(#hallwayGrad)" stroke="#1F293D" strokeWidth="2" />
              
              {/* Central Atrium */}
              <circle cx="500" cy="300" r="110" fill="#0A0E17" stroke="#00E5FF" strokeWidth="1.5" strokeDasharray="6 4" opacity="0.6" />
              <text x="500" y="305" fill="#64748B" fontSize="13" textAnchor="middle" fontFamily="sans-serif">
                GIẾNG TRỜI TRUNG TÂM ({selectedFloor})
              </text>

              {/* Store Zones (Decorative) */}
              <rect x="140" y="120" width="220" height="130" rx="10" fill="#141E33" stroke="rgba(0, 229, 255, 0.2)" />
              <rect x="640" y="120" width="220" height="130" rx="10" fill="#141E33" stroke="rgba(0, 229, 255, 0.2)" />
              <rect x="140" y="350" width="220" height="130" rx="10" fill="#141E33" stroke="rgba(0, 229, 255, 0.2)" />
              <rect x="640" y="350" width="220" height="130" rx="10" fill="#141E33" stroke="rgba(0, 229, 255, 0.2)" />

              {/* Navigation Route Path if active escort */}
              {activeEscort && selectedPoi && (
                <path
                  d={`M 500 492 Q 500 300 ${selectedPoi.x * 10} ${selectedPoi.y * 6}`}
                  fill="none"
                  stroke="#00E5FF"
                  strokeWidth="3"
                  strokeDasharray="8 6"
                  className="route-animated"
                />
              )}

              {/* Robot Current Marker */}
              {selectedFloor === 'T1' && (
                <g transform={`translate(${robotPos.x * 10}, ${robotPos.y * 6})`}>
                  <circle cx="0" cy="0" r="18" fill="rgba(0, 230, 118, 0.2)" className="pulse-dot" />
                  <circle cx="0" cy="0" r="10" fill="#00E676" stroke="#080B11" strokeWidth="2" />
                  <text x="0" y="24" fill="#00E676" fontSize="11" fontWeight="bold" textAnchor="middle">
                    ROBOT
                  </text>
                </g>
              )}

              {/* POI Markers */}
              {floorPois.map(poi => {
                const isSelected = selectedPoi?.id === poi.id;
                const isTarget = activeEscort?.target_poi_id === poi.id;
                const posX = poi.x * 10;
                const posY = poi.y * 6;

                return (
                  <g
                    key={poi.id}
                    transform={`translate(${posX}, ${posY})`}
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPoi(poi)}
                  >
                    <circle
                      cx="0"
                      cy="0"
                      r={isSelected || isTarget ? '16' : '12'}
                      fill={isTarget ? '#00E5FF' : isSelected ? '#3B82F6' : '#1E293B'}
                      stroke={isTarget ? '#FFFFFF' : '#00E5FF'}
                      strokeWidth="2"
                    />
                    <text
                      x="0"
                      y="-18"
                      fill={isSelected || isTarget ? '#00E5FF' : '#E2E8F0'}
                      fontSize="11"
                      fontWeight="600"
                      textAnchor="middle"
                    >
                      {poi.name}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* POI Detail Slide-in Card */}
          {selectedPoi && (
            <div className="poi-detail-card">
              <div className="poi-card-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  {getCategoryIcon(selectedPoi.category)}
                  <div>
                    <h3 className="poi-title">{selectedPoi.name}</h3>
                    <span className="poi-floor-badge">Vị trí: {selectedPoi.floor}</span>
                  </div>
                </div>
                <button className="btn-close-sm" onClick={() => setSelectedPoi(null)}>✕</button>
              </div>

              <p className="poi-desc">{selectedPoi.description}</p>

              <div className="poi-actions">
                <button
                  className="btn-primary btn-block"
                  disabled={loadingEscort || (activeEscort?.target_poi_id === selectedPoi.id)}
                  onClick={() => handleStartEscort(selectedPoi)}
                >
                  <Navigation size={16} style={{ display: 'inline', marginRight: 6 }} />
                  {activeEscort?.target_poi_id === selectedPoi.id
                    ? 'ĐANG DẪN ĐƯỜNG TỚI ĐÂY'
                    : 'ROBOT DẪN TÔI ĐẾN ĐÂY'}
                </button>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
