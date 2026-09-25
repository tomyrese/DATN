/**
 * Pi Robot WebSocket Manager (Real-Time Bidirectional Streaming)
 */
class RobotSocket {
  constructor() {
    this.ws = null;
    this.host = '';
    this.port = 8765;
    this.token = '';
    this.status = 'DISCONNECTED';
    this.seq = 0;

    this.heartbeatTimer = null;
    this.driveTimer = null;
    this.reconnectTimer = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 8;

    this.currentDriveDirection = null;
    this.currentDriveSpeed = 0.35;

    this.lastPingSent = 0;
    this.latencyMs = 0;

    this.telemetryListeners = new Set();
    this.safetyEventListeners = new Set();
    this.statusListeners = new Set();
    this.ackListeners = new Set();
    this.pingListeners = new Set();
  }

  static getInstance() {
    if (!window._robotSocketInstance) {
      window._robotSocketInstance = new RobotSocket();
    }
    return window._robotSocketInstance;
  }

  getStatus() {
    return this.status;
  }

  setStatus(newStatus) {
    this.status = newStatus;
    this.statusListeners.forEach(fn => {
      try { fn(newStatus); } catch (e) {}
    });
  }

  addTelemetryListener(cb) {
    this.telemetryListeners.add(cb);
    return () => this.telemetryListeners.delete(cb);
  }

  addSafetyEventListener(cb) {
    this.safetyEventListeners.add(cb);
    return () => this.safetyEventListeners.delete(cb);
  }

  addStatusListener(cb) {
    this.statusListeners.add(cb);
    cb(this.status);
    return () => this.statusListeners.delete(cb);
  }

  addAckListener(cb) {
    this.ackListeners.add(cb);
    return () => this.ackListeners.delete(cb);
  }

  addPingListener(cb) {
    this.pingListeners.add(cb);
    return () => this.pingListeners.delete(cb);
  }

  connect(host, port, token) {
    this.disconnect();

    this.host = host || window.location.hostname || 'localhost';
    this.port = port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    this.token = token || '';
    this.setStatus('CONNECTING');

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${protocol}//${this.host}:${this.port}/ws/v1/control?token=${encodeURIComponent(this.token)}`;

    try {
      this.ws = new WebSocket(url);
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
    } catch (e) {
      this.setStatus('FAILED');
      this.scheduleReconnect();
    }
  }

  handleOpen() {
    this.setStatus('AUTHENTICATING');
    this.reconnectAttempts = 0;

    // Send Handshake
    this.send({
      type: 'hello',
      protocol: 1,
      client: 'web',
      appVersion: '1.0.0',
    });

    this.startHeartbeat();
  }

  handleMessage(event) {
    try {
      const data = JSON.parse(event.data);

      if (data.type === 'hello_ack') {
        this.setStatus('CONNECTED');
      } else if (data.type === 'heartbeat_ack') {
        if (this.lastPingSent > 0) {
          this.latencyMs = Math.max(1, Math.round((performance.now() - this.lastPingSent)));
          this.pingListeners.forEach(fn => {
            try { fn(this.latencyMs); } catch (e) {}
          });
        }
      } else if (data.type === 'telemetry') {
        this.telemetryListeners.forEach(fn => {
          try { fn(data); } catch (e) {}
        });
      } else if (data.type === 'safety_event') {
        this.safetyEventListeners.forEach(fn => {
          try { fn(data); } catch (e) {}
        });
      } else if (data.type === 'command_ack') {
        this.ackListeners.forEach(fn => {
          try { fn(data); } catch (e) {}
        });
      } else if (data.type === 'error') {
        if (data.code === 'AUTH_INVALID') {
          this.setStatus('FAILED');
          this.disconnect();
        }
      }
    } catch (e) {}
  }

  handleError() {
    this.stopDriveLoop();
    if (this.status !== 'FAILED') {
      this.setStatus('FAILED');
    }
  }

  handleClose(event) {
    this.stopHeartbeat();
    this.stopDriveLoop();

    if (event && (event.code === 4003 || event.code === 4001)) {
      this.setStatus('FAILED');
    } else {
      this.setStatus('DISCONNECTED');
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      return;
    }

    const delay = Math.min(6000, 1000 * Math.pow(1.5, this.reconnectAttempts));
    this.reconnectAttempts++;

    this.reconnectTimer = setTimeout(() => {
      if (this.status === 'DISCONNECTED' || this.status === 'FAILED') {
        this.setStatus('CONNECTING');
        this.connect(this.host, this.port, this.token);
      }
    }, delay);
  }

  startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.lastPingSent = performance.now();
        this.send({ type: 'heartbeat', timestamp: Date.now() / 1000.0 });
      }
    }, 400);
  }

  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  send(payload) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(payload));
      } catch (e) {}
    }
  }

  startDriveLoop(direction, speed) {
    this.currentDriveDirection = direction;
    this.currentDriveSpeed = speed !== undefined ? speed : this.currentDriveSpeed;

    this.sendDriveMessage();

    if (this.driveTimer) {
      clearInterval(this.driveTimer);
    }

    this.driveTimer = setInterval(() => {
      this.sendDriveMessage();
    }, 100);
  }

  sendDriveMessage() {
    if (!this.currentDriveDirection) return;
    this.seq++;
    this.send({
      type: 'drive',
      direction: this.currentDriveDirection,
      speed: this.currentDriveSpeed,
      seq: this.seq,
    });
  }

  updateDriveSpeed(speed) {
    this.currentDriveSpeed = speed;
    if (this.currentDriveDirection) {
      this.sendDriveMessage();
    }
  }

  stopDriveLoop() {
    if (this.driveTimer) {
      clearInterval(this.driveTimer);
      this.driveTimer = null;
    }
    this.currentDriveDirection = null;
    this.sendStop();
  }

  sendStop() {
    this.seq++;
    this.send({
      type: 'stop',
      seq: this.seq,
    });
  }

  sendTankDrive(left, right) {
    this.seq++;
    this.send({
      type: 'tank_drive',
      left,
      right,
      seq: this.seq,
    });
  }

  sendMotorTest(motor, speed) {
    this.seq++;
    this.send({
      type: 'motor_test',
      motor,
      speed,
      seq: this.seq,
    });
  }

  sendEmergencyStop() {
    this.stopDriveLoop();
    this.send({
      type: 'emergency_stop',
    });
  }

  sendEmergencyReset() {
    this.send({
      type: 'emergency_reset',
    });
  }

  disconnect() {
    this.stopHeartbeat();
    this.stopDriveLoop();

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      try {
        this.ws.onopen = null;
        this.ws.onmessage = null;
        this.ws.onerror = null;
        this.ws.onclose = null;
        this.ws.close();
      } catch (e) {}
      this.ws = null;
    }

    this.setStatus('DISCONNECTED');
  }
}

window.RobotSocket = RobotSocket;
