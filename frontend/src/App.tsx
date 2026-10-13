import React, { useState, useEffect, useCallback } from 'react';
import { initializeStore, useRobotStore, updateGlobalState } from './store/useRobotStore';
import { RobotSocket } from './services/RobotSocket';
import { RobotApi } from './services/RobotApi';
import { StorageService } from './services/StorageService';
import { PairedRobotInfo } from './types/robot';
import { PointOfInterest } from './types/protocol';
import { Header } from './components/Header';
import { SafetyBanner } from './components/SafetyBanner';
import { NavigationTabs, TabType } from './components/NavigationTabs';
import { StoreDetailModal } from './components/StoreDetailModal';

// Customer / Guest Views (Area A)
import { GuestHomePage } from './pages/customer/GuestHomePage';
import { MallMapTab } from './pages/customer/MallMapTab';
import { MallAssistantTab } from './pages/customer/MallAssistantTab';
import { MallDirectoryTab } from './pages/customer/MallDirectoryTab';
import { GuestPromotionsTab } from './pages/customer/GuestPromotionsTab';

// Staff Views (Area B)
import { StaffDashboard } from './pages/staff/StaffDashboard';
import { DeliveryOrdersTab } from './pages/staff/DeliveryOrdersTab';
import { PromotionsTab } from './pages/staff/PromotionsTab';

// Robotics Control & Telemetry (Staff & Admin)
import { ControlTab } from './pages/ControlTab';

// Admin Views (Area C)
import { AdminTab } from './pages/admin/AdminTab';
import { SettingsTab } from './pages/SettingsTab';

// Initialize store listeners
initializeStore();

export const App: React.FC = () => {
  const { pairedRobot, settings, connectionStatus, isSafetyBlocked, isEmergencyStopped, userRole, currentUser } = useRobotStore();
  
  const [activeTab, setActiveTab] = useState<TabType>(
    userRole === 'admin' ? 'admin' : (userRole === 'staff' ? 'staff-dashboard' : 'home')
  );
  const [cameraTicket, setCameraTicket] = useState<string | null>(null);

  // Cross-tab navigation states
  const [mapTargetPoiId, setMapTargetPoiId] = useState<string | undefined>(undefined);
  const [assistantPrompt, setAssistantPrompt] = useState<string | undefined>(undefined);
  const [modalPoi, setModalPoi] = useState<PointOfInterest | null>(null);

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
      if (['staff-dashboard', 'control', 'delivery-orders', 'staff-promotions', 'admin', 'settings'].includes(activeTab)) {
        setActiveTab('home');
      }
    } else if (userRole === 'staff') {
      if (['admin', 'home', 'guest-promotions'].includes(activeTab)) {
        setActiveTab('staff-dashboard');
      }
    } else if (userRole === 'admin') {
      if (['home', 'guest-promotions', 'staff-dashboard'].includes(activeTab)) {
        setActiveTab('admin');
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

  // Handle navigation from Home shortcuts
  const handleNavigateTab = (tabId: TabType | string, payload?: any) => {
    if (payload?.targetPoiId) {
      setMapTargetPoiId(payload.targetPoiId);
    }
    if (payload?.prompt) {
      setAssistantPrompt(payload.prompt);
    }
    setActiveTab(tabId as TabType);
  };

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
      <Header onGoHome={() => setActiveTab(userRole === 'admin' ? 'admin' : (userRole === 'staff' ? 'staff-dashboard' : 'home'))} />
      {(userRole === 'staff' || userRole === 'admin') && <SafetyBanner />}
      <NavigationTabs activeTab={activeTab} onSelectTab={setActiveTab} />

      <main className="app-main">
        {/* ==================== AREA A: CUSTOMER / GUEST ==================== */}
        {activeTab === 'home' && (
          <GuestHomePage
            onNavigateTab={handleNavigateTab}
            onOpenStoreModal={(poi) => setModalPoi(poi)}
          />
        )}
        {activeTab === 'mall-map' && (
          <MallMapTab initialStoreId={mapTargetPoiId} />
        )}
        {activeTab === 'mall-directory' && (
          <MallDirectoryTab
            onNavigateToMap={(poiId) => handleNavigateTab('mall-map', { targetPoiId: poiId })}
            onAskAssistant={(name) => handleNavigateTab('mall-assistant', { prompt: `Chỉ đường và giới thiệu về ${name}` })}
          />
        )}
        {activeTab === 'guest-promotions' && (
          <GuestPromotionsTab
            onNavigateToMap={(poiId) => handleNavigateTab('mall-map', { targetPoiId: poiId })}
          />
        )}
        {activeTab === 'mall-assistant' && (
          <MallAssistantTab
            initialPrompt={assistantPrompt}
            onNavigateToMap={(poiId) => handleNavigateTab('mall-map', { targetPoiId: poiId })}
          />
        )}

        {/* ==================== AREA B: STAFF ==================== */}
        {activeTab === 'staff-dashboard' && <StaffDashboard />}
        {activeTab === 'delivery-orders' && <DeliveryOrdersTab />}
        {activeTab === 'staff-promotions' && <PromotionsTab />}

        {/* ==================== AREA C: ADMIN & OPERATIONAL ==================== */}
        {activeTab === 'admin' && <AdminTab />}
        {activeTab === 'control' && <ControlTab cameraTicket={cameraTicket} />}

        {/* ==================== SYSTEM SETTINGS ==================== */}
        {activeTab === 'settings' && <SettingsTab />}
      </main>

      {/* Global Store Detail Modal if opened from Home */}
      <StoreDetailModal
        store={modalPoi}
        isOpen={!!modalPoi}
        onClose={() => setModalPoi(null)}
        onNavigateToMap={(poiId) => {
          setModalPoi(null);
          handleNavigateTab('mall-map', { targetPoiId: poiId });
        }}
        onAskAssistant={(name) => {
          setModalPoi(null);
          handleNavigateTab('mall-assistant', { prompt: `Chỉ đường và giới thiệu về ${name}` });
        }}
      />
    </div>
  );
};
