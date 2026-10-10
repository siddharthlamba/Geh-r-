"""
Component A: Complete Conversation Understanding.
Analyzes the entire multi-turn conversation associated with a complaint.
Produces structured, validated representation distinguishing between explicit facts and inferences.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import re

from .gemini_client import get_gemini_client
from .severity_service import check_critical_safety_override
from ..config import CATEGORIES, DEFAULT_ROUTING

CONVERSATIONAL_TOKENS = {
    "hi", "hello", "hey", "help", "thanks", "thank", "you", "thx", "ok", "okay",
    "k", "who", "are", "you", "what", "is", "this", "sup", "yo", "good",
    "morning", "afternoon", "evening", "greetings", "test", "testing", "namaste",
    "start", "info", "please"
}

CONVERSATIONAL_PHRASES = {
    "hi", "hello", "hey", "help", "thanks", "thank you", "thx", "ok", "okay",
    "k", "who are you", "who r u", "what is this", "what is gehor", "what can you do",
    "good morning", "good afternoon", "good evening", "greetings", "test",
    "testing", "yo", "sup", "howdy", "namaste", "help me", "start"
}

ACTIONABLE_SYMPTOM_KEYWORDS = [
    "broken", "leak", "leaking", "water", "pipe", "tap", "drain", "flood", "sewage",
    "wifi", "wi-fi", "internet", "network", "router", "lan", "eduroam", "portal",
    "fan", "light", "bulb", "tube", "ac", "air condition", "cooler", "cooling",
    "spark", "sparking", "shock", "wire", "power", "blackout", "fuse",
    "mess", "food", "canteen", "meal", "dinner", "lunch", "breakfast",
    "clean", "dirty", "trash", "dustbin", "sweep", "mop", "washroom", "toilet", "stink", "smell",
    "plant", "plants", "tree", "trees", "garden", "lawn", "grass", "flower", "ground", "soil",
    "ragging", "ragged", "bully", "bullying", "bullied", "hazing", "hazed",
    "harass", "harassment", "assault", "stalking", "threat", "fight", "beaten",
    "unconscious", "bleeding", "ambulance", "theft", "stolen", "lost", "bus", "shuttle"
]

GREETING_RESPONSE = "Hello! 👋 How can I help you today? Please describe the campus issue or grievance you would like to report."

def is_conversational_greeting(text: str) -> bool:
    """
    Checks if user input contains only conversational tokens or greetings with no actionable symptoms.
    Normalizes user input (lowercase, strip trailing punctuation/whitespace).
    """
    if not text:
        return False
    # Normalize: lowercase, strip punctuation and whitespace
    normalized = re.sub(r"[^\w\s]", "", text.lower()).strip()
    if not normalized:
        return False

    # Exact match against known greeting phrases
    if normalized in CONVERSATIONAL_PHRASES:
        return True

    # Reject if any actionable symptom keywords are present
    if any(s in normalized for s in ACTIONABLE_SYMPTOM_KEYWORDS):
        return False

    # Check if all tokens are conversational tokens and message is short
    tokens = normalized.split()
    if len(tokens) <= 5 and all(t in CONVERSATIONAL_TOKENS for t in tokens):
        return True

    return False

class ConversationAnalysis(BaseModel):
    complaint_summary: str
    original_problem_description: str
    relevant_location: str
    category: str
    subcategory: str
    reported_symptoms: List[str]
    potential_impact: str
    urgency_indicators: List[str]
    missing_information: List[str]
    recommended_responsible_department: str
    recommended_severity: str
    confidence_estimates: Dict[str, float]
    explicit_facts: List[str]
    inferred_details: List[str]
    inference_provider: str  # "gemini_free_tier" or "rule_fallback"
    model_version: str

class ConversationAnalyzer:
    def __init__(self):
        self.gemini_client = get_gemini_client()

    def analyze_conversation(
        self,
        messages: List[Dict[str, str]],
        initial_context: Optional[Dict[str, Any]] = None
    ) -> ConversationAnalysis:
        """
        Analyzes the complete conversation sequence.
        """
        # 1. Format complete dialogue transcript
        transcript_lines = []
        student_texts = []
        for m in messages:
            sender = m.get("sender", "student")
            content = m.get("content", "").strip()
            if not content:
                continue
            transcript_lines.append(f"{sender.upper()}: {content}")
            if sender.lower() == "student":
                student_texts.append(content)

        full_transcript = "\n".join(transcript_lines)
        combined_student_text = " ".join(student_texts)

        # 2. Intent Guard: Pure conversational greeting check
        if is_conversational_greeting(combined_student_text):
            return ConversationAnalysis(
                complaint_summary="Conversational Greeting",
                original_problem_description="",
                relevant_location="Campus",
                category="Other",
                subcategory="Greeting",
                reported_symptoms=[],
                potential_impact="None (Conversational greeting)",
                urgency_indicators=[],
                missing_information=["Campus issue or grievance description"],
                recommended_responsible_department="Administration",
                recommended_severity="LOW",
                confidence_estimates={"classification": 1.0, "routing": 1.0},
                explicit_facts=[],
                inferred_details=[],
                inference_provider="deterministic_guard",
                model_version="conversational_intent_guard"
            )

        # 3. Deterministic Safety Override Check
        crit_match = check_critical_safety_override(combined_student_text)
        if crit_match:
            dept, cat_name, trigger_word, reason = crit_match
            loc = self._extract_location_fallback(combined_student_text)
            return ConversationAnalysis(
                complaint_summary=f"Critical Incident: {combined_student_text[:120]}",
                original_problem_description=combined_student_text,
                relevant_location=loc,
                category=cat_name,
                subcategory="Safety Override",
                reported_symptoms=[f"Critical trigger '{trigger_word}' detected"],
                potential_impact="Immediate personal safety or student safeguarding concern",
                urgency_indicators=[f"Deterministic safety override: {reason}"],
                missing_information=[],
                recommended_responsible_department=dept,
                recommended_severity="CRITICAL",
                confidence_estimates={"classification": 0.99, "routing": 0.99},
                explicit_facts=student_texts,
                inferred_details=[],
                inference_provider="deterministic_safety_guard",
                model_version="safety_guard"
            )

        # 4. Try Local LLM Inference first if available
        if self.gemini_client.is_available:
            prompt = self._build_gemini_prompt(full_transcript, initial_context)
            result = self.gemini_client.generate_structured_json(
                prompt=prompt,
                system_instruction=(
                    "You are the Gehor Institutional Grievance Analysis Engine. "
                    "Analyze the conversation objectively and strictly base your analysis on the actual symptoms described by the user.\n"
                    "MANDATORY INSTRUCTIONS:\n"
                    "1. Strictly base follow-up questions, category, and missing information on the actual symptoms described by the user.\n"
                    "2. Explicitly FORBID assuming or defaulting to IT / Network unless tech-specific keywords (e.g. wifi, router, network, internet, portal, eduroam) are explicitly stated.\n"
                    "3. If the complaint concerns plants, gardening, trees, flowers, grass, lawn, grounds, or landscaping, assign category 'Landscaping & Groundskeeping' and recommend department 'Facilities & Groundskeeping'.\n"
                    "4. Gracefully and completely accept user corrections when the user clarifies or corrects an earlier AI misunderstanding.\n"
                    "5. Distinguish explicit facts from inferences. Do not fabricate missing details. Output strictly valid JSON."
                )
            )

            if result.success and result.data:
                try:
                    d = result.data
                    return ConversationAnalysis(
                        complaint_summary=d.get("complaint_summary", combined_student_text[:120]),
                        original_problem_description=d.get("original_problem_description", student_texts[0] if student_texts else ""),
                        relevant_location=d.get("relevant_location", "Unknown Location"),
                        category=d.get("category", "Infrastructure"),
                        subcategory=d.get("subcategory", "General Maintenance"),
                        reported_symptoms=d.get("reported_symptoms", []),
                        potential_impact=d.get("potential_impact", "Standard campus disruption"),
                        urgency_indicators=d.get("urgency_indicators", []),
                        missing_information=d.get("missing_information", []),
                        recommended_responsible_department=d.get("recommended_responsible_department", "Maintenance & Engineering"),
                        recommended_severity=d.get("recommended_severity", "MEDIUM"),
                        confidence_estimates=d.get("confidence_estimates", {"classification": 0.94, "routing": 0.91}),
                        explicit_facts=d.get("explicit_facts", student_texts),
                        inferred_details=d.get("inferred_details", []),
                        inference_provider=result.provider,
                        model_version=result.model
                    )
                except Exception as parse_err:
                    # Fall through to deterministic fallback if parsing unexpected structure
                    pass

        # 3. Deterministic Python Heuristic Fallback (Transparently marked)
        return self._deterministic_fallback_analysis(student_texts, full_transcript, initial_context)

    def _build_gemini_prompt(self, transcript: str, context: Optional[Dict[str, Any]]) -> str:
        categories_str = ", ".join(CATEGORIES)
        return f"""
Analyze the following student complaint conversation in an educational campus setting:

--- TRANSCRIPT ---
{transcript}
--- END TRANSCRIPT ---

Existing context: {context or {}}

Allowed Categories: {categories_str}
Allowed Severities: LOW, MEDIUM, HIGH, CRITICAL

RULES FOR ANALYSIS:
- Strictly base category, symptoms, and routing recommendations on the ACTUAL symptoms described by the student.
- DO NOT assume or default to 'IT / Network' unless tech-specific keywords (e.g. wifi, internet, router, network, eduroam) are explicitly stated.
- If the issue involves plants, trees, flowers, lawn, grass, gardens, grounds, or landscaping, assign category 'Landscaping & Groundskeeping' and department 'Facilities & Groundskeeping'.
- If the student provides a correction (e.g., correcting an AI misunderstanding), prioritize the student's correction over previous turns.
- Missing information must only ask for relevant details grounded in the actual reported domain (e.g. for plants: specific garden/gate/lawn location; never Wi-Fi/network questions).

Return a JSON object with EXACTLY the following structure:
{{
  "complaint_summary": "1-2 sentence objective executive brief of the problem",
  "original_problem_description": "the primary issue reported by student",
  "relevant_location": "building, block, floor, or room number if stated, else 'Unknown'",
  "category": "most accurate category from Allowed Categories",
  "subcategory": "specific subcategory name",
  "reported_symptoms": ["list of explicit observations or symptoms reported"],
  "potential_impact": "impact on students, safety, or academic routine",
  "urgency_indicators": ["any time-sensitive or deteriorating indicators"],
  "missing_information": ["vital unconfirmed details e.g. room number, leak source, scope - strictly relevant to this domain"],
  "recommended_responsible_department": "institution department (IT Services, Maintenance & Engineering, Facilities & Groundskeeping, Food & Catering, Hostel Administration, Housekeeping & Cleanliness, Security Office, Academic Administration, Transport Office)",
  "recommended_severity": "LOW, MEDIUM, HIGH, or CRITICAL",
  "confidence_estimates": {{"classification": 0.95, "routing": 0.92, "severity": 0.90}},
  "explicit_facts": ["facts stated directly by student"],
  "inferred_details": ["inferences deduced by context"]
}}
"""

    def _extract_location_fallback(self, text: str) -> str:
        loc_patterns = [
            r"((?:main\s+|back\s+|north\s+|south\s+)?gate(?:\s*\d*)?)",
            r"((?:botanical\s+|central\s+)?garden)",
            r"((?:central\s+|main\s+)?lawn)",
            r"(hostel\s+(?:block\s+)?[A-Za-z0-9]+(?:\s*,\s*(?:room|staircase|\d+)[A-Za-z0-9\s]*)?)",
            r"(block\s+[A-Za-z0-9]+(?:\s*,\s*(?:room|\d+|floor)[A-Za-z0-9\s]*)?)",
            r"(room\s*(?:no\.?)?\s*[A-Za-z0-9\-]+)",
            r"([A-Za-z]\s*-\s*\d{3,4})",
            r"(chemistry\s+lab\s*\d*)",
            r"(physics\s+lab\s*\d*)",
            r"(library(?:\s+\w+)?)",
            r"(mess\s+(?:hall\s+)?[A-Za-z0-9]*)",
            r"(dining\s+hall\s*[A-Za-z0-9]*)",
            r"(cafeteria\s*[A-Za-z0-9]*)"
        ]
        for p in loc_patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(0).strip().title()
        return "Campus"

    def _deterministic_fallback_analysis(
        self,
        student_texts: List[str],
        full_transcript: str,
        initial_context: Optional[Dict[str, Any]]
    ) -> ConversationAnalysis:
        combined = " ".join(student_texts)
        lower = combined.lower()

        # Deterministic Safety Override Check
        crit_match = check_critical_safety_override(combined)
        if crit_match:
            dept, cat_name, trigger_word, reason = crit_match
            loc = self._extract_location_fallback(combined)
            return ConversationAnalysis(
                complaint_summary=f"Critical Incident: {combined[:120]}",
                original_problem_description=combined,
                relevant_location=loc,
                category=cat_name,
                subcategory="Safety Override",
                reported_symptoms=[f"Critical trigger '{trigger_word}' detected"],
                potential_impact="Immediate personal safety or student safeguarding concern",
                urgency_indicators=[f"Deterministic safety override: {reason}"],
                missing_information=[],
                recommended_responsible_department=dept,
                recommended_severity="CRITICAL",
                confidence_estimates={"classification": 0.99, "routing": 0.99},
                explicit_facts=student_texts,
                inferred_details=[],
                inference_provider="deterministic_safety_guard",
                model_version="safety_guard"
            )

        # Extract location
        loc = self._extract_location_fallback(combined)

        if initial_context and initial_context.get("location"):
            loc = initial_context.get("location")

        # Category and department detection
        cat = initial_context.get("category") if (initial_context and initial_context.get("category")) else "Infrastructure"
        subcat = initial_context.get("subcategory") if (initial_context and initial_context.get("subcategory")) else "General Maintenance"
        dept = DEFAULT_ROUTING.get(cat, "Maintenance & Engineering")
        symptoms = []
        impact = "Routine amenity disruption"
        urgency = []
        missing = []

        if not initial_context or not initial_context.get("category"):
            if any(w in lower for w in ["plant", "plants", "tree", "trees", "garden", "gardening", "grass", "lawn", "flower", "landscaping", "groundskeeping", "botanical", "horticulture"]):
                cat = "Landscaping & Groundskeeping"
                subcat = "Horticulture & Grounds"
                dept = "Facilities & Groundskeeping"
                symptoms.append("Dying plants or unmaintained campus grounds")
                impact = "Campus aesthetics and botanical green cover"
            elif any(w in lower for w in ["wifi", "wi-fi", "internet", "network", "router"]) or re.search(r"\blan\b", lower):
                cat = "IT / Network"
                subcat = "Wi-Fi & Connectivity"
                dept = "IT Services"
                symptoms.append("Network connectivity downtime")
                impact = "Academic research and digital access blocked"
            elif any(w in lower for w in ["water", "leak", "pipe", "tap", "drain", "flood", "sewage"]):
                cat = "Plumbing"
                subcat = "Water Supply & Plumbing"
                dept = "Maintenance & Engineering"
                symptoms.append("Water leakage or piping failure")
                impact = "Potential water damage, flooding, or slippery floor hazard"
                if "slippery" in lower or "floor" in lower:
                    urgency.append("Slip and fall hazard in pedestrian corridor")
            elif any(w in lower for w in ["spark", "shock", "live wire", "electric", "short circuit", "power cut"]):
                cat = "Electrical"
                subcat = "Wiring & Power Sockets"
                dept = "Maintenance & Engineering"
                symptoms.append("Electrical sparking or failure")
                impact = "Electrical hazard and personal safety risk"
                urgency.append("Active electrical hazard")
            elif any(w in lower for w in ["mess", "food", "dinner", "lunch", "meal", "canteen"]):
                cat = "Mess / Food"
                subcat = "Food Quality & Catering"
                dept = "Food & Catering"
                symptoms.append("Meal hygiene or catering grievance")
                impact = "Student dietary health and mess operational quality"
            elif any(w in lower for w in ["hostel", "warden", "curfew", "roommate", "bed"]):
                cat = "Hostel"
                subcat = "Hostel Living"
                dept = "Hostel Administration"
                symptoms.append("Residential welfare grievance")
                impact = "Hostel accommodation standard"
            elif any(w in lower for w in ["bus", "shuttle", "transport", "driver"]):
                cat = "Transport"
                subcat = "Campus Transit"
                dept = "Transport Office"
                symptoms.append("Shuttle transit schedule irregularity")
                impact = "Student campus commute delays"
            elif any(w in lower for w in ["washroom dirty", "clean", "dustbin", "trash", "pest"]):
                cat = "Cleanliness"
                subcat = "Sanitation & Housekeeping"
                dept = "Housekeeping & Cleanliness"
                symptoms.append("Sanitation or housekeeping requirement")
                impact = "Hygiene standard in communal spaces"
            elif any(w in lower for w in ["prof", "professor", "faculty", "exam", "grade", "course", "lecture", "academic", "attendance", "syllabus"]):
                cat = "Academic"
                subcat = "Academic Grievance"
                dept = "Academic Administration"
                symptoms.append("Curriculum or lecture schedule concern")
                impact = "Academic progression and course learning"
            elif any(w in lower for w in ["security", "guard", "theft", "stolen", "lost", "cctv", "parking", "harass"]) or ("gate" in lower and not any(w in lower for w in ["plant", "plants", "tree", "garden", "grass", "flower", "landscaping"])):
                cat = "Security"
                subcat = "Campus Safety & Security"
                dept = "Security Office"
                symptoms.append("Security or property concern")
                impact = "Campus physical security and student safety"

        if loc == "Campus":
            missing.append("Exact room, floor, or building block")

        # Severity estimate
        sev = "MEDIUM"
        if any(w in lower for w in ["fire", "hazard", "smoke", "spark", "electric shock", "gas leak"]):
            sev = "CRITICAL"
        elif any(w in lower for w in ["pipe burst", "no water", "flooding", "slippery", "entire hostel", "blackout"]):
            sev = "HIGH"
        elif any(w in lower for w in ["noisy fan", "loose", "minor", "bulb flicker", "plant", "plants", "garden", "lawn", "flower", "groundskeeping"]):
            sev = "LOW"

        # Summary
        summary = f"{cat} incident reported at {loc}: {student_texts[0][:80] if student_texts else 'Issue reported'}"

        return ConversationAnalysis(
            complaint_summary=summary,
            original_problem_description=student_texts[0] if student_texts else "Student reported issue",
            relevant_location=loc,
            category=cat,
            subcategory=subcat,
            reported_symptoms=symptoms or ["Amenity non-functional"],
            potential_impact=impact,
            urgency_indicators=urgency,
            missing_information=missing,
            recommended_responsible_department=dept,
            recommended_severity=sev,
            confidence_estimates={"classification": 0.94, "routing": 0.91, "severity": 0.90},
            explicit_facts=student_texts,
            inferred_details=[f"Mapped to {dept} based on institutional policy matrix"],
            inference_provider="rule_fallback",
            model_version="deterministic_nlp_v1"
        )
