import React, { useState, useEffect } from 'react';
import { 
  X, User, Phone, MapPin, Tag, Building2, Clock, CheckCircle2, 
  AlertTriangle, Shield, Cpu, MessageSquare, Save, ArrowRight, Mail
} from 'lucide-react';
import StatusBadge from './StatusBadge';
import SeverityBadge from './SeverityBadge';
import TimelineView from './TimelineView';
import { updateComplaint, getComplaintEvents } from '../api';

const STATUS_OPTIONS = ['SUBMITTED', 'CLASSIFIED', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'CLOSED', 'REJECTED'];
const SEVERITY_OPTIONS = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
const DEPARTMENT_OPTIONS = [
  'IT Services',
  'Maintenance & Engineering',
  'Hostel Administration',
  'Food & Catering',
  'Housekeeping & Cleanliness',
  'Security Office',
  'Academic Administration',
  'Transport Office'
];

export default function ComplaintDetailModal({ complaint, isOpen, onClose, onUpdated }) {
  if (!isOpen || !complaint) return null;

  const [currentStatus, setCurrentStatus] = useState(complaint.status);
  const [assignedTo, setAssignedTo] = useState(complaint.assigned_to || '');
  const [department, setDepartment] = useState(complaint.department_name);
  const [severity, setSeverity] = useState(complaint.severity);
  const [internalNotes, setInternalNotes] = useState(complaint.internal_notes || '');
  const [events, setEvents] = useState([]);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    setCurrentStatus(complaint.status);
    setAssignedTo(complaint.assigned_to || '');
    setDepartment(complaint.department_name);
    setSeverity(complaint.severity);
    setInternalNotes(complaint.internal_notes || '');

    // Fetch timeline events
    getComplaintEvents(complaint.id)
      .then(setEvents)
      .catch(console.error);
  }, [complaint]);

  let parsedPlan = null;
  if (complaint.resolution_plan) {
    try {
      parsedPlan = typeof complaint.resolution_plan === 'string'
        ? JSON.parse(complaint.resolution_plan)
        : complaint.resolution_plan;
    } catch (e) {
      parsedPlan = null;
    }
  }

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const updated = await updateComplaint(complaint.id, {
        status: currentStatus,
        assigned_to: assignedTo.trim() || null,
        department_name: department,
        severity: severity,
        internal_notes: internalNotes,
        performed_by: 'Admin: Aditya Verma'
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);
      if (onUpdated) onUpdated(updated);
      
      // Refresh events
      getComplaintEvents(complaint.id).then(setEvents);
    } catch (err) {
      alert("Failed to save updates: " + err.message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[92vh] overflow-hidden shadow-2xl flex flex-col border border-gray-100 dark:bg-slate-900 dark:border-slate-700 animate-in fade-in duration-200">
        
        {/* Header */}
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-mono font-bold text-lg text-gray-900">
              {complaint.id}
            </span>
            <StatusBadge status={currentStatus} />
            <SeverityBadge severity={severity} />
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Main Issue Summary */}
          <div>
            <h3 className="text-xl font-bold text-gray-900 leading-snug">
              {complaint.title}
            </h3>
            <p className="mt-2 text-sm text-gray-700 leading-relaxed bg-gray-50 p-3.5 rounded-xl border border-gray-100">
              {complaint.description}
            </p>
          </div>

          {/* Evidence photo if uploaded */}
          {complaint.evidence_url && (
            <div className="border border-gray-200 rounded-xl p-3 bg-gray-50">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-2">
                Attached Evidence
              </span>
              <img 
                src={complaint.evidence_url} 
                alt="Evidence preview" 
                className="max-h-60 rounded-lg object-contain border"
              />
            </div>
          )}

          {/* 2-Column Grid: Metadata & Student Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* Left Card: Location & Category */}
            <div className="p-4 rounded-xl border border-gray-200 bg-white space-y-3">
              <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                Case Details
              </span>

              <div className="flex items-center gap-2.5 text-sm">
                <MapPin className="w-4 h-4 text-rose-500 shrink-0" />
                <div>
                  <span className="text-xs text-gray-400 block">Location</span>
                  <span className="font-semibold text-gray-800">{complaint.location}</span>
                </div>
              </div>

              <div className="flex items-center gap-2.5 text-sm">
                <Tag className="w-4 h-4 text-indigo-500 shrink-0" />
                <div>
                  <span className="text-xs text-gray-400 block">Category</span>
                  <span className="font-semibold text-gray-800">
                    {complaint.category} {complaint.subcategory && `(${complaint.subcategory})`}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2.5 text-sm">
                <Clock className="w-4 h-4 text-emerald-500 shrink-0" />
                <div>
                  <span className="text-xs text-gray-400 block">Created On</span>
                  <span className="font-medium text-gray-800">
                    {new Date(complaint.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            {/* Right Card: Student Reporter */}
            <div className="p-4 rounded-xl border border-gray-200 bg-white space-y-3">
              <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                Student Reporter
              </span>

              <div className="flex items-center gap-2.5 text-sm">
                <User className="w-4 h-4 text-blue-500 shrink-0" />
                <div>
                  <span className="text-xs text-gray-400 block">Name & ID</span>
                  <span className="font-semibold text-gray-800">
                    {complaint.student_name || 'Student Demo'} ({complaint.student_id || 'STU-2026-901'})
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2.5 text-sm">
                <Phone className="w-4 h-4 text-teal-500 shrink-0" />
                <div>
                  <span className="text-xs text-gray-400 block">Contact</span>
                  <span className="font-medium text-gray-800">
                    {complaint.student_contact || '+91 98765 43210'}
                  </span>
                </div>
              </div>

              {complaint.verified_email && (
                <div className="flex items-center gap-2.5 text-sm">
                  <Mail className="w-4 h-4 text-emerald-600 shrink-0" />
                  <div>
                    <span className="text-xs text-gray-400 block">Verified Institutional Email</span>
                    <span className="font-mono text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      {complaint.verified_email}
                    </span>
                  </div>
                </div>
              )}
            </div>

          </div>

          {/* AI Diagnostic Report (PRD requirement) */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-50/60 to-teal-50/60 border border-emerald-200">
            <div className="flex items-center gap-2 mb-2">
              <Cpu className="w-4 h-4 text-emerald-700" />
              <h4 className="text-xs font-bold text-emerald-900 uppercase tracking-wider">
                Gehor AI Diagnostic Report
              </h4>
              <div className="flex items-center gap-1.5 ml-auto">
                {complaint.routing_mode && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-teal-100 text-teal-800 font-semibold">
                    {complaint.routing_mode}
                  </span>
                )}
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-200 text-emerald-900 font-bold">
                  Confidence: {Math.round((complaint.ai_confidence || 0.94) * 100)}%
                </span>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-emerald-950">
              <div className="bg-white/80 p-2.5 rounded-lg border border-emerald-100">
                <span className="font-semibold text-emerald-800 block">Severity Reasoning:</span>
                <p className="mt-1 text-gray-600">
                  {complaint.ai_reasoning || "Standard priority classification based on semantic impact analysis."}
                </p>
              </div>
              <div className="bg-white/80 p-2.5 rounded-lg border border-emerald-100">
                <span className="font-semibold text-emerald-800 block">Routing Rationale:</span>
                <p className="mt-1 text-gray-600">
                  Auto-routed to {complaint.department_name} following category-to-department policy matrix.
                </p>
              </div>
            </div>

            {/* AI Incident Summary & Brief */}
            {(complaint.ai_summary || parsedPlan?.incident_summary) && (
              <div className="mt-3 bg-white/80 p-2.5 rounded-lg border border-emerald-100 text-xs">
                <span className="font-semibold text-emerald-800 block">Incident Brief & Summary:</span>
                <p className="mt-1 text-gray-700 leading-relaxed whitespace-pre-line">
                  {complaint.ai_summary || parsedPlan?.incident_summary}
                </p>
              </div>
            )}

            {/* Actionable Step-by-Step Resolution Plan */}
            {parsedPlan?.step_by_step_plan && parsedPlan.step_by_step_plan.length > 0 && (
              <div className="mt-3 bg-white/80 p-2.5 rounded-lg border border-emerald-100 text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-emerald-800">Resolution Action Plan (SOP Grounded):</span>
                  {parsedPlan.inference_provider && (
                    <span className="text-[10px] text-gray-400">
                      Engine: {parsedPlan.inference_provider}
                    </span>
                  )}
                </div>
                <div className="space-y-1.5">
                  {parsedPlan.step_by_step_plan.map((step) => (
                    <div key={step.step_number} className="p-2 rounded bg-emerald-50/50 border border-emerald-100/50 flex items-start gap-2">
                      <span className="font-bold text-emerald-700 shrink-0">{step.step_number}.</span>
                      <div className="space-y-0.5">
                        <div className="font-semibold text-gray-800">{step.action}</div>
                        <div className="text-gray-600">{step.details}</div>
                        {step.tools_or_personnel_needed && (
                          <div className="text-[11px] text-gray-500">
                            Required: {step.tools_or_personnel_needed}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                {parsedPlan.immediate_precautions && parsedPlan.immediate_precautions.length > 0 && (
                  <div className="pt-2 border-t border-emerald-100 text-[11px] text-amber-800">
                    <span className="font-semibold text-amber-900">Immediate Precautions: </span>
                    {parsedPlan.immediate_precautions.join(" • ")}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Admin Management Controls */}
          <div className="p-5 rounded-xl border border-gray-200 bg-gray-50/80 space-y-4">
            <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider flex items-center gap-2">
              <Shield className="w-4 h-4 text-purple-600" />
              <span>Administrative Actions & Triage</span>
            </h4>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {/* Status */}
              <div>
                <label className="text-xs font-semibold text-gray-600 block mb-1">
                  Update Status
                </label>
                <select
                  value={currentStatus}
                  onChange={(e) => setCurrentStatus(e.target.value)}
                  className="w-full text-xs font-medium bg-white border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500"
                >
                  {STATUS_OPTIONS.map((st) => (
                    <option key={st} value={st}>{st}</option>
                  ))}
                </select>
              </div>

              {/* Department Reassignment */}
              <div>
                <label className="text-xs font-semibold text-gray-600 block mb-1">
                  Department
                </label>
                <select
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="w-full text-xs font-medium bg-white border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500"
                >
                  {DEPARTMENT_OPTIONS.map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>

              {/* Severity Override */}
              <div>
                <label className="text-xs font-semibold text-gray-600 block mb-1">
                  Severity Level
                </label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="w-full text-xs font-medium bg-white border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500"
                >
                  {SEVERITY_OPTIONS.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Assign Technician */}
            <div>
              <label className="text-xs font-semibold text-gray-600 block mb-1">
                Assign Staff / Technician
              </label>
              <input
                type="text"
                placeholder="e.g. Er. Rajesh Sharma, Rahul IT"
                value={assignedTo}
                onChange={(e) => setAssignedTo(e.target.value)}
                className="w-full text-xs bg-white border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            {/* Internal Admin Notes */}
            <div>
              <label className="text-xs font-semibold text-gray-600 block mb-1">
                Internal Case Notes & Investigation Log
              </label>
              <textarea
                rows={2}
                placeholder="Add technician findings, vendor ticket reference, or inspection notes..."
                value={internalNotes}
                onChange={(e) => setInternalNotes(e.target.value)}
                className="w-full text-xs bg-white border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          {/* Audit Timeline */}
          <div>
            <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-3">
              Full Event Audit Log
            </h4>
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <TimelineView currentStatus={currentStatus} events={events} />
            </div>
          </div>

        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
          <div>
            {saveSuccess && (
              <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4" /> Updates saved successfully!
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Close
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-4 py-2 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg shadow-sm flex items-center gap-1.5 transition-colors disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              <span>{isSaving ? 'Saving...' : 'Save Changes'}</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
