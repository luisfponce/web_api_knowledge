from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from main import myapp

client = TestClient(myapp)


def test_login_and_access_private():
    # Ensure user exists; tolerate pre-existing data in local DB runs
    signup_response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "pytest",
            "name": "Py",
            "last_name": "Tester",
            "phone": 5511111111,
            "email": "pytest@example.com",
            "hashed_password": "pytest",
        },
    )
    assert signup_response.status_code in (200, 400)
    if signup_response.status_code == 400:
        assert signup_response.json().get("detail") == "username already taken"

    # First, get a token
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "pytest",
            "password": "pytest",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Then, call private route with that token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200

def test_failed_login_and_access_private():
    response = client.post("/api/v1/auth/login", json={  # <-- use json instead of data
        "username": "teest_non_admitable_user",
        "password": "teest_non_admitable_user"
    })
    assert response.status_code == 401
    token = None
    try:
        token = response.json()["access_token"]
    except:
        assert True
    assert token == None

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 401
