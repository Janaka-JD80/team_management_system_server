import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.deps import get_current_user
from app.schemas.auth import JwtPayload

def override_get_current_user_team_member():
    return JwtPayload(
        sub="11111111-1111-1111-1111-111111111111",
        exp=0,
        user_email="member@example.com",
        full_name="Test Member",
        roles=["team_member"],
        permissions=["create:report", "edit:own_report", "submit:report", "view:own_reports"]
    )

def override_get_current_user_manager():
    return JwtPayload(
        sub="22222222-2222-2222-2222-222222222222",
        exp=0,
        user_email="manager@example.com",
        full_name="Test Manager",
        roles=["manager"],
        permissions=["view:all_reports", "review:report", "view:dashboard", "manage:projects"]
    )

client = TestClient(app)

def test_team_member_cannot_access_manager_endpoint():
    app.dependency_overrides[get_current_user] = override_get_current_user_team_member
    
    response = client.get("/api/v1/reports/")
    assert response.status_code == 403
    assert response.json()["message"] == "Operation requires 'view:all_reports' permission"
    
    app.dependency_overrides.clear()

def test_manager_can_access_manager_endpoint():
    app.dependency_overrides[get_current_user] = override_get_current_user_manager
    
    response = client.get("/api/v1/reports/")
    assert response.status_code != 403
    
    app.dependency_overrides.clear()

def test_team_member_cannot_create_project():
    app.dependency_overrides[get_current_user] = override_get_current_user_team_member
    
    response = client.post("/api/v1/projects/", json={"name": "Test", "description": "Desc"})
    assert response.status_code == 403
    assert response.json()["message"] == "Operation requires 'manage:projects' permission"
    
    app.dependency_overrides.clear()
