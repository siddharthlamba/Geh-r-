import React from 'react';
import { MapPin, Tag, Building2, Check, Edit3, ShieldAlert, Sparkles } from 'lucide-react';
import SeverityBadge from './SeverityBadge';

export default function ConfirmationCard({ data, onConfirm, onEdit, isSubmitting = false }) {
  if (!data) return null;

  return (
    <div className="mt-2 bg-gradient-to-br from-white to-gray-50 rounded-xl border-2 border-emerald-500/30 p-4 shadow-md max-w-md dark:from-slate-800 dark:to-slate-900 dark:border-emerald-600/30 dark:shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-slate-700 mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded-md bg-emerald-100 text-emerald-700 dark:bg-slate-800 dark:text-emerald-400 dark:border dark:border-emerald-500/30">
            <Sparkles className="w-4 h-4" />
          </div>
          <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-400">
            AI Structured Summary
          </span>
        </div>
        <SeverityBadge severity={data.severity} />
      </div>

      {/* Summary Fields */}
      <div className="space-y-2.5 text-xs text-gray-700 dark:text-slate-300">
        <div>
          <span className="text-gray-400 font-medium">Issue Description:</span>
          <p className="font-semibold text-gray-900 dark:text-slate-200 mt-0.5 line-clamp-2">
            {data.description || data.title}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-2 pt-1">
          <div className="flex items-start gap-1.5 bg-gray-50 dark:bg-slate-800/80 p-2 rounded-lg border border-gray-100 dark:border-slate-700">
            <MapPin className="w-3.5 h-3.5 text-rose-500 mt-0.5 shrink-0" />
            <div>
              <span className="text-[10px] text-gray-400 block font-medium">LOCATION</span>
              <span className="font-semibold text-gray-800 dark:text-slate-200">{data.location || 'Campus'}</span>
            </div>
          </div>

          <div className="flex items-start gap-1.5 bg-gray-50 dark:bg-slate-800/80 p-2 rounded-lg border border-gray-100 dark:border-slate-700">
            <Tag className="w-3.5 h-3.5 text-indigo-500 mt-0.5 shrink-0" />
            <div>
              <span className="text-[10px] text-gray-400 block font-medium">CATEGORY</span>
              <span className="font-semibold text-gray-800 dark:text-slate-200">{data.category}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-emerald-50/70 dark:bg-slate-800/80 p-2 rounded-lg border border-emerald-100/80 dark:border-slate-700">
          <Building2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <div>
            <span className="text-[10px] text-emerald-700 dark:text-emerald-400 block font-medium uppercase">Target Department</span>
            <span className="font-bold text-emerald-950 dark:text-slate-200">{data.department || 'Maintenance'}</span>
          </div>
        </div>

        {data.verified_email && (
          <div className="flex items-center gap-2 bg-blue-50/80 dark:bg-slate-800/80 p-2 rounded-lg border border-blue-200/80 dark:border-slate-700">
            <span className="text-blue-600 dark:text-blue-400 font-bold text-xs">📧</span>
            <div className="min-w-0">
              <span className="text-[10px] text-blue-700 dark:text-blue-400 block font-medium uppercase">Verified Institutional Email</span>
              <span className="font-mono font-bold text-blue-950 dark:text-slate-200 truncate block">{data.verified_email}</span>
            </div>
          </div>
        )}

        {data.severity_reasoning && (
          <p className="text-[11px] text-gray-500 dark:text-slate-300 italic bg-gray-100/60 dark:bg-slate-800/80 p-2 rounded border border-gray-200/50 dark:border-slate-700">
            💡 {data.severity_reasoning}
          </p>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-4 pt-3 border-t border-gray-100 dark:border-slate-700 flex items-center gap-2">
        <button
          onClick={onConfirm}
          disabled={isSubmitting}
          className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white dark:bg-emerald-600 dark:text-white dark:hover:bg-emerald-700 dark:shadow-sm font-semibold py-2 px-3 rounded-lg text-xs flex items-center justify-center gap-1.5 shadow-sm transition-colors disabled:opacity-50"
        >
          <Check className="w-4 h-4" />
          <span>{isSubmitting ? 'Submitting...' : 'Confirm & Submit'}</span>
        </button>

        <button
          onClick={onEdit}
          disabled={isSubmitting}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 dark:bg-slate-800 dark:text-slate-300 dark:border dark:border-slate-700 dark:hover:bg-slate-700 font-medium py-2 px-3 rounded-lg text-xs flex items-center justify-center gap-1.5 transition-colors"
        >
          <Edit3 className="w-3.5 h-3.5" />
          <span>Edit Details</span>
        </button>
      </div>
    </div>
  );
}
