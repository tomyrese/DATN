/**
 * Pi Robot Central Command Web Application Controller
 */

// Application State
const AppState = {
  host: localStorage.getItem('pi_robot_host') || window.location.hostname || 'localhost',
  port: parseInt(localStorage.getItem('pi_robot_port') || window.location.port || '8765', 10),
  token: localStorage.getItem('pi_robot_token') || '',
  robotId: localStorage.getItem('pi_robot_id') || 'RBT01',
  robotName: localStorage.getItem('pi_robot_name') || 'Pi Robot',
  currentSpeed: 0.35,
  miniCameraEnabled: localStorage.getItem('pi_robot_mini_cam') !== 'false',
  autoReconnect: localStorage.getItem('pi_robot_auto_rec') !== 'false',
  cameraTicket: null,
  cameraTicketTimer: null,
  robotState: 'STOPPED',
  safetyState: 'CLEAR',
  personDetected: false,
  isEmergencyStopped: false,
  logs: [],
};

// Global Switch Tab function
window.switchTab = function(tabId) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
  });
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.toggle('active', pane.id === `pane-${tabId}`);
  });

  // Handle camera activation when switching to camera tab
  if (tabId === 'camera') {
    refreshCameraStream(true);
  } else if (tabId === 'control' && AppState.miniCameraEnabled) {
    refreshCameraStream(false);
  }
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  initUI();
  initSocket();
  initKeyListeners();
  initQrScanner();
  initAutoFetchLogs();

  // Attempt auto connect if credentials exist
  if (AppState.host && AppState.token) {
    connectRobot();
  } else {
    // If running directly on robot IP without token, prompt pair modal
    openPairModal();
  }
});

function initUI() {
  // Navigation Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab');
      window.switchTab(tabId);
    });
  });

  // Pair Modal Toggle
  document.getElementById('btnHeaderPair').addEventListener('click', openPairModal);
  document.getElementById('btnOpenPairModal').addEventListener('click', openPairModal);
  document.getElementById('btnClosePairModal').addEventListener('click', closePairModal);

  // Settings Save & Connect
  document.getElementById('btnSaveConnection').addEventListener('click', () => {
    const host = document.getElementById('settingHost').value.trim();
    const port = parseInt(document.getElementById('settingPort').value, 10) || 8765;
    const token = document.getElementById('settingToken').value.trim();

    AppState.host = host;
    AppState.port = port;
    AppState.token = token;

    localStorage.setItem('pi_robot_host', host);
    localStorage.setItem('pi_robot_port', port.toString());
    localStorage.setItem('pi_robot_token', token);

    connectRobot();
  });

  document.getElementById('btnUnpairRobot').addEventListener('click', unpairRobot);

  // Prefs
  const prefMiniCam = document.getElementById('prefMiniCamera');
  prefMiniCam.checked = AppState.miniCameraEnabled;
  prefMiniCam.addEventListener('change', e => {
    AppState.miniCameraEnabled = e.target.checked;
    localStorage.setItem('pi_robot_mini_cam', e.target.checked.toString());
    document.getElementById('controlStreamCard').style.display = e.target.checked ? 'flex' : 'none';
  });

  const prefAutoRec = document.getElementById('prefAutoReconnect');
  prefAutoRec.checked = AppState.autoReconnect;
  prefAutoRec.addEventListener('change', e => {
    AppState.autoReconnect = e.target.checked;
    localStorage.setItem('pi_robot_auto_rec', e.target.checked.toString());
  });

  // Throttle Slider & Speed Chips
  const slider = document.getElementById('throttleSlider');
  const badge = document.getElementById('throttleBadge');
  slider.addEventListener('input', e => {
    const val = parseInt(e.target.value, 10);
    badge.textContent = `${val}%`;
    AppState.currentSpeed = val / 100.0;
    RobotSocket.getInstance().updateDriveSpeed(AppState.currentSpeed);
    updateSpeedChipSelection(AppState.currentSpeed);
  });

  document.querySelectorAll('.speed-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const spd = parseFloat(chip.getAttribute('data-speed'));
      AppState.currentSpeed = spd;
      slider.value = Math.round(spd * 100);
      badge.textContent = `${slider.value}%`;
      RobotSocket.getInstance().updateDriveSpeed(spd);
      updateSpeedChipSelection(spd);
    });
  });

  // D-Pad Touch / Mouse Bindings
  bindDpadButton('btnDriveUp', 'forward');
  bindDpadButton('btnDriveDown', 'backward');
  bindDpadButton('btnDriveLeft', 'left');
  bindDpadButton('btnDriveRight', 'right');
  document.getElementById('btnDriveStop').addEventListener('click', () => {
    RobotSocket.getInstance().sendStop();
  });

  // Emergency Stop Buttons
  document.getElementById('btnEmergencyStop').addEventListener('click', triggerEStop);
  document.getElementById('btnControlEStop').addEventListener('click', triggerEStop);
  document.getElementById('btnBannerReset').addEventListener('click', triggerEStopReset);
  document.getElementById('btnControlReset').addEventListener('click', triggerEStopReset);

  // Motor Bench Test Buttons
  document.querySelectorAll('.btn-motor-test').forEach(btn => {
    const motorId = parseInt(btn.getAttribute('data-motor'), 10);
    const speed = parseFloat(btn.getAttribute('data-speed'));

    const startTest = (e) => {
      e.preventDefault();
      btn.classList.add('active');
      document.getElementById(`cardMotor${motorId}`).classList.add('active-motor');
      RobotSocket.getInstance().sendMotorTest(motorId, speed);
    };

    const endTest = (e) => {
      e.preventDefault();
      btn.classList.remove('active');
      document.getElementById(`cardMotor${motorId}`).classList.remove('active-motor');
      RobotSocket.getInstance().sendMotorTest(motorId, 0.0);
    };

    btn.addEventListener('mousedown', startTest);
    btn.addEventListener('mouseup', endTest);
    btn.addEventListener('mouseleave', endTest);
    btn.addEventListener('touchstart', startTest, { passive: false });
    btn.addEventListener('touchend', endTest, { passive: false });
  });

  document.getElementById('btnBenchStopAll').addEventListener('click', () => {
    RobotSocket.getInstance().sendStop();
  });

  // Log Actions
  document.getElementById('btnClearLogs').addEventListener('click', () => {
    document.getElementById('logTerminal').innerHTML = '';
  });
  document.getElementById('btnCopyLogs').addEventListener('click', () => {
    const text = Array.from(document.querySelectorAll('.log-line')).map(el => el.textContent).join('\n');
    navigator.clipboard.writeText(text).then(() => alert('Logs copied to clipboard'));
  });

  // Snapshot
  document.getElementById('btnCamSnapshot').addEventListener('click', async () => {
    if (!AppState.token) return;
    const url = `${RobotApi.getBaseUrl(AppState.host, AppState.port)}/api/v1/camera/snapshot?token=${AppState.token}`;
    window.open(url, '_blank');
  });

  // Prepopulate Settings Inputs
  document.getElementById('settingHost').value = AppState.host;
  document.getElementById('settingPort').value = AppState.port;
  document.getElementById('settingToken').value = AppState.token;
  document.getElementById('pairHostInput').value = AppState.host;
  document.getElementById('pairPortInput').value = AppState.port;
}

function updateSpeedChipSelection(speed) {
  document.querySelectorAll('.speed-chip').forEach(chip => {
    const val = parseFloat(chip.getAttribute('data-speed'));
    chip.classList.toggle('active', Math.abs(val - speed) < 0.03);
  });
}

function bindDpadButton(elementId, direction) {
  const btn = document.getElementById(elementId);
  if (!btn) return;

  const handleStart = (e) => {
    e.preventDefault();
    btn.classList.add('active');
    RobotSocket.getInstance().startDriveLoop(direction, AppState.currentSpeed);
  };

  const handleEnd = (e) => {
    e.preventDefault();
    btn.classList.remove('active');
    RobotSocket.getInstance().stopDriveLoop();
  };

  btn.addEventListener('mousedown', handleStart);
  btn.addEventListener('mouseup', handleEnd);
  btn.addEventListener('mouseleave', handleEnd);
  btn.addEventListener('touchstart', handleStart, { passive: false });
  btn.addEventListener('touchend', handleEnd, { passive: false });
  btn.addEventListener('touchcancel', handleEnd, { passive: false });
}

function initSocket() {
  const socket = RobotSocket.getInstance();

  socket.addStatusListener(status => {
    const pill = document.getElementById('connectionPill');
    const label = document.getElementById('connectionStatusText');
    label.textContent = status;

    pill.className = 'connection-pill';
    if (status === 'CONNECTED') {
      pill.classList.add('status-connected');
      logEvent('WebSocket connection authenticated and active.');
      fetchCameraTicketAndStream();
    } else if (status === 'CONNECTING' || status === 'AUTHENTICATING') {
      pill.classList.add('status-connecting');
    } else {
      pill.classList.add('status-disconnected');
      document.getElementById('pingValue').textContent = '-- ms';
    }
    updateSafetyBanner();
  });

  socket.addPingListener(ms => {
    document.getElementById('pingValue').textContent = `${ms} ms`;
  });

  socket.addTelemetryListener(telemetry => {
    handleTelemetryUpdate(telemetry);
  });

  socket.addSafetyEventListener(event => {
    if (event.event === 'person_detected') {
      AppState.personDetected = true;
      logEvent(`[SAFETY_EVENT] Person detected in center path (${Math.round((event.confidence || 0.85)*100)}%)`);
    } else if (event.event === 'person_clear') {
      AppState.personDetected = false;
      logEvent('[SAFETY_EVENT] Person cleared from safety zone.');
    } else if (event.event === 'emergency_stop') {
      AppState.isEmergencyStopped = true;
      logEvent('[CRITICAL] Emergency stop engaged!');
    }
    updateSafetyBanner();
  });

  socket.addAckListener(ack => {
    if (!ack.accepted && ack.reason) {
      logEvent(`[REJECTED] Drive command denied: ${ack.reason}`);
    }
  });
}

function handleTelemetryUpdate(telemetry) {
  AppState.robotState = telemetry.robotState;
  AppState.safetyState = telemetry.safetyState;
  AppState.personDetected = telemetry.personDetected;
  AppState.isEmergencyStopped = telemetry.safetyState === 'ERROR_STOP' || telemetry.robotState === 'SAFETY_STOP';

  // HUD Telemetry Updates
  document.getElementById('hudCamFps').textContent = telemetry.cameraFps ? telemetry.cameraFps.toFixed(1) : '0.0';
  document.getElementById('hudInfFps').textContent = telemetry.inferenceFps ? telemetry.inferenceFps.toFixed(1) : '0.0';
  document.getElementById('ctrlCamFps').textContent = `${telemetry.cameraFps ? telemetry.cameraFps.toFixed(1) : '0.0'} FPS`;
  document.getElementById('fullCamFpsBadge').textContent = `CAM: ${telemetry.cameraFps ? telemetry.cameraFps.toFixed(1) : '0.0'} FPS`;

  if (telemetry.cpuTemp) {
    const t = telemetry.cpuTemp.toFixed(1);
    document.getElementById('hudCpuTemp').textContent = `${t} °C`;
    document.getElementById('diagCpuTemp').textContent = `${t} °C`;
  }
  if (telemetry.cpuUsage !== undefined && telemetry.cpuUsage !== null) {
    const u = Math.round(telemetry.cpuUsage);
    document.getElementById('hudCpuLoad').textContent = `${u}%`;
    document.getElementById('diagCpuLoad').textContent = `${u}%`;
  }
  if (telemetry.memoryUsage !== undefined && telemetry.memoryUsage !== null) {
    const m = Math.round(telemetry.memoryUsage);
    document.getElementById('hudRamUsage').textContent = `${m}%`;
    document.getElementById('diagRamLoad').textContent = `${m}%`;
  }
  if (telemetry.uptime) {
    document.getElementById('diagUptime').textContent = formatUptime(telemetry.uptime);
  }

  // Safety Zone Status
  const szElem = document.getElementById('hudSafetyZone');
  if (telemetry.personDetected) {
    szElem.textContent = 'DETECTED';
    szElem.className = 'hud-metric-value text-red';
  } else {
    szElem.textContent = 'CLEAR';
    szElem.className = 'hud-metric-value text-green';
  }

  // Motor Output Bars
  const m1 = Math.round((telemetry.m1 || 0) * 100);
  const m2 = Math.round((telemetry.m2 || 0) * 100);
  const m3 = Math.round((telemetry.m3 || 0) * 100);
  const m4 = Math.round((telemetry.m4 || 0) * 100);

  document.getElementById('hudM1').textContent = `${m1}%`;
  document.getElementById('barM1').style.width = `${Math.abs(m1)}%`;
  document.getElementById('hudM2').textContent = `${m2}%`;
  document.getElementById('barM2').style.width = `${Math.abs(m2)}%`;
  document.getElementById('hudM3').textContent = `${m3}%`;
  document.getElementById('barM3').style.width = `${Math.abs(m3)}%`;
  document.getElementById('hudM4').textContent = `${m4}%`;
  document.getElementById('barM4').style.width = `${Math.abs(m4)}%`;

  document.getElementById('m1SpeedPill').textContent = `${m1}%`;
  document.getElementById('m2SpeedPill').textContent = `${m2}%`;
  document.getElementById('m3SpeedPill').textContent = `${m3}%`;
  document.getElementById('m4SpeedPill').textContent = `${m4}%`;

  // Overlay Warnings on Video
  const ctrlAlert = document.getElementById('ctrlStreamAlert');
  if (ctrlAlert) {
    ctrlAlert.classList.toggle('hidden', !telemetry.personDetected);
  }
  const fullAiBadge = document.getElementById('fullCamAiBadge');
  if (fullAiBadge) {
    if (telemetry.personDetected) {
      fullAiBadge.classList.remove('alert-hidden');
      fullAiBadge.textContent = `PERSON DETECTED (${Math.round((telemetry.personConfidence || 0.85) * 100)}%)`;
    } else {
      fullAiBadge.classList.add('alert-hidden');
    }
  }

  updateSafetyBanner();
}

function updateSafetyBanner() {
  const banner = document.getElementById('safetyBanner');
  const title = document.getElementById('safetyBannerTitle');
  const desc = document.getElementById('safetyBannerDesc');
  const resetBtn = document.getElementById('btnBannerReset');
  const ctrlResetBtn = document.getElementById('btnControlReset');
  const socketStatus = RobotSocket.getInstance().getStatus();

  if (AppState.isEmergencyStopped || AppState.safetyState === 'ERROR_STOP') {
    banner.className = 'safety-banner banner-danger';
    title.textContent = 'EMERGENCY STOP ACTIVE';
    desc.textContent = 'Hardware motor power latched off. Check surroundings and click Reset.';
    resetBtn.classList.remove('hidden');
    if (ctrlResetBtn) ctrlResetBtn.classList.remove('hidden');
    return;
  }

  if (resetBtn) resetBtn.classList.add('hidden');
  if (ctrlResetBtn) ctrlResetBtn.classList.add('hidden');

  if (AppState.personDetected || AppState.safetyState === 'PERSON_DETECTED' || AppState.robotState === 'PERSON_DETECTED') {
    banner.className = 'safety-banner banner-warning';
    title.textContent = 'PERSON DETECTED IN PATH';
    desc.textContent = 'Robot stopped automatically. Motion interlock active until path is clear.';
    return;
  }

  if (AppState.robotState === 'CAMERA_ERROR') {
    banner.className = 'safety-banner banner-danger';
    title.textContent = 'CSI CAMERA FEED ERROR';
    desc.textContent = 'Video stream lost. Hardware fail-safe stop engaged.';
    return;
  }

  if (socketStatus !== 'CONNECTED') {
    banner.className = 'safety-banner banner-warning';
    title.textContent = 'WEBSOCKET DISCONNECTED';
    desc.textContent = 'Fail-Safe stop active. Awaiting connection to Pi Robot...';
    return;
  }

  banner.className = 'safety-banner banner-clear';
  title.textContent = 'SAFETY SYSTEM OPERATIONAL (ALL CLEAR)';
  desc.textContent = 'Autonomous safety interlock active. No obstacles in stop zone.';
}

function triggerEStop() {
  RobotSocket.getInstance().sendEmergencyStop();
  RobotApi.emergencyStop(AppState.host, AppState.port);
}

function triggerEStopReset() {
  if (confirm('Confirm Safety Reset: Are you sure the area around the robot is clear of obstacles and hazards?')) {
    RobotSocket.getInstance().sendEmergencyReset();
    RobotApi.emergencyReset(AppState.host, AppState.port, AppState.token);
  }
}

// Keyboard shortcuts
function initKeyListeners() {
  let activeKey = null;

  window.addEventListener('keydown', e => {
    if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

    const key = e.key.toLowerCase();
    if (activeKey === key) return;

    if (key === 'w' || e.key === 'ArrowUp') {
      activeKey = key;
      document.getElementById('btnDriveUp').classList.add('active');
      RobotSocket.getInstance().startDriveLoop('forward', AppState.currentSpeed);
    } else if (key === 's' || e.key === 'ArrowDown') {
      activeKey = key;
      document.getElementById('btnDriveDown').classList.add('active');
      RobotSocket.getInstance().startDriveLoop('backward', AppState.currentSpeed);
    } else if (key === 'a' || e.key === 'ArrowLeft') {
      activeKey = key;
      document.getElementById('btnDriveLeft').classList.add('active');
      RobotSocket.getInstance().startDriveLoop('left', AppState.currentSpeed);
    } else if (key === 'd' || e.key === 'ArrowRight') {
      activeKey = key;
      document.getElementById('btnDriveRight').classList.add('active');
      RobotSocket.getInstance().startDriveLoop('right', AppState.currentSpeed);
    } else if (key === ' ' || key === 'x') {
      RobotSocket.getInstance().sendStop();
    } else if (key === 'e') {
      triggerEStop();
    } else if (key === 'r') {
      triggerEStopReset();
    } else if (['1', '2', '3', '4', '5'].includes(key)) {
      const speeds = [0.20, 0.35, 0.50, 0.75, 1.00];
      const selected = speeds[parseInt(key, 10) - 1];
      AppState.currentSpeed = selected;
      document.getElementById('throttleSlider').value = Math.round(selected * 100);
      document.getElementById('throttleBadge').textContent = `${Math.round(selected * 100)}%`;
      RobotSocket.getInstance().updateDriveSpeed(selected);
      updateSpeedChipSelection(selected);
    }
  });

  window.addEventListener('keyup', e => {
    if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;
    const key = e.key.toLowerCase();
    if (activeKey === key) {
      activeKey = null;
      document.getElementById('btnDriveUp').classList.remove('active');
      document.getElementById('btnDriveDown').classList.remove('active');
      document.getElementById('btnDriveLeft').classList.remove('active');
      document.getElementById('btnDriveRight').classList.remove('active');
      RobotSocket.getInstance().stopDriveLoop();
    }
  });
}

// Camera MJPEG ticket & stream management
async function fetchCameraTicketAndStream() {
  if (!AppState.token) return;
  const ticket = await RobotApi.getCameraTicket(AppState.host, AppState.port, AppState.token);
  if (ticket) {
    AppState.cameraTicket = ticket;
    refreshCameraStream(true);
  }

  if (AppState.cameraTicketTimer) clearInterval(AppState.cameraTicketTimer);
  AppState.cameraTicketTimer = setInterval(async () => {
    const t = await RobotApi.getCameraTicket(AppState.host, AppState.port, AppState.token);
    if (t) AppState.cameraTicket = t;
  }, 20000);
}

function refreshCameraStream(isFull) {
  const url = AppState.cameraTicket
    ? `${RobotApi.getBaseUrl(AppState.host, AppState.port)}/api/v1/camera/mjpeg?ticket=${AppState.cameraTicket}`
    : `${RobotApi.getBaseUrl(AppState.host, AppState.port)}/api/v1/camera/mjpeg?token=${AppState.token}`;

  const ctrlImg = document.getElementById('ctrlCameraImg');
  const fullImg = document.getElementById('fullCameraImg');

  if (ctrlImg) {
    ctrlImg.src = url;
    document.getElementById('ctrlStreamPlaceholder').classList.add('hidden');
  }
  if (fullImg) {
    fullImg.src = url;
    document.getElementById('fullStreamPlaceholder').classList.add('hidden');
  }
}

// Connect / Pair Logic
function connectRobot() {
  RobotSocket.getInstance().connect(AppState.host, AppState.port, AppState.token);
}

function openPairModal() {
  document.getElementById('pairModal').classList.remove('hidden');
}

function closePairModal() {
  document.getElementById('pairModal').classList.add('hidden');
  if (window.qrScannerInstance) {
    window.qrScannerInstance.stopCamera();
  }
}

function initQrScanner() {
  window.qrScannerInstance = new WebQrScanner(parsed => {
    document.getElementById('pairHostInput').value = parsed.host;
    document.getElementById('pairPortInput').value = parsed.port;
    document.getElementById('pairCodeInput').value = parsed.pairCode;
    submitPairing(parsed.host, parsed.port, parsed.pairCode);
  });

  document.getElementById('btnStartQrCamera').addEventListener('click', () => {
    window.qrScannerInstance.startCamera();
  });

  document.getElementById('btnSubmitPairPin').addEventListener('click', () => {
    const host = document.getElementById('pairHostInput').value.trim();
    const port = parseInt(document.getElementById('pairPortInput').value, 10) || 8765;
    const code = document.getElementById('pairCodeInput').value.trim().toUpperCase();
    submitPairing(host, port, code);
  });
}

async function submitPairing(host, port, code) {
  const errBox = document.getElementById('pairErrorMsg');
  errBox.classList.add('hidden');

  if (!host || !code) {
    errBox.textContent = 'Please enter both Robot IP and 6-character PIN code.';
    errBox.classList.remove('hidden');
    return;
  }

  try {
    const res = await RobotApi.pair(host, port, code);
    if (res.success && res.token) {
      AppState.host = host;
      AppState.port = port;
      AppState.token = res.token;
      AppState.robotId = res.robotId || 'RBT01';
      AppState.robotName = res.robotName || 'Pi Robot';

      localStorage.setItem('pi_robot_host', host);
      localStorage.setItem('pi_robot_port', port.toString());
      localStorage.setItem('pi_robot_token', res.token);
      localStorage.setItem('pi_robot_id', AppState.robotId);
      localStorage.setItem('pi_robot_name', AppState.robotName);

      document.getElementById('settingHost').value = host;
      document.getElementById('settingPort').value = port;
      document.getElementById('settingToken').value = res.token;

      closePairModal();
      connectRobot();
      logEvent(`Successfully paired with ${AppState.robotName} (${AppState.robotId})`);
    } else {
      errBox.textContent = res.message || 'Invalid or expired pairing code.';
      errBox.classList.remove('hidden');
    }
  } catch (e) {
    errBox.textContent = `Connection failed: ${e.message}`;
    errBox.classList.remove('hidden');
  }
}

async function unpairRobot() {
  if (confirm('Are you sure you want to forget this robot and revoke credentials?')) {
    if (AppState.host && AppState.token) {
      await RobotApi.revokeSession(AppState.host, AppState.port, AppState.token);
    }
    RobotSocket.getInstance().disconnect();
    localStorage.removeItem('pi_robot_token');
    AppState.token = '';
    document.getElementById('settingToken').value = '';
    openPairModal();
  }
}

function logEvent(msg) {
  const term = document.getElementById('logTerminal');
  if (!term) return;
  const timeStr = new Date().toLocaleTimeString();
  const line = document.createElement('div');
  line.className = 'log-line';
  line.textContent = `[${timeStr}] ${msg}`;
  term.appendChild(line);
  term.scrollTop = term.scrollHeight;
}

function initAutoFetchLogs() {
  setInterval(async () => {
    if (AppState.token && RobotSocket.getInstance().getStatus() === 'CONNECTED') {
      const serverLogs = await RobotApi.getRecentLogs(AppState.host, AppState.port, AppState.token);
      if (serverLogs && serverLogs.length > 0) {
        const term = document.getElementById('logTerminal');
        // Add only fresh logs if desired
      }
    }
  }, 5000);
}

function formatUptime(seconds) {
  if (!seconds || seconds <= 0) return '0s';
  const sec = Math.floor(seconds % 60);
  const min = Math.floor((seconds / 60) % 60);
  const hrs = Math.floor(seconds / 3600);
  if (hrs > 0) return `${hrs}h ${min}m`;
  if (min > 0) return `${min}m ${sec}s`;
  return `${sec}s`;
}
