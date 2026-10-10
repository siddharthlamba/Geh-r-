import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, KeyRound, Mail, ArrowRight, Sparkles } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('admin@campus.edu');
  const [password, setPassword] = useState('admin123');

  const handleLogin = (e) => {
    e.preventDefault();
    localStorage.setItem('gehor_admin_auth', 'true');
    navigate('/admin');
  };

  const handleQuickDemoLogin = () => {
    setEmail('admin@campus.edu');
    setPassword('admin123');
    localStorage.setItem('gehor_admin_auth', 'true');
    navigate('/admin');
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-gray-900 via-gray-800 to-emerald-950 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl p-8 border border-white/20 space-y-6">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-purple-600 text-white flex items-center justify-center mx-auto shadow-md">
            <Shield className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">
            Administrative Portal
          </h2>
          <p className="text-xs text-gray-500">
            Institutional complaint triage, department routing, and SLA oversight
          </p>
        </div>

        {/* Demo Credentials Quick Box */}
        <div className="p-3 bg-purple-50 rounded-xl border border-purple-200 text-xs text-purple-900 flex items-center justify-between">
          <div>
            <span className="font-bold block">1-Click Hackathon Access:</span>
            <span className="text-[11px] text-purple-700">admin@campus.edu / admin123</span>
          </div>
          <button
            type="button"
            onClick={handleQuickDemoLogin}
            className="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white font-semibold text-xs rounded-lg transition-colors shadow-2xs"
          >
            Quick Demo Fill
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">
              Admin Email
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">
              Password
            </label>
            <div className="relative">
              <KeyRound className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-2.5 bg-gray-900 hover:bg-gray-800 text-white font-bold text-sm rounded-xl shadow-md transition-all flex items-center justify-center gap-2"
          >
            <span>Sign In to Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

      </div>
    </div>
  );
}
