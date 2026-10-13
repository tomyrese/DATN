import React, { useState, useEffect } from 'react';
import { useRobotStore } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { Promotion, PointOfInterest } from '../../types/protocol';
import {
  Search,
  MapPin,
  Bot,
  Tag,
  Store,
  Navigation,
  Sparkles,
  Wifi,
  Clock,
  ArrowRight,
  ShieldCheck,
  CheckCircle,
  HelpCircle,
  Film,
  Utensils,
  Shirt,
} from 'lucide-react';

interface GuestHomePageProps {
  onNavigateTab: (tabId: string, payload?: any) => void;
  onOpenStoreModal: (poi: PointOfInterest) => void;
}

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

export const GuestHomePage: React.FC<GuestHomePageProps> = ({
  onNavigateTab,
  onOpenStoreModal,
}) => {
  const { pois, connectionStatus, pairedRobot } = useRobotStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [loadingPromos, setLoadingPromos] = useState(true);

  // Fetch real active promotions from backend SQLite
  useEffect(() => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    RobotApi.getPromotions(host, port)
      .then(promos => {
        setPromotions(promos || []);
        setLoadingPromos(false);
      })
      .catch(() => {
        setLoadingPromos(false);
      });
  }, [pairedRobot]);

  const customerPois = pois.filter(p => !p.is_staff_only);

  // Filtered store search suggestions
  const searchResults = searchQuery.trim()
    ? customerPois.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.category.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : [];

  const quickQuestions = [
    'Nhà vệ sinh gần nhất ở đâu?',
    'Có khuyến mãi nào hôm nay?',
    'Tìm cửa hàng thời trang',
    'Chỉ đường đến rạp CGV',
    'Quán cafe nghỉ chân ở đâu?',
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '1000px', margin: '0 auto', width: '100%' }}>
      
      {/* ==================== 1. WELCOME HERO SECTION ==================== */}
      <section
        className="card-clean"
        style={{
          padding: '24px 28px',
          background: 'linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 100%)',
          border: '1px solid #BFDBFE',
          borderRadius: '16px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: '#DBEAFE', color: '#1D4ED8', padding: '4px 10px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 700, marginBottom: '10px' }}>
              <Sparkles size={14} />
              <span>ROBOT HỖ TRỢ TRUNG TÂM THƯƠNG MẠI</span>
            </div>
            <h2 style={{ fontSize: '1.65rem', fontWeight: 800, color: '#0F172A', margin: '0 0 8px 0', lineHeight: 1.25 }}>
              Xin chào! Tôi có thể giúp gì cho quý khách?
            </h2>
            <p style={{ margin: 0, fontSize: '0.95rem', color: '#475569', maxWidth: '620px', lineHeight: 1.5 }}>
              Tra cứu vị trí gian hàng, dẫn đường trực tiếp tại Tầng 1, hỏi đáp thông tin tiện ích và cập nhật ưu đãi mới nhất trong ngày.
            </p>
          </div>

          {/* Robot Operational Status Pill */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: '#F0FDF4',
              border: '1px solid #86EFAC',
              padding: '8px 14px',
              borderRadius: '12px',
            }}
          >
            <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#16A34A', boxShadow: '0 0 0 3px #DCFCE7' }}></div>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#166534', fontWeight: 600 }}>Trạng thái Robot</div>
              <div style={{ fontSize: '0.85rem', color: '#14532D', fontWeight: 800 }}>
                {connectionStatus === 'CONNECTED' ? 'Sẵn sàng tại Sảnh T1' : 'Hệ thống trực tuyến'}
              </div>
            </div>
          </div>
        </div>

        {/* ==================== SMART SEARCH BAR ==================== */}
        <div style={{ marginTop: '20px', position: 'relative' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              background: '#FFFFFF',
              border: '2px solid #2563EB',
              borderRadius: '12px',
              padding: '10px 16px',
              gap: '12px',
              boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.1)',
            }}
          >
            <Search size={22} color="#2563EB" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tôi đang tìm gì? Nhập tên cửa hàng, món ăn, dịch vụ..."
              style={{
                border: 'none',
                outline: 'none',
                width: '100%',
                fontSize: '1rem',
                fontWeight: 500,
                color: '#0F172A',
                background: 'transparent',
              }}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                style={{
                  background: '#F1F5F9',
                  border: 'none',
                  borderRadius: '50%',
                  width: '24px',
                  height: '24px',
                  cursor: 'pointer',
                  color: '#64748B',
                  fontWeight: 'bold',
                }}
              >
                ✕
              </button>
            )}
          </div>

          {/* Instant Search Results Dropdown */}
          {searchQuery.trim() !== '' && (
            <div
              style={{
                position: 'absolute',
                top: '105%',
                left: 0,
                right: 0,
                background: '#FFFFFF',
                borderRadius: '12px',
                border: '1px solid #CBD5E1',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                zIndex: 50,
                maxHeight: '280px',
                overflowY: 'auto',
                padding: '6px',
              }}
            >
              {searchResults.length > 0 ? (
                searchResults.map(poi => (
                  <div
                    key={poi.id}
                    onClick={() => {
                      onOpenStoreModal(poi);
                      setSearchQuery('');
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '10px 14px',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      borderBottom: '1px solid #F1F5F9',
                      transition: 'background 0.15s ease',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#F8FAFC')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '20px' }}>{STORE_EMOJIS[poi.id] || '🏪'}</span>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: '0.92rem', color: '#0F172A' }}>{poi.name}</div>
                        <div style={{ fontSize: '0.78rem', color: '#64748B' }}>{poi.description}</div>
                      </div>
                    </div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#2563EB', background: '#EFF6FF', padding: '3px 8px', borderRadius: '6px' }}>
                      Xem chi tiết →
                    </span>
                  </div>
                ))
              ) : (
                <div style={{ padding: '16px', textAlign: 'center', color: '#64748B', fontSize: '0.9rem' }}>
                  Không tìm thấy địa điểm phù hợp với từ khóa "{searchQuery}"
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {/* ==================== 2. PRIMARY 4 SHORTCUTS ==================== */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '14px' }}>
        
        {/* Bản đồ & Dẫn đường */}
        <div
          onClick={() => onNavigateTab('mall-map')}
          className="card-clean hover-elevate"
          style={{
            padding: '18px 20px',
            cursor: 'pointer',
            border: '1.5px solid #E2E8F0',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '10px', background: '#EFF6FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563EB' }}>
              <Navigation size={22} />
            </div>
            <ArrowRight size={18} color="#94A3B8" />
          </div>
          <div>
            <h3 style={{ margin: '4px 0 2px 0', fontSize: '1.05rem', fontWeight: 800, color: '#0F172A' }}>
              Bản Đồ Dẫn Đường
            </h3>
            <p style={{ margin: 0, fontSize: '0.82rem', color: '#64748B' }}>
              Xem vị trí robot và lộ trình đến gian hàng tại Tầng 1
            </p>
          </div>
        </div>

        {/* Danh mục gian hàng */}
        <div
          onClick={() => onNavigateTab('mall-directory')}
          className="card-clean hover-elevate"
          style={{
            padding: '18px 20px',
            cursor: 'pointer',
            border: '1.5px solid #E2E8F0',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '10px', background: '#FDF2F8', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#DB2777' }}>
              <Store size={22} />
            </div>
            <ArrowRight size={18} color="#94A3B8" />
          </div>
          <div>
            <h3 style={{ margin: '4px 0 2px 0', fontSize: '1.05rem', fontWeight: 800, color: '#0F172A' }}>
              Gian Hàng & Dịch Vụ
            </h3>
            <p style={{ margin: 0, fontSize: '0.82rem', color: '#64748B' }}>
              Tra cứu thời trang, ẩm thực, rạp phim và hotline
            </p>
          </div>
        </div>

        {/* Hỏi Trợ Lý Ảo */}
        <div
          onClick={() => onNavigateTab('mall-assistant')}
          className="card-clean hover-elevate"
          style={{
            padding: '18px 20px',
            cursor: 'pointer',
            border: '1.5px solid #E2E8F0',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '10px', background: '#F0FDF4', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#16A34A' }}>
              <Bot size={22} />
            </div>
            <ArrowRight size={18} color="#94A3B8" />
          </div>
          <div>
            <h3 style={{ margin: '4px 0 2px 0', fontSize: '1.05rem', fontWeight: 800, color: '#0F172A' }}>
              Hỏi Trợ Lý Ảo AI
            </h3>
            <p style={{ margin: 0, fontSize: '0.82rem', color: '#64748B' }}>
              Hỏi đáp tự nhiên về vị trí, tiện ích và giải đáp thắc mắc
            </p>
          </div>
        </div>

        {/* Ưu Đãi & Khuyến Mãi */}
        <div
          onClick={() => onNavigateTab('guest-promotions')}
          className="card-clean hover-elevate"
          style={{
            padding: '18px 20px',
            cursor: 'pointer',
            border: '1.5px solid #E2E8F0',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ width: '42px', height: '42px', borderRadius: '10px', background: '#FEF2F2', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#DC2626' }}>
              <Tag size={22} />
            </div>
            <span style={{ background: '#DC2626', color: '#FFFFFF', fontSize: '0.7rem', fontWeight: 700, padding: '2px 7px', borderRadius: '10px' }}>
              {promotions.length} Ưu đãi
            </span>
          </div>
          <div>
            <h3 style={{ margin: '4px 0 2px 0', fontSize: '1.05rem', fontWeight: 800, color: '#0F172A' }}>
              Khuyến Mãi Hôm Nay
            </h3>
            <p style={{ margin: 0, fontSize: '0.82rem', color: '#64748B' }}>
              Chương trình giảm giá và ưu đãi đang có hiệu lực
            </p>
          </div>
        </div>

      </section>

      {/* ==================== 3. ACTIVE PROMOTIONS PREVIEW ==================== */}
      <section className="card-clean" style={{ padding: '22px 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Tag size={20} color="#DC2626" />
            <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#0F172A' }}>
              Chương Trình Khuyến Mãi Nổi Bật
            </h3>
          </div>
          <button
            onClick={() => onNavigateTab('guest-promotions')}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#2563EB',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            Xem tất cả ({promotions.length}) →
          </button>
        </div>

        {loadingPromos ? (
          <div style={{ padding: '20px', textAlign: 'center', color: '#64748B' }}>Đang tải danh sách ưu đãi...</div>
        ) : promotions.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
            {promotions.slice(0, 3).map(promo => (
              <div
                key={promo.id}
                style={{
                  border: '1.5px solid #FEE2E2',
                  background: '#FFF5F5',
                  borderRadius: '12px',
                  padding: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '10px',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#991B1B', background: '#FEE2E2', padding: '2px 8px', borderRadius: '6px' }}>
                      {promo.store_name || 'Khuyến mãi'}
                    </span>
                    {promo.discount_percent > 0 && (
                      <span style={{ background: '#DC2626', color: '#FFFFFF', padding: '2px 6px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
                        -{promo.discount_percent}%
                      </span>
                    )}
                  </div>
                  <h4 style={{ margin: '0 0 4px 0', fontSize: '0.98rem', fontWeight: 800, color: '#0F172A' }}>
                    {promo.title}
                  </h4>
                  <p style={{ margin: 0, fontSize: '0.82rem', color: '#475569', lineHeight: 1.4 }}>
                    {promo.description}
                  </p>
                </div>
                {promo.promo_code && (
                  <div style={{ fontSize: '0.78rem', color: '#991B1B', fontWeight: 600 }}>
                    Mã: <code style={{ background: '#FEE2E2', padding: '2px 6px', borderRadius: '4px' }}>{promo.promo_code}</code>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div style={{ padding: '20px', textAlign: 'center', color: '#64748B', background: '#F8FAFC', borderRadius: '10px' }}>
            Hiện chưa có chương trình khuyến mãi nào được công bố.
          </div>
        )}
      </section>

      {/* ==================== 4. QUICK CONCIERGE PROMPTS ==================== */}
      <section className="card-clean" style={{ padding: '22px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
          <HelpCircle size={20} color="#2563EB" />
          <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#0F172A' }}>
            Tôi có thể hỏi ai? Gợi ý câu hỏi nhanh cho Trợ Lý Ảo
          </h3>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          {quickQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => onNavigateTab('mall-assistant', { prompt: q })}
              style={{
                background: '#F1F5F9',
                border: '1px solid #CBD5E1',
                borderRadius: '20px',
                padding: '8px 14px',
                fontSize: '0.84rem',
                fontWeight: 600,
                color: '#334155',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#EFF6FF';
                e.currentTarget.style.borderColor = '#93C5FD';
                e.currentTarget.style.color = '#1D4ED8';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#F1F5F9';
                e.currentTarget.style.borderColor = '#CBD5E1';
                e.currentTarget.style.color = '#334155';
              }}
            >
              <span>💬 {q}</span>
            </button>
          ))}
        </div>
      </section>

      {/* ==================== 5. PUBLIC UTILITIES & ESSENTIAL INFO ==================== */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
        
        {/* Wi-Fi & Giờ mở cửa */}
        <div className="card-clean" style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Wifi size={18} color="#2563EB" />
            <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 800, color: '#0F172A' }}>
              Wi-Fi Miễn Phí Tại TTTM
            </h4>
          </div>
          <div style={{ background: '#F8FAFC', padding: '10px 14px', borderRadius: '8px', border: '1px solid #E2E8F0', fontSize: '0.82rem', color: '#475569' }}>
            Mạng Wi-Fi: <strong style={{ color: '#0F172A' }}>TTTM-FreeWiFi</strong> (Không cần mật khẩu, kết nối trực tiếp tại sảnh).
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#64748B' }}>
            <Clock size={16} /> Giờ mở cửa TTTM: <strong>09:30 - 22:00</strong> (Tất cả các ngày trong tuần)
          </div>
        </div>

        {/* Tiện ích nhanh */}
        <div className="card-clean" style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MapPin size={18} color="#16A34A" />
            <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 800, color: '#0F172A' }}>
              Lối Tắt Tiện Ích Tầng 1
            </h4>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <button
              onClick={() => onNavigateTab('mall-map', { targetPoiId: 'poi_wc' })}
              style={{
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                padding: '8px',
                fontSize: '0.8rem',
                fontWeight: 600,
                color: '#334155',
                cursor: 'pointer',
                textAlign: 'left',
              }}
            >
              🚻 Nhà Vệ Sinh T1
            </button>
            <button
              onClick={() => onNavigateTab('mall-map', { targetPoiId: 'poi_elevator' })}
              style={{
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                padding: '8px',
                fontSize: '0.8rem',
                fontWeight: 600,
                color: '#334155',
                cursor: 'pointer',
                textAlign: 'left',
              }}
            >
              🛗 Thang Máy Trung Tâm
            </button>
            <button
              onClick={() => onNavigateTab('mall-map', { targetPoiId: 'poi_reception' })}
              style={{
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                padding: '8px',
                fontSize: '0.8rem',
                fontWeight: 600,
                color: '#334155',
                cursor: 'pointer',
                textAlign: 'left',
              }}
            >
              💁 Quầy Lễ Tân & CSKH
            </button>
            <button
              onClick={() => onNavigateTab('mall-map', { targetPoiId: 'poi_cgv' })}
              style={{
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                padding: '8px',
                fontSize: '0.8rem',
                fontWeight: 600,
                color: '#334155',
                cursor: 'pointer',
                textAlign: 'left',
              }}
            >
              🎬 Rạp CGV Cinema
            </button>
          </div>
        </div>

      </section>

    </div>
  );
};
