import jwt
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import httpx
from pydantic import BaseModel

from backend.config import settings
from backend.core.errors import AuthorizationError

security = HTTPBearer()

# In-memory cache for JWKS
_jwks_cache = {}

class CurrentUser(BaseModel):
    user_id: str
    tenant_id: Optional[str] = None
    role: Optional[str] = None

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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CurrentUser:
    token = credentials.credentials
    try:
        jwks = await get_jwks()
        payload = verify_token(token, jwks)
        
        user_id = payload.get("sub")
        metadata = payload.get("org_metadata", {})
        tenant_id = payload.get("org_id")
        role = metadata.get("role")
        
        return CurrentUser(user_id=user_id, tenant_id=tenant_id, role=role)
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
