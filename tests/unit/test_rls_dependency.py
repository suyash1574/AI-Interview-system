import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from backend.dependencies.db import get_tenant_db
from backend.dependencies.auth import CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
@patch('backend.dependencies.db.AsyncSessionLocal')
async def test_get_tenant_db_sets_rls(mock_session_local):
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session_local.return_value.__aenter__.return_value = mock_session
    
    user = CurrentUser(user_id="user_1", tenant_id="tenant_123", role="ADMIN")
    
    gen = get_tenant_db(user)
    session = await anext(gen)
    
    assert session == mock_session
    # Verify execute was called to set the tenant
    assert mock_session.execute.call_count == 1
    call_args = mock_session.execute.call_args[0][0]
    assert "SET LOCAL app.current_tenant" in str(call_args)
