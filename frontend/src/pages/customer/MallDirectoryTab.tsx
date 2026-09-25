import React, { useState } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { PointOfInterest } from '../../types/protocol';
import { Search, Navigation, Coffee, ShoppingBag, Film, Info, Sparkles } from 'lucide-react';

export const MallDirectoryTab: React.FC = () => {
  const { pois, pairedRobot, activeEscort } = useRobotStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const customerPois = pois.filter(p => !p.is_staff_only);

  const filteredPois = customerPois.filter(poi => {
    const matchCat = selectedCategory === 'all' || poi.category === selectedCategory;
    const matchSearch =
      poi.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      poi.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchCat && matchSearch;
  });

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'food':
        return <Coffee size={20} color="#EA580C" />;
      case 'fashion':
        return <ShoppingBag size={20} color="#DB2777" />;
      case 'entertainment':
        return <Film size={20} color="#7C3AED" />;
      default:
        return <Info size={20} color="#2563EB" />;
    }
  };

  const handleEscort = async (poi: PointOfInterest) => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    try {
      const res = await RobotApi.requestEscort(host, port, poi.id);
      if (res.success && res.task) {
        updateGlobalState(() => ({ activeEscort: res.task }));
        alert(`Robot đã bắt đầu dẫn đường đến: ${res.task.target_name}!`);
      }
    } catch (e: any) {
      alert(`Lỗi: ${e.message}`);
    }
  };

  return (
    <div className="tab-pane active">
      <div className="directory-container">
        
        {/* Search & Filter Header */}
        <div className="card directory-search-card">
          <div className="search-bar-wrapper">
            <Search size={20} color="#64748B" />
            <input
              type="text"
              className="directory-search-input"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tìm kiếm gian hàng, nhà hàng, rạp phim, khu vệ sinh..."
            />
          </div>

          <div className="category-filters">
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
        </div>

        {/* Directory Cards Grid */}
        <div className="directory-grid">
          {filteredPois.map(poi => {
            const isTarget = activeEscort?.target_poi_id === poi.id;
            return (
              <div key={poi.id} className={`directory-card ${isTarget ? 'active-target-card' : ''}`}>
                <div className="dir-card-top">
                  <div className="dir-icon-box">
                    {getCategoryIcon(poi.category)}
                  </div>
                  <div className="dir-badges">
                    <span className="floor-badge">Sảnh Chính T1</span>
                    <span className="cat-badge">{poi.category.toUpperCase()}</span>
                  </div>
                </div>

                <h3 className="dir-name">{poi.name}</h3>
                <p className="dir-desc">{poi.description}</p>

                <button
                  className="btn-primary btn-block btn-dir-escort"
                  onClick={() => handleEscort(poi)}
                  disabled={isTarget}
                >
                  <Navigation size={15} style={{ display: 'inline', marginRight: 6 }} />
                  {isTarget ? 'ROBOT ĐANG DẪN ĐƯỜNG' : 'ROBOT DẪN TÔI ĐẾN ĐÂY'}
                </button>
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
};
