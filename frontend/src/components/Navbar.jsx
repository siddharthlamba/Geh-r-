import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { MessageSquare, Search, LayoutDashboard, Shield, Sparkles, Activity } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

export default function Navbar() {
  const location = useLocation();
  const [isAdminMode, setIsAdminMode] = useState(location.pathname.startsWith('/admin'));

  useEffect(() => {
    setIsAdminMode(location.pathname.startsWith('/admin'));
  }, [location.pathname]);

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-gray-200 dark:bg-slate-900/95 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-md shadow-emerald-600/20 group-hover:scale-105 transition-transform">
            <span className="text-xl font-extrabold tracking-tight">G</span>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-lg font-bold tracking-tight text-gray-900 group-hover:text-emerald-700 transition-colors dark:text-slate-200 dark:group-hover:text-emerald-400">
                Gehör
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-emerald-100 text-emerald-800 rounded dark:bg-slate-800 dark:text-emerald-400 dark:border dark:border-emerald-500/30">
                AI MVP
              </span>
            </div>
            <p className="text-[11px] text-gray-500 font-medium tracking-wide dark:text-slate-400">
              A hearing, being heard. ✧
            </p>
          </div>
        </Link>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1 bg-gray-100/80 p-1 rounded-xl border border-gray-200/80 text-sm font-medium dark:bg-slate-800/80 dark:border-slate-700">
          <Link
            to="/report"
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg transition-all ${
              isActive('/report')
                ? 'bg-white text-emerald-700 shadow-sm font-semibold dark:bg-slate-900 dark:text-emerald-400 dark:border dark:border-slate-700'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200/50 dark:text-slate-400 dark:hover:text-emerald-400 dark:hover:bg-slate-800'
            }`}
          >
            <MessageSquare className="w-4 h-4 text-emerald-600" />
            <span>WhatsApp Chat</span>
          </Link>

          <Link
            to="/track"
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg transition-all ${
              isActive('/track')
                ? 'bg-white text-emerald-700 shadow-sm font-semibold dark:bg-slate-900 dark:text-sky-400 dark:border dark:border-slate-700'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200/50 dark:text-slate-400 dark:hover:text-sky-400 dark:hover:bg-slate-800'
            }`}
          >
            <Search className="w-4 h-4 text-blue-600" />
            <span>Track Status</span>
          </Link>

          <Link
            to="/admin"
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg transition-all ${
              isActive('/admin')
                ? 'bg-white text-emerald-700 shadow-sm font-semibold dark:bg-slate-900 dark:text-indigo-400 dark:border dark:border-slate-700'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200/50 dark:text-slate-400 dark:hover:text-indigo-400 dark:hover:bg-slate-800'
            }`}
          >
            <LayoutDashboard className="w-4 h-4 text-purple-600" />
            <span>Admin Portal</span>
          </Link>
        </nav>

        {/* Status / Mode Switcher Pill */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 dark:bg-slate-800 dark:border-slate-700 dark:text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping dark:bg-emerald-400"></span>
            <span className="font-medium">System Online</span>
          </div>

          <Link
            to={isAdminMode ? "/report" : "/admin"}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm ${
              isAdminMode
                ? 'bg-emerald-600 text-white hover:bg-emerald-700 dark:bg-emerald-600 dark:text-white dark:hover:bg-emerald-700'
                : 'bg-gray-900 text-white hover:bg-gray-800 dark:bg-slate-800 dark:text-slate-200 dark:border dark:border-slate-700 dark:hover:bg-slate-700'
            }`}
          >
            {isAdminMode ? (
              <>
                <MessageSquare className="w-3.5 h-3.5" />
                <span>Switch to Student</span>
              </>
            ) : (
              <>
                <Shield className="w-3.5 h-3.5" />
                <span>Admin Login</span>
              </>
            )}
          </Link>

          <div className="h-5 w-px bg-gray-200 dark:bg-slate-700 mx-0.5"></div>

          {/* Theme Switcher Toggle (Top Right) */}
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
