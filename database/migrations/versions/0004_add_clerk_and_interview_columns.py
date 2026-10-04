"""Add clerk_id and interview columns, templates and usage tables with RLS

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-04 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Add Clerk & profile columns to users
    op.add_column('users', sa.Column('clerk_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(), nullable=True))
    op.create_index('idx_users_clerk_id', 'users', ['clerk_id'], unique=True)

    # 2. Add duration and integrity_score to interviews
    op.add_column('interviews', sa.Column('duration_minutes', sa.Integer(), server_default='30', nullable=False))
    op.add_column('interviews', sa.Column('integrity_score', sa.Float(), server_default='1.0', nullable=False))

    # 3. Create interview_templates table
    op.create_table(
        'interview_templates',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('role_title', sa.String(), nullable=False),
        sa.Column('competencies', JSONB, nullable=False, server_default='[]'),
        sa.Column('duration_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_interview_templates_tenant', 'interview_templates', ['tenant_id'])

    # 4. Create usage_records table
    op.create_table(
        'usage_records',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('interview_id', sa.String(), nullable=True),
        sa.Column('minutes_consumed', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('model_tokens_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cost_estimate_usd', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_usage_records_tenant', 'usage_records', ['tenant_id'])

    # 5. Enable RLS on new tables
    op.execute("ALTER TABLE interview_templates ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY interview_templates_tenant_isolation ON interview_templates
        FOR ALL USING (tenant_id = current_setting('app.current_tenant_id', true));
    """)

    op.execute("ALTER TABLE usage_records ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY usage_records_tenant_isolation ON usage_records
        FOR ALL USING (tenant_id = current_setting('app.current_tenant_id', true));
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS usage_records_tenant_isolation ON usage_records;")
    op.execute("DROP POLICY IF EXISTS interview_templates_tenant_isolation ON interview_templates;")

    op.drop_table('usage_records')
    op.drop_table('interview_templates')

    op.drop_column('interviews', 'integrity_score')
    op.drop_column('interviews', 'duration_minutes')

    op.drop_index('idx_users_clerk_id', table_name='users')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'clerk_id')
