"""
Component D: Recipient-Specific Resolution Instructions.
Generates an actionable, structured resolution brief and executive summary
tailored to the receiving department and grounded in campus SOPs.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import datetime
import json

from .gemini_client import get_gemini_client
from ..knowledge import search_knowledge

DEPARTMENT_STANDARD_SOPS = {
    "Maintenance & Engineering": [
        "SOP-MAINT-01: Isolate primary utility source (breaker panel or shut-off valve) prior to inspection.",
        "SOP-MAINT-02: Deploy bright yellow hazard/caution signage in pedestrian zones within 15 minutes of report.",
        "SOP-MAINT-03: Multi-meter testing and pressure testing required before restoring utility access."
    ],
    "IT Services": [
        "SOP-IT-01: Query central SNMP monitoring console for access point switch port status.",
        "SOP-IT-02: Perform remote gateway ping, DNS resolution check, and VLAN trunk port verification.",
        "SOP-IT-03: On-site patch cord and physical PoE injector inspection if remote reboot fails."
    ],
    "Food & Catering": [
        "SOP-MESS-01: Conduct food probe thermometer check on warming trays (must be >= 65°C).",
        "SOP-MESS-02: Quarantine suspect batch sample for microbiological quality testing.",
        "SOP-MESS-03: Vendor warning issuance and immediate meal replacement protocol."
    ],
    "Hostel Administration": [
        "SOP-HOSTEL-01: Resident welfare inspection conducted in presence of assistant warden.",
        "SOP-HOSTEL-02: Temporary room allotment provided if living amenity is compromised > 6 hours.",
        "SOP-HOSTEL-03: Resident written confirmation required before closing room ticket."
    ],
    "Housekeeping & Cleanliness": [
        "SOP-HK-01: Immediate disinfectant spray and wet floor signage placement.",
        "SOP-HK-02: Biohazard waste disposal protocol for sanitary or chemical spills.",
        "SOP-HK-03: Post-cleaning inspection checklist sign-off by block supervisor."
    ],
    "Security Office": [
        "SOP-SEC-01: Immediate perimeter cordon and CCTV review for incident timeframe.",
        "SOP-SEC-02: Entry/exit gate log verification and security supervisor dispatch.",
        "SOP-SEC-03: Incident log registration with campus proctor office."
    ],
    "Academic Administration": [
        "SOP-ACAD-01: Verify classroom schedule and student attendance grievance record.",
        "SOP-ACAD-02: Alternative lecture hall arrangement if classroom AV equipment fails.",
        "SOP-ACAD-03: Department head notification within 24 hours."
    ],
    "Transport Office": [
        "SOP-TRANS-01: Verify vehicle GPS telemetry logs and route timetable compliance.",
        "SOP-TRANS-02: Deploy standby backup shuttle bus for missed campus routes.",
        "SOP-TRANS-03: Driver counseling and route dispatch log sign-off."
    ],
    "Facilities & Groundskeeping": [
        "SOP-GROUNDS-01: Inspect soil hydration, foliage condition, and irrigation systems within 12 hours.",
        "SOP-GROUNDS-02: Deploy groundskeeping team for immediate watering, soil aeration, and nutrient treatment.",
        "SOP-GROUNDS-03: Grounds supervisor verification and photographic log of revived plants."
    ]
}

class StepItem(BaseModel):
    step_number: int
    action: str
    details: str
    tools_or_personnel_needed: Optional[str] = None
    verification_check: Optional[str] = None

class ResolutionBrief(BaseModel):
    complaint_id: str
    severity: str
    urgency_explanation: str
    incident_summary: str
    responsible_recipient: str
    routing_rationale: str
    immediate_precautions: List[str]
    step_by_step_plan: List[StepItem]
    escalation_conditions: List[str]
    closure_criteria: List[str]
    uncertainties_and_assumptions: List[str]
    grounded_sops_referenced: List[str]
    generated_at: str
    inference_provider: str

class ResolutionService:
    def __init__(self):
        self.gemini_client = get_gemini_client()

    def generate_resolution_brief(
        self,
        complaint_id: str,
        title: str,
        description: str,
        category: str,
        subcategory: str,
        location: str,
        severity: str,
        department_name: str,
        assigned_staff: Optional[str] = None,
        routing_rationale: str = ""
    ) -> ResolutionBrief:
        """
        Generates comprehensive 9-point resolution brief grounded in institutional SOPs.
        """
        # Retrieve relevant approved SOPs from knowledge base (RAG)
        relevant_docs = search_knowledge(f"{category} {description}")
        approved_sops = DEPARTMENT_STANDARD_SOPS.get(
            department_name,
            DEPARTMENT_STANDARD_SOPS["Maintenance & Engineering"]
        )

        sop_context = "\n".join(approved_sops)
        knowledge_context = "\n".join([d["content"] for d in relevant_docs])

        # Try Gemini Free-Tier synthesis if configured
        if self.gemini_client.is_available:
            prompt = f"""
Generate an actionable institutional resolution brief for campus staff:

Complaint ID: {complaint_id}
Title: {title}
Description: {description}
Category: {category} ({subcategory})
Location: {location}
Severity: {severity}
Assigned Department: {department_name}
Assigned Staff: {assigned_staff or 'Department Duty Officer'}

Approved SOP Context:
{sop_context}
{knowledge_context}

Produce a JSON object with EXACTLY the following structure:
{{
  "urgency_explanation": "concise explanation of the urgency and operational impact",
  "incident_summary": "structured what happened, where, student report, impact",
  "immediate_precautions": ["precaution 1", "precaution 2"],
  "step_by_step_plan": [
    {{
      "step_number": 1,
      "action": "Immediate inspection / verification action",
      "details": "exact operational instructions",
      "tools_or_personnel_needed": "required tools or certifications",
      "verification_check": "how to verify completion of this step"
    }}
  ],
  "escalation_conditions": ["condition requiring emergency or supervisor escalation"],
  "closure_criteria": ["tangible evidence required before marking complaint resolved"],
  "uncertainties_and_assumptions": ["unconfirmed details that technician must verify on site"]
}}
"""
            result = self.gemini_client.generate_structured_json(
                prompt=prompt,
                system_instruction="You are an institutional operations expert. Create grounded, actionable resolution plans. Return strictly valid JSON."
            )

            if result.success and result.data:
                d = result.data
                steps = []
                for s in d.get("step_by_step_plan", []):
                    if isinstance(s, dict):
                        steps.append(StepItem(
                            step_number=s.get("step_number", len(steps) + 1),
                            action=str(s.get("action", "Action")),
                            details=str(s.get("details", "")),
                            tools_or_personnel_needed=str(s["tools_or_personnel_needed"]) if s.get("tools_or_personnel_needed") else None,
                            verification_check=str(s["verification_check"]) if s.get("verification_check") else None
                        ))

                def to_str(val, default=""):
                    if isinstance(val, dict):
                        return " | ".join(f"{k}: {v}" for k, v in val.items() if v)
                    if isinstance(val, list):
                        return "; ".join(str(x) for x in val)
                    return str(val) if val else default

                def to_list(val, default=None):
                    if default is None:
                        default = []
                    if isinstance(val, list):
                        return [to_str(x) for x in val]
                    if isinstance(val, dict):
                        return [f"{k}: {v}" for k, v in val.items()]
                    if isinstance(val, str) and val.strip():
                        return [val]
                    return default

                urgency = to_str(d.get("urgency_explanation"), f"Priority level {severity} response required under department SLA.")
                incident_sum = to_str(d.get("incident_summary"), f"{title} reported at {location}.")

                if not steps:
                    return self._generate_grounded_fallback_brief(
                        complaint_id, title, description, category, location,
                        severity, department_name, assigned_staff, routing_rationale, approved_sops
                    )

                return ResolutionBrief(
                    complaint_id=complaint_id,
                    severity=severity,
                    urgency_explanation=urgency,
                    incident_summary=incident_sum,
                    responsible_recipient=f"{department_name}" + (f" ({assigned_staff})" if assigned_staff else ""),
                    routing_rationale=routing_rationale or f"Assigned to {department_name} under institutional category policy.",
                    immediate_precautions=to_list(d.get("immediate_precautions"), []),
                    step_by_step_plan=steps,
                    escalation_conditions=to_list(d.get("escalation_conditions"), ["Escalate if hazard worsens or active safety risk emerges."]),
                    closure_criteria=to_list(d.get("closure_criteria"), ["Physical verification that amenity is fully restored."]),
                    uncertainties_and_assumptions=to_list(d.get("uncertainties_and_assumptions"), ["Exact source of fault to be confirmed on site."]),
                    grounded_sops_referenced=approved_sops[:2],
                    generated_at=datetime.datetime.now(datetime.UTC).isoformat(),
                    inference_provider=result.provider
                )

        # Deterministic Grounded SOP Fallback (Transparently marked)
        return self._generate_grounded_fallback_brief(
            complaint_id, title, description, category, location,
            severity, department_name, assigned_staff, routing_rationale, approved_sops
        )

    def _generate_grounded_fallback_brief(
        self,
        complaint_id: str,
        title: str,
        description: str,
        category: str,
        location: str,
        severity: str,
        department_name: str,
        assigned_staff: Optional[str],
        routing_rationale: str,
        approved_sops: List[str]
    ) -> ResolutionBrief:
        """
        Produces an evidence-based, recipient-tailored resolution brief using verified campus procedures.
        """
        # Tailor plan based on department
        if department_name == "IT Services":
            precautions = [
                "Verify student device does not have static IP misconfiguration.",
                "Ensure server room switches are not manually rebooted during peak exam hours."
            ]
            steps = [
                StepItem(
                    step_number=1,
                    action="Initial Diagnostic Ping & Port Telemetry",
                    details=f"Query central IT console for access points located in '{location}'. Check status of trunk VLAN ports.",
                    tools_or_personnel_needed="SNMP Console / Network Technician",
                    verification_check="Verify if AP responds to ICMP echo and reports normal client load."
                ),
                StepItem(
                    step_number=2,
                    action="Gateway & DHCP Scope Verification",
                    details="Check if DHCP lease pool is exhausted or DNS resolution is failing for connected users.",
                    tools_or_personnel_needed="Network Administrator Credentials",
                    verification_check="Confirm valid IP assignment on test terminal."
                ),
                StepItem(
                    step_number=3,
                    action="On-Site Hardware Inspection",
                    details=f"Inspect physical access point and Cat-6 patch cabling at '{location}'. Check PoE LED indicator.",
                    tools_or_personnel_needed="Ladder, RJ-45 Cable Tester, Spare Patch Cord",
                    verification_check="Green link lights established on physical switch."
                ),
                StepItem(
                    step_number=4,
                    action="Client Connectivity Verification & Close",
                    details="Request student on-site to verify connection and re-authenticate via campus captive portal.",
                    tools_or_personnel_needed="Student Terminal / Mobile Device",
                    verification_check="Successful throughput test (> 25 Mbps)."
                )
            ]
            escalation = [
                "If switch stack is unresponsive or core fiber link is severed, escalate immediately to Dr. Sandeep Verma (IT Head).",
                "If issue affects multiple buildings simultaneously, initiate campus network incident protocol."
            ]
            closure = [
                "At least 5 concurrent devices successfully connected to Wi-Fi at the reported location.",
                "Student confirmation obtained and ticket status updated to RESOLVED in Gehor portal."
            ]

        elif department_name in ["Maintenance & Engineering", "Plumbing", "Electrical"]:
            is_electric = "electric" in category.lower() or "spark" in description.lower()
            precautions = [
                "Deploy high-visibility caution tape or 'Caution: Wet Floor' signage around the perimeter.",
                "Do not touch standing water in the vicinity of electrical fixtures or conduits."
            ]
            steps = [
                StepItem(
                    step_number=1,
                    action="Rapid Site Inspection & Hazard Containment",
                    details=f"Dispatch duty technician to '{location}'. Isolate the affected area from foot traffic.",
                    tools_or_personnel_needed="Safety Cones, Caution Tape, Flashlight",
                    verification_check="Physical perimeter secure; zero students walking through hazard."
                ),
                StepItem(
                    step_number=2,
                    action="Source Isolation & Utility Cut-Off",
                    details="Locate and shut off the specific isolating valve or circuit breaker controlling this zone.",
                    tools_or_personnel_needed="Lockout/Tagout Kit or Plumbing Valve Key",
                    verification_check="Active flow of water or electrical current ceased."
                ),
                StepItem(
                    step_number=3,
                    action="Component Repair / Replacement",
                    details=f"Disassemble damaged piping, fitting, or fixture. Replace with institutional standard component.",
                    tools_or_personnel_needed="Pipe Wrench, Sealant / Multimeter, Spare Parts",
                    verification_check="New fitting seated without leak under normal operating pressure."
                ),
                StepItem(
                    step_number=4,
                    action="Sanitation & Area Clearance",
                    details="Coordinate with Housekeeping to mop and dry the affected floor completely.",
                    tools_or_personnel_needed="Mop, Industrial Floor Squeegee",
                    verification_check="Floor dry and safe for re-opening to campus residents."
                )
            ]
            escalation = [
                "If main riser pipe is fractured or structural seepage is observed, contact Er. Rajesh Sharma immediately.",
                "If water has contacted energized electrical panels, trip master breaker and contact Campus Security."
            ]
            closure = [
                "Zero leakage observed after 30 minutes of continuous line pressure.",
                "Floor completely dry and caution cones safely removed."
            ]

        elif department_name == "Food & Catering":
            precautions = [
                "Do not discard remaining batch of questioned meal until quality inspection is completed.",
                "Ensure student mess committee representatives are notified."
            ]
            steps = [
                StepItem(
                    step_number=1,
                    action="Immediate Kitchen & Serving Counter Inspection",
                    details=f"Mess Supervisor inspects dining counters at '{location}'. Verify temperature logs.",
                    tools_or_personnel_needed="Calibrated Digital Food Probe Thermometer",
                    verification_check="Food hot-holding temperature verified >= 65°C."
                ),
                StepItem(
                    step_number=2,
                    action="Sample Quarantine & Batch Verification",
                    details="Collect 250g sample of questioned meal in sterile container for test record.",
                    tools_or_personnel_needed="Sample Containers, Mess Logbook",
                    verification_check="Sample cataloged and preserved in mess refrigerator."
                ),
                StepItem(
                    step_number=3,
                    action="Fresh Batch Preparation / Alternative Meal",
                    details="Instruct head caterer to discard compromised tray and issue freshly prepared substitute.",
                    tools_or_personnel_needed="Catering Staff",
                    verification_check="Fresh meal served to affected students."
                )
            ]
            escalation = [
                "If multiple students report gastrointestinal illness, alert Campus Medical Health Center immediately.",
                "Escalate vendor contract breach to Mess Committee Dean."
            ]
            closure = [
                "Mess supervisor inspection sign-off in logbook.",
                "Student representative satisfies meal replacement."
            ]

        elif department_name == "Facilities & Groundskeeping":
            precautions = [
                "Ensure immediate manual watering if automated irrigation systems are non-functional.",
                "Cordon off any areas with damaged or falling tree branches."
            ]
            steps = [
                StepItem(
                    step_number=1,
                    action="On-Site Horticultural Inspection",
                    details=f"Groundskeeping supervisor to inspect vegetation and soil condition at '{location}'.",
                    tools_or_personnel_needed="Soil moisture meter, pruning shears",
                    verification_check="Plant health status and root causes (drought, pests, soil condition) recorded."
                ),
                StepItem(
                    step_number=2,
                    action="Irrigation & Soil Treatment",
                    details="Provide deep watering and apply organic compost/nutrients to stressed flora.",
                    tools_or_personnel_needed="Water hose / mobile water tanker, compost mix",
                    verification_check="Adequate soil hydration achieved without waterlogging."
                ),
                StepItem(
                    step_number=3,
                    action="Pruning & Weed Removal",
                    details="Prune dried foliage and remove parasitic weeds or debris around plant beds.",
                    tools_or_personnel_needed="Pruning shears, rake, waste collection bin",
                    verification_check="Plant bed cleared and pruned neatly."
                ),
                StepItem(
                    step_number=4,
                    action="Maintenance Schedule Setup",
                    details="Add location to daily watering and grounds inspection rotation roster.",
                    tools_or_personnel_needed="Groundskeeping roster log",
                    verification_check="Duty gardener assigned for ongoing care."
                )
            ]
            escalation = [
                "If widespread plant death or pest outbreak is detected across multiple zones, escalate to Campus Horticulture Officer Verma.",
                "If campus water supply constraints prevent regular watering, coordinate with Maintenance for emergency tanker dispatch."
            ]
            closure = [
                "Plants adequately hydrated with revived foliar turgor.",
                "Supervisor sign-off and photographic confirmation logged in Gehor portal."
            ]

        else:
            # Generic Institutional Procedure
            precautions = ["Follow standard campus health and safety protocols."]
            steps = [
                StepItem(
                    step_number=1,
                    action="On-Site Assessment & Verification",
                    details=f"Inspect reported condition at '{location}' within department SLA window.",
                    tools_or_personnel_needed="Department Duty Inspector",
                    verification_check="Condition verified and documented in case log."
                ),
                StepItem(
                    step_number=2,
                    action="Remedial Action Implementation",
                    details=f"Carry out necessary corrective measures for: {title}.",
                    tools_or_personnel_needed="Institutional Staff",
                    verification_check="Defect rectified."
                ),
                StepItem(
                    step_number=3,
                    action="Student Notification & Closure",
                    details="Update ticket notes in Gehor admin dashboard and confirm resolution with student.",
                    tools_or_personnel_needed="Admin Portal",
                    verification_check="Status updated to RESOLVED."
                )
            ]
            escalation = ["Escalate to department head if resolution requires external vendor quote > $100."]
            closure = ["Physical verification that issue is resolved and resident informed."]

        urgency_exp = (
            f"Severity is assessed as {severity}. " +
            ("Immediate hazard to personal safety requiring sub-2h response." if severity == "CRITICAL" else
             "High impact disruption requiring sub-6h operational turnaround." if severity == "HIGH" else
             "Standard institutional turnaround under SLA.")
        )

        return ResolutionBrief(
            complaint_id=complaint_id,
            severity=severity,
            urgency_explanation=urgency_exp,
            incident_summary=f"{title} at {location}. {description[:120]}",
            responsible_recipient=f"{department_name}" + (f" ({assigned_staff})" if assigned_staff else ""),
            routing_rationale=routing_rationale or f"Mapped to {department_name} based on institutional routing policy.",
            immediate_precautions=precautions,
            step_by_step_plan=steps,
            escalation_conditions=escalation,
            closure_criteria=closure,
            uncertainties_and_assumptions=[f"Exact cause to be verified on-site at {location}."],
            grounded_sops_referenced=approved_sops[:2],
            generated_at=datetime.datetime.now(datetime.UTC).isoformat(),
            inference_provider="rule_fallback"
        )
