from app.config import Config
from app.utils.security import hash_password, verify_password
from tests.test_registration import get_valid_donor_payload

def test_unauthorized_access_protected_routes(client):
    """Test 11: Ensure protected routes reject unauthenticated requests."""
    res_me = client.get("/api/v1/auth/me")
    assert res_me.status_code == 401

    res_donor = client.get("/api/v1/auth/donor/dashboard-data")
    assert res_donor.status_code == 401

    res_admin = client.get("/api/v1/auth/admin/dashboard-data")
    assert res_admin.status_code == 401

def test_admin_access_to_admin_routes(client):
    """Test 12: Admin can access admin routes; donor cannot access admin routes."""
    # 1. Login as Admin
    admin_login_res = client.post("/api/v1/auth/admin/login", json={
        "email": Config.ADMIN_EMAIL,
        "password": Config.ADMIN_PASSWORD
    })
    admin_token = admin_login_res.get_json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin accesses admin route -> 200 OK
    res_admin_access = client.get("/api/v1/auth/admin/dashboard-data", headers=admin_headers)
    assert res_admin_access.status_code == 200

    # 2. Register & Login as Donor
    client.post("/api/v1/auth/register", json=get_valid_donor_payload())
    donor_login_res = client.post("/api/v1/auth/donor/login", json={
        "email": "john.donor@example.com",
        "password": "Password123!"
    })
    donor_token = donor_login_res.get_json()["access_token"]
    donor_headers = {"Authorization": f"Bearer {donor_token}"}

    # Donor accesses donor route -> 200 OK
    res_donor_access = client.get("/api/v1/auth/donor/dashboard-data", headers=donor_headers)
    assert res_donor_access.status_code == 200

    # Donor attempts to access admin route -> 403 Forbidden
    res_forbidden = client.get("/api/v1/auth/admin/dashboard-data", headers=donor_headers)
    assert res_forbidden.status_code == 403
    assert "System Administrators only" in res_forbidden.get_json()["detail"]

def test_logout(client):
    """Test 13: Logout endpoint requires auth token and returns success message."""
    client.post("/api/v1/auth/register", json=get_valid_donor_payload())
    donor_login_res = client.post("/api/v1/auth/donor/login", json={
        "email": "john.donor@example.com",
        "password": "Password123!"
    })
    token = donor_login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res_logout = client.post("/api/v1/auth/logout", headers=headers)
    assert res_logout.status_code == 200
    assert res_logout.get_json()["success"] is True

def test_password_hash_verification():
    """Test 14: Verify password hashing and verification functionality."""
    raw_pwd = "MySecretPassword123!"
    hashed = hash_password(raw_pwd)

    # Hashes must never be plain text
    assert hashed != raw_pwd

    # Verify password match
    assert verify_password(raw_pwd, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False
