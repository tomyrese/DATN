import React from 'react';
import { useRobotStore, updateGlobalState } from '../store/useRobotStore';
import { StorageService } from '../services/StorageService';
import { Bot, User, ShieldCheck, Settings } from 'lucide-react';

interface HeaderProps {
  onOpenPairModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenPairModal }) => {
  const { connectionStatus, userRole } = useRobotStore();

  const getStatusInfo = () => {
    switch (connectionStatus) {
      case 'CONNECTED':
        return { text: 'Sẵn Sàng', className: 'online' };
      case 'CONNECTING':
      case 'AUTHENTICATING':
      case 'RECONNECTING':
        return { text: 'Đang Kết Nối...', className: 'connecting' };
      default:
        return { text: 'Ngoại Tuyến', className: 'offline' };
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
          <Bot size={26} />
        </div>
        <div className="brand-text-block">
          <h1>
            MALL ROBOT <span className="brand-badge">AI 4.0</span>
          </h1>
          <p>
            {userRole === 'staff'
              ? 'Chế Độ: Nhân Viên Vận Hành'
              : 'Trợ Lý Lễ Tân & Dẫn Đường Trung Tâm Thương Mại'}
          </p>
        </div>
      </div>

      <div className="header-actions">
        {/* Connection Status Pill */}
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
              <ShieldCheck size={16} color="#B45309" />
              <span>Nhân Viên</span>
            </>
          ) : (
            <>
              <User size={16} />
              <span>Khách Tham Quan</span>
            </>
          )}
        </button>

        {/* Settings / Pairing Modal */}
        <button
          className="btn-outline"
          onClick={onOpenPairModal}
          style={{ padding: '8px 12px' }}
          title="Cài đặt kết nối & Quét mã QR"
        >
          <Settings size={18} />
        </button>
      </div>
    </header>
  );
};
