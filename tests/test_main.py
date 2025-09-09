from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "Bank App": "This is a simple app using FastAPI and mariadb."
    }

def test_login_and_access_private():
    # First, get a token
    response = client.post("/api/v1/auth/login", json={  # <-- use json instead of data
        "username": "a",
        "password": "a"
    })
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
