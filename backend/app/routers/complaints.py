import datetime
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import get_db
from ..models import Complaint, ComplaintEvent
from ..schemas import (
    ComplaintCreate,
    ComplaintUpdate,
    ComplaintResponse,
    ComplaintEventSchema,
    ResolutionBriefSchema
)
from ..agent import generate_complaint_id
from ..routing import route_complaint
from ..severity import calculate_severity
from ..ai.orchestrator import AIOrchestrator
from ..ai.routing_learning_service import RoutingLearningService
from ..ai.resolution_service import ResolutionService

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

@router.get("", response_model=List[ComplaintResponse])
def list_complaints(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    category: Optional[str] = Query(None, description="Filter by category"),
    department: Optional[str] = Query(None, description="Filter by department"),
    search: Optional[str] = Query(None, description="Search by ID, location, description, or student"),
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)
    
    if status and status.upper() != "ALL":
        query = query.filter(Complaint.status == status.upper())
    if severity and severity.upper() != "ALL":
        query = query.filter(Complaint.severity == severity.upper())
    if category and category != "ALL":
        query = query.filter(Complaint.category == category)
    if department and department != "ALL":
        query = query.filter(Complaint.department_name == department)
        
    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                Complaint.id.ilike(s),
                Complaint.title.ilike(s),
                Complaint.description.ilike(s),
                Complaint.location.ilike(s),
                Complaint.student_name.ilike(s),
                Complaint.student_id.ilike(s),
                Complaint.assigned_to.ilike(s)
            )
        )
        
    complaints = query.order_by(Complaint.created_at.desc()).limit(limit).all()
    return complaints

@router.post("", response_model=ComplaintResponse)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    new_id = generate_complaint_id(db)
    
    # Process through AI Intelligence Layer
    orchestrator = AIOrchestrator(db)
    messages = [{"sender": "student", "content": payload.description}]
    context = {
        "title": payload.title,
        "description": payload.description,
        "category": payload.category,
        "subcategory": payload.subcategory,
        "location": payload.location,
        "severity": payload.severity,
        "department": payload.department_name
    }
    orchestrated = orchestrator.process_full_complaint_intake(
        complaint_id=new_id,
        messages=messages,
        initial_context=context
    )

    dept = payload.department_name or orchestrated.routing_decision.department_name
    sev = payload.severity or orchestrated.severity_eval.severity
    title = payload.title or payload.description[:70]
    category = payload.category or orchestrated.analysis.category
    subcategory = payload.subcategory or orchestrated.analysis.subcategory
    location = payload.location or orchestrated.analysis.relevant_location or "Campus"

    complaint = Complaint(
        id=new_id,
        student_id=payload.student_id or "STU-2026-901",
        student_name=payload.student_name or "Student Demo",
        student_contact=payload.student_contact or "+91 98765 43210",
        title=title,
        description=payload.description,
        category=category,
        subcategory=subcategory,
        severity=sev,
        location=location,
        department_name=dept,
        assigned_to=orchestrated.routing_decision.assigned_staff,
        status="SUBMITTED",
        evidence_url=payload.evidence_url,
        ai_confidence=orchestrated.routing_decision.confidence,
        ai_intent="MANUAL_CREATE",
        ai_reasoning=orchestrated.severity_eval.reasoning,
        internal_notes=None,
        ai_summary=orchestrated.ai_summary,
        resolution_plan=orchestrated.resolution_plan_json,
        predicted_department=dept,
        routing_confidence=orchestrated.routing_decision.confidence,
        routing_mode=orchestrated.routing_decision.routing_mode,
        ai_provider=orchestrated.ai_provider,
        verified_email=payload.verified_email
    )
    db.add(complaint)

    event = ComplaintEvent(
        complaint_id=new_id,
        event_type="SUBMISSION",
        new_value="SUBMITTED",
        performed_by="Student Portal",
        notes="Complaint created."
    )
    db.add(event)
    db.commit()
    db.refresh(complaint)
    return complaint

@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    comp = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not comp:
        # Check case-insensitive
        comp = db.query(Complaint).filter(Complaint.id.ilike(complaint_id)).first()
    if not comp:
        raise HTTPException(status_code=404, detail=f"Complaint with ID '{complaint_id}' not found.")
    return comp

@router.patch("/{complaint_id}", response_model=ComplaintResponse)
def update_complaint(complaint_id: str, payload: ComplaintUpdate, db: Session = Depends(get_db)):
    comp = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    now = datetime.datetime.now(datetime.UTC)
    performer = payload.performed_by or "Administrator"

    # Status transition
    if payload.status and payload.status != comp.status:
        old_status = comp.status
        comp.status = payload.status
        
        if payload.status in ["RESOLVED", "CLOSED"] and not comp.resolved_at:
            comp.resolved_at = now
            
        event = ComplaintEvent(
            complaint_id=comp.id,
            event_type="STATUS_CHANGE",
            old_value=old_status,
            new_value=payload.status,
            performed_by=performer,
            notes=f"Status transitioned from {old_status} to {payload.status}.",
            timestamp=now
        )
        db.add(event)

    # Assigned staff
    if payload.assigned_to and payload.assigned_to != comp.assigned_to:
        old_assigned = comp.assigned_to or "Unassigned"
        comp.assigned_to = payload.assigned_to
        if comp.status == "SUBMITTED":
            comp.status = "ASSIGNED"
            
        event = ComplaintEvent(
            complaint_id=comp.id,
            event_type="ASSIGNMENT",
            old_value=old_assigned,
            new_value=payload.assigned_to,
            performed_by=performer,
            notes=f"Complaint assigned to staff member {payload.assigned_to}.",
            timestamp=now
        )
        db.add(event)

    # Department reassignment
    if payload.department_name and payload.department_name != comp.department_name:
        old_dept = comp.department_name
        comp.department_name = payload.department_name
        event = ComplaintEvent(
            complaint_id=comp.id,
            event_type="ROUTING",
            old_value=old_dept,
            new_value=payload.department_name,
            performed_by=performer,
            notes=f"Reassigned from department '{old_dept}' to '{payload.department_name}'.",
            timestamp=now
        )
        db.add(event)

        # Supervised routing feedback recorded for adaptive routing
        learning_service = RoutingLearningService(db)
        learning_service.record_supervisor_decision(
            complaint_id=comp.id,
            features_text=f"{comp.category} {comp.title} {comp.description}",
            predicted_department=comp.predicted_department or old_dept or "Unknown",
            actual_department=payload.department_name,
            supervisor_name=performer
        )

    # Category override
    if payload.category and payload.category != comp.category:
        old_cat = comp.category
        comp.category = payload.category
        event = ComplaintEvent(
            complaint_id=comp.id,
            event_type="CLASSIFICATION",
            old_value=old_cat,
            new_value=payload.category,
            performed_by=performer,
            notes=f"Category manually updated to {payload.category}.",
            timestamp=now
        )
        db.add(event)

    # Severity override
    if payload.severity and payload.severity != comp.severity:
        old_sev = comp.severity
        comp.severity = payload.severity
        event = ComplaintEvent(
            complaint_id=comp.id,
            event_type="CLASSIFICATION",
            old_value=old_sev,
            new_value=payload.severity,
            performed_by=performer,
            notes=f"Severity manually adjusted from {old_sev} to {payload.severity}.",
            timestamp=now
        )
        db.add(event)

    # Internal notes
    if payload.internal_notes is not None:
        comp.internal_notes = payload.internal_notes
        if payload.internal_notes.strip():
            event = ComplaintEvent(
                complaint_id=comp.id,
                event_type="NOTE",
                performed_by=performer,
                notes=payload.internal_notes,
                timestamp=now
            )
            db.add(event)

    if payload.verified_email is not None:
        comp.verified_email = payload.verified_email

    comp.updated_at = now
    db.commit()
    db.refresh(comp)
    return comp

@router.get("/{complaint_id}/events", response_model=List[ComplaintEventSchema])
def get_complaint_events(complaint_id: str, db: Session = Depends(get_db)):
    comp = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")
    events = db.query(ComplaintEvent).filter(ComplaintEvent.complaint_id == complaint_id).order_by(ComplaintEvent.timestamp.asc()).all()
    return events

@router.get("/{complaint_id}/resolution-brief", response_model=ResolutionBriefSchema)
def get_resolution_brief(complaint_id: str, db: Session = Depends(get_db)):
    comp = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not comp:
        comp = db.query(Complaint).filter(Complaint.id.ilike(complaint_id)).first()
    if not comp:
        raise HTTPException(status_code=404, detail=f"Complaint with ID '{complaint_id}' not found.")
        
    if comp.resolution_plan:
        try:
            data = json.loads(comp.resolution_plan)
            return data
        except Exception:
            pass

    # Generate on-demand if not already generated
    res_service = ResolutionService()
    brief = res_service.generate_resolution_brief(
        complaint_id=comp.id,
        title=comp.title,
        description=comp.description,
        category=comp.category,
        subcategory=comp.subcategory or "",
        location=comp.location,
        severity=comp.severity,
        department_name=comp.department_name,
        assigned_staff=comp.assigned_to,
        routing_rationale=comp.ai_reasoning or ""
    )
    brief_dict = brief.model_dump()
    comp.resolution_plan = json.dumps(brief_dict)
    if not comp.ai_summary:
        comp.ai_summary = brief.incident_summary
    db.commit()
    return brief_dict

