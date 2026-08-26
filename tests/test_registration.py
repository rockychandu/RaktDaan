def get_valid_donor_payload():
    return {
        "name": "John Donor",
        "email": "john.donor@example.com",
        "phone": "9876543210",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "date_of_birth": "1995-05-15",
        "gender": "Male",
        "blood_group": "O+",
        "address": "124 Blood Bank Avenue",
        "city": "Mumbai",
        "state": "Maharashtra",
        "emergency_contact": "9876543211"
    }

def test_successful_donor_registration(client):
    """Test 1: Successful donor registration with valid data."""
    payload = get_valid_donor_payload()
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    res_json = response.get_json()
    data = res_json.get("data", res_json)
    assert data["email"] == "john.donor@example.com"
    assert data["role"] == "DONOR"
    assert data["donor_profile"]["blood_group"] == "O+"
    assert data["donor_profile"]["city"] == "Mumbai"

def test_duplicate_email_registration(client):
    """Test 2: Prevent registration with duplicate email."""
    payload = get_valid_donor_payload()
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 422
    assert "already registered" in str(res2.get_json()["detail"])

def test_invalid_email(client):
    """Test 3: Reject registration with invalid email format."""
    payload = get_valid_donor_payload()
    payload["email"] = "invalid-email-syntax"
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert "Invalid email format" in str(response.get_json()["detail"])

def test_weak_password(client):
    """Test 4: Reject registration with weak password."""
    payload = get_valid_donor_payload()
    payload["password"] = "weak"
    payload["confirm_password"] = "weak"
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert "at least 8 characters" in str(response.get_json()["detail"])

def test_password_mismatch(client):
    """Test 5: Reject registration when password confirmation does not match."""
    payload = get_valid_donor_payload()
    payload["confirm_password"] = "DifferentPassword123!"
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert "do not match" in str(response.get_json()["detail"])
