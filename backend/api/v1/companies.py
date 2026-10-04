import uuid
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.dependencies.auth import get_current_user, CurrentUser
from backend.dependencies.db import get_tenant_db
from database.models import Company, Tenant

router = APIRouter()

class CompanyCreateRequest(BaseModel):
    name: str
    domain: Optional[str] = None
    tier: str = "ENTERPRISE"
    settings: Optional[Dict[str, Any]] = None

class CompanyUpdateRequest(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    tier: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class CompanyResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    domain: Optional[str] = None
    tier: str
    settings: Dict[str, Any]

@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    payload: CompanyCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID required to create company profile",
        )

    # Check if company already exists for tenant
    stmt = select(Company).where(Company.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    existing = res.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company already registered for this tenant",
        )

    company_id = str(uuid.uuid4())
    company = Company(
        id=company_id,
        tenant_id=current_user.tenant_id,
        name=payload.name,
        domain=payload.domain,
        tier=payload.tier,
        settings=payload.settings or {},
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)

    return CompanyResponse(
        id=company.id,
        tenant_id=company.tenant_id,
        name=company.name,
        domain=company.domain,
        tier=company.tier,
        settings=company.settings or {},
    )

@router.get("/me", response_model=CompanyResponse)
async def get_my_company(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant ID required")

    stmt = select(Company).where(Company.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    company = res.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found")

    return CompanyResponse(
        id=company.id,
        tenant_id=company.tenant_id,
        name=company.name,
        domain=company.domain,
        tier=company.tier,
        settings=company.settings or {},
    )

@router.put("/me", response_model=CompanyResponse)
async def update_my_company(
    payload: CompanyUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant ID required")

    stmt = select(Company).where(Company.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    company = res.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found")

    if payload.name is not None:
        company.name = payload.name
    if payload.domain is not None:
        company.domain = payload.domain
    if payload.tier is not None:
        company.tier = payload.tier
    if payload.settings is not None:
        company.settings = payload.settings

    await db.commit()
    await db.refresh(company)

    return CompanyResponse(
        id=company.id,
        tenant_id=company.tenant_id,
        name=company.name,
        domain=company.domain,
        tier=company.tier,
        settings=company.settings or {},
    )
