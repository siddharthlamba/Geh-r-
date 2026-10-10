/**
 * Gehor API client services
 */

const BASE_URL = ''; // Proxied through Vite in dev or same origin in prod

export async function sendMessage(sessionId, message, evidenceUrl = null, studentId = 'STU-2026-901') {
  const res = await fetch(`${BASE_URL}/api/agent/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      student_id: studentId,
      evidence_url: evidenceUrl,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to send message');
  }
  return res.json();
}

export async function getSessionHistory(sessionId) {
  const res = await fetch(`${BASE_URL}/api/agent/session/${sessionId}`);
  if (!res.ok) throw new Error('Failed to load session history');
  return res.json();
}

export async function resetSession(sessionId) {
  const res = await fetch(`${BASE_URL}/api/agent/session/${sessionId}/reset`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to reset session');
  return res.json();
}

export async function getComplaints(params = {}) {
  const query = new URLSearchParams();
  if (params.status && params.status !== 'ALL') query.append('status', params.status);
  if (params.severity && params.severity !== 'ALL') query.append('severity', params.severity);
  if (params.category && params.category !== 'ALL') query.append('category', params.category);
  if (params.department && params.department !== 'ALL') query.append('department', params.department);
  if (params.search) query.append('search', params.search);

  const res = await fetch(`${BASE_URL}/api/complaints?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch complaints');
  return res.json();
}

export async function getComplaintById(complaintId) {
  const res = await fetch(`${BASE_URL}/api/complaints/${complaintId}`);
  if (!res.ok) throw new Error(`Complaint ${complaintId} not found`);
  return res.json();
}

export async function updateComplaint(complaintId, updates) {
  const res = await fetch(`${BASE_URL}/api/complaints/${complaintId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  if (!res.ok) throw new Error('Failed to update complaint');
  return res.json();
}

export async function getComplaintEvents(complaintId) {
  const res = await fetch(`${BASE_URL}/api/complaints/${complaintId}/events`);
  if (!res.ok) throw new Error('Failed to fetch events');
  return res.json();
}

export async function getDashboardStats() {
  const res = await fetch(`${BASE_URL}/api/dashboard/stats`);
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function getDashboardCharts() {
  const res = await fetch(`${BASE_URL}/api/dashboard/charts`);
  if (!res.ok) throw new Error('Failed to fetch chart data');
  return res.json();
}

export async function getRoutingRules() {
  const res = await fetch(`${BASE_URL}/api/settings/routing`);
  if (!res.ok) throw new Error('Failed to fetch routing rules');
  return res.json();
}

export async function updateRoutingRule(rule) {
  const res = await fetch(`${BASE_URL}/api/settings/routing`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rule),
  });
  if (!res.ok) throw new Error('Failed to update routing rule');
  return res.json();
}

export async function getDepartments() {
  const res = await fetch(`${BASE_URL}/api/settings/departments`);
  if (!res.ok) throw new Error('Failed to fetch departments');
  return res.json();
}

export async function getFaqDocs() {
  const res = await fetch(`${BASE_URL}/api/settings/faq`);
  if (!res.ok) throw new Error('Failed to fetch FAQs');
  return res.json();
}

export async function uploadEvidenceFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('File upload failed');
  return res.json();
}
