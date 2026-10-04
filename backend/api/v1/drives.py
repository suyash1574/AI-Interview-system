import uuid
import csv
import io
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.dependencies.auth import get_current_user, CurrentUser
from backend.dependencies.db import get_tenant_db
from backend.core.services.tokens import generate_guest_token
from backend.core.services.email import EmailDispatcher
from database.models import Drive, Job, Candidate, Invitation, Interview, Evaluation

router = APIRouter()

class DriveCreateRequest(BaseModel):
    name: str
    job_id: str
    pass_threshold: int = 70
    config: Optional[Dict[str, Any]] = None

class DriveStatusUpdateRequest(BaseModel):
    status: str # ACTIVE, PAUSED, COMPLETED

class CandidateInviteItem(BaseModel):
    name: str
    email: EmailStr

class DriveInviteBatchRequest(BaseModel):
    candidates: List[CandidateInviteItem]

class DriveResponse(BaseModel):
    id: str
    tenant_id: str
    job_id: str
    name: str
    status: str
    pass_threshold: int
    config: Dict[str, Any]
    candidate_count: Optional[int] = 0
    completed_count: Optional[int] = 0

class InvitationResultItem(BaseModel):
    invitation_id: str
    candidate_id: str
    candidate_name: str
    email: str
    token: str
    session_url: str

class BulkCsvInviteResponse(BaseModel):
    total_parsed: int
    successful_invites: int
    results: List[InvitationResultItem]

@router.post("", response_model=DriveResponse, status_code=status.HTTP_201_CREATED)
async def create_drive(
    payload: DriveCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID required to create hiring drives",
        )

    job_stmt = select(Job).where(Job.id == payload.job_id, Job.tenant_id == current_user.tenant_id)
    job_res = await db.execute(job_stmt)
    job = job_res.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found for this tenant",
        )

    drive_id = str(uuid.uuid4())
    drive = Drive(
        id=drive_id,
        tenant_id=current_user.tenant_id,
        job_id=payload.job_id,
        name=payload.name,
        status="ACTIVE",
        pass_threshold=payload.pass_threshold,
        config=payload.config or {"duration_minutes": 25, "difficulty": "intermediate"},
    )
    db.add(drive)
    await db.commit()
    await db.refresh(drive)

    return DriveResponse(
        id=drive.id,
        tenant_id=drive.tenant_id,
        job_id=drive.job_id,
        name=drive.name,
        status=drive.status,
        pass_threshold=drive.pass_threshold,
        config=drive.config,
        candidate_count=0,
        completed_count=0,
    )

@router.get("", response_model=List[DriveResponse])
async def list_drives(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant ID required")

    stmt = select(Drive).where(Drive.tenant_id == current_user.tenant_id)
    result = await db.execute(stmt)
    drives = result.scalars().all()

    output = []
    for d in drives:
        # Dynamic candidate & completed counts
        count_stmt = select(func.count(Invitation.id)).where(Invitation.drive_id == d.id)
        count_res = await db.execute(count_stmt)
        candidate_count = count_res.scalar() or 0

        comp_stmt = select(func.count(Interview.id)).where(Interview.drive_id == d.id, Interview.status == "COMPLETED")
        comp_res = await db.execute(comp_stmt)
        completed_count = comp_res.scalar() or 0

        output.append(
            DriveResponse(
                id=d.id,
                tenant_id=d.tenant_id,
                job_id=d.job_id,
                name=d.name,
                status=d.status,
                pass_threshold=d.pass_threshold,
                config=d.config or {},
                candidate_count=candidate_count,
                completed_count=completed_count,
            )
        )
    return output

@router.get("/{drive_id}", response_model=DriveResponse)
async def get_drive(
    drive_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant ID required")

    stmt = select(Drive).where(Drive.id == drive_id, Drive.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    drive = res.scalar_one_or_none()

    if not drive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drive not found")

    count_stmt = select(func.count(Invitation.id)).where(Invitation.drive_id == drive.id)
    count_res = await db.execute(count_stmt)
    candidate_count = count_res.scalar() or 0

    comp_stmt = select(func.count(Interview.id)).where(Interview.drive_id == drive.id, Interview.status == "COMPLETED")
    comp_res = await db.execute(comp_stmt)
    completed_count = comp_res.scalar() or 0

    return DriveResponse(
        id=drive.id,
        tenant_id=drive.tenant_id,
        job_id=drive.job_id,
        name=drive.name,
        status=drive.status,
        pass_threshold=drive.pass_threshold,
        config=drive.config or {},
        candidate_count=candidate_count,
        completed_count=completed_count,
    )

@router.put("/{drive_id}/status", response_model=DriveResponse)
async def update_drive_status(
    drive_id: str,
    payload: DriveStatusUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    """Updates drive lifecycle status (ACTIVE, PAUSED, COMPLETED)."""
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant ID required")

    stmt = select(Drive).where(Drive.id == drive_id, Drive.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    drive = res.scalar_one_or_none()
    if not drive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drive not found")

    new_status = payload.status.upper()
    if new_status not in ["ACTIVE", "PAUSED", "COMPLETED", "DRAFT"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {payload.status}")

    drive.status = new_status
    await db.commit()
    await db.refresh(drive)

    return await get_drive(drive_id=drive_id, current_user=current_user, db=db)

@router.post("/{drive_id}/invitations", response_model=List[InvitationResultItem], status_code=status.HTTP_201_CREATED)
async def invite_candidates_to_drive(
    drive_id: str,
    payload: DriveInviteBatchRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant ID required")

    stmt = select(Drive).where(Drive.id == drive_id, Drive.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    drive = res.scalar_one_or_none()
    if not drive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drive not found")

    results = []
    dispatcher = EmailDispatcher()

    for item in payload.candidates:
        cand_stmt = select(Candidate).where(
            Candidate.email == item.email,
            Candidate.tenant_id == current_user.tenant_id,
        )
        cand_res = await db.execute(cand_stmt)
        candidate = cand_res.scalar_one_or_none()

        if not candidate:
            candidate = Candidate(
                id=str(uuid.uuid4()),
                tenant_id=current_user.tenant_id,
                name=item.name,
                email=item.email,
            )
            db.add(candidate)
            await db.flush()

        interview_id = str(uuid.uuid4())
        interview = Interview(
            id=interview_id,
            tenant_id=current_user.tenant_id,
            job_id=drive.job_id,
            drive_id=drive.id,
            candidate_id=candidate.id,
            status="PENDING",
            transcript=[],
        )
        db.add(interview)
        await db.flush()

        token = generate_guest_token(candidate.id, interview_id)
        invitation = Invitation(
            id=str(uuid.uuid4()),
            tenant_id=current_user.tenant_id,
            drive_id=drive.id,
            candidate_id=candidate.id,
            email=item.email,
            token=token,
            status="SENT",
        )
        db.add(invitation)

        session_url = f"/interview/{interview_id}?token={token}"
        dispatcher.send_invitation(
            recipient_email=candidate.email,
            candidate_name=candidate.name,
            job_title=drive.name,
            interview_link=session_url
        )

        results.append(
            InvitationResultItem(
                invitation_id=invitation.id,
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                email=candidate.email,
                token=token,
                session_url=session_url,
            )
        )

    await db.commit()
    return results

@router.post("/{drive_id}/invitations/bulk-csv", response_model=BulkCsvInviteResponse, status_code=status.HTTP_201_CREATED)
async def bulk_csv_invite_candidates(
    drive_id: str,
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    """
    Parses a CSV file containing columns `name` and `email` to invite candidates in bulk.
    """
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant ID required")

    content = await file.read()
    try:
        decoded_text = content.decode("utf-8")
    except UnicodeDecodeError:
        decoded_text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(decoded_text))
    candidates_to_invite = []

    for row in reader:
        # Standardize keys (strip whitespace and lower)
        clean_row = {k.strip().lower(): v.strip() for k, v in row.items() if k and v}
        name = clean_row.get("name") or clean_row.get("candidate_name") or clean_row.get("full_name")
        email = clean_row.get("email") or clean_row.get("candidate_email")

        if name and email and "@" in email:
            candidates_to_invite.append(CandidateInviteItem(name=name, email=email))

    if not candidates_to_invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid candidate rows with 'name' and 'email' found in CSV",
        )

    results = await invite_candidates_to_drive(
        drive_id=drive_id,
        payload=DriveInviteBatchRequest(candidates=candidates_to_invite),
        current_user=current_user,
        db=db,
    )

    return BulkCsvInviteResponse(
        total_parsed=len(candidates_to_invite),
        successful_invites=len(results),
        results=results,
    )
