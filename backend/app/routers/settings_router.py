from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import RoutingRule, Department, KnowledgeDoc
from ..schemas import RoutingRuleSchema, KnowledgeDocSchema, LearningStatsSchema
from ..ai.routing_learning_service import RoutingLearningService

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("/learning-stats", response_model=LearningStatsSchema)
def get_learning_stats(db: Session = Depends(get_db)):
    service = RoutingLearningService(db)
    return service.calculate_learning_metrics()


@router.get("/routing", response_model=List[RoutingRuleSchema])
def get_routing_rules(db: Session = Depends(get_db)):
    rules = db.query(RoutingRule).all()
    return rules

@router.put("/routing", response_model=RoutingRuleSchema)
def update_routing_rule(payload: RoutingRuleSchema, db: Session = Depends(get_db)):
    rule = db.query(RoutingRule).filter(RoutingRule.category == payload.category).first()
    if not rule:
        rule = RoutingRule(
            category=payload.category,
            department_name=payload.department_name,
            priority_level=payload.priority_level or "NORMAL",
            notes=payload.notes
        )
        db.add(rule)
    else:
        rule.department_name = payload.department_name
        rule.priority_level = payload.priority_level or "NORMAL"
        rule.notes = payload.notes
        
    db.commit()
    db.refresh(rule)
    return rule

@router.get("/departments")
def list_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).filter(Department.is_active == True).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "code": d.code,
            "description": d.description,
            "head_name": d.head_name,
            "contact_email": d.contact_email,
            "sla_hours": d.default_sla_hours
        }
        for d in depts
    ]

@router.get("/faq", response_model=List[KnowledgeDocSchema])
def list_knowledge_docs(db: Session = Depends(get_db)):
    docs = db.query(KnowledgeDoc).all()
    return docs
