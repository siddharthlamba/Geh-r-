import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import ReportPage from './pages/ReportPage';
import TrackPage from './pages/TrackPage';
import LoginPage from './pages/LoginPage';
import AdminDashboard from './pages/AdminDashboard';
import AdminComplaints from './pages/AdminComplaints';
import AdminAnalytics from './pages/AdminAnalytics';
import AdminSettings from './pages/AdminSettings';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex flex-col font-sans transition-colors duration-200">
        <Navbar />
        <main className="flex-1 flex flex-col">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/report" element={<ReportPage />} />
            <Route path="/track" element={<TrackPage />} />
            <Route path="/login" element={<LoginPage />} />
            
            {/* Admin Routes */}
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/complaints" element={<AdminComplaints />} />
            <Route path="/admin/analytics" element={<AdminAnalytics />} />
            <Route path="/admin/settings" element={<AdminSettings />} />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
