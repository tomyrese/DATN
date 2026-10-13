import React, { useState } from 'react';
import { useRobotStore, updateGlobalState } from '../store/useRobotStore';
import { StorageService } from '../services/StorageService';
import { RobotApi } from '../services/RobotApi';
import { RobotSocket } from '../services/RobotSocket';
import { LoginModal } from './LoginModal';
import { Bot, User, ShieldCheck, Shield, LogOut, LogIn } from 'lucide-react';

interface HeaderProps {
  onOpenSettings?: () => void;
  onGoHome?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenSettings, onGoHome }) => {
  const { connectionStatus, userRole, currentUser, pairedRobot } = useRobotStore();
  const [showLoginModal, setShowLoginModal] = useState(false);

  const getStatusInfo = () => {
    switch (connectionStatus) {
      case 'CONNECTED':
        return { text: 'Sẵn Sàng', className: 'online' };
      case 'CONNECTING':
      case 'AUTHENTICATING':
      case 'RECONNECTING':
        return { text: 'Đang nối', className: 'connecting' };
      default:
        return { text: 'Sẵn Sàng', className: 'online' };
    }
  };

  const status = getStatusInfo();

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
    // Reconnect as guest
    RobotSocket.getInstance().connect(host, port, 'guest');
  };

  return (
    <>
      <header className="app-header">
        <div className="brand-section" onClick={onGoHome} style={{ cursor: onGoHome ? 'pointer' : 'default' }}>
          <div className="brand-icon-bubble">
            <Bot size={20} />
          </div>
          <div className="brand-text-block">
            <h1 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 800 }}>
              ROBOT TTTM
            </h1>
            <span className="brand-subtext" style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 600 }}>
              Trung Tâm Thương Mại
            </span>
          </div>
        </div>

        <div className="header-actions" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Status Pill */}
          <div className="robot-status-pill">
            <span className={`status-dot ${status.className}`}></span>
            <span>{status.text}</span>
          </div>

          {/* User Role & Login/Logout Action */}
          {userRole === 'admin' ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  background: '#FEF3C7',
                  color: '#B45309',
                  padding: '5px 9px',
                  borderRadius: '8px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  border: '1px solid #FDE68A'
                }}
              >
                <Shield size={13} />
                <span>Admin: {currentUser?.username || 'admin'}</span>
              </div>
              <button
                onClick={handleLogout}
                title="Đăng xuất"
                style={{
                  background: '#F1F5F9',
                  border: '1px solid #CBD5E1',
                  borderRadius: '8px',
                  padding: '6px 8px',
                  cursor: 'pointer',
                  color: '#475569',
                  display: 'flex',
                  alignItems: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 600
                }}
              >
                <LogOut size={13} />
              </button>
            </div>
          ) : userRole === 'staff' ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  background: '#EFF6FF',
                  color: '#1D4ED8',
                  padding: '5px 9px',
                  borderRadius: '8px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  border: '1px solid #BFDBFE'
                }}
              >
                <ShieldCheck size={13} />
                <span>NV: {currentUser?.username || 'Staff'}</span>
              </div>
              <button
                onClick={handleLogout}
                title="Đăng xuất"
                style={{
                  background: '#F1F5F9',
                  border: '1px solid #CBD5E1',
                  borderRadius: '8px',
                  padding: '6px 8px',
                  cursor: 'pointer',
                  color: '#475569',
                  display: 'flex',
                  alignItems: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 600
                }}
              >
                <LogOut size={13} />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowLoginModal(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                background: '#F8FAFC',
                border: '1.5px solid #CBD5E1',
                borderRadius: '8px',
                padding: '6px 10px',
                fontSize: '0.78rem',
                fontWeight: 700,
                color: '#334155',
                cursor: 'pointer'
              }}
            >
              <LogIn size={13} color="#2563EB" />
              <span>Đăng Nhập</span>
            </button>
          )}
        </div>
      </header>

      <LoginModal isOpen={showLoginModal} onClose={() => setShowLoginModal(false)} />
    </>
  );
};
