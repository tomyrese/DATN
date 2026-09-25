import React, { useState, useEffect } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { DeliveryOrder } from '../../types/protocol';
import { 
  Package, 
  Plus, 
  RefreshCw, 
  CheckCircle2, 
  Clock, 
  Truck, 
  MapPin, 
  X, 
  ArrowRight, 
  Send,
  AlertCircle,
  Sparkles,
  Check
} from 'lucide-react';

export const DeliveryOrdersTab: React.FC = () => {
  const { deliveryOrders, pois, pairedRobot } = useRobotStore();
  const [activeSubTab, setActiveSubTab] = useState<'active' | 'queue' | 'history'>('active');
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const [creatorName, setCreatorName] = useState('Nhân viên quầy');
  const [pickupId, setPickupId] = useState(pois[0]?.id || 'poi_highlands');
  const [dropoffId, setDropoffId] = useState(pois[1]?.id || 'poi_reception');
  const [itemDesc, setItemDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const fetchOrders = async () => {
    setRefreshing(true);
    try {
      const host = pairedRobot?.host || '';
      const port = pairedRobot?.port || 0;
      const orders = await RobotApi.getDeliveryOrders(host, port);
      if (orders) {
        updateGlobalState(() => ({ deliveryOrders: orders }));
      }
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchOrders();
    const interval = setInterval(fetchOrders, 3000);
    return () => clearInterval(interval);
  }, [pairedRobot]);

  // Categorize orders
  const activeOrders = deliveryOrders.filter(o => 
    ['MOVING_TO_PICKUP', 'ARRIVED_AT_PICKUP', 'DELIVERING', 'ARRIVED_AT_DROPOFF'].includes(o.status)
  );
  const queueOrders = deliveryOrders.filter(o => o.status === 'PENDING');
  const historyOrders = deliveryOrders.filter(o => ['COMPLETED', 'CANCELLED'].includes(o.status));

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pickupId || !dropoffId) {
      alert('Vui lòng chọn điểm lấy và điểm giao.');
      return;
    }
    if (pickupId === dropoffId) {
      alert('Điểm lấy và điểm giao phải khác nhau.');
      return;
    }

    setLoading(true);
    try {
      const host = pairedRobot?.host || '';
      const port = pairedRobot?.port || 0;
      const res = await RobotApi.createDeliveryOrder(
        host,
        port,
        {
          creatorName: creatorName.trim() || 'Nhân viên',
          pickupPoiId: pickupId,
          dropoffPoiId: dropoffId,
          itemDescription: itemDesc.trim() || 'Kiện hàng đồ uống / tài liệu',
        },
        pairedRobot?.token
      );

      if (res.success && res.order) {
        updateGlobalState(prev => ({
          deliveryOrders: [res.order!, ...prev.deliveryOrders],
        }));
        setIsModalOpen(false);
        setItemDesc('');
        showToast('🎉 Đã tạo đơn giao hàng thành công!');
        fetchOrders();
      } else {
        alert(res.message || 'Không thể tạo đơn hàng.');
      }
    } catch (err: any) {
      alert(`Lỗi kết nối: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (orderId: string, nextStatus: string, progress: number) => {
    try {
      const host = pairedRobot?.host || '';
      const port = pairedRobot?.port || 0;
      const ok = await RobotApi.updateDeliveryOrderStatus(
        host,
        port,
        orderId,
        nextStatus,
        progress,
        pairedRobot?.token
      );
      if (ok) {
        showToast('✅ Đã cập nhật trạng thái đơn hàng!');
        fetchOrders();
      }
    } catch (err: any) {
      alert(`Lỗi cập nhật: ${err.message}`);
    }
  };

  const handleCancelOrder = async (orderId: string) => {
    if (!confirm('Bạn có chắc muốn hủy đơn giao hàng này không?')) return;
    await handleUpdateStatus(orderId, 'CANCELLED', 0);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING':
        return <span className="badge-status-clean pending">⏳ Hàng Đợi Điều Phối</span>;
      case 'MOVING_TO_PICKUP':
        return <span className="badge-status-clean delivering">🚚 Đang Đến Lấy Hàng</span>;
      case 'ARRIVED_AT_PICKUP':
        return <span className="badge-status-clean completed">📦 Đã Đến Điểm Lấy</span>;
      case 'DELIVERING':
        return <span className="badge-status-clean delivering">🚀 Đang Giao Đến Đích</span>;
      case 'ARRIVED_AT_DROPOFF':
        return <span className="badge-status-clean completed">📍 Đã Đến Điểm Giao</span>;
      case 'COMPLETED':
        return <span className="badge-status-clean completed">✅ Đã Giao Thành Công</span>;
      case 'CANCELLED':
        return <span className="badge-status-clean error">❌ Đã Hủy</span>;
      default:
        return <span className="badge-status-clean">{status}</span>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '1000px', margin: '0 auto', width: '100%' }}>
      
      {/* Toast Notification */}
      {toastMessage && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          zIndex: 9999,
          background: '#0F172A',
          color: '#F8FAFC',
          padding: '12px 20px',
          borderRadius: '12px',
          boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontWeight: 600,
          fontSize: '0.9rem'
        }}>
          <Sparkles size={18} color="#38BDF8" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Main Action Header */}
      <div className="card-clean" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0F172A', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Truck size={22} color="#2563EB" />
              GIAO HÀNG NỘI BỘ TTTM
            </h2>
            <p style={{ fontSize: '0.85rem', color: '#64748B', margin: '4px 0 0 0' }}>
              Hệ thống tự động vận chuyển hàng hóa, đồ ăn & tài liệu giữa các quầy
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button 
              className="btn-outline" 
              onClick={fetchOrders} 
              disabled={refreshing}
              title="Làm mới dữ liệu"
              style={{ padding: '8px 14px' }}
            >
              <RefreshCw size={16} className={refreshing ? 'spin-pulse' : ''} />
              <span>Làm mới</span>
            </button>
            <button 
              className="btn-solid-blue" 
              onClick={() => setIsModalOpen(true)}
              style={{ padding: '8px 18px', fontWeight: 700 }}
            >
              <Plus size={18} />
              <span>Tạo Đơn Giao</span>
            </button>
          </div>
        </div>

        {/* Sub Navigation Tabs */}
        <div style={{ display: 'flex', gap: '8px', marginTop: '16px', borderTop: '1px solid #F1F5F9', paddingTop: '12px' }}>
          <button
            onClick={() => setActiveSubTab('active')}
            style={{
              flex: 1,
              padding: '10px 12px',
              borderRadius: '10px',
              border: 'none',
              background: activeSubTab === 'active' ? '#EFF6FF' : 'transparent',
              color: activeSubTab === 'active' ? '#1D4ED8' : '#64748B',
              fontWeight: 700,
              fontSize: '0.9rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              transition: 'all 0.15s ease'
            }}
          >
            <Truck size={16} />
            <span>Đang Thực Hiện ({activeOrders.length})</span>
          </button>

          <button
            onClick={() => setActiveSubTab('queue')}
            style={{
              flex: 1,
              padding: '10px 12px',
              borderRadius: '10px',
              border: 'none',
              background: activeSubTab === 'queue' ? '#EFF6FF' : 'transparent',
              color: activeSubTab === 'queue' ? '#1D4ED8' : '#64748B',
              fontWeight: 700,
              fontSize: '0.9rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              transition: 'all 0.15s ease'
            }}
          >
            <Clock size={16} />
            <span>Hàng Chờ ({queueOrders.length})</span>
          </button>

          <button
            onClick={() => setActiveSubTab('history')}
            style={{
              flex: 1,
              padding: '10px 12px',
              borderRadius: '10px',
              border: 'none',
              background: activeSubTab === 'history' ? '#EFF6FF' : 'transparent',
              color: activeSubTab === 'history' ? '#1D4ED8' : '#64748B',
              fontWeight: 700,
              fontSize: '0.9rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              transition: 'all 0.15s ease'
            }}
          >
            <CheckCircle2 size={16} />
            <span>Lịch Sử ({historyOrders.length})</span>
          </button>
        </div>
      </div>

      {/* TAB 1: ACTIVE ORDER (ĐANG THỰC HIỆN) */}
      {activeSubTab === 'active' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {activeOrders.length === 0 ? (
            <div className="card-clean" style={{ textAlign: 'center', padding: '40px 20px' }}>
              <Package size={48} color="#94A3B8" style={{ marginBottom: '12px' }} />
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#334155' }}>Hiện Không Có Đơn Đang Giao</h3>
              <p style={{ fontSize: '0.85rem', color: '#94A3B8', marginTop: '4px' }}>
                Robot đang rảnh rỗi. Hãy bấm nút "Tạo Đơn Giao" để phân công nhiệm vụ mới.
              </p>
              <button 
                className="btn-solid-blue" 
                onClick={() => setIsModalOpen(true)}
                style={{ marginTop: '16px', padding: '10px 20px', margin: '16px auto 0' }}
              >
                <Plus size={16} />
                <span>Tạo Đơn Ngay</span>
              </button>
            </div>
          ) : (
            activeOrders.map(order => (
              <div key={order.order_id} className="card-clean" style={{ padding: '20px', border: '2px solid #3B82F6' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '0.82rem', fontWeight: 800, background: '#DBEAFE', color: '#1E40AF', padding: '4px 10px', borderRadius: '6px' }}>
                      #{order.order_id}
                    </span>
                    <span style={{ fontSize: '0.85rem', color: '#64748B' }}>
                      Tạo bởi: <strong>{order.creator_name}</strong>
                    </span>
                  </div>
                  {getStatusBadge(order.status)}
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0F172A', margin: 0 }}>
                    {order.item_description}
                  </h3>
                </div>

                {/* Pickup -> Dropoff Route Card */}
                <div style={{ background: '#F8FAFC', padding: '12px 16px', borderRadius: '12px', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#DBEAFE', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <MapPin size={18} color="#2563EB" />
                      </div>
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600 }}>ĐIỂM LẤY HÀNG</div>
                        <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0F172A' }}>{order.pickup_poi_name}</div>
                      </div>
                    </div>

                    <ArrowRight size={20} color="#94A3B8" />

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#D1FAE5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <MapPin size={18} color="#10B981" />
                      </div>
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600 }}>ĐIỂM GIAO ĐẾN</div>
                        <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0F172A' }}>{order.dropoff_poi_name}</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div style={{ marginBottom: '18px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', fontWeight: 700, color: '#475569', marginBottom: '6px' }}>
                    <span>Tiến độ vận chuyển</span>
                    <span>{order.current_progress}%</span>
                  </div>
                  <div style={{ width: '100%', height: '10px', background: '#E2E8F0', borderRadius: '5px', overflow: 'hidden' }}>
                    <div 
                      style={{ 
                        width: `${Math.max(5, order.current_progress)}%`, 
                        height: '100%', 
                        background: 'linear-gradient(90deg, #3B82F6, #10B981)', 
                        borderRadius: '5px',
                        transition: 'width 0.4s ease'
                      }} 
                    />
                  </div>
                </div>

                {/* 1-Touch Action Controls */}
                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                  {order.status === 'MOVING_TO_PICKUP' && (
                    <button
                      className="btn-solid-blue"
                      style={{ flex: 1, padding: '12px 18px', fontSize: '0.95rem', fontWeight: 700 }}
                      onClick={() => handleUpdateStatus(order.order_id, 'ARRIVED_AT_PICKUP', 100)}
                    >
                      📍 Đã Đến Điểm Lấy Hàng
                    </button>
                  )}

                  {order.status === 'ARRIVED_AT_PICKUP' && (
                    <button
                      className="btn-solid-emerald"
                      style={{ flex: 1, padding: '14px 18px', fontSize: '1rem', fontWeight: 800 }}
                      onClick={() => handleUpdateStatus(order.order_id, 'DELIVERING', 0)}
                    >
                      📦 Đã Xếp Hàng Lên Xe • Bắt Đầu Giao 🚀
                    </button>
                  )}

                  {order.status === 'DELIVERING' && (
                    <button
                      className="btn-solid-blue"
                      style={{ flex: 1, padding: '12px 18px', fontSize: '0.95rem', fontWeight: 700 }}
                      onClick={() => handleUpdateStatus(order.order_id, 'ARRIVED_AT_DROPOFF', 100)}
                    >
                      📍 Đã Đến Nơi Nhận Hàng
                    </button>
                  )}

                  {order.status === 'ARRIVED_AT_DROPOFF' && (
                    <button
                      className="btn-solid-emerald"
                      style={{ flex: 1, padding: '14px 18px', fontSize: '1rem', fontWeight: 800 }}
                      onClick={() => handleUpdateStatus(order.order_id, 'COMPLETED', 100)}
                    >
                      ✅ Đã Nhận Hàng Xong (Hoàn Tất Đơn)
                    </button>
                  )}

                  <button
                    className="btn-outline"
                    style={{ padding: '12px 18px', color: '#EF4444', borderColor: '#FECACA' }}
                    onClick={() => handleCancelOrder(order.order_id)}
                  >
                    Hủy Đơn
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* TAB 2: QUEUE (HÀNG ĐỢI ĐIỀU PHỐI) */}
      {activeSubTab === 'queue' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ background: '#EFF6FF', border: '1px solid #BFDBFE', padding: '12px 16px', borderRadius: '12px', fontSize: '0.85rem', color: '#1E40AF', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={18} />
            <span>Hệ thống FIFO: Robot sẽ tự động thực hiện các đơn trong hàng đợi này ngay khi đơn đang chạy hoàn tất.</span>
          </div>

          {queueOrders.length === 0 ? (
            <div className="card-clean" style={{ textAlign: 'center', padding: '36px 20px' }}>
              <Clock size={44} color="#94A3B8" style={{ marginBottom: '10px' }} />
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#334155' }}>Hàng Đợi Trống</h3>
              <p style={{ fontSize: '0.85rem', color: '#94A3B8', marginTop: '4px' }}>
                Không có đơn hàng nào đang chờ xử lý.
              </p>
            </div>
          ) : (
            queueOrders.map((order, index) => (
              <div key={order.order_id} className="order-card-clean">
                <div className="order-card-top">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ background: '#3B82F6', color: '#FFF', fontWeight: 800, fontSize: '0.8rem', padding: '2px 8px', borderRadius: '4px' }}>
                      Vị trí #{index + 1}
                    </span>
                    <span className="order-code">#{order.order_id}</span>
                  </div>
                  {getStatusBadge(order.status)}
                </div>

                <div>
                  <h4 style={{ fontSize: '0.98rem', fontWeight: 800, color: '#0F172A', margin: '0 0 4px 0' }}>
                    {order.item_description}
                  </h4>
                  <div style={{ fontSize: '0.8rem', color: '#64748B' }}>
                    Người tạo: {order.creator_name}
                  </div>
                </div>

                <div style={{ background: '#F8FAFC', padding: '10px 12px', borderRadius: '10px', fontSize: '0.85rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#334155', fontWeight: 600 }}>
                    <MapPin size={14} color="#2563EB" />
                    <span>Lấy tại: <strong>{order.pickup_poi_name}</strong></span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#334155', fontWeight: 600, marginTop: '4px' }}>
                    <ArrowRight size={14} color="#10B981" />
                    <span>Giao đến: <strong>{order.dropoff_poi_name}</strong></span>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
                  <button
                    className="btn-solid-blue"
                    style={{ flex: 1, padding: '8px 12px', fontSize: '0.85rem' }}
                    onClick={() => handleUpdateStatus(order.order_id, 'MOVING_TO_PICKUP', 0)}
                  >
                    🚀 Ưu Tiên Giao Ngay
                  </button>
                  <button
                    className="btn-outline"
                    style={{ padding: '8px 12px', color: '#EF4444', borderColor: '#FECACA' }}
                    onClick={() => handleCancelOrder(order.order_id)}
                  >
                    Hủy
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* TAB 3: HISTORY (LỊCH SỬ) */}
      {activeSubTab === 'history' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {historyOrders.length === 0 ? (
            <div className="card-clean" style={{ textAlign: 'center', padding: '36px 20px' }}>
              <CheckCircle2 size={44} color="#94A3B8" style={{ marginBottom: '10px' }} />
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#334155' }}>Chưa Có Lịch Sử</h3>
              <p style={{ fontSize: '0.85rem', color: '#94A3B8', marginTop: '4px' }}>
                Các đơn hàng sau khi hoàn tất hoặc hủy sẽ được lưu trữ tại đây.
              </p>
            </div>
          ) : (
            historyOrders.map(order => (
              <div key={order.order_id} className="order-card-clean" style={{ opacity: 0.9 }}>
                <div className="order-card-top">
                  <span className="order-code">#{order.order_id}</span>
                  {getStatusBadge(order.status)}
                </div>

                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0F172A', margin: '0 0 4px 0' }}>
                    {order.item_description}
                  </h4>
                  <div style={{ fontSize: '0.8rem', color: '#64748B' }}>
                    Người tạo: {order.creator_name} • {order.pickup_poi_name} ➔ {order.dropoff_poi_name}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* CREATE ORDER MODAL */}
      {isModalOpen && (
        <div className="modal-backdrop-clean" onClick={() => setIsModalOpen(false)}>
          <div className="modal-dialog-clean" onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#0F172A' }}>
                TẠO ĐƠN GIAO HÀNG MỚI
              </h3>
              <button className="btn-outline" style={{ padding: '6px', borderRadius: '50%' }} onClick={() => setIsModalOpen(false)}>
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateOrder} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '6px' }}>
                  Người tạo đơn (Tên / Quầy):
                </label>
                <input
                  type="text"
                  className="quick-search-input"
                  style={{ padding: '10px 14px' }}
                  value={creatorName}
                  onChange={e => setCreatorName(e.target.value)}
                  placeholder="VD: Quầy Lễ Tân, UNIQLO..."
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '6px' }}>
                  Tên món hàng / Ghi chú:
                </label>
                <input
                  type="text"
                  className="quick-search-input"
                  style={{ padding: '10px 14px' }}
                  value={itemDesc}
                  onChange={e => setItemDesc(e.target.value)}
                  placeholder="VD: 2 ly Cafe, Áo size L, Tài liệu..."
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '6px' }}>
                    Điểm lấy hàng:
                  </label>
                  <select
                    className="quick-search-input"
                    style={{ padding: '10px 12px' }}
                    value={pickupId}
                    onChange={e => setPickupId(e.target.value)}
                  >
                    {pois.map(p => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '6px' }}>
                    Điểm giao đến:
                  </label>
                  <select
                    className="quick-search-input"
                    style={{ padding: '10px 12px' }}
                    value={dropoffId}
                    onChange={e => setDropoffId(e.target.value)}
                  >
                    {pois.map(p => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '10px', marginTop: '12px' }}>
                <button type="button" className="btn-outline" style={{ flex: 1 }} onClick={() => setIsModalOpen(false)}>
                  Hủy
                </button>
                <button type="submit" className="btn-solid-blue" style={{ flex: 1.5, fontWeight: 700 }} disabled={loading}>
                  {loading ? 'Đang gửi...' : '🚀 Xác Nhận Giao Hàng'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
