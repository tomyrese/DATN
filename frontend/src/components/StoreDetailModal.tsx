import React, { useEffect } from 'react';
import { PointOfInterest, Promotion, MallStore } from '../types/protocol';
import { X, Navigation, Bot, Clock, Phone, MapPin, Tag, CheckCircle2 } from 'lucide-react';

interface StoreDetailModalProps {
  store: PointOfInterest | MallStore | null;
  promotions?: Promotion[];
  isOpen: boolean;
  onClose: () => void;
  onNavigateToMap: (poiId: string) => void;
  onAskAssistant: (storeName: string) => void;
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

export const StoreDetailModal: React.FC<StoreDetailModalProps> = ({
  store,
  promotions = [],
  isOpen,
  onClose,
  onNavigateToMap,
  onAskAssistant,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !store) return null;

  const storeId = store.id;
  const storeName = store.name;
  const description = store.description || 'Không có mô tả chi tiết.';
  const emoji = STORE_EMOJIS[storeId] || '🏪';

  // Find active promotions for this store
  const storePromos = promotions.filter(p => p.store_id === storeId || p.store_name?.toLowerCase() === storeName.toLowerCase());

  // Category labels
  const categoryLabels: Record<string, string> = {
    food: 'Ẩm thực & Nhà hàng',
    fashion: 'Thời trang & Phụ kiện',
    entertainment: 'Giải trí & Rạp chiếu',
    utility: 'Tiện ích công cộng',
    staff: 'Khu vực nội bộ',
  };

  const categoryName = categoryLabels[store.category] || store.category || 'Gian hàng';

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.65)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        padding: '16px',
      }}
    >
      <div
        className="modal-card"
        onClick={(e) => e.stopPropagation()}
        style={{
          background: '#FFFFFF',
          borderRadius: '16px',
          width: '100%',
          maxWidth: '520px',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          border: '1px solid #E2E8F0',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          maxHeight: '90vh',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '20px 24px 16px',
            borderBottom: '1px solid #F1F5F9',
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            background: 'linear-gradient(to right, #F8FAFC, #FFFFFF)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div
              style={{
                width: '52px',
                height: '52px',
                borderRadius: '12px',
                background: '#EFF6FF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '28px',
                border: '1px solid #DBEAFE',
                flexShrink: 0,
              }}
            >
              {emoji}
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <span
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: '#2563EB',
                    background: '#DBEAFE',
                    padding: '2px 8px',
                    borderRadius: '6px',
                  }}
                >
                  {categoryName}
                </span>
                <span
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: '#64748B',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '3px',
                  }}
                >
                  <MapPin size={12} /> Tầng 1 (Khu Trung Tâm)
                </span>
              </div>
              <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800, color: '#0F172A' }}>
                {storeName}
              </h2>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: '#F1F5F9',
              border: 'none',
              borderRadius: '8px',
              padding: '8px',
              cursor: 'pointer',
              color: '#64748B',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '20px 24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          {/* Store description */}
          <div>
            <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '6px', letterSpacing: '0.5px' }}>
              Giới thiệu
            </h4>
            <p style={{ margin: 0, fontSize: '0.92rem', color: '#334155', lineHeight: '1.5' }}>
              {description}
            </p>
          </div>

          {/* Quick info row */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '12px',
              background: '#F8FAFC',
              padding: '12px 14px',
              borderRadius: '10px',
              border: '1px solid #E2E8F0',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={16} color="#64748B" />
              <div>
                <div style={{ fontSize: '0.7rem', color: '#64748B', fontWeight: 600 }}>Giờ mở cửa</div>
                <div style={{ fontSize: '0.82rem', color: '#0F172A', fontWeight: 700 }}>09:30 - 22:00</div>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Phone size={16} color="#64748B" />
              <div>
                <div style={{ fontSize: '0.7rem', color: '#64748B', fontWeight: 600 }}>Hotline hỗ trợ</div>
                <div style={{ fontSize: '0.82rem', color: '#0F172A', fontWeight: 700 }}>1900 6868</div>
              </div>
            </div>
          </div>

          {/* Active Promotions if any */}
          {storePromos.length > 0 && (
            <div>
              <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#DC2626', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.5px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Tag size={14} /> Ưu đãi & Khuyến mãi hiện hành ({storePromos.length})
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {storePromos.map((promo) => (
                  <div
                    key={promo.id}
                    style={{
                      border: '1.5px dashed #FCA5A5',
                      background: '#FEF2F2',
                      borderRadius: '10px',
                      padding: '10px 14px',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 800, fontSize: '0.92rem', color: '#991B1B' }}>
                        {promo.title}
                      </span>
                      {promo.discount_percent > 0 && (
                        <span style={{ background: '#DC2626', color: '#FFFFFF', padding: '2px 6px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
                          -{promo.discount_percent}%
                        </span>
                      )}
                    </div>
                    <p style={{ margin: 0, fontSize: '0.82rem', color: '#4B5563' }}>
                      {promo.description}
                    </p>
                    {promo.promo_code && (
                      <div style={{ marginTop: '6px', fontSize: '0.78rem', color: '#7F1D1D', fontWeight: 600 }}>
                        Mã giảm giá: <code style={{ background: '#FEE2E2', padding: '2px 6px', borderRadius: '4px' }}>{promo.promo_code}</code>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Operational status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', color: '#16A34A', fontWeight: 600 }}>
            <CheckCircle2 size={16} /> Gian hàng đang mở cửa đón khách tại Tầng 1
          </div>

        </div>

        {/* Footer Actions */}
        <div
          style={{
            padding: '14px 24px',
            borderTop: '1px solid #F1F5F9',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
            background: '#F8FAFC',
          }}
        >
          <button
            onClick={() => {
              onClose();
              onNavigateToMap(storeId);
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              background: '#2563EB',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '10px',
              padding: '12px 18px',
              fontSize: '0.95rem',
              fontWeight: 700,
              cursor: 'pointer',
              boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.2)',
            }}
          >
            <Navigation size={18} />
            <span>Chỉ Đường Trên Bản Đồ</span>
          </button>

          <button
            onClick={() => {
              onClose();
              onAskAssistant(storeName);
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              background: '#FFFFFF',
              color: '#1E293B',
              border: '1.5px solid #CBD5E1',
              borderRadius: '10px',
              padding: '10px 16px',
              fontSize: '0.88rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <Bot size={16} color="#2563EB" />
            <span>Hỏi Trợ Lý Về Địa Điểm Này</span>
          </button>
        </div>
      </div>
    </div>
  );
};
