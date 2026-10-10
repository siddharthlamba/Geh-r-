"""
Component C (Part 2): Progressive Autonomy Routing Service.
Validates active destinations, checks learned supervisor feedback,
and routes autonomously when confidence exceeds threshold.
"""
from typing import Dict, Any, Tuple, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import re

from .gemini_client import get_gemini_client
from .routing_learning_service import RoutingLearningService
from ..models import Department, RoutingRule, User
from ..config import DEFAULT_ROUTING, ROUTING_AUTONOMOUS_CONFIDENCE_THRESHOLD

class RoutingDecision(BaseModel):
    department_name: str
    confidence: float
    routing_mode: str  # "AUTONOMOUS" | "SUPERVISED" | "FALLBACK"
    rationale: str
    assigned_staff: Optional[str] = None
    is_active_department: bool

class RoutingService:
    def __init__(self, db: Session):
        self.db = db
        self.learning_service = RoutingLearningService(db)
        self.gemini_client = get_gemini_client()
        self.threshold = ROUTING_AUTONOMOUS_CONFIDENCE_THRESHOLD

    def route_complaint(
        self,
        category: str,
        subcategory: str = "",
        description: str = "",
        location: str = ""
    ) -> RoutingDecision:
        """
        Determines target department using progressive autonomy.
        """
        features_text = f"{category} {subcategory} {description} {location}".strip()
        lower_features = features_text.lower()

        # Step 0: Deterministic Safety Override (Absolute Priority)
        from .severity_service import check_critical_safety_override
        crit_match = check_critical_safety_override(lower_features)
        if crit_match:
            dept, cat_name, trigger_word, reason = crit_match
            return RoutingDecision(
                department_name=dept,
                confidence=0.99,
                routing_mode="AUTONOMOUS",
                rationale=f"Deterministic safety override ({trigger_word}): {reason}",
                assigned_staff=self._get_assigned_staff_for_dept(dept),
                is_active_department=True
            )

        # Step 1: Check Learned Supervisor Corrections (Phase 3: Learning from labelled decisions)
        corrections_map = self.learning_service.get_learned_corrections_map()
        feature_words = set(w.lower() for w in lower_features.split() if len(w) > 3)
        for pattern_words, learned_dept in corrections_map.items():
            overlap = feature_words.intersection(set(pattern_words))
            if len(overlap) >= 3:
                # Strong match with a previously supervisor-corrected case!
                if self._is_active_department(learned_dept):
                    return RoutingDecision(
                        department_name=learned_dept,
                        confidence=0.96,
                        routing_mode="AUTONOMOUS",
                        rationale=f"Routed based on verified supervisor correction pattern for similar issue ({', '.join(list(overlap)[:3])}).",
                        assigned_staff=self._get_assigned_staff_for_dept(learned_dept),
                        is_active_department=True
                    )

        # Step 2: Contextual Keyword & Emergency Overrides
        if any(w in lower_features for w in ["fire", "hazard", "spark", "electric shock", "gas leak"]):
            dept = "Maintenance & Engineering"
            return RoutingDecision(
                department_name=dept,
                confidence=0.98,
                routing_mode="AUTONOMOUS",
                rationale="Emergency safety hazard auto-routed directly to Maintenance & Engineering rapid response.",
                assigned_staff=self._get_assigned_staff_for_dept(dept),
                is_active_department=self._is_active_department(dept)
            )

        # Landscaping & Groundskeeping override
        if any(w in lower_features for w in ["plant", "plants", "tree", "trees", "garden", "gardening", "grass", "lawn", "flower", "flowers", "landscaping", "groundskeeping", "botanical", "horticulture"]):
            dept = "Facilities & Groundskeeping"
            return RoutingDecision(
                department_name=dept,
                confidence=0.96,
                routing_mode="AUTONOMOUS",
                rationale="Campus landscaping, plants, and groundskeeping issue auto-routed to Facilities & Groundskeeping.",
                assigned_staff=self._get_assigned_staff_for_dept(dept),
                is_active_department=self._is_active_department(dept)
            )

        is_security_gate = "gate" in lower_features and not any(w in lower_features for w in ["plant", "plants", "tree", "trees", "garden", "lawn", "grass", "flower", "landscaping"])
        if any(w in lower_features for w in ["ambulance", "clinic", "doctor", "theft", "stolen", "security guard", "intruder", "trespass"]) or is_security_gate:
            dept = "Security Office"
            return RoutingDecision(
                department_name=dept,
                confidence=0.95,
                routing_mode="AUTONOMOUS",
                rationale="Safety, gate security, or emergency health transit routed to Security Office.",
                assigned_staff=self._get_assigned_staff_for_dept(dept),
                is_active_department=self._is_active_department(dept)
            )

        # Step 3: Check database-configured routing rules
        db_rule = self.db.query(RoutingRule).filter(RoutingRule.category == category).first()
        target_dept = db_rule.department_name if db_rule else DEFAULT_ROUTING.get(category, "Maintenance & Engineering")

        # Step 4: Verify Department Exists & Is Active in Database
        is_active = self._is_active_department(target_dept)
        if not is_active:
            # Fallback to general Maintenance
            return RoutingDecision(
                department_name="Maintenance & Engineering",
                confidence=0.70,
                routing_mode="FALLBACK",
                rationale=f"Target department '{target_dept}' is inactive or unconfigured. Routed to primary Maintenance fallback.",
                assigned_staff=None,
                is_active_department=True
            )

        # Step 5: Confidence Calculation & Autonomy Check
        confidence = 0.92
        if not category or category == "Other":
            confidence = 0.72  # Lower confidence requires human supervisor review

        routing_mode = "AUTONOMOUS" if confidence >= self.threshold else "SUPERVISED"
        rationale = (
            f"Auto-routed to '{target_dept}' with high confidence ({round(confidence*100)}%) matching category '{category}'."
            if routing_mode == "AUTONOMOUS"
            else f"Routed to '{target_dept}' under SUPERVISED mode for administrative confirmation (confidence {round(confidence*100)}% < threshold {round(self.threshold*100)}%)."
        )

        return RoutingDecision(
            department_name=target_dept,
            confidence=confidence,
            routing_mode=routing_mode,
            rationale=rationale,
            assigned_staff=self._get_assigned_staff_for_dept(target_dept),
            is_active_department=True
        )

    def _is_active_department(self, dept_name: str) -> bool:
        dept = self.db.query(Department).filter(
            Department.name == dept_name,
            Department.is_active == True
        ).first()
        return dept is not None

    def _get_assigned_staff_for_dept(self, dept_name: str) -> Optional[str]:
        """
        Retrieves real staff member from the database if configured.
        Never invents fake employees.
        """
        staff = self.db.query(User).filter(
            User.department_name == dept_name,
            User.role == "STAFF"
        ).first()
        return staff.name if staff else None
