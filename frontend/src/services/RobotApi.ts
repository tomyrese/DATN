import {
  PairResponse,
  HealthResponse,
  InfoResponse,
  PointOfInterest,
  DeliveryOrder,
  EscortTask,
  AskAssistantResponse,
} from '../types/protocol';

export class RobotApi {
  static getBaseUrl(host: string, port: number): string {
    if (!host) {
      return window.location.origin;
    }
    const cleanHost = host.trim();
    if (cleanHost.startsWith('http://') || cleanHost.startsWith('https://')) {
      return cleanHost.replace(/\/+$/, '');
    }
    const currentPort = port || 8765;
    return `http://${cleanHost}:${currentPort}`;
  }

  private static async fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs = 5000): Promise<Response> {
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

  static async pair(host: string, port: number, pairCode: string): Promise<PairResponse> {
    const url = `${this.getBaseUrl(host, port)}/api/v1/pair`;
    const res = await this.fetchWithTimeout(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pairCode: pairCode.trim().toUpperCase() }),
    });
    return res.json();
  }

  static async getHealth(host: string, port: number): Promise<HealthResponse> {
    const url = `${this.getBaseUrl(host, port)}/api/v1/health`;
    const res = await this.fetchWithTimeout(url);
    return res.json();
  }

  static async getInfo(host: string, port: number): Promise<InfoResponse> {
    const url = `${this.getBaseUrl(host, port)}/api/v1/info`;
    const res = await this.fetchWithTimeout(url);
    return res.json();
  }

  static async emergencyStop(host: string, port: number): Promise<boolean> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/emergency-stop`;
      const res = await this.fetchWithTimeout(url, { method: 'POST' });
      const data = await res.json();
      return !!data.success;
    } catch {
      return false;
    }
  }

  static async emergencyReset(
    host: string,
    port: number,
    token: string
  ): Promise<{ success: boolean; reason?: string }> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/emergency-reset`;
      const res = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      return res.json();
    } catch (e: any) {
      return { success: false, reason: e.message };
    }
  }

  static async getCameraTicket(host: string, port: number, token: string): Promise<string | null> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/camera/ticket`;
      const res = await this.fetchWithTimeout(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      return data.ticket || null;
    } catch {
      return null;
    }
  }

  static async getRecentLogs(host: string, port: number, token: string): Promise<string[]> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/logs/recent`;
      const res = await this.fetchWithTimeout(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      return data.logs || [];
    } catch {
      return [];
    }
  }

  static async revokeSession(host: string, port: number, token: string): Promise<boolean> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/session`;
      const res = await this.fetchWithTimeout(url, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      return res.ok;
    } catch {
      return false;
    }
  }

  // ==================== MALL & NAVIGATION SERVICES ====================

  static async getMallPois(host: string, port: number, includeStaff = false): Promise<PointOfInterest[]> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/pois?include_staff=${includeStaff}`;
      const res = await this.fetchWithTimeout(url);
      const data = await res.json();
      return data.pois || [];
    } catch (e) {
      console.warn('Failed to load mall POIs:', e);
      return [];
    }
  }

  static async getDeliveryOrders(host: string, port: number): Promise<DeliveryOrder[]> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/delivery/orders`;
      const res = await this.fetchWithTimeout(url);
      const data = await res.json();
      return data.orders || [];
    } catch (e) {
      console.warn('Failed to load delivery orders:', e);
      return [];
    }
  }

  static async createDeliveryOrder(
    host: string,
    port: number,
    token: string,
    order: { creatorName: string; pickupPoiId: string; dropoffPoiId: string; itemDescription: string }
  ): Promise<{ success: boolean; order?: DeliveryOrder; message?: string }> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/delivery/orders`;
      const res = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(order),
      });
      return res.json();
    } catch (e: any) {
      return { success: false, message: e.message };
    }
  }

  static async updateDeliveryOrderStatus(
    host: string,
    port: number,
    token: string,
    orderId: string,
    status: string,
    progress?: number
  ): Promise<boolean> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/delivery/orders/${orderId}`;
      const res = await this.fetchWithTimeout(url, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status, progress }),
      });
      const data = await res.json();
      return !!data.success;
    } catch {
      return false;
    }
  }

  static async requestEscort(
    host: string,
    port: number,
    targetPoiId: string
  ): Promise<{ success: boolean; task?: EscortTask; message?: string }> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/escort`;
      const res = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ targetPoiId }),
      });
      return res.json();
    } catch (e: any) {
      return { success: false, message: e.message };
    }
  }

  static async cancelEscort(host: string, port: number): Promise<boolean> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/escort`;
      const res = await this.fetchWithTimeout(url, { method: 'DELETE' });
      const data = await res.json();
      return !!data.success;
    } catch {
      return false;
    }
  }

  static async getEscortStatus(host: string, port: number): Promise<EscortTask | null> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/escort`;
      const res = await this.fetchWithTimeout(url);
      const data = await res.json();
      return data.task || null;
    } catch {
      return null;
    }
  }

  static async askAssistant(
    host: string,
    port: number,
    question: string
  ): Promise<AskAssistantResponse> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/ai/ask`;
      const res = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      return res.json();
    } catch (e: any) {
      return {
        answer: 'Xin lỗi, robot tạm thời mất kết nối với máy chủ AI. Quý khách vui lòng thử lại sau giây lát!',
      };
    }
  }
}
