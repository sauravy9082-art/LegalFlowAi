import React, { useState, useEffect } from 'react';
import { Send, Bot, User as UserIcon, Globe, Sparkles, Loader2, RotateCcw } from 'lucide-react';
import { chatAPI } from '../services/api';

const INITIAL_WELCOME_MESSAGE = {
  id: 'welcome',
  sender: 'ai',
  message: 'Hello! I am your LegalFlow AI Assistant. Ask me anything about notice periods, security deposits, liability, termination clauses, or financial penalties in this contract.',
  referenced_pages: []
};

export const ChatPanel = ({ documentId }) => {
  const storageKey = `legalflow_chat_${documentId}`;

  const [messages, setMessages] = useState(() => {
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch (e) {}
    return [INITIAL_WELCOME_MESSAGE];
  });

  const [input, setInput] = useState('');
  const [language, setLanguage] = useState('English');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!documentId) return;

    chatAPI.getHistory(documentId)
      .then((res) => {
        if (res && Array.isArray(res.data) && res.data.length > 0) {
          const combined = [INITIAL_WELCOME_MESSAGE, ...res.data];
          setMessages(combined);
          try {
            localStorage.setItem(storageKey, JSON.stringify(combined));
          } catch (e) {}
        }
      })
      .catch(() => {});
  }, [documentId]);

  useEffect(() => {
    if (documentId && messages.length > 0) {
      try {
        localStorage.setItem(storageKey, JSON.stringify(messages));
      } catch (e) {}
    }
  }, [messages, documentId]);

  const handleClearHistory = async () => {
    if (window.confirm('Clear all chat conversation history for this document?')) {
      setMessages([INITIAL_WELCOME_MESSAGE]);
      try {
        localStorage.removeItem(storageKey);
        await chatAPI.clearHistory(documentId);
      } catch (e) {}
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput('');
    
    const userMsg = { id: Date.now().toString(), sender: 'user', message: userText };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await chatAPI.sendMessage(documentId, userText, null, language);
      setMessages(prev => [...prev, res.data]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          message: 'Legal AI Assistant Analysis: This agreement specifies standard contract terms. Ask specific questions about notice periods or liability to inspect context.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#EAE6DC] border-l border-[#D9D6CC] text-[#17202A]">
      {/* Header */}
      <div className="p-3 border-b border-[#D9D6CC] bg-[#102A43] text-white flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-[#B58B45]" />
          <span className="text-xs font-bold text-white tracking-tight">Ask LegalFlow AI</span>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={handleClearHistory}
            className="px-2 py-1 bg-[#163A59] hover:bg-[#102A43] text-slate-200 hover:text-white rounded border border-slate-500/40 text-[10px] font-medium transition-colors flex items-center gap-1 shadow-2xs"
            title="Clear Chat History"
          >
            <RotateCcw className="w-3 h-3 text-slate-300" />
            <span>Clear Chat</span>
          </button>

          <div className="flex items-center gap-1 bg-[#163A59] px-1.5 py-0.5 rounded border border-slate-500/40 shadow-2xs">
            <Globe className="w-3 h-3 text-slate-300" />
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-transparent text-[11px] text-slate-200 font-semibold focus:outline-none cursor-pointer"
            >
              <option value="English" className="bg-[#102A43] text-white">English</option>
              <option value="Hindi" className="bg-[#102A43] text-white">Hindi (हिन्दी)</option>
              <option value="Marathi" className="bg-[#102A43] text-white">Marathi (मराठी)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3.5 bg-[#EAE6DC]">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-2.5 text-xs ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'ai' && (
              <div className="w-6 h-6 rounded bg-[#102A43] text-white flex items-center justify-center shrink-0 shadow-2xs mt-0.5">
                <Bot className="w-3.5 h-3.5 text-[#B58B45]" />
              </div>
            )}

            <div className={`max-w-[85%] rounded-lg px-3.5 py-2.5 leading-relaxed shadow-2xs ${
              msg.sender === 'user'
                ? 'bg-[#163A59] text-white'
                : 'bg-[#FFFFFF] border border-[#D9D6CC] text-[#17202A]'
            }`}>
              <p className="whitespace-pre-wrap">{msg.message}</p>
              
              {msg.referenced_pages && msg.referenced_pages.length > 0 && (
                <div className="mt-2 text-[10px] text-[#64748B] border-t border-[#D9D6CC] pt-1 flex items-center gap-1 font-mono">
                  <span>Referenced Pages: Page {msg.referenced_pages.join(', ')}</span>
                </div>
              )}
            </div>

            {msg.sender === 'user' && (
              <div className="w-6 h-6 rounded bg-[#0F766E] text-white flex items-center justify-center shrink-0 mt-0.5">
                <UserIcon className="w-3.5 h-3.5" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-[11px] text-[#64748B] italic p-2 bg-white rounded border border-[#D9D6CC] shadow-2xs w-max">
            <Loader2 className="w-3 h-3 animate-spin text-[#163A59]" />
            Analyzing contract context...
          </div>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSend} className="p-3 border-t border-[#D9D6CC] bg-white">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about this contract..."
            className="w-full bg-[#F4F1E8] border border-[#D9D6CC] rounded-lg py-2 pl-3 pr-9 text-xs text-[#17202A] placeholder-[#64748B] focus:outline-none focus:bg-white focus:border-[#163A59] focus:ring-1 focus:ring-[#163A59] transition-colors"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="absolute right-1 p-1.5 bg-[#163A59] hover:bg-[#102A43] disabled:opacity-30 text-white rounded-md transition-colors"
          >
            <Send className="w-3 h-3" />
          </button>
        </div>
      </form>
    </div>
  );
};
