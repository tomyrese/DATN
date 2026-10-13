import React, { useState, useEffect } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { RobotSocket } from '../../services/RobotSocket';
import { MallStore, Promotion, DeliveryOrder } from '../../types/protocol';
import {
  Store,
  Tag,
  Package,
  Gamepad2,
  Clock,
  Phone,
  Save,
  CheckCircle2,
  AlertCircle,
  Plus,
  Trash2,
  ShieldAlert,
  ArrowRight,
  TrendingUp,
  MapPin,
  RefreshCw,
} from 'lucide-react';

export const StaffDashboard: React.FC = () => {
  const { currentUser, pairedRobot, telemetry, connectionStatus, isSafetyBlocked, isEmergencyStopped, settings } = useRobotStore();
  const [activeSubTab, setActiveSubTab] = useState<'overview' | 'store-info' | 'promotions' | 'orders' | 'control'>('overview');

  // Stores data
  const [stores, setStores] = useState<MallStore[]>([]);
  const [selectedStoreId, setSelectedStoreId] = useState<string>('');
  const [storeForm, setStoreForm] = useState<Partial<MallStore>>({
    name: '',
    description: '',
    contact_phone: '',
    opening_hours: '',
    is_active: 1,
  });
  const [savingStore, setSavingStore] = useState(false);
  const [storeSuccessMsg, setStoreSuccessMsg] = useState<string | null>(null);
  const [storeErrorMsg, setStoreErrorMsg] = useState<string | null>(null);

  // Promotions data
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [loadingPromos, setLoadingPromos] = useState(false);
  const [showAddPromoModal, setShowAddPromoModal] = useState(false);
  const [newPromo, setNewPromo] = useState({
    title: '',
    description: '',
    discountPercent: 15,
    promoCode: '',
    startTime: '',
    endTime: '',
  });
  const [promoError, setPromoError] = useState<string | null>(null);
  const [savingPromo, setSavingPromo] = useState(false);

  // Orders data
  const [orders, setOrders] = useState<DeliveryOrder[]>([]);

  const host = pairedRobot?.host || window.location.hostname || 'localhost';
  const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
  const token = currentUser?.token || '';

  // Load stores that this staff is assigned to (or all if admin)
  const loadData = async () => {
    try {
      const allStores = await RobotApi.getStores(host, port);
      const assignedIds = currentUser?.assignedStoreIds || [];
      const userStores = currentUser?.role === 'admin'
        ? allStores
        : allStores.filter(s => assignedIds.includes(s.id));

      setStores(userStores.length > 0 ? userStores : allStores);

      const defaultStore = userStores.length > 0 ? userStores[0] : allStores[0];
      if (defaultStore && !selectedStoreId) {
        setSelectedStoreId(defaultStore.id);
        setStoreForm({
          name: defaultStore.name,
          description: defaultStore.description,
          contact_phone: defaultStore.contact_phone || '1900 6868',
          opening_hours: defaultStore.opening_hours || '09:30 - 22:00',
          is_active: defaultStore.is_active,
        });
      }

      // Load promos
      const promoData = await RobotApi.getPromotions(host, port);
      setPromotions(promoData || []);

      // Load orders
      const orderData = await RobotApi.getDeliveryOrders(host, port);
      setOrders(orderData || []);
    } catch (e) {
      console.warn('Error loading staff dashboard data:', e);
    }
  };

  useEffect(() => {
    loadData();
  }, [currentUser]);

  // When selected store changes in dropdown
  const handleSelectStore = (storeId: string) => {
    setSelectedStoreId(storeId);
    const target = stores.find(s => s.id === storeId);
    if (target) {
      setStoreForm({
        name: target.name,
        description: target.description,
        contact_phone: target.contact_phone || '1900 6868',
        opening_hours: target.opening_hours || '09:30 - 22:00',
        is_active: target.is_active,
      });
    }
    setStoreSuccessMsg(null);
    setStoreErrorMsg(null);
  };

  // Save Store Profile
  const handleSaveStore = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStoreId) return;
    setSavingStore(true);
    setStoreSuccessMsg(null);
    setStoreErrorMsg(null);

    try {
      const res = await RobotApi.updateStore(host, port, selectedStoreId, storeForm, token);
      if (res.success) {
        setStoreSuccessMsg('Đã cập nhật thông tin gian hàng thành công!');
        // Reload store list
        loadData();
      } else {
        setStoreErrorMsg(res.message || 'Không thể lưu thay đổi. Vui lòng kiểm tra quyền hạn.');
      }
    } catch (err: any) {
      setStoreErrorMsg(`Lỗi kết nối: ${err.message}`);
    } finally {
      setSavingStore(false);
    }
  };

  // Create Promotion for assigned store
  const handleCreatePromo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPromo.title.trim() || !selectedStoreId) {
      setPromoError('Vui lòng điền đầy đủ tiêu đề và chọn gian hàng.');
      return;
    }

    setSavingPromo(true);
    setPromoError(null);

    try {
      const res = await RobotApi.createPromotion(
        host,
        port,
        {
          storeId: selectedStoreId,
          title: newPromo.title,
          description: newPromo.description,
          discountPercent: Number(newPromo.discountPercent),
          promoCode: newPromo.promoCode.trim().toUpperCase() || undefined,
        },
        token
      );

      if (res.success) {
        setShowAddPromoModal(false);
        setNewPromo({
          title: '',
          description: '',
          discountPercent: 15,
          promoCode: '',
          startTime: '',
          endTime: '',
        });
        loadData();
      } else {
        setPromoError(res.message || 'Không thể tạo chương trình ưu đãi.');
      }
    } catch (err: any) {
      setPromoError(`Lỗi kết nối: ${err.message}`);
    } finally {
      setSavingPromo(false);
    }
  };

  // Delete Promotion
  const handleDeletePromo = async (promoId: string) => {
    if (!window.confirm('Quý khách có chắc chắn muốn xóa chương trình khuyến mãi này?')) return;
    try {
      const ok = await RobotApi.deletePromotion(host, port, promoId, token);
      if (ok) {
        loadData();
      } else {
        alert('Không thể xóa ưu đãi. Vui lòng kiểm tra quyền hạn.');
      }
    } catch (e: any) {
      alert(`Lỗi: ${e.message}`);
    }
  };

  const assignedStoreNames = stores.map(s => s.name).join(', ') || 'Chưa được phân công';
  const myPromotions = promotions.filter(p => p.store_id === selectedStoreId);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px', maxWidth: '1080px', margin: '0 auto', width: '100%' }}>
      
      {/* ==================== 1. STAFF HEADER BAR ==================== */}
      <section
        className="card-clean"
        style={{
          padding: '20px 24px',
          background: 'linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 100%)',
          borderRadius: '16px',
          border: '1px solid #E2E8F0',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1D4ED8', background: '#DBEAFE', padding: '2px 8px', borderRadius: '6px' }}>
                BÀN LÀM VIỆC NHÂN VIÊN
              </span>
              <span style={{ fontSize: '0.8rem', color: '#64748B', fontWeight: 600 }}>
                Tài khoản: <strong>{currentUser?.username || 'staff'}</strong>
              </span>
            </div>
            <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#0F172A', margin: '0 0 4px 0' }}>
              Xin chào, {currentUser?.fullName || currentUser?.username}!
            </h2>
            <p style={{ margin: 0, fontSize: '0.86rem', color: '#475569' }}>
              Gian hàng phụ trách: <strong style={{ color: '#0F172A' }}>{assignedStoreNames}</strong>
            </p>
          </div>

          {/* Quick Sub-navigation Buttons */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              onClick={() => setActiveSubTab('overview')}
              style={{
                background: activeSubTab === 'overview' ? '#2563EB' : '#F1F5F9',
                color: activeSubTab === 'overview' ? '#FFFFFF' : '#334155',
                border: 'none',
                borderRadius: '8px',
                padding: '8px 14px',
                fontSize: '0.84rem',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              Tổng Quan
            </button>
            <button
              onClick={() => setActiveSubTab('store-info')}
              style={{
                background: activeSubTab === 'store-info' ? '#2563EB' : '#F1F5F9',
                color: activeSubTab === 'store-info' ? '#FFFFFF' : '#334155',
                border: 'none',
                borderRadius: '8px',
                padding: '8px 14px',
                fontSize: '0.84rem',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              Thông Tin Gian Hàng
            </button>
            <button
              onClick={() => setActiveSubTab('promotions')}
              style={{
                background: activeSubTab === 'promotions' ? '#2563EB' : '#F1F5F9',
                color: activeSubTab === 'promotions' ? '#FFFFFF' : '#334155',
                border: 'none',
                borderRadius: '8px',
                padding: '8px 14px',
                fontSize: '0.84rem',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              Khuyến Mãi ({myPromotions.length})
            </button>
            <button
              onClick={() => setActiveSubTab('control')}
              style={{
                background: activeSubTab === 'control' ? '#2563EB' : '#F1F5F9',
                color: activeSubTab === 'control' ? '#FFFFFF' : '#334155',
                border: 'none',
                borderRadius: '8px',
                padding: '8px 14px',
                fontSize: '0.84rem',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              Giám Sát Robot
            </button>
          </div>
        </div>
      </section>

      {/* ==================== 2. SUBTAB: OVERVIEW ==================== */}
      {activeSubTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* 4 Metric Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
            <div className="card-clean" style={{ padding: '18px', borderLeft: '4px solid #2563EB' }}>
              <div style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600 }}>Gian Hàng Được Gán</div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0F172A', marginTop: '4px' }}>
                {stores.length}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#16A34A', fontWeight: 600, marginTop: '2px' }}>
                Đang trực tuyến trên bản đồ
              </div>
            </div>

            <div className="card-clean" style={{ padding: '18px', borderLeft: '4px solid #DC2626' }}>
              <div style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600 }}>Ưu Đãi Đang Hoạt Động</div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0F172A', marginTop: '4px' }}>
                {myPromotions.length}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: '2px' }}>
                Hiển thị cho khách tham quan
              </div>
            </div>

            <div className="card-clean" style={{ padding: '18px', borderLeft: '4px solid #16A34A' }}>
              <div style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600 }}>Đơn Giao Hàng Nội Bộ</div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0F172A', marginTop: '4px' }}>
                {orders.length}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#16A34A', fontWeight: 600, marginTop: '2px' }}>
                Hệ thống sẵn sàng tiếp nhận
              </div>
            </div>

            <div className="card-clean" style={{ padding: '18px', borderLeft: '4px solid #F59E0B' }}>
              <div style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600 }}>Trạng Thái Robot</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0F172A', marginTop: '8px' }}>
                {connectionStatus === 'CONNECTED' ? 'Sẵn Sàng Tại T1' : 'Chế Độ Giả Lập'}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '2px' }}>
                Pin: 92% | An toàn: Hoạt động
              </div>
            </div>
          </div>

          {/* Action Tasks Row */}
          <div className="card-clean" style={{ padding: '22px 24px' }}>
            <h3 style={{ margin: '0 0 14px 0', fontSize: '1.1rem', fontWeight: 800, color: '#0F172A' }}>
              Nhiệm Vụ Thường Nhật
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
              <div
                onClick={() => setActiveSubTab('store-info')}
                style={{
                  border: '1px solid #E2E8F0',
                  borderRadius: '12px',
                  padding: '16px',
                  cursor: 'pointer',
                  background: '#F8FAFC',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                  <Store size={18} color="#2563EB" />
                  <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, color: '#0F172A' }}>
                    Cập nhật giờ mở cửa & giới thiệu
                  </h4>
                </div>
                <p style={{ margin: 0, fontSize: '0.82rem', color: '#64748B', lineHeight: 1.4 }}>
                  Chỉnh sửa mô tả, số hotline và giờ hoạt động để khách tham quan nắm bắt thông tin chính xác nhất.
                </p>
              </div>

              <div
                onClick={() => setActiveSubTab('promotions')}
                style={{
                  border: '1px solid #E2E8F0',
                  borderRadius: '12px',
                  padding: '16px',
                  cursor: 'pointer',
                  background: '#F8FAFC',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                  <Tag size={18} color="#DC2626" />
                  <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, color: '#0F172A' }}>
                    Đăng chương trình ưu đãi mới
                  </h4>
                </div>
                <p style={{ margin: 0, fontSize: '0.82rem', color: '#64748B', lineHeight: 1.4 }}>
                  Tạo mã giảm giá, mức chiết khấu % và thông báo khuyến mãi trong tuần đến khách hàng.
                </p>
              </div>

              <div
                onClick={() => setActiveSubTab('control')}
                style={{
                  border: '1px solid #E2E8F0',
                  borderRadius: '12px',
                  padding: '16px',
                  cursor: 'pointer',
                  background: '#F8FAFC',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                  <Gamepad2 size={18} color="#16A34A" />
                  <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, color: '#0F172A' }}>
                    Giám sát vị trí & điều khiển robot
                  </h4>
                </div>
                <p style={{ margin: 0, fontSize: '0.82rem', color: '#64748B', lineHeight: 1.4 }}>
                  Xem robot đang ở đâu trên sơ đồ tầng, tiếp quản điều khiển khi cần giải tỏa tắc nghẽn.
                </p>
              </div>
            </div>
          </div>

        </div>
      )}

      {/* ==================== 3. SUBTAB: STORE INFO EDITOR ==================== */}
      {activeSubTab === 'store-info' && (
        <div className="card-clean" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ margin: '0 0 4px 0', fontSize: '1.2rem', fontWeight: 800, color: '#0F172A' }}>
                Quản Lý Thông Tin Gian Hàng
              </h3>
              <p style={{ margin: 0, fontSize: '0.86rem', color: '#64748B' }}>
                Nhân viên được phép chỉnh sửa tên hiển thị, mô tả, hotline và giờ mở cửa trong phạm vi được phân công.
              </p>
            </div>

            {/* Store selector if multiple */}
            {stores.length > 1 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.84rem', fontWeight: 600, color: '#475569' }}>Chọn gian hàng:</span>
                <select
                  value={selectedStoreId}
                  onChange={(e) => handleSelectStore(e.target.value)}
                  style={{
                    padding: '8px 12px',
                    borderRadius: '8px',
                    border: '1px solid #CBD5E1',
                    fontSize: '0.88rem',
                    fontWeight: 600,
                  }}
                >
                  {stores.map(s => (
                    <option key={s.id} value={s.id}>{s.name} ({s.id})</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {storeSuccessMsg && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#F0FDF4', color: '#166534', padding: '12px 16px', borderRadius: '8px', marginBottom: '16px', border: '1px solid #BBF7D0', fontSize: '0.88rem' }}>
              <CheckCircle2 size={18} />
              <span>{storeSuccessMsg}</span>
            </div>
          )}

          {storeErrorMsg && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#FEF2F2', color: '#991B1B', padding: '12px 16px', borderRadius: '8px', marginBottom: '16px', border: '1px solid #FECACA', fontSize: '0.88rem' }}>
              <AlertCircle size={18} />
              <span>{storeErrorMsg}</span>
            </div>
          )}

          <form onSubmit={handleSaveStore} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#334155', marginBottom: '6px' }}>
                  Tên Gian Hàng
                </label>
                <input
                  type="text"
                  value={storeForm.name || ''}
                  onChange={(e) => setStoreForm({ ...storeForm, name: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    border: '1.5px solid #CBD5E1',
                    fontSize: '0.92rem',
                    boxSizing: 'border-box',
                  }}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#334155', marginBottom: '6px' }}>
                  Hotline Liên Hệ Công Khai
                </label>
                <input
                  type="text"
                  value={storeForm.contact_phone || ''}
                  onChange={(e) => setStoreForm({ ...storeForm, contact_phone: e.target.value })}
                  placeholder="Ví dụ: 1900 6868"
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    border: '1.5px solid #CBD5E1',
                    fontSize: '0.92rem',
                    boxSizing: 'border-box',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#334155', marginBottom: '6px' }}>
                  Giờ Hoạt Động Hằng Ngày
                </label>
                <input
                  type="text"
                  value={storeForm.opening_hours || ''}
                  onChange={(e) => setStoreForm({ ...storeForm, opening_hours: e.target.value })}
                  placeholder="Ví dụ: 09:30 - 22:00"
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    border: '1.5px solid #CBD5E1',
                    fontSize: '0.92rem',
                    boxSizing: 'border-box',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#334155', marginBottom: '6px' }}>
                  Trạng Thái Hoạt Động
                </label>
                <select
                  value={storeForm.is_active ? 1 : 0}
                  onChange={(e) => setStoreForm({ ...storeForm, is_active: Number(e.target.value) })}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    border: '1.5px solid #CBD5E1',
                    fontSize: '0.92rem',
                    boxSizing: 'border-box',
                    background: '#FFFFFF',
                  }}
                >
                  <option value={1}>Đang Mở Cửa Đón Khách</option>
                  <option value={0}>Tạm Đóng Cửa / Bảo Trì</option>
                </select>
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#334155', marginBottom: '6px' }}>
                Mô Tả & Giới Thiệu Gian Hàng
              </label>
              <textarea
                value={storeForm.description || ''}
                onChange={(e) => setStoreForm({ ...storeForm, description: e.target.value })}
                rows={4}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: '1.5px solid #CBD5E1',
                  fontSize: '0.92rem',
                  fontFamily: 'inherit',
                  lineHeight: 1.45,
                  boxSizing: 'border-box',
                }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '10px' }}>
              <button
                type="submit"
                disabled={savingStore}
                className="btn-solid-blue"
                style={{ padding: '12px 24px', fontSize: '0.95rem', fontWeight: 700 }}
              >
                <Save size={18} />
                <span>{savingStore ? 'Đang lưu...' : 'Lưu Thay Đổi'}</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* ==================== 4. SUBTAB: PROMOTIONS ==================== */}
      {activeSubTab === 'promotions' && (
        <div className="card-clean" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ margin: '0 0 4px 0', fontSize: '1.2rem', fontWeight: 800, color: '#0F172A' }}>
                Quản Lý Khuyến Mãi Gian Hàng
              </h3>
              <p style={{ margin: 0, fontSize: '0.86rem', color: '#64748B' }}>
                Chỉ cho phép tạo và quản lý ưu đãi áp dụng cho gian hàng được giao ({assignedStoreNames}).
              </p>
            </div>

            <button
              onClick={() => setShowAddPromoModal(true)}
              className="btn-solid-blue"
              style={{ padding: '10px 16px', fontSize: '0.86rem', fontWeight: 700 }}
            >
              <Plus size={16} />
              <span>Thêm Khuyến Mãi Mới</span>
            </button>
          </div>

          {/* Promotion list */}
          {myPromotions.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '14px' }}>
              {myPromotions.map(promo => (
                <div
                  key={promo.id}
                  style={{
                    border: '1.5px solid #E2E8F0',
                    borderRadius: '12px',
                    padding: '16px',
                    background: '#FFFFFF',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    gap: '12px',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1E40AF', background: '#DBEAFE', padding: '2px 8px', borderRadius: '4px' }}>
                        {promo.store_name || selectedStoreId}
                      </span>
                      {promo.discount_percent > 0 && (
                        <span style={{ background: '#DC2626', color: '#FFFFFF', padding: '2px 6px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
                          -{promo.discount_percent}%
                        </span>
                      )}
                    </div>
                    <h4 style={{ margin: '0 0 4px 0', fontSize: '1.05rem', fontWeight: 800, color: '#0F172A' }}>
                      {promo.title}
                    </h4>
                    <p style={{ margin: 0, fontSize: '0.84rem', color: '#475569', lineHeight: 1.4 }}>
                      {promo.description}
                    </p>
                    {promo.promo_code && (
                      <div style={{ marginTop: '8px', fontSize: '0.78rem', color: '#991B1B', fontWeight: 600 }}>
                        Mã: <code style={{ background: '#FEE2E2', padding: '2px 6px', borderRadius: '4px' }}>{promo.promo_code}</code>
                      </div>
                    )}
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid #F1F5F9', paddingTop: '10px' }}>
                    <button
                      onClick={() => handleDeletePromo(promo.id)}
                      style={{
                        background: '#FEF2F2',
                        border: '1px solid #FECACA',
                        color: '#DC2626',
                        borderRadius: '6px',
                        padding: '6px 12px',
                        fontSize: '0.78rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <Trash2 size={14} /> Xóa ưu đãi
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ padding: '36px', textAlign: 'center', color: '#64748B', background: '#F8FAFC', borderRadius: '12px' }}>
              Gian hàng hiện chưa có chương trình khuyến mãi nào. Hãy nhấn "Thêm Khuyến Mãi Mới" để tạo!
            </div>
          )}

          {/* Create Promo Modal */}
          {showAddPromoModal && (
            <div
              style={{
                position: 'fixed',
                inset: 0,
                backgroundColor: 'rgba(15, 23, 42, 0.6)',
                backdropFilter: 'blur(3px)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 9999,
                padding: '16px',
              }}
            >
              <div
                style={{
                  background: '#FFFFFF',
                  borderRadius: '16px',
                  width: '100%',
                  maxWidth: '480px',
                  padding: '24px',
                  boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
                }}
              >
                <h3 style={{ margin: '0 0 14px 0', fontSize: '1.2rem', fontWeight: 800, color: '#0F172A' }}>
                  Tạo Chương Trình Khuyến Mãi Mới
                </h3>

                {promoError && (
                  <div style={{ background: '#FEF2F2', color: '#991B1B', padding: '10px 14px', borderRadius: '8px', marginBottom: '14px', fontSize: '0.84rem' }}>
                    {promoError}
                  </div>
                )}

                <form onSubmit={handleCreatePromo} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, marginBottom: '4px' }}>
                      Tên Chương Trình (VD: Sale Giữa Mùa 30%)
                    </label>
                    <input
                      type="text"
                      value={newPromo.title}
                      onChange={(e) => setNewPromo({ ...newPromo, title: e.target.value })}
                      required
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1.5px solid #CBD5E1', boxSizing: 'border-box' }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, marginBottom: '4px' }}>
                      Mô Tả Chi Tiết Ưu Đãi
                    </label>
                    <textarea
                      value={newPromo.description}
                      onChange={(e) => setNewPromo({ ...newPromo, description: e.target.value })}
                      rows={3}
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1.5px solid #CBD5E1', boxSizing: 'border-box' }}
                    />
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, marginBottom: '4px' }}>
                        % Giảm Giá
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={newPromo.discountPercent}
                        onChange={(e) => setNewPromo({ ...newPromo, discountPercent: Number(e.target.value) })}
                        style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1.5px solid #CBD5E1', boxSizing: 'border-box' }}
                      />
                    </div>

                    <div>
                      <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, marginBottom: '4px' }}>
                        Mã Ưu Đãi (Nếu Có)
                      </label>
                      <input
                        type="text"
                        placeholder="VD: UNIQLO30"
                        value={newPromo.promoCode}
                        onChange={(e) => setNewPromo({ ...newPromo, promoCode: e.target.value })}
                        style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1.5px solid #CBD5E1', boxSizing: 'border-box' }}
                      />
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
                    <button
                      type="button"
                      onClick={() => setShowAddPromoModal(false)}
                      style={{ padding: '8px 16px', background: '#F1F5F9', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 600 }}
                    >
                      Hủy
                    </button>
                    <button
                      type="submit"
                      disabled={savingPromo}
                      className="btn-solid-blue"
                      style={{ padding: '8px 18px', fontWeight: 700 }}
                    >
                      {savingPromo ? 'Đang tạo...' : 'Tạo Khuyến Mãi'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ==================== 5. SUBTAB: ROBOT TELEMETRY & CONTROL ==================== */}
      {activeSubTab === 'control' && (
        <div className="card-clean" style={{ padding: '24px' }}>
          <h3 style={{ margin: '0 0 4px 0', fontSize: '1.2rem', fontWeight: 800, color: '#0F172A' }}>
            Giám Sát Vận Hành & Điều Khiển Robot
          </h3>
          <p style={{ margin: '0 0 20px 0', fontSize: '0.86rem', color: '#64748B' }}>
            Chỉ nhân viên được xác thực phiên làm việc mới có quyền quan sát telemetry và gửi lệnh điều khiển.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
            <div style={{ background: '#F8FAFC', padding: '16px', borderRadius: '12px', border: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600 }}>Tình Trạng Kết Nối</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: connectionStatus === 'CONNECTED' ? '#16A34A' : '#F59E0B', marginTop: '4px' }}>
                {connectionStatus === 'CONNECTED' ? '🟢 KẾT NỐI TRỰC TIẾP' : '🟡 CHẾ ĐỘ GIẢ LẬP VIRTUAL'}
              </div>
            </div>

            <div style={{ background: '#F8FAFC', padding: '16px', borderRadius: '12px', border: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600 }}>Trạng Thái An Toàn LiDAR/Camera</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: isEmergencyStopped ? '#DC2626' : (isSafetyBlocked ? '#EA580C' : '#16A34A'), marginTop: '4px' }}>
                {isEmergencyStopped ? '🔴 DỪNG KHẨN CẤP (E-STOP)' : (isSafetyBlocked ? '🟠 PHÁT HIỆN VẬT CẢN' : '🟢 AN TOÀN TUYỆT ĐỐI')}
              </div>
            </div>

            <div style={{ background: '#F8FAFC', padding: '16px', borderRadius: '12px', border: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600 }}>Tốc Độ Thiết Đặt</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#0F172A', marginTop: '4px' }}>
                {((settings.defaultSpeed || 0.35) * 100).toFixed(0)}% ({settings.defaultSpeed || 0.35} m/s)
              </div>
            </div>
          </div>

          {/* Emergency Stop & Reset Controls */}
          <div style={{ display: 'flex', gap: '12px', marginTop: '20px', flexWrap: 'wrap' }}>
            <button
              onClick={() => {
                RobotSocket.getInstance().sendEmergencyStop();
                RobotApi.emergencyStop(host, port);
              }}
              style={{
                flex: 1,
                padding: '14px 20px',
                background: '#DC2626',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '10px',
                fontSize: '0.95rem',
                fontWeight: 800,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: '0 4px 6px -1px rgba(220, 38, 38, 0.3)',
              }}
            >
              <ShieldAlert size={20} />
              <span>DỪNG KHẨN CẤP (E-STOP)</span>
            </button>

            <button
              onClick={() => {
                RobotSocket.getInstance().sendEmergencyReset();
                RobotApi.emergencyReset(host, port, token);
              }}
              style={{
                padding: '14px 20px',
                background: '#F1F5F9',
                color: '#334155',
                border: '1.5px solid #CBD5E1',
                borderRadius: '10px',
                fontSize: '0.95rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <RefreshCw size={18} />
              <span>Khôi Phục Trạng Thái (Reset)</span>
            </button>
          </div>
        </div>
      )}

    </div>
  );
};
