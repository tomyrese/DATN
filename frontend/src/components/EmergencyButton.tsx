import React from 'react';
import { RobotSocket } from '../services/RobotSocket';
import { RobotApi } from '../services/RobotApi';
import { useRobotStore } from '../store/useRobotStore';

export const EmergencyButton: React.FC = () => {
  const { pairedRobot } = useRobotStore();

  const handleEStop = () => {
    RobotSocket.getInstance().sendEmergencyStop();
    if (pairedRobot) {
      RobotApi.emergencyStop(pairedRobot.host, pairedRobot.port);
    }
  };

  return (
    <button className="btn-emergency-stop" onClick={handleEStop}>
      <span className="estop-title">CRITICAL EMERGENCY STOP</span>
      <span className="estop-sub">INSTANT POWER CUT & HARDWARE BRAKE (KEY: E)</span>
    </button>
  );
};
