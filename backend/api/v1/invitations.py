from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.services.tokens import generate_guest_token
from backend.core.services.email import EmailDispatcher
from backend.dependencies.auth import get_current_user, CurrentUser, get_actor, AuthActor
from backend.dependencies.db import get_tenant_db
from database.models import Invitation, Drive, Candidate

router = APIRouter(prefix="/invitations", tags=["invitations"])

class GenerateTokenRequest(BaseModel):
    candidate_id: str
    interview_id: str

class GenerateTokenResponse(BaseModel):
    token: str

class InvitationStatusUpdateRequest(BaseModel):
    status: str # PENDING, SENT, OPENED, IN_PROGRESS, COMPLETED, EXPIRED

class InvitationDetailResponse(BaseModel):
    id: str
    tenant_id: str
    drive_id: str
    candidate_id: str
    email: str
    status: str
    token: str

@router.post("/generate", response_model=GenerateTokenResponse)
def generate_token(request: GenerateTokenRequest):
    try:
        token = generate_guest_token(request.candidate_id, request.interview_id)
        return GenerateTokenResponse(token=token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{invitation_id}", response_model=InvitationDetailResponse)
async def get_invitation(
    invitation_id: str,
    db: AsyncSession = Depends(get_tenant_db),
):
    stmt = select(Invitation).where(Invitation.id == invitation_id)
    res = await db.execute(stmt)
    inv = res.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    return InvitationDetailResponse(
        id=inv.id,
        tenant_id=inv.tenant_id,
        drive_id=inv.drive_id,
        candidate_id=inv.candidate_id,
        email=inv.email,
        status=inv.status,
        token=inv.token,
    )

@router.put("/{invitation_id}/status", response_model=InvitationDetailResponse)
async def update_invitation_status(
    invitation_id: str,
    payload: InvitationStatusUpdateRequest,
    db: AsyncSession = Depends(get_tenant_db),
):
    stmt = select(Invitation).where(Invitation.id == invitation_id)
    res = await db.execute(stmt)
    inv = res.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    new_status = payload.status.upper()
    valid_statuses = ["PENDING", "SENT", "OPENED", "IN_PROGRESS", "COMPLETED", "EXPIRED"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {payload.status}")

    inv.status = new_status
    await db.commit()
    await db.refresh(inv)

    return InvitationDetailResponse(
        id=inv.id,
        tenant_id=inv.tenant_id,
        drive_id=inv.drive_id,
        candidate_id=inv.candidate_id,
        email=inv.email,
        status=inv.status,
        token=inv.token,
    )

@router.put("/resend/{invitation_id}", response_model=InvitationDetailResponse)
async def resend_invitation(
    invitation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant ID required")

    stmt = select(Invitation).where(Invitation.id == invitation_id, Invitation.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    inv = res.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found for this tenant")

    # Load candidate and drive
    cand_stmt = select(Candidate).where(Candidate.id == inv.candidate_id)
    cand_res = await db.execute(cand_stmt)
    candidate = cand_res.scalar_one_or_none()

    drive_stmt = select(Drive).where(Drive.id == inv.drive_id)
    drive_res = await db.execute(drive_stmt)
    drive = drive_res.scalar_one_or_none()

    session_url = f"/interview/{inv.id}?token={inv.token}"
    dispatcher = EmailDispatcher()
    dispatcher.send_invitation(
        recipient_email=inv.email,
        candidate_name=candidate.name if candidate else "Candidate",
        job_title=drive.name if drive else "Technical Role",
        interview_link=session_url
    )

    inv.status = "SENT"
    await db.commit()
    await db.refresh(inv)

    return InvitationDetailResponse(
        id=inv.id,
        tenant_id=inv.tenant_id,
        drive_id=inv.drive_id,
        candidate_id=inv.candidate_id,
        email=inv.email,
        status=inv.status,
        token=inv.token,
    )
