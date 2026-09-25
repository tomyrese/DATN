import React, { useState } from 'react';
import { useRobotStore, updateGlobalState } from '../store/useRobotStore';
import { RobotSocket } from '../services/RobotSocket';
import { StorageService } from '../services/StorageService';
import { Settings, Wifi, User, ShieldCheck, CheckCircle2, Save, Trash2, Cpu, Wrench } from 'lucide-react';

export const SettingsTab: React.FC = () => {
  const { pairedRobot, settings, userRole, telemetry } = useRobotStore();

  const [inputHost, setInputHost] = useState(pairedRobot?.host || window.location.hostname || 'localhost');
  const [inputPort, setInputPort] = useState(pairedRobot?.port ? pairedRobot.port.toString() : '8765');
  const [inputToken, setInputToken] = useState(pairedRobot?.token || '');
  const [remoteTunnelUrl, setRemoteTunnelUrl] = useState(settings.remoteTunnelUrl || '');
  const [defaultSpeed, setDefaultSpeed] = useState(Math.round((settings.defaultSpeed || 0.35) * 100));
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSaveConnection = (e: React.FormEvent) => {
    e.preventDefault();
    const portNum = parseInt(inputPort, 10) || 8765;
    let cleanHost = inputHost.trim();
    const cleanToken = inputToken.trim();
    const cleanTunnel = remoteTunnelUrl.trim();

    if (cleanTunnel) {
      cleanHost = cleanTunnel.replace(/^https?:\/\//, '').replace(/\/+$/, '');
    }

    const newPaired = {
      robotId: pairedRobot?.robotId || 'MALL-ROBOT-01',
      robotName: pairedRobot?.robotName || 'TTTM Navigation Robot',
      host: cleanHost,
      port: cleanTunnel ? 443 : portNum,
      token: cleanToken,
      lastConnected: Date.now(),
    };

    const newSettings = {
      ...settings,
      remoteTunnelUrl: cleanTunnel,
      defaultSpeed: defaultSpeed / 100,
    };

    StorageService.savePairedRobot(newPaired);
    StorageService.saveSettings(newSettings);

    updateGlobalState(() => ({
      pairedRobot: newPaired,
      settings: newSettings,
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
    if (window.confirm('Bạn có chắc chắn muốn ngắt kết nối khỏi Robot này?')) {
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
    <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Role Selection Card */}
      <div className="card-clean">
        <div className="card-title-group" style={{ marginBottom: '16px' }}>
          <h2>CHẾ ĐỘ GIAO DIỆN</h2>
          <p>Lựa chọn giao diện hiển thị phù hợp với nhu cầu sử dụng</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '14px' }}>
          <div
            onClick={() => handleSwitchRole('customer')}
            style={{
              padding: '18px',
              borderRadius: '16px',
              border: userRole === 'customer' ? '2px solid #2563EB' : '1px solid #E2E8F0',
              background: userRole === 'customer' ? '#EFF6FF' : '#FFFFFF',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#2563EB', fontWeight: 800 }}>
              <User size={20} />
              <span>Khách Tham Quan (Customer)</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: '#64748B' }}>
              Bản đồ tầng 1, hỏi đáp Trợ lý AI và chỉ dẫn đến các gian hàng mua sắm, ẩm thực.
            </p>
          </div>

          <div
            onClick={() => handleSwitchRole('staff')}
            style={{
              padding: '18px',
              borderRadius: '16px',
              border: userRole === 'staff' ? '2px solid #D97706' : '1px solid #E2E8F0',
              background: userRole === 'staff' ? '#FFFBEB' : '#FFFFFF',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#B45309', fontWeight: 800 }}>
              <ShieldCheck size={20} />
              <span>Nhân Viên Vận Hành (Staff)</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: '#64748B' }}>
              Lái robot bằng phím hoặc camera trực tiếp, quản lý điều phối đơn giao hàng nội bộ.
            </p>
          </div>
        </div>
      </div>

      {/* Connection Config Card */}
      <div className="card-clean">
        <div className="card-title-group" style={{ marginBottom: '16px' }}>
          <h2>KẾT NỐI ROBOT & MẠNG</h2>
          <p>Địa chỉ máy chủ Robot (Mặc định tự động nhận khi quét mã QR trên màn hình OLED)</p>
        </div>

        <form onSubmit={handleSaveConnection} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 140px', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '6px' }}>
                Địa chỉ IP Robot:
              </label>
              <input
                type="text"
                className="quick-search-input"
                style={{ padding: '10px 14px' }}
                value={inputHost}
                onChange={e => setInputHost(e.target.value)}
                placeholder="VD: 192.168.1.100"
              />
            </div>

            <div>
              <label style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '6px' }}>
                Cổng (Port):
              </label>
              <input
                type="text"
                className="quick-search-input"
                style={{ padding: '10px 14px' }}
                value={inputPort}
                onChange={e => setInputPort(e.target.value)}
                placeholder="8765"
              />
            </div>
          </div>

          <div>
            <label style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '6px' }}>
              Mã Xác Thực Kết Nối (Token):
            </label>
            <input
              type="text"
              className="quick-search-input"
              style={{ padding: '10px 14px' }}
              value={inputToken}
              onChange={e => setInputToken(e.target.value)}
              placeholder="Nhập mã xác thực từ OLED hoặc quét QR"
            />
          </div>

          {saveSuccess && (
            <div style={{ color: '#059669', fontSize: '0.9rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle2 size={18} />
              <span>Đã lưu cài đặt và kết nối lại thành công!</span>
            </div>
          )}

          <div style={{ display: 'flex', gap: '10px', marginTop: '8px' }}>
            <button type="submit" className="btn-solid-blue" style={{ flex: 1 }}>
              <Save size={16} />
              <span>Lưu & Kết Nối Lại</span>
            </button>
            <button type="button" className="btn-outline" onClick={handleUnpair} style={{ color: '#EF4444' }}>
              <Trash2 size={16} />
              <span>Ngắt Kết Nối</span>
            </button>
          </div>
        </form>
      </div>

    </div>
  );
};
