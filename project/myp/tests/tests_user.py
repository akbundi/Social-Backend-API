from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_and_login():
    res = client.post("/users/register", json={"name": "Test", "email": "test@example.com", "password": "pass123"})
    assert res.status_code == 200

    res = client.post("/users/login", json={"email": "test@example.com", "password": "pass123"})
    assert res.status_code == 200
    assert "access_token" in res.json()
