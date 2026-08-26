from tests.test_registration import get_valid_donor_payload

def test_registration_missing_required_fields(client):
    payload = {"name": "Test User"}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    data = response.get_json()
    assert "email" in str(data["detail"])
    assert "phone" in str(data["detail"])

def test_registration_underage_donor(client):
    payload = get_valid_donor_payload()
    payload["email"] = "underage@example.com"
    payload["date_of_birth"] = "2020-01-01" # 6 years old
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert "at least 18 years old" in str(response.get_json()["detail"])

def test_registration_invalid_blood_group(client):
    payload = get_valid_donor_payload()
    payload["email"] = "badblood@example.com"
    payload["blood_group"] = "C+"
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert "Invalid blood group" in str(response.get_json()["detail"])

def test_registration_invalid_phone_number(client):
    payload = get_valid_donor_payload()
    payload["email"] = "badphone@example.com"
    payload["phone"] = "123" # Too short
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert "10 to 15 numeric digits" in str(response.get_json()["detail"])
