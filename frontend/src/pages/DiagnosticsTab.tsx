import React from 'react';
import { useRobotStore, updateGlobalState } from '../store/useRobotStore';
import { Copy, Trash2 } from 'lucide-react';

export const DiagnosticsTab: React.FC = () => {
  const { telemetry, logs } = useRobotStore();

  const cpuTemp = telemetry?.cpuTemp ? `${telemetry.cpuTemp.toFixed(1)} °C` : '--';
  const cpuLoad = telemetry?.cpuUsage !== undefined && telemetry?.cpuUsage !== null ? `${Math.round(telemetry.cpuUsage)} %` : '--';
  const ramLoad = telemetry?.memoryUsage !== undefined && telemetry?.memoryUsage !== null ? `${Math.round(telemetry.memoryUsage)} %` : '--';

  const formatUptime = (seconds?: number) => {
    if (!seconds || seconds <= 0) return '0s';
    const sec = Math.floor(seconds % 60);
    const min = Math.floor((seconds / 60) % 60);
    const hrs = Math.floor(seconds / 3600);
    if (hrs > 0) return `${hrs}h ${min}m`;
    if (min > 0) return `${min}m ${sec}s`;
    return `${sec}s`;
  };

  const handleClearLogs = () => {
    updateGlobalState(() => ({ logs: [] }));
  };

  const handleCopyLogs = () => {
    navigator.clipboard.writeText(logs.join('\n')).then(() => alert('Logs copied to clipboard'));
  };

  return (
    <div className="tab-pane active">
      <div className="diagnostics-grid">
        
        {/* Metric Gauges */}
        <div className="card diag-stats-card">
          <span className="card-tag">HARDWARE HEALTH & THERMAL METRICS</span>
          <div className="diag-metrics-row">
            <div className="metric-gauge-box">
              <span className="gauge-label">CPU TEMPERATURE</span>
              <span className="gauge-value text-green">{cpuTemp}</span>
              <span className="gauge-sub">Throttling Limit: 80°C</span>
            </div>
            <div className="metric-gauge-box">
              <span className="gauge-label">CPU USAGE</span>
              <span className="gauge-value text-cyan">{cpuLoad}</span>
              <span className="gauge-sub">4 Cores Active</span>
            </div>
            <div className="metric-gauge-box">
              <span className="gauge-label">MEMORY LOAD</span>
              <span className="gauge-value text-cyan">{ramLoad}</span>
              <span className="gauge-sub">LPDDR4 System RAM</span>
            </div>
            <div className="metric-gauge-box">
              <span className="gauge-label">ROBOT UPTIME</span>
              <span className="gauge-value text-white">{formatUptime(telemetry?.uptime)}</span>
              <span className="gauge-sub">Continuous Operation</span>
            </div>
          </div>
        </div>

        {/* Live Terminal Logs */}
        <div className="card diag-logs-card">
          <div className="card-header">
            <span className="card-tag">REAL-TIME SYSTEM & EVENT LOGS</span>
            <div style={{ display: 'flex', gap: 6 }}>
              <button className="btn-sm" onClick={handleCopyLogs}>
                <Copy size={13} style={{ display: 'inline', marginRight: 4 }} />
                Copy
              </button>
              <button className="btn-sm" onClick={handleClearLogs}>
                <Trash2 size={13} style={{ display: 'inline', marginRight: 4 }} />
                Clear
              </button>
            </div>
          </div>
          <div className="log-terminal">
            {logs.length === 0 ? (
              <div className="log-line text-muted">[SYSTEM] Pi Robot Web Console Initialized. Awaiting events...</div>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="log-line">{log}</div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
