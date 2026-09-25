import React, { useState, useEffect, useCallback } from 'react';
import { initializeStore, useRobotStore, updateGlobalState } from './store/useRobotStore';
import { RobotSocket } from './services/RobotSocket';
import { RobotApi } from './services/RobotApi';
import { StorageService } from './services/StorageService';
import { PairedRobotInfo } from './types/robot';
import { Header } from './components/Header';
import { SafetyBanner } from './components/SafetyBanner';
import { NavigationTabs, TabType } from './components/NavigationTabs';
import { PairingModal } from './components/PairingModal';

// Customer Tabs
import { MallMapTab } from './pages/customer/MallMapTab';
import { MallAssistantTab } from './pages/customer/MallAssistantTab';
import { MallDirectoryTab } from './pages/customer/MallDirectoryTab';

// Staff Tabs
import { DeliveryOrdersTab } from './pages/staff/DeliveryOrdersTab';
import { DashboardTab } from './pages/DashboardTab';
import { ControlTab } from './pages/ControlTab';
import { CameraTab } from './pages/CameraTab';
import { DiagnosticsTab } from './pages/DiagnosticsTab';
import { MotorTestTab } from './pages/MotorTestTab';
import { SettingsTab } from './pages/SettingsTab';

// Initialize the store listeners once on load
initializeStore();

export const App: React.FC = () => {
  const { pairedRobot, settings, connectionStatus, isSafetyBlocked, isEmergencyStopped, userRole } = useRobotStore();
  const [activeTab, setActiveTab] = useState<TabType>(userRole === 'staff' ? 'delivery-orders' : 'mall-map');
  const [isPairingOpen, setIsPairingOpen] = useState(false);
  const [cameraTicket, setCameraTicket] = useState<string | null>(null);

  // Auto-pair from URL query param when scanning OLED QR code (e.g. http://pi-ip:8765/?code=ABC123)
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

          // Clean URL without reloading page
          const cleanUrl = window.location.pathname;
          window.history.replaceState({}, document.title, cleanUrl);
        }
      }).catch(err => {
        console.warn('Auto pairing via QR code URL failed:', err);
      });
    } else {
      // Auto-load POIs & info from current origin if hosted directly on Raspberry Pi
      RobotApi.getMallPois(host, port, false).then(pois => {
        if (pois && pois.length > 0) {
          updateGlobalState(() => ({ pois }));
        }
      }).catch(() => {});
    }
  }, []);

  // Sync tab when userRole switches
  useEffect(() => {
    if (userRole === 'customer') {
      if (['delivery-orders', 'control', 'camera', 'dashboard', 'diagnostics', 'motor-test'].includes(activeTab)) {
        setActiveTab('mall-map');
      }
    } else if (userRole === 'staff') {
      if (['mall-assistant', 'mall-directory'].includes(activeTab)) {
        setActiveTab('delivery-orders');
      }
    }
  }, [userRole]);

  // Auto-connect on startup if robot info is saved
  useEffect(() => {
    if (pairedRobot && connectionStatus === 'DISCONNECTED') {
      RobotSocket.getInstance().connect(pairedRobot.host, pairedRobot.port, pairedRobot.token);
    }
  }, [pairedRobot, connectionStatus]);

  // Periodic camera ticket refresh (tickets expire in 5 minutes)
  const refreshCameraTicket = useCallback(async () => {
    if (pairedRobot && connectionStatus === 'CONNECTED') {
      try {
        const ticket = await RobotApi.getCameraTicket(pairedRobot.host, pairedRobot.port, pairedRobot.token);
        if (ticket) {
          setCameraTicket(ticket);
        }
      } catch (err) {
        console.warn('Failed to refresh camera ticket:', err);
      }
    }
  }, [pairedRobot, connectionStatus]);

  useEffect(() => {
    refreshCameraTicket();
    const interval = setInterval(refreshCameraTicket, 3 * 60 * 1000); // every 3 mins
    return () => clearInterval(interval);
  }, [refreshCameraTicket]);

  // Global Keyboard Navigation & Control shortcuts (Staff mode only)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't capture when typing in inputs or textareas
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      const socket = RobotSocket.getInstance();
      const speed = settings.defaultSpeed || 0.35;
      const key = e.key.toLowerCase();

      // Emergency Controls (always available)
      if (key === 'e' || key === 'x') {
        socket.sendEmergencyStop();
        if (pairedRobot) {
          RobotApi.emergencyStop(pairedRobot.host, pairedRobot.port);
        }
        return;
      }

      if (key === 'r') {
        socket.sendEmergencyReset();
        if (pairedRobot) {
          RobotApi.emergencyReset(pairedRobot.host, pairedRobot.port, pairedRobot.token);
        }
        return;
      }

      // Drive Controls (only for Staff if connected & safety clear)
      if (userRole === 'staff' && connectionStatus === 'CONNECTED' && !isSafetyBlocked && !isEmergencyStopped) {
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
  }, [connectionStatus, isSafetyBlocked, isEmergencyStopped, settings.defaultSpeed, pairedRobot, userRole]);

  return (
    <div className="app-container">
      <Header onOpenPairModal={() => setIsPairingOpen(true)} />
      {userRole === 'staff' && <SafetyBanner />}
      <NavigationTabs activeTab={activeTab} onSelectTab={setActiveTab} />

      <main className="app-main">
        {/* Customer Views */}
        {activeTab === 'mall-map' && <MallMapTab />}
        {activeTab === 'mall-assistant' && <MallAssistantTab />}
        {activeTab === 'mall-directory' && <MallDirectoryTab />}

        {/* Staff Views */}
        {activeTab === 'delivery-orders' && <DeliveryOrdersTab />}
        {activeTab === 'dashboard' && <DashboardTab onSelectTab={setActiveTab} />}
        {activeTab === 'control' && <ControlTab cameraTicket={cameraTicket} />}
        {activeTab === 'camera' && <CameraTab cameraTicket={cameraTicket} />}
        {activeTab === 'diagnostics' && <DiagnosticsTab />}
        {activeTab === 'motor-test' && <MotorTestTab />}

        {/* Common Settings */}
        {activeTab === 'settings' && <SettingsTab />}
      </main>

      <PairingModal isOpen={isPairingOpen} onClose={() => setIsPairingOpen(false)} />
    </div>
  );
};
