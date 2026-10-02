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
