import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.config import settings
from backend.dependencies.auth import get_current_user, CurrentUser, get_actor, AuthActor
from backend.dependencies.db import get_tenant_db
from backend.core.services.tokens import generate_guest_token
from database.models import Interview, Job, Candidate

router = APIRouter()

class InterviewCreateRequest(BaseModel):
    job_id: str
    candidate_name: str
    candidate_email: EmailStr

class InterviewResponse(BaseModel):
    id: str
    tenant_id: str
    job_id: str
    candidate_id: str
    candidate_name: str
    candidate_email: str
    status: str
    guest_token: Optional[str] = None
    session_url: Optional[str] = None
    transcript: Optional[List[dict]] = None

class SessionCredentialsResponse(BaseModel):
    livekit_token: str
    ws_url: str
    session_id: str
    interview_id: str

@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    payload: InterviewCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID required to schedule interviews",
        )

    # Validate that job exists for this tenant
    job_stmt = select(Job).where(Job.id == payload.job_id, Job.tenant_id == current_user.tenant_id)
    job_res = await db.execute(job_stmt)
    job = job_res.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated job not found for this tenant",
        )

    # Find or create candidate in this tenant
    cand_stmt = select(Candidate).where(
        Candidate.email == payload.candidate_email,
        Candidate.tenant_id == current_user.tenant_id,
    )
    cand_res = await db.execute(cand_stmt)
    candidate = cand_res.scalar_one_or_none()

    if not candidate:
        candidate = Candidate(
            id=str(uuid.uuid4()),
            tenant_id=current_user.tenant_id,
            name=payload.candidate_name,
            email=payload.candidate_email,
        )
        db.add(candidate)
        await db.flush()

    interview_id = str(uuid.uuid4())
    interview = Interview(
        id=interview_id,
        tenant_id=current_user.tenant_id,
        job_id=job.id,
        candidate_id=candidate.id,
        status="PENDING",
        transcript=[],
    )
    db.add(interview)
    await db.commit()
    await db.refresh(interview)

    guest_token = generate_guest_token(candidate.id, interview.id)

    return InterviewResponse(
        id=interview.id,
        tenant_id=interview.tenant_id,
        job_id=interview.job_id,
        candidate_id=candidate.id,
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        status=interview.status,
        guest_token=guest_token,
        session_url=f"/interview/{interview.id}?token={guest_token}",
        transcript=interview.transcript or [],
    )

@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: str,
    actor: AuthActor = Depends(get_actor),
    db: AsyncSession = Depends(get_tenant_db),
):
    stmt = select(Interview).where(Interview.id == interview_id)
    res = await db.execute(stmt)
    interview = res.scalar_one_or_none()

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    # Candidate authorization check
    if actor.is_candidate and actor.interview_id != interview_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Candidate not authorized for this interview",
        )

    cand_stmt = select(Candidate).where(Candidate.id == interview.candidate_id)
    cand_res = await db.execute(cand_stmt)
    candidate = cand_res.scalar_one_or_none()

    return InterviewResponse(
        id=interview.id,
        tenant_id=interview.tenant_id,
        job_id=interview.job_id,
        candidate_id=interview.candidate_id,
        candidate_name=candidate.name if candidate else "Candidate",
        candidate_email=candidate.email if candidate else "",
        status=interview.status,
        transcript=interview.transcript or [],
    )

@router.post("/{interview_id}/session", response_model=SessionCredentialsResponse)
async def initiate_session(
    interview_id: str,
    actor: AuthActor = Depends(get_actor),
    db: AsyncSession = Depends(get_tenant_db),
):
    stmt = select(Interview).where(Interview.id == interview_id)
    res = await db.execute(stmt)
    interview = res.scalar_one_or_none()

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    if actor.is_candidate and actor.interview_id != interview_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Candidate not authorized for this interview session",
        )

    session_id = str(uuid.uuid4())
    room_name = f"interview-{interview.id}"

    # Generate LiveKit Token
    try:
        from livekit.api import AccessToken, VideoGrants
        token = AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
        token.with_identity(actor.id)
        token.with_name(f"Participant-{actor.id[:6]}")
        token.with_grants(VideoGrants(room_join=True, room=room_name))
        livekit_jwt = token.to_jwt()
    except Exception:
        # Fallback if LiveKit keys not configured
        livekit_jwt = f"mock-livekit-token-{session_id}"

    ws_url = f"/api/v1/realtime/interview/{session_id}?interview_id={interview.id}"

    return SessionCredentialsResponse(
        livekit_token=livekit_jwt,
        ws_url=ws_url,
        session_id=session_id,
        interview_id=interview.id,
    )
