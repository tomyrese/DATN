import React, { useState, useRef, useEffect } from 'react';
import { useRobotStore, updateGlobalState } from '../../store/useRobotStore';
import { RobotApi } from '../../services/RobotApi';
import { ChatMessage } from '../../types/robot';
import { Bot, Send, Sparkles, Navigation, User } from 'lucide-react';

const QUICK_PROMPTS = [
  'Nhà vệ sinh ở đâu?',
  'Quán cà phê gần đây',
  'Cửa hàng thời trang ZARA',
  'Rạp chiếu phim CGV',
  'Giờ mở cửa TTTM',
  'Mật khẩu WiFi miễn phí',
];

export const MallAssistantTab: React.FC = () => {
  const { chatMessages, pairedRobot, pois } = useRobotStore();
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

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
        text: 'Xin lỗi quý khách, hệ thống AI tạm thời gián đoạn kết nối. Quý khách có thể xem bản đồ hoặc thử lại!',
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
        alert(`Robot đã bắt đầu dẫn đường đến: ${res.task.target_name}!`);
      }
    } catch (e: any) {
      alert(`Lỗi: ${e.message}`);
    }
  };

  return (
    <div className="tab-pane active">
      <div className="assistant-container">
        
        {/* Assistant Header Card */}
        <div className="assistant-hero">
          <div className="assistant-avatar">
            <Bot size={28} color="#00E5FF" />
          </div>
          <div>
            <h2 className="assistant-title">TRỢ LÝ ẢO ROBOT TTTM (AI CONCIERGE)</h2>
            <p className="assistant-sub">Hỏi đáp thông tin gian hàng, tiện ích, sự kiện và yêu cầu robot dẫn đường tức thì.</p>
          </div>
        </div>

        {/* Quick Suggestion Chips */}
        <div className="quick-chips-row">
          <Sparkles size={16} color="#00E5FF" style={{ flexShrink: 0 }} />
          <div className="chips-scroll">
            {QUICK_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                className="chip-btn"
                onClick={() => handleSend(prompt)}
                disabled={loading}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Message Stream */}
        <div className="chat-thread-box">
          {chatMessages.map(msg => {
            const isBot = msg.sender === 'assistant';
            return (
              <div key={msg.id} className={`chat-bubble-row ${isBot ? 'bot-row' : 'user-row'}`}>
                <div className={`chat-bubble ${isBot ? 'bot-bubble' : 'user-bubble'}`}>
                  <div className="bubble-header">
                    <span className="bubble-sender">{isBot ? 'ROBOT CONCIERGE' : 'QUÝ KHÁCH'}</span>
                    <span className="bubble-time">{msg.time}</span>
                  </div>

                  <div className="bubble-text">{msg.text}</div>

                  {/* Action button if bot suggested a location */}
                  {isBot && msg.suggestedPoiId && (
                    <div className="bubble-action-box">
                      <button
                        className="btn-escort-chip"
                        onClick={() => handleEscortToSuggested(msg.suggestedPoiId!)}
                      >
                        <Navigation size={14} style={{ display: 'inline', marginRight: 6 }} />
                        Dẫn đường tới {msg.suggestedPoiName || 'địa điểm này'}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="chat-bubble-row bot-row">
              <div className="chat-bubble bot-bubble typing-bubble">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span style={{ fontSize: 12, color: '#64748B', marginLeft: 8 }}>Robot đang suy nghĩ câu trả lời...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form
          className="chat-input-bar"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(inputText);
          }}
        >
          <input
            type="text"
            className="input-text chat-input-field"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Hỏi vị trí gian hàng, rạp phim, nhà vệ sinh, ẩm thực..."
            disabled={loading}
          />
          <button type="submit" className="btn-primary btn-chat-send" disabled={loading || !inputText.trim()}>
            <Send size={16} />
          </button>
        </form>

      </div>
    </div>
  );
};
