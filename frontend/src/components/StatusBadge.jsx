import React from 'react';
import { Clock, CheckCircle2, UserCheck, PlayCircle, XCircle, Archive } from 'lucide-react';

export default function StatusBadge({ status, className = '' }) {
  const st = (status || 'SUBMITTED').toUpperCase();

  switch (st) {
    case 'SUBMITTED':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-50 text-purple-700 border border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:border-purple-800/60 ${className}`}>
          <Clock className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
          Submitted
        </span>
      );
    case 'CLASSIFIED':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-800/60 ${className}`}>
          <Clock className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
          Classified
        </span>
      );
    case 'ASSIGNED':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 dark:bg-blue-950/40 dark:text-sky-300 dark:border-blue-800/60 ${className}`}>
          <UserCheck className="w-3.5 h-3.5 text-blue-600 dark:text-sky-400" />
          Assigned
        </span>
      );
    case 'IN_PROGRESS':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800/60 ${className}`}>
          <PlayCircle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 animate-spin" style={{ animationDuration: '4s' }} />
          In Progress
        </span>
      );
    case 'RESOLVED':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/60 ${className}`}>
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
          Resolved
        </span>
      );
    case 'CLOSED':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 border border-gray-300 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700 ${className}`}>
          <Archive className="w-3.5 h-3.5 text-gray-500 dark:text-slate-400" />
          Closed
        </span>
      );
    case 'REJECTED':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800/60 ${className}`}>
          <XCircle className="w-3.5 h-3.5 text-red-600 dark:text-red-400" />
          Rejected
        </span>
      );
    default:
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 border border-gray-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700 ${className}`}>
          {status}
        </span>
      );
  }
}
