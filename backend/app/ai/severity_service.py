"""
Component B: Severity Prediction with Deterministic Safety Safeguards.
Combines contextual analysis with hard emergency safety rules, categorized critical
trigger overrides (Ragging, Sexual Misconduct, Physical Hazards, Violence, Acute Medical),
and deterministic routing target department mapping.
"""
import re
from typing import Tuple, Dict, Any, List, Optional
from pydantic import BaseModel

from .gemini_client import get_gemini_client

# Categorized Critical Safety Trigger Definitions
CRITICAL_SAFETY_CATEGORIES = [
    {
        "category_name": "Anti-Ragging / Safeguarding",
        "target_department": "Anti-Ragging / Safeguarding",
        "patterns": [
            # Ragging / Bullying / Hazing
            r"\b(ragging|ragged|bully|bullying|bullied|hazing|hazed)\b",
            r"\b(senior\s+harassment|threatened\s+by\s+seniors?|forced\s+by\s+seniors?)\b",
            r"\b(mental\s+harassment|intimidation|blackmail|hostel\s+ragging)\b",
            # Sexual Misconduct
            r"\b(sexual\s+harassment|sexual\s+assault|molestation|molested|stalking|stalked|stalker)\b",
            r"\b(inappropriate\s+touch(?:ing)?|groping|non-consensual|posh|eve\s+teasing|indecent\s+exposure)\b"
        ],
        "reason": "Zero-tolerance anti-ragging & student safeguarding violation detected. Direct escalation to Anti-Ragging Committee."
    },
    {
        "category_name": "Security & Safety",
        "target_department": "Security & Safety",
        "patterns": [
            # Physical Hazards
            r"\b(fire|smoke|burning\s+smell|flames)\b",
            r"\b(electric\s+shock|live\s+wire|sparking|short\s+circuit|electrocution)\b",
            r"\b(gas\s+leak|chemical\s+spill|toxic\s+fumes|explosion)\b",
            r"\b(collapsed|structural\s+collapse|ceiling\s+falling|roof\s+collapse)\b",
            # Violence / Weapon Altercations
            r"\b(physical\s+fight|assault|physical\s+assault|stabbing|knife|weapon|beaten\s+up|beating|mob\s+attack|violence|violent\s+clash)\b",
            # Acute Life-Safety Medical Emergencies
            r"\b(unconscious|severe\s+bleeding|medical\s+emergency|cardiac\s+arrest|heart\s+attack|seizure|overdose|poisoning|ambulance\s+needed)\b"
        ],
        "reason": "Active physical safety hazard, violence, or acute medical emergency detected. Emergency safety response protocol."
    }
]

HIGH_IMPACT_PATTERNS = [
    (r"\b(slippery|slip hazard|slipping)\b", "Corridor slipping hazard resulting from flooding/spill"),
    (r"\b(pipe burst|flooding|water gushing|water leak)\b", "Significant water damage or flooding"),
    (r"\b(no water|water outage|blackout|power outage)\b", "Essential amenity outage"),
    (r"\b(entire hostel|entire block|whole building|all rooms|every student|widespread)\b", "Widespread multi-resident disruption"),
    (r"\b(undercooked|spoiled|food poisoning|contaminated|worms|cockroach in food|insects? in food)\b", "Severe food hygiene or dietary health risk")
]

def check_critical_safety_override(text: str) -> Optional[Tuple[str, str, str, str]]:
    """
    Performs token-level and regex pattern matching over text for critical safety triggers.
    Returns: (target_department, category_name, matched_trigger, reason) or None.
    Target department is strictly mapped to either 'Anti-Ragging / Safeguarding' or 'Security & Safety'.
    """
    if not text:
        return None
    text_lower = text.lower()
    for cat in CRITICAL_SAFETY_CATEGORIES:
        dept = cat["target_department"]
        cat_name = cat["category_name"]
        reason = cat["reason"]
        for p in cat["patterns"]:
            match = re.search(p, text_lower)
            if match:
                trigger = match.group(0)
                return (dept, cat_name, trigger, reason)
    return None

class SeverityEvaluation(BaseModel):
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    reasoning: str
    confidence: float
    is_safety_critical: bool
    emergency_trigger: Optional[str] = None
    evaluated_by: str  # "deterministic_safety_guard" | "gemini_free_tier" | "rule_heuristic"
    recalculated: bool = False
    target_department: Optional[str] = None
    critical_category: Optional[str] = None

class SeverityService:
    def __init__(self):
        self.gemini_client = get_gemini_client()

    def evaluate_severity(
        self,
        full_conversation_text: str,
        category: str = "",
        location: str = "",
        previous_severity: Optional[str] = None
    ) -> SeverityEvaluation:
        """
        Evaluates complaint severity.
        Deterministic safety safeguards take absolute precedence over model outputs.
        """
        text_lower = full_conversation_text.lower()
        
        # 1. HARD DETERMINISTIC SAFETY SAFEGUARD (Categorized Critical Trigger Overrides)
        # Any immediate safety, violence, sexual misconduct, or ragging issue MUST trigger CRITICAL.
        crit_match = check_critical_safety_override(text_lower)
        if crit_match:
            dept, cat_name, trigger_word, reason = crit_match
            return SeverityEvaluation(
                severity="CRITICAL",
                reasoning=f"Critical safety override: '{trigger_word}'. {reason}",
                confidence=0.99,
                is_safety_critical=True,
                emergency_trigger=trigger_word,
                evaluated_by="deterministic_safety_guard",
                recalculated=bool(previous_severity),
                target_department=dept,
                critical_category=cat_name
            )

        # 2. Hard High-Impact Safeguards
        for pattern, reason in HIGH_IMPACT_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                trigger_word = match.group(0)
                return SeverityEvaluation(
                    severity="HIGH",
                    reasoning=f"High operational or hazard impact trigger detected: '{trigger_word}'. {reason}.",
                    confidence=0.96,
                    is_safety_critical=False,
                    emergency_trigger=None,
                    evaluated_by="deterministic_safety_guard",
                    recalculated=bool(previous_severity)
                )

        # 3. Contextual model evaluation for nuanced cases
        if self.gemini_client.is_available:
            prompt = f"""
Evaluate the severity of this institutional campus issue:
Text: {full_conversation_text}
Category: {category}
Location: {location}

Allowed Severity Levels:
- LOW: Minor inconvenience, single-user non-disruptive cosmetic or routine repair
- MEDIUM: Significant disruption to routine operation, classroom appliance, or room amenity
- HIGH: Widespread disruption, worsening leak, or multi-person impact
- CRITICAL: Credible threat to personal safety or emergency

Return JSON:
{{
  "severity": "LOW, MEDIUM, HIGH, or CRITICAL",
  "reasoning": "1-2 sentence evidence-backed rationale",
  "confidence": 0.93
}}
"""
            result = self.gemini_client.generate_structured_json(
                prompt=prompt,
                system_instruction="You are a safety and operational severity evaluator. Return strictly valid JSON."
            )
            if result.success and result.data:
                pred_sev = result.data.get("severity", "MEDIUM").upper()
                if pred_sev in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                    return SeverityEvaluation(
                        severity=pred_sev,
                        reasoning=result.data.get("reasoning", "Assessed via contextual conversational model."),
                        confidence=float(result.data.get("confidence", 0.92)),
                        is_safety_critical=pred_sev == "CRITICAL",
                        emergency_trigger=None,
                        evaluated_by=result.provider,
                        recalculated=bool(previous_severity)
                    )

        # 4. Fallback Rule Heuristics
        minor_patterns = [r"noisy fan", r"loose", r"tube light", r"minor", r"squeak", r"squeaky", r"bulb flicker", r"handle", r"desk handle", r"scratched"]
        for p in minor_patterns:
            if re.search(r"\b" + p + r"\b", text_lower):
                return SeverityEvaluation(
                    severity="LOW",
                    reasoning=f"Minor non-urgent maintenance issue ('{p}').",
                    confidence=0.90,
                    is_safety_critical=False,
                    emergency_trigger=None,
                    evaluated_by="rule_heuristic",
                    recalculated=bool(previous_severity)
                )

        # Default standard priority
        return SeverityEvaluation(
            severity="MEDIUM",
            reasoning="Standard operational maintenance or campus amenity disruption.",
            confidence=0.88,
            is_safety_critical=False,
            emergency_trigger=None,
            evaluated_by="rule_heuristic",
            recalculated=bool(previous_severity)
        )
