import React from 'react';
import { useRobotStore, updateGlobalState } from '../store/useRobotStore';
import { StorageService } from '../services/StorageService';
import { Bot, User, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  onOpenSettings?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenSettings }) => {
  const { connectionStatus, userRole } = useRobotStore();

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

  const handleToggleRole = () => {
    if (userRole === 'customer') {
      StorageService.saveUserRole('staff');
      updateGlobalState(() => ({ userRole: 'staff' }));
    } else {
      StorageService.saveUserRole('customer');
      updateGlobalState(() => ({ userRole: 'customer' }));
    }
  };

  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-icon-bubble">
          <Bot size={20} />
        </div>
        <div className="brand-text-block">
          <h1>
            ROBOT TTTM
          </h1>
        </div>
      </div>

      <div className="header-actions">
        {/* Status Pill */}
        <div className="robot-status-pill">
          <span className={`status-dot ${status.className}`}></span>
          <span>{status.text}</span>
        </div>

        {/* Role Toggle Button */}
        <button
          className={`btn-role-switch ${userRole === 'staff' ? 'active-staff' : ''}`}
          onClick={handleToggleRole}
          title="Chuyển chế độ Khách Hàng / Nhân Viên"
        >
          {userRole === 'staff' ? (
            <>
              <ShieldCheck size={13} color="#B45309" />
              <span>NV</span>
            </>
          ) : (
            <>
              <User size={13} />
              <span>Khách</span>
            </>
          )}
        </button>
      </div>
    </header>
  );
};
