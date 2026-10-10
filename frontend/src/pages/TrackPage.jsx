import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { Search, MapPin, Tag, Building2, Clock, User, ArrowLeft, MessageSquare, AlertCircle } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import SeverityBadge from '../components/SeverityBadge';
import TimelineView from '../components/TimelineView';
import { getComplaintById, getComplaintEvents } from '../api';

const QUICK_DEMO_IDS = ['GH-2026-1035', 'GH-2026-1036', 'GH-2026-1038', 'GH-2026-1037'];

export default function TrackPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const initialId = searchParams.get('id') || 'GH-2026-1035';

  const [searchId, setSearchId] = useState(initialId);
  const [complaint, setComplaint] = useState(null);
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchComplaint = async (id) => {
    if (!id.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getComplaintById(id.trim());
      setComplaint(data);
      const evs = await getComplaintEvents(data.id);
      setEvents(evs);
      setSearchParams({ id: data.id });
    } catch (err) {
      setComplaint(null);
      setError(`Complaint with ID "${id}" could not be found. Please check the ID and try again.`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (initialId) {
      fetchComplaint(initialId);
    }
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchComplaint(searchId);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-extrabold text-gray-900 dark:text-slate-200 tracking-tight">
            Track Complaint Status
          </h1>
          <p className="text-sm text-gray-600 dark:text-slate-400">
            Enter your unique Complaint ID (GH-2026-XXXX) to view real-time investigation progress and technician assignment.
          </p>
        </div>

        {/* Search Input Box */}
        <div className="bg-white dark:bg-slate-800 p-4 rounded-2xl shadow-md border border-gray-200 dark:border-slate-700">
          <form onSubmit={handleSearchSubmit} className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-5 h-5 text-gray-400 absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="Enter Complaint ID (e.g. GH-2026-1042)..."
                value={searchId}
                onChange={(e) => setSearchId(e.target.value)}
                className="w-full pl-11 pr-4 py-2.5 text-sm font-mono uppercase bg-gray-50 dark:bg-slate-900 dark:text-slate-200 rounded-xl border border-gray-300 dark:border-slate-700 focus:bg-white dark:focus:bg-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white dark:bg-emerald-600 dark:text-white dark:hover:bg-emerald-700 font-bold text-sm rounded-xl shadow-sm transition-colors disabled:opacity-50"
            >
              {isLoading ? 'Checking...' : 'Track'}
            </button>
          </form>

          {/* Quick Demo Chips */}
          <div className="mt-3 flex items-center gap-2 overflow-x-auto text-xs text-gray-500">
            <span className="font-semibold uppercase tracking-wider text-[10px] text-gray-400 shrink-0">
              Try Demo Tickets:
            </span>
            {QUICK_DEMO_IDS.map((demoId) => (
              <button
                key={demoId}
                onClick={() => {
                  setSearchId(demoId);
                  fetchComplaint(demoId);
                }}
                className="font-mono font-medium px-2.5 py-1 rounded-md bg-gray-100 hover:bg-emerald-50 hover:text-emerald-800 border border-gray-200 transition-colors"
              >
                {demoId}
              </button>
            ))}
          </div>
        </div>

        {/* Error notification */}
        {error && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* Complaint Result Card */}
        {complaint && (
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden divide-y divide-gray-100 animate-in fade-in duration-300">
            
            {/* Top Bar */}
            <div className="p-6 bg-gray-50/70 flex flex-wrap items-center justify-between gap-4">
              <div>
                <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">
                  Complaint Tracking File
                </span>
                <h2 className="text-2xl font-extrabold text-gray-900 font-mono mt-0.5">
                  {complaint.id}
                </h2>
              </div>
              <div className="flex items-center gap-2">
                <StatusBadge status={complaint.status} className="text-sm py-1 px-3" />
                <SeverityBadge severity={complaint.severity} className="text-sm py-1 px-3" />
              </div>
            </div>

            {/* Core Issue Body */}
            <div className="p-6 space-y-4">
              <h3 className="text-lg font-bold text-gray-900">
                {complaint.title}
              </h3>
              <p className="text-sm text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-xl border border-gray-100">
                {complaint.description}
              </p>

              {complaint.evidence_url && (
                <div>
                  <span className="text-xs font-semibold text-gray-500 uppercase block mb-1.5">
                    Attached Evidence Photo:
                  </span>
                  <img
                    src={complaint.evidence_url}
                    alt="Uploaded Evidence"
                    className="h-44 rounded-xl object-cover border"
                  />
                </div>
              )}

              {/* 3-Column Info Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                <div className="p-3 rounded-xl bg-gray-50 border border-gray-200/80">
                  <div className="flex items-center gap-1.5 text-xs text-gray-400 font-medium mb-1">
                    <MapPin className="w-3.5 h-3.5 text-rose-500" />
                    <span>LOCATION</span>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">{complaint.location}</p>
                </div>

                <div className="p-3 rounded-xl bg-gray-50 border border-gray-200/80">
                  <div className="flex items-center gap-1.5 text-xs text-gray-400 font-medium mb-1">
                    <Building2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>DEPARTMENT</span>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">{complaint.department_name}</p>
                </div>

                <div className="p-3 rounded-xl bg-gray-50 border border-gray-200/80">
                  <div className="flex items-center gap-1.5 text-xs text-gray-400 font-medium mb-1">
                    <User className="w-3.5 h-3.5 text-blue-600" />
                    <span>ASSIGNED STAFF</span>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">
                    {complaint.assigned_to || 'Pending allocation'}
                  </p>
                </div>
              </div>
            </div>

            {/* Live Visual Timeline Stepper */}
            <div className="p-6">
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">
                Redressal Timeline & Investigation Log
              </h4>
              <TimelineView currentStatus={complaint.status} events={events} createdAt={complaint.created_at} />
            </div>

            {/* Bottom Actions */}
            <div className="p-4 bg-gray-50 flex items-center justify-between">
              <span className="text-xs text-gray-500">
                Last updated: {new Date(complaint.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              <Link
                to="/report"
                className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 flex items-center gap-1"
              >
                <MessageSquare className="w-3.5 h-3.5" />
                <span>Chat with AI regarding this issue</span>
              </Link>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
