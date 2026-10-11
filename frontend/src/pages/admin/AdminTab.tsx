import React, { useState, useEffect } from 'react';
import { useRobotStore } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { AdminUser, AuditLog, MapGraphData } from '../../types/protocol';
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
  Store
} from 'lucide-react';

export const AdminTab: React.FC = () => {
  const { pairedRobot, currentUser, pois } = useRobotStore();
  const [subTab, setSubTab] = useState<'users' | 'map_patrol' | 'audit' | 'database'>('users');
  const [users, setUsers] = useState<AdminUser[]>([]);
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

  const loadUsers = async () => {
    if (!token) return;
    try {
      const list = await RobotApi.getAdminUsers(host, port, token);
      setUsers(list);
    } catch (e) {}
  };

  const loadAuditLogs = async () => {
    if (!token) return;
    try {
      const logs = await RobotApi.getAuditLogs(host, port, token);
      setAuditLogs(logs);
    } catch (e) {}
  };

  const loadMapAndPatrol = async () => {
    try {
      const g = await RobotApi.getMapGraph(host, port);
      setGraphData(g);
      const p = await RobotApi.getPatrolStatus(host, port);
      setPatrolStatus(p);
    } catch (e) {}
  };

  useEffect(() => {
    loadUsers();
    loadMapAndPatrol();
    loadAuditLogs();
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
        await loadUsers();
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
      await loadUsers();
    }
  };

  const handleTriggerPatrol = async () => {
    try {
      const res = await RobotApi.triggerPatrol(host, port, token);
      if (res.success) {
        alert('Đã kích hoạt chế độ tuần tra hành lang TTTM!');
        await loadMapAndPatrol();
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
        await loadAuditLogs();
      } else {
        alert('Sao lưu thất bại');
      }
    } catch (e: any) {
      alert(`Lỗi: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', width: '100%', maxWidth: '1000px', margin: '0 auto' }}>
      
      {/* Top Banner */}
      <div style={{
        background: 'linear-gradient(135deg, #1E293B 0%, #0F172A 100%)',
        color: '#FFFFFF',
        padding: '18px 22px',
        borderRadius: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: 'rgba(56, 189, 248, 0.2)',
            padding: '10px',
            borderRadius: '12px',
            border: '1px solid rgba(56, 189, 248, 0.4)'
          }}>
            <ShieldCheck size={24} color="#38BDF8" />
          </div>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800 }}>TRUNG TÂM ĐIỀU HÀNH & QUẢN TRỊ HỆ THỐNG</h2>
            <p style={{ margin: '4px 0 0', fontSize: '0.75rem', color: '#94A3B8' }}>
              Quyền Quản Trị Viên (Admin) • Kiểm soát người dùng, phân bổ cửa hàng, bản đồ graph, tuần tra và dữ liệu
            </p>
          </div>
        </div>

        <span style={{
          background: 'rgba(255,255,255,0.1)',
          padding: '6px 12px',
          borderRadius: '8px',
          fontSize: '0.75rem',
          fontWeight: 700,
          letterSpacing: '0.5px'
        }}>
          ROLE: ADMIN
        </span>
      </div>

      {/* Sub-nav Tabs */}
      <div style={{
        display: 'flex',
        gap: '8px',
        background: '#FFFFFF',
        padding: '6px',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        overflowX: 'auto'
      }}>
        {[
          { id: 'users', label: 'Tài Khoản & Nhân Viên', icon: <Users size={16} /> },
          { id: 'map_patrol', label: 'Bản Đồ Graph & Tuần Tra', icon: <Compass size={16} /> },
          { id: 'audit', label: 'Nhật Ký Kiểm Toán (Audit)', icon: <FileText size={16} /> },
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

      {/* Tab 1: Users & Staff Management */}
      {subTab === 'users' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1.8fr', gap: '14px' }}>
          
          {/* Create User Card */}
          <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
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
                  placeholder="Ví dụ: staff_highlands"
                  style={{ width: '100%', padding: '7px 9px', borderRadius: '6px', border: '1.5px solid #CBD5E1', fontSize: '0.8rem' }}
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
                  style={{ width: '100%', padding: '7px 9px', borderRadius: '6px', border: '1.5px solid #CBD5E1', fontSize: '0.8rem' }}
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
                  style={{ width: '100%', padding: '7px 9px', borderRadius: '6px', border: '1.5px solid #CBD5E1', fontSize: '0.8rem' }}
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
                  style={{ width: '100%', padding: '7px 9px', borderRadius: '6px', border: '1.5px solid #CBD5E1', fontSize: '0.8rem' }}
                >
                  <option value="staff">Nhân Viên Cửa Hàng (Staff)</option>
                  <option value="admin">Quản Trị Viên (Admin)</option>
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
          <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
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

      {/* Tab 2: Map Graph & Patrol */}
      {subTab === 'map_patrol' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
          
          <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
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
                <span style={{ fontWeight: 600, color: '#475569' }}>Số Vòng Đã Hoàn Thành:</span>
                <span style={{ fontWeight: 700 }}>{patrolStatus?.completed_loops || 0} vòng</span>
              </div>
            </div>

            <button
              onClick={handleTriggerPatrol}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '11px',
                background: '#2563EB',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                fontWeight: 700,
                fontSize: '0.85rem',
                cursor: 'pointer'
              }}
            >
              <Play size={16} />
              <span>Kích Hoạt Tuần Tra Ngay Lập Tức</span>
            </button>
          </div>

          <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <h3 style={{ margin: '0 0 10px', fontSize: '0.95rem', fontWeight: 800, color: '#0F172A' }}>
              TOPOLOGICAL MAP GRAPH ({graphData?.nodes?.length || 0} Nodes, {graphData?.edges?.length || 0} Edges)
            </h3>
            <p style={{ fontSize: '0.78rem', color: '#64748B', margin: '0 0 12px' }}>
              Bản đồ hình học được tính toán bằng thuật toán A* shortest path để đảm bảo robot không bao giờ đi xuyên qua tường hoặc vùng cấm.
            </p>

            <div style={{ maxHeight: '280px', overflowY: 'auto', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.74rem' }}>
                <thead>
                  <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', textAlign: 'left' }}>
                    <th style={{ padding: '6px 8px' }}>Node ID</th>
                    <th style={{ padding: '6px 8px' }}>Tọa Độ (X, Y mét)</th>
                    <th style={{ padding: '6px 8px' }}>Nhãn POI</th>
                  </tr>
                </thead>
                <tbody>
                  {graphData?.nodes?.map(n => (
                    <tr key={n.id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                      <td style={{ padding: '5px 8px', fontWeight: 700 }}>{n.id}</td>
                      <td style={{ padding: '5px 8px', color: '#64748B' }}>({n.x.toFixed(1)}m, {n.y.toFixed(1)}m)</td>
                      <td style={{ padding: '5px 8px', color: '#2563EB' }}>{n.label || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}

      {/* Tab 3: Audit Logs */}
      {subTab === 'audit' && (
        <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '18px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 800, color: '#0F172A' }}>
                NHẬT KÝ KIỂM TOÁN HỆ THỐNG (AUDIT LOGS)
              </h3>
              <p style={{ margin: '3px 0 0', fontSize: '0.75rem', color: '#64748B' }}>
                Lưu vết 100 thao tác nhạy cảm: Đăng nhập, Dừng khẩn cấp, Tạo người dùng, Sao lưu cơ sở dữ liệu
              </p>
            </div>
            <button
              onClick={loadAuditLogs}
              style={{
                background: '#F1F5F9',
                border: '1px solid #CBD5E1',
                borderRadius: '6px',
                padding: '6px 10px',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <RotateCcw size={12} />
              <span>Tải Lại</span>
            </button>
          </div>

          <div style={{ maxHeight: '450px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.76rem' }}>
              <thead>
                <tr style={{ background: '#F8FAFC', borderBottom: '1.5px solid #E2E8F0', textAlign: 'left', color: '#64748B' }}>
                  <th style={{ padding: '8px' }}>Thời Gian</th>
                  <th style={{ padding: '8px' }}>Người Dùng</th>
                  <th style={{ padding: '8px' }}>Hành Động</th>
                  <th style={{ padding: '8px' }}>Tài Nguyên</th>
                  <th style={{ padding: '8px' }}>Chi Tiết</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map(log => (
                  <tr key={log.id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                    <td style={{ padding: '7px 8px', color: '#64748B', whiteSpace: 'nowrap' }}>
                      {log.created_at ? new Date(log.created_at).toLocaleString() : '—'}
                    </td>
                    <td style={{ padding: '7px 8px', fontWeight: 700 }}>
                      {log.username || 'Hệ thống'}
                      {log.role && <span style={{ fontSize: '0.68rem', color: '#94A3B8', marginLeft: '4px' }}>({log.role})</span>}
                    </td>
                    <td style={{ padding: '7px 8px' }}>
                      <span style={{
                        padding: '2px 6px',
                        borderRadius: '4px',
                        fontSize: '0.68rem',
                        fontWeight: 800,
                        background: '#EFF6FF',
                        color: '#1D4ED8'
                      }}>
                        {log.action}
                      </span>
                    </td>
                    <td style={{ padding: '7px 8px', color: '#475569' }}>{log.resource}</td>
                    <td style={{ padding: '7px 8px', color: '#334155' }}>{log.details || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 4: Database & Maintenance */}
      {subTab === 'database' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
          
          <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '18px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <h3 style={{ margin: '0 0 10px', fontSize: '0.95rem', fontWeight: 800, color: '#0F172A', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Database size={18} color="#2563EB" />
              <span>SAO LƯU CƠ SỞ DỮ LIỆU SQLITE (ATOMIC BACKUP)</span>
            </h3>
            <p style={{ fontSize: '0.78rem', color: '#64748B', lineHeight: 1.4, margin: '0 0 14px' }}>
              Cơ sở dữ liệu SQLite chạy ở chế độ WAL (Write-Ahead Logging) với Foreign Keys được kích hoạt bắt buộc. Bạn có thể tạo bản sao lưu snapshot đầy đủ an toàn trước khi thay đổi cấu trúc hoặc di chuyển robot.
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

          <div style={{ background: '#FFFFFF', borderRadius: '14px', padding: '18px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
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
