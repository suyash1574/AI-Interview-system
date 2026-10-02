import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')

write_file('database/models.py', """
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    users = relationship("User", back_populates="tenant")

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    role = Column(String, nullable=False)
    tenant = relationship("Tenant", back_populates="users")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    title = Column(String, nullable=False)
    competencies = Column(JSONB, nullable=False, default=list)

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)

class Interview(Base):
    __tablename__ = "interviews"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    transcript = Column(JSONB, nullable=True)

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(String, primary_key=True, default=generate_uuid)
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False)
    score_raw = Column(Integer, nullable=True)
    evidence = Column(JSONB, nullable=True)
""")

write_file('tests/unit/test_models.py', """
import pytest
from database.models import Tenant, User, Job, Candidate, Interview, Evaluation, Base

def test_models_exist():
    # Simple test to verify models can be imported and have correct table names
    assert Tenant.__tablename__ == "tenants"
    assert User.__tablename__ == "users"
    assert Job.__tablename__ == "jobs"
    assert Candidate.__tablename__ == "candidates"
    assert Interview.__tablename__ == "interviews"
    assert Evaluation.__tablename__ == "evaluations"
""")

write_file('alembic/env.py', """
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from database.models import Base
from backend.config import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
""")

write_file('alembic/script.py.mako', '''
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
''')

print('Database models and alembic environment configured.')
