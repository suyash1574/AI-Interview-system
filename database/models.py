from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    
    users = relationship("User", back_populates="tenant")
    company = relationship("Company", back_populates="tenant", uselist=False)
    jobs = relationship("Job", back_populates="tenant")
    drives = relationship("Drive", back_populates="tenant")

class Company(Base):
    __tablename__ = "companies"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), unique=True, nullable=False)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=True)
    tier = Column(String, nullable=False, default="ENTERPRISE")
    settings = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    tenant = relationship("Tenant", back_populates="company")

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    email = Column(String, nullable=False)
    name = Column(String, nullable=True)
    role = Column(String, nullable=False, default="RECRUITER") # SUPER_ADMIN, COMPANY_ADMIN, RECRUITER
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    tenant = relationship("Tenant", back_populates="users")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    competencies = Column(JSONB, nullable=False, default=list) # [{name, type, score}]
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    tenant = relationship("Tenant", back_populates="jobs")
    drives = relationship("Drive", back_populates="job")
    interviews = relationship("Interview", back_populates="job")

class Drive(Base):
    __tablename__ = "drives"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="ACTIVE") # DRAFT, ACTIVE, PAUSED, COMPLETED
    pass_threshold = Column(Integer, nullable=False, default=70)
    config = Column(JSONB, nullable=False, default=dict) # durations, required_sections, difficulty
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    tenant = relationship("Tenant", back_populates="drives")
    job = relationship("Job", back_populates="drives")
    invitations = relationship("Invitation", back_populates="drive")
    interviews = relationship("Interview", back_populates="drive")

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    resumes = relationship("Resume", back_populates="candidate")
    interviews = relationship("Interview", back_populates="candidate")
    invitations = relationship("Invitation", back_populates="candidate")

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_url = Column(String, nullable=True)
    parsed_text = Column(Text, nullable=True)
    extracted_skills = Column(JSONB, nullable=False, default=list)
    extracted_experience = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    candidate = relationship("Candidate", back_populates="resumes")

class Invitation(Base):
    __tablename__ = "invitations"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    drive_id = Column(String, ForeignKey("drives.id"), nullable=False)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    email = Column(String, nullable=False)
    token = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False, default="PENDING") # PENDING, SENT, OPENED, COMPLETED, EXPIRED
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    drive = relationship("Drive", back_populates="invitations")
    candidate = relationship("Candidate", back_populates="invitations")

class Interview(Base):
    __tablename__ = "interviews"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    drive_id = Column(String, ForeignKey("drives.id"), nullable=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=True)
    status = Column(String, nullable=False, default="PENDING") # PENDING, IN_PROGRESS, COMPLETED, FAILED
    transcript = Column(JSONB, nullable=True, default=list) # [{"speaker": "AI"|"CANDIDATE", "text": "...", "timestamp": ...}]
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    job = relationship("Job", back_populates="interviews")
    drive = relationship("Drive", back_populates="interviews")
    candidate = relationship("Candidate", back_populates="interviews")
    evaluations = relationship("Evaluation", back_populates="interview")
    integrity_events = relationship("IntegrityEvent", back_populates="interview")
    reports = relationship("Report", back_populates="interview")

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False)
    overall_score = Column(Integer, nullable=True) # 0-100
    recommendation = Column(String, nullable=True) # PASS, HOLD, REJECT
    summary = Column(Text, nullable=True)
    score_raw = Column(Integer, nullable=True)
    evidence = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    interview = relationship("Interview", back_populates="evaluations")
    agent_runs = relationship("AgentRun", back_populates="evaluation")

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    evaluation_id = Column(String, ForeignKey("evaluations.id"), nullable=False)
    agent_name = Column(String, nullable=False) # TECHNICAL, BEHAVIORAL, COMMUNICATION
    score = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    feedback = Column(Text, nullable=True)
    evidence_citations = Column(JSONB, nullable=False, default=list)
    raw_output = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    evaluation = relationship("Evaluation", back_populates="agent_runs")

class IntegrityEvent(Base):
    __tablename__ = "integrity_events"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False)
    session_id = Column(String, nullable=True)
    event_type = Column(String, nullable=False) # TAB_SWITCH, WINDOW_BLUR, MULTIPLE_FACES, NO_FACE, AUDIO_ANOMALY
    severity = Column(String, nullable=False, default="LOW") # LOW, MEDIUM, HIGH
    confidence = Column(Float, nullable=True, default=1.0)
    details = Column(JSONB, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=get_utc_now)

    interview = relationship("Interview", back_populates="integrity_events")

class Report(Base):
    __tablename__ = "reports"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False)
    pdf_url = Column(String, nullable=False)
    report_type = Column(String, nullable=False, default="RECRUITER") # RECRUITER, CANDIDATE
    status = Column(String, nullable=False, default="READY") # PENDING, READY, FAILED
    metadata_info = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    interview = relationship("Interview", back_populates="reports")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String, nullable=True)
    action = Column(String, nullable=False) # e.g. CREATE_DRIVE, EXPORT_REPORT, INVITE_CANDIDATES
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    details = Column(JSONB, nullable=False, default=dict)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String, nullable=True) # None = all tenant recruiters
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False, default="INFO") # INFO, SUCCESS, WARNING, ALERT
    is_read = Column(Boolean, nullable=False, default=False)
    link = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
