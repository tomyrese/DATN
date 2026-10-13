import React, { useState, useEffect } from 'react';
import { useRobotStore } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { Promotion } from '../../types/protocol';
import { Tag, Navigation, Copy, Check, Clock, Sparkles } from 'lucide-react';

interface GuestPromotionsTabProps {
  onNavigateToMap?: (poiId: string) => void;
}

export const GuestPromotionsTab: React.FC<GuestPromotionsTabProps> = ({ onNavigateToMap }) => {
  const { pairedRobot, pois } = useRobotStore();
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [loading, setLoading] = useState(true);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  useEffect(() => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    RobotApi.getPromotions(host, port)
      .then(promos => {
        setPromotions(promos || []);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, [pairedRobot]);

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const handleNavigateStore = (storeId: string, storeName?: string) => {
    if (!onNavigateToMap) return;
    // Find matching POI ID
    const matchPoi = pois.find(
      p => p.id === storeId || (storeName && p.name.toLowerCase() === storeName.toLowerCase())
    );
    if (matchPoi) {
      onNavigateToMap(matchPoi.id);
    } else {
      onNavigateToMap(storeId);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '1000px', margin: '0 auto', width: '100%' }}>
      
      {/* Header Banner */}
      <div
        className="card-clean"
        style={{
          padding: '24px 28px',
          background: 'linear-gradient(135deg, #FEF2F2 0%, #FFFFFF 100%)',
          border: '1px solid #FECACA',
          borderRadius: '16px',
        }}
      >
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: '#FEE2E2', color: '#DC2626', padding: '4px 10px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 700, marginBottom: '8px' }}>
          <Sparkles size={14} />
          <span>ƯU ĐÃI & KHUYẾN MÃI TẠI TTTM</span>
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#0F172A', margin: '0 0 6px 0' }}>
          Chương Trình Khuyến Mãi Đang Hiệu Lực
        </h2>
        <p style={{ margin: 0, fontSize: '0.92rem', color: '#475569', lineHeight: 1.4 }}>
          Khám phá các ưu đãi mua sắm và ẩm thực hấp dẫn từ các gian hàng tại Tầng 1 hôm nay.
        </p>
      </div>

      {/* Promotions List Grid */}
      {loading ? (
        <div className="card-clean" style={{ padding: '40px', textAlign: 'center', color: '#64748B' }}>
          Đang tải thông tin ưu đãi từ hệ thống...
        </div>
      ) : promotions.length > 0 ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))', gap: '16px' }}>
          {promotions.map(promo => (
            <div
              key={promo.id}
              className="card-clean hover-elevate"
              style={{
                borderRadius: '14px',
                padding: '20px',
                border: '1.5px solid #FEE2E2',
                background: '#FFFFFF',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '14px',
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      color: '#991B1B',
                      background: '#FEE2E2',
                      padding: '3px 8px',
                      borderRadius: '6px',
                    }}
                  >
                    {promo.store_name || 'Gian hàng'}
                  </span>
                  {promo.discount_percent > 0 && (
                    <span
                      style={{
                        background: '#DC2626',
                        color: '#FFFFFF',
                        padding: '3px 8px',
                        borderRadius: '6px',
                        fontSize: '0.8rem',
                        fontWeight: 800,
                      }}
                    >
                      GIẢM {promo.discount_percent}%
                    </span>
                  )}
                </div>

                <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#0F172A', margin: '0 0 6px 0' }}>
                  {promo.title}
                </h3>
                <p style={{ fontSize: '0.86rem', color: '#475569', lineHeight: 1.45, margin: '0 0 12px 0' }}>
                  {promo.description}
                </p>

                {promo.promo_code && (
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      background: '#FEF2F2',
                      border: '1px dashed #FCA5A5',
                      padding: '8px 12px',
                      borderRadius: '8px',
                    }}
                  >
                    <div style={{ fontSize: '0.8rem', color: '#991B1B' }}>
                      Mã ưu đãi: <strong style={{ fontSize: '0.9rem', color: '#7F1D1D' }}>{promo.promo_code}</strong>
                    </div>
                    <button
                      onClick={() => handleCopyCode(promo.promo_code!)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        background: '#FFFFFF',
                        border: '1px solid #FECACA',
                        borderRadius: '6px',
                        padding: '4px 8px',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        color: copiedCode === promo.promo_code ? '#16A34A' : '#991B1B',
                        cursor: 'pointer',
                      }}
                    >
                      {copiedCode === promo.promo_code ? (
                        <>
                          <Check size={12} /> Đã chép
                        </>
                      ) : (
                        <>
                          <Copy size={12} /> Sao chép
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <button
                className="btn-solid-blue"
                style={{ width: '100%', padding: '10px 14px', fontSize: '0.85rem' }}
                onClick={() => handleNavigateStore(promo.store_id, promo.store_name)}
              >
                <Navigation size={16} />
                <span>Chỉ Đường Đến Gian Hàng Này</span>
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="card-clean" style={{ padding: '40px 20px', textAlign: 'center', color: '#64748B' }}>
          <p style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 8px 0' }}>Chưa có chương trình ưu đãi nào</p>
          <p style={{ fontSize: '0.85rem', margin: 0 }}>Các ưu đãi mới sẽ được cập nhật liên tục từ các gian hàng tại TTTM.</p>
        </div>
      )}

    </div>
  );
};
