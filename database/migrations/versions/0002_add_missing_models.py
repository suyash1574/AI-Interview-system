"""Add missing models and RLS policies

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-03 18:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Update existing tables with missing columns
    op.add_column('tenants', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('jobs', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('jobs', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('candidates', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))

    # 2. Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('domain', sa.String(), nullable=True),
        sa.Column('tier', sa.String(), nullable=False, server_default='ENTERPRISE'),
        sa.Column('settings', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )

    # 3. Create drives table
    op.create_table(
        'drives',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_id', sa.String(), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='ACTIVE'),
        sa.Column('pass_threshold', sa.Integer(), nullable=False, server_default='70'),
        sa.Column('config', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_drives_tenant', 'drives', ['tenant_id'])

    # 4. Create resumes table
    op.create_table(
        'resumes',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('candidate_id', sa.String(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_url', sa.String(), nullable=True),
        sa.Column('parsed_text', sa.Text(), nullable=True),
        sa.Column('extracted_skills', JSONB, nullable=False, server_default='[]'),
        sa.Column('extracted_experience', JSONB, nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_resumes_tenant', 'resumes', ['tenant_id'])
    op.create_index('idx_resumes_candidate', 'resumes', ['candidate_id'])

    # 5. Create invitations table
    op.create_table(
        'invitations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('drive_id', sa.String(), sa.ForeignKey('drives.id', ondelete='CASCADE'), nullable=False),
        sa.Column('candidate_id', sa.String(), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('token', sa.String(), unique=True, nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='PENDING'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_invitations_token', 'invitations', ['token'])
    op.create_index('idx_invitations_tenant', 'invitations', ['tenant_id'])

    # 6. Update interviews table with drive_id, resume_id, created_at
    op.add_column('interviews', sa.Column('drive_id', sa.String(), sa.ForeignKey('drives.id', ondelete='SET NULL'), nullable=True))
    op.add_column('interviews', sa.Column('resume_id', sa.String(), sa.ForeignKey('resumes.id', ondelete='SET NULL'), nullable=True))
    op.add_column('interviews', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))

    # 7. Update evaluations table with tenant_id, overall_score, recommendation, summary, created_at
    op.add_column('evaluations', sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=True))
    op.add_column('evaluations', sa.Column('overall_score', sa.Integer(), nullable=True))
    op.add_column('evaluations', sa.Column('recommendation', sa.String(), nullable=True))
    op.add_column('evaluations', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('evaluations', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))

    # 8. Create agent_runs table
    op.create_table(
        'agent_runs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('evaluation_id', sa.String(), sa.ForeignKey('evaluations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agent_name', sa.String(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('evidence_citations', JSONB, nullable=False, server_default='[]'),
        sa.Column('raw_output', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_agent_runs_eval', 'agent_runs', ['evaluation_id'])

    # 9. Create integrity_events table
    op.create_table(
        'integrity_events',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('interview_id', sa.String(), sa.ForeignKey('interviews.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False, server_default='LOW'),
        sa.Column('confidence', sa.Float(), nullable=True, server_default='1.0'),
        sa.Column('details', JSONB, nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_integrity_interview', 'integrity_events', ['interview_id'])
    op.create_index('idx_integrity_event_type', 'integrity_events', ['interview_id', 'event_type'])

    # 10. Enable RLS on all newly added multi-tenant tables
    for table in ['companies', 'drives', 'resumes', 'invitations', 'evaluations', 'agent_runs', 'integrity_events']:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"""
            CREATE POLICY tenant_isolation_policy ON {table}
            USING (tenant_id = current_setting('app.current_tenant', true));
        """)


def downgrade() -> None:
    for table in ['companies', 'drives', 'resumes', 'invitations', 'evaluations', 'agent_runs', 'integrity_events']:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_policy ON {table};")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")

    op.drop_table('integrity_events')
    op.drop_table('agent_runs')
    op.drop_table('invitations')
    op.drop_table('resumes')
    op.drop_table('drives')
    op.drop_table('companies')

    op.drop_column('evaluations', 'created_at')
    op.drop_column('evaluations', 'summary')
    op.drop_column('evaluations', 'recommendation')
    op.drop_column('evaluations', 'overall_score')
    op.drop_column('evaluations', 'tenant_id')

    op.drop_column('interviews', 'created_at')
    op.drop_column('interviews', 'resume_id')
    op.drop_column('interviews', 'drive_id')

    op.drop_column('candidates', 'created_at')
    op.drop_column('candidates', 'phone')
    op.drop_column('jobs', 'created_at')
    op.drop_column('jobs', 'description')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'name')
    op.drop_column('tenants', 'created_at')
