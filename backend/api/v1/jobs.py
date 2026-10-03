import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.dependencies.auth import get_current_user, CurrentUser
from backend.dependencies.db import get_tenant_db
from backend.core.services.extraction import GLiNERExtractor
from database.models import Job

router = APIRouter()
extractor = GLiNERExtractor()

class JobCreateRequest(BaseModel):
    title: str
    description_text: str

class CompetencyItem(BaseModel):
    name: str
    type: str
    score: float

class JobResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    competencies: List[dict]

    class Config:
        from_attributes = True

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID required to create jobs",
        )

    # Extract competencies using GLiNER extractor
    extracted_competencies = extractor.extract_competencies(payload.description_text)

    job_id = str(uuid.uuid4())
    new_job = Job(
        id=job_id,
        tenant_id=current_user.tenant_id,
        title=payload.title,
        competencies=extracted_competencies,
    )

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    return JobResponse(
        id=new_job.id,
        tenant_id=new_job.tenant_id,
        title=new_job.title,
        competencies=new_job.competencies,
    )

@router.get("", response_model=List[JobResponse])
async def list_jobs(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID required to list jobs",
        )

    stmt = select(Job).where(Job.tenant_id == current_user.tenant_id)
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    return [
        JobResponse(
            id=job.id,
            tenant_id=job.tenant_id,
            title=job.title,
            competencies=job.competencies,
        )
        for job in jobs
    ]

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID required to fetch job",
        )

    stmt = select(Job).where(Job.id == job_id, Job.tenant_id == current_user.tenant_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return JobResponse(
        id=job.id,
        tenant_id=job.tenant_id,
        title=job.title,
        competencies=job.competencies,
    )
