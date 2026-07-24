
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.session.models import Session

router = APIRouter(prefix="/sessions", tags=["sessions"])

# For demonstration in Wave 7 (in-memory store for sessions)
_session_store: dict[str, Session] = {}

class SessionCreateRequest(BaseModel):
    tenant_id: str
    user_id: str

@router.post("/", response_model=Session)
async def create_session(req: SessionCreateRequest):
    session = Session(
        tenant_id=req.tenant_id,
        user_id=req.user_id
    )
    _session_store[session.session_id] = session
    return session

@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str):
    if session_id not in _session_store:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_store[session_id]

@router.post("/{session_id}/conversations")
async def add_conversation(session_id: str, conversation_id: str):
    if session_id not in _session_store:
        raise HTTPException(status_code=404, detail="Session not found")
    session = _session_store[session_id]
    session.add_conversation(conversation_id)
    return session

@router.delete("/{session_id}")
async def close_session(session_id: str):
    if session_id not in _session_store:
        raise HTTPException(status_code=404, detail="Session not found")
    session = _session_store[session_id]
    session.close()
    return session
