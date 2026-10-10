import React, { useState, useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('gehor-theme');
      if (saved) return saved === 'dark';
      return false; // Default to Light Mode
    }
    return false;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      localStorage.setItem('gehor-theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('gehor-theme', 'light');
    }
  }, [isDark]);

  const toggleTheme = () => {
    setIsDark((prev) => !prev);
  };

  return (
    <div className="flex items-center">
      <button
        type="button"
        onClick={toggleTheme}
        aria-label={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
        title={isDark ? "Dark Mode - Click for Light" : "Light Mode - Click for Dark"}
        className="relative inline-flex items-center w-14 h-7 rounded-full p-0.5 cursor-pointer select-none transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 bg-gray-200 border border-gray-300 dark:bg-slate-800 dark:border-slate-700"
      >
        {/* Slider Thumb / Knob with minimal monochrome icon */}
        <div
          className={`w-5.5 h-5.5 rounded-full flex items-center justify-center transition-transform duration-300 ease-in-out ${
            isDark
              ? 'translate-x-7 bg-slate-900 text-emerald-400 border border-slate-700 shadow-sm'
              : 'translate-x-0.5 bg-white text-gray-800 shadow-sm border border-gray-200'
          }`}
        >
          {isDark ? (
            <Moon className="w-3 h-3 stroke-[2.2]" />
          ) : (
            <Sun className="w-3 h-3 stroke-[2.2]" />
          )}
        </div>
      </button>
    </div>
  );
}
