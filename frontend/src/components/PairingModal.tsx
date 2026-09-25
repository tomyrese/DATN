import React, { useState, useRef, useEffect } from 'react';
import { RobotApi } from '../services/RobotApi';
import { RobotSocket } from '../services/RobotSocket';
import { StorageService } from '../services/StorageService';
import { updateGlobalState, useRobotStore } from '../store/useRobotStore';
import { Camera, X, QrCode, Globe, ShieldCheck, AlertCircle } from 'lucide-react';

interface PairingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PairingModal: React.FC<PairingModalProps> = ({ isOpen, onClose }) => {
  const { pairedRobot } = useRobotStore();

  const getInitialHost = () => {
    if (pairedRobot?.host) return pairedRobot.host;
    if (window.location.hostname !== 'localhost' && !window.location.hostname.includes('127.0.0.1')) {
      return ''; // Don't auto-fill vercel.app
    }
    return 'localhost';
  };

  const [host, setHost] = useState(getInitialHost());
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
      setErrorMsg(`Không thể mở camera: ${err.message}. Vui lòng cấp quyền hoặc nhập mã PIN thủ công.`);
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
    let cleanHost = targetHost.trim();
    if (!cleanHost || !targetCode) {
      setErrorMsg('Vui lòng nhập địa chỉ IP/Tunnel Robot và mã PIN OLED 6 ký tự.');
      return;
    }

    // Handle tunnel URLs (e.g. https://xxx.trycloudflare.com)
    let effectivePort = targetPort;
    if (cleanHost.startsWith('http://') || cleanHost.startsWith('https://')) {
      const url = new URL(cleanHost);
      cleanHost = url.hostname;
      effectivePort = url.protocol === 'https:' ? 443 : (parseInt(url.port, 10) || 80);
    }

    setLoading(true);
    setErrorMsg('');

    try {
      const res = await RobotApi.pair(cleanHost, effectivePort, targetCode);
      if (res.success && res.token) {
        const info = {
          robotId: res.robotId,
          robotName: res.robotName,
          host: cleanHost,
          port: effectivePort,
          token: res.token,
          lastConnected: Date.now(),
        };

        StorageService.savePairedRobot(info);
        StorageService.saveUserRole('staff');

        updateGlobalState(() => ({
          pairedRobot: info,
          userRole: 'staff',
        }));

        RobotSocket.getInstance().connect(cleanHost, effectivePort, res.token);
        stopCamera();
        onClose();
      } else {
        setErrorMsg(res.message || 'Mã PIN không đúng hoặc đã hết hạn.');
      }
    } catch (err: any) {
      setErrorMsg(`Không thể kết nối đến Robot: ${err.message}. Kiểm tra lại địa chỉ Tunnel URL / IP.`);
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
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <ShieldCheck size={20} color="#2563EB" />
            <h3 className="modal-title">XÁC THỰC NHÂN VIÊN & KẾT NỐI ROBOT</h3>
          </div>
          <button className="btn-close-modal" onClick={() => { stopCamera(); onClose(); }}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <div style={{ background: '#EFF6FF', border: '1px solid #BFDBFE', borderRadius: 8, padding: '10px 14px', fontSize: '0.8rem', color: '#1E40AF', marginBottom: 16, lineHeight: 1.5 }}>
            💡 <strong>Hướng dẫn kết nối từ xa:</strong> Nhập đường link Cloudflare Tunnel từ robot (ví dụ: <code style={{ color: '#2563EB', fontWeight: 700 }}>https://xxx.trycloudflare.com</code>) hoặc IP mạng nội bộ (192.168.x.x) kèm mã PIN hiển thị trên màn hình OLED của Robot.
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, padding: 12, background: '#F8FAFC', borderRadius: 12, border: '1px solid #E2E8F0', marginBottom: 16 }}>
            <video
              ref={videoRef}
              playsInline
              style={{ width: '100%', maxHeight: 180, objectFit: 'cover', borderRadius: 8, display: cameraActive ? 'block' : 'none' }}
            />
            {!cameraActive && (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, color: '#64748B', fontSize: '0.8rem', padding: '10px 0' }}>
                <QrCode size={36} color="#2563EB" />
                <span>Quét mã QR trên màn hình OLED của Robot</span>
              </div>
            )}
            <button className="btn-primary btn-block" type="button" onClick={cameraActive ? stopCamera : startCamera}>
              <Camera size={16} style={{ display: 'inline', marginRight: 6 }} />
              {cameraActive ? 'DỪNG QUÉT CAMERA' : 'BẬT CAMERA QUÉT MÃ QR OLED'}
            </button>
          </div>

          <div className="modal-divider"><span>HOẶC NHẬP MÃ PIN THỦ CÔNG</span></div>

          <form onSubmit={handleSubmitManual}>
            <div className="form-row">
              <div className="form-col-2">
                <label className="setting-label">Địa chỉ Robot (Tunnel URL hoặc IP)</label>
                <input
                  type="text"
                  className="input-text"
                  value={host}
                  onChange={(e) => setHost(e.target.value)}
                  placeholder="e.g. xxx.trycloudflare.com hoặc 192.168.1.50"
                  required
                />
              </div>
              <div className="form-col-1">
                <label className="setting-label">Port</label>
                <input
                  type="number"
                  className="input-text"
                  value={port}
                  onChange={(e) => setPort(e.target.value)}
                  placeholder="8765"
                />
              </div>
            </div>

            <div style={{ marginBottom: 14 }}>
              <label className="setting-label">Mã PIN OLED 6 Ký Tự</label>
              <input
                type="text"
                className="input-text pin-input"
                value={pinCode}
                onChange={(e) => setPinCode(e.target.value.toUpperCase())}
                placeholder="VD: 7A9K3F"
                maxLength={12}
                style={{ textAlign: 'center', fontSize: '1.2rem', letterSpacing: 4, fontWeight: 900, color: '#2563EB' }}
                required
              />
            </div>

            {errorMsg && (
              <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', color: '#DC2626', padding: '10px 14px', borderRadius: 8, fontSize: '0.8rem', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                <AlertCircle size={16} />
                <span>{errorMsg}</span>
              </div>
            )}

            <button type="submit" className="btn-primary btn-block" disabled={loading} style={{ padding: 13, fontSize: '0.9rem' }}>
              {loading ? 'ĐANG KẾT NỐI & XÁC THỰC...' : 'XÁC THỰC & ĐĂNG NHẬP NHÂN VIÊN'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
