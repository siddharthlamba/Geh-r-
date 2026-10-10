import React, { useState, useEffect } from 'react';
import { CheckCircle2, Clock, PlayCircle, UserCheck, ShieldCheck, AlertCircle } from 'lucide-react';

const STAGES = [
  { key: 'SUBMITTED', label: 'Complaint Submitted', desc: 'Registered via conversational agent' },
  { key: 'CLASSIFIED', label: 'AI Classified', desc: 'Category & severity assessed' },
  { key: 'ASSIGNED', label: 'Assigned to Dept', desc: 'Routed to response team' },
  { key: 'IN_PROGRESS', label: 'Investigation in Progress', desc: 'Technician on-site inspection' },
  { key: 'RESOLVED', label: 'Resolved', desc: 'Remedial action completed' },
  { key: 'CLOSED', label: 'Closed', desc: 'Verified and closed' }
];

export default function TimelineView({ currentStatus = 'SUBMITTED', events = [], createdAt = null }) {
  const statusOrder = ['SUBMITTED', 'CLASSIFIED', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'CLOSED'];
  const currentIndex = statusOrder.indexOf(currentStatus.toUpperCase());
  const [autoAdvanced, setAutoAdvanced] = useState(false);

  useEffect(() => {
    // If status is already IN_PROGRESS or higher, auto-advance is inherently met
    if (currentIndex >= 3) {
      setAutoAdvanced(true);
      return;
    }

    const submissionTimestamp = createdAt
      ? new Date(createdAt).getTime()
      : (events.find(e => e.event_type === 'SUBMISSION')?.timestamp
        ? new Date(events.find(e => e.event_type === 'SUBMISSION').timestamp).getTime()
        : null);

    const now = Date.now();
    const delay = 15000; // 15-second delay
    const elapsed = submissionTimestamp ? now - submissionTimestamp : delay;

    if (elapsed >= delay) {
      setAutoAdvanced(true);
    } else {
      setAutoAdvanced(false);
      const remaining = Math.max(0, delay - elapsed);
      const timer = setTimeout(() => {
        setAutoAdvanced(true);
      }, remaining);
      return () => clearTimeout(timer);
    }
  }, [currentStatus, createdAt, events, currentIndex]);

  // When autoAdvanced is true, AI Classified (idx 1) and Assigned to Dept (idx 2) transition to completed/checked
  const effectiveIndex = (autoAdvanced && currentIndex < 2) ? 2 : currentIndex;

  return (
    <div className="py-2">
      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-gray-200">
        {STAGES.map((stage, idx) => {
          const isPassed = effectiveIndex >= idx;
          const isCurrent = effectiveIndex === idx || (autoAdvanced && currentStatus.toUpperCase() === 'SUBMITTED' && idx === 3);
          
          // Find matching event from audit log if available
          const matchingEvent = events.find(e => 
            e.new_value?.toUpperCase() === stage.key || 
            (stage.key === 'SUBMITTED' && e.event_type === 'SUBMISSION') ||
            (stage.key === 'CLASSIFIED' && e.event_type === 'CLASSIFICATION') ||
            (stage.key === 'ASSIGNED' && (e.event_type === 'ASSIGNMENT' || e.event_type === 'ROUTING')) ||
            (stage.key === 'RESOLVED' && e.event_type === 'RESOLUTION')
          );

          return (
            <div key={stage.key} className="relative flex items-start gap-3">
              {/* Node Icon */}
              <div
                className={`absolute -left-6 top-0.5 w-5 h-5 rounded-full flex items-center justify-center ring-4 ring-white transition-all ${
                  isPassed
                    ? isCurrent && !autoAdvanced
                      ? 'bg-amber-500 text-white animate-pulse'
                      : 'bg-emerald-600 text-white'
                    : isCurrent
                    ? 'bg-amber-500 text-white animate-pulse'
                    : 'bg-gray-200 text-gray-400'
                }`}
              >
                {isPassed ? (
                  isCurrent && !autoAdvanced ? (
                    <Clock className="w-3 h-3" />
                  ) : (
                    <CheckCircle2 className="w-3.5 h-3.5" />
                  )
                ) : isCurrent ? (
                  <Clock className="w-3 h-3" />
                ) : (
                  <span className="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
                )}
              </div>

              {/* Text content */}
              <div className="flex-1">
                <div className="flex items-baseline justify-between">
                  <h4
                    className={`text-xs font-semibold ${
                      isCurrent
                        ? 'text-amber-800'
                        : isPassed
                        ? 'text-gray-900'
                        : 'text-gray-400'
                    }`}
                  >
                    {stage.label}
                  </h4>
                  {matchingEvent ? (
                    <span className="text-[10px] text-gray-400">
                      {new Date(matchingEvent.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  ) : (autoAdvanced && (idx === 1 || idx === 2)) ? (
                    <span className="text-[10px] text-emerald-600 font-medium">
                      Auto-verified
                    </span>
                  ) : null}
                </div>

                <p className="text-[11px] text-gray-500 mt-0.5">
                  {matchingEvent?.notes || stage.desc}
                </p>

                {matchingEvent?.performed_by ? (
                  <span className="inline-block mt-1 text-[10px] bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded font-medium">
                    By: {matchingEvent.performed_by}
                  </span>
                ) : (autoAdvanced && (idx === 1 || idx === 2)) ? (
                  <span className="inline-block mt-1 text-[10px] bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded font-medium">
                    By: Gehor AI Engine (15s Auto-advance)
                  </span>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
