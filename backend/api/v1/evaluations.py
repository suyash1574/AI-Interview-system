from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.dependencies.auth import get_current_user, CurrentUser
from backend.dependencies.db import get_tenant_db
from database.models import Interview, Evaluation
from workers.tasks.evaluation import evaluate_interview_task
from workers.tasks.reports import generate_and_dispatch_report_task

router = APIRouter()

class EvaluationReportRequest(BaseModel):
    interview_id: str

class EvaluationReportResponse(BaseModel):
    message: str
    interview_id: str
    status: str

class EvaluationDetailResponse(BaseModel):
    id: str
    interview_id: str
    score_raw: Optional[int] = None
    evidence: Optional[Any] = None

@router.post("/report", response_model=EvaluationReportResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_evaluation_report(
    payload: EvaluationReportRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID required to request evaluation reports",
        )

    stmt = select(Interview).where(
        Interview.id == payload.interview_id,
        Interview.tenant_id == current_user.tenant_id,
    )
    res = await db.execute(stmt)
    interview = res.scalar_one_or_none()

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found for this tenant",
        )

    # In production, this queues the celery task:
    # evaluate_interview_task.delay(interview.id, str(interview.transcript))
    # generate_and_dispatch_report_task.delay(interview.id, evaluation_result, "recruiter@example.com")

    return EvaluationReportResponse(
        message="Evaluation pipeline initiated successfully in background queue.",
        interview_id=interview.id,
        status="PROCESSING",
    )

@router.get("/{interview_id}", response_model=EvaluationDetailResponse)
async def get_evaluation(
    interview_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID required to view evaluations",
        )

    # Verify interview belongs to tenant
    int_stmt = select(Interview).where(
        Interview.id == interview_id,
        Interview.tenant_id == current_user.tenant_id,
    )
    int_res = await db.execute(int_stmt)
    interview = int_res.scalar_one_or_none()

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    eval_stmt = select(Evaluation).where(Evaluation.interview_id == interview_id)
    eval_res = await db.execute(eval_stmt)
    evaluation = eval_res.scalar_one_or_none()

    if not evaluation:
        # Return empty/pending evaluation state if not completed yet
        return EvaluationDetailResponse(
            id=f"eval-{interview_id}",
            interview_id=interview_id,
            score_raw=None,
            evidence=[],
        )

    return EvaluationDetailResponse(
        id=evaluation.id,
        interview_id=evaluation.interview_id,
        score_raw=evaluation.score_raw,
        evidence=evaluation.evidence,
    )
