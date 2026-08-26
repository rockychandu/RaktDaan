from tests.test_registration import get_valid_donor_payload

def test_donor_login_credentials_check(client):
    client.post("/api/v1/auth/register", json=get_valid_donor_payload())
    
    # Correct email & password
    res = client.post("/api/v1/auth/donor/login", json={
        "email": "john.donor@example.com",
        "password": "Password123!"
    })
    assert res.status_code == 200
    assert "access_token" in res.get_json()

def test_donor_login_wrong_password(client):
    client.post("/api/v1/auth/register", json=get_valid_donor_payload())
    
    res = client.post("/api/v1/auth/donor/login", json={
        "email": "john.donor@example.com",
        "password": "WrongPassword!1"
    })
    assert res.status_code == 401
    assert "Invalid email or password" in res.get_json()["detail"]
