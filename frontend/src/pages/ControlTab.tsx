import React, { useState } from 'react';
import { useRobotStore } from '../store/useRobotStore';
import { DPad } from '../components/DPad';
import { RobotSocket } from '../services/RobotSocket';
import { RobotApi } from '../services/RobotApi';
import { Video, AlertOctagon, RefreshCw, Zap, ShieldAlert } from 'lucide-react';

interface ControlTabProps {
  cameraTicket: string | null;
}

export const ControlTab: React.FC<ControlTabProps> = ({ cameraTicket }) => {
  const { pairedRobot, settings, telemetry, isSafetyBlocked, isEmergencyStopped, connectionStatus } = useRobotStore();
  const [speed, setSpeed] = useState(settings.defaultSpeed || 0.35);

  const disabled = connectionStatus !== 'CONNECTED' || isSafetyBlocked || isEmergencyStopped;

  const handleSpeedSelect = (val: number) => {
    setSpeed(val);
    RobotSocket.getInstance().updateDriveSpeed(val);
  };

  const handleEStop = () => {
    RobotSocket.getInstance().sendEmergencyStop();
    if (pairedRobot) {
      RobotApi.emergencyStop(pairedRobot.host, pairedRobot.port);
    }
  };

  const handleReset = () => {
    RobotSocket.getInstance().sendEmergencyReset();
    if (pairedRobot) {
      RobotApi.emergencyReset(pairedRobot.host, pairedRobot.port, pairedRobot.token);
    }
  };

  const streamUrl = pairedRobot
    ? (cameraTicket
        ? `${RobotApi.getBaseUrl(pairedRobot.host, pairedRobot.port)}/api/v1/camera/mjpeg?ticket=${cameraTicket}`
        : `${RobotApi.getBaseUrl(pairedRobot.host, pairedRobot.port)}/api/v1/camera/mjpeg?token=${pairedRobot.token}`)
    : '';

  return (
    <div className="control-screen-layout">
      
      {/* Left Column: Live Camera Video */}
      <div className="camera-live-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Video size={20} color="#2563EB" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800 }}>CAMERA TRỰC TIẾP (HD)</h3>
          </div>
          <span className="brand-badge" style={{ background: '#F1F5F9', color: '#0F172A' }}>
            {telemetry?.cameraFps ? `${telemetry.cameraFps.toFixed(1)} FPS` : 'Camera Sẵn Sàng'}
          </span>
        </div>

        <div className="camera-frame">
          {streamUrl ? (
            <img src={streamUrl} alt="Robot Live Camera" />
          ) : (
            <div style={{ color: '#94A3B8', textAlign: 'center' }}>
              <Video size={48} style={{ opacity: 0.5, marginBottom: '8px' }} />
              <div>Đang tải luồng camera robot...</div>
            </div>
          )}

          <div className="camera-badge-live">
            <span className="status-dot online"></span>
            <span>TRỰC TIẾP</span>
          </div>

          {telemetry?.personDetected && (
            <div style={{
              position: 'absolute',
              bottom: 12,
              left: 12,
              right: 12,
              background: 'rgba(239, 68, 68, 0.9)',
              color: '#FFFFFF',
              padding: '8px 14px',
              borderRadius: '8px',
              fontSize: '0.85rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <ShieldAlert size={16} />
              <span>PHÁT HIỆN VẬT CẢN / NGƯỜI TRƯỚC MẶT — ĐANG GIẢM TỐC AN TOÀN</span>
            </div>
          )}
        </div>
      </div>

      {/* Right Column: Gamepad D-Pad & Emergency Controls */}
      <div className="dpad-card">
        
        {/* 3-Step Speed Selector */}
        <div className="speed-selector-group">
          <label>Chọn Tốc Độ Di Chuyển:</label>
          <div className="speed-buttons-row">
            {[
              { label: '🐢 Chậm (0.2m/s)', val: 0.2 },
              { label: '🚶 Vừa (0.35m/s)', val: 0.35 },
              { label: '⚡ Nhanh (0.6m/s)', val: 0.6 },
            ].map(item => (
              <button
                key={item.val}
                type="button"
                className={`speed-btn-option ${speed === item.val ? 'active' : ''}`}
                onClick={() => handleSpeedSelect(item.val)}
                disabled={disabled}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        {/* 3x3 DPad Controls */}
        <DPad currentSpeed={speed} disabled={disabled} />

        {/* Emergency Stop Button */}
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <button type="button" className="btn-emergency-giant" onClick={handleEStop}>
            <AlertOctagon size={24} />
            <span>DỪNG KHẨN CẤP (E-STOP)</span>
          </button>

          {isEmergencyStopped && (
            <button type="button" className="btn-reset-estop-clean" onClick={handleReset}>
              <RefreshCw size={16} style={{ display: 'inline', marginRight: '6px' }} />
              KHÔI PHỤC HOẠT ĐỘNG (RESET)
            </button>
          )}
        </div>

      </div>

    </div>
  );
};
