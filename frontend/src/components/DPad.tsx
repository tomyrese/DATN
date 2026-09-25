import React, { useState } from 'react';
import { RobotSocket } from '../services/RobotSocket';
import { ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Square } from 'lucide-react';

interface DPadProps {
  currentSpeed: number;
  disabled?: boolean;
}

export const DPad: React.FC<DPadProps> = ({ currentSpeed, disabled = false }) => {
  const [activeDir, setActiveDir] = useState<string | null>(null);

  const startDrive = (dir: 'forward' | 'backward' | 'left' | 'right', e: React.SyntheticEvent) => {
    e.preventDefault();
    if (disabled) return;
    setActiveDir(dir);
    RobotSocket.getInstance().startDriveLoop(dir, currentSpeed);
  };

  const stopDrive = (e: React.SyntheticEvent) => {
    e.preventDefault();
    setActiveDir(null);
    RobotSocket.getInstance().stopDriveLoop();
  };

  const handleManualStop = (e: React.SyntheticEvent) => {
    e.preventDefault();
    setActiveDir(null);
    RobotSocket.getInstance().sendStop();
  };

  return (
    <div className="dpad-wrapper">
      <div className="dpad-container">
        {/* Forward */}
        <button
          className={`dpad-btn dpad-up ${activeDir === 'forward' ? 'active' : ''}`}
          disabled={disabled}
          onMouseDown={(e) => startDrive('forward', e)}
          onMouseUp={stopDrive}
          onMouseLeave={stopDrive}
          onTouchStart={(e) => startDrive('forward', e)}
          onTouchEnd={stopDrive}
          title="Forward (W / Up Arrow)"
        >
          <ArrowUp size={22} />
          <span>FORWARD</span>
        </button>

        {/* Mid Row (Left - Stop - Right) */}
        <div className="dpad-mid-row">
          <button
            className={`dpad-btn dpad-left ${activeDir === 'left' ? 'active' : ''}`}
            disabled={disabled}
            onMouseDown={(e) => startDrive('left', e)}
            onMouseUp={stopDrive}
            onMouseLeave={stopDrive}
            onTouchStart={(e) => startDrive('left', e)}
            onTouchEnd={stopDrive}
            title="Turn Left (A / Left Arrow)"
          >
            <ArrowLeft size={22} />
            <span>LEFT</span>
          </button>

          <button
            className="dpad-btn dpad-stop"
            disabled={disabled}
            onClick={handleManualStop}
            title="Stop (Space / X)"
          >
            <Square size={18} fill="#FF1744" stroke="none" />
            <span>STOP</span>
          </button>

          <button
            className={`dpad-btn dpad-right ${activeDir === 'right' ? 'active' : ''}`}
            disabled={disabled}
            onMouseDown={(e) => startDrive('right', e)}
            onMouseUp={stopDrive}
            onMouseLeave={stopDrive}
            onTouchStart={(e) => startDrive('right', e)}
            onTouchEnd={stopDrive}
            title="Turn Right (D / Right Arrow)"
          >
            <ArrowRight size={22} />
            <span>RIGHT</span>
          </button>
        </div>

        {/* Backward */}
        <button
          className={`dpad-btn dpad-down ${activeDir === 'backward' ? 'active' : ''}`}
          disabled={disabled}
          onMouseDown={(e) => startDrive('backward', e)}
          onMouseUp={stopDrive}
          onMouseLeave={stopDrive}
          onTouchStart={(e) => startDrive('backward', e)}
          onTouchEnd={stopDrive}
          title="Backward (S / Down Arrow)"
        >
          <ArrowDown size={22} />
          <span>BACKWARD</span>
        </button>
      </div>
    </div>
  );
};
