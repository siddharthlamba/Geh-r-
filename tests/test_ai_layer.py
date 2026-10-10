"""
Gehor AI Intelligence Layer - Test Suite.
Validates all 12 core scenarios:
1. Normal academic complaint
2. Minor maintenance complaint
3. Water leak safety hazard
4. IT / Wi-Fi outage
5. Mess food quality
6. Ambiguous complaint (missing info)
7. Critical safety hazard (emergency override)
8. Inactive / unconfigured department fallback
9. Conflicting routing examples
10. Timeout / quota exhaustion fallback
11. Recalculation on additional info
12. Supervised routing correction & learning feedback
"""

import pytest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.models import Department, RoutingRule, User, Complaint, RoutingFeedback
from backend.app.seed_data import seed_database
from backend.app.ai.conversation_analyzer import ConversationAnalyzer
from backend.app.ai.severity_service import SeverityService
from backend.app.ai.routing_service import RoutingService
from backend.app.ai.routing_learning_service import RoutingLearningService
from backend.app.ai.resolution_service import ResolutionService
from backend.app.ai.orchestrator import AIOrchestrator
from backend.app.ai.gemini_client import GeminiInferenceResult


@pytest.fixture
def test_db():
    """In-memory SQLite database session isolated per test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    yield db
    db.close()


# Scenario 1: Normal Academic Complaint
def test_scenario_1_academic_complaint(test_db):
    analyzer = ConversationAnalyzer()
    messages = [
        {"sender": "student", "content": "The professor did not arrive for the advanced physics lecture in Hall A."}
    ]
    analysis = analyzer.analyze_conversation(messages)
    assert analysis.category == "Academic"
    assert "Academic" in analysis.recommended_responsible_department or "Academic Administration" in analysis.recommended_responsible_department
    assert analysis.recommended_severity in ["LOW", "MEDIUM"]


# Scenario 2: Minor Maintenance Complaint
def test_scenario_2_minor_maintenance(test_db):
    analyzer = ConversationAnalyzer()
    severity_svc = SeverityService()
    routing_svc = RoutingService(test_db)

    messages = [
        {"sender": "student", "content": "The study table desk handle is loose and squeaky in Room 302."}
    ]
    analysis = analyzer.analyze_conversation(messages)
    sev_eval = severity_svc.evaluate_severity(
        full_conversation_text=messages[0]["content"],
        category=analysis.category
    )
    decision = routing_svc.route_complaint(
        category="Infrastructure",
        description=messages[0]["content"],
        location="Room 302"
    )

    assert sev_eval.severity == "LOW"
    assert decision.department_name == "Maintenance & Engineering"
    assert not sev_eval.is_safety_critical


# Scenario 3: Water Leak Safety Hazard
def test_scenario_3_water_leak_safety_hazard(test_db):
    severity_svc = SeverityService()
    routing_svc = RoutingService(test_db)

    text = "Large water leak in Block C 2nd floor washroom is flooding out into the main corridor, causing a dangerous slippery hazard."
    sev_eval = severity_svc.evaluate_severity(full_conversation_text=text, category="Plumbing", location="Block C")
    decision = routing_svc.route_complaint(category="Plumbing", description=text, location="Block C")

    assert sev_eval.severity in ["HIGH", "CRITICAL"]
    assert "hazard" in sev_eval.reasoning.lower() or "slipping" in sev_eval.reasoning.lower() or "water" in sev_eval.reasoning.lower()
    assert decision.department_name == "Maintenance & Engineering"


# Scenario 4: IT / Wi-Fi Outage
def test_scenario_4_it_wifi_outage(test_db):
    analyzer = ConversationAnalyzer()
    routing_svc = RoutingService(test_db)

    messages = [
        {"sender": "student", "content": "Wi-Fi is completely down in Block C 3rd Floor, no internet connection on eduroam."}
    ]
    analysis = analyzer.analyze_conversation(messages)
    decision = routing_svc.route_complaint(
        category=analysis.category,
        subcategory=analysis.subcategory,
        description=messages[0]["content"],
        location="Block C"
    )

    assert analysis.category == "IT / Network"
    assert decision.department_name == "IT Services"
    assert decision.confidence >= 0.85


# Scenario 5: Mess Food Quality
def test_scenario_5_mess_food_quality(test_db):
    severity_svc = SeverityService()
    routing_svc = RoutingService(test_db)

    text = "The food served at dining hall today had undercooked chicken and spoiled milk, causing stomach aches."
    sev_eval = severity_svc.evaluate_severity(full_conversation_text=text, category="Mess / Food", location="Dining Hall")
    decision = routing_svc.route_complaint(category="Mess / Food", description=text)

    assert sev_eval.severity in ["HIGH", "CRITICAL"]
    assert decision.department_name == "Food & Catering"


# Scenario 6: Ambiguous Complaint (Missing Info)
def test_scenario_6_ambiguous_complaint_missing_info(test_db):
    analyzer = ConversationAnalyzer()
    messages = [
        {"sender": "student", "content": "The light is broken and flickering."}
    ]
    analysis = analyzer.analyze_conversation(messages)
    assert len(analysis.missing_information) > 0
    assert any("room" in m.lower() or "block" in m.lower() or "location" in m.lower() for m in analysis.missing_information)


# Scenario 7: Critical Safety Hazard (Deterministic Emergency Override)
def test_scenario_7_critical_safety_hazard_override(test_db):
    severity_svc = SeverityService()
    text = "Emergency! Electric shock and active sparking short circuit with smoke coming from the power panel in Chemistry Lab 102!"
    sev_eval = severity_svc.evaluate_severity(full_conversation_text=text)

    assert sev_eval.severity == "CRITICAL"
    assert sev_eval.is_safety_critical is True
    assert sev_eval.evaluated_by == "deterministic_safety_guard"
    assert sev_eval.emergency_trigger is not None


# Scenario 8: Inactive / Unconfigured Department Fallback
def test_scenario_8_inactive_department_fallback(test_db):
    # Deactivate Transport Office
    dept = test_db.query(Department).filter(Department.name == "Transport Office").first()
    if dept:
        dept.is_active = False
        test_db.commit()

    routing_svc = RoutingService(test_db)
    decision = routing_svc.route_complaint(category="Transport", description="Campus shuttle bus did not arrive at stop 4.")

    assert decision.routing_mode == "FALLBACK"
    assert decision.department_name == "Maintenance & Engineering"
    assert "inactive" in decision.rationale.lower() or "fallback" in decision.rationale.lower()


# Scenario 9: Conflicting Routing Signals (Supervised Mode)
def test_scenario_9_conflicting_routing_signals(test_db):
    routing_svc = RoutingService(test_db)
    # Ambiguous or 'Other' category with vague content
    decision = routing_svc.route_complaint(
        category="Other",
        description="General miscellaneous query regarding non-standard item.",
        location="Campus"
    )

    assert decision.routing_mode == "SUPERVISED"
    assert decision.confidence < routing_svc.threshold


# Scenario 10: Timeout / Quota Exhaustion Fallback
def test_scenario_10_quota_timeout_fallback(test_db, monkeypatch):
    orchestrator = AIOrchestrator(test_db)

    # Simulate quota exhaustion in gemini client
    def mock_quota_failure(*args, **kwargs):
        return GeminiInferenceResult(
            success=False,
            provider="rule_fallback",
            model="gemini-1.5-flash",
            latency_ms=10.0,
            error_message="Resource has been exhausted (e.g. check quota) 429",
            is_quota_exhausted=True
        )

    monkeypatch.setattr(orchestrator.analyzer.gemini_client, "generate_structured_json", mock_quota_failure)
    monkeypatch.setattr(orchestrator.resolution_service.gemini_client, "generate_structured_json", mock_quota_failure)

    messages = [{"sender": "student", "content": "Wi-Fi is not connecting in Room 101."}]
    payload = orchestrator.process_full_complaint_intake("GH-2026-9999", messages)

    assert payload is not None
    assert payload.ai_provider == "rule_fallback"
    assert payload.routing_decision.department_name == "IT Services"
    assert len(payload.resolution_brief.step_by_step_plan) > 0


# Scenario 11: Recalculation on Additional Info
def test_scenario_11_recalculation_on_additional_info(test_db):
    severity_svc = SeverityService()

    # Turn 1: Normal report
    initial_text = "There is water dripping slowly from the ceiling."
    eval1 = severity_svc.evaluate_severity(initial_text)
    assert eval1.severity in ["LOW", "MEDIUM", "HIGH"]
    assert eval1.severity != "CRITICAL"

    # Turn 2: Critical addition
    followup_text = "Wait, water is dripping directly into a high voltage switchboard and there is electric shock sparking!"
    eval2 = severity_svc.evaluate_severity(followup_text, previous_severity=eval1.severity)

    assert eval2.severity == "CRITICAL"
    assert eval2.is_safety_critical is True
    assert eval2.recalculated is True


# Scenario 12: Supervised Routing Correction & Learning Feedback
def test_scenario_12_supervised_routing_learning_feedback(test_db):
    learning_svc = RoutingLearningService(test_db)
    routing_svc = RoutingService(test_db)

    # Initial metrics
    stats_before = learning_svc.calculate_learning_metrics()

    # Record supervisor decision correcting routing for a smart podium AV issue
    feature_text = "smart podium digital projector av system hdmi audio failed"
    learning_svc.record_supervisor_decision(
        complaint_id="GH-2026-1045",
        features_text=feature_text,
        predicted_department="Maintenance & Engineering",
        actual_department="IT Services",
        supervisor_name="Admin Triage Officer"
    )

    stats_after = learning_svc.calculate_learning_metrics()
    assert stats_after["total_feedback_samples"] == stats_before["total_feedback_samples"] + 1
    assert stats_after["corrected_count"] == stats_before["corrected_count"] + 1

    # Verify learned corrections are retained and used for future similar complaints
    decision = routing_svc.route_complaint(
        category="Infrastructure",
        description="smart podium digital projector failed in hall B",
        location="Hall B"
    )
    assert decision.department_name == "IT Services"
    assert decision.routing_mode == "AUTONOMOUS"
    assert "supervisor correction" in decision.rationale.lower()


# Scenario 13: Landscaping & Groundskeeping (Plants dying at main gate)
def test_scenario_13_landscaping_groundskeeping_plants_at_gate(test_db):
    analyzer = ConversationAnalyzer()
    severity_svc = SeverityService()
    routing_svc = RoutingService(test_db)

    complaint_text = "Plants dying at the main gate due to lack of watering."
    messages = [
        {"sender": "student", "content": complaint_text}
    ]

    analysis = analyzer.analyze_conversation(messages)
    assert analysis.category == "Landscaping & Groundskeeping"
    assert "Facilities" in analysis.recommended_responsible_department or "Grounds" in analysis.recommended_responsible_department
    assert analysis.recommended_severity in ["LOW", "MEDIUM"]
    assert "IT" not in analysis.recommended_responsible_department

    sev_eval = severity_svc.evaluate_severity(
        full_conversation_text=complaint_text,
        category=analysis.category,
        location="Main Gate"
    )
    assert sev_eval.severity in ["LOW", "MEDIUM"]
    assert sev_eval.is_safety_critical is False

    decision = routing_svc.route_complaint(
        category=analysis.category,
        subcategory=analysis.subcategory,
        description=complaint_text,
        location="Main Gate"
    )
    assert decision.department_name == "Facilities & Groundskeeping"
    assert decision.department_name != "IT Services"
    assert decision.department_name != "Security Office"
    assert decision.confidence >= 0.85

    # Full Intake Pipeline Verification
    orchestrator = AIOrchestrator(test_db)
    intake = orchestrator.process_full_complaint_intake(
        complaint_id="GH-2026-1099",
        messages=messages
    )
    assert intake.analysis.category == "Landscaping & Groundskeeping"
    assert intake.routing_decision.department_name == "Facilities & Groundskeeping"
    assert intake.routing_decision.department_name != "IT Services"
    assert intake.severity_eval.severity in ["LOW", "MEDIUM"]


# Scenario 14: Agent Dialog Landscaping & Memory Reset
def test_scenario_14_agent_dialog_landscaping_no_wifi_leakage(test_db):
    from backend.app.agent import GehorAgent
    from backend.app.routers.agent_router import reset_session
    from backend.app.models import ChatMessage

    agent = GehorAgent(test_db)
    session_id = "test_sess_landscaping"

    # Turn 1: Student reports landscaping issue at main gate
    res = agent.process_message(
        session_id=session_id,
        user_message="Plants dying at the main gate"
    )

    # Verify agent does NOT hallucinate Wi-Fi or IT
    assert "wi-fi" not in res["reply"].lower()
    assert "wifi" not in res["reply"].lower()
    assert "network" not in res["reply"].lower()

    draft = res.get("draft_complaint")
    if draft:
        assert draft["category"] == "Landscaping & Groundskeeping"
        assert draft["department"] == "Facilities & Groundskeeping"
        assert draft["severity"] in ["LOW", "MEDIUM"]

    # Verify memory clear / session reset endpoint
    reset_session(session_id=session_id, db=test_db)
    remaining_msgs = test_db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
    assert len(remaining_msgs) == 0


# Scenario 15: Friction Layer / Email Verification Gate on Critical & High Severity Complaints
def test_scenario_15_email_verification_gate_for_critical_high(test_db):
    from backend.app.agent import GehorAgent
    from backend.app.models import Complaint, ComplaintEvent

    agent = GehorAgent(test_db)
    session_id = "test_sess_critical_gate"

    # Turn 1: User reports a critical hazard (sparking high voltage wires and fire hazard in Chemistry lab)
    res1 = agent.process_message(
        session_id=session_id,
        user_message="Emergency! Electrical sparking wires and active fire hazard in Chemistry Lab Room 302!"
    )

    # Agent should evaluate as CRITICAL or HIGH and gate with AWAITING_EMAIL_VERIFICATION
    assert res1["state"] == "AWAITING_EMAIL_VERIFICATION"
    assert "Institutional Verification Required" in res1["reply"] or "official institutional email" in res1["reply"].lower()

    # Turn 2: User provides invalid text (not an email)
    res2 = agent.process_message(
        session_id=session_id,
        user_message="please hurry up this is not an email"
    )
    assert res2["state"] == "AWAITING_EMAIL_VERIFICATION"
    assert "Invalid Institutional Email" in res2["reply"]

    # Turn 3: User provides valid institutional email
    res3 = agent.process_message(
        session_id=session_id,
        user_message="My email is student2026@campus.edu"
    )
    # Should now transition to CONFIRMATION with confirmation card
    assert res3["state"] == "CONFIRMATION"
    assert res3["message_type"] == "confirmation_card"
    draft = res3.get("draft_complaint")
    assert draft is not None
    assert draft.get("verified_email") == "student2026@campus.edu"

    # Turn 4: User confirms the submission
    res4 = agent.process_message(
        session_id=session_id,
        user_message="Yes, please confirm and submit this complaint."
    )
    assert res4["state"] == "SUBMITTED"
    complaint_id = res4["complaint_id"]
    assert complaint_id is not None

    # Verify Complaint row in database has verified_email populated
    saved_complaint = test_db.query(Complaint).filter(Complaint.id == complaint_id).first()
    assert saved_complaint is not None
    assert saved_complaint.verified_email == "student2026@campus.edu"
    assert saved_complaint.severity in ["CRITICAL", "HIGH"]

    # Verify EMAIL_VERIFICATION audit event
    email_event = test_db.query(ComplaintEvent).filter(
        ComplaintEvent.complaint_id == complaint_id,
        ComplaintEvent.event_type == "EMAIL_VERIFICATION"
    ).first()
    assert email_event is not None
    assert "student2026@campus.edu" in email_event.new_value


# Scenario 16: Local Offline Ollama Qwen 3 4B Structured JSON Chat Inference
def test_scenario_16_ollama_local_qwen3_chat_inference(monkeypatch):
    import ollama
    import json
    from backend.app.ai.gemini_client import GeminiClient

    client = GeminiClient()
    assert client.model == "qwen3:4b"
    assert client.is_available is True

    # Mock ollama.chat returning a valid ChatResponse
    class MockMessage:
        content = json.dumps({
            "category": "Landscaping & Groundskeeping",
            "department": "Facilities & Groundskeeping",
            "severity": "LOW"
        })

    class MockChatResponse:
        message = MockMessage()

    recorded_kwargs = {}
    def mock_ollama_chat(**kwargs):
        recorded_kwargs.update(kwargs)
        return MockChatResponse()

    monkeypatch.setattr(ollama, "chat", mock_ollama_chat)

    res = client.generate_structured_json(
        prompt="Plants are wilting at front lawn",
        system_instruction="Classify campus complaint",
        temperature=0.1
    )

    assert res.success is True
    assert res.provider == "ollama_offline"
    assert res.model == "qwen3:4b"
    assert res.data["category"] == "Landscaping & Groundskeeping"
    assert recorded_kwargs["model"] == "qwen3:4b"
    assert recorded_kwargs["format"] == "json"
    assert recorded_kwargs["options"]["temperature"] == 0.1
    assert any(m["role"] == "system" for m in recorded_kwargs["messages"])


# Scenario 17: Deterministic Intent Guard (Pure Conversational Greeting)
def test_scenario_17_conversational_guard_hi(test_db):
    from backend.app.agent import GehorAgent
    from backend.app.ai.conversation_analyzer import ConversationAnalyzer, GREETING_RESPONSE

    # 1. Analyzer test
    analyzer = ConversationAnalyzer()
    messages = [{"sender": "student", "content": "hi"}]
    analysis = analyzer.analyze_conversation(messages)
    assert analysis.original_problem_description == ""
    assert analysis.inference_provider == "deterministic_guard"
    assert len(analysis.reported_symptoms) == 0

    # 2. Agent Turn test
    agent = GehorAgent(test_db)
    session_id = "test_sess_greeting_guard"

    res = agent.process_message(
        session_id=session_id,
        user_message="hi"
    )

    # Must yield greeting response and not ask for location / slot-filling
    assert res["state"] == "IDLE"
    assert res["reply"] == GREETING_RESPONSE
    assert "block" not in res["reply"].lower()
    assert "room" not in res["reply"].lower()
    assert "floor" not in res["reply"].lower()

    # Draft should not have description set to "hi"
    draft = res.get("draft_complaint")
    if draft:
        assert not draft.get("description")


# Scenario 18: Deterministic Safety Safeguard - Bullying & Anti-Ragging Priority
def test_scenario_18_critical_safeguarding_bullying_cafeteria(test_db):
    from backend.app.agent import GehorAgent
    from backend.app.ai.severity_service import SeverityService
    from backend.app.ai.routing_service import RoutingService
    from backend.app.routing import route_complaint
    from backend.app.severity import calculate_severity

    complaint_text = "there is a friend of mine who suffered serious bullying at the cafeteria today"

    # 1. Direct severity & routing engine checks
    sev, sev_reason = calculate_severity(complaint_text)
    assert sev == "CRITICAL"
    assert "bullying" in sev_reason.lower() or "safeguard" in sev_reason.lower()

    dept, routing_reason = route_complaint("Anti-Ragging / Safeguarding", "Safeguarding Incident", complaint_text)
    assert dept == "Anti-Ragging / Safeguarding"
    assert dept != "Food & Catering"

    # 2. AI Layer Services
    sev_svc = SeverityService()
    sev_eval = sev_svc.evaluate_severity(complaint_text)
    assert sev_eval.severity == "CRITICAL"
    assert sev_eval.is_safety_critical is True
    assert sev_eval.evaluated_by == "deterministic_safety_guard"
    assert sev_eval.target_department == "Anti-Ragging / Safeguarding"

    routing_svc = RoutingService(test_db)
    route_dec = routing_svc.route_complaint(
        category="Anti-Ragging / Safeguarding",
        subcategory="Safeguarding Incident",
        description=complaint_text,
        location="Cafeteria"
    )
    assert route_dec.department_name == "Anti-Ragging / Safeguarding"
    assert route_dec.department_name != "Food & Catering"
    assert route_dec.confidence >= 0.95

    # 3. Agent Full Turn: Must trigger CRITICAL, assign to Anti-Ragging, and gate at AWAITING_EMAIL_VERIFICATION
    agent = GehorAgent(test_db)
    session_id = "test_sess_bullying_cafeteria"

    res = agent.process_message(
        session_id=session_id,
        user_message=complaint_text
    )

    assert res["state"] == "AWAITING_EMAIL_VERIFICATION"
    assert "Institutional Verification Required" in res["reply"]
    draft = res["draft_complaint"]
    assert draft["severity"] == "CRITICAL"
    assert draft["department"] == "Anti-Ragging / Safeguarding"
    assert draft["department"] != "Food & Catering"





