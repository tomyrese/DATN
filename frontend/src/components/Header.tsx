import React from 'react';
import { useRobotStore, updateGlobalState } from '../store/useRobotStore';
import { StorageService } from '../services/StorageService';
import { Sliders, ShieldCheck, User, Sparkles, LogOut } from 'lucide-react';

interface HeaderProps {
  onOpenPairModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenPairModal }) => {
  const { connectionStatus, latencyMs, pairedRobot, userRole } = useRobotStore();

  const getStatusClass = () => {
    switch (connectionStatus) {
      case 'CONNECTED':
        return 'status-connected';
      case 'CONNECTING':
      case 'AUTHENTICATING':
      case 'RECONNECTING':
        return 'status-connecting';
      default:
        return 'status-disconnected';
    }
  };

  const handleToggleRole = () => {
    if (userRole === 'customer') {
      if (!pairedRobot) {
        onOpenPairModal();
      } else {
        StorageService.saveUserRole('staff');
        updateGlobalState(() => ({ userRole: 'staff' }));
      }
    } else {
      StorageService.saveUserRole('customer');
      updateGlobalState(() => ({ userRole: 'customer' }));
    }
  };

  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-logo">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="10" width="36" height="28" rx="8" fill="#141926" stroke="#00E676" strokeWidth="2.5" />
            <circle cx="16" cy="22" r="4" fill="#00E5FF" />
            <circle cx="32" cy="22" r="4" fill="#00E5FF" />
            <path d="M18 31H30" stroke="#00E676" strokeWidth="2.5" strokeLinecap="round" />
            <path d="M24 4V10" stroke="#00E676" strokeWidth="2.5" strokeLinecap="round" />
            <circle cx="24" cy="4" r="2" fill="#00E676" />
          </svg>
        </div>
        <div className="brand-info">
          <h1 className="brand-title">
            MALL ROBOT <span>AI</span>
          </h1>
          <span className="brand-subtitle">
            {userRole === 'staff'
              ? `Chế độ: Nhân Viên Vận Hành (${pairedRobot?.robotId || 'RBT01'})`
              : 'Trợ Lý Lễ Tân & Dẫn Đường TTTM'}
          </span>
        </div>
      </div>

      <div className="header-status-area">
        {/* Role Mode Switcher */}
        <button
          className={`role-switcher-btn ${userRole === 'staff' ? 'role-staff' : 'role-customer'}`}
          onClick={handleToggleRole}
          title="Chuyển đổi giao diện Khách Hàng / Nhân Viên"
        >
          {userRole === 'staff' ? (
            <>
              <ShieldCheck size={14} />
              <span>NV VẬN HÀNH</span>
              <LogOut size={12} style={{ marginLeft: 4, opacity: 0.7 }} />
            </>
          ) : (
            <>
              <User size={14} />
              <span>KHÁCH THAM QUAN</span>
            </>
          )}
        </button>

        {connectionStatus === 'CONNECTED' && (
          <div className="ping-badge" title="WebSocket Latency">
            <span className="ping-dot"></span>
            <span>{latencyMs} ms</span>
          </div>
        )}

        <div className={`connection-pill ${getStatusClass()}`}>
          <span className="status-indicator"></span>
          <span>{connectionStatus}</span>
        </div>

        <button className="btn-icon" onClick={onOpenPairModal} title="Cấu hình kết nối / Quét mã">
          <Sliders size={18} />
        </button>
      </div>
    </header>
  );
};
