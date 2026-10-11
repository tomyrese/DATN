import React, { useState, useEffect } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { Promotion } from '../../types/protocol';
import { Tag, Plus, Trash2, Calendar, Percent, Store, CheckCircle, Clock } from 'lucide-react';

export const PromotionsTab: React.FC = () => {
  const { pairedRobot, currentUser, userRole, pois } = useRobotStore();
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form states
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [storeId, setStoreId] = useState('');
  const [discountPercent, setDiscountPercent] = useState<number>(15);
  const [promoCode, setPromoCode] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  // Filter stores user can create promotions for
  const availableStores = pois.filter(p => {
    if (userRole === 'admin') return true;
    return currentUser?.assignedStoreIds?.includes(p.id);
  });

  const loadPromotions = async () => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    setLoading(true);
    try {
      // If staff with assigned stores, can query their primary store or all
      const storeFilter = userRole === 'staff' && currentUser?.assignedStoreIds?.length === 1
        ? currentUser.assignedStoreIds[0]
        : undefined;
      const data = await RobotApi.getPromotions(host, port, storeFilter);
      setPromotions(data);
      updateGlobalState(() => ({ promotions: data }));
    } catch (e) {
      console.warn('Failed to load promotions:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPromotions();
    if (availableStores.length > 0 && !storeId) {
      setStoreId(availableStores[0].id);
    }
  }, [currentUser]);

  const handleCreatePromo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !storeId) {
      setFormError('Vui lòng nhập tên chương trình và chọn gian hàng');
      return;
    }
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    const token = currentUser?.token || pairedRobot?.token || '';

    try {
      const res = await RobotApi.createPromotion(
        host,
        port,
        {
          storeId,
          title: title.trim(),
          description: description.trim(),
          discountPercent: Number(discountPercent),
          promoCode: promoCode.trim().toUpperCase() || undefined,
        },
        token
      );
      if (res.success) {
        setTitle('');
        setDescription('');
        setPromoCode('');
        setShowAddModal(false);
        setFormError(null);
        await loadPromotions();
      } else {
        setFormError(res.message || 'Không thể tạo khuyến mãi');
      }
    } catch (err: any) {
      setFormError(`Lỗi: ${err.message}`);
    }
  };

  const handleDeletePromo = async (promoId: string) => {
    if (!confirm('Bạn có chắc chắn muốn xóa khuyến mãi này?')) return;
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    const token = currentUser?.token || pairedRobot?.token || '';
    const ok = await RobotApi.deletePromotion(host, port, promoId, token);
    if (ok) {
      await loadPromotions();
    } else {
      alert('Không thể xóa khuyến mãi');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', width: '100%', maxWidth: '900px', margin: '0 auto' }}>
      
      {/* Header bar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: '#FFFFFF',
        padding: '16px 20px',
        borderRadius: '14px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
      }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Tag size={20} color="#2563EB" />
            <span>QUẢN LÝ CHƯƠNG TRÌNH KHUYẾN MÃI</span>
          </h2>
          <p style={{ margin: '4px 0 0', fontSize: '0.78rem', color: '#64748B' }}>
            {userRole === 'admin'
              ? 'Quản trị viên: Quản lý khuyến mãi toàn trung tâm thương mại'
              : `Nhân viên: Quản lý ưu đãi thuộc gian hàng được phân công (${currentUser?.assignedStoreIds?.join(', ') || 'Chưa gán'})`}
          </p>
        </div>

        <button
          onClick={() => {
            setFormError(null);
            setShowAddModal(true);
          }}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: '#2563EB',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '8px',
            padding: '9px 14px',
            fontWeight: 700,
            fontSize: '0.82rem',
            cursor: 'pointer'
          }}
        >
          <Plus size={16} />
          <span>Tạo Khuyến Mãi</span>
        </button>
      </div>

      {/* Promotion List */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
        {promotions.length === 0 ? (
          <div style={{
            gridColumn: '1 / -1',
            padding: '40px 20px',
            textAlign: 'center',
            background: '#FFFFFF',
            borderRadius: '14px',
            color: '#94A3B8'
          }}>
            <Tag size={40} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
            <p style={{ fontSize: '0.9rem', fontWeight: 600 }}>Chưa có chương trình khuyến mãi nào</p>
            <p style={{ fontSize: '0.78rem' }}>Nhấn nút "Tạo Khuyến Mãi" ở trên để phát hành ưu đãi mới đến khách tham quan</p>
          </div>
        ) : (
          promotions.map(promo => (
            <div
              key={promo.id}
              style={{
                background: '#FFFFFF',
                borderRadius: '14px',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                boxShadow: '0 2px 4px rgba(0,0,0,0.04)',
                border: '1px solid #E2E8F0',
                position: 'relative'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span style={{
                    background: '#EFF6FF',
                    color: '#1D4ED8',
                    padding: '4px 8px',
                    borderRadius: '6px',
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    <Store size={12} />
                    <span>{promo.store_name || promo.store_id}</span>
                  </span>

                  <span style={{
                    background: '#DCFCE7',
                    color: '#15803D',
                    padding: '4px 8px',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    fontWeight: 800,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '2px'
                  }}>
                    <Percent size={12} />
                    <span>{promo.discount_percent}%</span>
                  </span>
                </div>

                <h3 style={{ margin: '0 0 6px', fontSize: '0.95rem', fontWeight: 800, color: '#0F172A' }}>
                  {promo.title}
                </h3>
                <p style={{ margin: '0 0 10px', fontSize: '0.78rem', color: '#64748B', lineHeight: 1.4 }}>
                  {promo.description || 'Ưu đãi đặc biệt áp dụng trực tiếp tại quầy thanh toán.'}
                </p>

                {promo.promo_code && (
                  <div style={{
                    display: 'inline-block',
                    background: '#FEF3C7',
                    border: '1px dashed #F59E0B',
                    padding: '3px 8px',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    fontWeight: 800,
                    color: '#B45309',
                    marginBottom: '10px'
                  }}>
                    MÃ: {promo.promo_code}
                  </div>
                )}
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingTop: '10px',
                borderTop: '1px solid #F1F5F9'
              }}>
                <span style={{ fontSize: '0.7rem', color: '#94A3B8', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Clock size={12} />
                  <span>Đang hiệu lực</span>
                </span>

                <button
                  onClick={() => handleDeletePromo(promo.id)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#EF4444',
                    cursor: 'pointer',
                    padding: '4px 6px',
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '0.75rem',
                    fontWeight: 600
                  }}
                >
                  <Trash2 size={13} />
                  <span>Xóa</span>
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal Tạo Khuyến Mãi */}
      {showAddModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(15, 23, 42, 0.65)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '16px'
        }}>
          <div style={{
            background: '#FFFFFF',
            borderRadius: '16px',
            width: '100%',
            maxWidth: '460px',
            padding: '20px',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2)'
          }}>
            <h3 style={{ margin: '0 0 14px', fontSize: '1rem', fontWeight: 800, color: '#0F172A' }}>
              TẠO CHƯƠNG TRÌNH KHUYẾN MÃI MỚI
            </h3>

            {formError && (
              <div style={{
                background: '#FEE2E2',
                color: '#DC2626',
                padding: '8px 12px',
                borderRadius: '8px',
                fontSize: '0.8rem',
                marginBottom: '12px'
              }}>
                {formError}
              </div>
            )}

            <form onSubmit={handleCreatePromo} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                  Gian Hàng Áp Dụng
                </label>
                <select
                  value={storeId}
                  onChange={(e) => setStoreId(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: '8px',
                    border: '1.5px solid #CBD5E1',
                    fontSize: '0.82rem'
                  }}
                >
                  {availableStores.map(store => (
                    <option key={store.id} value={store.id}>
                      {store.name} ({store.id})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                  Tên Khuyến Mãi
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Ví dụ: Giảm 20% BST Thu Đông Mới"
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: '8px',
                    border: '1.5px solid #CBD5E1',
                    fontSize: '0.82rem'
                  }}
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                    % Giảm Giá
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={discountPercent}
                    onChange={(e) => setDiscountPercent(Number(e.target.value))}
                    style={{
                      width: '100%',
                      padding: '8px 10px',
                      borderRadius: '8px',
                      border: '1.5px solid #CBD5E1',
                      fontSize: '0.82rem'
                    }}
                    required
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                    Mã Giảm Giá (Tùy chọn)
                  </label>
                  <input
                    type="text"
                    value={promoCode}
                    onChange={(e) => setPromoCode(e.target.value)}
                    placeholder="AUTUMN20"
                    style={{
                      width: '100%',
                      padding: '8px 10px',
                      borderRadius: '8px',
                      border: '1.5px solid #CBD5E1',
                      fontSize: '0.82rem'
                    }}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                  Mô Tả Chi Tiết
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Nhập điều kiện áp dụng hoặc thời hạn..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: '8px',
                    border: '1.5px solid #CBD5E1',
                    fontSize: '0.82rem',
                    fontFamily: 'inherit'
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '8px' }}>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  style={{
                    padding: '9px 14px',
                    background: '#F1F5F9',
                    border: 'none',
                    borderRadius: '8px',
                    fontWeight: 600,
                    fontSize: '0.82rem',
                    cursor: 'pointer'
                  }}
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '9px 16px',
                    background: '#2563EB',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '8px',
                    fontWeight: 700,
                    fontSize: '0.82rem',
                    cursor: 'pointer'
                  }}
                >
                  Xác Nhận Tạo
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
