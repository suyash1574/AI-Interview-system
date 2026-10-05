from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database.session import AsyncSessionLocal
from backend.dependencies.auth import get_current_user, CurrentUser

async def get_tenant_db(user: CurrentUser = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        if user.tenant_id:
            # Set tenant context for PostgreSQL RLS across all migration schemas
            await session.execute(
                text("SET LOCAL app.current_tenant = :tenant_id; SET LOCAL app.current_tenant_id = :tenant_id").bindparams(tenant_id=user.tenant_id)
            )
        yield session


