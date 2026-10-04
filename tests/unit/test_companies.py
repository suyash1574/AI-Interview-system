import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.dependencies.auth import get_current_user, CurrentUser
from backend.dependencies.db import get_tenant_db
from database.models import Company

@pytest.fixture
def mock_admin():
    return CurrentUser(user_id="admin-1", tenant_id="tenant-acme", role="COMPANY_ADMIN")

@pytest.fixture
def mock_db():
    return AsyncMock()

def test_create_company(mock_admin, mock_db):
    app.dependency_overrides[get_current_user] = lambda: mock_admin
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    # No existing company
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res

    client = TestClient(app)
    response = client.post(
        "/api/v1/companies",
        json={
            "name": "Acme Corp",
            "domain": "acme.com",
            "tier": "ENTERPRISE",
            "settings": {"brand_color": "#0284c7"}
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Acme Corp"
    assert data["domain"] == "acme.com"
    assert data["tier"] == "ENTERPRISE"
    assert mock_db.add.called
    assert mock_db.commit.called

    app.dependency_overrides.clear()

def test_get_my_company(mock_admin, mock_db):
    app.dependency_overrides[get_current_user] = lambda: mock_admin
    app.dependency_overrides[get_tenant_db] = lambda: mock_db

    fake_company = Company(
        id="comp-1",
        tenant_id="tenant-acme",
        name="Acme Corp",
        domain="acme.com",
        tier="ENTERPRISE",
        settings={"sso_enabled": True}
    )
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = fake_company
    mock_db.execute.return_value = mock_res

    client = TestClient(app)
    response = client.get("/api/v1/companies/me")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Acme Corp"
    assert data["settings"]["sso_enabled"] is True

    app.dependency_overrides.clear()
