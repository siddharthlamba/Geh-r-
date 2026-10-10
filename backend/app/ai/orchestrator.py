"""
Gehor AI Orchestrator.
Coordinates full conversation understanding, severity prediction,
progressive autonomous routing, and recipient resolution brief generation.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json

from .conversation_analyzer import ConversationAnalyzer, ConversationAnalysis
from .severity_service import SeverityService, SeverityEvaluation
from .routing_service import RoutingService, RoutingDecision
from .resolution_service import ResolutionService, ResolutionBrief

class OrchestratedComplaintPayload(BaseModel):
    analysis: ConversationAnalysis
    severity_eval: SeverityEvaluation
    routing_decision: RoutingDecision
    resolution_brief: ResolutionBrief
    ai_summary: str
    resolution_plan_json: str
    ai_provider: str

class AIOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.analyzer = ConversationAnalyzer()
        self.severity_service = SeverityService()
        self.routing_service = RoutingService(db)
        self.resolution_service = ResolutionService()

    def process_full_complaint_intake(
        self,
        complaint_id: str,
        messages: List[Dict[str, str]],
        initial_context: Optional[Dict[str, Any]] = None
    ) -> OrchestratedComplaintPayload:
        """
        Executes complete AI pipeline over conversation history.
        """
        # Step 1: Conversation Understanding (Component A)
        analysis = self.analyzer.analyze_conversation(messages, initial_context)

        # Step 2: Severity Prediction with Deterministic Safety Safeguards (Component B)
        full_text = " ".join([m.get("content", "") for m in messages if m.get("sender") == "student"])
        severity_eval = self.severity_service.evaluate_severity(
            full_conversation_text=full_text or analysis.original_problem_description,
            category=analysis.category,
            location=analysis.relevant_location
        )

        # Step 3: Progressive Autonomy Routing (Component C)
        routing_decision = self.routing_service.route_complaint(
            category=analysis.category,
            subcategory=analysis.subcategory,
            description=analysis.original_problem_description,
            location=analysis.relevant_location
        )

        # Step 4: Recipient-Specific Resolution Brief (Component D)
        brief = self.resolution_service.generate_resolution_brief(
            complaint_id=complaint_id,
            title=analysis.complaint_summary[:80],
            description=analysis.original_problem_description,
            category=analysis.category,
            subcategory=analysis.subcategory,
            location=analysis.relevant_location,
            severity=severity_eval.severity,
            department_name=routing_decision.department_name,
            assigned_staff=routing_decision.assigned_staff,
            routing_rationale=routing_decision.rationale
        )

        resolution_json = brief.model_dump_json()

        # Determine overall provider reported
        if analysis.inference_provider.startswith("ollama") or brief.inference_provider.startswith("ollama"):
            provider = "ollama_offline"
        elif analysis.inference_provider == "gemini_free_tier" or brief.inference_provider == "gemini_free_tier":
            provider = "gemini_free_tier"
        else:
            provider = "rule_fallback"

        return OrchestratedComplaintPayload(
            analysis=analysis,
            severity_eval=severity_eval,
            routing_decision=routing_decision,
            resolution_brief=brief,
            ai_summary=analysis.complaint_summary,
            resolution_plan_json=resolution_json,
            ai_provider=provider
        )
