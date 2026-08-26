from tests.test_registration import get_valid_donor_payload

def test_full_donor_onboarding_workflow(client):
    """
    Tests complete donor registration, profile creation, login, and dashboard access.
    """
    payload = get_valid_donor_payload()
    reg_res = client.post("/api/v1/auth/register", json=payload)
    assert reg_res.status_code == 201

    login_res = client.post("/api/v1/auth/donor/login", json={
        "email": "john.donor@example.com",
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    dash_res = client.get("/api/v1/auth/donor/dashboard-data", headers=headers)
    assert dash_res.status_code == 200
    data = dash_res.get_json()
    assert data["blood_group"] == "O+"
