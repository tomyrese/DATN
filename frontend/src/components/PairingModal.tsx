import React, { useState, useRef, useEffect } from 'react';
import { RobotApi } from '../services/RobotApi';
import { RobotSocket } from '../services/RobotSocket';
import { StorageService } from '../services/StorageService';
import { updateGlobalState, useRobotStore } from '../store/useRobotStore';
import { Camera, X, QrCode } from 'lucide-react';

interface PairingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PairingModal: React.FC<PairingModalProps> = ({ isOpen, onClose }) => {
  const { pairedRobot } = useRobotStore();
  const [host, setHost] = useState(pairedRobot?.host || window.location.hostname || 'localhost');
  const [port, setPort] = useState(pairedRobot?.port ? pairedRobot.port.toString() : '8765');
  const [pinCode, setPinCode] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    if (pairedRobot) {
      setHost(pairedRobot.host);
      setPort(pairedRobot.port.toString());
    }
  }, [pairedRobot]);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

  const startCamera = async () => {
    stopCamera();
    setErrorMsg('');
    try {
      const constraints = {
        video: { facingMode: { ideal: 'environment' } },
      };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setCameraActive(true);
      scanQrLoop();
    } catch (err: any) {
      setErrorMsg(`Camera error: ${err.message}. Please allow camera permissions or enter PIN manually.`);
    }
  };

  const scanQrLoop = async () => {
    if (!streamRef.current || !videoRef.current) return;

    if ('BarcodeDetector' in window) {
      try {
        const detector = new (window as any).BarcodeDetector({ formats: ['qr_code'] });
        const barcodes = await detector.detect(videoRef.current);
        if (barcodes.length > 0 && barcodes[0].rawValue) {
          const raw = barcodes[0].rawValue;
          const parts = raw.split('|');
          if (parts.length === 4 && parts[0] === 'P1') {
            const [, qHost, qPort, qCode] = parts;
            stopCamera();
            setHost(qHost);
            setPort(qPort);
            setPinCode(qCode);
            submitPair(qHost, parseInt(qPort, 10), qCode);
            return;
          }
        }
      } catch (e) {}
    }

    if (streamRef.current) {
      requestAnimationFrame(scanQrLoop);
    }
  };

  const submitPair = async (targetHost: string, targetPort: number, targetCode: string) => {
    if (!targetHost || !targetCode) {
      setErrorMsg('Please enter both Robot IP and PIN code.');
      return;
    }

    setLoading(true);
    setErrorMsg('');

    try {
      const res = await RobotApi.pair(targetHost, targetPort, targetCode);
      if (res.success && res.token) {
        const info = {
          robotId: res.robotId,
          robotName: res.robotName,
          host: targetHost,
          port: targetPort,
          token: res.token,
          lastConnected: Date.now(),
        };

        StorageService.savePairedRobot(info);
        updateGlobalState(() => ({ pairedRobot: info }));

        RobotSocket.getInstance().connect(targetHost, targetPort, res.token);
        stopCamera();
        onClose();
      } else {
        setErrorMsg(res.message || 'Invalid or expired pairing code.');
      }
    } catch (err: any) {
      setErrorMsg(`Connection failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitManual = (e: React.FormEvent) => {
    e.preventDefault();
    submitPair(host.trim(), parseInt(port, 10) || 8765, pinCode.trim());
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <div className="modal-header">
          <h3 className="modal-title">SECURE ROBOT PAIRING</h3>
          <button className="btn-close-modal" onClick={() => { stopCamera(); onClose(); }}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <p className="modal-desc">
            Scan the dynamic QR code on the Robot's 1.3" OLED screen or enter the 6-character PIN code.
          </p>

          <div className="qr-scanner-box">
            <video
              ref={videoRef}
              playsInline
              className={`qr-video ${cameraActive ? '' : 'hidden'}`}
            />
            {!cameraActive && (
              <div className="qr-placeholder">
                <QrCode size={48} color="#00E5FF" />
                <span>Click Start Camera to Scan OLED QR</span>
              </div>
            )}
            <button className="btn-primary btn-block" onClick={cameraActive ? stopCamera : startCamera}>
              <Camera size={16} style={{ display: 'inline', marginRight: 6 }} />
              {cameraActive ? 'STOP CAMERA' : 'START CAMERA SCANNER'}
            </button>
          </div>

          <div className="modal-divider"><span>OR ENTER 6-CHAR PIN</span></div>

          <form onSubmit={handleSubmitManual}>
            <div className="form-row">
              <div className="form-col-2">
                <label className="setting-label">Robot Host / IP</label>
                <input
                  type="text"
                  className="input-text"
                  value={host}
                  onChange={(e) => setHost(e.target.value)}
                  placeholder="192.168.1.50 or localhost"
                />
              </div>
              <div className="form-col-1">
                <label className="setting-label">Port</label>
                <input
                  type="number"
                  className="input-text"
                  value={port}
                  onChange={(e) => setPort(e.target.value)}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-col-full">
                <label className="setting-label">6-Character OLED PIN Code</label>
                <input
                  type="text"
                  className="input-text text-uppercase pin-input"
                  value={pinCode}
                  onChange={(e) => setPinCode(e.target.value.toUpperCase())}
                  placeholder="e.g. 7A9K3F"
                  maxLength={12}
                />
              </div>
            </div>

            {errorMsg && <div className="pair-error-msg">{errorMsg}</div>}

            <button type="submit" className="btn-primary btn-block" disabled={loading} style={{ marginTop: 8 }}>
              {loading ? 'AUTHENTICATING...' : 'PAIR WITH ROBOT'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
