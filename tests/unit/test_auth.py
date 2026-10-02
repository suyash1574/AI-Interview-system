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
