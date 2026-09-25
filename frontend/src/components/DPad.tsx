import React, { useState, useEffect } from 'react';
import { RobotSocket } from '../services/RobotSocket';
import { ChevronUp, ChevronDown, ChevronLeft, ChevronRight, Square } from 'lucide-react';

interface DPadProps {
  currentSpeed: number;
  disabled?: boolean;
}

export const DPad: React.FC<DPadProps> = ({ currentSpeed, disabled }) => {
  const [activeDirection, setActiveDirection] = useState<string | null>(null);

  const startDrive = (direction: 'forward' | 'backward' | 'left' | 'right') => {
    if (disabled) return;
    setActiveDirection(direction);
    RobotSocket.getInstance().startDriveLoop(direction, currentSpeed);
  };

  const stopDrive = () => {
    setActiveDirection(null);
    RobotSocket.getInstance().stopDriveLoop();
  };

  useEffect(() => {
    const handleMouseUp = () => {
      if (activeDirection) {
        stopDrive();
      }
    };
    window.addEventListener('mouseup', handleMouseUp);
    window.addEventListener('touchend', handleMouseUp);
    return () => {
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('touchend', handleMouseUp);
    };
  }, [activeDirection]);

  return (
    <div className="dpad-3x3" role="group" aria-label="Robot Directional Controls">
      {/* Row 1: Empty - Forward - Empty */}
      <div />
      <button
        type="button"
        className={`dpad-btn-key ${activeDirection === 'forward' ? 'is-pressed' : ''}`}
        onMouseDown={() => startDrive('forward')}
        onTouchStart={() => startDrive('forward')}
        disabled={disabled}
        title="Tiến lên (Phím W / Mũi tên lên)"
      >
        <ChevronUp size={28} />
        <span className="dpad-sub-hint">TIẾN [W]</span>
      </button>
      <div />

      {/* Row 2: Left - Stop - Right */}
      <button
        type="button"
        className={`dpad-btn-key ${activeDirection === 'left' ? 'is-pressed' : ''}`}
        onMouseDown={() => startDrive('left')}
        onTouchStart={() => startDrive('left')}
        disabled={disabled}
        title="Rẽ trái (Phím A / Mũi tên trái)"
      >
        <ChevronLeft size={28} />
        <span className="dpad-sub-hint">TRÁI [A]</span>
      </button>

      <button
        type="button"
        className="dpad-btn-key btn-center-stop"
        onClick={stopDrive}
        disabled={disabled}
        title="Dừng xe (Phím Space)"
      >
        <Square size={22} fill="currentColor" />
        <span className="dpad-sub-hint">DỪNG [Space]</span>
      </button>

      <button
        type="button"
        className={`dpad-btn-key ${activeDirection === 'right' ? 'is-pressed' : ''}`}
        onMouseDown={() => startDrive('right')}
        onTouchStart={() => startDrive('right')}
        disabled={disabled}
        title="Rẽ phải (Phím D / Mũi tên phải)"
      >
        <ChevronRight size={28} />
        <span className="dpad-sub-hint">PHẢI [D]</span>
      </button>

      {/* Row 3: Empty - Backward - Empty */}
      <div />
      <button
        type="button"
        className={`dpad-btn-key ${activeDirection === 'backward' ? 'is-pressed' : ''}`}
        onMouseDown={() => startDrive('backward')}
        onTouchStart={() => startDrive('backward')}
        disabled={disabled}
        title="Lùi lại (Phím S / Mũi tên xuống)"
      >
        <ChevronDown size={28} />
        <span className="dpad-sub-hint">LÙI [S]</span>
      </button>
      <div />
    </div>
  );
};
