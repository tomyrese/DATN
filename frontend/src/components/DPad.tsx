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
      <div className="dpad-grid-container">
        {/* Forward (Row 1, Col 2) */}
        <button
          className={`dpad-key dpad-key-up ${activeDir === 'forward' ? 'active' : ''}`}
          disabled={disabled}
          onMouseDown={(e) => startDrive('forward', e)}
          onMouseUp={stopDrive}
          onMouseLeave={stopDrive}
          onTouchStart={(e) => startDrive('forward', e)}
          onTouchEnd={stopDrive}
          onTouchCancel={stopDrive}
          onContextMenu={(e) => e.preventDefault()}
          title="Tiến (W / Mũi tên Lên)"
        >
          <ArrowUp size={24} />
          <span>TIẾN (W)</span>
        </button>

        {/* Turn Left (Row 2, Col 1) */}
        <button
          className={`dpad-key dpad-key-left ${activeDir === 'left' ? 'active' : ''}`}
          disabled={disabled}
          onMouseDown={(e) => startDrive('left', e)}
          onMouseUp={stopDrive}
          onMouseLeave={stopDrive}
          onTouchStart={(e) => startDrive('left', e)}
          onTouchEnd={stopDrive}
          onTouchCancel={stopDrive}
          onContextMenu={(e) => e.preventDefault()}
          title="Rẽ Trái (A / Mũi tên Trái)"
        >
          <ArrowLeft size={24} />
          <span>TRÁI (A)</span>
        </button>

        {/* Center Stop Button (Row 2, Col 2) */}
        <button
          className="dpad-key dpad-key-stop"
          disabled={disabled}
          onClick={handleManualStop}
          onContextMenu={(e) => e.preventDefault()}
          title="Dừng (Space / X)"
        >
          <Square size={20} fill="#EF4444" stroke="none" />
          <span>DỪNG</span>
        </button>

        {/* Turn Right (Row 2, Col 3) */}
        <button
          className={`dpad-key dpad-key-right ${activeDir === 'right' ? 'active' : ''}`}
          disabled={disabled}
          onMouseDown={(e) => startDrive('right', e)}
          onMouseUp={stopDrive}
          onMouseLeave={stopDrive}
          onTouchStart={(e) => startDrive('right', e)}
          onTouchEnd={stopDrive}
          onTouchCancel={stopDrive}
          onContextMenu={(e) => e.preventDefault()}
          title="Rẽ Phải (D / Mũi tên Phải)"
        >
          <ArrowRight size={24} />
          <span>PHẢI (D)</span>
        </button>

        {/* Backward (Row 3, Col 2) */}
        <button
          className={`dpad-key dpad-key-down ${activeDir === 'backward' ? 'active' : ''}`}
          disabled={disabled}
          onMouseDown={(e) => startDrive('backward', e)}
          onMouseUp={stopDrive}
          onMouseLeave={stopDrive}
          onTouchStart={(e) => startDrive('backward', e)}
          onTouchEnd={stopDrive}
          onTouchCancel={stopDrive}
          onContextMenu={(e) => e.preventDefault()}
          title="Lùi (S / Mũi tên Xuống)"
        >
          <ArrowDown size={24} />
          <span>LÙI (S)</span>
        </button>
      </div>
    </div>
  );
};
