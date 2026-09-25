import React from 'react';
import { useRobotStore } from '../store/useRobotStore';
import { TabType } from '../components/NavigationTabs';
import { EmergencyButton } from '../components/EmergencyButton';

interface DashboardTabProps {
  onSelectTab: (tab: TabType) => void;
}

export const DashboardTab: React.FC<DashboardTabProps> = ({ onSelectTab }) => {
  const { telemetry } = useRobotStore();

  const camFps = telemetry?.cameraFps ? telemetry.cameraFps.toFixed(1) : '0.0';
  const infFps = telemetry?.inferenceFps ? telemetry.inferenceFps.toFixed(1) : '0.0';
  const cpuTemp = telemetry?.cpuTemp ? `${telemetry.cpuTemp.toFixed(1)} °C` : '--';
  const cpuLoad = telemetry?.cpuUsage !== undefined && telemetry?.cpuUsage !== null ? `${Math.round(telemetry.cpuUsage)}%` : '--%';
  const ramLoad = telemetry?.memoryUsage !== undefined && telemetry?.memoryUsage !== null ? `${Math.round(telemetry.memoryUsage)}%` : '--%';
  const isPerson = telemetry?.personDetected;

  const m1 = Math.round((telemetry?.m1 || 0) * 100);
  const m2 = Math.round((telemetry?.m2 || 0) * 100);
  const m3 = Math.round((telemetry?.m3 || 0) * 100);
  const m4 = Math.round((telemetry?.m4 || 0) * 100);

  return (
    <div className="tab-pane active">
      <div className="dashboard-hero-grid">
        
        {/* HUD Card */}
        <div className="card hud-card">
          <div className="card-header">
            <span className="card-tag">SYSTEM TELEMETRY HUD</span>
            <div className="live-tag">
              <span className="pulse-dot"></span> LIVE FEED
            </div>
          </div>

          <div className="hud-metric-grid">
            <div className="hud-metric-box">
              <span className="hud-metric-label">CSI CAM FPS</span>
              <span className="hud-metric-value text-cyan">{camFps}</span>
              <span className="hud-metric-unit">Picamera2 640x480</span>
            </div>
            <div className="hud-metric-box">
              <span className="hud-metric-label">AI INFERENCE</span>
              <span className="hud-metric-value text-cyan">{infFps}</span>
              <span className="hud-metric-unit">SSD MobileNet V2</span>
            </div>
            <div className="hud-metric-box">
              <span className="hud-metric-label">CPU TEMP</span>
              <span className="hud-metric-value text-green">{cpuTemp}</span>
              <span className="hud-metric-unit">BCM2711 SoC</span>
            </div>
            <div className="hud-metric-box">
              <span className="hud-metric-label">CPU LOAD</span>
              <span className="hud-metric-value text-cyan">{cpuLoad}</span>
              <span className="hud-metric-unit">4x Cortex-A72</span>
            </div>
            <div className="hud-metric-box">
              <span className="hud-metric-label">RAM USAGE</span>
              <span className="hud-metric-value text-cyan">{ramLoad}</span>
              <span className="hud-metric-unit">LPDDR4 System RAM</span>
            </div>
            <div className="hud-metric-box">
              <span className="hud-metric-label">SAFETY ZONE</span>
              <span className={`hud-metric-value ${isPerson ? 'text-red' : 'text-green'}`}>
                {isPerson ? 'DETECTED' : 'CLEAR'}
              </span>
              <span className="hud-metric-unit">Center Path [0.2 - 0.8]</span>
            </div>
          </div>

          {/* Motor Output Bars */}
          <div className="motor-telemetry-sub">
            <span className="sub-section-title">MOTOR DRIVER OUTPUTS (TB6612FNG 4-CHANNELS)</span>
            <div className="motor-bars-grid">
              <div className="motor-bar-item">
                <div className="bar-header"><span>M1 (FL)</span><span>{m1}%</span></div>
                <div className="bar-track"><div className="bar-fill" style={{ width: `${Math.abs(m1)}%` }}></div></div>
              </div>
              <div className="motor-bar-item">
                <div className="bar-header"><span>M3 (FR)</span><span>{m3}%</span></div>
                <div className="bar-track"><div className="bar-fill" style={{ width: `${Math.abs(m3)}%` }}></div></div>
              </div>
              <div className="motor-bar-item">
                <div className="bar-header"><span>M2 (RL)</span><span>{m2}%</span></div>
                <div className="bar-track"><div className="bar-fill" style={{ width: `${Math.abs(m2)}%` }}></div></div>
              </div>
              <div className="motor-bar-item">
                <div className="bar-header"><span>M4 (RR)</span><span>{m4}%</span></div>
                <div className="bar-track"><div className="bar-fill" style={{ width: `${Math.abs(m4)}%` }}></div></div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Nav Tiles */}
        <div className="tiles-grid">
          <div className="menu-tile tile-primary" onClick={() => onSelectTab('control')}>
            <div className="tile-top"><span className="tile-pill">DRIVE</span><span className="tile-badge">WASD</span></div>
            <h3 className="tile-title">DRIVE CONTROLLER</h3>
            <p className="tile-desc">Tactile D-Pad, Throttle slider, Hotkeys & Live PIP camera.</p>
          </div>
          <div className="menu-tile tile-cyan" onClick={() => onSelectTab('camera')}>
            <div className="tile-top"><span className="tile-pill">VISION</span><span className="tile-badge">CSI</span></div>
            <h3 className="tile-title">CSI CAMERA FEED</h3>
            <p className="tile-desc">High-framerate MJPEG stream & real-time AI bounding boxes.</p>
          </div>
          <div className="menu-tile" onClick={() => onSelectTab('diagnostics')}>
            <div className="tile-top"><span className="tile-pill">STATS</span></div>
            <h3 className="tile-title">SYSTEM DIAGNOSTICS</h3>
            <p className="tile-desc">System vitals, thermal charts, and real-time terminal logs.</p>
          </div>
          <div className="menu-tile" onClick={() => onSelectTab('motor-test')}>
            <div className="tile-top"><span className="tile-pill">BENCH</span></div>
            <h3 className="tile-title">MOTOR BENCH TEST</h3>
            <p className="tile-desc">Individual directional testing for all 4 DC motor channels.</p>
          </div>
        </div>

      </div>

      <div className="emergency-action-section">
        <EmergencyButton />
      </div>
    </div>
  );
};
