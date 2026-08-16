from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.approval.models import Approval, ApprovalState

router = APIRouter(prefix="/approvals", tags=["approvals"])

# For demonstration in Wave 7 (in-memory store for approvals)
_approval_store: dict[str, Approval] = {}

class ApprovalCreateRequest(BaseModel):
    target_type: str
    target_id: str
    requested_by: str
    metadata: dict[str, Any] = {}

class RejectRequest(BaseModel):
    user_id: str
    reason: str

@router.post("/", response_model=Approval)
async def create_approval(req: ApprovalCreateRequest):
    approval = Approval(
        target_type=req.target_type,
        target_id=req.target_id,
        state=ApprovalState.REQUIRED,
        requested_by=req.requested_by,
        metadata=req.metadata
    )
    _approval_store[approval.approval_id] = approval
    return approval

@router.get("/{approval_id}", response_model=Approval)
async def get_approval(approval_id: str):
    if approval_id not in _approval_store:
        raise HTTPException(status_code=404, detail="Approval not found")
    return _approval_store[approval_id]

@router.post("/{approval_id}/approve", response_model=Approval)
async def approve(approval_id: str, user_id: str):
    if approval_id not in _approval_store:
        raise HTTPException(status_code=404, detail="Approval not found")
    approval = _approval_store[approval_id]
    try:
        approval.approve(user_id=user_id)
        # TODO: Publish ApprovalApprovedEvent to EventBus
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return approval

@router.post("/{approval_id}/reject", response_model=Approval)
async def reject(approval_id: str, req: RejectRequest):
    if approval_id not in _approval_store:
        raise HTTPException(status_code=404, detail="Approval not found")
    approval = _approval_store[approval_id]
    try:
        approval.reject(user_id=req.user_id, reason=req.reason)
        # TODO: Publish ApprovalRejectedEvent to EventBus
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return approval
