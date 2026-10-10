"""
Department Routing Engine for Gehor.
Routes complaint categories to institutional departments with configurable fallbacks.
"""
from typing import Tuple
import re
from .config import DEFAULT_ROUTING, DEPARTMENT_METADATA

def route_complaint(category: str, subcategory: str = "", text: str = "") -> Tuple[str, str]:
    """
    Determines the target department based on category and description.
    Returns: (department_name, routing_rationale)
    """
    text_lower = text.lower()
    
    # 0. Deterministic Safety Override (Absolute Priority)
    from .ai.severity_service import check_critical_safety_override
    crit = check_critical_safety_override(f"{category} {text_lower}")
    if crit:
        dept, cat_name, trigger, reason = crit
        return (dept, f"Critical safety override ({trigger}): {reason}")

    # Specific contextual overrides
    if "ambulance" in text_lower or "clinic" in text_lower or "doctor" in text_lower:
        return ("Security Office", "Health/Emergency medical escort routed to Campus Security.")
        
    if "food" in text_lower or "mess" in text_lower or "canteen" in text_lower or "dining" in text_lower:
        return ("Food & Catering", "Mess catering & dining hygiene matter.")
        
    if "wifi" in text_lower or "wi-fi" in text_lower or "internet" in text_lower or "router" in text_lower or re.search(r"\blan\b", text_lower):
        return ("IT Services", "Network & connectivity ticket.")
        
    if "water leak" in text_lower or "broken pipe" in text_lower or "plumbing" in text_lower or "tap" in text_lower:
        return ("Maintenance & Engineering", "Plumbing infrastructure maintenance.")
        
    if "electric" in text_lower or "shock" in text_lower or "short circuit" in text_lower or "switch" in text_lower or "wiring" in text_lower:
        return ("Maintenance & Engineering", "Electrical infrastructure repair.")

    if "ac" in text_lower or "air condition" in text_lower or "cooling" in text_lower or "fan" in text_lower:
        return ("Maintenance & Engineering", "HVAC / Electrical appliance maintenance.")

    if "shuttle" in text_lower or "bus" in text_lower or "driver" in text_lower:
        return ("Transport Office", "Campus transit operation.")

    if any(w in text_lower for w in ["plant", "plants", "tree", "trees", "garden", "lawn", "grass", "flower", "landscaping", "groundskeeping", "botanical"]):
        return ("Facilities & Groundskeeping", "Campus landscaping and groundskeeping matter.")

    # Category-based default routing
    dept = DEFAULT_ROUTING.get(category, "Maintenance & Engineering")
    rationale = f"Mapped by category '{category}' to '{dept}' based on institutional routing policy."
    
    return (dept, rationale)
