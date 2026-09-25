import React, { useState } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { PointOfInterest } from '../../types/protocol';
import {
  Navigation,
  Navigation2,
  XCircle,
  Coffee,
  ShoppingBag,
  Film,
  Sparkles,
  MapPin,
  Clock,
  Compass,
  Search,
  CheckCircle2,
} from 'lucide-react';

export const MallMapTab: React.FC = () => {
  const { pois, activeEscort, pairedRobot, telemetry } = useRobotStore();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedPoi, setSelectedPoi] = useState<PointOfInterest | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loadingEscort, setLoadingEscort] = useState(false);

  // Customer POIs on single floor
  const customerPois = pois.filter(p => !p.is_staff_only);

  const filteredPois = customerPois.filter(p => {
    const matchCat = selectedCategory === 'all' || p.category === selectedCategory;
    const matchSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) || p.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchCat && matchSearch;
  });

  const handleStartEscort = async (poi: PointOfInterest) => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    setLoadingEscort(true);
    try {
      const res = await RobotApi.requestEscort(host, port, poi.id);
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
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    try {
      await RobotApi.cancelEscort(host, port);
      updateGlobalState(() => ({ activeEscort: null }));
    } catch (e) {}
  };

  // Escort live polling effect
  React.useEffect(() => {
    if (!activeEscort || activeEscort.status !== 'NAVIGATING') return;

    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);

    const interval = setInterval(async () => {
      try {
        const task = await RobotApi.getEscortStatus(host, port);
        if (task) {
          updateGlobalState(() => ({ activeEscort: task }));
          if (task.status === 'ARRIVED') {
            alert(`🎉 Robot đã dẫn quý khách đến đúng vị trí: ${task.target_name}!`);
            setTimeout(() => {
              updateGlobalState(() => ({ activeEscort: null }));
            }, 3000);
          }
        }
      } catch (err) {}
    }, 1000);

    return () => clearInterval(interval);
  }, [activeEscort?.status]);

  // Store coordinates mapping for SVG Route calculation
  const storeCoordinates: Record<string, { x: number; y: number }> = {
    poi_uniqlo: { x: 200, y: 130 },
    poi_kura_sushi: { x: 550, y: 130 },
    poi_zara: { x: 900, y: 130 },
    poi_highlands: { x: 200, y: 340 },
    poi_cgv: { x: 900, y: 340 },
    poi_elevator: { x: 200, y: 540 },
    poi_reception: { x: 550, y: 540 },
    poi_wc: { x: 900, y: 540 },
  };

  // Dynamically calculate robot position based on escort progress
  const targetCoord = activeEscort ? storeCoordinates[activeEscort.target_poi_id] : null;
  const progressRatio = (activeEscort?.current_progress || 0) / 100.0;
  const currentRobotPos = targetCoord
    ? {
        x: 550 + (targetCoord.x - 550) * progressRatio,
        y: 430 + (targetCoord.y - 430) * progressRatio,
      }
    : { x: 550, y: 430 };

  const getRoutePath = (targetPoiId: string) => {
    const target = storeCoordinates[targetPoiId];
    if (!target) return `M 550 430 L 550 340`;
    // Corridor waypoint routing
    if (target.y < 200) {
      return `M 550 430 L 550 220 L ${target.x} 220 L ${target.x} ${target.y + 70}`;
    } else if (target.y > 500) {
      return `M 550 430 L 550 450 L ${target.x} 450 L ${target.x} ${target.y - 60}`;
    } else {
      return `M 550 430 L 550 340 L ${target.x} 340`;
    }
  };

  return (
    <div className="tab-pane active">
      <div className="mall-map-container">
        
        {/* Active Escort Status Banner */}
        {activeEscort && (
          <div className="escort-banner">
            <div className="escort-banner-content">
              <div className="escort-spinner">
                <Navigation2 size={24} className="spin-pulse" />
              </div>
              <div>
                <div className="escort-title">
                  ROBOT ĐANG DẪN ĐƯỜNG ĐẾN: {activeEscort.target_name}
                </div>
                <div className="escort-sub">
                  Vui lòng đi theo sau Robot • Tốc độ an toàn: {telemetry?.speed?.toFixed(2) || '0.35'} m/s • Thời gian dự kiến: ~{activeEscort.estimated_seconds}s
                </div>
              </div>
            </div>
            <button className="btn-cancel-escort" onClick={handleCancelEscort}>
              <XCircle size={16} style={{ display: 'inline', marginRight: 6 }} />
              HỦY DẪN ĐƯỜNG
            </button>
          </div>
        )}

        {/* Top Filter & Search Toolbar */}
        <div className="map-toolbar">
          <div className="category-filters" style={{ flex: 1, margin: 0 }}>
            {[
              { id: 'all', label: 'Tất Cả Gian Hàng' },
              { id: 'fashion', label: '👗 Thời Trang' },
              { id: 'food', label: '🍔 Ẩm Thực & Cafe' },
              { id: 'entertainment', label: '🎬 Rạp Chiếu Phim' },
              { id: 'utility', label: '🚻 Tiện Ích & WC' },
            ].map(cat => (
              <button
                key={cat.id}
                className={`cat-btn ${selectedCategory === cat.id ? 'active' : ''}`}
                onClick={() => setSelectedCategory(cat.id)}
              >
                {cat.label}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: '0.8rem', fontWeight: 700, color: '#059669', background: '#ECFDF5', padding: '6px 14px', borderRadius: 20, border: '1px solid #A7F3D0' }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10B981', boxShadow: '0 0 6px #10B981' }}></span>
              Sảnh TTTM Tầng 1 (Live)
            </span>
          </div>
        </div>

        {/* Unified Single-Floor Architectural Floorplan Viewport */}
        <div className="map-viewport-card">
          <div className="floorplan-wrapper">
            <svg viewBox="0 0 1100 660" className="floorplan-svg">
              <defs>
                <pattern id="mallTile" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#E2E8F0" strokeWidth="0.8" />
                </pattern>

                <linearGradient id="hallwayAvenue" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#FFFFFF" />
                  <stop offset="100%" stopColor="#F8FAFC" />
                </linearGradient>

                <linearGradient id="glassAtriumGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#E0F2FE" />
                  <stop offset="100%" stopColor="#BAE6FD" />
                </linearGradient>

                <filter id="softCardShadow" x="-10%" y="-10%" width="120%" height="120%">
                  <feDropShadow dx="0" dy="4" stdDeviation="6" floodColor="#0F172A" floodOpacity="0.07" />
                </filter>
                <filter id="laserGlow" x="-20%" y="-20%" width="140%" height="140%">
                  <feDropShadow dx="0" dy="0" stdDeviation="6" floodColor="#2563EB" floodOpacity="0.6" />
                </filter>
                <filter id="robotRadar" x="-50%" y="-50%" width="200%" height="200%">
                  <feDropShadow dx="0" dy="0" stdDeviation="8" floodColor="#10B981" floodOpacity="0.5" />
                </filter>
              </defs>

              {/* Floor Background Grid */}
              <rect width="1100" height="660" fill="url(#mallTile)" />

              {/* Mall Outer Boundary */}
              <rect
                x="30"
                y="20"
                width="1040"
                height="620"
                rx="24"
                fill="url(#hallwayAvenue)"
                stroke="#CBD5E1"
                strokeWidth="2.5"
              />

              {/* Central Skylight Atrium & Fountain */}
              <circle
                cx="550"
                cy="340"
                r="70"
                fill="url(#glassAtriumGrad)"
                stroke="#38BDF8"
                strokeWidth="2"
                strokeDasharray="6 4"
              />
              <circle cx="550" cy="340" r="28" fill="#FFFFFF" stroke="#0284C7" strokeWidth="1.5" />
              <text x="550" y="336" fill="#0284C7" fontSize="10" fontWeight="900" textAnchor="middle">GIẾNG TRỜI</text>
              <text x="550" y="350" fill="#64748B" fontSize="9" fontWeight="700" textAnchor="middle">VÒM KÍNH</text>

              {/* Main Corridors Direction Guides */}
              <line x1="350" y1="340" x2="470" y2="340" stroke="#CBD5E1" strokeWidth="1.5" strokeDasharray="4 4" />
              <line x1="630" y1="340" x2="750" y2="340" stroke="#CBD5E1" strokeWidth="1.5" strokeDasharray="4 4" />
              <line x1="550" y1="220" x2="550" y2="260" stroke="#CBD5E1" strokeWidth="1.5" strokeDasharray="4 4" />
              <line x1="550" y1="420" x2="550" y2="460" stroke="#CBD5E1" strokeWidth="1.5" strokeDasharray="4 4" />

              {/* ================= TOP ROW STORES ================= */}
              {/* 1. UNIQLO LifeWear */}
              <g
                filter="url(#softCardShadow)"
                style={{ cursor: 'pointer' }}
                onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_uniqlo') || null)}
              >
                <rect x="60" y="50" width="280" height="160" rx="14" fill="#FFFFFF" stroke={selectedPoi?.id === 'poi_uniqlo' ? '#2563EB' : '#E2E8F0'} strokeWidth={selectedPoi?.id === 'poi_uniqlo' ? '3' : '1.5'} />
                <rect x="60" y="50" width="280" height="7" rx="3.5" fill="#EF4444" />
                <rect x="80" y="75" width="40" height="40" rx="6" fill="#EF4444" />
                <text x="100" y="94" fill="#FFFFFF" fontSize="10" fontWeight="900" textAnchor="middle">UNI</text>
                <text x="100" y="106" fill="#FFFFFF" fontSize="10" fontWeight="900" textAnchor="middle">QLO</text>
                <text x="135" y="92" fill="#0F172A" fontSize="14" fontWeight="800">UNIQLO LifeWear</text>
                <text x="135" y="110" fill="#64748B" fontSize="10" fontWeight="600">Thời Trang Nhật Bản</text>
                <rect x="80" y="135" width="90" height="24" rx="6" fill="#FEF2F2" />
                <text x="125" y="151" fill="#DC2626" fontSize="10" fontWeight="700" textAnchor="middle">Cánh Tây Bắc</text>
              </g>

              {/* 2. Kura Sushi */}
              <g
                filter="url(#softCardShadow)"
                style={{ cursor: 'pointer' }}
                onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_kura_sushi') || null)}
              >
                <rect x="410" y="50" width="280" height="160" rx="14" fill="#FFFFFF" stroke={selectedPoi?.id === 'poi_kura_sushi' ? '#2563EB' : '#E2E8F0'} strokeWidth={selectedPoi?.id === 'poi_kura_sushi' ? '3' : '1.5'} />
                <rect x="410" y="50" width="280" height="7" rx="3.5" fill="#F97316" />
                <circle cx="440" cy="95" r="18" fill="#FFF7ED" stroke="#F97316" strokeWidth="1.5" />
                <text x="440" y="100" fill="#EA580C" fontSize="15" textAnchor="middle">🍣</text>
                <text x="470" y="92" fill="#0F172A" fontSize="14" fontWeight="800">KURA SUSHI</text>
                <text x="470" y="110" fill="#64748B" fontSize="10" fontWeight="600">Sushi Băng Chuyền Nhật</text>
                <rect x="430" y="135" width="90" height="24" rx="6" fill="#FFF7ED" />
                <text x="475" y="151" fill="#EA580C" fontSize="10" fontWeight="700" textAnchor="middle">Khu Ẩm Thực</text>
              </g>

              {/* 3. ZARA */}
              <g
                filter="url(#softCardShadow)"
                style={{ cursor: 'pointer' }}
                onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_zara') || null)}
              >
                <rect x="760" y="50" width="280" height="160" rx="14" fill="#FFFFFF" stroke={selectedPoi?.id === 'poi_zara' ? '#2563EB' : '#E2E8F0'} strokeWidth={selectedPoi?.id === 'poi_zara' ? '3' : '1.5'} />
                <rect x="760" y="50" width="280" height="7" rx="3.5" fill="#0F172A" />
                <text x="900" y="95" fill="#0F172A" fontSize="18" fontWeight="900" textAnchor="middle" letterSpacing="3">Z A R A</text>
                <text x="900" y="115" fill="#64748B" fontSize="10" fontWeight="600" textAnchor="middle">Thời Trang Quốc Tế Nam & Nữ</text>
                <rect x="855" y="135" width="90" height="24" rx="6" fill="#F1F5F9" />
                <text x="900" y="151" fill="#0F172A" fontSize="10" fontWeight="700" textAnchor="middle">Cánh Đông Bắc</text>
              </g>

              {/* ================= MIDDLE ROW STORES ================= */}
              {/* 4. Highlands Coffee */}
              <g
                filter="url(#softCardShadow)"
                style={{ cursor: 'pointer' }}
                onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_highlands') || null)}
              >
                <rect x="60" y="260" width="280" height="160" rx="14" fill="#FFFFFF" stroke={selectedPoi?.id === 'poi_highlands' ? '#2563EB' : '#E2E8F0'} strokeWidth={selectedPoi?.id === 'poi_highlands' ? '3' : '1.5'} />
                <rect x="60" y="260" width="280" height="7" rx="3.5" fill="#B91C1C" />
                <circle cx="95" cy="305" r="18" fill="#FEF2F2" stroke="#B91C1C" strokeWidth="1.5" />
                <text x="95" y="310" fill="#B91C1C" fontSize="15" textAnchor="middle">☕</text>
                <text x="125" y="302" fill="#B91C1C" fontSize="13" fontWeight="900">HIGHLANDS COFFEE</text>
                <text x="125" y="320" fill="#64748B" fontSize="10" fontWeight="600">Cà Phê, Trà & Freeze</text>
                <rect x="80" y="345" width="90" height="24" rx="6" fill="#FEF2F2" />
                <text x="125" y="361" fill="#B91C1C" fontSize="10" fontWeight="700" textAnchor="middle">Cánh Tây Nam</text>
              </g>

              {/* 5. CGV Cinemas */}
              <g
                filter="url(#softCardShadow)"
                style={{ cursor: 'pointer' }}
                onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_cgv') || null)}
              >
                <rect x="760" y="260" width="280" height="160" rx="14" fill="#FFFFFF" stroke={selectedPoi?.id === 'poi_cgv' ? '#2563EB' : '#E2E8F0'} strokeWidth={selectedPoi?.id === 'poi_cgv' ? '3' : '1.5'} />
                <rect x="760" y="260" width="280" height="7" rx="3.5" fill="#DC2626" />
                <text x="900" y="300" fill="#DC2626" fontSize="18" fontWeight="900" textAnchor="middle" letterSpacing="1">CGV CINEMAS</text>
                <text x="900" y="320" fill="#64748B" fontSize="10" fontWeight="600" textAnchor="middle">Rạp Chiếu Phim IMAX & 4DX</text>
                <rect x="850" y="345" width="100" height="24" rx="6" fill="#FEF2F2" />
                <text x="900" y="361" fill="#DC2626" fontSize="10" fontWeight="700" textAnchor="middle">Cánh Đông</text>
              </g>

              {/* ================= BOTTOM ROW AMENITIES ================= */}
              {/* 6. Thang Máy & Bãi Xe */}
              <g
                filter="url(#softCardShadow)"
                style={{ cursor: 'pointer' }}
                onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_elevator') || null)}
              >
                <rect x="60" y="470" width="280" height="130" rx="14" fill="#FFFFFF" stroke={selectedPoi?.id === 'poi_elevator' ? '#2563EB' : '#E2E8F0'} strokeWidth={selectedPoi?.id === 'poi_elevator' ? '3' : '1.5'} />
                <rect x="60" y="470" width="280" height="7" rx="3.5" fill="#64748B" />
                <circle cx="95" cy="515" r="16" fill="#F1F5F9" stroke="#64748B" strokeWidth="1.5" />
                <text x="95" y="520" fill="#64748B" fontSize="14" textAnchor="middle">🛗</text>
                <text x="125" y="512" fill="#0F172A" fontSize="13" fontWeight="800">THANG MÁY & BÃI XE</text>
                <text x="125" y="530" fill="#64748B" fontSize="10">Lối xuống bãi đỗ xe</text>
              </g>

              {/* 7. Quầy Lễ Tân & CSKH */}
              <g
                filter="url(#softCardShadow)"
                style={{ cursor: 'pointer' }}
                onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_reception') || null)}
              >
                <rect x="410" y="470" width="280" height="130" rx="14" fill="#EFF6FF" stroke={selectedPoi?.id === 'poi_reception' ? '#2563EB' : '#BFDBFE'} strokeWidth={selectedPoi?.id === 'poi_reception' ? '3' : '1.5'} />
                <rect x="410" y="470" width="280" height="7" rx="3.5" fill="#2563EB" />
                <text x="550" y="512" fill="#1D4ED8" fontSize="13" fontWeight="900" textAnchor="middle">ℹ️ QUẦY LỄ TÂN & CSKH</text>
                <text x="550" y="530" fill="#3B82F6" fontSize="10" fontWeight="600" textAnchor="middle">Sảnh Chính Cửa Nam</text>
                <rect x="495" y="550" width="110" height="22" rx="6" fill="#DBEAFE" />
                <text x="550" y="565" fill="#1D4ED8" fontSize="9.5" fontWeight="800" textAnchor="middle">ĐIỂM XUẤT PHÁT</text>
              </g>

              {/* 8. Restroom / WC */}
              <g
                filter="url(#softCardShadow)"
                style={{ cursor: 'pointer' }}
                onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_wc') || null)}
              >
                <rect x="760" y="470" width="280" height="130" rx="14" fill="#FFFFFF" stroke={selectedPoi?.id === 'poi_wc' ? '#2563EB' : '#E2E8F0'} strokeWidth={selectedPoi?.id === 'poi_wc' ? '3' : '1.5'} />
                <rect x="760" y="470" width="280" height="7" rx="3.5" fill="#0284C7" />
                <circle cx="795" cy="515" r="16" fill="#E0F2FE" stroke="#0284C7" strokeWidth="1.5" />
                <text x="795" y="520" fill="#0284C7" fontSize="14" textAnchor="middle">🚻</text>
                <text x="825" y="512" fill="#0F172A" fontSize="13" fontWeight="800">KHU VỆ SINH (WC)</text>
                <text x="825" y="530" fill="#64748B" fontSize="10">Nam • Nữ • Em Bé</text>
              </g>

              {/* Animated Laser Route Path */}
              {activeEscort && (
                <g filter="url(#laserGlow)">
                  <path
                    d={getRoutePath(activeEscort.target_poi_id)}
                    fill="none"
                    stroke="#2563EB"
                    strokeWidth="6"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="route-animated"
                  />
                  {storeCoordinates[activeEscort.target_poi_id] && (
                    <circle
                      cx={storeCoordinates[activeEscort.target_poi_id].x}
                      cy={storeCoordinates[activeEscort.target_poi_id].y}
                      r="16"
                      fill="#2563EB"
                    />
                  )}
                </g>
              )}

              {/* Robot Position Indicator (In Open Promenade) */}
              <g transform={`translate(${currentRobotPos.x}, ${currentRobotPos.y})`} filter="url(#robotRadar)">
                <circle cx="0" cy="0" r="28" fill="rgba(16, 185, 129, 0.2)" className="spin-pulse" />
                <circle cx="0" cy="0" r="15" fill="#10B981" stroke="#FFFFFF" strokeWidth="3" />
                <polygon points="0,-8 6,5 0,2 -6,5" fill="#FFFFFF" />
                <rect x="-38" y="20" width="76" height="22" rx="6" fill="#0F172A" />
                <text x="0" y="35" fill="#10B981" fontSize="10" fontWeight="900" textAnchor="middle">
                  ROBOT
                </text>
              </g>
            </svg>
          </div>

          {/* POI Details Card */}
          {selectedPoi && (
            <div className="poi-detail-card">
              <div className="poi-card-header">
                <div>
                  <h3 className="poi-title">{selectedPoi.name}</h3>
                  <span className="poi-floor-badge">{selectedPoi.category.toUpperCase()} • SẢNH CHÍNH</span>
                </div>
                <button className="btn-close-sm" onClick={() => setSelectedPoi(null)}>✕</button>
              </div>

              <p className="poi-desc">{selectedPoi.description}</p>

              <button
                className="btn-primary btn-block"
                disabled={loadingEscort || (activeEscort?.target_poi_id === selectedPoi.id)}
                onClick={() => handleStartEscort(selectedPoi)}
              >
                <Navigation size={16} style={{ display: 'inline', marginRight: 6 }} />
                {activeEscort?.target_poi_id === selectedPoi.id
                  ? 'ROBOT ĐANG DẪN ĐƯỜNG ĐẾN ĐÂY'
                  : 'YÊU CẦU ROBOT DẪN TÔI ĐẾN ĐÂY'}
              </button>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
