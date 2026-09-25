import React, { useState } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { PointOfInterest } from '../../types/protocol';
import { Search, Navigation } from 'lucide-react';

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

export const MallDirectoryTab: React.FC = () => {
  const { pois, pairedRobot, activeEscort } = useRobotStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loadingPoiId, setLoadingPoiId] = useState<string | null>(null);

  const customerPois = pois.filter(p => !p.is_staff_only);

  const filteredPois = customerPois.filter(poi => {
    const matchCat = selectedCategory === 'all' || poi.category === selectedCategory;
    const matchSearch =
      poi.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      poi.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchCat && matchSearch;
  });

  const handleEscort = async (poi: PointOfInterest) => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    setLoadingPoiId(poi.id);
    try {
      const res = await RobotApi.requestEscort(host, port, poi.id);
      if (res.success && res.task) {
        updateGlobalState(() => ({ activeEscort: res.task }));
        alert(`🎉 Robot đã nhận lệnh và bắt đầu dẫn đường đến: ${res.task.target_name}!`);
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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Search & Filter Header Bar */}
      <div className="card-clean" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          
          <div className="quick-search-box">
            <Search size={20} />
            <input
              type="text"
              className="quick-search-input"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tìm kiếm theo tên cửa hàng, món ăn, dịch vụ..."
            />
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

      {/* Store Directory Cards Grid */}
      <div className="delivery-orders-grid">
        {filteredPois.map(poi => {
          const isTarget = activeEscort?.target_poi_id === poi.id;
          const isLoading = loadingPoiId === poi.id;

          return (
            <div
              key={poi.id}
              className="card-clean"
              style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '14px',
                border: isTarget ? '2px solid #2563EB' : '1px solid var(--border-light)',
                background: isTarget ? '#F0FDF4' : '#FFFFFF',
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span style={{ fontSize: '32px' }}>{STORE_EMOJIS[poi.id] || '🏪'}</span>
                  <span className="brand-badge" style={{ background: '#F1F5F9', color: '#475569' }}>
                    Tầng 1
                  </span>
                </div>

                <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0F172A', marginBottom: '4px' }}>
                  {poi.name}
                </h3>
                <p style={{ fontSize: '0.88rem', color: '#64748B', lineHeight: '1.4' }}>
                  {poi.description}
                </p>
              </div>

              <button
                className={isTarget ? 'btn-solid-emerald' : 'btn-solid-blue'}
                style={{ width: '100%' }}
                onClick={() => handleEscort(poi)}
                disabled={isTarget || isLoading}
              >
                <Navigation size={16} />
                <span>
                  {isTarget ? 'ĐANG DẪN ĐƯỜNG TỚI ĐÂY' : (isLoading ? 'Đang gửi lệnh...' : 'DẪN TÔI ĐẾN ĐÂY 👉')}
                </span>
              </button>
            </div>
          );
        })}
      </div>

    </div>
  );
};
