import pytest
from database.models import (
    Tenant, 
    Company, 
    User, 
    Job, 
    Drive, 
    Candidate, 
    Resume, 
    Invitation, 
    Interview, 
    Evaluation, 
    AgentRun, 
    IntegrityEvent, 
    Base
)

def test_models_exist():
    assert Tenant.__tablename__ == "tenants"
    assert Company.__tablename__ == "companies"
    assert User.__tablename__ == "users"
    assert Job.__tablename__ == "jobs"
    assert Drive.__tablename__ == "drives"
    assert Candidate.__tablename__ == "candidates"
    assert Resume.__tablename__ == "resumes"
    assert Invitation.__tablename__ == "invitations"
    assert Interview.__tablename__ == "interviews"
    assert Evaluation.__tablename__ == "evaluations"
    assert AgentRun.__tablename__ == "agent_runs"
    assert IntegrityEvent.__tablename__ == "integrity_events"
