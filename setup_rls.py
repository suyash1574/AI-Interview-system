import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')

write_file('backend/dependencies/db.py', '''
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database.session import AsyncSessionLocal
from backend.dependencies.auth import get_current_user, CurrentUser

async def get_tenant_db(user: CurrentUser = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        if user.tenant_id:
            # Set tenant context for PostgreSQL RLS
            # Using SET LOCAL ensures the setting only lasts for the duration of the transaction
            await session.execute(text("SET LOCAL app.current_tenant = :tenant_id").bindparams(tenant_id=user.tenant_id))
        yield session
''')

write_file('database/migrations/versions/0001_initial_and_rls.py', '''
"""Initial schema and RLS

Revision ID: 0001
Revises: 
Create Date: 2026-10-02 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create Tables
    op.create_table('tenants',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('jobs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('competencies', JSONB, nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('candidates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('interviews',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('transcript', JSONB, nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('evaluations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('interview_id', sa.String(), nullable=False),
        sa.Column('score_raw', sa.Integer(), nullable=True),
        sa.Column('evidence', JSONB, nullable=True),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Enable RLS
    for table in ['users', 'jobs', 'candidates', 'interviews']:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"""
            CREATE POLICY tenant_isolation_policy ON {table}
            USING (tenant_id = current_setting('app.current_tenant', true));
        """)

def downgrade() -> None:
    for table in ['evaluations', 'interviews', 'candidates', 'jobs', 'users', 'tenants']:
        op.drop_table(table)
''')

write_file('tests/unit/test_rls_dependency.py', '''
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
''')

print("RLS setup complete.")
