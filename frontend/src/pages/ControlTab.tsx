import React, { useState } from 'react';
import { useRobotStore } from '../store/useRobotStore';
import { DPad } from '../components/DPad';
import { RobotSocket } from '../services/RobotSocket';
import { RobotApi } from '../services/RobotApi';
import { Video, AlertOctagon, RefreshCw, ShieldAlert, Compass, MapPin, Zap, Activity, Radio } from 'lucide-react';

interface ControlTabProps {
  cameraTicket: string | null;
}

export const ControlTab: React.FC<ControlTabProps> = ({ cameraTicket }) => {
  const { pairedRobot, settings, telemetry, latencyMs, isEmergencyStopped } = useRobotStore();
  const [speed, setSpeed] = useState(settings.defaultSpeed || 0.35);

  const disabled = isEmergencyStopped;

  const rawOdomX = telemetry?.odometryX ?? 50.0;
  const rawOdomY = telemetry?.odometryY ?? 51.0;
  const odomHeading = telemetry?.odometryHeading ?? 0;
  const odomHeadingDeg = Math.round((odomHeading * 180) / Math.PI);
  const odomConfidence = Math.round((telemetry?.odometryConfidence ?? 0.95) * 100);

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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', width: '100%' }}>
      
      {/* Staff & Admin Technical Telemetry HUD Bar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '10px 16px',
        backgroundColor: '#FFFFFF',
        borderRadius: '14px',
        border: '1px solid #E2E8F0',
        boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
        gap: '10px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: isEmergencyStopped ? '#EF4444' : (telemetry?.robotState === 'STOPPED' ? '#10B981' : '#3B82F6'),
          }} />
          <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#0F172A' }}>
            ROBOT: {telemetry?.robotState || 'SẴN SÀNG'}
          </span>
          <span style={{
            fontSize: '0.7rem',
            padding: '2px 8px',
            borderRadius: '6px',
            backgroundColor: '#EFF6FF',
            color: '#1D4ED8',
            fontWeight: 800
          }}>
            STAFF CONSOLE
          </span>
        </div>

        {/* Real Odometry Metrics for Authorized Technicians */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          gap: '12px',
          fontSize: '0.75rem',
          color: '#475569'
        }}>
          <span title="Tọa độ tích phân Dead-Reckoning">
            📍 <strong>X:</strong> {rawOdomX.toFixed(1)}m, <strong>Y:</strong> {rawOdomY.toFixed(1)}m
          </span>
          <span title="Góc hướng Robot">
            🧭 <strong>Hướng:</strong> {odomHeadingDeg}°
          </span>
          <span title="Độ tin cậy cảm biến" style={{ color: odomConfidence > 80 ? '#059669' : '#D97706', fontWeight: 700 }}>
            ⚡ Tin cậy: {odomConfidence}%
          </span>
          <span style={{
            fontSize: '0.68rem',
            padding: '2px 6px',
            borderRadius: '4px',
            backgroundColor: '#FEF3C7',
            color: '#B45309',
            fontWeight: 800
          }}>
            [DEAD-RECKONING]
          </span>
          {latencyMs > 0 && (
            <span style={{ fontSize: '0.7rem', color: '#64748B' }}>
              📡 {latencyMs}ms
            </span>
          )}
        </div>
      </div>

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

          {/* Ultrasonic & Safety State Bar */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: '#F8FAFC',
            padding: '8px 12px',
            borderRadius: '8px',
            border: '1px solid #E2E8F0',
            fontSize: '0.75rem',
            color: '#334155'
          }}>
            <div>
              <span style={{ fontWeight: 600 }}>Cảm biến HC-SR04: </span>
              <span>Trái: <strong>{telemetry?.ultrasonicLeft !== undefined && telemetry?.ultrasonicLeft !== null ? Math.round(telemetry.ultrasonicLeft) : '—'}cm</strong></span>
              <span style={{ margin: '0 4px', color: '#CBD5E1' }}>|</span>
              <span>Phải: <strong>{telemetry?.ultrasonicRight !== undefined && telemetry?.ultrasonicRight !== null ? Math.round(telemetry.ultrasonicRight) : '—'}cm</strong></span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{
                padding: '2px 8px',
                borderRadius: '4px',
                fontSize: '0.7rem',
                fontWeight: 800,
                background: telemetry?.obstacleState && telemetry.obstacleState !== 'CLEAR' ? '#FEE2E2' : '#DCFCE7',
                color: telemetry?.obstacleState && telemetry.obstacleState !== 'CLEAR' ? '#DC2626' : '#15803D'
              }}>
                {telemetry?.obstacleState || 'CLEAR'}
              </span>
            </div>
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
    </div>
  );
};
