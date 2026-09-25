import React from 'react';
import { useRobotStore } from '../store/useRobotStore';
import { RobotApi } from '../services/RobotApi';
import { Camera } from 'lucide-react';

interface CameraTabProps {
  cameraTicket: string | null;
}

export const CameraTab: React.FC<CameraTabProps> = ({ cameraTicket }) => {
  const { pairedRobot, telemetry } = useRobotStore();

  const streamUrl = pairedRobot
    ? (cameraTicket
        ? `${RobotApi.getBaseUrl(pairedRobot.host, pairedRobot.port)}/api/v1/camera/mjpeg?ticket=${cameraTicket}`
        : `${RobotApi.getBaseUrl(pairedRobot.host, pairedRobot.port)}/api/v1/camera/mjpeg?token=${pairedRobot.token}`)
    : '';

  const handleSnapshot = () => {
    if (!pairedRobot) return;
    const url = `${RobotApi.getBaseUrl(pairedRobot.host, pairedRobot.port)}/api/v1/camera/snapshot?token=${pairedRobot.token}`;
    window.open(url, '_blank');
  };

  const camFps = telemetry?.cameraFps ? telemetry.cameraFps.toFixed(1) : '0.0';
  const infFps = telemetry?.inferenceFps ? telemetry.inferenceFps.toFixed(1) : '0.0';
  const confPercent = telemetry?.personConfidence ? Math.round(telemetry.personConfidence * 100) : 0;

  return (
    <div className="tab-pane active">
      <div className="camera-layout-grid">
        
        {/* Stream Viewport Card */}
        <div className="card camera-feed-card">
          <div className="card-header">
            <div>
              <span className="card-tag">RASPBERRY PI CSI CAMERA STREAM</span>
              <div className="card-sub">640x480 @ 30 FPS Hardware CSI (Picamera2)</div>
            </div>
            <button className="btn-sm" onClick={handleSnapshot}>
              <Camera size={14} style={{ display: 'inline', marginRight: 4 }} />
              Snapshot
            </button>
          </div>

          <div className="stream-viewport full-viewport">
            {streamUrl ? (
              <img src={streamUrl} alt="CSI Camera Feed" />
            ) : (
              <div className="stream-placeholder">
                <div className="loader-spinner"></div>
                <span>Connecting to robot camera stream...</span>
              </div>
            )}
            <div className="stream-hud-overlay">
              <div className="overlay-pill left-pill">
                <span className="pulse-dot"></span>
                <span>CAM: {camFps} FPS</span>
              </div>
              {telemetry?.personDetected && (
                <div className="overlay-pill right-pill">
                  <span>PERSON DETECTED ({confPercent}%)</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* AI & Vision Specs */}
        <div className="card ai-meta-card">
          <span className="card-tag">AI VISION PIPELINE & STOP ZONE SPECS</span>
          <div className="meta-table">
            <div className="meta-row">
              <span className="meta-key">Camera Backend:</span>
              <span className="meta-val">Picamera2 Native (RGB888)</span>
            </div>
            <div className="meta-row">
              <span className="meta-key">AI Detection Model:</span>
              <span className="meta-val">SSD MobileNet V2 COCO (INT8)</span>
            </div>
            <div className="meta-row">
              <span className="meta-key">Inference Speed:</span>
              <span className="meta-val">{infFps} FPS</span>
            </div>
            <div className="meta-row">
              <span className="meta-key">Active Stop Zone X:</span>
              <span className="meta-val">20% to 80% Horizontal Center</span>
            </div>
            <div className="meta-row">
              <span className="meta-key">Safety Clear Delay:</span>
              <span className="meta-val">1.5s Anti-Flicker Hysteresis</span>
            </div>
            <div className="meta-row">
              <span className="meta-key">Auto-Resume Policy:</span>
              <span className="meta-val text-green">STRICT LOCKOUT</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
