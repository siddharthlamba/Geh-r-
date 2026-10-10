import React from 'react';
import { AlertTriangle, AlertCircle, Info, ShieldAlert } from 'lucide-react';

export default function SeverityBadge({ severity, className = '' }) {
  const sev = (severity || 'MEDIUM').toUpperCase();

  switch (sev) {
    case 'CRITICAL':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-100 text-red-800 border border-red-300 animate-critical shadow-sm dark:bg-red-950/40 dark:text-red-300 dark:border-red-800/60 ${className}`}>
          <ShieldAlert className="w-3.5 h-3.5 text-red-600 animate-pulse dark:text-red-400" />
          CRITICAL
        </span>
      );
    case 'HIGH':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800/60 ${className}`}>
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
          HIGH
        </span>
      );
    case 'MEDIUM':
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-800/60 ${className}`}>
          <AlertCircle className="w-3.5 h-3.5 text-blue-600 dark:text-sky-400" />
          MEDIUM
        </span>
      );
    case 'LOW':
    default:
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/60 ${className}`}>
          <Info className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" />
          LOW
        </span>
      );
  }
}
