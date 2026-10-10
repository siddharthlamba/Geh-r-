import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import ChatRequest, ChatResponse, ChatMessageSchema
from ..models import ChatSession, ChatMessage
from ..agent import GehorAgent

router = APIRouter(prefix="/api/agent", tags=["Agent"])

@router.post("/message", response_model=ChatResponse)
def handle_agent_message(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Receives student conversational input and processes it through the Gehor Agent.
    """
    if not payload.message.strip() and not payload.evidence_url:
        raise HTTPException(status_code=400, detail="Message or evidence cannot be empty")
        
    agent = GehorAgent(db)
    result = agent.process_message(
        session_id=payload.session_id,
        user_message=payload.message,
        student_id=payload.student_id or "STU-2026-901",
        evidence_url=payload.evidence_url
    )
    return result

@router.get("/session/{session_id}")
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    """
    Returns full message history for the specified session.
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        return {"session_id": session_id, "messages": [], "state": "GREETING"}
        
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp).all()
    
    formatted = []
    for m in messages:
        formatted.append({
            "id": m.id,
            "sender": m.sender,
            "content": m.content,
            "message_type": m.message_type,
            "metadata": json.loads(m.metadata_json) if m.metadata_json else None,
            "timestamp": m.timestamp.isoformat()
        })
        
    return {
        "session_id": session.id,
        "state": session.state,
        "last_complaint_id": session.last_complaint_id,
        "messages": formatted
    }

@router.post("/session/{session_id}/reset")
def reset_session(session_id: str, db: Session = Depends(get_db)):
    """
    Resets conversation session so student can start a fresh issue report.
    Completely wipes conversational history and draft state.
    """
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session:
        session.state = "GREETING"
        session.extracted_data = "{}"
        session.last_complaint_id = None
    db.commit()
    return {"status": "success", "session_id": session_id}
