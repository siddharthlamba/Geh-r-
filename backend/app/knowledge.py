"""
Knowledge base engine and campus FAQ search for Gehor.
"""

INITIAL_KNOWLEDGE_DOCS = [
    {
        "title": "Hostel Timings & Gate Pass Rules",
        "category": "Hostel",
        "tags": "curfew, gate pass, timing, entry, late, night out",
        "content": "Hostel curfew is 10:30 PM on weekdays and 11:00 PM on weekends. Night-out gate passes must be requested through the Student Portal at least 6 hours in advance and approved by the Hostel Warden. Emergency entry after curfew requires verification at Main Gate Security."
    },
    {
        "title": "Hostel Mess & Dining Hours",
        "category": "Mess / Food",
        "tags": "mess, breakfast, lunch, dinner, food, snacks, dining",
        "content": "Dining Hall Hours:\n• Breakfast: 7:30 AM – 9:30 AM\n• Lunch: 12:30 PM – 2:30 PM\n• Evening Snacks: 5:00 PM – 6:15 PM\n• Dinner: 7:45 PM – 9:45 PM\nFor dietary grievances, food quality reports, or hygiene concerns, complaints are escalated directly to the Mess Supervisor and Student Mess Committee."
    },
    {
        "title": "Campus Wi-Fi & Network Access",
        "category": "IT / Network",
        "tags": "wifi, internet, eduroam, login, password, network, lan",
        "content": "Connect to 'Campus-Secure' or 'eduroam' using your Student ID (STU-XXXX) and campus password. If you experience authentication failures, reset your password at itportal.campus.edu. For physical LAN port issues in hostel rooms, submit an IT complaint."
    },
    {
        "title": "Campus Health Center & Medical Emergency",
        "category": "Security / Health",
        "tags": "health, doctor, ambulance, clinic, emergency, medicine, injury",
        "content": "The Campus Medical Center is open 24/7 next to Student Center Block B. Emergency Ambulance Helpline: +91 98765 00108 / Extension 108. For emergency trauma or acute medical illness, security provides immediate campus transit."
    },
    {
        "title": "Campus Shuttle Bus Schedule",
        "category": "Transport",
        "tags": "bus, shuttle, transport, timing, route, metro",
        "content": "Campus shuttle buses run every 20 minutes from 7:00 AM to 10:00 PM between Hostel Complex, Academic Quad, Library, and the University Metro Station. During peak hours (8 AM - 10 AM, 5 PM - 7 PM), buses operate every 10 minutes."
    },
    {
        "title": "Complaint Resolution SLAs & Escalation",
        "category": "Administration",
        "tags": "sla, policy, timeline, priority, urgent, resolution time",
        "content": "Complaint SLAs:\n• CRITICAL (Safety/Hazard): 2 Hours maximum response\n• HIGH (Major amenity failure): 6-8 Hours\n• MEDIUM (Room fixtures, Wi-Fi): 12-24 Hours\n• LOW (Minor repairs): 48 Hours\nStudents can track complaint progress live using their Complaint ID (GH-2026-XXXX)."
    }
]

def search_knowledge(query: str, db=None) -> list:
    """
    Search campus knowledge base for relevant FAQ answers.
    Matches keywords and semantic tags.
    """
    q = query.lower()
    results = []
    
    for doc in INITIAL_KNOWLEDGE_DOCS:
        score = 0
        title_lower = doc["title"].lower()
        content_lower = doc["content"].lower()
        tags_lower = doc.get("tags", "").lower()
        
        # Word overlap
        query_words = [w for w in q.split() if len(w) > 3]
        for w in query_words:
            if w in title_lower:
                score += 3
            if w in tags_lower:
                score += 2
            if w in content_lower:
                score += 1
                
        if score > 0:
            results.append((score, doc))
            
    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results[:2]]
