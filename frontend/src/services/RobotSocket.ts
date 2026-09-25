import {
  TelemetryData,
  SafetyEventData,
  CommandAckData,
} from '../types/protocol';
import { ConnectionStatus } from '../types/robot';
import { RobotApi } from './RobotApi';

type TelemetryListener = (data: TelemetryData) => void;
type SafetyEventListener = (data: SafetyEventData) => void;
type StatusListener = (status: ConnectionStatus) => void;
type AckListener = (ack: CommandAckData) => void;
type PingListener = (latencyMs: number) => void;

export class RobotSocket {
  private static instance: RobotSocket | null = null;

  private ws: WebSocket | null = null;
  private host = '';
  private port = 8765;
  private token = '';
  private status: ConnectionStatus = 'DISCONNECTED';
  private seq = 0;

  private heartbeatTimer: any = null;
  private driveTimer: any = null;
  private reconnectTimer: any = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 8;

  private currentDriveDirection: 'forward' | 'backward' | 'left' | 'right' | null = null;
  private currentDriveSpeed = 0.35;

  private lastPingSent = 0;
  private latencyMs = 0;

  private telemetryListeners: Set<TelemetryListener> = new Set();
  private safetyEventListeners: Set<SafetyEventListener> = new Set();
  private statusListeners: Set<StatusListener> = new Set();
  private ackListeners: Set<AckListener> = new Set();
  private pingListeners: Set<PingListener> = new Set();

  public static getInstance(): RobotSocket {
    if (!RobotSocket.instance) {
      RobotSocket.instance = new RobotSocket();
    }
    return RobotSocket.instance;
  }

  public getStatus(): ConnectionStatus {
    return this.status;
  }

  public setStatus(newStatus: ConnectionStatus) {
    this.status = newStatus;
    this.statusListeners.forEach(listener => listener(newStatus));
  }

  public addTelemetryListener(cb: TelemetryListener) {
    this.telemetryListeners.add(cb);
    return () => this.telemetryListeners.delete(cb);
  }

  public addSafetyEventListener(cb: SafetyEventListener) {
    this.safetyEventListeners.add(cb);
    return () => this.safetyEventListeners.delete(cb);
  }

  public addStatusListener(cb: StatusListener) {
    this.statusListeners.add(cb);
    cb(this.status);
    return () => this.statusListeners.delete(cb);
  }

  public addAckListener(cb: AckListener) {
    this.ackListeners.add(cb);
    return () => this.ackListeners.delete(cb);
  }

  public addPingListener(cb: PingListener) {
    this.pingListeners.add(cb);
    return () => this.pingListeners.delete(cb);
  }

  public connect(host: string, port: number, token: string) {
    this.disconnect();

    this.host = host || window.location.hostname || 'localhost';
    this.port = port || 8765;
    this.token = token || '';
    this.setStatus('CONNECTING');

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let wsHost = this.host;
    if (wsHost.startsWith('http://')) wsHost = wsHost.replace('http://', '');
    if (wsHost.startsWith('https://')) wsHost = wsHost.replace('https://', '');
    wsHost = wsHost.replace(/\/+$/, '');

    let url: string;
    if (wsHost.includes(':')) {
      url = `${protocol}//${wsHost}/ws/v1/control?token=${encodeURIComponent(this.token)}`;
    } else if (wsHost.includes('trycloudflare.com') || wsHost.includes('.app') || wsHost.includes('.com') || wsHost.includes('.io') || wsHost.includes('.net')) {
      url = `${protocol}//${wsHost}/ws/v1/control?token=${encodeURIComponent(this.token)}`;
    } else {
      url = `${protocol}//${wsHost}:${this.port}/ws/v1/control?token=${encodeURIComponent(this.token)}`;
    }

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

  private handleOpen() {
    this.setStatus('AUTHENTICATING');
    this.reconnectAttempts = 0;

    this.send({
      type: 'hello',
      protocol: 1,
      client: 'web-react',
      appVersion: '1.0.0',
    });

    this.startHeartbeat();
  }

  private handleMessage(event: MessageEvent) {
    try {
      const data = JSON.parse(event.data);

      if (data.type === 'hello_ack') {
        this.setStatus('CONNECTED');
      } else if (data.type === 'heartbeat_ack') {
        if (this.lastPingSent > 0) {
          this.latencyMs = Math.max(1, Math.round(performance.now() - this.lastPingSent));
          this.pingListeners.forEach(l => l(this.latencyMs));
        }
      } else if (data.type === 'telemetry') {
        this.telemetryListeners.forEach(l => l(data as TelemetryData));
      } else if (data.type === 'safety_event') {
        this.safetyEventListeners.forEach(l => l(data as SafetyEventData));
      } else if (data.type === 'command_ack') {
        this.ackListeners.forEach(l => l(data as CommandAckData));
      } else if (data.type === 'error') {
        if (data.code === 'AUTH_INVALID') {
          this.setStatus('FAILED');
          this.disconnect();
        }
      }
    } catch (e) {}
  }

  private handleError() {
    this.stopDriveLoop();
    if (this.status !== 'FAILED') {
      this.setStatus('FAILED');
    }
  }

  private handleClose(event: CloseEvent) {
    this.stopHeartbeat();
    this.stopDriveLoop();

    if (event.code === 4003 || event.code === 4001) {
      this.setStatus('FAILED');
    } else {
      this.setStatus('DISCONNECTED');
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
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

  private startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.lastPingSent = performance.now();
        this.send({ type: 'heartbeat', timestamp: Date.now() / 1000.0 });
      }
    }, 400);
  }

  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  public send(payload: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(payload));
      } catch (e) {}
    }
  }

  public startDriveLoop(direction: 'forward' | 'backward' | 'left' | 'right', speed?: number) {
    this.currentDriveDirection = direction;
    if (speed !== undefined) {
      this.currentDriveSpeed = speed;
    }

    this.sendDriveMessage();

    if (this.driveTimer) {
      clearInterval(this.driveTimer);
    }

    this.driveTimer = setInterval(() => {
      this.sendDriveMessage();
    }, 100);
  }

  private sendDriveMessage() {
    if (!this.currentDriveDirection) {
      return;
    }
    this.seq++;
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.send({
        type: 'drive',
        direction: this.currentDriveDirection,
        speed: this.currentDriveSpeed,
        seq: this.seq,
      });
    } else {
      RobotApi.directDrive(this.host, this.port, this.currentDriveDirection, this.currentDriveSpeed);
    }
  }

  public updateDriveSpeed(speed: number) {
    this.currentDriveSpeed = speed;
    if (this.currentDriveDirection) {
      this.sendDriveMessage();
    }
  }

  public stopDriveLoop() {
    if (this.driveTimer) {
      clearInterval(this.driveTimer);
      this.driveTimer = null;
    }
    this.currentDriveDirection = null;
    this.sendStop();
  }

  public sendStop() {
    this.seq++;
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.send({
        type: 'stop',
        seq: this.seq,
      });
    } else {
      RobotApi.directDrive(this.host, this.port, 'stop', 0);
    }
  }

  public sendTankDrive(left: number, right: number) {
    this.seq++;
    this.send({
      type: 'tank_drive',
      left,
      right,
      seq: this.seq,
    });
  }

  public sendMotorTest(motor: number, speed: number) {
    this.seq++;
    this.send({
      type: 'motor_test',
      motor,
      speed,
      seq: this.seq,
    });
  }

  public sendEmergencyStop() {
    this.stopDriveLoop();
    this.send({
      type: 'emergency_stop',
    });
  }

  public sendEmergencyReset() {
    this.send({
      type: 'emergency_reset',
    });
  }

  public disconnect() {
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
