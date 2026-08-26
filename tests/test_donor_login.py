from tests.test_registration import get_valid_donor_payload

def test_successful_donor_login(client):
    """Test 6: Successful donor login returning valid access token."""
    payload = get_valid_donor_payload()
    reg_res = client.post("/api/v1/auth/register", json=payload)
    assert reg_res.status_code == 201

    login_payload = {
        "email": "john.donor@example.com",
        "password": "Password123!"
    }
    response = client.post("/api/v1/auth/donor/login", json=login_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "DONOR"
    assert data["user"]["email"] == "john.donor@example.com"

def test_incorrect_donor_password(client):
    """Test 7: Reject donor login with incorrect password."""
    payload = get_valid_donor_payload()
    client.post("/api/v1/auth/register", json=payload)

    login_payload = {
        "email": "john.donor@example.com",
        "password": "WrongPassword123!"
    }
    response = client.post("/api/v1/auth/donor/login", json=login_payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.get_json()["detail"]

def test_non_existent_donor(client):
    """Test 8: Reject donor login for non-existent email."""
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "Password123!"
    }
    response = client.post("/api/v1/auth/donor/login", json=login_payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.get_json()["detail"]
