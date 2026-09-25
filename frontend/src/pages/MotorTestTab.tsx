import React, { useState } from 'react';
import { RobotSocket } from '../services/RobotSocket';
import { useRobotStore } from '../store/useRobotStore';

const MOTORS = [
  { id: 1, name: 'MOTOR 1 (FRONT LEFT)', channel: 'TB_L Channel A • GPIO13 / GPIO5,6' },
  { id: 2, name: 'MOTOR 2 (REAR LEFT)', channel: 'TB_L Channel B • GPIO19 / GPIO26,22' },
  { id: 3, name: 'MOTOR 3 (FRONT RIGHT)', channel: 'TB_R Channel A • GPIO12 / GPIO16,20' },
  { id: 4, name: 'MOTOR 4 (REAR RIGHT)', channel: 'TB_R Channel B • GPIO18 / GPIO23,24' },
];

export const MotorTestTab: React.FC = () => {
  const { telemetry, isSafetyBlocked, isEmergencyStopped, connectionStatus } = useRobotStore();
  const [activeMotor, setActiveMotor] = useState<number | null>(null);

  const disabled = connectionStatus !== 'CONNECTED' || isSafetyBlocked || isEmergencyStopped;

  const startTest = (motorId: number, speed: number, e: React.SyntheticEvent) => {
    e.preventDefault();
    if (disabled) return;
    setActiveMotor(motorId);
    RobotSocket.getInstance().sendMotorTest(motorId, speed);
  };

  const stopTest = (motorId: number, e: React.SyntheticEvent) => {
    e.preventDefault();
    setActiveMotor(null);
    RobotSocket.getInstance().sendMotorTest(motorId, 0.0);
  };

  const handleStopAll = () => {
    RobotSocket.getInstance().sendStop();
  };

  const getSpeedForMotor = (id: number) => {
    if (!telemetry) return '0%';
    let val = 0;
    if (id === 1) val = telemetry.m1;
    if (id === 2) val = telemetry.m2;
    if (id === 3) val = telemetry.m3;
    if (id === 4) val = telemetry.m4;
    return `${Math.round(val * 100)}%`;
  };

  return (
    <div className="tab-pane active">
      <div className="bench-layout">
        
        <div className="warning-banner">
          <span className="warning-title">⚠️ MOTOR BENCH TEST MODE</span>
          <p className="warning-desc">
            Ensure the robot is placed safely on a workbench stand with all 4 wheels elevated off the ground. Press and hold to spin each motor at 20% test speed.
          </p>
        </div>

        <div className="motors-grid">
          {MOTORS.map(m => (
            <div
              key={m.id}
              className={`motor-test-card ${activeMotor === m.id ? 'active-motor' : ''}`}
            >
              <div className="motor-card-header">
                <div>
                  <h3 className="motor-title">{m.name}</h3>
                  <span className="motor-channel">{m.channel}</span>
                </div>
                <span className="motor-speed-pill">{getSpeedForMotor(m.id)}</span>
              </div>
              <div className="motor-test-actions">
                <button
                  className="btn-motor-test btn-fwd"
                  disabled={disabled}
                  onMouseDown={(e) => startTest(m.id, 0.20, e)}
                  onMouseUp={(e) => stopTest(m.id, e)}
                  onMouseLeave={(e) => stopTest(m.id, e)}
                  onTouchStart={(e) => startTest(m.id, 0.20, e)}
                  onTouchEnd={(e) => stopTest(m.id, e)}
                >
                  HOLD FWD (+20%)
                </button>
                <button
                  className="btn-motor-test btn-rev"
                  disabled={disabled}
                  onMouseDown={(e) => startTest(m.id, -0.20, e)}
                  onMouseUp={(e) => stopTest(m.id, e)}
                  onMouseLeave={(e) => stopTest(m.id, e)}
                  onTouchStart={(e) => startTest(m.id, -0.20, e)}
                  onTouchEnd={(e) => stopTest(m.id, e)}
                >
                  HOLD REV (-20%)
                </button>
              </div>
            </div>
          ))}
        </div>

        <button className="btn-emergency-stop" onClick={handleStopAll}>
          STOP ALL MOTORS
        </button>

      </div>
    </div>
  );
};
