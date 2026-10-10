import React from 'react';
import { useNavigate } from 'react-router-dom';
import WhatsAppChat from '../components/WhatsAppChat';
import { MessageSquare, ArrowLeft, Shield, Info } from 'lucide-react';

export default function ReportPage() {
  const navigate = useNavigate();

  const handleTrackComplaint = (complaintId) => {
    navigate(`/track?id=${complaintId}`);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-b from-emerald-50/40 via-gray-100 to-gray-100 dark:from-slate-900 dark:via-slate-900 dark:to-slate-900 py-4 sm:py-6 px-2 sm:px-4 flex flex-col justify-center">
      <div className="max-w-5xl mx-auto w-full mb-3 px-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse dark:bg-emerald-400"></span>
          <h2 className="text-sm font-bold text-gray-800 dark:text-slate-200">
            WhatsApp Conversational Intake Desk
          </h2>
        </div>
        <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-slate-400 font-medium">
          <span className="hidden sm:inline">Type naturally or upload photo</span>
          <button
            onClick={() => navigate('/track')}
            className="text-emerald-700 hover:text-emerald-800 dark:text-emerald-400 dark:hover:text-emerald-300 font-semibold"
          >
            Track Existing ID →
          </button>
        </div>
      </div>

      <WhatsAppChat onTrackComplaint={handleTrackComplaint} />
    </div>
  );
}
