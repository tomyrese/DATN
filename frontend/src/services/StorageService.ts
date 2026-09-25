import { PairedRobotInfo, AppSettings, UserRole } from '../types/robot';

const KEY_PAIRED_ROBOT = 'pi_robot_paired_info';
const KEY_SETTINGS = 'pi_robot_settings';
const KEY_USER_ROLE = 'pi_robot_user_role';

const DEFAULT_SETTINGS: AppSettings = {
  defaultSpeed: 0.35,
  enableCameraPreview: true,
  autoReconnect: true,
  mjpegQuality: 70,
  remoteTunnelUrl: '',
};

export class StorageService {
  static savePairedRobot(info: PairedRobotInfo): void {
    try {
      localStorage.setItem(KEY_PAIRED_ROBOT, JSON.stringify(info));
    } catch (e) {}
  }

  static getPairedRobot(): PairedRobotInfo | null {
    try {
      const json = localStorage.getItem(KEY_PAIRED_ROBOT);
      if (!json) return null;
      return JSON.parse(json) as PairedRobotInfo;
    } catch (e) {
      return null;
    }
  }

  static clearPairedRobot(): void {
    try {
      localStorage.removeItem(KEY_PAIRED_ROBOT);
    } catch (e) {}
  }

  static saveSettings(settings: Partial<AppSettings>): void {
    try {
      const current = this.getSettings();
      const updated = { ...current, ...settings };
      localStorage.setItem(KEY_SETTINGS, JSON.stringify(updated));
    } catch (e) {}
  }

  static getSettings(): AppSettings {
    try {
      const json = localStorage.getItem(KEY_SETTINGS);
      if (!json) return DEFAULT_SETTINGS;
      return { ...DEFAULT_SETTINGS, ...JSON.parse(json) };
    } catch (e) {
      return DEFAULT_SETTINGS;
    }
  }

  static saveUserRole(role: UserRole): void {
    try {
      localStorage.setItem(KEY_USER_ROLE, role);
    } catch (e) {}
  }

  static getUserRole(): UserRole {
    try {
      const role = localStorage.getItem(KEY_USER_ROLE);
      return role === 'staff' ? 'staff' : 'customer';
    } catch (e) {
      return 'customer';
    }
  }
}
