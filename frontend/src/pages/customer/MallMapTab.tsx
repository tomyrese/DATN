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
  Layers,
  MapPin,
  Clock,
  Compass,
} from 'lucide-react';

export const MallMapTab: React.FC = () => {
  const { pois, activeEscort, pairedRobot, telemetry } = useRobotStore();
  const [selectedFloor, setSelectedFloor] = useState<'T1' | 'T2' | 'T3'>('T1');
  const [selectedPoi, setSelectedPoi] = useState<PointOfInterest | null>(null);
  const [loadingEscort, setLoadingEscort] = useState(false);

  // Filter POIs for current floor
  const floorPois = pois.filter(p => p.floor === selectedFloor && !p.is_staff_only);

  const handleStartEscort = async (poi: PointOfInterest) => {
    if (!pairedRobot) {
      alert('Vui lòng kết nối với Robot qua mục Cài Đặt trước khi yêu cầu dẫn đường.');
      return;
    }
    setLoadingEscort(true);
    try {
      const res = await RobotApi.requestEscort(pairedRobot.host, pairedRobot.port, poi.id);
      if (res.success && res.task) {
        updateGlobalState(() => ({ activeEscort: res.task }));
      } else {
        alert(res.message || 'Không thể khởi động chế độ dẫn đường.');
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

  // Simulated Robot position on Floor 1
  const robotPos = { x: 50, y: 80 };

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
                  ROBOT ĐANG DẪN ĐƯỜNG ĐẾN: {activeEscort.target_name} ({activeEscort.target_floor})
                </div>
                <div className="escort-sub">
                  Vui lòng đi theo Robot • Tốc độ an toàn: {telemetry?.speed?.toFixed(2) || '0.35'} m/s • Thời gian dự kiến: ~{activeEscort.estimated_seconds}s
                </div>
              </div>
            </div>
            <button className="btn-cancel-escort" onClick={handleCancelEscort}>
              <XCircle size={16} style={{ display: 'inline', marginRight: 6 }} />
              HỦY DẪN ĐƯỜNG
            </button>
          </div>
        )}

        {/* Map Toolbar & Floor Switcher */}
        <div className="map-toolbar">
          <div className="floor-selector">
            <Layers size={18} color="#2563EB" />
            <span className="toolbar-label">SƠ ĐỒ TẦNG:</span>
            {[
              { id: 'T1', label: 'Tầng 1 (Sảnh Chính & Thời Trang)' },
              { id: 'T2', label: 'Tầng 2 (Ẩm Thực & Mua Sắm)' },
              { id: 'T3', label: 'Tầng 3 (Rạp Chiếu Phim & Giải Trí)' },
            ].map(f => (
              <button
                key={f.id}
                className={`floor-btn ${selectedFloor === f.id ? 'active' : ''}`}
                onClick={() => {
                  setSelectedFloor(f.id as any);
                  setSelectedPoi(null);
                }}
              >
                {f.label}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: '0.8rem', color: '#64748B' }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10B981' }}></span> Robot sẵn sàng
            </span>
          </div>
        </div>

        {/* High-End Architectural Floorplan Viewport */}
        <div className="map-viewport-card">
          <div className="floorplan-wrapper">
            <svg viewBox="0 0 1000 600" className="floorplan-svg">
              <defs>
                {/* Subtle Modern Grid */}
                <pattern id="lightGrid" width="50" height="50" patternUnits="userSpaceOnUse">
                  <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#E2E8F0" strokeWidth="0.75" />
                </pattern>

                {/* Atrium Skylight Gradient */}
                <linearGradient id="atriumGlass" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#E0F2FE" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#BAE6FD" stopOpacity="0.5" />
                </linearGradient>

                {/* Walkway Gradient */}
                <linearGradient id="walkwayGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#FFFFFF" />
                  <stop offset="100%" stopColor="#F8FAFC" />
                </linearGradient>

                {/* Shadow Filters for Store Blocks */}
                <filter id="storeShadow" x="-10%" y="-10%" width="120%" height="120%">
                  <feDropShadow dx="0" dy="4" stdDeviation="6" floodColor="#0F172A" floodOpacity="0.06" />
                </filter>
                <filter id="robotGlow" x="-50%" y="-50%" width="200%" height="200%">
                  <feDropShadow dx="0" dy="0" stdDeviation="8" floodColor="#10B981" floodOpacity="0.4" />
                </filter>
              </defs>

              {/* Background Canvas */}
              <rect width="1000" height="600" fill="url(#lightGrid)" />

              {/* Mall Outer Floor Perimeter */}
              <rect
                x="80"
                y="50"
                width="840"
                height="500"
                rx="28"
                fill="url(#walkwayGrad)"
                stroke="#CBD5E1"
                strokeWidth="2.5"
              />

              {/* Central Skylight Atrium & Fountain */}
              <circle
                cx="500"
                cy="300"
                r="105"
                fill="url(#atriumGlass)"
                stroke="#38BDF8"
                strokeWidth="2"
                strokeDasharray="6 4"
              />
              <circle cx="500" cy="300" r="45" fill="#E0F2FE" stroke="#0284C7" strokeWidth="1.5" />
              <text x="500" y="295" fill="#0284C7" fontSize="11" fontWeight="800" textAnchor="middle">
                GIẾNG TRỜI VÒM KÍNH
              </text>
              <text x="500" y="312" fill="#64748B" fontSize="10" fontWeight="600" textAnchor="middle">
                {selectedFloor === 'T1' ? 'SẢNH TRUNG TÂM T1' : selectedFloor === 'T2' ? 'KHU VỰC SỰ KIỆN T2' : 'SẢNH CHỜ RẠP PHIM T3'}
              </text>

              {/* Architectural Entrance / Doors */}
              {selectedFloor === 'T1' && (
                <>
                  <rect x="440" y="535" width="120" height="16" rx="4" fill="#0F172A" />
                  <text x="500" y="547" fill="#FFFFFF" fontSize="9" fontWeight="800" textAnchor="middle">
                    CỬA VÀO CHÍNH (SẢNH NAM)
                  </text>
                </>
              )}

              {/* ================= FLOOR 1 SPECIFIC STORES ================= */}
              {selectedFloor === 'T1' && (
                <>
                  {/* ZARA Store Block */}
                  <g
                    filter="url(#storeShadow)"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_zara') || null)}
                  >
                    <rect x="620" y="90" width="260" height="170" rx="14" fill="#FFFFFF" stroke={selectedPoi?.id === 'poi_zara' ? '#2563EB' : '#E2E8F0'} strokeWidth={selectedPoi?.id === 'poi_zara' ? '3' : '1.5'} />
                    <rect x="620" y="90" width="260" height="8" rx="4" fill="#0F172A" />
                    <text x="750" y="145" fill="#0F172A" fontSize="16" fontWeight="900" textAnchor="middle" letterSpacing="2">Z A R A</text>
                    <text x="750" y="165" fill="#64748B" fontSize="10" fontWeight="600" textAnchor="middle">Thời Trang Quốc Tế Nam & Nữ</text>
                    <rect x="710" y="185" width="80" height="22" rx="11" fill="#F1F5F9" />
                    <text x="750" y="200" fill="#2563EB" fontSize="10" fontWeight="700" textAnchor="middle">Tầng 1 • Khu A</text>
                  </g>

                  {/* UNIQLO Store Block */}
                  <g
                    filter="url(#storeShadow)"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_uniqlo') || null)}
                  >
                    <rect x="120" y="90" width="260" height="170" rx="14" fill="#FFFFFF" stroke={selectedPoi?.id === 'poi_uniqlo' ? '#2563EB' : '#E2E8F0'} strokeWidth={selectedPoi?.id === 'poi_uniqlo' ? '3' : '1.5'} />
                    <rect x="120" y="90" width="260" height="8" rx="4" fill="#EF4444" />
                    <rect x="230" y="115" width="40" height="40" rx="6" fill="#EF4444" />
                    <text x="250" y="138" fill="#FFFFFF" fontSize="11" fontWeight="900" textAnchor="middle">UNI</text>
                    <text x="250" y="150" fill="#FFFFFF" fontSize="10" fontWeight="900" textAnchor="middle">QLO</text>
                    <text x="250" y="180" fill="#0F172A" fontSize="13" fontWeight="800" textAnchor="middle">UNIQLO LifeWear</text>
                    <text x="250" y="200" fill="#64748B" fontSize="10" fontWeight="600" textAnchor="middle">Thời Trang Nhật Bản</text>
                  </g>

                  {/* Highlands Coffee Block */}
                  <g
                    filter="url(#storeShadow)"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_highlands') || null)}
                  >
                    <rect x="120" y="340" width="260" height="160" rx="14" fill="#FFFFFF" stroke={selectedPoi?.id === 'poi_highlands' ? '#2563EB' : '#E2E8F0'} strokeWidth={selectedPoi?.id === 'poi_highlands' ? '3' : '1.5'} />
                    <rect x="120" y="340" width="260" height="8" rx="4" fill="#B91C1C" />
                    <circle cx="250" cy="385" r="20" fill="#FEF2F2" stroke="#B91C1C" strokeWidth="1.5" />
                    <text x="250" y="390" fill="#B91C1C" fontSize="16" textAnchor="middle">☕</text>
                    <text x="250" y="425" fill="#B91C1C" fontSize="13" fontWeight="900" textAnchor="middle">HIGHLANDS COFFEE</text>
                    <text x="250" y="445" fill="#64748B" fontSize="10" fontWeight="600" textAnchor="middle">Cà Phê, Trà & Bánh Ngọt</text>
                  </g>

                  {/* Quầy Lễ Tân & CSKH */}
                  <g
                    filter="url(#storeShadow)"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_reception') || null)}
                  >
                    <rect x="420" y="425" width="160" height="75" rx="12" fill="#EFF6FF" stroke={selectedPoi?.id === 'poi_reception' ? '#2563EB' : '#BFDBFE'} strokeWidth="2" />
                    <text x="500" y="455" fill="#1D4ED8" fontSize="11" fontWeight="800" textAnchor="middle">ℹ️ QUẦY LỄ TÂN & CSKH</text>
                    <text x="500" y="475" fill="#3B82F6" fontSize="9" fontWeight="600" textAnchor="middle">Đổi quà & Thông tin</text>
                  </g>

                  {/* Restroom T1 */}
                  <g
                    filter="url(#storeShadow)"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_wc_t1') || null)}
                  >
                    <rect x="700" y="380" width="180" height="120" rx="14" fill="#F8FAFC" stroke={selectedPoi?.id === 'poi_wc_t1' ? '#2563EB' : '#E2E8F0'} strokeWidth="1.5" />
                    <text x="790" y="425" fill="#0284C7" fontSize="18" textAnchor="middle">🚻</text>
                    <text x="790" y="450" fill="#0F172A" fontSize="12" fontWeight="800" textAnchor="middle">NHÀ VỆ SINH TẦNG 1</text>
                    <text x="790" y="468" fill="#64748B" fontSize="10" textAnchor="middle">Nam • Nữ • Em Bé</text>
                  </g>
                </>
              )}

              {/* ================= FLOOR 2 SPECIFIC STORES ================= */}
              {selectedFloor === 'T2' && (
                <>
                  {/* Phúc Long */}
                  <g
                    filter="url(#storeShadow)"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_phuclong') || null)}
                  >
                    <rect x="120" y="90" width="260" height="170" rx="14" fill="#FFFFFF" stroke={selectedPoi?.id === 'poi_phuclong' ? '#2563EB' : '#E2E8F0'} strokeWidth="2" />
                    <rect x="120" y="90" width="260" height="8" rx="4" fill="#059669" />
                    <text x="250" y="145" fill="#059669" fontSize="15" fontWeight="900" textAnchor="middle">TRÀ PHÚC LONG</text>
                    <text x="250" y="168" fill="#64748B" fontSize="10" fontWeight="600" textAnchor="middle">Trà Đào • Trà Sữa Thơm Ngon</text>
                  </g>

                  {/* Kura Sushi */}
                  <g
                    filter="url(#storeShadow)"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_kura_sushi') || null)}
                  >
                    <rect x="620" y="90" width="260" height="170" rx="14" fill="#FFFFFF" stroke={selectedPoi?.id === 'poi_kura_sushi' ? '#2563EB' : '#E2E8F0'} strokeWidth="2" />
                    <rect x="620" y="90" width="260" height="8" rx="4" fill="#F97316" />
                    <text x="750" y="145" fill="#EA580C" fontSize="15" fontWeight="900" textAnchor="middle">KURA SUSHI</text>
                    <text x="750" y="168" fill="#64748B" fontSize="10" fontWeight="600" textAnchor="middle">Sushi Băng Chuyền Nhật Bản</text>
                  </g>

                  {/* Adidas Originals */}
                  <g
                    filter="url(#storeShadow)"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_adidas') || null)}
                  >
                    <rect x="120" y="340" width="260" height="160" rx="14" fill="#FFFFFF" stroke={selectedPoi?.id === 'poi_adidas' ? '#2563EB' : '#E2E8F0'} strokeWidth="2" />
                    <rect x="120" y="340" width="260" height="8" rx="4" fill="#0F172A" />
                    <text x="250" y="415" fill="#0F172A" fontSize="15" fontWeight="900" textAnchor="middle">ADIDAS ORIGINALS</text>
                    <text x="250" y="438" fill="#64748B" fontSize="10" fontWeight="600" textAnchor="middle">Giày & Thời Trang Thể Thao</text>
                  </g>

                  {/* Restroom T2 */}
                  <g
                    filter="url(#storeShadow)"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_wc_t2') || null)}
                  >
                    <rect x="700" y="380" width="180" height="120" rx="14" fill="#F8FAFC" stroke={selectedPoi?.id === 'poi_wc_t2' ? '#2563EB' : '#E2E8F0'} strokeWidth="1.5" />
                    <text x="790" y="425" fill="#0284C7" fontSize="18" textAnchor="middle">🚻</text>
                    <text x="790" y="450" fill="#0F172A" fontSize="12" fontWeight="800" textAnchor="middle">NHÀ VỆ SINH TẦNG 2</text>
                  </g>
                </>
              )}

              {/* ================= FLOOR 3 SPECIFIC STORES ================= */}
              {selectedFloor === 'T3' && (
                <>
                  {/* CGV Cinemas */}
                  <g
                    filter="url(#storeShadow)"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_cgv') || null)}
                  >
                    <rect x="120" y="90" width="380" height="220" rx="16" fill="#FEF2F2" stroke={selectedPoi?.id === 'poi_cgv' ? '#EF4444' : '#FECACA'} strokeWidth="2.5" />
                    <text x="310" y="160" fill="#DC2626" fontSize="22" fontWeight="900" textAnchor="middle" letterSpacing="1">CGV CINEMAS</text>
                    <text x="310" y="190" fill="#991B1B" fontSize="12" fontWeight="700" textAnchor="middle">Cụm Rạp Chiếu Phim IMAX & 4DX</text>
                    <text x="310" y="215" fill="#64748B" fontSize="11" textAnchor="middle">Suất chiếu từ 09:00 - 23:30</text>
                  </g>

                  {/* TimeZone Arcade */}
                  <g
                    filter="url(#storeShadow)"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_arcade') || null)}
                  >
                    <rect x="560" y="90" width="320" height="220" rx="16" fill="#FAF5FF" stroke={selectedPoi?.id === 'poi_arcade' ? '#8B5CF6' : '#E9D5FF'} strokeWidth="2.5" />
                    <text x="720" y="160" fill="#7C3AED" fontSize="20" fontWeight="900" textAnchor="middle">TIMEZONE GAME</text>
                    <text x="720" y="190" fill="#6D28D9" fontSize="12" fontWeight="700" textAnchor="middle">Khu Trò Chơi Điện Tử & Gắp Thú</text>
                  </g>

                  {/* Restroom T3 */}
                  <g
                    filter="url(#storeShadow)"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedPoi(pois.find(p => p.id === 'poi_wc_t3') || null)}
                  >
                    <rect x="700" y="380" width="180" height="120" rx="14" fill="#F8FAFC" stroke={selectedPoi?.id === 'poi_wc_t3' ? '#2563EB' : '#E2E8F0'} strokeWidth="1.5" />
                    <text x="790" y="425" fill="#0284C7" fontSize="18" textAnchor="middle">🚻</text>
                    <text x="790" y="450" fill="#0F172A" fontSize="12" fontWeight="800" textAnchor="middle">NHÀ VỆ SINH TẦNG 3</text>
                  </g>
                </>
              )}

              {/* Dynamic Escort Navigation Trail */}
              {activeEscort && selectedPoi && (
                <g>
                  <path
                    d={`M 500 480 L 500 300 L ${selectedPoi.x * 10} ${selectedPoi.y * 6}`}
                    fill="none"
                    stroke="#2563EB"
                    strokeWidth="5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="route-animated"
                  />
                  <circle cx={selectedPoi.x * 10} cy={selectedPoi.y * 6} r="14" fill="#2563EB" />
                  <circle cx={selectedPoi.x * 10} cy={selectedPoi.y * 6} r="22" fill="none" stroke="#2563EB" strokeWidth="2" opacity="0.6" className="spin-pulse" />
                </g>
              )}

              {/* Robot Location Marker */}
              {selectedFloor === 'T1' && (
                <g transform={`translate(${robotPos.x * 10}, ${robotPos.y * 6})`} filter="url(#robotGlow)">
                  <circle cx="0" cy="0" r="22" fill="rgba(16, 185, 129, 0.25)" className="spin-pulse" />
                  <circle cx="0" cy="0" r="14" fill="#10B981" stroke="#FFFFFF" strokeWidth="2.5" />
                  <polygon points="0,-7 5,5 0,2 -5,5" fill="#FFFFFF" />
                  <rect x="-35" y="18" width="70" height="20" rx="6" fill="#0F172A" />
                  <text x="0" y="32" fill="#10B981" fontSize="10" fontWeight="900" textAnchor="middle">
                    ROBOT
                  </text>
                </g>
              )}
            </svg>
          </div>

          {/* Selected POI Details Slide-Up Card */}
          {selectedPoi && (
            <div className="poi-detail-card">
              <div className="poi-card-header">
                <div>
                  <h3 className="poi-title">{selectedPoi.name}</h3>
                  <span className="poi-floor-badge">{selectedPoi.floor} • {selectedPoi.category.toUpperCase()}</span>
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
