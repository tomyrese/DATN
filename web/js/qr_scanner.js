/**
 * Pi Robot In-Browser QR Scanner (WebRTC + BarcodeDetector API)
 */
class WebQrScanner {
  constructor(onSuccessCallback) {
    this.onSuccess = onSuccessCallback;
    this.videoElem = document.getElementById('qrVideo');
    this.canvasElem = document.getElementById('qrCanvas');
    this.placeholderElem = document.getElementById('qrPlaceholder');
    this.stream = null;
    this.scanning = false;
    this.barcodeDetector = null;

    if ('BarcodeDetector' in window) {
      try {
        this.barcodeDetector = new BarcodeDetector({ formats: ['qr_code'] });
      } catch (e) {}
    }
  }

  static parsePayload(payload) {
    if (!payload || typeof payload !== 'string') return null;
    const parts = payload.trim().split('|');
    if (parts.length !== 4) return null;
    const [proto, host, portStr, code] = parts;
    if (proto !== 'P1') return null;
    const port = parseInt(portStr, 10);
    if (isNaN(port) || port < 1 || port > 65535) return null;
    const cleanCode = code.trim().toUpperCase();
    if (cleanCode.length < 4 || cleanCode.length > 12) return null;
    return { protocol: proto, host: host.trim(), port, pairCode: cleanCode };
  }

  async startCamera() {
    this.stopCamera();
    try {
      const constraints = {
        video: {
          facingMode: { ideal: 'environment' },
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
      };
      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.videoElem.srcObject = this.stream;
      this.videoElem.classList.remove('hidden');
      if (this.placeholderElem) this.placeholderElem.classList.add('hidden');
      await this.videoElem.play();
      this.scanning = true;
      this.scanLoop();
      return true;
    } catch (e) {
      alert(`Camera access error: ${e.message}. Please allow camera permissions or enter the 6-character PIN code manually.`);
      return false;
    }
  }

  stopCamera() {
    this.scanning = false;
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    if (this.videoElem) {
      this.videoElem.srcObject = null;
      this.videoElem.classList.add('hidden');
    }
    if (this.placeholderElem) {
      this.placeholderElem.classList.remove('hidden');
    }
  }

  async scanLoop() {
    if (!this.scanning || !this.videoElem) return;

    if (this.barcodeDetector && this.videoElem.readyState >= 2) {
      try {
        const barcodes = await this.barcodeDetector.detect(this.videoElem);
        if (barcodes.length > 0 && barcodes[0].rawValue) {
          const parsed = WebQrScanner.parsePayload(barcodes[0].rawValue);
          if (parsed) {
            this.stopCamera();
            if (this.onSuccess) this.onSuccess(parsed);
            return;
          }
        }
      } catch (err) {}
    }

    if (this.scanning) {
      requestAnimationFrame(this.scanLoop.bind(this));
    }
  }
}

window.WebQrScanner = WebQrScanner;
