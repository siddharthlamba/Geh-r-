"""
Integration test suite for Gehor API Endpoints with AI Intelligence Layer.
Tests:
- GET /api/complaints/{id}/resolution-brief
- PATCH /api/complaints/{id} with department update & supervised learning recording
- GET /api/settings/learning-stats
"""

import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import StaticPool
from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app.seed_data import seed_database
from backend.app.models import Complaint

# Set up test database fixture with StaticPool so all threads/sessions share the in-memory db
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    yield db
    db.close()

@pytest.fixture
def client():
    return TestClient(app)


def test_get_complaint_resolution_brief(client, setup_test_db):
    # Fetch first seeded complaint
    comp = setup_test_db.query(Complaint).first()
    assert comp is not None

    response = client.get(f"/api/complaints/{comp.id}/resolution-brief")
    assert response.status_code == 200
    data = response.json()
    assert "complaint_id" in data
    assert "step_by_step_plan" in data
    assert len(data["step_by_step_plan"]) > 0
    assert "incident_summary" in data
    assert "responsible_recipient" in data


def test_update_complaint_records_supervised_learning(client, setup_test_db):
    comp = setup_test_db.query(Complaint).first()
    assert comp is not None
    original_dept = comp.department_name

    new_dept = "IT Services" if original_dept != "IT Services" else "Maintenance & Engineering"

    # Reassign department via PATCH
    patch_response = client.patch(
        f"/api/complaints/{comp.id}",
        json={
            "department_name": new_dept,
            "performed_by": "Test Administrator"
        }
    )
    assert patch_response.status_code == 200
    updated_comp = patch_response.json()
    assert updated_comp["department_name"] == new_dept

    # Verify learning stats reflect supervisor correction
    stats_response = client.get("/api/settings/learning-stats")
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["total_feedback_samples"] >= 1
    assert stats["corrected_count"] >= 1
