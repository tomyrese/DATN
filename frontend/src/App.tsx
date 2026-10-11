import React, { useState, useEffect, useCallback } from 'react';
import { initializeStore, useRobotStore, updateGlobalState } from './store/useRobotStore';
import { RobotSocket } from './services/RobotSocket';
import { RobotApi } from './services/RobotApi';
import { StorageService } from './services/StorageService';
import { PairedRobotInfo } from './types/robot';
import { Header } from './components/Header';
import { SafetyBanner } from './components/SafetyBanner';
import { NavigationTabs, TabType } from './components/NavigationTabs';

// Customer Views
import { MallMapTab } from './pages/customer/MallMapTab';
import { MallAssistantTab } from './pages/customer/MallAssistantTab';
import { MallDirectoryTab } from './pages/customer/MallDirectoryTab';

// Staff & Admin Views
import { ControlTab } from './pages/ControlTab';
import { DeliveryOrdersTab } from './pages/staff/DeliveryOrdersTab';
import { PromotionsTab } from './pages/staff/PromotionsTab';
import { AdminTab } from './pages/admin/AdminTab';
import { SettingsTab } from './pages/SettingsTab';

// Initialize store listeners
initializeStore();

export const App: React.FC = () => {
  const { pairedRobot, settings, connectionStatus, isSafetyBlocked, isEmergencyStopped, userRole, currentUser } = useRobotStore();
  const [activeTab, setActiveTab] = useState<TabType>(
    userRole === 'admin' ? 'admin' : (userRole === 'staff' ? 'control' : 'mall-map')
  );
  const [cameraTicket, setCameraTicket] = useState<string | null>(null);

  // Auto-pair from URL query param when scanning OLED QR code
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const codeParam = params.get('code') || params.get('pairCode');
    const roleParam = params.get('role');

    const host = window.location.hostname || 'localhost';
    const port = window.location.port ? parseInt(window.location.port, 10) : (window.location.protocol === 'https:' ? 443 : 8765);

    if (codeParam) {
      RobotApi.pair(host, port, codeParam).then(res => {
        if (res.success && res.token) {
          const robotInfo: PairedRobotInfo = {
            robotId: res.robotId,
            robotName: res.robotName,
            host,
            port,
            token: res.token,
            lastConnected: Date.now(),
          };
          StorageService.savePairedRobot(robotInfo);
          if (roleParam === 'staff') {
            StorageService.saveUserRole('staff');
            updateGlobalState(() => ({ userRole: 'staff' }));
          }
          updateGlobalState(() => ({ pairedRobot: robotInfo }));
          RobotSocket.getInstance().connect(host, port, res.token);

          const cleanUrl = window.location.pathname;
          window.history.replaceState({}, document.title, cleanUrl);
        }
      }).catch(err => {
        console.warn('Auto pairing via QR code URL failed:', err);
      });
    } else {
      RobotApi.getMallPois(host, port, false).then(pois => {
        if (pois && pois.length > 0) {
          updateGlobalState(() => ({ pois }));
        }
      }).catch(() => {});
    }
  }, []);

  // Sync tab when userRole switches
  useEffect(() => {
    if (userRole === 'customer' || userRole === 'guest') {
      if (['control', 'delivery-orders', 'staff-promotions', 'admin', 'settings'].includes(activeTab)) {
        setActiveTab('mall-map');
      }
    } else if (userRole === 'staff') {
      if (['admin', 'mall-directory'].includes(activeTab)) {
        setActiveTab('control');
      }
    }
  }, [userRole]);

  // Auto-connect on startup and when pairedRobot changes
  useEffect(() => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : (window.location.protocol === 'https:' ? 443 : 8765));
    const token = currentUser?.token || pairedRobot?.token || 'guest';
    RobotSocket.getInstance().connect(host, port, token);
  }, [pairedRobot, currentUser]);

  // Periodic camera ticket refresh for authenticated staff/admin
  const refreshCameraTicket = useCallback(async () => {
    const token = currentUser?.token || pairedRobot?.token;
    if (token && (userRole === 'staff' || userRole === 'admin') && connectionStatus === 'CONNECTED') {
      try {
        const host = pairedRobot?.host || window.location.hostname || 'localhost';
        const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
        const ticket = await RobotApi.getCameraTicket(host, port, token);
        if (ticket) {
          setCameraTicket(ticket);
        }
      } catch (err) {
        console.warn('Failed to refresh camera ticket:', err);
      }
    }
  }, [pairedRobot, currentUser, userRole, connectionStatus]);

  useEffect(() => {
    refreshCameraTicket();
    const interval = setInterval(refreshCameraTicket, 3 * 60 * 1000);
    return () => clearInterval(interval);
  }, [refreshCameraTicket]);

  // Keyboard drive controls (Staff and Admin modes only)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      const socket = RobotSocket.getInstance();
      const speed = settings.defaultSpeed || 0.35;
      const key = e.key.toLowerCase();

      // Emergency Controls
      if (key === 'e' || key === 'x') {
        socket.sendEmergencyStop();
        const host = pairedRobot?.host || window.location.hostname || 'localhost';
        const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
        RobotApi.emergencyStop(host, port);
        return;
      }

      if (key === 'r') {
        socket.sendEmergencyReset();
        const host = pairedRobot?.host || window.location.hostname || 'localhost';
        const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
        const token = currentUser?.token || pairedRobot?.token || '';
        RobotApi.emergencyReset(host, port, token);
        return;
      }

      // Drive Controls (Staff or Admin only)
      if ((userRole === 'staff' || userRole === 'admin') && connectionStatus === 'CONNECTED' && !isSafetyBlocked && !isEmergencyStopped) {
        switch (key) {
          case 'w':
          case 'arrowup':
            e.preventDefault();
            socket.startDriveLoop('forward', speed);
            break;
          case 's':
          case 'arrowdown':
            e.preventDefault();
            socket.startDriveLoop('backward', speed);
            break;
          case 'a':
          case 'arrowleft':
            e.preventDefault();
            socket.startDriveLoop('left', speed);
            break;
          case 'd':
          case 'arrowright':
            e.preventDefault();
            socket.startDriveLoop('right', speed);
            break;
          case ' ':
            e.preventDefault();
            socket.stopDriveLoop();
            break;
        }
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return;

      const key = e.key.toLowerCase();
      if (['w', 'a', 's', 'd', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright'].includes(key)) {
        if (connectionStatus === 'CONNECTED') {
          RobotSocket.getInstance().stopDriveLoop();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [connectionStatus, isSafetyBlocked, isEmergencyStopped, settings.defaultSpeed, pairedRobot, userRole, currentUser]);

  return (
    <div className="app-container">
      <Header />
      {(userRole === 'staff' || userRole === 'admin') && <SafetyBanner />}
      <NavigationTabs activeTab={activeTab} onSelectTab={setActiveTab} />

      <main className="app-main">
        {/* Customer / Guest Views */}
        {activeTab === 'mall-map' && <MallMapTab />}
        {activeTab === 'mall-assistant' && <MallAssistantTab />}
        {activeTab === 'mall-directory' && <MallDirectoryTab />}

        {/* Staff & Admin Shared Views */}
        {activeTab === 'control' && <ControlTab cameraTicket={cameraTicket} />}
        {activeTab === 'delivery-orders' && <DeliveryOrdersTab />}
        {activeTab === 'staff-promotions' && <PromotionsTab />}

        {/* Admin Views */}
        {activeTab === 'admin' && <AdminTab />}

        {/* Settings & Diagnostics */}
        {activeTab === 'settings' && <SettingsTab />}
      </main>
    </div>
  );
};
