"""Session management API endpoints"""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.core.database import get_session
from app.core.scheduler import scheduler
from app.core.config import get_settings
from app.state_machine import state_machine, KioskState

router = APIRouter()
settings = get_settings()

# In-memory session storage (in production, use Redis or similar)
sessions = {}


@router.post("/start")
async def start_session(request: Request):
    """Start new kiosk session"""
    session_id = str(uuid.uuid4())
    
    # Create session data
    session_data = {
        "id": session_id,
        "started_at": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "state": KioskState.HOME.name,
        "context": {}
    }
    
    sessions[session_id] = session_data
    
    # Setup session timeout
    scheduler.add_session_timeout(
        session_id=session_id,
        timeout_seconds=settings.session_timeout_seconds,
        callback=lambda: end_session_timeout(session_id)
    )
    
    return {
        "session_id": session_id,
        "timeout_seconds": settings.session_timeout_seconds
    }


@router.post("/activity/{session_id}")
async def update_activity(session_id: str):
    """Update session activity timestamp"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions[session_id]["last_activity"] = datetime.utcnow()
    
    # Reset timeout
    scheduler.reset_session_timeout(session_id)
    
    return {"status": "activity updated"}


@router.get("/status/{session_id}")
async def get_session_status(session_id: str):
    """Get current session status"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    
    # Calculate time remaining
    elapsed = (datetime.utcnow() - session_data["last_activity"]).total_seconds()
    time_remaining = max(0, settings.session_timeout_seconds - elapsed)
    
    return {
        "session_id": session_id,
        "state": session_data["state"],
        "started_at": session_data["started_at"],
        "last_activity": session_data["last_activity"],
        "time_remaining_seconds": int(time_remaining),
        "context": session_data.get("context", {})
    }


@router.post("/end/{session_id}")
async def end_session(session_id: str):
    """End session and cleanup"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Cancel timeout
    scheduler.cancel_session_timeout(session_id)
    
    # Clear session data
    del sessions[session_id]
    
    # Reset state machine
    state_machine.reset_to_home()
    
    return {"status": "session ended"}


@router.post("/transition/{session_id}")
async def state_transition(
    session_id: str,
    trigger: str,
    context: Optional[dict] = None
):
    """Trigger state transition"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update activity
    sessions[session_id]["last_activity"] = datetime.utcnow()
    scheduler.reset_session_timeout(session_id)
    
    # Update context if provided
    if context:
        sessions[session_id]["context"].update(context)
        for key, value in context.items():
            state_machine.set_context(key, value)
    
    # Trigger transition
    try:
        if hasattr(state_machine, trigger):
            getattr(state_machine, trigger)()
            sessions[session_id]["state"] = state_machine.state
            
            return {
                "status": "success",
                "new_state": state_machine.state,
                "available_transitions": state_machine.get_available_transitions()
            }
        else:
            raise ValueError(f"Invalid trigger: {trigger}")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def end_session_timeout(session_id: str):
    """Handle session timeout"""
    if session_id in sessions:
        # Log timeout
        session_data = sessions[session_id]
        duration = (datetime.utcnow() - session_data["started_at"]).total_seconds()
        
        # Clear session
        del sessions[session_id]
        
        # Reset state machine
        state_machine.reset_to_home()


@router.get("/active")
async def get_active_sessions():
    """Get count of active sessions (admin endpoint)"""
    active_count = len(sessions)
    
    # Get session details
    session_list = []
    for sid, data in sessions.items():
        elapsed = (datetime.utcnow() - data["last_activity"]).total_seconds()
        session_list.append({
            "id": sid,
            "state": data["state"],
            "duration_seconds": int((datetime.utcnow() - data["started_at"]).total_seconds()),
            "idle_seconds": int(elapsed)
        })
    
    return {
        "active_count": active_count,
        "sessions": session_list
    }