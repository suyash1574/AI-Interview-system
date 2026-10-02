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
