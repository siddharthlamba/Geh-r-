import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict

class ComplaintEventSchema(BaseModel):
    id: int
    complaint_id: str
    event_type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    performed_by: str
    notes: Optional[str] = None
    timestamp: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class ComplaintCreate(BaseModel):
    title: Optional[str] = None
    description: str
    category: str
    subcategory: Optional[str] = None
    severity: str = "MEDIUM"
    location: str
    department_name: Optional[str] = None
    student_id: Optional[str] = "STU-2026-901"
    student_name: Optional[str] = "Student Demo"
    student_contact: Optional[str] = "+91 98765 43210"
    evidence_url: Optional[str] = None
    verified_email: Optional[str] = None

class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    department_name: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    internal_notes: Optional[str] = None
    performed_by: Optional[str] = "Admin Staff"
    supervisor_confirmation: Optional[bool] = None
    verified_email: Optional[str] = None

class ComplaintResponse(BaseModel):
    id: str
    student_id: Optional[str]
    student_name: Optional[str]
    student_contact: Optional[str]
    title: str
    description: str
    category: str
    subcategory: Optional[str]
    severity: str
    location: str
    department_name: str
    assigned_to: Optional[str]
    status: str
    evidence_url: Optional[str]
    ai_confidence: Optional[float]
    ai_intent: Optional[str]
    ai_reasoning: Optional[str]
    internal_notes: Optional[str]
    
    # Enhanced AI Intelligence Layer Fields
    ai_summary: Optional[str] = None
    resolution_plan: Optional[str] = None
    predicted_department: Optional[str] = None
    routing_confidence: Optional[float] = 0.92
    routing_mode: Optional[str] = "SUPERVISED"
    ai_provider: Optional[str] = "gemini_free_tier"
    verified_email: Optional[str] = None
    
    created_at: datetime.datetime
    updated_at: datetime.datetime
    resolved_at: Optional[datetime.datetime]
    events: Optional[List[ComplaintEventSchema]] = []

    model_config = ConfigDict(from_attributes=True)

class ChatMessageSchema(BaseModel):
    id: int
    session_id: str
    sender: str
    content: str
    message_type: str
    metadata_json: Optional[str] = None
    timestamp: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    student_id: Optional[str] = "STU-2026-901"
    evidence_url: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    message_type: str = "text"
    state: str
    draft_complaint: Optional[Dict[str, Any]] = None
    complaint_id: Optional[str] = None
    duplicate_warning: Optional[Dict[str, Any]] = None
    quick_options: Optional[List[str]] = None

class DashboardStats(BaseModel):
    total_complaints: int
    pending_count: int
    in_progress_count: int
    resolved_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    avg_resolution_hours: float
    categories_breakdown: Dict[str, int]
    severity_breakdown: Dict[str, int]
    department_workload: Dict[str, int]
    status_breakdown: Dict[str, int]

class RoutingRuleSchema(BaseModel):
    category: str
    department_name: str
    priority_level: Optional[str] = "NORMAL"
    notes: Optional[str] = None

class KnowledgeDocSchema(BaseModel):
    id: int
    title: str
    category: str
    content: str
    tags: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class RoutingFeedbackSchema(BaseModel):
    id: int
    complaint_id: str
    features_text: str
    predicted_department: str
    actual_department: str
    was_corrected: bool
    supervisor_name: str
    timestamp: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class LearningStatsSchema(BaseModel):
    total_feedback_samples: int
    corrected_count: int
    confirmed_count: int
    accuracy_percentage: float
    autonomous_eligibility_rate: float
    model_version: str
    active_routing_rules: int

class StepItem(BaseModel):
    step_number: int
    action: str
    details: str
    tools_or_personnel_needed: Optional[str] = None
    verification_check: Optional[str] = None

class ResolutionBriefSchema(BaseModel):
    complaint_id: str
    severity: str
    urgency_explanation: str
    incident_summary: str
    responsible_recipient: str
    routing_rationale: str
    immediate_precautions: List[str]
    step_by_step_plan: List[StepItem]
    escalation_conditions: List[str]
    closure_criteria: List[str]
    uncertainties_and_assumptions: List[str]
    grounded_sops_referenced: List[str]
    generated_at: str
    inference_provider: str
