from app.config import Config

def test_seeded_admin_login(client):
    res = client.post("/api/v1/auth/admin/login", json={
        "email": Config.ADMIN_EMAIL,
        "password": Config.ADMIN_PASSWORD
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["role"] == "ADMIN"
    assert data["user"]["email"] == Config.ADMIN_EMAIL.lower()
