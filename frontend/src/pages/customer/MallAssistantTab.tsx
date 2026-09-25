import React, { useState, useRef, useEffect } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { ChatMessage } from '../../types/robot';
import { Bot, Send, Sparkles, Navigation, User } from 'lucide-react';

const QUICK_PROMPTS = [
  '🚻 Nhà vệ sinh gần nhất ở đâu?',
  '☕ Tìm quán cà phê Highlands',
  '👕 Cửa hàng thời trang Uniqlo',
  '🎬 Rạp chiếu phim CGV',
  '📶 Mật khẩu WiFi miễn phí',
  '🕒 Giờ đóng cửa TTTM',
];

export const MallAssistantTab: React.FC = () => {
  const { chatMessages, pairedRobot } = useRobotStore();
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, loading]);

  const handleSend = async (questionText: string) => {
    const query = questionText.trim();
    if (!query) return;

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text: query,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    updateGlobalState(prev => ({
      chatMessages: [...prev.chatMessages, userMsg],
    }));

    setInputText('');
    setLoading(true);

    try {
      const host = pairedRobot?.host || window.location.hostname || 'localhost';
      const port = pairedRobot?.port || 8765;
      const res = await RobotApi.askAssistant(host, port, query);

      const botMsg: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        sender: 'assistant',
        text: res.answer,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        suggestedPoiId: res.suggested_poi_id,
        suggestedPoiName: res.suggested_poi_name,
      };

      updateGlobalState(prev => ({
        chatMessages: [...prev.chatMessages, botMsg],
      }));
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        sender: 'assistant',
        text: 'Xin lỗi quý khách, hệ thống AI đang bận một chút. Quý khách có thể xem bản đồ hoặc bấm thử lại nhé!',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      updateGlobalState(prev => ({
        chatMessages: [...prev.chatMessages, errorMsg],
      }));
    } finally {
      setLoading(false);
    }
  };

  const handleEscortToSuggested = async (poiId: string) => {
    const host = pairedRobot?.host || window.location.hostname || 'localhost';
    const port = pairedRobot?.port || (window.location.port ? parseInt(window.location.port, 10) : 8765);
    try {
      const res = await RobotApi.requestEscort(host, port, poiId);
      if (res.success && res.task) {
        updateGlobalState(() => ({ activeEscort: res.task }));
        alert(`🎉 Robot đã nhận lệnh và bắt đầu dẫn đường đến: ${res.task.target_name}!`);
      }
    } catch (e: any) {
      alert(`Lỗi: ${e.message}`);
    }
  };

  return (
    <div className="chat-container-card">
      
      {/* Friendly AI Concierge Welcome Header */}
      <div className="chat-welcome-banner">
        <div className="chat-welcome-avatar">🤖</div>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 800 }}>TRỢ LÝ ẢO</h2>
          <p style={{ fontSize: '0.85rem', color: '#64748B' }}>
            Hỏi bất cứ điều gì về các gian hàng, ẩm thực, rạp phim hoặc yêu cầu dẫn đường trực tiếp!
          </p>
        </div>
      </div>

      {/* Quick Suggestion Chips */}
      <div className="chat-suggestions-bar">
        {QUICK_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            className="suggestion-chip"
            onClick={() => handleSend(prompt)}
            disabled={loading}
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Chat Messages Stream */}
      <div className="chat-messages-area">
        {chatMessages.map(msg => {
          const isBot = msg.sender === 'assistant';
          return (
            <div key={msg.id} className={`chat-msg-row ${isBot ? 'bot' : 'user'}`}>
              <div className="chat-bubble-clean">
                <div>{msg.text}</div>

                {/* 1-Touch Escort Trigger */}
                {isBot && msg.suggestedPoiId && (
                  <div>
                    <button
                      className="btn-msg-escort"
                      onClick={() => handleEscortToSuggested(msg.suggestedPoiId!)}
                    >
                      <Navigation size={14} />
                      <span>Dẫn tôi đến {msg.suggestedPoiName || 'đây'} ngay 👉</span>
                    </button>
                  </div>
                )}
                
                <div style={{ fontSize: '0.72rem', opacity: 0.6, marginTop: '4px', textAlign: isBot ? 'left' : 'right' }}>
                  {msg.time}
                </div>
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="chat-msg-row bot">
            <div className="chat-bubble-clean" style={{ color: '#64748B', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="spin-pulse">⏳</span>
              <span>Robot đang tìm câu trả lời tốt nhất cho quý khách...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input Bar */}
      <form
        className="chat-input-bar"
        onSubmit={e => {
          e.preventDefault();
          handleSend(inputText);
        }}
      >
        <input
          type="text"
          className="chat-input-field"
          value={inputText}
          onChange={e => setInputText(e.target.value)}
          placeholder="Nhập câu hỏi của bạn (VD: Tìm quán ăn ngon, nhà vệ sinh ở đâu...)"
          disabled={loading}
        />
        <button
          type="submit"
          className="btn-solid-blue"
          disabled={loading || !inputText.trim()}
          style={{ borderRadius: '9999px', padding: '12px 24px' }}
        >
          <Send size={18} />
          <span>Gửi</span>
        </button>
      </form>

    </div>
  );
};
