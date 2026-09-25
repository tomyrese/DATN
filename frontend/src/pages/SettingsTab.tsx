import React, { useState } from 'react';
import { useRobotStore, updateGlobalState } from '../store/useRobotStore';
import { RobotSocket } from '../services/RobotSocket';
import { StorageService } from '../services/StorageService';
import { User, ShieldCheck, CheckCircle2, Save, Trash2 } from 'lucide-react';

export const SettingsTab: React.FC = () => {
  const { pairedRobot, settings, userRole } = useRobotStore();

  const [inputHost, setInputHost] = useState(pairedRobot?.host || window.location.hostname || 'localhost');
  const [inputPort, setInputPort] = useState(pairedRobot?.port ? pairedRobot.port.toString() : '8765');
  const [inputToken, setInputToken] = useState(pairedRobot?.token || 'guest');
  const [saveSuccess, setSaveSuccess] = useState(false);

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

  const handleSwitchRole = (newRole: 'customer' | 'staff') => {
    StorageService.saveUserRole(newRole);
    updateGlobalState(() => ({ userRole: newRole }));
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
      
      {/* Role Selection Card */}
      <div className="card-clean" style={{ padding: '16px 18px' }}>
        <div className="card-title-group" style={{ marginBottom: '12px' }}>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 800 }}>CHẾ ĐỘ GIAO DIỆN</h2>
          <p style={{ fontSize: '0.8rem' }}>Chọn giao diện phù hợp với mục đích sử dụng</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div
            onClick={() => handleSwitchRole('customer')}
            style={{
              padding: '14px',
              borderRadius: '14px',
              border: userRole === 'customer' ? '2px solid #2563EB' : '1px solid #E2E8F0',
              background: userRole === 'customer' ? '#EFF6FF' : '#FFFFFF',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              gap: '4px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#2563EB', fontWeight: 800, fontSize: '0.9rem' }}>
              <User size={16} />
              <span>Khách Tham Quan</span>
            </div>
            <p style={{ fontSize: '0.75rem', color: '#64748B', lineHeight: '1.3' }}>
              Bản đồ, hỏi đáp AI và chỉ dẫn đường gian hàng.
            </p>
          </div>

          <div
            onClick={() => handleSwitchRole('staff')}
            style={{
              padding: '14px',
              borderRadius: '14px',
              border: userRole === 'staff' ? '2px solid #D97706' : '1px solid #E2E8F0',
              background: userRole === 'staff' ? '#FFFBEB' : '#FFFFFF',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              gap: '4px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#B45309', fontWeight: 800, fontSize: '0.9rem' }}>
              <ShieldCheck size={16} />
              <span>Nhân Viên</span>
            </div>
            <p style={{ fontSize: '0.75rem', color: '#64748B', lineHeight: '1.3' }}>
              Lái robot camera, điều phối đơn giao hàng.
            </p>
          </div>
        </div>
      </div>

      {/* Connection Config Card */}
      <div className="card-clean" style={{ padding: '16px 18px' }}>
        <div className="card-title-group" style={{ marginBottom: '12px' }}>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 800 }}>KẾT NỐI ROBOT</h2>
          <p style={{ fontSize: '0.8rem' }}>Tự động nhận diện khi kết nối mạng nội bộ của Robot</p>
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

    </div>
  );
};
