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
  Sparkles
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
          itemDescription: itemDesc.trim() || 'Hàng hóa / Tài liệu',
        },
        pairedRobot?.token
      );

      if (res.success && res.order) {
        updateGlobalState(prev => ({
          deliveryOrders: [res.order!, ...prev.deliveryOrders],
        }));
        setIsModalOpen(false);
        setItemDesc('');
        showToast('🎉 Đã tạo đơn thành công!');
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
        showToast('✅ Đã cập nhật trạng thái đơn!');
        fetchOrders();
      }
    } catch (err: any) {
      alert(`Lỗi cập nhật: ${err.message}`);
    }
  };

  const handleCancelOrder = async (orderId: string) => {
    if (!confirm('Bạn có chắc muốn hủy đơn này không?')) return;
    await handleUpdateStatus(orderId, 'CANCELLED', 0);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING':
        return <span className="badge-status-clean pending" style={{ fontSize: '0.78rem', padding: '3px 8px', whiteSpace: 'nowrap' }}>⏳ Chờ điều phối</span>;
      case 'MOVING_TO_PICKUP':
        return <span className="badge-status-clean delivering" style={{ fontSize: '0.78rem', padding: '3px 8px', whiteSpace: 'nowrap' }}>🚚 Đến lấy hàng</span>;
      case 'ARRIVED_AT_PICKUP':
        return <span className="badge-status-clean completed" style={{ fontSize: '0.78rem', padding: '3px 8px', whiteSpace: 'nowrap' }}>📦 Đến điểm lấy</span>;
      case 'DELIVERING':
        return <span className="badge-status-clean delivering" style={{ fontSize: '0.78rem', padding: '3px 8px', whiteSpace: 'nowrap' }}>🚀 Đang giao</span>;
      case 'ARRIVED_AT_DROPOFF':
        return <span className="badge-status-clean completed" style={{ fontSize: '0.78rem', padding: '3px 8px', whiteSpace: 'nowrap' }}>📍 Đến điểm giao</span>;
      case 'COMPLETED':
        return <span className="badge-status-clean completed" style={{ fontSize: '0.78rem', padding: '3px 8px', whiteSpace: 'nowrap' }}>✅ Đã giao xong</span>;
      case 'CANCELLED':
        return <span className="badge-status-clean error" style={{ fontSize: '0.78rem', padding: '3px 8px', whiteSpace: 'nowrap' }}>❌ Đã hủy</span>;
      default:
        return <span className="badge-status-clean" style={{ fontSize: '0.78rem', padding: '3px 8px', whiteSpace: 'nowrap' }}>{status}</span>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', maxWidth: '800px', margin: '0 auto', width: '100%' }}>
      
      {/* Toast Notification */}
      {toastMessage && (
        <div style={{
          position: 'fixed',
          top: '16px',
          right: '16px',
          zIndex: 9999,
          background: '#0F172A',
          color: '#F8FAFC',
          padding: '10px 16px',
          borderRadius: '10px',
          boxShadow: '0 8px 20px rgba(0,0,0,0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontWeight: 600,
          fontSize: '0.85rem'
        }}>
          <Sparkles size={16} color="#38BDF8" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Main Header Card */}
      <div className="card-clean" style={{ padding: '12px 14px', width: '100%', boxSizing: 'border-box', overflow: 'hidden' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '6px' }}>
          <div style={{ minWidth: 0 }}>
            <h2 style={{ fontSize: '1rem', fontWeight: 800, color: '#0F172A', margin: 0, display: 'flex', alignItems: 'center', gap: '5px', whiteSpace: 'nowrap' }}>
              <Truck size={17} color="#2563EB" />
              GIAO HÀNG
            </h2>
            <p style={{ fontSize: '0.74rem', color: '#64748B', margin: '2px 0 0 0', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              Vận chuyển giữa các quầy
            </p>
          </div>

          <div style={{ display: 'flex', gap: '6px', alignItems: 'center', flexShrink: 0 }}>
            <button 
              className="btn-outline" 
              onClick={fetchOrders} 
              disabled={refreshing}
              title="Làm mới"
              style={{ padding: '6px 8px', borderRadius: '8px' }}
            >
              <RefreshCw size={14} className={refreshing ? 'spin-pulse' : ''} />
            </button>
            <button 
              className="btn-solid-blue" 
              onClick={() => setIsModalOpen(true)}
              style={{ padding: '6px 12px', fontSize: '0.8rem', fontWeight: 700, borderRadius: '8px', whiteSpace: 'nowrap' }}
            >
              <Plus size={14} />
              <span>Tạo đơn</span>
            </button>
          </div>
        </div>

        {/* Sub-Navigation Grid (3 equal columns, zero line breaks) */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(3, 1fr)', 
          gap: '6px', 
          marginTop: '12px', 
          borderTop: '1px solid #F1F5F9', 
          paddingTop: '10px' 
        }}>
          <button
            onClick={() => setActiveSubTab('active')}
            style={{
              padding: '8px 4px',
              borderRadius: '8px',
              border: 'none',
              background: activeSubTab === 'active' ? '#EFF6FF' : 'transparent',
              color: activeSubTab === 'active' ? '#1D4ED8' : '#64748B',
              fontWeight: 700,
              fontSize: '0.82rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '4px',
              whiteSpace: 'nowrap',
              transition: 'all 0.15s ease'
            }}
          >
            <Truck size={14} />
            <span>Đang giao ({activeOrders.length})</span>
          </button>

          <button
            onClick={() => setActiveSubTab('queue')}
            style={{
              padding: '8px 4px',
              borderRadius: '8px',
              border: 'none',
              background: activeSubTab === 'queue' ? '#EFF6FF' : 'transparent',
              color: activeSubTab === 'queue' ? '#1D4ED8' : '#64748B',
              fontWeight: 700,
              fontSize: '0.82rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '4px',
              whiteSpace: 'nowrap',
              transition: 'all 0.15s ease'
            }}
          >
            <Clock size={14} />
            <span>Hàng chờ ({queueOrders.length})</span>
          </button>

          <button
            onClick={() => setActiveSubTab('history')}
            style={{
              padding: '8px 4px',
              borderRadius: '8px',
              border: 'none',
              background: activeSubTab === 'history' ? '#EFF6FF' : 'transparent',
              color: activeSubTab === 'history' ? '#1D4ED8' : '#64748B',
              fontWeight: 700,
              fontSize: '0.82rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '4px',
              whiteSpace: 'nowrap',
              transition: 'all 0.15s ease'
            }}
          >
            <CheckCircle2 size={14} />
            <span>Lịch sử ({historyOrders.length})</span>
          </button>
        </div>
      </div>

      {/* TAB 1: ACTIVE ORDER */}
      {activeSubTab === 'active' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {activeOrders.length === 0 ? (
            <div className="card-clean" style={{ textAlign: 'center', padding: '36px 16px' }}>
              <Package size={44} color="#94A3B8" style={{ marginBottom: '10px' }} />
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#1E293B', margin: '0 0 4px 0' }}>Robot Đang Rảnh</h3>
              <p style={{ fontSize: '0.84rem', color: '#64748B', margin: 0 }}>
                Hiện không có đơn hàng nào đang thực hiện. Bấm <strong>"+ Tạo đơn"</strong> ở trên để giao hàng mới.
              </p>
            </div>
          ) : (
            activeOrders.map(order => {
              // Detailed task breakdown based on active phase
              let phaseNumber = 1;
              let phaseTitle = 'Đang di chuyển đến điểm lấy';
              let phaseTarget = order.pickup_poi_name;
              let phaseActionText = 'Robot đang tự hành di chuyển đến điểm lấy, quét vật cản và duy trì tốc độ an toàn.';
              let phaseGuideText = `Quầy "${order.pickup_poi_name}" vui lòng chuẩn bị sẵn hàng hóa. Khi robot đỗ, xếp hàng lên xe rồi xác nhận.`;
              let phaseThemeColor = '#2563EB';
              let phaseBgColor = '#EFF6FF';
              let phaseBorderColor = '#BFDBFE';

              if (order.status === 'ARRIVED_AT_PICKUP') {
                phaseNumber = 2;
                phaseTitle = 'Đã đến điểm lấy — Chờ xếp hàng';
                phaseTarget = order.pickup_poi_name;
                phaseActionText = 'Robot đã dừng đỗ an toàn tại quầy lấy hàng. Màn hình OLED hiển thị thông báo mời xếp hàng.';
                phaseGuideText = `Nhân viên quầy vui lòng đặt "${order.item_description}" lên khoang xe, sau đó nhấn "🚀 Đã Xếp Hàng • Bắt Đầu Giao".`;
                phaseThemeColor = '#D97706';
                phaseBgColor = '#FFFBEB';
                phaseBorderColor = '#FDE68A';
              } else if (order.status === 'DELIVERING') {
                phaseNumber = 3;
                phaseTitle = 'Đang vận chuyển đến điểm giao';
                phaseTarget = order.dropoff_poi_name;
                phaseActionText = 'Robot đang tự hành chở hàng trên hành lang T1, cảnh báo chướng ngại vật và hướng tới điểm đích.';
                phaseGuideText = `Người nhận tại quầy "${order.dropoff_poi_name}" chuẩn bị đón robot để nhận kiện hàng.`;
                phaseThemeColor = '#2563EB';
                phaseBgColor = '#EFF6FF';
                phaseBorderColor = '#BFDBFE';
              } else if (order.status === 'ARRIVED_AT_DROPOFF') {
                phaseNumber = 4;
                phaseTitle = 'Đã đến điểm giao — Chờ nhận hàng';
                phaseTarget = order.dropoff_poi_name;
                phaseActionText = 'Robot đã đến đúng vị trí giao hàng. Đang chờ người nhận kiểm tra và lấy kiện hàng khỏi xe.';
                phaseGuideText = `Người nhận vui lòng lấy "${order.item_description}" ra khỏi xe, sau đó nhấn "✅ Đã Nhận Hàng (Hoàn Tất)".`;
                phaseThemeColor = '#059669';
                phaseBgColor = '#ECFDF5';
                phaseBorderColor = '#A7F3D0';
              }

              return (
                <div key={order.order_id} className="card-clean" style={{ padding: '16px', border: `2px solid ${phaseThemeColor}`, borderRadius: '14px', background: '#FFFFFF' }}>
                  
                  {/* Top Bar: Order ID & Status Badge */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', gap: '8px', flexWrap: 'wrap' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '0.82rem', fontWeight: 800, background: '#1E293B', color: '#FFFFFF', padding: '4px 10px', borderRadius: '6px' }}>
                        #{order.order_id}
                      </span>
                      <span style={{ fontSize: '0.82rem', color: '#64748B' }}>
                        Tạo bởi: <strong style={{ color: '#0F172A' }}>{order.creator_name}</strong>
                      </span>
                    </div>
                    {getStatusBadge(order.status)}
                  </div>

                  {/* Item Description Header */}
                  <div style={{ marginBottom: '14px' }}>
                    <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Kiện hàng / Nội dung giao:
                    </div>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0F172A', margin: '2px 0 0 0' }}>
                      📦 {order.item_description}
                    </h3>
                  </div>

                  {/* DETAILED MISSION STATUS BOX */}
                  <div style={{ 
                    background: phaseBgColor, 
                    border: `1.5px solid ${phaseBorderColor}`, 
                    borderRadius: '12px', 
                    padding: '12px 14px', 
                    marginBottom: '14px' 
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                      <div style={{ 
                        width: '26px', 
                        height: '26px', 
                        borderRadius: '50%', 
                        background: phaseThemeColor, 
                        color: '#FFFFFF', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center', 
                        fontSize: '0.8rem', 
                        fontWeight: 800, 
                        flexShrink: 0 
                      }}>
                        {phaseNumber}
                      </div>
                      <div style={{ fontSize: '0.92rem', fontWeight: 800, color: phaseThemeColor }}>
                        {phaseTitle}
                      </div>
                    </div>

                    <div style={{ fontSize: '0.82rem', color: '#1E293B', fontWeight: 600, marginBottom: '6px', lineHeight: 1.4 }}>
                      📍 <strong>Mục tiêu:</strong> {phaseTarget}
                    </div>

                    <div style={{ fontSize: '0.8rem', color: '#475569', lineHeight: 1.45, marginBottom: '8px' }}>
                      🤖 <strong>Hoạt động của xe:</strong> {phaseActionText}
                    </div>

                    <div style={{ 
                      fontSize: '0.78rem', 
                      background: 'rgba(255, 255, 255, 0.7)', 
                      padding: '8px 10px', 
                      borderRadius: '8px', 
                      color: '#334155', 
                      lineHeight: 1.4 
                    }}>
                      💡 <strong>Hướng dẫn:</strong> {phaseGuideText}
                    </div>
                  </div>

                  {/* 4-STAGE INTERACTIVE VISUAL STEPPER */}
                  <div style={{ marginBottom: '14px', background: '#F8FAFC', padding: '10px 8px', borderRadius: '10px' }}>
                    <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase', marginBottom: '8px', textAlign: 'center' }}>
                      Quy trình giao hàng 4 bước
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '4px', textAlign: 'center' }}>
                      
                      {/* Step 1 */}
                      <div style={{
                        padding: '6px 2px',
                        borderRadius: '6px',
                        background: phaseNumber >= 1 ? (phaseNumber === 1 ? '#DBEAFE' : '#DCFCE7') : '#F1F5F9',
                        color: phaseNumber >= 1 ? (phaseNumber === 1 ? '#1E40AF' : '#166534') : '#94A3B8',
                        border: phaseNumber === 1 ? '1.5px solid #3B82F6' : '1px solid transparent'
                      }}>
                        <div style={{ fontSize: '0.75rem', fontWeight: 800 }}>1. Đi lấy</div>
                        <div style={{ fontSize: '0.66rem', marginTop: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {order.pickup_poi_name}
                        </div>
                      </div>

                      {/* Step 2 */}
                      <div style={{
                        padding: '6px 2px',
                        borderRadius: '6px',
                        background: phaseNumber >= 2 ? (phaseNumber === 2 ? '#FEF3C7' : '#DCFCE7') : '#F1F5F9',
                        color: phaseNumber >= 2 ? (phaseNumber === 2 ? '#92400E' : '#166534') : '#94A3B8',
                        border: phaseNumber === 2 ? '1.5px solid #F59E0B' : '1px solid transparent'
                      }}>
                        <div style={{ fontSize: '0.75rem', fontWeight: 800 }}>2. Xếp hàng</div>
                        <div style={{ fontSize: '0.66rem', marginTop: '2px', whiteSpace: 'nowrap' }}>
                          {phaseNumber > 2 ? 'Đã xếp xong' : (phaseNumber === 2 ? 'Đang chờ' : 'Chờ lấy')}
                        </div>
                      </div>

                      {/* Step 3 */}
                      <div style={{
                        padding: '6px 2px',
                        borderRadius: '6px',
                        background: phaseNumber >= 3 ? (phaseNumber === 3 ? '#DBEAFE' : '#DCFCE7') : '#F1F5F9',
                        color: phaseNumber >= 3 ? (phaseNumber === 3 ? '#1E40AF' : '#166534') : '#94A3B8',
                        border: phaseNumber === 3 ? '1.5px solid #3B82F6' : '1px solid transparent'
                      }}>
                        <div style={{ fontSize: '0.75rem', fontWeight: 800 }}>3. Vận chuyển</div>
                        <div style={{ fontSize: '0.66rem', marginTop: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {order.dropoff_poi_name}
                        </div>
                      </div>

                      {/* Step 4 */}
                      <div style={{
                        padding: '6px 2px',
                        borderRadius: '6px',
                        background: phaseNumber >= 4 ? '#FEF3C7' : '#F1F5F9',
                        color: phaseNumber >= 4 ? '#92400E' : '#94A3B8',
                        border: phaseNumber === 4 ? '1.5px solid #10B981' : '1px solid transparent'
                      }}>
                        <div style={{ fontSize: '0.75rem', fontWeight: 800 }}>4. Nhận hàng</div>
                        <div style={{ fontSize: '0.66rem', marginTop: '2px', whiteSpace: 'nowrap' }}>
                          {phaseNumber === 4 ? 'Đang bàn giao' : 'Đích đến'}
                        </div>
                      </div>

                    </div>
                  </div>

                  {/* Route Summary Card */}
                  <div style={{ background: '#F8FAFC', padding: '10px 12px', borderRadius: '10px', marginBottom: '14px', border: '1px solid #E2E8F0' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
                        <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#DBEAFE', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                          <MapPin size={15} color="#2563EB" />
                        </div>
                        <div style={{ minWidth: 0 }}>
                          <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700 }}>ĐIỂM LẤY HÀNG</div>
                          <div style={{ fontSize: '0.86rem', fontWeight: 800, color: '#0F172A', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{order.pickup_poi_name}</div>
                        </div>
                      </div>

                      <ArrowRight size={16} color="#94A3B8" style={{ flexShrink: 0 }} />

                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
                        <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#D1FAE5', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                          <MapPin size={15} color="#10B981" />
                        </div>
                        <div style={{ minWidth: 0 }}>
                          <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700 }}>ĐIỂM GIAO ĐẾN</div>
                          <div style={{ fontSize: '0.86rem', fontWeight: 800, color: '#0F172A', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{order.dropoff_poi_name}</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div style={{ marginBottom: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', fontWeight: 700, color: '#475569', marginBottom: '4px' }}>
                      <span>Tiến độ giai đoạn hiện tại</span>
                      <span style={{ color: phaseThemeColor }}>{order.current_progress}%</span>
                    </div>
                    <div style={{ width: '100%', height: '8px', background: '#E2E8F0', borderRadius: '4px', overflow: 'hidden' }}>
                      <div 
                        style={{ 
                          width: `${Math.max(6, order.current_progress)}%`, 
                          height: '100%', 
                          background: phaseNumber === 4 ? '#10B981' : 'linear-gradient(90deg, #3B82F6, #10B981)', 
                          borderRadius: '4px',
                          transition: 'width 0.4s ease'
                        }} 
                      />
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div style={{ display: 'flex', gap: '8px' }}>
                    {order.status === 'MOVING_TO_PICKUP' && (
                      <button
                        className="btn-solid-blue"
                        style={{ flex: 1, padding: '11px 14px', fontSize: '0.88rem', fontWeight: 700, whiteSpace: 'nowrap' }}
                        onClick={() => handleUpdateStatus(order.order_id, 'ARRIVED_AT_PICKUP', 100)}
                      >
                        📍 Đã Đến Điểm Lấy
                      </button>
                    )}

                    {order.status === 'ARRIVED_AT_PICKUP' && (
                      <button
                        className="btn-solid-emerald"
                        style={{ flex: 1, padding: '11px 14px', fontSize: '0.9rem', fontWeight: 800, whiteSpace: 'nowrap', background: '#10B981', color: '#FFFFFF' }}
                        onClick={() => handleUpdateStatus(order.order_id, 'DELIVERING', 0)}
                      >
                        🚀 Đã Xếp Hàng • Bắt Đầu Giao
                      </button>
                    )}

                    {order.status === 'DELIVERING' && (
                      <button
                        className="btn-solid-blue"
                        style={{ flex: 1, padding: '11px 14px', fontSize: '0.88rem', fontWeight: 700, whiteSpace: 'nowrap' }}
                        onClick={() => handleUpdateStatus(order.order_id, 'ARRIVED_AT_DROPOFF', 100)}
                      >
                        📍 Đã Đến Điểm Giao
                      </button>
                    )}

                    {order.status === 'ARRIVED_AT_DROPOFF' && (
                      <button
                        className="btn-solid-emerald"
                        style={{ flex: 1, padding: '11px 14px', fontSize: '0.9rem', fontWeight: 800, whiteSpace: 'nowrap', background: '#059669', color: '#FFFFFF' }}
                        onClick={() => handleUpdateStatus(order.order_id, 'COMPLETED', 100)}
                      >
                        ✅ Đã Nhận Hàng (Hoàn Tất)
                      </button>
                    )}

                    <button
                      className="btn-outline"
                      style={{ padding: '11px 12px', fontSize: '0.82rem', color: '#EF4444', borderColor: '#FECACA', whiteSpace: 'nowrap' }}
                      onClick={() => handleCancelOrder(order.order_id)}
                    >
                      Hủy Đơn
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* TAB 2: QUEUE */}
      {activeSubTab === 'queue' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ background: '#EFF6FF', border: '1px solid #BFDBFE', padding: '10px 14px', borderRadius: '10px', fontSize: '0.8rem', color: '#1E40AF', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Sparkles size={16} />
            <span>Robot sẽ tự động bắt đầu đơn tiếp theo theo thứ tự FIFO ngay khi đơn hiện tại xong.</span>
          </div>

          {queueOrders.length === 0 ? (
            <div className="card-clean" style={{ textAlign: 'center', padding: '32px 16px' }}>
              <Clock size={38} color="#94A3B8" style={{ marginBottom: '8px' }} />
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#334155' }}>Hàng Đợi Trống</h3>
              <p style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '2px' }}>
                Không có đơn hàng nào đang chờ xử lý.
              </p>
            </div>
          ) : (
            queueOrders.map((order, index) => (
              <div key={order.order_id} className="order-card-clean" style={{ padding: '12px 14px', borderRadius: '10px' }}>
                <div className="order-card-top" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ background: '#3B82F6', color: '#FFF', fontWeight: 800, fontSize: '0.75rem', padding: '2px 8px', borderRadius: '4px' }}>
                      Thứ tự #{index + 1}
                    </span>
                    <span className="order-code" style={{ fontSize: '0.8rem', fontWeight: 700, color: '#64748B' }}>#{order.order_id}</span>
                  </div>
                  {getStatusBadge(order.status)}
                </div>

                <div style={{ marginBottom: '8px' }}>
                  <h4 style={{ fontSize: '0.98rem', fontWeight: 800, color: '#0F172A', margin: '0 0 2px 0' }}>
                    📦 {order.item_description}
                  </h4>
                  <div style={{ fontSize: '0.78rem', color: '#64748B' }}>
                    Người tạo: <strong>{order.creator_name}</strong>
                  </div>
                </div>

                <div style={{ background: '#F8FAFC', padding: '8px 10px', borderRadius: '8px', fontSize: '0.8rem', marginBottom: '10px', border: '1px solid #E2E8F0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#334155', fontWeight: 600 }}>
                    <MapPin size={13} color="#2563EB" />
                    <span>Lấy hàng: <strong>{order.pickup_poi_name}</strong></span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#334155', fontWeight: 600, marginTop: '4px' }}>
                    <ArrowRight size={13} color="#10B981" />
                    <span>Giao đến: <strong>{order.dropoff_poi_name}</strong></span>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    className="btn-solid-blue"
                    style={{ flex: 1, padding: '8px 12px', fontSize: '0.82rem', fontWeight: 700 }}
                    onClick={() => handleUpdateStatus(order.order_id, 'MOVING_TO_PICKUP', 0)}
                  >
                    🚀 Ưu Tiên Chạy Ngay
                  </button>
                  <button
                    className="btn-outline"
                    style={{ padding: '8px 12px', fontSize: '0.82rem', color: '#EF4444', borderColor: '#FECACA' }}
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

      {/* TAB 3: HISTORY */}
      {activeSubTab === 'history' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {historyOrders.length === 0 ? (
            <div className="card-clean" style={{ textAlign: 'center', padding: '32px 16px' }}>
              <CheckCircle2 size={38} color="#94A3B8" style={{ marginBottom: '8px' }} />
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#334155' }}>Chưa Có Lịch Sử</h3>
              <p style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '2px' }}>
                Các đơn đã giao hoặc hủy sẽ hiển thị tại đây.
              </p>
            </div>
          ) : (
            historyOrders.map(order => (
              <div key={order.order_id} className="order-card-clean" style={{ padding: '12px 14px', opacity: 0.95, borderRadius: '10px' }}>
                <div className="order-card-top" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span className="order-code" style={{ fontSize: '0.8rem', fontWeight: 800, color: '#475569' }}>#{order.order_id}</span>
                  {getStatusBadge(order.status)}
                </div>

                <div>
                  <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0F172A', margin: '0 0 2px 0' }}>
                    📦 {order.item_description}
                  </h4>
                  <div style={{ fontSize: '0.78rem', color: '#64748B' }}>
                    {order.creator_name} • Lộ trình: <strong>{order.pickup_poi_name}</strong> ➔ <strong>{order.dropoff_poi_name}</strong>
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 800, color: '#0F172A' }}>
                TẠO ĐƠN GIAO MỚI
              </h3>
              <button className="btn-outline" style={{ padding: '5px', borderRadius: '50%' }} onClick={() => setIsModalOpen(false)}>
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleCreateOrder} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                  Người tạo đơn:
                </label>
                <input
                  type="text"
                  className="quick-search-input"
                  style={{ padding: '9px 12px', fontSize: '0.88rem' }}
                  value={creatorName}
                  onChange={e => setCreatorName(e.target.value)}
                  placeholder="VD: Quầy Lễ Tân..."
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                  Món hàng / Ghi chú:
                </label>
                <input
                  type="text"
                  className="quick-search-input"
                  style={{ padding: '9px 12px', fontSize: '0.88rem' }}
                  value={itemDesc}
                  onChange={e => setItemDesc(e.target.value)}
                  placeholder="VD: 2 ly Highlands Cafe..."
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                    Điểm lấy hàng:
                  </label>
                  <select
                    className="quick-search-input"
                    style={{ padding: '9px 10px', fontSize: '0.85rem' }}
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
                  <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                    Điểm giao đến:
                  </label>
                  <select
                    className="quick-search-input"
                    style={{ padding: '9px 10px', fontSize: '0.85rem' }}
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

              <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                <button type="button" className="btn-outline" style={{ flex: 1, padding: '9px 12px' }} onClick={() => setIsModalOpen(false)}>
                  Hủy
                </button>
                <button type="submit" className="btn-solid-blue" style={{ flex: 1.5, padding: '9px 12px', fontWeight: 700 }} disabled={loading}>
                  {loading ? 'Đang gửi...' : '🚀 Tạo Đơn Ngay'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
