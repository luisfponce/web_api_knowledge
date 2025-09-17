from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

TEST_USER = "testuser"
TEST_PSW  = "testPSW"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "Bank App": "This is a simple app using FastAPI and mariadb."
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


def test_register_card():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "send_email": "false"}
    response = client.post("/api/v1/cards/cards", json={
        "user_id": 1,
        "card_type": "visa",
        "card_number": "5256010203040506",
        "expiration_date": "01/2025",
    },  headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "card_number": "5256010203040506",
        "user_id": 1,
        "card_type": "visa",
        "expiration_date": "01/2025"
    }

def test_read_users():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200


def test_read_cards():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/cards", headers=headers)
    assert response.status_code == 200