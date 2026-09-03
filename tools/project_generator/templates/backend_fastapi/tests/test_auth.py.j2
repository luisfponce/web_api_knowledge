from fastapi.testclient import TestClient


def test_register_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "username": "demo", "password": "long-enough-password"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["username"] == "demo"
    assert body["token"]["access_token"]


def test_duplicate_registration_is_conflict(client: TestClient) -> None:
    payload = {"email": "user@example.com", "username": "demo", "password": "long-enough-password"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "user_exists"
