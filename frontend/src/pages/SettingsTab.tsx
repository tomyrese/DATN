import React, { useState } from 'react';
import { useRobotStore, updateGlobalState } from '../store/useRobotStore';
import { RobotSocket } from '../services/RobotSocket';
import { StorageService } from '../services/StorageService';
import { Settings, Wifi, KeyRound, Save, Trash2, CheckCircle2, Globe, Shield, User, ShieldCheck } from 'lucide-react';

export const SettingsTab: React.FC = () => {
  const { pairedRobot, settings, userRole } = useRobotStore();

  const [inputHost, setInputHost] = useState(pairedRobot?.host || window.location.hostname || 'localhost');
  const [inputPort, setInputPort] = useState(pairedRobot?.port ? pairedRobot.port.toString() : '8765');
  const [inputToken, setInputToken] = useState(pairedRobot?.token || '');
  const [remoteTunnelUrl, setRemoteTunnelUrl] = useState(settings.remoteTunnelUrl || '');
  const [enablePreview, setEnablePreview] = useState(settings.enableCameraPreview ?? true);
  const [defaultSpeed, setDefaultSpeed] = useState(Math.round((settings.defaultSpeed || 0.35) * 100));
  const [autoReconnect, setAutoReconnect] = useState(settings.autoReconnect ?? true);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSaveConnection = (e: React.FormEvent) => {
    e.preventDefault();
    const portNum = parseInt(inputPort, 10) || 8765;
    let cleanHost = inputHost.trim();
    const cleanToken = inputToken.trim();
    const cleanTunnel = remoteTunnelUrl.trim();

    // If a tunnel URL is provided, strip http/https and set as host
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
      enableCameraPreview: enablePreview,
      defaultSpeed: defaultSpeed / 100,
      autoReconnect: autoReconnect,
    };

    StorageService.savePairedRobot(newPaired);
    StorageService.saveSettings(newSettings);

    updateGlobalState(() => ({
      pairedRobot: newPaired,
      settings: newSettings,
    }));

    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2500);

    // Reconnect with new configuration
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
    if (window.confirm('Bạn có chắc chắn muốn hủy liên kết với Robot này?')) {
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
    <div className="tab-pane active">
      <div className="space-y-6" style={{ maxWidth: '820px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        
        {/* Role Mode Card */}
        <div className="card">
          <div className="card-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <ShieldCheck size={20} color="#00E5FF" />
              <div>
                <span className="card-tag">CHẾ ĐỘ GIAO DIỆN (PORTAL ROLE)</span>
                <div className="card-sub">Lựa chọn giữa giao diện dành cho Khách tham quan và Nhân viên vận hành</div>
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '16px' }}>
            <div
              className={`menu-tile ${userRole === 'customer' ? 'tile-primary' : ''}`}
              onClick={() => handleSwitchRole('customer')}
              style={{ cursor: 'pointer', padding: '16px', borderRadius: '10px' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <User size={18} color="#00E5FF" />
                <strong>Khách Tham Quan (Customer)</strong>
              </div>
              <p style={{ fontSize: '12px', color: '#94A3B8', margin: 0 }}>
                Bản đồ TTTM, hỏi đáp Trợ lý ảo AI, chỉ đường đến các gian hàng, không cần đăng nhập.
              </p>
            </div>

            <div
              className={`menu-tile ${userRole === 'staff' ? 'tile-cyan' : ''}`}
              onClick={() => handleSwitchRole('staff')}
              style={{ cursor: 'pointer', padding: '16px', borderRadius: '10px' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <ShieldCheck size={18} color="#00E676" />
                <strong>Nhân Viên Vận Hành (Staff)</strong>
              </div>
              <p style={{ fontSize: '12px', color: '#94A3B8', margin: 0 }}>
                Quản lý đặt đơn giao hàng nội bộ, lái thủ công, xem Camera CSI và chẩn đoán phần cứng.
              </p>
            </div>
          </div>
        </div>

        {/* Remote Internet Connection Card */}
        <div className="card">
          <div className="card-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Globe size={20} color="#00E5FF" />
              <div>
                <span className="card-tag">KẾT NỐI TỪ XA QUA INTERNET (KHÔNG CẦN CHUNG MẠNG)</span>
                <div className="card-sub">Kết nối qua Cloudflare Tunnel / ngrok / Tailscale miễn phí</div>
              </div>
            </div>
          </div>

          <div style={{ marginTop: '14px', background: 'rgba(0, 229, 255, 0.05)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(0, 229, 255, 0.2)', fontSize: '12px', color: '#94A3B8', lineHeight: 1.6 }}>
            💡 <strong>Để điều khiển Robot từ bất kỳ đâu qua Internet (Deploy Vercel):</strong>
            <br />
            1. Trên Raspberry Pi, chạy lệnh: <code style={{ color: '#00E5FF', background: '#080B11', padding: '2px 6px', borderRadius: 4 }}>bash scripts/setup_cloudflare_tunnel.sh</code>
            <br />
            2. Copy đường link công khai dạng <code style={{ color: '#00E676' }}>https://xxx.trycloudflare.com</code> và dán vào ô bên dưới:
          </div>

          <form onSubmit={handleSaveConnection} style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label className="setting-label">Cloudflare Tunnel URL / Domain từ xa</label>
              <input
                type="text"
                value={remoteTunnelUrl}
                onChange={(e) => setRemoteTunnelUrl(e.target.value)}
                placeholder="ví dụ: https://robot-mall.trycloudflare.com hoặc robot.yourdomain.com"
                className="input-text"
              />
            </div>

            <div className="modal-divider"><span>HOẶC KẾT NỐI MẠNG NỘI BỘ (LAN IP)</span></div>

            <div className="form-row">
              <div className="form-col-2">
                <label className="setting-label">IP Nội bộ Robot</label>
                <input
                  type="text"
                  value={inputHost}
                  onChange={(e) => setInputHost(e.target.value)}
                  placeholder="192.168.1.50 hoặc localhost"
                  className="input-text"
                />
              </div>

              <div className="form-col-1">
                <label className="setting-label">Port</label>
                <input
                  type="number"
                  value={inputPort}
                  onChange={(e) => setInputPort(e.target.value)}
                  placeholder="8765"
                  className="input-text"
                />
              </div>
            </div>

            <div>
              <label className="setting-label">Mã Token Nhân Viên (Bearer Token)</label>
              <input
                type="password"
                value={inputToken}
                onChange={(e) => setInputToken(e.target.value)}
                placeholder="Tự động điền sau khi ghép nối bằng mã PIN hoặc quét QR"
                className="input-text"
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '10px' }}>
              <div>
                {saveSuccess && (
                  <span style={{ color: '#00E676', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <CheckCircle2 size={16} /> Đã lưu cấu hình và đang kết nối lại!
                  </span>
                )}
              </div>

              <button type="submit" className="btn-primary" style={{ padding: '8px 20px' }}>
                <Save size={15} style={{ display: 'inline', marginRight: '6px' }} />
                LƯU & KẾT NỐI
              </button>
            </div>
          </form>
        </div>

        {/* Paired Robot Information Card */}
        <div className="card">
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <KeyRound size={20} color="#00E676" />
              <div>
                <span className="card-tag">THÔNG TIN ROBOT ĐÃ KẾT NỐI</span>
                <div className="card-sub">Trạng thái phiên làm việc hiện tại</div>
              </div>
            </div>

            {pairedRobot && (
              <button
                onClick={handleUnpair}
                className="btn-sm"
                style={{ color: '#FF3D71', borderColor: 'rgba(255, 61, 113, 0.3)', background: 'rgba(255, 61, 113, 0.1)' }}
              >
                <Trash2 size={13} style={{ display: 'inline', marginRight: '4px' }} />
                Hủy Liên Kết
              </button>
            )}
          </div>

          <div style={{ marginTop: '16px' }}>
            {pairedRobot ? (
              <div className="meta-table">
                <div className="meta-row">
                  <span className="meta-key">Robot ID:</span>
                  <span className="meta-val text-cyan">{pairedRobot.robotId}</span>
                </div>
                <div className="meta-row">
                  <span className="meta-key">Tên Thiết Bị:</span>
                  <span className="meta-val">{pairedRobot.robotName}</span>
                </div>
                <div className="meta-row">
                  <span className="meta-key">Địa Chỉ Host:</span>
                  <span className="meta-val">{pairedRobot.host}:{pairedRobot.port}</span>
                </div>
                <div className="meta-row">
                  <span className="meta-key">Lần Kết Nối Cuối:</span>
                  <span className="meta-val">{new Date(pairedRobot.lastConnected).toLocaleString()}</span>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '16px', color: '#64748B', fontSize: '13px' }}>
                Chưa có cấu hình Robot nào được lưu. Bạn có thể sử dụng nút quét mã PIN/QR ở góc trên.
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
