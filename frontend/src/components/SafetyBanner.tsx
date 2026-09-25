import React from 'react';
import { useRobotStore } from '../store/useRobotStore';
import { RobotSocket } from '../services/RobotSocket';
import { RobotApi } from '../services/RobotApi';

export const SafetyBanner: React.FC = () => {
  const { isEmergencyStopped, safetyState, personDetected, personConfidence, robotState, connectionStatus, pairedRobot } = useRobotStore();

  const handleResetEStop = () => {
    if (window.confirm('Confirm Safety Reset: Are you sure the area around the robot is clear of obstacles?')) {
      RobotSocket.getInstance().sendEmergencyReset();
      if (pairedRobot) {
        RobotApi.emergencyReset(pairedRobot.host, pairedRobot.port, pairedRobot.token);
      }
    }
  };

  if (isEmergencyStopped || safetyState === 'ERROR_STOP') {
    return (
      <section className="safety-banner-wrapper">
        <div className="safety-banner banner-danger">
          <span className="banner-icon-dot"></span>
          <div className="banner-text-box">
            <h2 className="banner-title">EMERGENCY STOP ACTIVE</h2>
            <p className="banner-desc">Hardware motor power latched off. Check surroundings and click Reset Interlock.</p>
          </div>
          <button className="btn-banner-reset" onClick={handleResetEStop}>
            RESET INTERLOCK (R)
          </button>
        </div>
      </section>
    );
  }

  if (personDetected || safetyState === 'PERSON_DETECTED' || robotState === 'PERSON_DETECTED') {
    const percent = Math.round(personConfidence * 100);
    return (
      <section className="safety-banner-wrapper">
        <div className="safety-banner banner-warning">
          <span className="banner-icon-dot"></span>
          <div className="banner-text-box">
            <h2 className="banner-title">PERSON DETECTED IN PATH ({percent}%)</h2>
            <p className="banner-desc">Robot stopped automatically. Motion interlock active until path is clear.</p>
          </div>
        </div>
      </section>
    );
  }

  if (robotState === 'CAMERA_ERROR') {
    return (
      <section className="safety-banner-wrapper">
        <div className="safety-banner banner-danger">
          <span className="banner-icon-dot"></span>
          <div className="banner-text-box">
            <h2 className="banner-title">CSI CAMERA FEED ERROR</h2>
            <p className="banner-desc">Video stream lost. Hardware fail-safe stop engaged.</p>
          </div>
        </div>
      </section>
    );
  }

  if (connectionStatus !== 'CONNECTED') {
    return (
      <section className="safety-banner-wrapper">
        <div className="safety-banner banner-warning">
          <span className="banner-icon-dot"></span>
          <div className="banner-text-box">
            <h2 className="banner-title">WEBSOCKET DISCONNECTED</h2>
            <p className="banner-desc">Fail-Safe stop active. Awaiting connection to Pi Robot...</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="safety-banner-wrapper">
      <div className="safety-banner banner-clear">
        <span className="banner-icon-dot"></span>
        <div className="banner-text-box">
          <h2 className="banner-title">SAFETY SYSTEM OPERATIONAL (ALL CLEAR)</h2>
          <p className="banner-desc">Autonomous safety interlock active. No obstacles in stop zone.</p>
        </div>
      </div>
    </section>
  );
};
