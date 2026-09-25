import React, { useState } from 'react';
import { useRobotStore } from '../store/useRobotStore';
import { DPad } from '../components/DPad';
import { RobotSocket } from '../services/RobotSocket';
import { RobotApi } from '../services/RobotApi';
import { Video, AlertOctagon, RefreshCw, ShieldAlert } from 'lucide-react';

interface ControlTabProps {
  cameraTicket: string | null;
}

export const ControlTab: React.FC<ControlTabProps> = ({ cameraTicket }) => {
  const { pairedRobot, settings, telemetry, isEmergencyStopped } = useRobotStore();
  const [speed, setSpeed] = useState(settings.defaultSpeed || 0.35);

  const disabled = isEmergencyStopped;

  const handleSpeedSelect = (val: number) => {
    setSpeed(val);
    RobotSocket.getInstance().updateDriveSpeed(val);
  };

  const handleEStop = () => {
    RobotSocket.getInstance().sendEmergencyStop();
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    RobotApi.emergencyStop(host, port);
  };

  const handleReset = () => {
    RobotSocket.getInstance().sendEmergencyReset();
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    RobotApi.emergencyReset(host, port, pairedRobot?.token || 'guest');
  };

  const streamUrl = pairedRobot
    ? (cameraTicket
        ? `${RobotApi.getBaseUrl(pairedRobot.host, pairedRobot.port)}/api/v1/camera/mjpeg?ticket=${cameraTicket}`
        : `${RobotApi.getBaseUrl(pairedRobot.host, pairedRobot.port)}/api/v1/camera/mjpeg?token=${pairedRobot.token || 'guest'}`)
    : `${RobotApi.getBaseUrl()}/api/v1/camera/mjpeg?token=guest`;

  return (
    <div className="control-screen-layout">
      
      {/* Live Camera Video */}
      <div className="camera-live-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Video size={18} color="#2563EB" />
            <h3 style={{ fontSize: '1rem', fontWeight: 800, whiteSpace: 'nowrap' }}>CAMERA TRỰC TIẾP</h3>
          </div>
          <span className="brand-badge" style={{ background: '#F1F5F9', color: '#0F172A', whiteSpace: 'nowrap' }}>
            {telemetry?.cameraFps ? `${telemetry.cameraFps.toFixed(0)} FPS` : 'HD'}
          </span>
        </div>

        <div className="camera-frame">
          <img src={streamUrl} alt="Robot Live Camera" onError={(e) => {
            // Fallback image if stream temporarily reloads
            (e.target as HTMLElement).style.opacity = '0.7';
          }} />

          <div className="camera-badge-live">
            <span className="status-dot online"></span>
            <span>TRỰC TIẾP</span>
          </div>

          {telemetry?.personDetected && (
            <div style={{
              position: 'absolute',
              bottom: 8,
              left: 8,
              right: 8,
              background: 'rgba(239, 68, 68, 0.95)',
              color: '#FFFFFF',
              padding: '6px 10px',
              borderRadius: '8px',
              fontSize: '0.78rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <ShieldAlert size={14} />
              <span>CÓ VẬT CẢN PHÍA TRƯỚC</span>
            </div>
          )}
        </div>
      </div>

      {/* Gamepad D-Pad & Emergency Controls */}
      <div className="dpad-card">
        
        {/* 3-Step Speed Selector */}
        <div className="speed-selector-group">
          <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475569' }}>Tốc Độ Di Chuyển:</label>
          <div className="speed-buttons-row">
            {[
              { label: '🐢 Chậm', val: 0.2 },
              { label: '🚶 Vừa', val: 0.35 },
              { label: '⚡ Nhanh', val: 0.6 },
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
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '4px' }}>
          <button type="button" className="btn-emergency-giant" onClick={handleEStop}>
            <AlertOctagon size={20} />
            <span>DỪNG KHẨN CẤP</span>
          </button>

          {isEmergencyStopped && (
            <button type="button" className="btn-reset-estop-clean" onClick={handleReset}>
              <RefreshCw size={14} style={{ display: 'inline', marginRight: '6px' }} />
              KHÔI PHỤC HOẠT ĐỘNG
            </button>
          )}
        </div>

      </div>

    </div>
  );
};
