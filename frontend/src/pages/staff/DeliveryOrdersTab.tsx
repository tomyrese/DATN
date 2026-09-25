import React, { useState, useEffect } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { DeliveryOrder } from '../../types/protocol';
import { Package, Plus, RefreshCw, CheckCircle2, Clock, Truck, MapPin, X, ArrowRight } from 'lucide-react';

export const DeliveryOrdersTab: React.FC = () => {
  const { deliveryOrders, pois, pairedRobot } = useRobotStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [creatorName, setCreatorName] = useState('Nhân viên Quầy');
  const [pickupId, setPickupId] = useState(pois[0]?.id || 'poi_reception');
  const [dropoffId, setDropoffId] = useState(pois[1]?.id || 'poi_zara');
  const [itemDesc, setItemDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchOrders = async () => {
    if (!pairedRobot) return;
    setRefreshing(true);
    try {
      const orders = await RobotApi.getDeliveryOrders(pairedRobot.host, pairedRobot.port);
      if (orders) {
        updateGlobalState(() => ({ deliveryOrders: orders }));
      }
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchOrders();
    const interval = setInterval(fetchOrders, 4000);
    return () => clearInterval(interval);
  }, [pairedRobot]);

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pairedRobot) {
      alert('Vui lòng kết nối Robot trước khi tạo đơn.');
      return;
    }

    setLoading(true);
    try {
      const res = await RobotApi.createDeliveryOrder(
        pairedRobot.host,
        pairedRobot.port,
        pairedRobot.token,
        {
          creatorName,
          pickupPoiId: pickupId,
          dropoffPoiId: dropoffId,
          itemDescription: itemDesc || 'Kiện hàng đồ uống / tài liệu',
        }
      );

      if (res.success && res.order) {
        updateGlobalState(prev => ({
          deliveryOrders: [res.order!, ...prev.deliveryOrders],
        }));
        setIsModalOpen(false);
        setItemDesc('');
      } else {
        alert(res.message || 'Không thể tạo đơn hàng.');
      }
    } catch (err: any) {
      alert(`Lỗi: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (orderId: string, nextStatus: any, progress: number) => {
    if (!pairedRobot) return;
    try {
      const ok = await RobotApi.updateDeliveryOrderStatus(
        pairedRobot.host,
        pairedRobot.port,
        pairedRobot.token,
        orderId,
        nextStatus,
        progress
      );
      if (ok) {
        fetchOrders();
      }
    } catch (err: any) {
      alert(`Lỗi: ${err.message}`);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING':
        return <span className="badge-status-clean pending">⏳ Chờ Điều Phối</span>;
      case 'MOVING_TO_PICKUP':
        return <span className="badge-status-clean delivering">🚚 Đang Đến Lấy Hàng</span>;
      case 'ARRIVED_AT_PICKUP':
        return <span className="badge-status-clean completed">📦 Đã Đến Điểm Lấy</span>;
      case 'DELIVERING':
        return <span className="badge-status-clean delivering">🚀 Đang Giao Đến Đích</span>;
      case 'ARRIVED_AT_DROPOFF':
      case 'COMPLETED':
        return <span className="badge-status-clean completed">✅ Đã Giao Xong</span>;
      default:
        return <span className="badge-status-clean">{status}</span>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Top Header Card */}
      <div className="card-clean" style={{ padding: '18px 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800 }}>QUẢN LÝ GIAO HÀNG NỘI BỘ (ROBOT DELIVERY)</h2>
            <p style={{ fontSize: '0.88rem', color: '#64748B' }}>
              Tạo đơn và cử Robot tự động vận chuyển đồ ăn, đồ uống hoặc tài liệu giữa các quầy/gian hàng
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn-outline" onClick={fetchOrders} disabled={refreshing}>
              <RefreshCw size={16} className={refreshing ? 'spin-pulse' : ''} />
              <span>Làm mới</span>
            </button>
            <button className="btn-solid-blue" onClick={() => setIsModalOpen(true)}>
              <Plus size={18} />
              <span>Tạo Đơn Giao Hàng</span>
            </button>
          </div>
        </div>
      </div>

      {/* Orders Grid List */}
      <div className="delivery-orders-grid">
        {deliveryOrders.length === 0 ? (
          <div className="card-clean" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '48px 20px' }}>
            <Package size={48} color="#94A3B8" style={{ marginBottom: '12px' }} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#334155' }}>Chưa Có Đơn Giao Hàng Nào</h3>
            <p style={{ fontSize: '0.88rem', color: '#94A3B8', marginTop: '4px' }}>
              Bấm vào nút "Tạo Đơn Giao Hàng" ở trên để tạo lệnh vận chuyển đầu tiên.
            </p>
          </div>
        ) : (
          deliveryOrders.map(order => (
            <div key={order.order_id} className="order-card-clean">
              <div className="order-card-top">
                <span className="order-code">#{order.order_id.substring(0, 8).toUpperCase()}</span>
                {getStatusBadge(order.status)}
              </div>

              <div>
                <h4 style={{ fontSize: '1rem', fontWeight: 800, color: '#0F172A' }}>{order.item_description}</h4>
                <div style={{ fontSize: '0.82rem', color: '#64748B', marginTop: '4px' }}>
                  Người tạo: {order.creator_name}
                </div>
              </div>

              <div style={{ background: '#F8FAFC', padding: '10px 12px', borderRadius: '10px', fontSize: '0.85rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#334155', fontWeight: 600 }}>
                  <MapPin size={14} color="#2563EB" />
                  <span>Điểm lấy: <strong>{order.pickup_poi_name}</strong></span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#334155', fontWeight: 600, marginTop: '4px' }}>
                  <ArrowRight size={14} color="#10B981" />
                  <span>Điểm giao: <strong>{order.dropoff_poi_name}</strong></span>
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                {order.status === 'PENDING' && (
                  <button
                    className="btn-solid-blue"
                    style={{ width: '100%', padding: '9px 12px', fontSize: '0.88rem' }}
                    onClick={() => handleUpdateStatus(order.order_id, 'MOVING_TO_PICKUP', 25)}
                  >
                    Bắt Đầu Đi Lấy Hàng 🚚
                  </button>
                )}
                {order.status === 'MOVING_TO_PICKUP' && (
                  <button
                    className="btn-solid-emerald"
                    style={{ width: '100%', padding: '9px 12px', fontSize: '0.88rem' }}
                    onClick={() => handleUpdateStatus(order.order_id, 'DELIVERING', 50)}
                  >
                    Đã Xếp Hàng • Đi Giao 🚀
                  </button>
                )}
                {order.status === 'DELIVERING' && (
                  <button
                    className="btn-solid-emerald"
                    style={{ width: '100%', padding: '9px 12px', fontSize: '0.88rem' }}
                    onClick={() => handleUpdateStatus(order.order_id, 'COMPLETED', 100)}
                  >
                    Xác Nhận Đã Giao Xong ✅
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Clean Create Order Modal Dialog */}
      {isModalOpen && (
        <div className="modal-backdrop-clean" onClick={() => setIsModalOpen(false)}>
          <div className="modal-dialog-clean" onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h3 style={{ margin: 0 }}>TẠO ĐƠN GIAO HÀNG</h3>
              <button className="btn-outline" style={{ padding: '6px' }} onClick={() => setIsModalOpen(false)}>
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateOrder} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
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
                  placeholder="VD: 2 ly Highlands Coffee, Tài liệu bàn A3..."
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '6px' }}>
                  Điểm lấy hàng:
                </label>
                <select
                  className="quick-search-input"
                  style={{ padding: '10px 14px' }}
                  value={pickupId}
                  onChange={e => setPickupId(e.target.value)}
                >
                  {pois.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.category})
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
                  style={{ padding: '10px 14px' }}
                  value={dropoffId}
                  onChange={e => setDropoffId(e.target.value)}
                >
                  {pois.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.category})
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                <button type="button" className="btn-outline" style={{ flex: 1 }} onClick={() => setIsModalOpen(false)}>
                  Hủy
                </button>
                <button type="submit" className="btn-solid-blue" style={{ flex: 1 }} disabled={loading}>
                  {loading ? 'Đang tạo...' : 'Tạo Đơn Ngay'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
