import re
from typing import Tuple

CRITICAL_KEYWORDS = [
    r"hazard", r"fire", r"smoke", r"electric shock", r"spark", r"live wire",
    r"short circuit", r"gas leak", r"chemical spill", r"explosion", r"collapsed",
    r"bleeding", r"emergency", r"burning smell", r"electrocution", r"poison", r"danger"
]

HIGH_KEYWORDS = [
    r"no water", r"water leak", r"broken pipe", r"slippery", r"flooding", r"flood",
    r"blackout", r"power cut", r"power outage", r"entire hostel", r"entire block",
    r"all rooms", r"every student", r"lift stuck", r"elevator stuck", r"food poison",
    r"spoiled food", r"raw sewage", r"stink", r"infestation"
]

MEDIUM_KEYWORDS = [
    r"wi-?fi", r"internet", r"network", r"router", r"not working", r"ac",
    r"air condition", r"cooling", r"projector", r"mic", r"speaker",
    r"slow", r"flush", r"tap", r"washroom dirty", r"mess food", r"unhygienic",
    r"broken chair", r"window broken", r"door lock"
]

LOW_KEYWORDS = [
    r"noisy fan", r"squeak", r"loose", r"tube light", r"bulb flicker",
    r"paint", r"dusty", r"cobweb", r"minor", r"scratched"
]

def calculate_severity(text: str, category: str = "", location: str = "") -> Tuple[str, str]:
    """
    Combines rule-based safety checks and situational severity analysis.
    Returns: (severity_level, reasoning)
    """
    content = f"{text} {category} {location}".lower()
    
    # 0. Deterministic Categorized Critical Safety Safeguard (Absolute Priority)
    from .ai.severity_service import check_critical_safety_override
    crit_match = check_critical_safety_override(content)
    if crit_match:
        dept, cat_name, trigger_word, reason = crit_match
        return ("CRITICAL", f"Critical safety override: '{trigger_word}'. {reason}")

    # 1. Critical safety hazard checks (Priority 1)
    for pattern in CRITICAL_KEYWORDS:
        if re.search(r"\b" + pattern + r"\b", content):
            return (
                "CRITICAL",
                f"Identified immediate safety hazard trigger '{pattern}'. Flagged for instant emergency response."
            )
            
    # 2. High operational impact checks
    for pattern in HIGH_KEYWORDS:
        if re.search(r"\b" + pattern + r"\b", content):
            return (
                "HIGH",
                f"Detected significant operational or multi-resident disruption trigger '{pattern}'."
            )
            
    # 3. Contextual category escalations
    if any(k in content for k in ["everyone", "entire", "all students", "whole floor"]):
        return (
            "HIGH",
            "Widespread disruption affecting multiple rooms or entire floor."
        )

    # 4. Medium operational disruption
    for pattern in MEDIUM_KEYWORDS:
        if re.search(r"\b" + pattern + r"\b", content):
            return (
                "MEDIUM",
                f"Disruption impacting routine daily functionality/amenity ('{pattern}')."
            )

    # 5. Low inconvenience
    for pattern in LOW_KEYWORDS:
        if re.search(r"\b" + pattern + r"\b", content):
            return (
                "LOW",
                f"Minor non-disruptive maintenance or cosmetic issue ('{pattern}')."
            )

    # Default to MEDIUM for standard issues, LOW if very brief
    if len(text.split()) < 4:
        return ("LOW", "Brief single-user maintenance report.")
        
    return ("MEDIUM", "Standard priority campus operational issue.")
