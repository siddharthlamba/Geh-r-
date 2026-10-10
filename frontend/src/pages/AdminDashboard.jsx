import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldAlert, Clock, PlayCircle, CheckCircle2, AlertTriangle, 
  BarChart3, RefreshCw, Filter, Search, ArrowUpRight, ChevronRight, 
  Settings, Users, Building2, Flame
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import SeverityBadge from '../components/SeverityBadge';
import ComplaintDetailModal from '../components/ComplaintDetailModal';
import { getDashboardStats, getDashboardCharts, getComplaints, updateComplaint } from '../api';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [charts, setCharts] = useState(null);
  const [recentComplaints, setRecentComplaints] = useState([]);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [filterSeverity, setFilterSeverity] = useState('ALL');

  const handleRowClick = async (item) => {
    let complaintToOpen = item;
    if (item.status === 'SUBMITTED') {
      try {
        const updated = await updateComplaint(item.id, {
          status: 'IN_PROGRESS',
          performed_by: 'Admin: Aditya Verma'
        });
        complaintToOpen = updated;
        setRecentComplaints((prev) => prev.map((c) => (c.id === item.id ? updated : c)));
        getDashboardStats().then(setStats).catch(console.error);
      } catch (err) {
        console.error('Failed to auto-transition status to IN_PROGRESS:', err);
      }
    }
    setSelectedComplaint(complaintToOpen);
  };

  const handleResolveComplaint = async (e, item) => {
    e.stopPropagation();
    try {
      const updated = await updateComplaint(item.id, {
        status: 'RESOLVED',
        performed_by: 'Admin: Aditya Verma'
      });
      setRecentComplaints((prev) => prev.map((c) => (c.id === item.id ? updated : c)));
      loadData();
    } catch (err) {
      alert('Failed to resolve complaint: ' + err.message);
    }
  };

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [s, c, list] = await Promise.all([
        getDashboardStats(),
        getDashboardCharts(),
        getComplaints({ limit: 10, severity: filterSeverity !== 'ALL' ? filterSeverity : null })
      ]);
      setStats(s);
      setCharts(c);
      setRecentComplaints(list);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filterSeverity]);

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Top Header & Navigation Sub-Tabs */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
                Institutional Redressal Control Center
              </h1>
              <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-emerald-100 text-emerald-800">
                Live
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Autonomous AI intake, category routing, emergency escalation, and staff dispatch
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Link
              to="/admin/complaints"
              className="px-3 py-2 bg-white hover:bg-gray-50 border border-gray-300 rounded-xl text-xs font-semibold text-gray-700 shadow-2xs transition-colors"
            >
              All Complaints Table
            </Link>
            <Link
              to="/admin/analytics"
              className="px-3 py-2 bg-white hover:bg-gray-50 border border-gray-300 rounded-xl text-xs font-semibold text-gray-700 shadow-2xs transition-colors"
            >
              Analytics
            </Link>
            <Link
              to="/admin/settings"
              className="px-3 py-2 bg-white hover:bg-gray-50 border border-gray-300 rounded-xl text-xs font-semibold text-gray-700 shadow-2xs transition-colors flex items-center gap-1"
            >
              <Settings className="w-3.5 h-3.5" />
              <span>Routing Rules</span>
            </Link>
            <button
              onClick={loadData}
              title="Refresh Dashboard"
              className="p-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-sm transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* ----------------- KPI CARDS ----------------- */}
        <div className="grid grid-cols-2 lg:grid-cols-6 gap-3 sm:gap-4">
          
          {/* Total */}
          <div className="p-4 rounded-2xl bg-white border border-gray-200 shadow-2xs">
            <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">
              Total Complaints
            </span>
            <p className="text-2xl sm:text-3xl font-extrabold text-gray-900 font-mono mt-1">
              {stats?.total_complaints || 0}
            </p>
            <span className="text-[10px] text-gray-500 mt-1 block">Across 8 departments</span>
          </div>

          {/* Pending Triage */}
          <div className="p-4 rounded-2xl bg-white border border-purple-200 shadow-2xs">
            <span className="text-[11px] font-bold text-purple-700 uppercase tracking-wider block">
              Pending Triage
            </span>
            <p className="text-2xl sm:text-3xl font-extrabold text-purple-900 font-mono mt-1">
              {stats?.pending_count || 0}
            </p>
            <span className="text-[10px] text-purple-600 mt-1 block">Awaiting assignment</span>
          </div>

          {/* In Progress */}
          <div className="p-4 rounded-2xl bg-white border border-blue-200 shadow-2xs">
            <span className="text-[11px] font-bold text-blue-700 uppercase tracking-wider block">
              In Progress
            </span>
            <p className="text-2xl sm:text-3xl font-extrabold text-blue-900 font-mono mt-1">
              {stats?.in_progress_count || 0}
            </p>
            <span className="text-[10px] text-blue-600 mt-1 block">Technician on site</span>
          </div>

          {/* Resolved */}
          <div className="p-4 rounded-2xl bg-white border border-emerald-200 shadow-2xs">
            <span className="text-[11px] font-bold text-emerald-700 uppercase tracking-wider block">
              Resolved
            </span>
            <p className="text-2xl sm:text-3xl font-extrabold text-emerald-900 font-mono mt-1">
              {stats?.resolved_count || 0}
            </p>
            <span className="text-[10px] text-emerald-600 mt-1 block">Successfully closed</span>
          </div>

          {/* Critical Hazards (Pulsing Red) */}
          <div className={`p-4 rounded-2xl bg-red-50 border border-red-300 shadow-2xs ${stats?.critical_count > 0 ? 'animate-critical' : ''}`}>
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-red-700 uppercase tracking-wider">
                Critical Hazards
              </span>
              <Flame className="w-4 h-4 text-red-600 animate-pulse" />
            </div>
            <p className="text-2xl sm:text-3xl font-extrabold text-red-900 font-mono mt-1">
              {stats?.critical_count || 0}
            </p>
            <span className="text-[10px] text-red-600 font-semibold mt-1 block">Requires immediate action</span>
          </div>

          {/* SLA Avg Time */}
          <div className="p-4 rounded-2xl bg-white border border-gray-200 shadow-2xs">
            <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">
              Avg Resolution SLA
            </span>
            <p className="text-2xl sm:text-3xl font-extrabold text-gray-900 font-mono mt-1">
              {stats?.avg_resolution_hours || 4.5}h
            </p>
            <span className="text-[10px] text-emerald-600 font-semibold mt-1 block">Target &lt; 8h</span>
          </div>

        </div>

        {/* ----------------- VISUAL BREAKDOWN CHARTS ROW ----------------- */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Category Distribution Bar */}
          <div className="p-5 rounded-2xl bg-white border border-gray-200 shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                Complaints by Category
              </h3>
              <span className="text-[10px] text-gray-400">Total: {stats?.total_complaints}</span>
            </div>

            <div className="space-y-2.5">
              {charts?.categories.slice(0, 5).map((cat) => {
                const pct = stats?.total_complaints ? Math.round((cat.value / stats.total_complaints) * 100) : 0;
                return (
                  <div key={cat.name} className="space-y-1">
                    <div className="flex justify-between text-xs font-medium text-gray-700">
                      <span>{cat.name}</span>
                      <span className="font-mono text-gray-500">{cat.value} ({pct}%)</span>
                    </div>
                    <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-emerald-600 rounded-full transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Severity Matrix */}
          <div className="p-5 rounded-2xl bg-white border border-gray-200 shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                Severity Triage Distribution
              </h3>
              <span className="text-[10px] text-gray-400">Hybrid AI + Rules</span>
            </div>

            <div className="grid grid-cols-2 gap-3 pt-1">
              <div 
                onClick={() => setFilterSeverity('CRITICAL')}
                className="p-3 rounded-xl bg-red-50 border border-red-200 cursor-pointer hover:bg-red-100/70 transition-colors"
              >
                <div className="flex items-center gap-1.5 text-xs font-bold text-red-800">
                  <ShieldAlert className="w-3.5 h-3.5 text-red-600" />
                  <span>CRITICAL</span>
                </div>
                <p className="text-2xl font-extrabold text-red-950 font-mono mt-1">
                  {stats?.critical_count || 0}
                </p>
                <span className="text-[10px] text-red-700">2h Max SLA</span>
              </div>

              <div 
                onClick={() => setFilterSeverity('HIGH')}
                className="p-3 rounded-xl bg-amber-50 border border-amber-200 cursor-pointer hover:bg-amber-100/70 transition-colors"
              >
                <div className="flex items-center gap-1.5 text-xs font-bold text-amber-800">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                  <span>HIGH</span>
                </div>
                <p className="text-2xl font-extrabold text-amber-950 font-mono mt-1">
                  {stats?.high_count || 0}
                </p>
                <span className="text-[10px] text-amber-700">6h Max SLA</span>
              </div>

              <div 
                onClick={() => setFilterSeverity('MEDIUM')}
                className="p-3 rounded-xl bg-blue-50 border border-blue-200 cursor-pointer hover:bg-blue-100/70 transition-colors"
              >
                <div className="flex items-center gap-1.5 text-xs font-bold text-blue-800">
                  <Clock className="w-3.5 h-3.5 text-blue-600" />
                  <span>MEDIUM</span>
                </div>
                <p className="text-2xl font-extrabold text-blue-950 font-mono mt-1">
                  {stats?.medium_count || 0}
                </p>
                <span className="text-[10px] text-blue-700">12h Max SLA</span>
              </div>

              <div 
                onClick={() => setFilterSeverity('LOW')}
                className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 cursor-pointer hover:bg-emerald-100/70 transition-colors"
              >
                <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-800">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  <span>LOW</span>
                </div>
                <p className="text-2xl font-extrabold text-emerald-950 font-mono mt-1">
                  {stats?.low_count || 0}
                </p>
                <span className="text-[10px] text-emerald-700">24-48h SLA</span>
              </div>
            </div>

            {filterSeverity !== 'ALL' && (
              <button
                onClick={() => setFilterSeverity('ALL')}
                className="text-[11px] text-gray-500 hover:text-gray-900 underline block text-center"
              >
                Clear severity filter
              </button>
            )}
          </div>

          {/* Department Workload */}
          <div className="p-5 rounded-2xl bg-white border border-gray-200 shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                Department Workload
              </h3>
              <Building2 className="w-4 h-4 text-gray-400" />
            </div>

            <div className="space-y-3">
              {charts?.department_workload.slice(0, 4).map((d) => (
                <div key={d.department} className="flex items-center justify-between text-xs p-2 rounded-lg bg-gray-50 border border-gray-100">
                  <span className="font-semibold text-gray-800 truncate max-w-[180px]">
                    {d.department}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-white text-gray-900 font-mono font-bold shadow-2xs border">
                    {d.complaints} active
                  </span>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* ----------------- RECENT COMPLAINTS TABLE ----------------- */}
        <div className="bg-white rounded-2xl shadow-2xs border border-gray-200 overflow-hidden">
          
          <div className="p-5 border-b border-gray-200 flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-bold text-gray-900">
                Incoming Complaint Stream
              </h3>
              <p className="text-xs text-gray-500">
                Click any row to open AI Diagnostic Report, assign technician, or transition status
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Link
                to="/admin/complaints"
                className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 flex items-center gap-1"
              >
                <span>View Full Table</span>
                <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-gray-50/80 border-b border-gray-200 text-gray-500 uppercase font-semibold text-[11px] tracking-wider">
                  <th className="py-3 px-4">Ticket ID</th>
                  <th className="py-3 px-4">Issue Summary</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Department</th>
                  <th className="py-3 px-4">Assigned Staff</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {recentComplaints.map((item) => (
                  <tr
                    key={item.id}
                    onClick={() => handleRowClick(item)}
                    className="hover:bg-gray-50/80 cursor-pointer transition-colors"
                  >
                    <td className="py-3.5 px-4 font-mono font-bold text-gray-900">
                      {item.id}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-gray-800 max-w-xs truncate">
                      {item.title}
                    </td>
                    <td className="py-3.5 px-4 text-gray-600">
                      {item.category}
                    </td>
                    <td className="py-3.5 px-4">
                      <SeverityBadge severity={item.severity} />
                    </td>
                    <td className="py-3.5 px-4 text-gray-600">
                      {item.department_name}
                    </td>
                    <td className="py-3.5 px-4 text-gray-500">
                      {item.assigned_to || (
                        <span className="text-gray-400 italic">Unassigned</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      {item.status === 'IN_PROGRESS' ? (
                        <button
                          onClick={(e) => handleResolveComplaint(e, item)}
                          className="px-2.5 py-1 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-xs transition-colors"
                        >
                          Resolve
                        </button>
                      ) : (
                        <span className="text-gray-400 font-mono">--</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>

        {/* Complaint Detail Triage Modal */}
        {selectedComplaint && (
          <ComplaintDetailModal
            complaint={selectedComplaint}
            isOpen={Boolean(selectedComplaint)}
            onClose={() => setSelectedComplaint(null)}
            onUpdated={(updated) => {
              setSelectedComplaint(updated);
              loadData();
            }}
          />
        )}

      </div>
    </div>
  );
}
