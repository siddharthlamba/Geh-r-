import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, Paperclip, Smile, Mic, CheckCheck, Bot, Sparkles, 
  MapPin, Clock, Search, MoreVertical, Phone, Video, Plus, 
  Image as ImageIcon, X, ExternalLink, ShieldCheck, ChevronRight
} from 'lucide-react';
import confetti from 'canvas-confetti';
import ConfirmationCard from './ConfirmationCard';
import SeverityBadge from './SeverityBadge';
import StatusBadge from './StatusBadge';
import { sendMessage, getSessionHistory, resetSession, uploadEvidenceFile } from '../api';

const QUICK_SUGGESTIONS = [
  { label: 'No Wi-Fi in Block C 📶', prompt: 'There has been no Wi-Fi in Block C since yesterday.' },
  { label: 'AC broken in B-204 ❄️', prompt: 'The AC in classroom B-204 is not cooling and blowing warm air.' },
  { label: 'Water leak in Hostel B 🚿', prompt: 'There is a major water pipe leak near the Hostel B staircase.' },
  { label: 'Track GH-2026-1035 🔍', prompt: 'Track GH-2026-1035' },
  { label: 'Mess dinner timings ❓', prompt: 'What are the hostel mess timings?' },
  { label: 'Electric spark in Lab ⚡', prompt: 'Active electric sparking from switch board in Physics Lab 101!' },
];

export default function WhatsAppChat({ onTrackComplaint }) {
  const [sessionId, setSessionId] = useState(() => 'sess_' + Math.random().toString(36).substring(2, 9));
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'ai',
      content: "Hi! 👋 I'm **Gehor AI**.\n\nI can help you report and track campus issues like Wi-Fi outages, hostel maintenance, mess food grievances, or electrical repairs.\n\nWhat happened?",
      message_type: 'text',
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentDraft, setCurrentDraft] = useState(null);
  const [evidenceUrl, setEvidenceUrl] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [activeSessionTab, setActiveSessionTab] = useState('current');
  const [searchFilter, setSearchFilter] = useState('');

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Handle sending a message
  const handleSend = async (customText = null) => {
    const textToSend = customText || inputText;
    if (!textToSend.trim() && !evidenceUrl) return;

    const userMsg = {
      id: 'usr_' + Date.now(),
      sender: 'student',
      content: textToSend,
      message_type: evidenceUrl ? 'image' : 'text',
      metadata: evidenceUrl ? { evidence_url: evidenceUrl } : null,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMsg]);
    setInputText('');
    const tempEvidence = evidenceUrl;
    setEvidenceUrl(null);
    setIsTyping(true);

    try {
      const response = await sendMessage(sessionId, textToSend, tempEvidence);

      // Check if complaint was submitted -> trigger celebration
      if (response.state === 'SUBMITTED' && response.complaint_id) {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 }
        });
      }

      if (response.draft_complaint) {
        setCurrentDraft(response.draft_complaint);
      }

      const aiMsg = {
        id: 'ai_' + Date.now(),
        sender: 'ai',
        content: response.reply,
        message_type: response.message_type,
        metadata: response.draft_complaint || { complaint_id: response.complaint_id },
        timestamp: new Date().toISOString(),
        quick_options: response.quick_options
      };

      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      const errorMsg = {
        id: 'err_' + Date.now(),
        sender: 'ai',
        content: "⚠️ We encountered a network hiccup communicating with the campus server. Please try again.",
        message_type: 'text',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  // Human confirmation trigger
  const handleConfirmSubmission = () => {
    handleSend("Yes, submit complaint");
  };

  // Edit details trigger
  const handleEditDetails = () => {
    handleSend("Edit details");
  };

  // Start fresh conversation
  const handleStartNewComplaint = async () => {
    try {
      if (sessionId) {
        await resetSession(sessionId);
      }
    } catch (e) {
      // Ignore reset failure if session was new
    }
    const newSess = 'sess_' + Math.random().toString(36).substring(2, 9);
    setSessionId(newSess);
    setCurrentDraft(null);
    setEvidenceUrl(null);
    setMessages([
      {
        id: 'welcome_' + Date.now(),
        sender: 'ai',
        content: "Hi! 👋 What new campus issue would you like to report?",
        message_type: 'text',
        timestamp: new Date().toISOString()
      }
    ]);
  };

  // File evidence upload
  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const result = await uploadEvidenceFile(file);
      setEvidenceUrl(result.url);
    } catch (err) {
      alert("Failed to upload image. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  // Render message bubble content
  const renderMessageContent = (msg) => {
    return (
      <div className="space-y-1.5">
        {/* If image attachment is present */}
        {msg.metadata?.evidence_url && (
          <div className="mb-2 rounded-lg overflow-hidden border border-black/10 max-w-xs">
            <img 
              src={msg.metadata.evidence_url} 
              alt="Evidence attached" 
              className="w-full h-40 object-cover hover:scale-105 transition-transform" 
            />
          </div>
        )}

        {/* Text paragraph */}
        <p className="whitespace-pre-line text-sm text-gray-800 dark:text-slate-200 leading-relaxed">
          {msg.content}
        </p>

        {/* Structured Confirmation Card */}
        {msg.message_type === 'confirmation_card' && msg.metadata && (
          <ConfirmationCard 
            data={msg.metadata} 
            onConfirm={handleConfirmSubmission} 
            onEdit={handleEditDetails} 
            isSubmitting={isTyping}
          />
        )}

        {/* Complaint Submitted Success Card */}
        {msg.message_type === 'complaint_submitted' && msg.metadata?.complaint_id && (
          <div className="mt-2 bg-emerald-50 dark:bg-slate-800 rounded-xl border border-emerald-200 dark:border-slate-700 p-3.5 flex items-center justify-between gap-3">
            <div>
              <span className="text-[10px] uppercase font-bold text-emerald-700 dark:text-emerald-400 tracking-wider">
                COMPLAINT REGISTERED
              </span>
              <p className="text-base font-extrabold text-emerald-950 dark:text-slate-100 font-mono">
                {msg.metadata.complaint_id}
              </p>
            </div>
            {onTrackComplaint && (
              <button
                onClick={() => onTrackComplaint(msg.metadata.complaint_id)}
                className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center gap-1 shadow-sm transition-colors"
              >
                <span>Track Live</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-full max-w-5xl mx-auto bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-gray-200/90 dark:border-slate-800 overflow-hidden flex h-[780px]">
      
      {/* ----------------- LEFT SIDEBAR (WhatsApp Desktop style) ----------------- */}
      <div className="w-80 border-r border-gray-200 dark:border-slate-800 bg-gray-50 dark:bg-slate-900 flex flex-col hidden sm:flex shrink-0">
        
        {/* User bar */}
        <div className="h-16 px-4 bg-gray-100/90 dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-emerald-700 text-white font-bold flex items-center justify-center text-sm shadow-inner">
              ST
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-900 dark:text-slate-200 leading-tight">Student Demo</h4>
              <p className="text-[11px] text-gray-500 dark:text-slate-400">STU-2026-901</p>
            </div>
          </div>
          <button
            onClick={handleStartNewComplaint}
            title="Start New Complaint"
            className="p-2 hover:bg-gray-200 dark:hover:bg-slate-700 rounded-full text-emerald-700 dark:text-emerald-400 transition-colors"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>

        {/* Search Bar */}
        <div className="p-3 border-b border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900">
          <div className="relative">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search past complaints..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-gray-100 dark:bg-slate-800 dark:text-slate-200 dark:placeholder-slate-500 rounded-lg focus:outline-none focus:ring-1 focus:ring-emerald-500 border border-transparent dark:border-slate-700"
            />
          </div>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto divide-y divide-gray-100 dark:divide-slate-800">
          
          {/* Active Gehor Assistant thread */}
          <div 
            onClick={() => setActiveSessionTab('current')}
            className={`p-3.5 flex items-start gap-3 cursor-pointer transition-colors ${
              activeSessionTab === 'current' ? 'bg-emerald-50/70 dark:bg-slate-800/80 border-l-4 border-emerald-600 dark:border-emerald-500' : 'hover:bg-gray-100/80 dark:hover:bg-slate-800/50'
            }`}
          >
            <div className="relative shrink-0">
              <div className="w-11 h-11 rounded-full bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-sm">
                <Bot className="w-6 h-6" />
              </div>
              <span className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-500 border-2 border-white rounded-full"></span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-900 dark:text-slate-200 truncate">Gehor AI Desk</span>
                <span className="text-[10px] text-emerald-700 dark:text-emerald-400 font-semibold">Just now</span>
              </div>
              <p className="text-[11px] text-gray-500 dark:text-slate-400 truncate mt-0.5">
                {messages[messages.length - 1]?.content.slice(0, 32)}...
              </p>
              <div className="flex items-center gap-1 mt-1">
                <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 dark:bg-slate-800 dark:text-emerald-400 dark:border dark:border-emerald-600/30 font-semibold">
                  Active Intake
                </span>
              </div>
            </div>
          </div>

          {/* Seed demo threads */}
          {[
            { id: 'GH-2026-1035', issue: 'Wi-Fi outage in Block B', status: 'IN_PROGRESS', time: '5h ago' },
            { id: 'GH-2026-1036', issue: 'Main water pipe leak', status: 'ASSIGNED', time: '2h ago' },
            { id: 'GH-2026-1038', issue: 'Sparking in Chem Lab', status: 'CRITICAL', time: '50m ago' },
            { id: 'GH-2026-1037', issue: 'Mess food quality report', status: 'RESOLVED', time: 'Yesterday' },
          ]
          .filter(t => !searchFilter || t.issue.toLowerCase().includes(searchFilter.toLowerCase()) || t.id.toLowerCase().includes(searchFilter.toLowerCase()))
          .map((thread) => (
            <div
              key={thread.id}
              onClick={() => onTrackComplaint ? onTrackComplaint(thread.id) : handleSend(`Track ${thread.id}`)}
              className="p-3.5 flex items-start gap-3 cursor-pointer hover:bg-gray-100/70 dark:hover:bg-slate-800/50 transition-colors"
            >
              <div className="w-11 h-11 rounded-full bg-gray-200 dark:bg-slate-800 text-gray-600 dark:text-slate-300 font-bold flex items-center justify-center text-xs shrink-0">
                GH
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-800 dark:text-slate-200 truncate">{thread.id}</span>
                  <span className="text-[10px] text-gray-400 dark:text-slate-500">{thread.time}</span>
                </div>
                <p className="text-[11px] text-gray-600 dark:text-slate-400 truncate mt-0.5">{thread.issue}</p>
                <div className="mt-1">
                  <StatusBadge status={thread.status} />
                </div>
              </div>
            </div>
          ))}

        </div>

        {/* Start New Ticket Bar */}
        <div className="p-3 border-t border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <button
            onClick={handleStartNewComplaint}
            className="w-full py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-sm transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>New Complaint Thread</span>
          </button>
        </div>

      </div>

      {/* ----------------- RIGHT CHAT AREA (WhatsApp Web chat pane) ----------------- */}
      <div className="flex-1 flex flex-col bg-[#efeae2] dark:bg-slate-900 relative min-w-0">
        
        {/* Chat Header */}
        <div className="h-16 px-4 bg-gray-100/95 dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700 flex items-center justify-between shrink-0 shadow-sm z-10">
          <div className="flex items-center gap-3 min-w-0">
            <div className="relative shrink-0">
              <div className="w-10 h-10 rounded-full bg-emerald-600 text-white flex items-center justify-center shadow-md">
                <Bot className="w-5 h-5" />
              </div>
              <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-500 border-2 border-white dark:border-slate-800 rounded-full"></span>
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1.5">
                <h3 className="text-sm font-bold text-gray-900 dark:text-slate-100 truncate">Gehor AI Official</h3>
                <ShieldCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
              </div>
              <p className="text-[11px] text-emerald-700 dark:text-emerald-400 font-medium truncate flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 dark:bg-emerald-400"></span>
                <span>online • typical reply: instant</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1 sm:gap-2 text-gray-600 dark:text-slate-300">
            <button 
              onClick={() => alert("Simulated WhatsApp Audio: Campus Helpline 108")}
              title="Voice Call (Simulated)"
              className="p-2 hover:bg-gray-200 dark:hover:bg-slate-700 rounded-full transition-colors text-gray-600 dark:text-slate-300"
            >
              <Phone className="w-4 h-4" />
            </button>
            <button 
              onClick={() => alert("Simulated Video Inspection link")}
              title="Video Call (Simulated)"
              className="p-2 hover:bg-gray-200 dark:hover:bg-slate-700 rounded-full transition-colors text-gray-600 dark:text-slate-300"
            >
              <Video className="w-4 h-4" />
            </button>
            <div className="h-5 w-px bg-gray-300 dark:bg-slate-700 mx-1"></div>
            <button
              onClick={handleStartNewComplaint}
              title="Reset Chat Session"
              className="px-2.5 py-1 text-xs font-semibold bg-gray-200 hover:bg-gray-300 text-gray-800 dark:bg-slate-700 dark:hover:bg-slate-600 dark:text-slate-200 rounded-lg transition-colors"
            >
              Clear Chat
            </button>
          </div>
        </div>

        {/* Message Feed Container */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 wa-chat-pattern">
          
          {/* Day Divider Badge */}
          <div className="flex justify-center my-2">
            <span className="px-3 py-1 rounded-lg bg-white/80 dark:bg-slate-800/90 shadow-sm text-[11px] font-semibold text-gray-600 dark:text-slate-300 dark:border dark:border-slate-700 uppercase tracking-wider backdrop-blur-sm">
              Today
            </span>
          </div>

          {/* End-to-End Encryption Notice */}
          <div className="flex justify-center my-2">
            <div className="max-w-md text-center bg-amber-50/90 dark:bg-amber-950/40 border border-amber-200/60 dark:border-amber-800/50 rounded-xl p-2.5 text-[11px] text-amber-800 dark:text-amber-300 shadow-sm">
              🔒 Messages are processed in real-time by Gehor AI agent. Critical hazards trigger instant institutional escalation.
            </div>
          </div>

          {/* Messages */}
          {messages.map((msg) => {
            const isUser = msg.sender === 'student';
            return (
              <div
                key={msg.id}
                className={`flex ${isUser ? 'justify-end' : 'justify-start'} transition-all`}
              >
                <div
                  className={`max-w-[85%] sm:max-w-[70%] rounded-2xl px-4 py-2.5 shadow-sm text-sm relative ${
                    isUser
                      ? 'bg-[#d9fdd3] dark:bg-emerald-950 text-gray-900 dark:text-slate-100 rounded-tr-none dark:border dark:border-emerald-700/40'
                      : 'bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-200 rounded-tl-none border border-gray-100 dark:border-slate-700'
                  }`}
                >
                  {renderMessageContent(msg)}

                  {/* Timestamp & double ticks */}
                  <div className="flex items-center justify-end gap-1 mt-1 text-[10px] text-gray-500 dark:text-slate-400">
                    <span>
                      {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    {isUser && <CheckCheck className="w-3.5 h-3.5 text-blue-500 dark:text-sky-400" />}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Live Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white dark:bg-slate-800 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm border border-gray-100 dark:border-slate-700 flex items-center gap-2">
                <span className="text-xs text-gray-500 dark:text-slate-400 font-medium">Gehor AI is typing</span>
                <div className="flex gap-1 items-center">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* ----------------- QUICK SUGGESTIONS CHIPS ----------------- */}
        <div className="px-3 py-2 bg-gray-100/90 dark:bg-slate-800 border-t border-gray-200 dark:border-slate-700 overflow-x-auto flex items-center gap-2 no-scrollbar">
          <span className="text-[10px] font-bold text-gray-400 dark:text-slate-400 uppercase tracking-wider shrink-0">
            Suggested:
          </span>
          {QUICK_SUGGESTIONS.map((item, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(item.prompt)}
              className="shrink-0 text-xs bg-white hover:bg-emerald-50 text-gray-700 hover:text-emerald-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:text-emerald-300 dark:hover:bg-slate-850 dark:border-slate-700 font-medium px-2.5 py-1 rounded-full border border-gray-200/90 hover:border-emerald-300 dark:hover:border-emerald-600/50 shadow-2xs transition-all active:scale-95"
            >
              {item.label}
            </button>
          ))}
        </div>

        {/* Evidence attachment preview bar if user attached file */}
        {evidenceUrl && (
          <div className="px-4 py-2 bg-emerald-50 dark:bg-slate-800/90 border-t border-emerald-200 dark:border-slate-700 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ImageIcon className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span className="text-xs text-emerald-900 dark:text-emerald-400 font-medium">Evidence attached</span>
              <img src={evidenceUrl} alt="Thumbnail" className="w-6 h-6 object-cover rounded border dark:border-slate-700" />
            </div>
            <button
              onClick={() => setEvidenceUrl(null)}
              className="text-gray-400 hover:text-red-500 dark:hover:text-red-400 p-1"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* ----------------- CHAT INPUT FOOTER ----------------- */}
        <div className="p-3 bg-gray-100 dark:bg-slate-800 border-t border-gray-200 dark:border-slate-700 flex items-center gap-2 shrink-0">
          
          {/* Emoji button */}
          <button 
            type="button" 
            title="Emoji"
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-200 dark:text-slate-400 dark:hover:text-slate-200 dark:hover:bg-slate-700 rounded-full transition-colors"
          >
            <Smile className="w-5 h-5" />
          </button>

          {/* Paperclip Attachment button */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept="image/*,.pdf"
            className="hidden"
          />
          <button
            type="button"
            title="Attach Evidence Photo"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="p-2 text-gray-500 hover:text-emerald-700 hover:bg-gray-200 dark:text-slate-400 dark:hover:text-emerald-400 dark:hover:bg-slate-700 rounded-full transition-colors relative"
          >
            <Paperclip className="w-5 h-5" />
            {isUploading && (
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            )}
          </button>

          {/* Text Input */}
          <div className="flex-1">
            <input
              type="text"
              placeholder="Describe your issue naturally (e.g., No Wi-Fi in Block C)..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              className="w-full bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 border border-gray-200 dark:border-slate-700 shadow-2xs placeholder:text-gray-400 dark:placeholder:text-slate-500"
            />
          </div>

          {/* Send / Mic button */}
          {inputText.trim() || evidenceUrl ? (
            <button
              onClick={() => handleSend()}
              className="p-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-md transition-all active:scale-95"
            >
              <Send className="w-5 h-5" />
            </button>
          ) : (
            <button
              type="button"
              onClick={() => handleSend("Microphone voice note: The AC in classroom B-204 is broken.")}
              title="Voice Message (Simulated)"
              className="p-2 text-gray-500 hover:text-emerald-700 hover:bg-gray-200 dark:text-slate-400 dark:hover:text-emerald-400 dark:hover:bg-slate-700 rounded-full transition-colors"
            >
              <Mic className="w-5 h-5" />
            </button>
          )}

        </div>

      </div>

    </div>
  );
}
