import React, { useState, useEffect } from 'react';
import { useRobotStore } from '../store/useRobotStore';
import { DPad } from '../components/DPad';
import { ThrottleSlider } from '../components/ThrottleSlider';
import { RobotSocket } from '../services/RobotSocket';
import { RobotApi } from '../services/RobotApi';

interface ControlTabProps {
  cameraTicket: string | null;
}

export const ControlTab: React.FC<ControlTabProps> = ({ cameraTicket }) => {
  const { pairedRobot, settings, telemetry, isSafetyBlocked, isEmergencyStopped, connectionStatus } = useRobotStore();
  const [speed, setSpeed] = useState(settings.defaultSpeed || 0.35);

  const disabled = connectionStatus !== 'CONNECTED' || isSafetyBlocked || isEmergencyStopped;

  const handleSpeedChange = (newSpeed: number) => {
    setSpeed(newSpeed);
    RobotSocket.getInstance().updateDriveSpeed(newSpeed);
  };

  const handleEStop = () => {
    RobotSocket.getInstance().sendEmergencyStop();
    if (pairedRobot) {
      RobotApi.emergencyStop(pairedRobot.host, pairedRobot.port);
    }
  };

  const handleReset = () => {
    if (window.confirm('Reset Emergency Stop?')) {
      RobotSocket.getInstance().sendEmergencyReset();
      if (pairedRobot) {
        RobotApi.emergencyReset(pairedRobot.host, pairedRobot.port, pairedRobot.token);
      }
    }
  };

  const streamUrl = pairedRobot
    ? (cameraTicket
        ? `${RobotApi.getBaseUrl(pairedRobot.host, pairedRobot.port)}/api/v1/camera/mjpeg?ticket=${cameraTicket}`
        : `${RobotApi.getBaseUrl(pairedRobot.host, pairedRobot.port)}/api/v1/camera/mjpeg?token=${pairedRobot.token}`)
    : '';

  return (
    <div className="tab-pane active">
      <div className="control-layout-grid">
        
        {/* Left: Mini Camera PIP */}
        {settings.enableCameraPreview && (
          <div className="control-stream-card">
            <div className="card-header">
              <span className="card-tag">LIVE CSI CAMERA PREVIEW</span>
              <span className="live-tag">
                {telemetry?.cameraFps ? telemetry.cameraFps.toFixed(1) : '0.0'} FPS
              </span>
            </div>
            <div className="stream-viewport">
              {streamUrl ? (
                <img src={streamUrl} alt="Camera Feed" />
              ) : (
                <div className="stream-placeholder">
                  <div className="loader-spinner"></div>
                  <span>Awaiting video stream...</span>
                </div>
              )}
              {telemetry?.personDetected && (
                <div className="stream-overlay-warning">
                  <span>PERSON IN SAFETY ZONE</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Right: D-Pad & Controls */}
        <div className="control-pad-card">
          <ThrottleSlider speed={speed} onSpeedChange={handleSpeedChange} disabled={disabled} />

          <DPad currentSpeed={speed} disabled={disabled} />

          <div className="hotkeys-bar">
            <div><kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> Drive</div>
            <div><kbd>SPACE</kbd> Stop</div>
            <div><kbd>1-5</kbd> Speed</div>
            <div><kbd>E</kbd> E-Stop</div>
            <div><kbd>R</kbd> Reset</div>
          </div>

          <div className="ctrl-bottom-estop">
            <button className="btn-emergency-stop" onClick={handleEStop}>
              EMERGENCY STOP (KEY: E)
            </button>
            {isEmergencyStopped && (
              <button className="btn-reset-estop" onClick={handleReset}>
                RESET EMERGENCY STOP (KEY: R)
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
