/**
 * Pi Robot REST API Client
 */
class RobotApi {
  static getBaseUrl(host, port) {
    if (!host) {
      return window.location.origin;
    }
    const currentPort = port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    return `http://${host}:${currentPort}`;
  }

  static async fetchWithTimeout(url, options = {}, timeoutMs = 4000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, { ...options, signal: controller.signal });
      clearTimeout(timer);
      return response;
    } catch (e) {
      clearTimeout(timer);
      throw e;
    }
  }

  static async pair(host, port, pairCode) {
    const url = `${this.getBaseUrl(host, port)}/api/v1/pair`;
    const res = await this.fetchWithTimeout(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pairCode: pairCode.trim().toUpperCase() }),
    });
    return res.json();
  }

  static async getHealth(host, port) {
    const url = `${this.getBaseUrl(host, port)}/api/v1/health`;
    const res = await this.fetchWithTimeout(url);
    return res.json();
  }

  static async getInfo(host, port) {
    const url = `${this.getBaseUrl(host, port)}/api/v1/info`;
    const res = await this.fetchWithTimeout(url);
    return res.json();
  }

  static async getPublicConfig(host, port) {
    const url = `${this.getBaseUrl(host, port)}/api/v1/config/public`;
    const res = await this.fetchWithTimeout(url);
    return res.json();
  }

  static async emergencyStop(host, port) {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/emergency-stop`;
      const res = await this.fetchWithTimeout(url, { method: 'POST' });
      return res.json();
    } catch (e) {
      return { success: false, error: e.message };
    }
  }

  static async emergencyReset(host, port, token) {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/emergency-reset`;
      const res = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      return res.json();
    } catch (e) {
      return { success: false, reason: e.message };
    }
  }

  static async getCameraTicket(host, port, token) {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/camera/ticket`;
      const res = await this.fetchWithTimeout(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      return data.ticket || null;
    } catch (e) {
      return null;
    }
  }

  static async getRecentLogs(host, port, token) {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/logs/recent`;
      const res = await this.fetchWithTimeout(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      return data.logs || [];
    } catch (e) {
      return [];
    }
  }

  static async revokeSession(host, port, token) {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/session`;
      const res = await this.fetchWithTimeout(url, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      return res.ok;
    } catch (e) {
      return false;
    }
  }
}

window.RobotApi = RobotApi;
