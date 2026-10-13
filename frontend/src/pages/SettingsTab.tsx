import React, { useState } from 'react';
import { useRobotStore, updateGlobalState } from '../store/useRobotStore';
import { RobotSocket } from '../services/RobotSocket';
import { StorageService } from '../services/StorageService';
import { RobotApi } from '../services/RobotApi';
import { LoginModal } from '../components/LoginModal';
import { User, ShieldCheck, CheckCircle2, Save, Trash2, Shield, LogOut, LogIn } from 'lucide-react';

export const SettingsTab: React.FC = () => {
  const { pairedRobot, settings, userRole, currentUser } = useRobotStore();

  const [inputHost, setInputHost] = useState(pairedRobot?.host || window.location.hostname || 'localhost');
  const [inputPort, setInputPort] = useState(pairedRobot?.port ? pairedRobot.port.toString() : '8765');
  const [inputToken, setInputToken] = useState(pairedRobot?.token || 'guest');
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);

  const handleSaveConnection = (e: React.FormEvent) => {
    e.preventDefault();
    const portNum = parseInt(inputPort, 10) || 8765;
    const cleanHost = inputHost.trim();
    const cleanToken = inputToken.trim() || 'guest';

    const newPaired = {
      robotId: pairedRobot?.robotId || 'MALL-ROBOT-01',
      robotName: pairedRobot?.robotName || 'TTTM Navigation Robot',
      host: cleanHost,
      port: portNum,
      token: cleanToken,
      lastConnected: Date.now(),
    };

    StorageService.savePairedRobot(newPaired);

    updateGlobalState(() => ({
      pairedRobot: newPaired,
    }));

    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2500);

    const socket = RobotSocket.getInstance();
    socket.disconnect();
    setTimeout(() => {
      socket.connect(newPaired.host, newPaired.port, cleanToken);
    }, 200);
  };

  const handleLogout = async () => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    const token = currentUser?.token;
    if (token) {
      await RobotApi.logout(host, port, token);
    }
    StorageService.clearAuthUser();
    updateGlobalState(() => ({
      currentUser: null,
      userRole: 'customer',
    }));
    RobotSocket.getInstance().connect(host, port, 'guest');
  };

  const handleSwitchToCustomerPreview = () => {
    StorageService.saveUserRole('customer');
    updateGlobalState(() => ({ userRole: 'customer' }));
  };

  const handleUnpair = () => {
    if (window.confirm('Ngắt kết nối robot?')) {
      StorageService.clearPairedRobot();
      RobotSocket.getInstance().disconnect();
      updateGlobalState(() => ({
        pairedRobot: null,
        connectionStatus: 'DISCONNECTED',
      }));
      setInputToken('');
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      
      {/* Account & Role Card */}
      <div className="card-clean" style={{ padding: '16px 18px' }}>
        <div className="card-title-group" style={{ marginBottom: '12px' }}>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 800 }}>TÀI KHOẢN & PHÂN QUYỀN</h2>
          <p style={{ fontSize: '0.8rem' }}>Thông tin phiên làm việc và quyền truy cập các tính năng</p>
        </div>

        {currentUser ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
            backgroundColor: '#F8FAFC',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            padding: '14px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  backgroundColor: currentUser.role === 'admin' ? '#FEF3C7' : '#EFF6FF',
                  color: currentUser.role === 'admin' ? '#B45309' : '#1D4ED8',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  {currentUser.role === 'admin' ? <Shield size={20} /> : <ShieldCheck size={20} />}
                </div>
                <div>
                  <div style={{ fontWeight: 800, fontSize: '0.92rem', color: '#0F172A' }}>
                    {currentUser.fullName || currentUser.username}
                  </div>
                  <div style={{ fontSize: '0.74rem', color: '#64748B' }}>
                    Tên tài khoản: @{currentUser.username}
                  </div>
                </div>
              </div>

              <span style={{
                fontSize: '0.74rem',
                fontWeight: 800,
                padding: '3px 10px',
                borderRadius: '99px',
                backgroundColor: currentUser.role === 'admin' ? '#FEF3C7' : '#EFF6FF',
                color: currentUser.role === 'admin' ? '#B45309' : '#1D4ED8',
              }}>
                {currentUser.role === 'admin' ? 'QUẢN TRỊ VIÊN' : 'NHÂN VIÊN'}
              </span>
            </div>

            {currentUser.assignedStoreIds && currentUser.assignedStoreIds.length > 0 && (
              <div style={{ fontSize: '0.76rem', color: '#64748B' }}>
                Gian hàng phụ trách: <strong>{currentUser.assignedStoreIds.join(', ')}</strong>
              </div>
            )}

            <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
              <button
                onClick={handleSwitchToCustomerPreview}
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  backgroundColor: '#FFFFFF',
                  border: '1px solid #CBD5E1',
                  borderRadius: '8px',
                  color: '#334155',
                  fontWeight: 700,
                  fontSize: '0.78rem',
                  cursor: 'pointer',
                }}
              >
                Xem Giao Diện Khách
              </button>
              <button
                onClick={handleLogout}
                style={{
                  padding: '8px 14px',
                  backgroundColor: '#FEE2E2',
                  border: '1px solid #FECACA',
                  borderRadius: '8px',
                  color: '#DC2626',
                  fontWeight: 700,
                  fontSize: '0.78rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  cursor: 'pointer',
                }}
              >
                <LogOut size={14} />
                <span>Đăng Xuất</span>
              </button>
            </div>
          </div>
        ) : (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: '#F8FAFC',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            padding: '14px',
          }}>
            <div>
              <div style={{ fontWeight: 800, fontSize: '0.9rem', color: '#0F172A' }}>
                Khách Tham Quan (Guest)
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748B' }}>
                Chỉ xem bản đồ và yêu cầu dẫn đường
              </div>
            </div>
            <button
              onClick={() => setShowLoginModal(true)}
              className="btn-solid-blue"
              style={{ padding: '8px 14px', fontSize: '0.8rem' }}
            >
              <LogIn size={14} />
              <span>Đăng Nhập</span>
            </button>
          </div>
        )}
      </div>

      {/* Connection Config Card */}
      <div className="card-clean" style={{ padding: '16px 18px' }}>
        <div className="card-title-group" style={{ marginBottom: '12px' }}>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 800 }}>KẾT NỐI ROBOT</h2>
          <p style={{ fontSize: '0.8rem' }}>Địa chỉ mạng của máy chủ điều khiển Robot</p>
        </div>

        <form onSubmit={handleSaveConnection} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 100px', gap: '10px' }}>
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                Địa chỉ IP Robot:
              </label>
              <input
                type="text"
                className="quick-search-input"
                style={{ padding: '8px 12px', fontSize: '0.88rem' }}
                value={inputHost}
                onChange={e => setInputHost(e.target.value)}
                placeholder="192.168.1.100"
              />
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                Cổng (Port):
              </label>
              <input
                type="text"
                className="quick-search-input"
                style={{ padding: '8px 12px', fontSize: '0.88rem' }}
                value={inputPort}
                onChange={e => setInputPort(e.target.value)}
                placeholder="8765"
              />
            </div>
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
              Mã Xác Thực (Token):
            </label>
            <input
              type="text"
              className="quick-search-input"
              style={{ padding: '8px 12px', fontSize: '0.88rem' }}
              value={inputToken}
              onChange={e => setInputToken(e.target.value)}
              placeholder="guest"
            />
          </div>

          {saveSuccess && (
            <div style={{ color: '#059669', fontSize: '0.85rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle2 size={16} />
              <span>Đã lưu và kết nối lại!</span>
            </div>
          )}

          <div style={{ display: 'flex', gap: '10px', marginTop: '4px' }}>
            <button type="submit" className="btn-solid-blue" style={{ flex: 1, padding: '10px 14px', fontSize: '0.88rem', whiteSpace: 'nowrap' }}>
              <Save size={15} />
              <span>Lưu Cài Đặt</span>
            </button>
            <button type="button" className="btn-outline" onClick={handleUnpair} style={{ color: '#EF4444', padding: '10px 14px', fontSize: '0.88rem', whiteSpace: 'nowrap' }}>
              <Trash2 size={15} />
              <span>Ngắt Kết Nối</span>
            </button>
          </div>
        </form>
      </div>

      <LoginModal isOpen={showLoginModal} onClose={() => setShowLoginModal(false)} />
    </div>
  );
};
