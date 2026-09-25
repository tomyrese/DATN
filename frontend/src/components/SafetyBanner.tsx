import React from 'react';
import { useRobotStore } from '../store/useRobotStore';
import { RobotSocket } from '../services/RobotSocket';
import { RobotApi } from '../services/RobotApi';
import { AlertTriangle, AlertOctagon, RotateCcw } from 'lucide-react';

export const SafetyBanner: React.FC = () => {
  const { isEmergencyStopped, safetyState, personDetected, robotState, pairedRobot } = useRobotStore();

  const handleResetEStop = () => {
    RobotSocket.getInstance().sendEmergencyReset();
    if (pairedRobot) {
      RobotApi.emergencyReset(pairedRobot.host, pairedRobot.port, pairedRobot.token);
    }
  };

  if (isEmergencyStopped || safetyState === 'ERROR_STOP') {
    return (
      <div style={{
        background: '#FEF2F2',
        border: '1px solid #FECACA',
        borderRadius: '12px',
        padding: '10px 14px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '8px',
        color: '#DC2626',
        fontSize: '0.85rem',
        fontWeight: 700
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertOctagon size={18} />
          <span>ĐANG DỪNG KHẨN CẤP</span>
        </div>
        <button
          onClick={handleResetEStop}
          style={{
            background: '#DC2626',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '6px',
            padding: '5px 12px',
            fontSize: '0.8rem',
            fontWeight: 700,
            cursor: 'pointer'
          }}
        >
          Khôi phục
        </button>
      </div>
    );
  }

  if (personDetected || safetyState === 'PERSON_DETECTED' || robotState === 'PERSON_DETECTED') {
    return (
      <div style={{
        background: '#FEF3C7',
        border: '1px solid #FDE68A',
        borderRadius: '12px',
        padding: '8px 12px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        color: '#92400E',
        fontSize: '0.82rem',
        fontWeight: 600
      }}>
        <AlertTriangle size={16} />
        <span>Có vật cản / người phía trước • Robot đang tự động giảm tốc</span>
      </div>
    );
  }

  return null;
};
