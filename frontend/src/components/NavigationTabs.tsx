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
    { id: 'mall-map', label: 'Dẫn Đường', icon: <Map size={18} /> },
    { id: 'mall-assistant', label: 'Trợ Lý AI', icon: <Bot size={18} /> },
    { id: 'mall-directory', label: 'Gian Hàng', icon: <Store size={18} /> },
  ];

  const staffTabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: 'control', label: 'Lái Robot', icon: <Gamepad2 size={18} /> },
    { id: 'delivery-orders', label: 'Giao Hàng', icon: <Package size={18} /> },
    { id: 'mall-map', label: 'Bản Đồ', icon: <Map size={18} /> },
    { id: 'settings', label: 'Cài Đặt', icon: <Settings size={18} /> },
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
          <span className="nav-tab-label">{tab.label}</span>
        </button>
      ))}
    </nav>
  );
};
