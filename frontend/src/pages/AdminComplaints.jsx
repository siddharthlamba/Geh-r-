import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, RefreshCw, ArrowLeft, Download, Eye, Shield } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import SeverityBadge from '../components/SeverityBadge';
import ComplaintDetailModal from '../components/ComplaintDetailModal';
import { getComplaints, updateComplaint } from '../api';

const STATUS_LIST = ['ALL', 'SUBMITTED', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'CLOSED', 'REJECTED'];
const SEVERITY_LIST = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
const CATEGORY_LIST = [
  'ALL',
  'IT / Network',
  'Plumbing',
  'Electrical',
  'Infrastructure',
  'Mess / Food',
  'Hostel',
  'Cleanliness',
  'Security',
  'Academic',
  'Transport'
];

export default function AdminComplaints() {
  const [complaints, setComplaints] = useState([]);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('ALL');
  const [severity, setSeverity] = useState('ALL');
  const [category, setCategory] = useState('ALL');
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchList = async () => {
    setIsLoading(true);
    try {
      const data = await getComplaints({
        search: search.trim() || null,
        status,
        severity,
        category,
      });
      setComplaints(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchList();
  }, [status, severity, category]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchList();
  };

  const handleRowClick = async (item) => {
    let complaintToOpen = item;
    if (item.status === 'SUBMITTED') {
      try {
        const updated = await updateComplaint(item.id, {
          status: 'IN_PROGRESS',
          performed_by: 'Admin: Aditya Verma'
        });
        complaintToOpen = updated;
        setComplaints((prev) => prev.map((c) => (c.id === item.id ? updated : c)));
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
      setComplaints((prev) => prev.map((c) => (c.id === item.id ? updated : c)));
    } catch (err) {
      alert('Failed to resolve complaint: ' + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Link
              to="/admin"
              className="p-2 bg-white hover:bg-gray-100 rounded-xl border border-gray-200 text-gray-600 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div>
              <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
                All Institutional Complaints
              </h1>
              <p className="text-xs text-gray-500">
                Filter by department, severity triage, or search by student and keyword
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={fetchList}
              className="px-3 py-2 bg-white hover:bg-gray-100 border border-gray-300 rounded-xl text-xs font-semibold text-gray-700 flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Filter & Search Bar */}
        <div className="bg-white p-4 rounded-2xl shadow-2xs border border-gray-200 space-y-3">
          
          <form onSubmit={handleSearchSubmit} className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="Search by ID (GH-XXXX), location, description, or student name..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-3 py-2 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <button
              type="submit"
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-2xs transition-colors"
            >
              Search
            </button>
          </form>

          {/* Filter Dropdowns */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
            <div>
              <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                Filter by Status:
              </label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-full text-xs bg-gray-50 border border-gray-200 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500"
              >
                {STATUS_LIST.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                Filter by Severity:
              </label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full text-xs bg-gray-50 border border-gray-200 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500"
              >
                {SEVERITY_LIST.map((sev) => (
                  <option key={sev} value={sev}>{sev}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                Filter by Category:
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full text-xs bg-gray-50 border border-gray-200 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500"
              >
                {CATEGORY_LIST.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

        </div>

        {/* Complaints Data Table */}
        <div className="bg-white rounded-2xl shadow-2xs border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-gray-50/80 border-b border-gray-200 text-gray-500 uppercase font-semibold text-[11px] tracking-wider">
                  <th className="py-3 px-4">Complaint ID</th>
                  <th className="py-3 px-4">Student</th>
                  <th className="py-3 px-4">Issue Description</th>
                  <th className="py-3 px-4">Location</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Department</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {complaints.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="py-12 text-center text-gray-400">
                      No complaints match the selected filter criteria.
                    </td>
                  </tr>
                ) : (
                  complaints.map((item) => (
                    <tr
                      key={item.id}
                      onClick={() => handleRowClick(item)}
                      className="hover:bg-gray-50/80 cursor-pointer transition-colors"
                    >
                      <td className="py-3.5 px-4 font-mono font-bold text-gray-900">
                        {item.id}
                      </td>
                      <td className="py-3.5 px-4 text-gray-700">
                        <span className="font-semibold block">{item.student_name}</span>
                        <span className="text-[10px] text-gray-400">{item.student_id}</span>
                      </td>
                      <td className="py-3.5 px-4 font-medium text-gray-800 max-w-xs truncate">
                        {item.title}
                      </td>
                      <td className="py-3.5 px-4 text-gray-600">
                        {item.location}
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
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Modal */}
        {selectedComplaint && (
          <ComplaintDetailModal
            complaint={selectedComplaint}
            isOpen={Boolean(selectedComplaint)}
            onClose={() => setSelectedComplaint(null)}
            onUpdated={(updated) => {
              setSelectedComplaint(updated);
              fetchList();
            }}
          />
        )}

      </div>
    </div>
  );
}
