"""
Seed realistic demo data for the Gehor hackathon platform.
Includes departments, staff users, knowledge docs, and active/resolved complaints.
"""
import datetime
from sqlalchemy.orm import Session
from .models import User, Department, Complaint, ComplaintEvent, KnowledgeDoc, RoutingRule
from .config import DEPARTMENT_METADATA, DEFAULT_ROUTING
from .knowledge import INITIAL_KNOWLEDGE_DOCS

def seed_database(db: Session):
    # 1. Seed Departments
    for name, meta in DEPARTMENT_METADATA.items():
        existing_dept = db.query(Department).filter(Department.name == name).first()
        if not existing_dept:
            dept = Department(
                name=name,
                code=meta["code"],
                description=meta["description"],
                head_name=meta["head_name"],
                contact_email=meta["contact_email"],
                default_sla_hours=meta["default_sla_hours"],
                is_active=True
            )
            db.add(dept)
    db.commit()

    # 2. Seed Routing Rules
    for cat, dept in DEFAULT_ROUTING.items():
        existing_rule = db.query(RoutingRule).filter(RoutingRule.category == cat).first()
        if not existing_rule:
            rule = RoutingRule(
                category=cat,
                department_name=dept,
                priority_level="NORMAL",
                notes="Standard institutional auto-route"
            )
            db.add(rule)
    db.commit()

    # 3. Seed Users (Demo Student, Admin, Staff)
    if db.query(User).count() == 0:
        users = [
            User(
                name="Aditya Verma (Admin)",
                student_id=None,
                email="admin@campus.edu",
                phone="+91 99887 76655",
                role="ADMIN",
                department_name="Central Administration"
            ),
            User(
                name="Rahul Sharma",
                student_id="STU-2026-901",
                email="rahul.s@student.edu",
                phone="+91 98765 43210",
                role="STUDENT"
            ),
            User(
                name="Er. Rajesh Sharma",
                student_id=None,
                email="rajesh.maint@campus.edu",
                phone="+91 91234 56789",
                role="STAFF",
                department_name="Maintenance & Engineering"
            ),
            User(
                name="Vikram IT Specialist",
                student_id=None,
                email="vikram.it@campus.edu",
                phone="+91 91234 56780",
                role="STAFF",
                department_name="IT Services"
            ),
            User(
                name="Suresh Grounds Supervisor",
                student_id=None,
                email="grounds@campus.edu",
                phone="+91 91234 56785",
                role="STAFF",
                department_name="Facilities & Groundskeeping"
            )
        ]
        db.add_all(users)
        db.commit()

    # 4. Seed Knowledge Documents
    if db.query(KnowledgeDoc).count() == 0:
        for doc in INITIAL_KNOWLEDGE_DOCS:
            k = KnowledgeDoc(
                title=doc["title"],
                category=doc["category"],
                content=doc["content"],
                tags=doc.get("tags")
            )
            db.add(k)
        db.commit()

    # 5. Seed Realistic Complaints
    if db.query(Complaint).count() == 0:
        now = datetime.datetime.now(datetime.UTC)
        sample_complaints = [
            {
                "id": "GH-2026-1035",
                "student_id": "STU-2026-842",
                "student_name": "Priya Sharma",
                "student_contact": "+91 98111 22334",
                "title": "Wi-Fi outage on 3rd floor Block B",
                "description": "Entire 3rd floor of Block B has no internet connectivity since 8:00 AM. Devices connect to SSID but give DNS failure.",
                "category": "IT / Network",
                "subcategory": "Wi-Fi & Connectivity",
                "severity": "MEDIUM",
                "location": "Block B, 3rd Floor",
                "department_name": "IT Services",
                "assigned_to": "Vikram IT Specialist",
                "status": "IN_PROGRESS",
                "ai_confidence": 0.96,
                "ai_intent": "CREATE_COMPLAINT",
                "ai_reasoning": "Network outage reported affecting multiple rooms in Block B.",
                "internal_notes": "Access Point AP-B301 rebooted. Investigating trunk VLAN switch port.",
                "created_at": now - datetime.timedelta(hours=5),
                "updated_at": now - datetime.timedelta(hours=1),
                "events": [
                    ("SUBMISSION", "SUBMITTED", "Student via Gehor AI", "Complaint submitted via WhatsApp chat.", now - datetime.timedelta(hours=5)),
                    ("CLASSIFICATION", "IT / Network / MEDIUM", "Gehor AI Classifier", "Classified as IT Network issue.", now - datetime.timedelta(hours=5)),
                    ("ROUTING", "IT Services", "Gehor Routing Engine", "Routed to IT Services queue.", now - datetime.timedelta(hours=5)),
                    ("ASSIGNMENT", "Vikram IT Specialist", "Admin: Aditya Verma", "Assigned to network engineer on duty.", now - datetime.timedelta(hours=3)),
                    ("STATUS_CHANGE", "IN_PROGRESS", "Vikram IT Specialist", "Investigating switch port and gateway.", now - datetime.timedelta(hours=1))
                ]
            },
            {
                "id": "GH-2026-1036",
                "student_id": "STU-2026-715",
                "student_name": "Arjun Patel",
                "student_contact": "+91 98222 33445",
                "title": "Main water pipe burst near staircase",
                "description": "Severe water leakage near Hostel Block C main staircase. Floor is completely flooded and slippery.",
                "category": "Plumbing",
                "subcategory": "Water Supply & Plumbing",
                "severity": "HIGH",
                "location": "Hostel Block C, Staircase 2",
                "department_name": "Maintenance & Engineering",
                "assigned_to": "Er. Rajesh Sharma",
                "status": "ASSIGNED",
                "ai_confidence": 0.98,
                "ai_intent": "CREATE_COMPLAINT",
                "ai_reasoning": "Flooding & slipping risk flagged as HIGH severity hazard.",
                "internal_notes": "Plumbing crew notified to isolate valve C-2 immediately.",
                "created_at": now - datetime.timedelta(hours=2),
                "updated_at": now - datetime.timedelta(minutes=45),
                "events": [
                    ("SUBMISSION", "SUBMITTED", "Student via Gehor AI", "Urgent water leak reported.", now - datetime.timedelta(hours=2)),
                    ("CLASSIFICATION", "Plumbing / HIGH", "Gehor AI Classifier", "Safety hazard: slipping hazard from flooding.", now - datetime.timedelta(hours=2)),
                    ("ROUTING", "Maintenance & Engineering", "Gehor Routing Engine", "Priority routing to Maintenance.", now - datetime.timedelta(hours=2)),
                    ("ASSIGNMENT", "Er. Rajesh Sharma", "Admin: Aditya Verma", "Assigned for emergency pipe clamp.", now - datetime.timedelta(minutes=45))
                ]
            },
            {
                "id": "GH-2026-1037",
                "student_id": "STU-2026-903",
                "student_name": "Neha Gupta",
                "student_contact": "+91 98333 44556",
                "title": "Mess dinner food cold and undercooked",
                "description": "Dinner served at Hostel Dining Hall 1 had undercooked lentils and cold rice. Multiple students complained to warden.",
                "category": "Mess / Food",
                "subcategory": "Food Quality & Catering",
                "severity": "MEDIUM",
                "location": "Hostel Dining Hall 1",
                "department_name": "Food & Catering",
                "assigned_to": "Supervisor Anand",
                "status": "RESOLVED",
                "ai_confidence": 0.93,
                "ai_intent": "CREATE_COMPLAINT",
                "ai_reasoning": "Mess catering quality issue.",
                "internal_notes": "Caterer warned; warmer units checked and batch replaced.",
                "created_at": now - datetime.timedelta(days=1, hours=8),
                "updated_at": now - datetime.timedelta(days=1),
                "resolved_at": now - datetime.timedelta(days=1),
                "events": [
                    ("SUBMISSION", "SUBMITTED", "Student via Gehor AI", "Mess complaint logged.", now - datetime.timedelta(days=1, hours=8)),
                    ("CLASSIFICATION", "Mess / Food / MEDIUM", "Gehor AI", "Categorized as Food & Catering.", now - datetime.timedelta(days=1, hours=8)),
                    ("ASSIGNMENT", "Supervisor Anand", "Admin", "Assigned to Mess Supervisor.", now - datetime.timedelta(days=1, hours=6)),
                    ("STATUS_CHANGE", "IN_PROGRESS", "Supervisor Anand", "Kitchen inspection conducted.", now - datetime.timedelta(days=1, hours=4)),
                    ("RESOLUTION", "RESOLVED", "Supervisor Anand", "Food warmer trays calibrated, vendor warned.", now - datetime.timedelta(days=1))
                ]
            },
            {
                "id": "GH-2026-1038",
                "student_id": "STU-2026-610",
                "student_name": "Rohan Nair",
                "student_contact": "+91 98444 55667",
                "title": "Exposed live wire sparking in Chemistry Lab",
                "description": "Active electric sparking from overhead conduit near bench 4 in Chemistry Lab 302. Burning plastic odor present.",
                "category": "Electrical",
                "subcategory": "Wiring & Power Sockets",
                "severity": "CRITICAL",
                "location": "Chemistry Lab 302, Bench 4",
                "department_name": "Maintenance & Engineering",
                "assigned_to": "Er. Rajesh Sharma",
                "status": "IN_PROGRESS",
                "ai_confidence": 0.99,
                "ai_intent": "CREATE_COMPLAINT",
                "ai_reasoning": "Active electrical sparks & burning smell flagged as CRITICAL emergency hazard.",
                "internal_notes": "Lab circuit breaker tripped remotely. Technician on site with multimeter.",
                "created_at": now - datetime.timedelta(minutes=50),
                "updated_at": now - datetime.timedelta(minutes=15),
                "events": [
                    ("SUBMISSION", "SUBMITTED", "Student via Gehor AI", "CRITICAL electrical hazard reported.", now - datetime.timedelta(minutes=50)),
                    ("CLASSIFICATION", "Electrical / CRITICAL", "Gehor AI Classifier", "Emergency rule triggered: 'sparking', 'burning smell'.", now - datetime.timedelta(minutes=50)),
                    ("ROUTING", "Maintenance & Engineering", "Gehor Emergency Route", "Immediate escalation.", now - datetime.timedelta(minutes=49)),
                    ("ASSIGNMENT", "Er. Rajesh Sharma", "System Auto-Escalation", "Immediate dispatch to electrical staff.", now - datetime.timedelta(minutes=30)),
                    ("STATUS_CHANGE", "IN_PROGRESS", "Er. Rajesh Sharma", "Technician dispatched on site.", now - datetime.timedelta(minutes=15))
                ]
            },
            {
                "id": "GH-2026-1039",
                "student_id": "STU-2026-554",
                "student_name": "Kavita Rao",
                "student_contact": "+91 98555 66778",
                "title": "Classroom B-204 AC blowing warm air",
                "description": "Split AC in room B-204 is not cooling at all during afternoon lectures. Ambient temperature reached 32C.",
                "category": "Infrastructure",
                "subcategory": "HVAC / Cooling",
                "severity": "MEDIUM",
                "location": "Academic Quad B-204",
                "department_name": "Maintenance & Engineering",
                "assigned_to": "Technician Manoj",
                "status": "SUBMITTED",
                "ai_confidence": 0.94,
                "ai_intent": "CREATE_COMPLAINT",
                "ai_reasoning": "Air conditioner non-cooling in teaching classroom.",
                "internal_notes": None,
                "created_at": now - datetime.timedelta(hours=1, minutes=20),
                "updated_at": now - datetime.timedelta(hours=1, minutes=20),
                "events": [
                    ("SUBMISSION", "SUBMITTED", "Student via Gehor AI", "Classroom AC issue submitted.", now - datetime.timedelta(hours=1, minutes=20)),
                    ("CLASSIFICATION", "Infrastructure / MEDIUM", "Gehor AI", "Categorized as HVAC Maintenance.", now - datetime.timedelta(hours=1, minutes=20)),
                    ("ROUTING", "Maintenance & Engineering", "Gehor Routing", "Routed to Maintenance queue.", now - datetime.timedelta(hours=1, minutes=20))
                ]
            },
            {
                "id": "GH-2026-1040",
                "student_id": "STU-2026-443",
                "student_name": "Aman Khan",
                "student_contact": "+91 98666 77889",
                "title": "Shuttle bus skipping Hostel Gate stop",
                "description": "Campus shuttle bus route #3 failed to halt at Hostel Gate 2 during morning 8:40 AM shift, causing students to be late for exams.",
                "category": "Transport",
                "subcategory": "Campus Transit",
                "severity": "MEDIUM",
                "location": "Hostel Gate 2 Bus Stop",
                "department_name": "Transport Office",
                "assigned_to": "Mr. Vikram Sethi",
                "status": "RESOLVED",
                "ai_confidence": 0.95,
                "ai_intent": "CREATE_COMPLAINT",
                "ai_reasoning": "Transit route schedule compliance issue.",
                "internal_notes": "Driver counseling completed. GPS logs verified.",
                "created_at": now - datetime.timedelta(days=2),
                "updated_at": now - datetime.timedelta(days=1, hours=10),
                "resolved_at": now - datetime.timedelta(days=1, hours=10),
                "events": [
                    ("SUBMISSION", "SUBMITTED", "Student via Gehor AI", "Transit issue logged.", now - datetime.timedelta(days=2)),
                    ("ROUTING", "Transport Office", "Gehor Routing", "Routed to Transport Office.", now - datetime.timedelta(days=2)),
                    ("ASSIGNMENT", "Mr. Vikram Sethi", "Admin", "Assigned to transport manager.", now - datetime.timedelta(days=1, hours=18)),
                    ("RESOLUTION", "RESOLVED", "Mr. Vikram Sethi", "Driver reprimanded and extra 8:40 AM shuttle assigned.", now - datetime.timedelta(days=1, hours=10))
                ]
            },
            {
                "id": "GH-2026-1041",
                "student_id": "STU-2026-312",
                "student_name": "Meera Joshi",
                "student_contact": "+91 98777 88990",
                "title": "2nd floor washroom dustbin overflowing",
                "description": "Sanitary dustbins in Library 2nd floor women's washroom haven't been emptied since yesterday.",
                "category": "Cleanliness",
                "subcategory": "Sanitation & Housekeeping",
                "severity": "LOW",
                "location": "Central Library, 2nd Floor",
                "department_name": "Housekeeping & Cleanliness",
                "assigned_to": "Mrs. Sunita Devi",
                "status": "RESOLVED",
                "ai_confidence": 0.97,
                "ai_intent": "CREATE_COMPLAINT",
                "ai_reasoning": "Routine housekeeping sanitation task.",
                "internal_notes": "Cleaned during evening round.",
                "created_at": now - datetime.timedelta(hours=18),
                "updated_at": now - datetime.timedelta(hours=14),
                "resolved_at": now - datetime.timedelta(hours=14),
                "events": [
                    ("SUBMISSION", "SUBMITTED", "Student via Gehor AI", "Housekeeping ticket created.", now - datetime.timedelta(hours=18)),
                    ("ROUTING", "Housekeeping & Cleanliness", "Gehor Routing", "Routed to Housekeeping.", now - datetime.timedelta(hours=18)),
                    ("RESOLUTION", "RESOLVED", "Mrs. Sunita Devi", "Washrooms sanitized and waste disposed.", now - datetime.timedelta(hours=14))
                ]
            }
        ]

        for s in sample_complaints:
            events_data = s.pop("events", [])
            complaint = Complaint(**s)
            db.add(complaint)
            for ev in events_data:
                event_obj = ComplaintEvent(
                    complaint_id=complaint.id,
                    event_type=ev[0],
                    new_value=ev[1],
                    performed_by=ev[2],
                    notes=ev[3],
                    timestamp=ev[4]
                )
                db.add(event_obj)
        db.commit()
