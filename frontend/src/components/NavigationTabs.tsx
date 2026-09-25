import React from 'react';
import { useRobotStore } from '../store/useRobotStore';
import {
  Map,
  Bot,
  Store,
  Package,
  LayoutDashboard,
  Compass,
  Video,
  Activity,
  Wrench,
  Settings,
} from 'lucide-react';

export type TabType =
  | 'mall-map'
  | 'mall-assistant'
  | 'mall-directory'
  | 'delivery-orders'
  | 'dashboard'
  | 'control'
  | 'camera'
  | 'diagnostics'
  | 'motor-test'
  | 'settings';

interface NavigationTabsProps {
  activeTab: TabType;
  onSelectTab: (tab: TabType) => void;
}

export const NavigationTabs: React.FC<NavigationTabsProps> = ({ activeTab, onSelectTab }) => {
  const { userRole } = useRobotStore();

  const customerTabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: 'mall-map', label: 'Bản Đồ TTTM', icon: <Map size={18} /> },
    { id: 'mall-assistant', label: 'Trợ Lý AI', icon: <Bot size={18} /> },
    { id: 'mall-directory', label: 'Gian Hàng & Tiện Ích', icon: <Store size={18} /> },
    { id: 'settings', label: 'Cài Đặt Kết Nối', icon: <Settings size={18} /> },
  ];

  const staffTabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: 'delivery-orders', label: 'Quản Lý Giao Hàng', icon: <Package size={18} /> },
    { id: 'mall-map', label: 'Sơ Đồ Robot', icon: <Map size={18} /> },
    { id: 'control', label: 'Lái Robot (WASD)', icon: <Compass size={18} /> },
    { id: 'camera', label: 'CSI Camera', icon: <Video size={18} /> },
    { id: 'dashboard', label: 'HUD Vận Hành', icon: <LayoutDashboard size={18} /> },
    { id: 'diagnostics', label: 'Nhật Ký & Phần Cứng', icon: <Activity size={18} /> },
    { id: 'motor-test', label: 'Test Động Cơ', icon: <Wrench size={18} /> },
    { id: 'settings', label: 'Cài Đặt', icon: <Settings size={18} /> },
  ];

  const tabs = userRole === 'staff' ? staffTabs : customerTabs;

  return (
    <nav className="nav-tabs" role="tablist">
      {tabs.map(tab => (
        <button
          key={tab.id}
          className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
          onClick={() => onSelectTab(tab.id)}
          role="tab"
        >
          {tab.icon}
          <span>{tab.label}</span>
        </button>
      ))}
    </nav>
  );
};
