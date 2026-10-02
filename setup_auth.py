import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')

with open('requirements.txt', 'a') as f:
    f.write('PyJWT[crypto]==2.8.0\n')
    f.write('httpx==0.25.2\n')

write_file('backend/config.py', """
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://autergo:autergo@localhost/autergo"
    CLERK_JWKS_URL: str = "https://clerk.autergo.com/.well-known/jwks.json"
    class Config:
        env_file = ".env"

settings = Settings()
""")

write_file('backend/dependencies/__init__.py', '')
write_file('backend/dependencies/auth.py', """
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
""")

write_file('tests/unit/test_auth.py', """
import pytest
from fastapi import HTTPException
from unittest.mock import patch, AsyncMock, MagicMock
from backend.dependencies.auth import get_current_user, CurrentUser, verify_token
from backend.core.errors import AuthorizationError
from fastapi.security import HTTPAuthorizationCredentials

@pytest.mark.asyncio
@patch('backend.dependencies.auth.get_jwks')
@patch('backend.dependencies.auth.verify_token')
async def test_get_current_user_success(mock_verify, mock_get_jwks):
    mock_get_jwks.return_value = {"keys": []}
    mock_verify.return_value = {
        "sub": "user_123",
        "org_id": "tenant_456",
        "org_metadata": {"role": "COMPANY_ADMIN"}
    }
    
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake_token")
    user = await get_current_user(creds)
    
    assert isinstance(user, CurrentUser)
    assert user.user_id == "user_123"
    assert user.tenant_id == "tenant_456"
    assert user.role == "COMPANY_ADMIN"

@pytest.mark.asyncio
@patch('backend.dependencies.auth.get_jwks')
@patch('backend.dependencies.auth.verify_token')
async def test_get_current_user_failure(mock_verify, mock_get_jwks):
    mock_get_jwks.return_value = {"keys": []}
    mock_verify.side_effect = AuthorizationError("Invalid claims")
    
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad_token")
    
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(creds)
        
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid claims"
""")

print("Authentication setup complete.")
