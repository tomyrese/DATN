import {
  PairResponse,
  HealthResponse,
  InfoResponse,
  PointOfInterest,
  DeliveryOrder,
  EscortTask,
  AskAssistantResponse,
  Promotion,
  AdminUser,
  AuditLog,
  MapGraphData,
} from '../types/protocol';
import { AuthUser } from '../types/robot';

export class RobotApi {
  static getBaseUrl(host?: string, port?: number): string {
    if (host && host.trim()) {
      let cleanHost = host.trim();
      if (cleanHost.startsWith('http://') || cleanHost.startsWith('https://')) {
        return cleanHost.replace(/\/+$/, '');
      }
      if (cleanHost.includes(':')) {
        return `http://${cleanHost}`;
      }
      if (cleanHost.includes('trycloudflare.com') || cleanHost.includes('.app') || cleanHost.includes('.com') || cleanHost.includes('.io') || cleanHost.includes('.net')) {
        return `https://${cleanHost}`;
      }
      const currentPort = port || 8765;
      return `http://${cleanHost}:${currentPort}`;
    }

    if (typeof window !== 'undefined') {
      if (window.location.port === '3000' || window.location.port === '5173') {
        return `http://${window.location.hostname || 'localhost'}:8765`;
      }
      return window.location.origin;
    }
    return 'http://localhost:8765';
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

  static async directDrive(host: string, port: number, direction: string, speed: number = 0.35, token?: string): Promise<boolean> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/control/drive`;
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const res = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers,
        body: JSON.stringify({ direction, speed }),
      }, 1500);
      return res.ok;
    } catch {
      return false;
    }
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
    order: { creatorName: string; pickupPoiId: string; dropoffPoiId: string; itemDescription: string },
    token?: string
  ): Promise<{ success: boolean; order?: DeliveryOrder; message?: string }> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/delivery/orders`;
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;
      const res = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers,
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
    orderId: string,
    status: string,
    progress?: number,
    token?: string
  ): Promise<boolean> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/delivery/orders/${orderId}`;
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;
      const res = await this.fetchWithTimeout(url, {
        method: 'PATCH',
        headers,
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

  // ==================== AUTHENTICATION & SESSIONS ====================

  static async login(
    host: string,
    port: number,
    creds: { username: string; password: string }
  ): Promise<{ success: boolean; token?: string; user?: AuthUser; message?: string }> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/auth/login`;
      const res = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(creds),
      });
      const data = await res.json();
      if (data.success && data.token && data.user) {
        return {
          success: true,
          token: data.token,
          user: {
            id: data.user.id,
            username: data.user.username,
            fullName: data.user.fullName || data.user.username,
            role: data.user.role,
            assignedStoreIds: data.user.assignedStoreIds || [],
            token: data.token,
          },
          message: data.message,
        };
      }
      return { success: false, message: data.message || 'Đăng nhập không thành công' };
    } catch (e: any) {
      return { success: false, message: e.message || 'Lỗi kết nối máy chủ' };
    }
  }

  static async logout(host: string, port: number, token: string): Promise<boolean> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/auth/logout`;
      const res = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      return res.ok;
    } catch {
      return false;
    }
  }

  static async getMe(host: string, port: number, token?: string): Promise<any> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/auth/me`;
      const headers: Record<string, string> = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;
      const res = await this.fetchWithTimeout(url, { headers });
      return res.json();
    } catch {
      return { authenticated: false, role: 'guest' };
    }
  }

  // ==================== PROMOTIONS (STAFF & ADMIN) ====================

  static async getPromotions(host: string, port: number, storeId?: string): Promise<Promotion[]> {
    try {
      const q = storeId ? `?store_id=${encodeURIComponent(storeId)}` : '';
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/promotions${q}`;
      const res = await this.fetchWithTimeout(url);
      const data = await res.json();
      return data.promotions || [];
    } catch {
      return [];
    }
  }

  static async createPromotion(
    host: string,
    port: number,
    promo: {
      storeId: string;
      title: string;
      description: string;
      discountPercent: number;
      promoCode?: string;
      startTime?: string;
      endTime?: string;
    },
    token: string
  ): Promise<{ success: boolean; promotion?: Promotion; message?: string }> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/promotions`;
      const res = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(promo),
      });
      return res.json();
    } catch (e: any) {
      return { success: false, message: e.message };
    }
  }

  static async deletePromotion(host: string, port: number, promoId: string, token: string): Promise<boolean> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/promotions/${promoId}`;
      const res = await this.fetchWithTimeout(url, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      return !!data.success;
    } catch {
      return false;
    }
  }

  // ==================== MAP GRAPH & PATROL ====================

  static async getMapGraph(host: string, port: number): Promise<MapGraphData | null> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/map/graph`;
      const res = await this.fetchWithTimeout(url);
      const data = await res.json();
      return data.graph || null;
    } catch {
      return null;
    }
  }

  static async getPatrolStatus(host: string, port: number): Promise<any> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/patrol`;
      const res = await this.fetchWithTimeout(url);
      return res.json();
    } catch {
      return null;
    }
  }

  static async triggerPatrol(host: string, port: number, token: string): Promise<{ success: boolean; message?: string }> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/mall/patrol/trigger`;
      const res = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      return res.json();
    } catch (e: any) {
      return { success: false, message: e.message };
    }
  }

  // ==================== ADMIN API ====================

  static async getAdminUsers(host: string, port: number, token: string): Promise<AdminUser[]> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/admin/users`;
      const res = await this.fetchWithTimeout(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      return data.users || [];
    } catch {
      return [];
    }
  }

  static async createAdminUser(
    host: string,
    port: number,
    userData: { username: string; password: string; fullName: string; role: string; assignedStoreIds?: string[] },
    token: string
  ): Promise<{ success: boolean; message?: string }> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/admin/users`;
      const res = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(userData),
      });
      return res.json();
    } catch (e: any) {
      return { success: false, message: e.message };
    }
  }

  static async toggleUserStatus(host: string, port: number, userId: string, isActive: boolean, token: string): Promise<boolean> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/admin/users/${userId}/status`;
      const res = await this.fetchWithTimeout(url, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ isActive }),
      });
      const data = await res.json();
      return !!data.success;
    } catch {
      return false;
    }
  }

  static async getAuditLogs(host: string, port: number, token: string): Promise<AuditLog[]> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/admin/audit-logs`;
      const res = await this.fetchWithTimeout(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      return data.logs || [];
    } catch {
      return [];
    }
  }

  static async backupDatabase(host: string, port: number, token: string): Promise<{ success: boolean; backupPath?: string }> {
    try {
      const url = `${this.getBaseUrl(host, port)}/api/v1/admin/backup-db`;
      const res = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      return res.json();
    } catch {
      return { success: false };
    }
  }
}
