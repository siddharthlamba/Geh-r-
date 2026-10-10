"""
Configuration, constants, routing rules, and status lifecycle for Gehor.
"""
import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# Offline Local AI Configuration (Ollama - Qwen 3 4B, 100% Offline & Self-Hosted)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b").strip()
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30"))

# Backward-compatibility references
GEMINI_API_KEY = ""
GEMINI_MODEL = OLLAMA_MODEL
GEMINI_TIMEOUT_SECONDS = OLLAMA_TIMEOUT_SECONDS

# Autonomous Routing Threshold
ROUTING_AUTONOMOUS_CONFIDENCE_THRESHOLD = float(
    os.getenv("ROUTING_AUTONOMOUS_CONFIDENCE_THRESHOLD", "0.85")
)

CATEGORIES = [
    "Academic",
    "Hostel",
    "Infrastructure",
    "IT / Network",
    "Transport",
    "Mess / Food",
    "Security",
    "Cleanliness",
    "Electrical",
    "Plumbing",
    "Administration",
    "Landscaping & Groundskeeping",
    "Anti-Ragging / Safeguarding",
    "Security & Safety",
    "Other"
]

SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

STATUS_LIFECYCLE = [
    "SUBMITTED",
    "CLASSIFIED",
    "ASSIGNED",
    "IN_PROGRESS",
    "RESOLVED",
    "CLOSED",
    "REJECTED"
]

DEFAULT_ROUTING = {
    "IT / Network": "IT Services",
    "Hostel": "Hostel Administration",
    "Electrical": "Maintenance & Engineering",
    "Plumbing": "Maintenance & Engineering",
    "Infrastructure": "Maintenance & Engineering",
    "Mess / Food": "Food & Catering",
    "Cleanliness": "Housekeeping & Cleanliness",
    "Security": "Security Office",
    "Security & Safety": "Security & Safety",
    "Anti-Ragging / Safeguarding": "Anti-Ragging / Safeguarding",
    "Academic": "Academic Administration",
    "Transport": "Transport Office",
    "Administration": "Academic Administration",
    "Landscaping & Groundskeeping": "Facilities & Groundskeeping",
    "Other": "Hostel Administration"
}

DEPARTMENT_METADATA = {
    "IT Services": {
        "code": "IT",
        "description": "Campus Wi-Fi, lab equipment, portal access, email services and AV tech.",
        "head_name": "Dr. Sandeep Verma",
        "contact_email": "it-helpdesk@campus.edu",
        "default_sla_hours": 12
    },
    "Maintenance & Engineering": {
        "code": "MAINT",
        "description": "Electrical systems, plumbing, HVAC/AC units, elevators, and building repairs.",
        "head_name": "Er. Rajesh Sharma",
        "contact_email": "facilities@campus.edu",
        "default_sla_hours": 8
    },
    "Hostel Administration": {
        "code": "HOSTEL",
        "description": "Hostel warden grievances, room allotment, hostel maintenance, discipline.",
        "head_name": "Chief Warden Office",
        "contact_email": "warden@campus.edu",
        "default_sla_hours": 24
    },
    "Food & Catering": {
        "code": "MESS",
        "description": "Hostel mess hygiene, dining hall operations, water coolers, food quality.",
        "head_name": "Mess Supervisor Anand",
        "contact_email": "mess-committee@campus.edu",
        "default_sla_hours": 6
    },
    "Housekeeping & Cleanliness": {
        "code": "HOUSEKEEP",
        "description": "Washroom sanitation, corridor cleaning, trash disposal, pest control.",
        "head_name": "Mrs. Sunita Devi",
        "contact_email": "housekeeping@campus.edu",
        "default_sla_hours": 4
    },
    "Security Office": {
        "code": "SEC",
        "description": "Campus safety, main gates, CCTV surveillance, lost & found, vehicle parking.",
        "head_name": "Col. R. K. Singh (Retd.)",
        "contact_email": "security@campus.edu",
        "default_sla_hours": 2
    },
    "Security & Safety": {
        "code": "SEC-EMERG",
        "description": "Campus physical security, active hazards, emergency response, and safety escorts.",
        "head_name": "Chief Security Officer",
        "contact_email": "emergency-security@campus.edu",
        "default_sla_hours": 1
    },
    "Anti-Ragging / Safeguarding": {
        "code": "SAFEGUARD",
        "description": "Zero-tolerance anti-ragging squad, student safeguarding, bullying and harassment intervention.",
        "head_name": "Prof. K. Narayanan (Chief Proctor)",
        "contact_email": "anti-ragging@campus.edu",
        "default_sla_hours": 1
    },
    "Academic Administration": {
        "code": "ACAD",
        "description": "Classroom schedules, exam halls, grading grievance, library services.",
        "head_name": "Dean of Academic Affairs",
        "contact_email": "academic-office@campus.edu",
        "default_sla_hours": 24
    },
    "Transport Office": {
        "code": "TRANS",
        "description": "Campus shuttle buses, route schedules, driver behavior, transport passes.",
        "head_name": "Mr. Vikram Sethi",
        "contact_email": "transport@campus.edu",
        "default_sla_hours": 12
    },
    "Facilities & Groundskeeping": {
        "code": "GROUNDS",
        "description": "Campus landscaping, gardens, lawns, tree maintenance, horticulture, outdoor environment.",
        "head_name": "Horticulture Officer Verma",
        "contact_email": "grounds@campus.edu",
        "default_sla_hours": 24
    }
}
