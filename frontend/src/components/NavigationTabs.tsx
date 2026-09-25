import React from 'react';
import { useRobotStore } from '../store/useRobotStore';
import { Map, Bot, Store, Gamepad2, Package, Settings } from 'lucide-react';

export type TabType =
  | 'mall-map'
  | 'mall-assistant'
  | 'mall-directory'
  | 'control'
  | 'delivery-orders'
  | 'settings';

interface NavigationTabsProps {
  activeTab: TabType;
  onSelectTab: (tab: TabType) => void;
}

export const NavigationTabs: React.FC<NavigationTabsProps> = ({ activeTab, onSelectTab }) => {
  const { userRole } = useRobotStore();

  const customerTabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: 'mall-map', label: 'Bản Đồ Dẫn Đường', icon: <Map size={20} /> },
    { id: 'mall-assistant', label: 'Hỏi Trợ Lý AI', icon: <Bot size={20} /> },
    { id: 'mall-directory', label: 'Danh Bạ Gian Hàng', icon: <Store size={20} /> },
  ];

  const staffTabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: 'control', label: 'Lái Robot & Camera', icon: <Gamepad2 size={20} /> },
    { id: 'delivery-orders', label: 'Quản Lý Giao Hàng', icon: <Package size={20} /> },
    { id: 'mall-map', label: 'Sơ Đồ Robot', icon: <Map size={20} /> },
    { id: 'settings', label: 'Cài Đặt & Kỹ Thuật', icon: <Settings size={20} /> },
  ];

  const tabs = userRole === 'staff' ? staffTabs : customerTabs;

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
          <span>{tab.label}</span>
        </button>
      ))}
    </nav>
  );
};
