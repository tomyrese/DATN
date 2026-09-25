import React from 'react';

interface ThrottleSliderProps {
  speed: number;
  onSpeedChange: (speed: number) => void;
  disabled?: boolean;
}

const PRESETS = [
  { value: 0.20, label: 'ECO 20%' },
  { value: 0.35, label: 'STD 35%' },
  { value: 0.50, label: 'MID 50%' },
  { value: 0.75, label: 'PWR 75%' },
  { value: 1.00, label: 'MAX 100%' },
];

export const ThrottleSlider: React.FC<ThrottleSliderProps> = ({ speed, onSpeedChange, disabled = false }) => {
  const percent = Math.round(speed * 100);

  return (
    <div className="throttle-box">
      <div className="throttle-header">
        <div>
          <span className="card-tag">THROTTLE CONTROL</span>
          <div className="card-sub">Target Motor Output Power</div>
        </div>
        <div className="throttle-val-badge">{percent}%</div>
      </div>

      <input
        type="range"
        className="throttle-slider"
        min={20}
        max={100}
        step={5}
        value={percent}
        disabled={disabled}
        onChange={(e) => onSpeedChange(parseInt(e.target.value, 10) / 100)}
      />

      <div className="speed-presets-row">
        {PRESETS.map(item => {
          const isSelected = Math.abs(speed - item.value) < 0.02;
          return (
            <button
              key={item.value}
              className={`speed-chip ${isSelected ? 'active' : ''}`}
              disabled={disabled}
              onClick={() => onSpeedChange(item.value)}
            >
              {item.label}
            </button>
          );
        })}
      </div>
    </div>
  );
};
