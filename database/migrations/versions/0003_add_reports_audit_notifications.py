"""Add reports, audit_logs, and notifications tables with RLS

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-04 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('interview_id', sa.String(), sa.ForeignKey('interviews.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pdf_url', sa.String(), nullable=False),
        sa.Column('report_type', sa.String(), nullable=False, server_default='RECRUITER'),
        sa.Column('status', sa.String(), nullable=False, server_default='READY'),
        sa.Column('metadata_info', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_reports_tenant', 'reports', ['tenant_id'])
    op.create_index('idx_reports_interview', 'reports', ['interview_id'])

    # 2. Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=False),
        sa.Column('resource_id', sa.String(), nullable=True),
        sa.Column('details', JSONB, nullable=False, server_default='{}'),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_audit_logs_tenant', 'audit_logs', ['tenant_id'])
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])

    # 3. Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(), nullable=False, server_default='INFO'),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('link', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_notifications_tenant_user', 'notifications', ['tenant_id', 'user_id'])

    # 4. Enable RLS on newly created tables
    op.execute("ALTER TABLE reports ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY reports_tenant_isolation ON reports
        FOR ALL USING (tenant_id = current_setting('app.current_tenant_id', true));
    """)

    op.execute("ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY audit_logs_tenant_isolation ON audit_logs
        FOR ALL USING (tenant_id = current_setting('app.current_tenant_id', true));
    """)

    op.execute("ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY notifications_tenant_isolation ON notifications
        FOR ALL USING (tenant_id = current_setting('app.current_tenant_id', true));
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS notifications_tenant_isolation ON notifications;")
    op.execute("DROP POLICY IF EXISTS audit_logs_tenant_isolation ON audit_logs;")
    op.execute("DROP POLICY IF EXISTS reports_tenant_isolation ON reports;")

    op.drop_table('notifications')
    op.drop_table('audit_logs')
    op.drop_table('reports')
