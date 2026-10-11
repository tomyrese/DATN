import React from 'react';
import { useRobotStore } from '../store/useRobotStore';
import { Map, Bot, Store, Gamepad2, Package, Settings, Tag, ShieldCheck } from 'lucide-react';

export type TabType =
  | 'mall-map'
  | 'mall-assistant'
  | 'mall-directory'
  | 'control'
  | 'delivery-orders'
  | 'staff-promotions'
  | 'admin'
  | 'settings';

interface NavigationTabsProps {
  activeTab: TabType;
  onSelectTab: (tab: TabType) => void;
}

export const NavigationTabs: React.FC<NavigationTabsProps> = ({ activeTab, onSelectTab }) => {
  const { userRole } = useRobotStore();

  const customerTabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: 'mall-map', label: 'Dẫn Đường', icon: <Map size={18} /> },
    { id: 'mall-assistant', label: 'Trợ Lý Ảo', icon: <Bot size={18} /> },
    { id: 'mall-directory', label: 'Gian Hàng', icon: <Store size={18} /> },
  ];

  const staffTabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: 'control', label: 'Điều Khiển', icon: <Gamepad2 size={18} /> },
    { id: 'delivery-orders', label: 'Giao Hàng', icon: <Package size={18} /> },
    { id: 'staff-promotions', label: 'Khuyến Mãi', icon: <Tag size={18} /> },
    { id: 'mall-map', label: 'Bản Đồ', icon: <Map size={18} /> },
    { id: 'mall-assistant', label: 'Trợ Lý AI', icon: <Bot size={18} /> },
    { id: 'settings', label: 'Cài Đặt', icon: <Settings size={18} /> },
  ];

  const adminTabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: 'admin', label: 'Quản Trị', icon: <ShieldCheck size={18} /> },
    { id: 'control', label: 'Điều Khiển', icon: <Gamepad2 size={18} /> },
    { id: 'delivery-orders', label: 'Giao Hàng', icon: <Package size={18} /> },
    { id: 'staff-promotions', label: 'Khuyến Mãi', icon: <Tag size={18} /> },
    { id: 'mall-map', label: 'Bản Đồ', icon: <Map size={18} /> },
    { id: 'settings', label: 'Cài Đặt', icon: <Settings size={18} /> },
  ];

  let tabs = customerTabs;
  if (userRole === 'admin') {
    tabs = adminTabs;
  } else if (userRole === 'staff') {
    tabs = staffTabs;
  }

  return (
    <nav className="main-nav-bar" role="tablist">
      {tabs.map(tab => (
        <button
          key={tab.id}
          className={`nav-tab-item ${activeTab === tab.id ? 'active' : ''}`}
          onClick={() => onSelectTab(tab.id)}
          role="tab"
        >
          {tab.icon}
          <span className="nav-tab-label">{tab.label}</span>
        </button>
      ))}
    </nav>
  );
};
