from app.config import Config
from tests.test_registration import get_valid_donor_payload

def test_successful_admin_login(client):
    """Test 9: Successful Admin login using seeded admin credentials."""
    login_payload = {
        "email": Config.ADMIN_EMAIL,
        "password": Config.ADMIN_PASSWORD
    }
    response = client.post("/api/v1/auth/admin/login", json=login_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["role"] == "ADMIN"
    assert data["user"]["email"] == Config.ADMIN_EMAIL.lower()

def test_donor_attempting_admin_login(client):
    """Test 10: Reject donor accounts attempting to login via admin endpoint."""
    donor_payload = get_valid_donor_payload()
    client.post("/api/v1/auth/register", json=donor_payload)

    login_payload = {
        "email": "john.donor@example.com",
        "password": "Password123!"
    }
    response = client.post("/api/v1/auth/admin/login", json=login_payload)
    assert response.status_code == 401
    assert "not registered as admin" in response.get_json()["detail"]
