import React, { useState, useEffect } from 'react';
import { RobotSocket } from '../services/RobotSocket';
import { RobotApi } from '../services/RobotApi';
import { useRobotStore } from '../store/useRobotStore';
import { ChevronUp, ChevronDown, ChevronLeft, ChevronRight, Square } from 'lucide-react';

interface DPadProps {
  currentSpeed: number;
  disabled?: boolean;
}

export const DPad: React.FC<DPadProps> = ({ currentSpeed, disabled }) => {
  const { pairedRobot } = useRobotStore();
  const [activeDirection, setActiveDirection] = useState<string | null>(null);

  const startDrive = (direction: 'forward' | 'backward' | 'left' | 'right') => {
    if (disabled) return;
    setActiveDirection(direction);
    RobotSocket.getInstance().startDriveLoop(direction, currentSpeed);

    // Direct HTTP fallback call for instant response
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    RobotApi.directDrive(host, port, direction, currentSpeed);
  };

  const stopDrive = () => {
    setActiveDirection(null);
    RobotSocket.getInstance().stopDriveLoop();

    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    RobotApi.directDrive(host, port, 'stop', 0);
  };

  useEffect(() => {
    const handleGlobalEnd = () => {
      if (activeDirection) {
        stopDrive();
      }
    };
    window.addEventListener('mouseup', handleGlobalEnd);
    window.addEventListener('touchend', handleGlobalEnd);
    window.addEventListener('touchcancel', handleGlobalEnd);
    return () => {
      window.removeEventListener('mouseup', handleGlobalEnd);
      window.removeEventListener('touchend', handleGlobalEnd);
      window.removeEventListener('touchcancel', handleGlobalEnd);
    };
  }, [activeDirection]);

  return (
    <div className="dpad-3x3" role="group" aria-label="Robot Directional Controls">
      {/* Row 1: Up */}
      <div />
      <button
        type="button"
        className={`dpad-btn-key ${activeDirection === 'forward' ? 'is-pressed' : ''}`}
        onMouseDown={(e) => { e.preventDefault(); startDrive('forward'); }}
        onTouchStart={(e) => { e.preventDefault(); startDrive('forward'); }}
        onMouseUp={(e) => { e.preventDefault(); stopDrive(); }}
        onTouchEnd={(e) => { e.preventDefault(); stopDrive(); }}
        disabled={disabled}
        title="Tiến lên"
      >
        <ChevronUp size={28} />
        <span className="dpad-sub-hint">TIẾN</span>
      </button>
      <div />

      {/* Row 2: Left - Stop - Right */}
      <button
        type="button"
        className={`dpad-btn-key ${activeDirection === 'left' ? 'is-pressed' : ''}`}
        onMouseDown={(e) => { e.preventDefault(); startDrive('left'); }}
        onTouchStart={(e) => { e.preventDefault(); startDrive('left'); }}
        onMouseUp={(e) => { e.preventDefault(); stopDrive(); }}
        onTouchEnd={(e) => { e.preventDefault(); stopDrive(); }}
        disabled={disabled}
        title="Rẽ trái"
      >
        <ChevronLeft size={28} />
        <span className="dpad-sub-hint">TRÁI</span>
      </button>

      <button
        type="button"
        className="dpad-btn-key btn-center-stop"
        onClick={(e) => { e.preventDefault(); stopDrive(); }}
        onTouchStart={(e) => { e.preventDefault(); stopDrive(); }}
        disabled={disabled}
        title="Dừng xe"
      >
        <Square size={20} fill="currentColor" />
        <span className="dpad-sub-hint">DỪNG</span>
      </button>

      <button
        type="button"
        className={`dpad-btn-key ${activeDirection === 'right' ? 'is-pressed' : ''}`}
        onMouseDown={(e) => { e.preventDefault(); startDrive('right'); }}
        onTouchStart={(e) => { e.preventDefault(); startDrive('right'); }}
        onMouseUp={(e) => { e.preventDefault(); stopDrive(); }}
        onTouchEnd={(e) => { e.preventDefault(); stopDrive(); }}
        disabled={disabled}
        title="Rẽ phải"
      >
        <ChevronRight size={28} />
        <span className="dpad-sub-hint">PHẢI</span>
      </button>

      {/* Row 3: Down */}
      <div />
      <button
        type="button"
        className={`dpad-btn-key ${activeDirection === 'backward' ? 'is-pressed' : ''}`}
        onMouseDown={(e) => { e.preventDefault(); startDrive('backward'); }}
        onTouchStart={(e) => { e.preventDefault(); startDrive('backward'); }}
        onMouseUp={(e) => { e.preventDefault(); stopDrive(); }}
        onTouchEnd={(e) => { e.preventDefault(); stopDrive(); }}
        disabled={disabled}
        title="Lùi lại"
      >
        <ChevronDown size={28} />
        <span className="dpad-sub-hint">LÙI</span>
      </button>
      <div />
    </div>
  );
};
