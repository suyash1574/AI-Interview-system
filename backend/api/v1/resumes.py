import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.dependencies.auth import get_actor, AuthActor
from backend.dependencies.db import get_tenant_db
from backend.core.services.resume_parser import ResumeParserService
from database.models import Resume, Interview, Candidate

router = APIRouter()
resume_parser = ResumeParserService()

class ResumeResponse(BaseModel):
    id: str
    candidate_id: str
    filename: str
    extracted_skills: List[Dict[str, Any]]
    summary: str

@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    candidate_id: str = Form(...),
    interview_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    actor: AuthActor = Depends(get_actor),
    db: AsyncSession = Depends(get_tenant_db),
):
    # Verify authorization
    if actor.is_candidate and actor.id != candidate_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized candidate")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty resume file")

    parsed = resume_parser.parse(file.filename, file_bytes)

    resume_id = str(uuid.uuid4())
    tenant_id = actor.tenant_id or "default-tenant"

    # Get candidate tenant if candidate uploaded
    if actor.is_candidate:
        cand_stmt = select(Candidate).where(Candidate.id == candidate_id)
        cand_res = await db.execute(cand_stmt)
        cand = cand_res.scalar_one_or_none()
        if cand:
            tenant_id = cand.tenant_id

    resume = Resume(
        id=resume_id,
        tenant_id=tenant_id,
        candidate_id=candidate_id,
        filename=file.filename,
        parsed_text=parsed.raw_text,
        extracted_skills=parsed.skills,
        extracted_experience=[{"summary": parsed.summary}],
    )
    db.add(resume)

    # Link to interview if specified
    if interview_id:
        stmt = (
            update(Interview)
            .where(Interview.id == interview_id)
            .values(resume_id=resume.id)
        )
        await db.execute(stmt)

    await db.commit()

    return ResumeResponse(
        id=resume.id,
        candidate_id=resume.candidate_id,
        filename=resume.filename,
        extracted_skills=resume.extracted_skills or [],
        summary=parsed.summary,
    )

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    actor: AuthActor = Depends(get_actor),
    db: AsyncSession = Depends(get_tenant_db),
):
    stmt = select(Resume).where(Resume.id == resume_id)
    res = await db.execute(stmt)
    resume = res.scalar_one_or_none()

    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    summary = ""
    if resume.extracted_experience and len(resume.extracted_experience) > 0:
        summary = resume.extracted_experience[0].get("summary", "")

    return ResumeResponse(
        id=resume.id,
        candidate_id=resume.candidate_id,
        filename=resume.filename,
        extracted_skills=resume.extracted_skills or [],
        summary=summary,
    )
