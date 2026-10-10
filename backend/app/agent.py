"""
Gehor Conversational AI Agent Core.
Handles multi-turn dialog, slot extraction, intent detection,
tool execution, and confirmation lifecycle.
"""
import json
import re
import datetime
import random
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session

from .models import Complaint, ComplaintEvent, ChatSession, ChatMessage
from .severity import calculate_severity
from .routing import route_complaint
from .duplicates import check_duplicate_complaints
from .knowledge import search_knowledge
from .config import CATEGORIES
from .ai.conversation_analyzer import is_conversational_greeting, GREETING_RESPONSE
from .ai.severity_service import check_critical_safety_override

def generate_complaint_id(db: Session) -> str:
    """
    Generates format: GH-2026-1042
    """
    year = datetime.datetime.now(datetime.UTC).year
    # Count existing complaints to produce incremental number
    count = db.query(Complaint).count()
    new_num = 1040 + count + 1
    # Check uniqueness
    candidate = f"GH-{year}-{new_num}"
    while db.query(Complaint).filter(Complaint.id == candidate).first():
        new_num += 1
        candidate = f"GH-{year}-{new_num}"
    return candidate

def detect_category(text: str) -> Tuple[str, str, float]:
    """
    Classifies complaint text into (category, subcategory, confidence).
    """
    t = text.lower()
    
    # 0. Deterministic Safety Override (Absolute Priority)
    crit = check_critical_safety_override(t)
    if crit:
        dept, cat_name, trigger, reason = crit
        return (cat_name, "Safeguarding Incident", 0.99)

    # 1. Landscaping & Groundskeeping (evaluated first so campus outdoor grounds/plants at gates aren't hijacked)
    if any(k in t for k in ["plant", "plants", "tree", "trees", "garden", "gardening", "grass", "lawn", "flower", "flowers", "landscaping", "groundskeeping", "botanical", "watering", "horticulture"]):
        return ("Landscaping & Groundskeeping", "Horticulture & Grounds", 0.95)

    # 2. Electrical / Power
    if any(k in t for k in ["electric", "shock", "spark", "short circuit", "switch", "wiring", "socket", "power strip", "fuse"]):
        return ("Electrical", "Wiring & Power Sockets", 0.95)
        
    # 3. Plumbing / Water
    if any(k in t for k in ["water", "leak", "pipe", "tap", "flush", "drain", "sewage", "faucet", "shower"]):
        return ("Plumbing", "Water Supply & Plumbing", 0.96)
        
    # 4. IT / Network
    if any(k in t for k in ["wifi", "wi-fi", "internet", "network", "router", "signal", "portal", "login", "eduroam"]) or re.search(r"\blan\b", t):
        return ("IT / Network", "Wi-Fi & Connectivity", 0.96)
        
    # 5. Mess / Food
    if any(k in t for k in ["mess", "food", "canteen", "meal", "breakfast", "lunch", "dinner", "unhygienic", "taste", "cook"]):
        return ("Mess / Food", "Food Quality & Catering", 0.93)
        
    # 6. Cleanliness
    if any(k in t for k in ["clean", "dirty", "trash", "dustbin", "sweep", "mop", "smell", "stink", "washroom dirty", "pest", "cockroach"]):
        return ("Cleanliness", "Sanitation & Housekeeping", 0.94)
        
    # 7. Infrastructure / Room appliances
    if any(k in t for k in ["ac", "air condition", "fan", "cooling", "projector", "chair", "table", "bench", "door", "window", "lock", "lift", "elevator"]):
        sub = "HVAC / Cooling" if "ac" in t or "cool" in t else "Classroom / Room Fixture"
        return ("Infrastructure", sub, 0.92)
        
    # 8. Security / Safety
    if any(k in t for k in ["security", "guard", "theft", "stolen", "lost", "cctv", "parking", "harass", "threat"]) or ("gate" in t and not any(k in t for k in ["plant", "plants", "tree", "garden", "grass", "flower", "landscaping"])):
        return ("Security", "Campus Safety & Security", 0.95)
        
    # 9. Transport
    if any(k in t for k in ["bus", "shuttle", "transport", "driver", "route", "van"]):
        return ("Transport", "Campus Transit", 0.93)
        
    # 10. Academic
    if any(k in t for k in ["prof", "faculty", "exam", "grade", "class", "lecture", "library", "attendance", "course"]):
        return ("Academic", "Academic Grievance", 0.90)
        
    # 11. Hostel General
    if any(k in t for k in ["hostel", "room", "warden", "curfew", "allotment", "roommate", "bed", "cupboard"]):
        return ("Hostel", "Hostel Living", 0.91)
        
    return ("Other", "General Inquiry", 0.80)

def extract_location(text: str) -> Optional[str]:
    """
    Extracts location details such as Block C, Room 204, 3rd Floor, Hostel Block B, Main Gate, etc.
    """
    patterns = [
        r"((?:main\s+|back\s+|north\s+|south\s+)?gate(?:\s*\d*)?)",
        r"((?:botanical\s+|central\s+)?garden)",
        r"((?:central\s+|main\s+)?lawn)",
        r"(hostel\s+(?:block\s+)?[A-Za-z0-9]+(?:\s*,\s*(?:room|staircase|\d+)[A-Za-z0-9\s]*)?)",
        r"(block\s+[A-Za-z0-9]+(?:\s*,\s*(?:room|\d+|floor)[A-Za-z0-9\s]*)?)",
        r"(room\s*(?:no\.?)?\s*[A-Za-z0-9\-]+)",
        r"([A-Za-z]\s*-\s*\d{3,4})",
        r"(chemistry\s+lab\s*\d*)",
        r"(physics\s+lab\s*\d*)",
        r"(computer\s+lab\s*\d*)",
        r"(library(?:\s+\w+)?)",
        r"(mess\s+(?:hall\s+)?[A-Za-z0-9]*)",
        r"(dining\s+hall\s*[A-Za-z0-9]*)",
        r"((?:central\s+|main\s+)?cafeteria(?:\s+(?:hall|court|area|\d+))?)",
        r"(auditorium)",
        r"(?:in|at|near)\s+([A-Za-z0-9\-–\s]{2,30})"
    ]
    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            loc = match.group(0).strip(" .,!?:")
            # Clean leading 'in ', 'at ', 'near '
            loc = re.sub(r"^(in|at|near)\s+", "", loc, flags=re.IGNORECASE)
            return loc.title()
    return None

class GehorAgent:
    """
    Stateful conversational agent managing conversation turns.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def process_message(
        self,
        session_id: str,
        user_message: str,
        student_id: str = "STU-2026-901",
        evidence_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main dialog pipeline.
        """
        # 1. Fetch or create session
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            session = ChatSession(
                id=session_id,
                student_id=student_id,
                state="GREETING",
                extracted_data="{}"
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            
        # Record user message in DB
        user_chat_msg = ChatMessage(
            session_id=session_id,
            sender="student",
            content=user_message,
            message_type="text" if not evidence_url else "image",
            metadata_json=json.dumps({"evidence_url": evidence_url}) if evidence_url else None
        )
        self.db.add(user_chat_msg)
        self.db.commit()

        # Parse current draft from session
        try:
            draft = json.loads(session.extracted_data) if session.extracted_data else {}
        except Exception:
            draft = {}

        if evidence_url and not draft.get("evidence_url"):
            draft["evidence_url"] = evidence_url

        cleaned_msg = user_message.strip()
        msg_lower = cleaned_msg.lower()

        # ----------------------------------------------------
        # Intent Check 1: Direct Complaint Tracking
        # e.g., "track GH-2026-1042" or "GH-2026-1035 status"
        # ----------------------------------------------------
        track_match = re.search(r"(GH-\d{4}-\d{4})", cleaned_msg, re.IGNORECASE)
        if track_match or "track" in msg_lower:
            complaint_id = track_match.group(1).upper() if track_match else None
            if not complaint_id and draft.get("last_complaint_id"):
                complaint_id = draft.get("last_complaint_id")
                
            if complaint_id:
                complaint = self.db.query(Complaint).filter(Complaint.id == complaint_id).first()
                if complaint:
                    reply_text = (
                        f"🔍 **Status for Complaint #{complaint.id}**\n\n"
                        f"• **Issue:** {complaint.title}\n"
                        f"• **Location:** {complaint.location}\n"
                        f"• **Status:** `{complaint.status}`\n"
                        f"• **Category:** {complaint.category}\n"
                        f"• **Department:** {complaint.department_name}\n"
                        f"• **Assigned Staff:** {complaint.assigned_to or 'Pending assignment'}\n"
                        f"• **Submitted:** {complaint.created_at.strftime('%b %d, %Y at %I:%M %p')}\n\n"
                        f"Would you like to track another issue or report a new problem?"
                    )
                    self._save_ai_message(session_id, reply_text, "text")
                    return {
                        "session_id": session_id,
                        "reply": reply_text,
                        "message_type": "text",
                        "state": "TRACKING",
                        "complaint_id": complaint.id,
                        "quick_options": ["Report another issue", f"Track {complaint.id} details"]
                    }
                else:
                    reply_text = f"We couldn't find any complaint matching ID `{complaint_id}`. Please verify your ID or enter another one."
                    self._save_ai_message(session_id, reply_text, "text")
                    return {
                        "session_id": session_id,
                        "reply": reply_text,
                        "message_type": "text",
                        "state": "TRACKING"
                    }

        # ----------------------------------------------------
        # Intent Check 2: FAQ / Institutional Knowledge Base
        # e.g. "what are mess timings", "gate pass rules", "clinic hours"
        # ----------------------------------------------------
        is_faq_query = any(k in msg_lower for k in [
            "timings", "timing", "rules", "rule", "gate pass", "curfew", "hours",
            "how to connect", "clinic", "ambulance number", "bus schedule", "sla"
        ])
        if is_faq_query and session.state not in ["CONFIRMATION", "COLLECTING_INFO"]:
            faq_results = search_knowledge(cleaned_msg, self.db)
            if faq_results:
                best = faq_results[0]
                reply_text = (
                    f"📚 **{best['title']}**\n\n"
                    f"{best['content']}\n\n"
                    f"Is there anything specific in {best['category']} you need to report as an issue?"
                )
                self._save_ai_message(session_id, reply_text, "text")
                return {
                    "session_id": session_id,
                    "reply": reply_text,
                    "message_type": "text",
                    "state": "GREETING",
                    "quick_options": ["Report an Issue", "Ask another question"]
                }

        # ----------------------------------------------------
        # Intent Check 2.5: Conversational Greeting Guard
        # ----------------------------------------------------
        if is_conversational_greeting(cleaned_msg) and not draft.get("description"):
            session.state = "IDLE"
            self.db.commit()
            self._save_ai_message(session_id, GREETING_RESPONSE, "text")
            return {
                "session_id": session_id,
                "reply": GREETING_RESPONSE,
                "message_type": "text",
                "state": "IDLE",
                "quick_options": ["Report an Issue", "Track Complaint", "Campus FAQ"]
            }

        # Check if user provided an email address in this turn
        email_in_msg = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", cleaned_msg)
        if email_in_msg and not draft.get("verified_email"):
            draft["verified_email"] = email_in_msg.group(1).lower()

        # ----------------------------------------------------
        # Intent Check: Awaiting Email Verification (Gate for High/Critical)
        # ----------------------------------------------------
        msg_tokens = set(re.findall(r"\b\w+\b", msg_lower))
        is_cancel = bool(msg_tokens.intersection({"no", "cancel", "edit", "change", "restart", "abort"}) or "start over" in msg_lower)

        if session.state == "AWAITING_EMAIL_VERIFICATION":
            if is_cancel:
                session.state = "COLLECTING_INFO"
                self.db.commit()
                reply_text = "No problem! What would you like to update about this issue?"
                self._save_ai_message(session_id, reply_text, "text")
                return {
                    "session_id": session_id,
                    "reply": reply_text,
                    "message_type": "text",
                    "state": "COLLECTING_INFO",
                    "draft_complaint": draft
                }

            if email_in_msg:
                draft["verified_email"] = email_in_msg.group(1).lower()
                session.extracted_data = json.dumps(draft)
                self.db.commit()
                return self._render_confirmation_card(session_id, session, draft)
            else:
                reply_text = (
                    "⚠️ **Invalid Institutional Email**\n\n"
                    "Please provide a valid official institutional email address (e.g., `student@campus.edu` or `rollno@university.edu`) "
                    "to verify this high-priority issue before submission."
                )
                self._save_ai_message(session_id, reply_text, "text")
                return {
                    "session_id": session_id,
                    "reply": reply_text,
                    "message_type": "text",
                    "state": "AWAITING_EMAIL_VERIFICATION",
                    "draft_complaint": draft,
                    "quick_options": ["student@campus.edu", "rahul.s@student.edu"]
                }

        # ----------------------------------------------------
        # Intent Check 3: User Confirmation (Yes / Submit / Confirm)
        # ----------------------------------------------------
        is_confirm = bool(msg_tokens.intersection({"yes", "submit", "confirm", "proceed", "sure", "ok", "yep"}) or "go ahead" in msg_lower or "do it" in msg_lower)

        if session.state == "CONFIRMATION" and is_confirm:
            # Commit the complaint to the database!
            new_id = generate_complaint_id(self.db)
            
            # Query all messages in the session for complete multi-turn conversation understanding
            session_msgs = (
                self.db.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.timestamp.asc())
                .all()
            )
            msg_dicts = [{"sender": m.sender, "content": m.content} for m in session_msgs]
            if not any(m["content"] == cleaned_msg for m in msg_dicts):
                msg_dicts.append({"sender": "student", "content": cleaned_msg})

            # Run complete AI Orchestration: Conversation Understanding, Severity, Routing, Resolution Brief
            from .ai.orchestrator import AIOrchestrator
            orchestrator = AIOrchestrator(self.db)
            try:
                orchestrated = orchestrator.process_full_complaint_intake(
                    complaint_id=new_id,
                    messages=msg_dicts,
                    initial_context=draft
                )
                title = draft.get("title") or orchestrated.analysis.complaint_summary[:70]
                desc = draft.get("description") or orchestrated.analysis.original_problem_description
                cat = orchestrated.analysis.category or draft.get("category", "Infrastructure")
                subcat = orchestrated.analysis.subcategory or draft.get("subcategory", "General")
                loc = orchestrated.analysis.relevant_location or draft.get("location", "Campus")
                sev = orchestrated.severity_eval.severity
                dept = orchestrated.routing_decision.department_name
                assigned_staff = orchestrated.routing_decision.assigned_staff
                reasoning = orchestrated.severity_eval.reasoning
                routing_mode = orchestrated.routing_decision.routing_mode
                routing_confidence = orchestrated.routing_decision.confidence
                routing_rationale = orchestrated.routing_decision.rationale
                ai_summary = orchestrated.ai_summary
                resolution_plan_json = orchestrated.resolution_plan_json
                ai_provider = orchestrated.ai_provider
            except Exception as orch_err:
                import logging
                logging.getLogger("gehor.agent").warning(f"Orchestration exception: {orch_err}. Using confirmed draft.")
                title = draft.get("title") or draft.get("description", "Campus Issue")[:70]
                desc = draft.get("description", "")
                cat = draft.get("category", "Infrastructure")
                subcat = draft.get("subcategory", "General Maintenance")
                loc = draft.get("location", "Campus")
                sev = draft.get("severity", "MEDIUM")
                dept = draft.get("department", "Maintenance & Engineering")
                assigned_staff = orchestrator.routing_service._get_assigned_staff_for_dept(dept)
                reasoning = draft.get("severity_reasoning", "Standard complaint triage.")
                routing_mode = "AUTONOMOUS"
                routing_confidence = 0.95
                routing_rationale = draft.get("routing_reason", f"Routed to {dept}.")
                fallback_brief = orchestrator.resolution_service._generate_grounded_fallback_brief(
                    new_id, title, desc, cat, loc, sev, dept, assigned_staff, "Assigned via confirmed draft.",
                    ["SOP-GEN-01: Standard department response protocol."]
                )
                ai_summary = f"{title} reported at {loc}. Priority: {sev}."
                resolution_plan_json = fallback_brief.model_dump_json()
                ai_provider = "rule_fallback"

            ev_url = draft.get("evidence_url")

            # Create complaint record
            complaint_obj = Complaint(
                id=new_id,
                student_id=student_id,
                student_name="Student Demo",
                student_contact="+91 98765 43210",
                title=title,
                description=desc,
                category=cat,
                subcategory=subcat,
                severity=sev,
                location=loc,
                department_name=dept,
                assigned_to=assigned_staff,
                status="SUBMITTED",
                evidence_url=ev_url,
                ai_confidence=routing_confidence,
                ai_intent="CREATE_COMPLAINT",
                ai_reasoning=reasoning,
                internal_notes=None,
                ai_summary=ai_summary,
                resolution_plan=resolution_plan_json,
                predicted_department=dept,
                routing_confidence=routing_confidence,
                routing_mode=routing_mode,
                ai_provider=ai_provider,
                verified_email=draft.get("verified_email")
            )
            self.db.add(complaint_obj)

            # Create initial audit log events
            event1 = ComplaintEvent(
                complaint_id=new_id,
                event_type="SUBMISSION",
                new_value="SUBMITTED",
                performed_by="Student via Gehor AI",
                notes="Complaint successfully submitted via conversational chat."
            )
            event2 = ComplaintEvent(
                complaint_id=new_id,
                event_type="CLASSIFICATION",
                new_value=f"{cat} / {sev}",
                performed_by="Gehor AI Classifier",
                notes=f"AI assigned category '{cat}' with severity '{sev}'. Reasoning: {reasoning}"
            )
            event3 = ComplaintEvent(
                complaint_id=new_id,
                event_type="ROUTING",
                new_value=dept,
                performed_by=f"Gehor Routing Engine ({routing_mode})",
                notes=f"{routing_rationale}"
            )
            event4 = ComplaintEvent(
                complaint_id=new_id,
                event_type="RESOLUTION_PLAN",
                new_value="GENERATED",
                performed_by=f"Gehor Resolution Engine ({ai_provider})",
                notes="Actionable recipient resolution brief generated grounded in campus SOPs."
            )
            events_to_add = [event1, event2, event3, event4]
            if draft.get("verified_email"):
                event_email = ComplaintEvent(
                    complaint_id=new_id,
                    event_type="EMAIL_VERIFICATION",
                    new_value=draft["verified_email"],
                    performed_by="Student via Gehor AI",
                    notes=f"Identity confirmed with institutional email: {draft['verified_email']}."
                )
                events_to_add.append(event_email)
            self.db.add_all(events_to_add)

            # Reset session state
            session.state = "SUBMITTED"
            session.last_complaint_id = new_id
            session.extracted_data = json.dumps({"last_complaint_id": new_id})
            self.db.commit()

            email_line = f"\n**Verified Email:** `{draft['verified_email']}`" if draft.get("verified_email") else ""
            reply_text = (
                f"Complaint submitted successfully! ✅\n\n"
                f"**Complaint ID:** `{new_id}`\n"
                f"**Assigned Department:** {dept}\n"
                f"**Priority Level:** {sev}\n"
                f"**Routing Mode:** {routing_mode}"
                f"{email_line}\n\n"
                f"We've logged this in the central institutional queue. You can check its real-time progress anytime by saying **'Track {new_id}'** or using the Track page."
            )
            self._save_ai_message(session_id, reply_text, "complaint_submitted", metadata={"complaint_id": new_id})

            return {
                "session_id": session_id,
                "reply": reply_text,
                "message_type": "complaint_submitted",
                "state": "SUBMITTED",
                "complaint_id": new_id,
                "quick_options": [f"Track {new_id}", "Report another issue"]
            }

        elif session.state == "CONFIRMATION" and is_cancel:
            session.state = "COLLECTING_INFO"
            self.db.commit()
            reply_text = "No problem! What would you like to change? (For example, you can tell me a different location or more details about the issue)."
            self._save_ai_message(session_id, reply_text, "text")
            return {
                "session_id": session_id,
                "reply": reply_text,
                "message_type": "text",
                "state": "COLLECTING_INFO",
                "draft_complaint": draft
            }

        # ----------------------------------------------------
        # Slot Filling & Multi-Turn Processing
        # ----------------------------------------------------
        # Extract location if not present or updated
        found_loc = extract_location(cleaned_msg)
        if found_loc and (not draft.get("location") or len(cleaned_msg.split()) <= 6):
            draft["location"] = found_loc

        # Check if the user is issuing a correction
        is_user_correction = any(phrase in msg_lower for phrase in [
            "not wifi", "not network", "not it", "not an it", "wrong category",
            "no, ", "actually ", "i meant", "talking about", "it is about", "it's about", "not about"
        ])

        # If description is empty or user is correcting a misunderstanding, update it cleanly
        if not draft.get("description") or is_user_correction:
            draft["description"] = cleaned_msg
            draft["title"] = cleaned_msg[:70]
            draft.pop("scope_clarified", None)
        else:
            # Append additional information
            draft["description"] = f"{draft['description']} | {cleaned_msg}"

        # Classify Category
        category, subcategory, confidence = detect_category(draft["description"])
        draft["category"] = category
        draft["subcategory"] = subcategory
        draft["ai_confidence"] = confidence

        # Calculate Severity (Hybrid AI + Rules)
        location_str = draft.get("location", "")
        severity, severity_reasoning = calculate_severity(draft["description"], category, location_str)
        draft["severity"] = severity
        draft["severity_reasoning"] = severity_reasoning

        # Route to Department
        department, routing_reason = route_complaint(category, subcategory, draft["description"])
        draft["department"] = department
        draft["routing_reason"] = routing_reason

        # Deterministic Safety / High Priority Gate (Immediate verification for CRITICAL issues)
        if severity == "CRITICAL" and not draft.get("verified_email"):
            if not draft.get("location"):
                draft["location"] = "Campus (Location to be confirmed)"
            session.state = "AWAITING_EMAIL_VERIFICATION"
            session.extracted_data = json.dumps(draft)
            self.db.commit()

            gate_prompt = (
                f"⚠️ **Institutional Verification Required ({severity} Priority)**\n\n"
                f"Because this issue is classified as **{severity}** priority ({draft.get('severity_reasoning', 'Urgent safety / safeguarding matter')}), "
                f"campus security policy requires official email verification to deter false reports and coordinate immediate dispatch.\n\n"
                f"Please reply with your **official institutional email address** (e.g. `student@campus.edu`):"
            )
            self._save_ai_message(session_id, gate_prompt, "text")
            return {
                "session_id": session_id,
                "reply": gate_prompt,
                "message_type": "text",
                "state": "AWAITING_EMAIL_VERIFICATION",
                "draft_complaint": draft,
                "quick_options": ["student@campus.edu", "my.name@university.edu"]
            }

        # Check for Missing Information
        # Essential missing info: LOCATION
        if not draft.get("location"):
            session.state = "COLLECTING_INFO"
            session.extracted_data = json.dumps(draft)
            self.db.commit()

            # Generate smart contextual prompt
            loc_prompts = {
                "IT / Network": "Got it. Which block, floor, or room is experiencing this network issue?",
                "Hostel": "Understood. Which hostel block and room number is this regarding?",
                "Infrastructure": "Thanks for reporting. Could you specify the exact room, lab, or floor number?",
                "Plumbing": "Got it. Where is the leak or water issue located (which block/washroom)?",
                "Electrical": "Understood. Where is this electrical issue located? (Room/Lab/Corridor)",
                "Mess / Food": "Thanks. Which dining hall or mess counter did this happen at?",
                "Cleanliness": "Got it. Which floor or area needs cleaning?",
                "Landscaping & Groundskeeping": "Understood. Where on campus are the plants, trees, or grounds located (e.g., Main Gate, Botanical Garden, Central Lawn)?"
            }
            reply_text = loc_prompts.get(
                category,
                "Got it. Where exactly are you experiencing this issue (Block, Room, or Floor)?"
            )
            quick_options_map = {
                "Landscaping & Groundskeeping": ["Main Gate", "Botanical Garden", "Central Lawn"],
                "IT / Network": ["Block C, 3rd Floor", "Hostel Block B, Room 204", "Academic Quad B-204"]
            }
            quick_opts = quick_options_map.get(category, ["Block C, 3rd Floor", "Hostel Block B, Room 204", "Academic Quad B-204"])
            self._save_ai_message(session_id, reply_text, "text")
            return {
                "session_id": session_id,
                "reply": reply_text,
                "message_type": "text",
                "state": "COLLECTING_INFO",
                "draft_complaint": draft,
                "quick_options": quick_opts
            }

        # Check if scope / urgency clarification is needed for broad complaints
        # ONLY trigger if the description explicitly mentions wifi or internet technology
        has_tech_kw = any(w in draft["description"].lower() for w in ["wifi", "wi-fi", "internet", "network", "router", "eduroam"]) or bool(re.search(r"\blan\b", draft["description"].lower()))
        if category == "IT / Network" and has_tech_kw and not draft.get("scope_clarified") and "everyone" not in msg_lower and "only me" not in msg_lower:
            draft["scope_clarified"] = True
            session.state = "COLLECTING_INFO"
            session.extracted_data = json.dumps(draft)
            self.db.commit()

            reply_text = "Thanks. Is the Wi-Fi problem affecting everyone around you or only your device?"
            self._save_ai_message(session_id, reply_text, "text")
            return {
                "session_id": session_id,
                "reply": reply_text,
                "message_type": "text",
                "state": "COLLECTING_INFO",
                "draft_complaint": draft,
                "quick_options": ["Affecting everyone", "Only my device"]
            }

        # ----------------------------------------------------
        # Trigger Gate on High / Critical Severity (Friction layer)
        # ----------------------------------------------------
        if severity in ["CRITICAL", "HIGH"] and not draft.get("verified_email"):
            session.state = "AWAITING_EMAIL_VERIFICATION"
            session.extracted_data = json.dumps(draft)
            self.db.commit()

            gate_prompt = (
                f"⚠️ **Institutional Verification Required ({severity} Priority)**\n\n"
                f"Because this issue is classified as **{severity}** priority ({draft.get('severity_reasoning', 'Urgent matter')}), "
                f"campus security policy requires official email verification to deter false reports and coordinate immediate dispatch.\n\n"
                f"Please reply with your **official institutional email address** (e.g. `student@campus.edu`):"
            )
            self._save_ai_message(session_id, gate_prompt, "text")
            return {
                "session_id": session_id,
                "reply": gate_prompt,
                "message_type": "text",
                "state": "AWAITING_EMAIL_VERIFICATION",
                "draft_complaint": draft,
                "quick_options": ["student@campus.edu", "rahul.s@student.edu"]
            }

        # ----------------------------------------------------
        # Ready for Confirmation!
        # Render Structured Confirmation Card
        # ----------------------------------------------------
        return self._render_confirmation_card(session_id, session, draft)

    def _render_confirmation_card(self, session_id: str, session: ChatSession, draft: Dict[str, Any]) -> Dict[str, Any]:
        """
        Renders the final AI Structured Summary Confirmation Card.
        """
        dup = check_duplicate_complaints(
            draft["description"],
            draft.get("location", ""),
            draft.get("category", ""),
            self.db
        )

        session.state = "CONFIRMATION"
        session.extracted_data = json.dumps(draft)
        self.db.commit()

        card_payload = {
            "title": draft.get("title", "Campus Issue"),
            "description": draft.get("description", ""),
            "category": draft.get("category", "Infrastructure"),
            "subcategory": draft.get("subcategory", ""),
            "severity": draft.get("severity", "MEDIUM"),
            "location": draft.get("location", "Campus"),
            "department": draft.get("department", "Maintenance & Engineering"),
            "evidence_url": draft.get("evidence_url"),
            "severity_reasoning": draft.get("severity_reasoning"),
            "verified_email": draft.get("verified_email")
        }

        confirmation_text = (
            f"Here's what I've understood from our conversation:\n\n"
            f"📋 **Issue:** {draft.get('description', '')[:90]}\n"
            f"📍 **Location:** {draft.get('location')}\n"
            f"🏷️ **Category:** {draft.get('category')} ({draft.get('subcategory')})\n"
            f"⚡ **Severity:** {draft.get('severity')}\n"
            f"🏢 **Assigned Department:** {draft.get('department')}\n"
        )
        if draft.get("verified_email"):
            confirmation_text += f"📧 **Verified Email:** `{draft['verified_email']}`\n"

        confirmation_text += "\nShould I submit this complaint?"

        if dup:
            confirmation_text = (
                f"⚠️ *Notice: A similar issue (#{dup['id']}) was recently reported at {dup['location']} and is currently `{dup['status']}`.*\n\n"
                + confirmation_text
            )

        self._save_ai_message(session_id, confirmation_text, "confirmation_card", metadata=card_payload)

        return {
            "session_id": session_id,
            "reply": confirmation_text,
            "message_type": "confirmation_card",
            "state": "CONFIRMATION",
            "draft_complaint": card_payload,
            "duplicate_warning": dup,
            "quick_options": ["Yes, submit complaint", "Edit details", "Cancel"]
        }

    def _save_ai_message(self, session_id: str, content: str, msg_type: str = "text", metadata: Optional[Dict[str, Any]] = None):
        msg = ChatMessage(
            session_id=session_id,
            sender="ai",
            content=content,
            message_type=msg_type,
            metadata_json=json.dumps(metadata) if metadata else None
        )
        self.db.add(msg)
        self.db.commit()
