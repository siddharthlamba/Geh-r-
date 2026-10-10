"""
Duplicate detection engine for Gehor complaints.
Detects similar active complaints within recent hours based on location and keywords.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from .models import Complaint

def check_duplicate_complaints(
    description: str,
    location: str,
    category: str,
    db: Session
) -> Optional[Dict[str, Any]]:
    """
    Checks if an unresolved complaint matches similar category and location/issue.
    """
    if not db:
        return None
        
    active_complaints = db.query(Complaint).filter(
        Complaint.status.in_(["SUBMITTED", "CLASSIFIED", "ASSIGNED", "IN_PROGRESS"])
    ).all()
    
    desc_words = set(w.lower() for w in description.split() if len(w) > 3)
    loc_words = set(w.lower() for w in location.split() if len(w) > 2)

    for item in active_complaints:
        # 1. Same category match
        is_same_cat = (item.category == category)
        
        # 2. Location match
        item_loc_words = set(w.lower() for w in item.location.split() if len(w) > 2)
        loc_overlap = loc_words.intersection(item_loc_words)
        
        # 3. Description overlap
        item_desc_words = set(w.lower() for w in item.description.split() if len(w) > 3)
        desc_overlap = desc_words.intersection(item_desc_words)

        if is_same_cat and (loc_overlap or len(desc_overlap) >= 2):
            return {
                "id": item.id,
                "title": item.title,
                "location": item.location,
                "status": item.status,
                "department": item.department_name,
                "created_at": item.created_at.strftime("%b %d, %H:%M"),
                "reason": f"Active ticket #{item.id} shares matching context in {item.location} ({', '.join(desc_overlap or loc_overlap)})."
            }
            
    return None
