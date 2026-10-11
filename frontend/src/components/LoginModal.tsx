import React, { useState } from 'react';
import { useRobotStore, updateGlobalState } from '../store/useRobotStore';
import { RobotApi } from '../services/RobotApi';
import { StorageService } from '../services/StorageService';
import { RobotSocket } from '../services/RobotSocket';
import { ShieldCheck, LogIn, X, User, Lock, Store, Shield } from 'lucide-react';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose }) => {
  const { pairedRobot } = useRobotStore();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleLogin = async (u?: string, p?: string) => {
    const userToLogin = u || username;
    const passToLogin = p || password;

    if (!userToLogin.trim() || !passToLogin) {
      setError('Vui lòng nhập tên người dùng và mật khẩu');
      return;
    }

    setLoading(true);
    setError(null);

    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);

    try {
      const res = await RobotApi.login(host, port, { username: userToLogin.trim(), password: passToLogin });
      if (res.success && res.user && res.token) {
        StorageService.saveAuthUser(res.user);
        updateGlobalState(() => ({
          currentUser: res.user,
          userRole: res.user.role,
        }));
        // Re-authenticate WebSocket if needed
        RobotSocket.getInstance().connect(host, port, res.token);
        onClose();
      } else {
        setError(res.message || 'Tên đăng nhập hoặc mật khẩu không chính xác');
      }
    } catch (e: any) {
      setError(`Lỗi: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
    handleLogin(u, p);
  };

  return (
    <div className="modal-backdrop" onClick={onClose} style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(15, 23, 42, 0.75)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '16px'
    }}>
      <div
        className="modal-card"
        onClick={(e) => e.stopPropagation()}
        style={{
          background: '#FFFFFF',
          borderRadius: '16px',
          width: '100%',
          maxWidth: '420px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* Header */}
        <div style={{
          padding: '16px 20px',
          background: 'linear-gradient(135deg, #1E293B 0%, #0F172A 100%)',
          color: '#FFFFFF',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={20} color="#38BDF8" />
            <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 800 }}>ĐĂNG NHẬP HỆ THỐNG</h3>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#94A3B8',
              cursor: 'pointer',
              padding: '4px',
              display: 'flex',
              alignItems: 'center',
              borderRadius: '6px'
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <p style={{ margin: 0, fontSize: '0.82rem', color: '#64748B' }}>
            Đăng nhập tài khoản Nhân viên gian hàng hoặc Quản trị viên để truy cập camera trực tiếp, điều khiển robot và quản lý khuyến mãi.
          </p>

          {error && (
            <div style={{
              padding: '10px 12px',
              background: '#FEE2E2',
              border: '1px solid #FCA5A5',
              borderRadius: '8px',
              color: '#DC2626',
              fontSize: '0.8rem',
              fontWeight: 600
            }}>
              {error}
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#334155' }}>
              Tên Đăng Nhập
            </label>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              border: '1.5px solid #CBD5E1',
              borderRadius: '8px',
              padding: '0 10px',
              background: '#F8FAFC'
            }}>
              <User size={16} color="#94A3B8" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Ví dụ: staff_zara hoặc admin"
                style={{
                  width: '100%',
                  padding: '10px 8px',
                  border: 'none',
                  background: 'transparent',
                  outline: 'none',
                  fontSize: '0.85rem'
                }}
              />
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#334155' }}>
              Mật Khẩu
            </label>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              border: '1.5px solid #CBD5E1',
              borderRadius: '8px',
              padding: '0 10px',
              background: '#F8FAFC'
            }}>
              <Lock size={16} color="#94A3B8" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Nhập mật khẩu..."
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleLogin();
                }}
                style={{
                  width: '100%',
                  padding: '10px 8px',
                  border: 'none',
                  background: 'transparent',
                  outline: 'none',
                  fontSize: '0.85rem'
                }}
              />
            </div>
          </div>

          <button
            onClick={() => handleLogin()}
            disabled={loading}
            style={{
              marginTop: '4px',
              padding: '12px',
              background: '#2563EB',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '8px',
              fontWeight: 700,
              fontSize: '0.9rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'background 0.2s ease',
              opacity: loading ? 0.7 : 1
            }}
          >
            <LogIn size={16} />
            <span>{loading ? 'Đang xác thực...' : 'Đăng Nhập'}</span>
          </button>

          {/* Quick Login Presets for Demo */}
          <div style={{
            marginTop: '8px',
            paddingTop: '12px',
            borderTop: '1px dashed #E2E8F0',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase' }}>
              Đăng nhập mẫu (Demo):
            </span>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <button
                type="button"
                onClick={() => handleQuickLogin('staff_zara', 'staff123')}
                style={{
                  padding: '8px 10px',
                  background: '#EFF6FF',
                  border: '1px solid #BFDBFE',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  color: '#1D4ED8',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <Store size={13} />
                <span>Staff: ZARA</span>
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('staff_uniqlo', 'staff123')}
                style={{
                  padding: '8px 10px',
                  background: '#FDF2F8',
                  border: '1px solid #FBCFE8',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  color: '#BE185D',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <Store size={13} />
                <span>Staff: UNIQLO</span>
              </button>
            </div>
            <button
              type="button"
              onClick={() => handleQuickLogin('admin', 'admin123')}
              style={{
                width: '100%',
                padding: '8px 10px',
                background: '#FEF3C7',
                border: '1px solid #FDE68A',
                borderRadius: '6px',
                fontSize: '0.75rem',
                color: '#B45309',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px'
              }}
            >
              <Shield size={14} />
              <span>Quản Trị Viên (Admin)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
