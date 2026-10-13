import React, { useState, useEffect } from 'react';
import { useRobotStore } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { AdminUser, AuditLog, MapGraphData, MallStore, Promotion, HealthResponse } from '../../types/protocol';
import {
  ShieldCheck,
  Users,
  Compass,
  FileText,
  Database,
  Plus,
  Lock,
  Unlock,
  Play,
  RotateCcw,
  CheckCircle,
  AlertTriangle,
  Server,
  Activity,
  Store,
  LayoutDashboard,
  Tag,
  Cpu,
  Camera,
  Bot,
  Radio,
  CheckCircle2,
  XCircle,
  RefreshCw,
} from 'lucide-react';

export const AdminTab: React.FC = () => {
  const { pairedRobot, currentUser, pois, connectionStatus } = useRobotStore();
  const [subTab, setSubTab] = useState<'overview' | 'stores' | 'users' | 'map_patrol' | 'audit' | 'database'>('overview');
  
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [stores, setStores] = useState<MallStore[]>([]);
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [graphData, setGraphData] = useState<MapGraphData | null>(null);
  const [patrolStatus, setPatrolStatus] = useState<any>(null);
  const [backupResult, setBackupResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // New user form states
  const [newUsername, setNewUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newFullName, setNewFullName] = useState('');
  const [newRole, setNewRole] = useState<'staff' | 'admin'>('staff');
  const [selectedStoreIds, setSelectedStoreIds] = useState<string[]>([]);
  const [userFormMsg, setUserFormMsg] = useState<{ type: 'ok' | 'err'; text: string } | null>(null);

  const host = pairedRobot?.host || window.location.hostname || 'localhost';
  const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
  const token = currentUser?.token || pairedRobot?.token || '';

  const loadData = async () => {
    try {
      const s = await RobotApi.getStores(host, port);
      setStores(s || []);
      const p = await RobotApi.getPromotions(host, port);
      setPromotions(p || []);
      const h = await RobotApi.getHealth(host, port);
      setHealth(h);
      if (token) {
        const u = await RobotApi.getAdminUsers(host, port, token);
        setUsers(u || []);
        const logs = await RobotApi.getAuditLogs(host, port, token);
        setAuditLogs(logs || []);
      }
      const g = await RobotApi.getMapGraph(host, port);
      setGraphData(g);
      const patrol = await RobotApi.getPatrolStatus(host, port);
      setPatrolStatus(patrol);
    } catch (e) {
      console.warn('Failed to load admin data:', e);
    }
  };

  useEffect(() => {
    loadData();
  }, [token]);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUsername.trim() || !newPassword || !newFullName.trim()) {
      setUserFormMsg({ type: 'err', text: 'Vui lòng điền đủ thông tin người dùng' });
      return;
    }
    setUserFormMsg(null);
    try {
      const res = await RobotApi.createAdminUser(
        host,
        port,
        {
          username: newUsername.trim(),
          password: newPassword,
          fullName: newFullName.trim(),
          role: newRole,
          assignedStoreIds: selectedStoreIds,
        },
        token
      );
      if (res.success) {
        setUserFormMsg({ type: 'ok', text: `Tạo tài khoản ${newUsername} thành công!` });
        setNewUsername('');
        setNewPassword('');
        setNewFullName('');
        setSelectedStoreIds([]);
        loadData();
      } else {
        setUserFormMsg({ type: 'err', text: res.message || 'Lỗi khi tạo người dùng' });
      }
    } catch (err: any) {
      setUserFormMsg({ type: 'err', text: err.message });
    }
  };

  const handleToggleUser = async (userId: string, currentActive: boolean) => {
    const ok = await RobotApi.toggleUserStatus(host, port, userId, !currentActive, token);
    if (ok) {
      loadData();
    }
  };

  const handleToggleStore = async (storeId: string, currentActive: boolean) => {
    try {
      const res = await RobotApi.updateStore(host, port, storeId, { is_active: currentActive ? 0 : 1 }, token);
      if (res.success) {
        loadData();
      }
    } catch (e: any) {
      alert(`Lỗi: ${e.message}`);
    }
  };

  const handleTriggerPatrol = async () => {
    try {
      const res = await RobotApi.triggerPatrol(host, port, token);
      if (res.success) {
        alert('Đã kích hoạt chế độ tuần tra hành lang TTTM!');
        loadData();
      } else {
        alert(res.message || 'Không thể kích hoạt tuần tra lúc này.');
      }
    } catch (e: any) {
      alert(`Lỗi: ${e.message}`);
    }
  };

  const handleBackupDB = async () => {
    setLoading(true);
    try {
      const res = await RobotApi.backupDatabase(host, port, token);
      if (res.success && res.backupPath) {
        setBackupResult(res.backupPath);
        loadData();
      } else {
        alert('Sao lưu thất bại');
      }
    } catch (e: any) {
      alert(`Lỗi: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const activeStoresCount = stores.filter(s => Boolean(s.is_active)).length;
  const activeStaffCount = users.filter(u => u.role === 'staff' && Boolean(u.is_active)).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px', width: '100%', maxWidth: '1080px', margin: '0 auto' }}>
      
      {/* Top Banner */}
      <div style={{
        background: 'linear-gradient(135deg, #1E293B 0%, #0F172A 100%)',
        color: '#FFFFFF',
        padding: '20px 24px',
        borderRadius: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '14px',
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            background: 'rgba(56, 189, 248, 0.2)',
            padding: '10px',
            borderRadius: '12px',
            border: '1px solid rgba(56, 189, 248, 0.4)'
          }}>
            <ShieldCheck size={26} color="#38BDF8" />
          </div>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800 }}>TRUNG TÂM QUẢN TRỊ HỆ THỐNG ROBOT</h2>
            <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: '#94A3B8' }}>
              Quyền Quản Trị Viên (Admin) • Kiểm soát người dùng, phân bổ gian hàng, bản đồ graph, tuần tra và an ninh dữ liệu
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={loadData}
            title="Làm mới dữ liệu"
            style={{
              background: 'rgba(255,255,255,0.12)',
              border: 'none',
              borderRadius: '8px',
              padding: '8px 12px',
              color: '#FFFFFF',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.78rem',
              fontWeight: 700,
            }}
          >
            <RefreshCw size={14} /> Làm Mới
          </button>
          <span style={{
            background: '#FEF3C7',
            color: '#B45309',
            padding: '6px 12px',
            borderRadius: '8px',
            fontSize: '0.75rem',
            fontWeight: 800,
          }}>
            ROLE: ADMIN
          </span>
        </div>
      </div>

      {/* Sub-nav Tabs */}
      <div style={{
        display: 'flex',
        gap: '8px',
        background: '#FFFFFF',
        padding: '6px',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        overflowX: 'auto',
        border: '1px solid #E2E8F0',
      }}>
        {[
          { id: 'overview', label: 'Tổng Quan Hệ Thống', icon: <LayoutDashboard size={16} /> },
          { id: 'stores', label: `Gian Hàng (${stores.length})`, icon: <Store size={16} /> },
          { id: 'users', label: `Tài Khoản & Nhân Viên (${users.length})`, icon: <Users size={16} /> },
          { id: 'map_patrol', label: 'Bản Đồ Graph & Tuần Tra', icon: <Compass size={16} /> },
          { id: 'audit', label: `Nhật Ký Audit (${auditLogs.length})`, icon: <FileText size={16} /> },
          { id: 'database', label: 'Cơ Sở Dữ Liệu & Sao Lưu', icon: <Database size={16} /> },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setSubTab(tab.id as any)}
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              padding: '10px 14px',
              background: subTab === tab.id ? '#2563EB' : 'transparent',
              color: subTab === tab.id ? '#FFFFFF' : '#475569',
              border: 'none',
              borderRadius: '8px',
              fontSize: '0.8rem',
              fontWeight: 700,
              cursor: 'pointer',
              whiteSpace: 'nowrap'
            }}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* ==================== SUBTAB: OVERVIEW ==================== */}
      {subTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          
          {/* 4 Primary System Counters */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
            <div className="card-clean" style={{ padding: '18px', borderLeft: '4px solid #2563EB' }}>
              <div style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600 }}>Tổng Gian Hàng TTTM</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0F172A', marginTop: '4px' }}>
                {stores.length}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#16A34A', fontWeight: 600, marginTop: '2px' }}>
                {activeStoresCount} gian hàng đang mở cửa
              </div>
            </div>

            <div className="card-clean" style={{ padding: '18px', borderLeft: '4px solid #DC2626' }}>
              <div style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600 }}>Khuyến Mãi Đang Chạy</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0F172A', marginTop: '4px' }}>
                {promotions.length}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: '2px' }}>
                Đồng bộ hiển thị cho khách
              </div>
            </div>

            <div className="card-clean" style={{ padding: '18px', borderLeft: '4px solid #16A34A' }}>
              <div style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600 }}>Nhân Viên Vận Hành</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0F172A', marginTop: '4px' }}>
                {activeStaffCount}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#16A34A', fontWeight: 600, marginTop: '2px' }}>
                Phân quyền theo phạm vi gian hàng
              </div>
            </div>

            <div className="card-clean" style={{ padding: '18px', borderLeft: '4px solid #0EA5E9' }}>
              <div style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600 }}>Tình Trạng Máy Chủ</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A', marginTop: '8px' }}>
                {health?.status === 'ok' ? '🟢 ONLINE (2.0.0)' : '🟢 SẴN SÀNG'}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '2px' }}>
                SQLite WAL • FastAPI • RBAC
              </div>
            </div>
          </div>

          {/* System Services Status Grid */}
          <div className="card-clean" style={{ padding: '20px 24px' }}>
            <h3 style={{ margin: '0 0 14px 0', fontSize: '1.05rem', fontWeight: 800, color: '#0F172A' }}>
              Tình Trạng Dịch Vụ & Phần Cứng
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', background: '#F8FAFC', borderRadius: '10px', border: '1px solid #E2E8F0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Server size={18} color="#2563EB" />
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0F172A' }}>FastAPI Backend Server</div>
                    <div style={{ fontSize: '0.72rem', color: '#64748B' }}>Cổng 8765 / WebSocket API</div>
                  </div>
                </div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#16A34A', background: '#DCFCE7', padding: '2px 8px', borderRadius: '4px' }}>HOẠT ĐỘNG</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', background: '#F8FAFC', borderRadius: '10px', border: '1px solid #E2E8F0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Database size={18} color="#16A34A" />
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0F172A' }}>Cơ Sở Dữ Liệu SQLite</div>
                    <div style={{ fontSize: '0.72rem', color: '#64748B' }}>WAL Mode / Foreign Keys On</div>
                  </div>
                </div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#16A34A', background: '#DCFCE7', padding: '2px 8px', borderRadius: '4px' }}>KẾT NỐI</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', background: '#F8FAFC', borderRadius: '10px', border: '1px solid #E2E8F0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Camera size={18} color="#9333EA" />
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0F172A' }}>Hệ Thống Camera & Stream</div>
                    <div style={{ fontSize: '0.72rem', color: '#64748B' }}>MJPEG Stream Ticket Token</div>
                  </div>
                </div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#16A34A', background: '#DCFCE7', padding: '2px 8px', borderRadius: '4px' }}>BẢO MẬT</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', background: '#F8FAFC', borderRadius: '10px', border: '1px solid #E2E8F0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Bot size={18} color="#EA580C" />
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0F172A' }}>Trợ Lý Ảo OpenRouter AI</div>
                    <div style={{ fontSize: '0.72rem', color: '#64748B' }}>Grounded RAG SQLite Context</div>
                  </div>
                </div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#16A34A', background: '#DCFCE7', padding: '2px 8px', borderRadius: '4px' }}>SẴN SÀNG</span>
              </div>
            </div>
          </div>

          {/* Quick Admin Actions */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              onClick={() => setSubTab('users')}
              className="btn-solid-blue"
              style={{ padding: '10px 18px', fontSize: '0.86rem' }}
            >
              <Plus size={16} />
              <span>Tạo Tài Khoản Nhân Viên Mới</span>
            </button>
            <button
              onClick={handleBackupDB}
              disabled={loading}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: '#10B981',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                padding: '10px 18px',
                fontSize: '0.86rem',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              <Database size={16} />
              <span>Sao Lưu Cơ Sở Dữ Liệu Ngay</span>
            </button>
            <button
              onClick={handleTriggerPatrol}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: '#F1F5F9',
                color: '#334155',
                border: '1px solid #CBD5E1',
                borderRadius: '8px',
                padding: '10px 18px',
                fontSize: '0.86rem',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              <Play size={16} color="#2563EB" />
              <span>Kích Hoạt Tuần Tra Robot TTTM</span>
            </button>
          </div>
        </div>
      )}

      {/* ==================== SUBTAB: STORES CATALOG ==================== */}
      {subTab === 'stores' && (
        <div className="card-clean" style={{ padding: '20px 24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#0F172A' }}>
                Danh Sách Gian Hàng & Trạng Thái Hoạt Động
              </h3>
              <p style={{ margin: '4px 0 0 0', fontSize: '0.82rem', color: '#64748B' }}>
                Quản trị viên có toàn quyền bật/tắt trạng thái mở cửa của tất cả các gian hàng trên sơ đồ TTTM.
              </p>
            </div>
            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#2563EB', background: '#EFF6FF', padding: '4px 10px', borderRadius: '6px' }}>
              Tổng: {stores.length} gian hàng
            </span>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #E2E8F0', textAlign: 'left', color: '#64748B' }}>
                  <th style={{ padding: '10px 8px' }}>Mã / ID</th>
                  <th style={{ padding: '10px 8px' }}>Tên Gian Hàng</th>
                  <th style={{ padding: '10px 8px' }}>Ngành Hàng</th>
                  <th style={{ padding: '10px 8px' }}>Hotline</th>
                  <th style={{ padding: '10px 8px' }}>Giờ Mở Cửa</th>
                  <th style={{ padding: '10px 8px', textAlign: 'right' }}>Trạng Thái Mở Cửa</th>
                </tr>
              </thead>
              <tbody>
                {stores.map(store => (
                  <tr key={store.id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                    <td style={{ padding: '10px 8px', fontFamily: 'monospace', fontWeight: 700, color: '#2563EB' }}>
                      {store.id}
                    </td>
                    <td style={{ padding: '10px 8px', fontWeight: 700, color: '#0F172A' }}>
                      {store.name}
                    </td>
                    <td style={{ padding: '10px 8px', color: '#475569' }}>
                      {store.category}
                    </td>
                    <td style={{ padding: '10px 8px', color: '#64748B' }}>
                      {store.contact_phone || '1900 6868'}
                    </td>
                    <td style={{ padding: '10px 8px', color: '#64748B' }}>
                      {store.opening_hours || '09:30 - 22:00'}
                    </td>
                    <td style={{ padding: '10px 8px', textAlign: 'right' }}>
                      <button
                        onClick={() => handleToggleStore(store.id, Boolean(store.is_active))}
                        style={{
                          background: store.is_active ? '#DCFCE7' : '#FEE2E2',
                          color: store.is_active ? '#15803D' : '#DC2626',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '5px 10px',
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          cursor: 'pointer',
                        }}
                      >
                        {store.is_active ? 'Đang Mở Cửa' : 'Đã Đóng Cửa'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ==================== SUBTAB: USERS & STAFF MANAGEMENT ==================== */}
      {subTab === 'users' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1.8fr', gap: '14px' }}>
          
          {/* Create User Card */}
          <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', border: '1px solid #E2E8F0' }}>
            <h3 style={{ margin: '0 0 12px', fontSize: '0.95rem', fontWeight: 800, color: '#0F172A', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Plus size={16} color="#2563EB" />
              <span>TẠO TÀI KHOẢN MỚI</span>
            </h3>

            {userFormMsg && (
              <div style={{
                padding: '8px 12px',
                borderRadius: '8px',
                fontSize: '0.78rem',
                fontWeight: 600,
                marginBottom: '10px',
                background: userFormMsg.type === 'ok' ? '#DCFCE7' : '#FEE2E2',
                color: userFormMsg.type === 'ok' ? '#15803D' : '#DC2626'
              }}>
                {userFormMsg.text}
              </div>
            )}

            <form onSubmit={handleCreateUser} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '3px' }}>
                  Tên Đăng Nhập
                </label>
                <input
                  type="text"
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  placeholder="Ví dụ: staff_uniqlo"
                  style={{ width: '100%', padding: '7px 9px', borderRadius: '6px', border: '1.5px solid #CBD5E1', fontSize: '0.8rem', boxSizing: 'border-box' }}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '3px' }}>
                  Mật Khẩu
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Nhập mật khẩu..."
                  style={{ width: '100%', padding: '7px 9px', borderRadius: '6px', border: '1.5px solid #CBD5E1', fontSize: '0.8rem', boxSizing: 'border-box' }}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '3px' }}>
                  Họ và Tên
                </label>
                <input
                  type="text"
                  value={newFullName}
                  onChange={(e) => setNewFullName(e.target.value)}
                  placeholder="Nguyễn Văn A"
                  style={{ width: '100%', padding: '7px 9px', borderRadius: '6px', border: '1.5px solid #CBD5E1', fontSize: '0.8rem', boxSizing: 'border-box' }}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '3px' }}>
                  Vai Trò (Role)
                </label>
                <select
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value as any)}
                  style={{ width: '100%', padding: '7px 9px', borderRadius: '6px', border: '1.5px solid #CBD5E1', fontSize: '0.8rem', boxSizing: 'border-box' }}
                >
                  <option value="staff">Nhân Viên Gian Hàng (Staff)</option>
                  <option value="admin">Quản Trị Viên Hệ Thống (Admin)</option>
                </select>
              </div>

              {newRole === 'staff' && (
                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '3px' }}>
                    Gán Gian Hàng Phụ Trách
                  </label>
                  <div style={{ maxHeight: '110px', overflowY: 'auto', border: '1.5px solid #CBD5E1', borderRadius: '6px', padding: '6px' }}>
                    {pois.filter(p => !p.is_staff_only).map(store => (
                      <label key={store.id} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', padding: '3px 0', cursor: 'pointer' }}>
                        <input
                          type="checkbox"
                          checked={selectedStoreIds.includes(store.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedStoreIds([...selectedStoreIds, store.id]);
                            } else {
                              setSelectedStoreIds(selectedStoreIds.filter(id => id !== store.id));
                            }
                          }}
                        />
                        <span>{store.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              <button
                type="submit"
                style={{
                  marginTop: '6px',
                  padding: '9px',
                  background: '#2563EB',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '6px',
                  fontWeight: 700,
                  fontSize: '0.82rem',
                  cursor: 'pointer'
                }}
              >
                Xác Nhận Tạo Tài Khoản
              </button>
            </form>
          </div>

          {/* User List Table */}
          <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', border: '1px solid #E2E8F0' }}>
            <h3 style={{ margin: '0 0 12px', fontSize: '0.95rem', fontWeight: 800, color: '#0F172A' }}>
              DANH SÁCH TÀI KHOẢN ({users.length})
            </h3>

            <div style={{ maxHeight: '420px', overflowY: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1.5px solid #E2E8F0', textAlign: 'left', color: '#64748B' }}>
                    <th style={{ padding: '8px 4px' }}>Username</th>
                    <th style={{ padding: '8px 4px' }}>Họ Tên</th>
                    <th style={{ padding: '8px 4px' }}>Quyền</th>
                    <th style={{ padding: '8px 4px' }}>Cửa Hàng</th>
                    <th style={{ padding: '8px 4px', textAlign: 'right' }}>Thao Tác</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                      <td style={{ padding: '8px 4px', fontWeight: 700 }}>{u.username}</td>
                      <td style={{ padding: '8px 4px', color: '#334155' }}>{u.full_name}</td>
                      <td style={{ padding: '8px 4px' }}>
                        <span style={{
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontSize: '0.7rem',
                          fontWeight: 700,
                          background: u.role === 'admin' ? '#FEF3C7' : '#EFF6FF',
                          color: u.role === 'admin' ? '#B45309' : '#1D4ED8'
                        }}>
                          {u.role.toUpperCase()}
                        </span>
                      </td>
                      <td style={{ padding: '8px 4px', color: '#64748B' }}>
                        {u.assignedStoreIds && u.assignedStoreIds.length > 0
                          ? u.assignedStoreIds.join(', ')
                          : '—'}
                      </td>
                      <td style={{ padding: '8px 4px', textAlign: 'right' }}>
                        <button
                          onClick={() => handleToggleUser(u.id, Boolean(u.is_active))}
                          title={u.is_active ? 'Khóa tài khoản' : 'Kích hoạt lại'}
                          style={{
                            background: u.is_active ? '#DCFCE7' : '#FEE2E2',
                            color: u.is_active ? '#15803D' : '#DC2626',
                            border: 'none',
                            borderRadius: '4px',
                            padding: '3px 8px',
                            fontSize: '0.7rem',
                            fontWeight: 700,
                            cursor: 'pointer'
                          }}
                        >
                          {u.is_active ? 'Hoạt Động' : 'Đã Khóa'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}

      {/* ==================== SUBTAB: MAP GRAPH & PATROL ==================== */}
      {subTab === 'map_patrol' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
          
          <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', border: '1px solid #E2E8F0' }}>
            <h3 style={{ margin: '0 0 10px', fontSize: '0.95rem', fontWeight: 800, color: '#0F172A', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Compass size={16} color="#2563EB" />
              <span>CẤU HÌNH TUẦN TRA CONCOURSE (5 PHÚT TỰ ĐỘNG)</span>
            </h3>
            <p style={{ fontSize: '0.78rem', color: '#64748B', lineHeight: 1.4, margin: '0 0 12px' }}>
              Khi robot ở trạng thái nghỉ không có yêu cầu dẫn đường hoặc giao hàng trong 5 phút và cảm biến an toàn CLEAR, robot sẽ tự động tuần tra qua các điểm waypoint được định nghĩa.
            </p>

            <div style={{ background: '#F8FAFC', borderRadius: '10px', padding: '12px', border: '1px solid #E2E8F0', marginBottom: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.8rem' }}>
                <span style={{ fontWeight: 600, color: '#475569' }}>Trạng Thái Tuần Tra:</span>
                <span style={{ fontWeight: 800, color: patrolStatus?.is_patrolling ? '#15803D' : '#64748B' }}>
                  {patrolStatus?.is_patrolling ? '⚡ ĐANG TUẦN TRA' : 'CHỜ (IDLE)'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.8rem' }}>
                <span style={{ fontWeight: 600, color: '#475569' }}>Waypoint Hiện Tại:</span>
                <span style={{ fontWeight: 700 }}>{patrolStatus?.current_waypoint_idx !== undefined ? `Điểm số ${patrolStatus.current_waypoint_idx}` : '0'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ fontWeight: 600, color: '#475569' }}>Tự Động Kích Hoạt Sau:</span>
                <span style={{ fontWeight: 700 }}>{patrolStatus?.idle_timeout_seconds || 300} giây</span>
              </div>
            </div>

            <button
              onClick={handleTriggerPatrol}
              style={{
                width: '100%',
                padding: '10px',
                background: '#2563EB',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                fontWeight: 700,
                fontSize: '0.82rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px'
              }}
            >
              <Play size={16} />
              <span>Kích Hoạt Tuần Tra Thủ Công Ngay</span>
            </button>
          </div>

          <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', border: '1px solid #E2E8F0' }}>
            <h3 style={{ margin: '0 0 10px', fontSize: '0.95rem', fontWeight: 800, color: '#0F172A', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Compass size={16} color="#16A34A" />
              <span>SƠ ĐỒ NODES & CẠNH ĐIỀU HƯỚNG</span>
            </h3>

            <div style={{ fontSize: '0.8rem', color: '#64748B', marginBottom: '10px' }}>
              Số nút (Nodes): <strong>{graphData?.nodes?.length || 0}</strong> • Số cạnh (Edges): <strong>{graphData?.edges?.length || 0}</strong>
            </div>

            <div style={{ maxHeight: '280px', overflowY: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.75rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #E2E8F0', textAlign: 'left', color: '#64748B' }}>
                    <th style={{ padding: '6px 4px' }}>Node ID</th>
                    <th style={{ padding: '6px 4px' }}>Tọa Độ (X, Y)</th>
                    <th style={{ padding: '6px 4px' }}>Tên Nhãn</th>
                  </tr>
                </thead>
                <tbody>
                  {graphData?.nodes?.map(n => (
                    <tr key={n.id} style={{ borderBottom: '1px solid #F8FAFC' }}>
                      <td style={{ padding: '6px 4px', fontFamily: 'monospace', fontWeight: 600 }}>{n.id}</td>
                      <td style={{ padding: '6px 4px' }}>({n.x}, {n.y})</td>
                      <td style={{ padding: '6px 4px', color: '#334155' }}>{n.label || 'Waypoint'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}

      {/* ==================== SUBTAB: AUDIT LOGS ==================== */}
      {subTab === 'audit' && (
        <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '18px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', border: '1px solid #E2E8F0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 800, color: '#0F172A', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <FileText size={18} color="#2563EB" />
              <span>NHẬT KÝ KIỂM TOÁN HỆ THỐNG (AUDIT LOGS)</span>
            </h3>
            <span style={{ fontSize: '0.75rem', color: '#64748B' }}>
              Ghi nhận các thao tác đăng nhập, tạo tài khoản, chỉnh sửa gian hàng & sao lưu dữ liệu
            </span>
          </div>

          <div style={{ maxHeight: '420px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem' }}>
              <thead>
                <tr style={{ borderBottom: '1.5px solid #E2E8F0', textAlign: 'left', color: '#64748B' }}>
                  <th style={{ padding: '8px 6px' }}>Thời Gian</th>
                  <th style={{ padding: '8px 6px' }}>Người Dùng</th>
                  <th style={{ padding: '8px 6px' }}>Quyền</th>
                  <th style={{ padding: '8px 6px' }}>Hành Động</th>
                  <th style={{ padding: '8px 6px' }}>Đối Tượng</th>
                  <th style={{ padding: '8px 6px' }}>Chi Tiết</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map(log => (
                  <tr key={log.id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                    <td style={{ padding: '8px 6px', whiteSpace: 'nowrap', color: '#64748B' }}>{log.created_at}</td>
                    <td style={{ padding: '8px 6px', fontWeight: 700 }}>{log.username || 'System'}</td>
                    <td style={{ padding: '8px 6px' }}>
                      <span style={{
                        padding: '2px 5px',
                        borderRadius: '4px',
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        background: log.role === 'admin' ? '#FEF3C7' : '#EFF6FF',
                        color: log.role === 'admin' ? '#B45309' : '#1D4ED8'
                      }}>
                        {log.role || 'GUEST'}
                      </span>
                    </td>
                    <td style={{ padding: '8px 6px', fontWeight: 600, color: '#0F172A' }}>{log.action}</td>
                    <td style={{ padding: '8px 6px', color: '#475569' }}>{log.resource}</td>
                    <td style={{ padding: '8px 6px', color: '#64748B' }}>{log.details || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ==================== SUBTAB: DATABASE & BACKUP ==================== */}
      {subTab === 'database' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '14px' }}>
          
          <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '18px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', border: '1px solid #E2E8F0' }}>
            <h3 style={{ margin: '0 0 10px', fontSize: '0.95rem', fontWeight: 800, color: '#0F172A', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Database size={18} color="#10B981" />
              <span>SAO LƯU DỮ LIỆU SQLITE TOÀN VẸN</span>
            </h3>
            <p style={{ fontSize: '0.78rem', color: '#64748B', lineHeight: 1.4, margin: '0 0 14px' }}>
              Tạo bản snapshot sao lưu an toàn toàn bộ các bảng người dùng, phiên đăng nhập, gian hàng, khuyến mãi và nhật ký kiểm toán vào thư mục lưu trữ an toàn của hệ thống.
            </p>

            <button
              onClick={handleBackupDB}
              disabled={loading}
              style={{
                width: '100%',
                padding: '11px',
                background: '#10B981',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                fontWeight: 700,
                fontSize: '0.85rem',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              <Server size={16} />
              <span>{loading ? 'Đang tạo bản sao lưu...' : 'Tạo Bản Sao Lưu Ngay (Backup DB)'}</span>
            </button>

            {backupResult && (
              <div style={{
                marginTop: '12px',
                padding: '10px 12px',
                background: '#ECFDF5',
                border: '1px solid #A7F3D0',
                borderRadius: '8px',
                color: '#065F46',
                fontSize: '0.78rem'
              }}>
                <div style={{ fontWeight: 800, display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                  <CheckCircle size={14} />
                  <span>Sao lưu thành công!</span>
                </div>
                <div style={{ wordBreak: 'break-all', fontFamily: 'monospace', fontSize: '0.72rem' }}>
                  Đường dẫn: {backupResult}
                </div>
              </div>
            )}
          </div>

          <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '18px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', border: '1px solid #E2E8F0' }}>
            <h3 style={{ margin: '0 0 10px', fontSize: '0.95rem', fontWeight: 800, color: '#0F172A', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Activity size={18} color="#2563EB" />
              <span>TÌNH TRẠNG MIGRATION & RÀNG BUỘC</span>
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {[
                { label: 'SQLite Mode', value: 'WAL (Write-Ahead Logging)' },
                { label: 'Foreign Keys Constraint', value: 'ENABLED (PRAGMA foreign_keys = ON)' },
                { label: 'Busy Timeout', value: '10,000 ms' },
                { label: 'Migration Version', value: 'Version 2 (Active)' },
                { label: 'OpenRouter AI Fallback', value: 'Local Vietnamese Rule Engine' },
              ].map(item => (
                <div key={item.label} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: '8px 10px',
                  background: '#F8FAFC',
                  borderRadius: '6px',
                  fontSize: '0.78rem'
                }}>
                  <span style={{ color: '#64748B', fontWeight: 600 }}>{item.label}:</span>
                  <span style={{ color: '#0F172A', fontWeight: 700 }}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

    </div>
  );
};
