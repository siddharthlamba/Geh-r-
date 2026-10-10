import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

def utc_now():
    return datetime.datetime.now(datetime.UTC)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    student_id = Column(String(50), unique=True, index=True, nullable=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(String(20), default="STUDENT")  # STUDENT, ADMIN, STAFF
    department_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now)

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    head_name = Column(String(100), nullable=True)
    contact_email = Column(String(120), nullable=True)
    default_sla_hours = Column(Integer, default=12)
    is_active = Column(Boolean, default=True)

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(30), primary_key=True, index=True)  # e.g. GH-2026-1042
    student_id = Column(String(50), nullable=True, default="STU-2026-901")
    student_name = Column(String(100), nullable=True, default="Student Demo")
    student_contact = Column(String(50), nullable=True, default="+91 98765 43210")
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50), nullable=True)
    severity = Column(String(20), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    location = Column(String(150), nullable=False)
    
    department_name = Column(String(100), nullable=False)
    assigned_to = Column(String(100), nullable=True)  # technician / staff
    status = Column(String(30), nullable=False, default="SUBMITTED")
    # SUBMITTED, CLASSIFIED, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED, REJECTED
    
    evidence_url = Column(String(300), nullable=True)
    ai_confidence = Column(Float, default=0.92)
    ai_intent = Column(String(50), default="CREATE_COMPLAINT")
    ai_reasoning = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)

    # Enhanced AI Intelligence Layer Fields
    ai_summary = Column(Text, nullable=True)  # Deep incident brief
    resolution_plan = Column(Text, nullable=True)  # Structured JSON recipient resolution brief
    predicted_department = Column(String(100), nullable=True)  # Model's initial prediction
    routing_confidence = Column(Float, default=0.92)
    routing_mode = Column(String(30), default="SUPERVISED")  # AUTONOMOUS, SUPERVISED, FALLBACK
    ai_provider = Column(String(50), default="gemini_free_tier")  # gemini_free_tier or rule_fallback
    verified_email = Column(String(120), nullable=True)  # Friction gate email for high/critical issues
    
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    resolved_at = Column(DateTime, nullable=True)

    events = relationship("ComplaintEvent", back_populates="complaint", cascade="all, delete-orphan", order_by="ComplaintEvent.timestamp")

class ComplaintEvent(Base):
    __tablename__ = "complaint_events"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String(30), ForeignKey("complaints.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  
    # SUBMISSION, CLASSIFICATION, ROUTING, ASSIGNMENT, STATUS_CHANGE, NOTE, RESOLUTION
    old_value = Column(String(100), nullable=True)
    new_value = Column(String(100), nullable=True)
    performed_by = Column(String(100), default="Gehor AI")
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utc_now)

    complaint = relationship("Complaint", back_populates="events")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(50), primary_key=True, index=True)  # session UUID
    student_id = Column(String(50), nullable=True, default="STU-2026-901")
    state = Column(String(50), default="GREETING")  # GREETING, COLLECTING_INFO, CONFIRMATION, SUBMITTED, TRACKING
    extracted_data = Column(Text, default="{}")  # JSON payload of current draft complaint
    last_complaint_id = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.timestamp")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String(20), nullable=False)  # "student" or "ai"
    content = Column(Text, nullable=False)
    message_type = Column(String(30), default="text")  # text, confirmation_card, complaint_submitted, image, quick_replies
    metadata_json = Column(Text, nullable=True)  # JSON string
    timestamp = Column(DateTime, default=utc_now)

    session = relationship("ChatSession", back_populates="messages")

class KnowledgeDoc(Base):
    __tablename__ = "knowledge_docs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=utc_now)

class RoutingRule(Base):
    __tablename__ = "routing_rules"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), unique=True, nullable=False)
    department_name = Column(String(100), nullable=False)
    priority_level = Column(String(20), default="NORMAL")
    notes = Column(String(255), nullable=True)

class RoutingFeedback(Base):
    """
    Component C: Supervised Routing feedback loop.
    Records labeled examples when an administrator confirms or corrects a routing decision.
    """
    __tablename__ = "routing_feedback"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String(30), nullable=False, index=True)
    features_text = Column(Text, nullable=False)
    predicted_department = Column(String(100), nullable=False)
    actual_department = Column(String(100), nullable=False)
    was_corrected = Column(Boolean, default=False)
    supervisor_name = Column(String(100), default="Admin Supervisor")
    timestamp = Column(DateTime, default=utc_now)
