import React, { useState, useEffect } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { PointOfInterest, Promotion } from '../../types/protocol';
import { StoreDetailModal } from '../../components/StoreDetailModal';
import { Search, Navigation, Info, Tag, MapPin } from 'lucide-react';

const CATEGORIES = [
  { id: 'all', label: 'Tất Cả' },
  { id: 'food', label: '🍔 Ẩm Thực & Cafe' },
  { id: 'fashion', label: '👗 Thời Trang' },
  { id: 'entertainment', label: '🎬 Rạp Chiếu Phim' },
  { id: 'utility', label: '🚻 Tiện Ích & WC' },
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

interface MallDirectoryTabProps {
  onNavigateToMap?: (poiId: string) => void;
  onAskAssistant?: (storeName: string) => void;
}

export const MallDirectoryTab: React.FC<MallDirectoryTabProps> = ({
  onNavigateToMap,
  onAskAssistant,
}) => {
  const { pois, pairedRobot, activeEscort } = useRobotStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loadingPoiId, setLoadingPoiId] = useState<string | null>(null);
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [modalPoi, setModalPoi] = useState<PointOfInterest | null>(null);

  useEffect(() => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    RobotApi.getPromotions(host, port)
      .then(promos => setPromotions(promos || []))
      .catch(() => {});
  }, [pairedRobot]);

  const customerPois = pois.filter(p => !p.is_staff_only);

  const filteredPois = customerPois.filter(poi => {
    const matchCat = selectedCategory === 'all' || poi.category === selectedCategory;
    const matchSearch =
      poi.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      poi.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchCat && matchSearch;
  });

  const handleEscort = async (poi: PointOfInterest) => {
    if (onNavigateToMap) {
      onNavigateToMap(poi.id);
      return;
    }
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    setLoadingPoiId(poi.id);
    try {
      const res = await RobotApi.requestEscort(host, port, poi.id);
      if (res.success && res.task) {
        updateGlobalState(() => ({ activeEscort: res.task }));
        alert(`🎉 Robot đã nhận lệnh dẫn đường đến: ${res.task.target_name}!`);
      } else {
        alert(res.message || 'Không thể bắt đầu dẫn đường lúc này.');
      }
    } catch (e: any) {
      alert(`Lỗi: ${e.message}`);
    } finally {
      setLoadingPoiId(null);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '1000px', margin: '0 auto', width: '100%' }}>
      
      {/* Search & Filter Header Bar */}
      <div className="card-clean" style={{ padding: '16px 20px', borderRadius: '16px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          
          <div className="quick-search-box">
            <Search size={20} />
            <input
              type="text"
              className="quick-search-input"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tìm kiếm gian hàng, món ăn, dịch vụ..."
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#64748B', fontWeight: 'bold' }}
              >
                ✕
              </button>
            )}
          </div>

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

        </div>
      </div>

      {/* Results Header Count */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 4px' }}>
        <span style={{ fontSize: '0.88rem', fontWeight: 600, color: '#64748B' }}>
          Hiển thị <strong>{filteredPois.length}</strong> gian hàng & tiện ích tại Tầng 1
        </span>
      </div>

      {/* Store Directory Cards Grid */}
      {filteredPois.length > 0 ? (
        <div className="delivery-orders-grid">
          {filteredPois.map(poi => {
            const isTarget = activeEscort?.target_poi_id === poi.id;
            const isLoading = loadingPoiId === poi.id;
            const storePromos = promotions.filter(p => p.store_id === poi.id || p.store_name?.toLowerCase() === poi.name.toLowerCase());

            return (
              <div
                key={poi.id}
                className="card-clean hover-elevate"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '14px',
                  borderRadius: '14px',
                  padding: '18px',
                  border: isTarget ? '2px solid #2563EB' : '1px solid var(--border-light)',
                  background: isTarget ? '#F0FDF4' : '#FFFFFF',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <span style={{ fontSize: '32px' }}>{STORE_EMOJIS[poi.id] || '🏪'}</span>
                    <span className="brand-badge" style={{ background: '#F1F5F9', color: '#475569', fontSize: '0.72rem' }}>
                      <MapPin size={11} style={{ marginRight: '2px', verticalAlign: '-1px' }} /> Tầng 1
                    </span>
                  </div>

                  <h3 style={{ fontSize: '1.12rem', fontWeight: 800, color: '#0F172A', marginBottom: '6px' }}>
                    {poi.name}
                  </h3>
                  <p style={{ fontSize: '0.86rem', color: '#64748B', lineHeight: '1.45', margin: '0 0 10px 0' }}>
                    {poi.description}
                  </p>

                  {/* Active Promo Tag if present */}
                  {storePromos.length > 0 && (
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: '#FEF2F2', color: '#DC2626', border: '1px solid #FECACA', padding: '3px 8px', borderRadius: '6px', fontSize: '0.74rem', fontWeight: 700 }}>
                      <Tag size={12} /> Có {storePromos.length} ưu đãi hôm nay
                    </div>
                  )}
                </div>

                {/* Card Action Buttons */}
                <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
                  <button
                    onClick={() => setModalPoi(poi)}
                    style={{
                      flex: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '5px',
                      background: '#F1F5F9',
                      border: '1px solid #CBD5E1',
                      borderRadius: '8px',
                      padding: '8px 10px',
                      fontSize: '0.82rem',
                      fontWeight: 600,
                      color: '#334155',
                      cursor: 'pointer',
                    }}
                  >
                    <Info size={15} />
                    <span>Chi Tiết</span>
                  </button>

                  <button
                    className={isTarget ? 'btn-solid-emerald' : 'btn-solid-blue'}
                    style={{ flex: 1.4, padding: '8px 10px', fontSize: '0.82rem' }}
                    onClick={() => handleEscort(poi)}
                    disabled={isTarget || isLoading}
                  >
                    <Navigation size={15} />
                    <span>{isTarget ? 'Đang Dẫn' : (isLoading ? 'Đang gửi...' : 'Chỉ Đường')}</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="card-clean" style={{ padding: '40px 20px', textAlign: 'center', color: '#64748B' }}>
          <p style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 8px 0' }}>Không tìm thấy gian hàng phù hợp</p>
          <p style={{ fontSize: '0.85rem', margin: 0 }}>Vui lòng thử tìm kiếm bằng từ khóa khác hoặc chọn danh mục "Tất Cả".</p>
        </div>
      )}

      {/* Store Detail Modal */}
      <StoreDetailModal
        store={modalPoi}
        promotions={promotions}
        isOpen={!!modalPoi}
        onClose={() => setModalPoi(null)}
        onNavigateToMap={(poiId) => {
          setModalPoi(null);
          if (onNavigateToMap) onNavigateToMap(poiId);
        }}
        onAskAssistant={(storeName) => {
          setModalPoi(null);
          if (onAskAssistant) onAskAssistant(storeName);
        }}
      />

    </div>
  );
};
