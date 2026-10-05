import jwt
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Union
import httpx
from pydantic import BaseModel

from backend.config import settings
from backend.core.errors import AuthorizationError
from backend.core.services.tokens import verify_guest_token

security = HTTPBearer()

# In-memory cache for JWKS
_jwks_cache = {}

class CurrentUser(BaseModel):
    user_id: str
    tenant_id: Optional[str] = None
    role: Optional[str] = None

class CandidateGuest(BaseModel):
    candidate_id: str
    interview_id: str
    role: str = "CANDIDATE"

class AuthActor(BaseModel):
    id: str
    role: str
    tenant_id: Optional[str] = None
    interview_id: Optional[str] = None
    is_candidate: bool = False

async def get_jwks():
    global _jwks_cache
    if not _jwks_cache:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(settings.CLERK_JWKS_URL)
                response.raise_for_status()
                _jwks_cache = response.json()
        except Exception as e:
            raise AuthorizationError(f"Failed to fetch JWKS: {str(e)}")
    return _jwks_cache

def verify_token(token: str, jwks: dict) -> dict:
    try:
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        
        if rsa_key:
            algorithm = jwt.algorithms.RSAAlgorithm.from_jwk(rsa_key)
            payload = jwt.decode(
                token,
                algorithm,
                algorithms=["RS256"],
                audience="autergo"
            )
            return payload
    except jwt.ExpiredSignatureError:
        raise AuthorizationError("Token expired")
    except jwt.exceptions.InvalidTokenError:
        raise AuthorizationError("Invalid claims")
    except Exception as e:
        raise AuthorizationError(f"Token validation failed: {str(e)}")
    raise AuthorizationError("Unable to find appropriate key")

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

async def ensure_clerk_provisioning(user_id: str, tenant_id: str, email: str, name: str, role: str):
    """Automatically provisions or updates Tenant and User records for authenticated Clerk users."""
    try:
        from database.session import AsyncSessionLocal
        from database.models import Tenant, User
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as db:
            # 1. Ensure Tenant exists
            t_stmt = select(Tenant).where(Tenant.id == tenant_id)
            t_res = await db.execute(t_stmt)
            tenant = t_res.scalar_one_or_none()
            if not tenant:
                tenant = Tenant(id=tenant_id, name="Default Organization")
                db.add(tenant)
                await db.flush()

            # 2. Ensure User exists
            u_stmt = select(User).where(User.clerk_id == user_id)
            u_res = await db.execute(u_stmt)
            user = u_res.scalar_one_or_none()
            if not user:
                user = User(
                    tenant_id=tenant_id,
                    clerk_id=user_id,
                    email=email,
                    name=name,
                    role=role or "RECRUITER",
                    email_verified=True,
                )
                db.add(user)
            else:
                user.last_login_at = datetime.now(timezone.utc)
            await db.commit()
    except Exception as e:
        logger.debug(f"User provisioning auto-sync deferred ({e})")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CurrentUser:
    token = credentials.credentials
    try:
        jwks = await get_jwks()
        payload = verify_token(token, jwks)
        
        user_id = payload.get("sub")
        metadata = payload.get("org_metadata", {})
        tenant_id = payload.get("org_id") or f"org_{user_id}"
        role = metadata.get("role") or "RECRUITER"
        email = payload.get("email") or f"{user_id}@autergo.com"
        name = payload.get("name") or "Recruiter"

        # Auto-provision tenant & user asynchronously
        import asyncio
        asyncio.create_task(ensure_clerk_provisioning(user_id, tenant_id, email, name, role))
        
        return CurrentUser(user_id=user_id, tenant_id=tenant_id, role=role)
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_candidate_guest(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CandidateGuest:
    token = credentials.credentials
    try:
        payload = verify_guest_token(token)
        candidate_id = payload.get("sub")
        interview_id = payload.get("interview_id")
        if not candidate_id or not interview_id:
            raise AuthorizationError("Malformed guest credentials")
        return CandidateGuest(candidate_id=candidate_id, interview_id=interview_id)
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_actor(credentials: HTTPAuthorizationCredentials = Depends(security)) -> AuthActor:
    token = credentials.credentials
    # Try candidate guest token first (HMAC HS256)
    try:
        payload = verify_guest_token(token)
        return AuthActor(
            id=payload["sub"],
            role="CANDIDATE",
            interview_id=payload.get("interview_id"),
            is_candidate=True
        )
    except Exception:
        pass

    # Fallback to Clerk JWT (RS256)
    try:
        jwks = await get_jwks()
        payload = verify_token(token, jwks)
        user_id = payload.get("sub")
        metadata = payload.get("org_metadata", {})
        return AuthActor(
            id=user_id,
            role=metadata.get("role", "RECRUITER"),
            tenant_id=payload.get("org_id"),
            is_candidate=False
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
