import React, { useState, useEffect } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { DeliveryOrder, PointOfInterest } from '../../types/protocol';
import { Package, Plus, RefreshCw, CheckCircle2, Clock, Truck, MapPin, ArrowRight, AlertCircle, X } from 'lucide-react';

export const DeliveryOrdersTab: React.FC = () => {
  const { deliveryOrders, pois, pairedRobot } = useRobotStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [creatorName, setCreatorName] = useState('Nhân viên Kho');
  const [pickupId, setPickupId] = useState(pois[0]?.id || 'poi_warehouse_b1');
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
      alert('Vui lòng kết nối và xác thực với Robot trước khi đặt đơn.');
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
          itemDescription: itemDesc || 'Kiện hàng nội bộ',
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

  const handleUpdateStatus = async (orderId: string, nextStatus: string, progress: number) => {
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
      alert(`Lỗi cập nhật đơn: ${err.message}`);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING':
        return <span className="status-badge badge-pending"><Clock size={12} /> CHỜ ĐIỀU PHỐI</span>;
      case 'MOVING_TO_PICKUP':
        return <span className="status-badge badge-moving"><Truck size={12} /> ĐANG ĐẾN LẤY HÀNG</span>;
      case 'ARRIVED_AT_PICKUP':
        return <span className="status-badge badge-arrived"><Package size={12} /> ĐÃ ĐẾN ĐIỂM LẤY</span>;
      case 'DELIVERING':
        return <span className="status-badge badge-moving"><Truck size={12} /> ĐANG GIAO ĐẾN ĐÍCH</span>;
      case 'ARRIVED_AT_DROPOFF':
        return <span className="status-badge badge-arrived"><MapPin size={12} /> ĐÃ ĐẾN ĐIỂM GIAO</span>;
      case 'COMPLETED':
        return <span className="status-badge badge-completed"><CheckCircle2 size={12} /> ĐÃ HOÀN THÀNH</span>;
      case 'CANCELLED':
        return <span className="status-badge badge-cancelled"><AlertCircle size={12} /> ĐÃ HỦY</span>;
      default:
        return <span className="status-badge">{status}</span>;
    }
  };

  return (
    <div className="tab-pane active">
      <div className="delivery-container">
        
        {/* Top Action Bar */}
        <div className="card delivery-header-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="delivery-icon-box">
              <Package size={24} color="#00E5FF" />
            </div>
            <div>
              <h2 className="delivery-title">QUẢN LÝ GIAO HÀNG NỘI BỘ (ROBOT DELIVERY DISPATCHER)</h2>
              <p className="delivery-sub">Đặt lệnh tự hành cho Robot lấy hàng từ kho/gian hàng và giao đến vị trí chỉ định.</p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <button className="btn-sm" onClick={fetchOrders} disabled={refreshing}>
              <RefreshCw size={14} className={refreshing ? 'spin-pulse' : ''} style={{ display: 'inline', marginRight: 4 }} />
              Làm Mới
            </button>
            <button className="btn-primary" onClick={() => setIsModalOpen(true)}>
              <Plus size={16} style={{ display: 'inline', marginRight: 4 }} />
              ĐẶT ĐƠN GIAO HÀNG
            </button>
          </div>
        </div>

        {/* Orders Stream / Table */}
        <div className="orders-list-wrapper">
          {deliveryOrders.length === 0 ? (
            <div className="empty-orders-box">
              <Package size={48} color="#64748B" />
              <div style={{ color: '#E2E8F0', fontWeight: 600, marginTop: 12 }}>Chưa có đơn giao hàng nào trong hệ thống</div>
              <div style={{ color: '#64748B', fontSize: 13, marginTop: 4 }}>Nhấn "Đặt Đơn Giao Hàng" ở trên để tạo lệnh vận chuyển đầu tiên.</div>
            </div>
          ) : (
            deliveryOrders.map(order => (
              <div key={order.order_id} className="order-card card">
                <div className="order-card-header">
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span className="order-id-badge">{order.order_id}</span>
                    <span className="order-creator">Tạo bởi: {order.creator_name}</span>
                  </div>
                  {getStatusBadge(order.status)}
                </div>

                <div className="order-route-box">
                  <div className="route-point">
                    <span className="point-label">ĐIỂM LẤY HÀNG (PICKUP)</span>
                    <span className="point-name">{order.pickup_poi_name}</span>
                  </div>
                  <div className="route-arrow">
                    <ArrowRight size={20} color="#00E5FF" />
                  </div>
                  <div className="route-point">
                    <span className="point-label">ĐIỂM GIAO ĐÍCH (DROPOFF)</span>
                    <span className="point-name">{order.dropoff_poi_name}</span>
                  </div>
                </div>

                <div className="order-meta-info">
                  <span>Kiện hàng: <strong>{order.item_description}</strong></span>
                  <span>Thời gian: {new Date(order.created_at * 1000).toLocaleTimeString()}</span>
                </div>

                {/* Progress Bar */}
                <div className="order-progress-track">
                  <div className="order-progress-fill" style={{ width: `${order.current_progress}%` }}></div>
                </div>

                {/* Staff Action Buttons based on order phase */}
                <div className="order-actions-row">
                  {order.status === 'MOVING_TO_PICKUP' && (
                    <button
                      className="btn-action-step"
                      onClick={() => handleUpdateStatus(order.order_id, 'ARRIVED_AT_PICKUP', 50)}
                    >
                      Xác Nhận Robot Đã Tới Điểm Lấy
                    </button>
                  )}
                  {order.status === 'ARRIVED_AT_PICKUP' && (
                    <button
                      className="btn-action-step btn-step-deliver"
                      onClick={() => handleUpdateStatus(order.order_id, 'DELIVERING', 75)}
                    >
                      Đã Xếp Hàng Lên Xe ➔ Bắt Đầu Vận Chuyển
                    </button>
                  )}
                  {order.status === 'DELIVERING' && (
                    <button
                      className="btn-action-step btn-step-complete"
                      onClick={() => handleUpdateStatus(order.order_id, 'COMPLETED', 100)}
                    >
                      Xác Nhận Khách Đã Nhận Hàng (Hoàn Thành)
                    </button>
                  )}
                  {order.status !== 'COMPLETED' && order.status !== 'CANCELLED' && (
                    <button
                      className="btn-action-cancel"
                      onClick={() => handleUpdateStatus(order.order_id, 'CANCELLED', 0)}
                    >
                      Hủy Đơn
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Create Order Modal */}
        {isModalOpen && (
          <div className="modal-overlay">
            <div className="modal-card">
              <div className="modal-header">
                <h3 className="modal-title">ĐẶT ĐƠN GIAO HÀNG TỰ HÀNH MỚI</h3>
                <button className="btn-close-modal" onClick={() => setIsModalOpen(false)}>
                  <X size={20} />
                </button>
              </div>

              <form onSubmit={handleCreateOrder} className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                <div>
                  <label className="setting-label">Tên Nhân Viên / Bộ Phận Đặt Đơn</label>
                  <input
                    type="text"
                    className="input-text"
                    value={creatorName}
                    onChange={(e) => setCreatorName(e.target.value)}
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-col-1">
                    <label className="setting-label">1. Điểm Lấy Hàng (Pickup)</label>
                    <select
                      className="input-text"
                      value={pickupId}
                      onChange={(e) => setPickupId(e.target.value)}
                    >
                      {pois.map(p => (
                        <option key={p.id} value={p.id}>
                          {p.name} ({p.floor})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-col-1">
                    <label className="setting-label">2. Điểm Giao Đích (Dropoff)</label>
                    <select
                      className="input-text"
                      value={dropoffId}
                      onChange={(e) => setDropoffId(e.target.value)}
                    >
                      {pois.map(p => (
                        <option key={p.id} value={p.id}>
                          {p.name} ({p.floor})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="setting-label">Mô Tả Kiện Hàng / Vật Phẩm</label>
                  <input
                    type="text"
                    className="input-text"
                    value={itemDesc}
                    onChange={(e) => setItemDesc(e.target.value)}
                    placeholder="ví dụ: Hộp tài liệu kế toán, 2 ly cà phê Highland, Thùng quần áo Zara..."
                    required
                  />
                </div>

                <button type="submit" className="btn-primary btn-block" disabled={loading} style={{ marginTop: 10 }}>
                  {loading ? 'ĐANG TẠO ĐƠN & ĐIỀU PHỐI ROBOT...' : 'XÁC NHẬN ĐIỀU PHỐI ROBOT GIAO HÀNG'}
                </button>
              </form>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
