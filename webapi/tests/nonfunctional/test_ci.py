from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from main import myapp
client = TestClient(myapp)

TEST_USER = "testuser"
TEST_PSW  = "testPSW"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "Portfolio App": "This is a simple app using FastAPI and mariadb."
    }


def test_register_user():
    response = client.post("/api/v1/auth/signup", json={
        "username": TEST_USER,
        "name": "user to test",
        "last_name": "my webapp",
        "phone": 3132333435,
        "email": "pytestmyapp@testing.com",
        "hashed_password": TEST_PSW
    })
    assert response.status_code == 200
    assert response.json() == {
        "message": "User created successfully"
    }

def get_token():
    response = client.post("/api/v1/auth/login", json={
        "username": TEST_USER,
        "password": TEST_PSW
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token


def test_register_prompt():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "send_email": "false"}
    response = client.post("/api/v1/prompts", json={
        "user_id": 1,
        "model_name": "gpt-4.1",
        "prompt_text": "Generate a test response",
        "category": "qa",
        "rate": "high",
    },  headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "user_id": 1,
        "model_name": "gpt-4.1",
        "prompt_text": "Generate a test response",
        "category": "qa",
        "rate": "high"
    }

def test_read_users():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200


def test_read_prompts():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/prompts", headers=headers)
    assert response.status_code == 200
