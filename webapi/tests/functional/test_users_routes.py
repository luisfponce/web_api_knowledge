from passlib.hash import sha256_crypt
from sqlmodel import select

from models.user import User
from auth.auth_service import crear_jwt


def test_read_users_success(client, auth_header, created_user):
    response = client.get("/api/v1/users", headers=auth_header)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == created_user.id


def test_read_users_with_phone_filter_success(client, auth_header, created_user):
    response = client.get(f"/api/v1/users?phone={created_user.phone}", headers=auth_header)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["phone"] == created_user.phone


def test_read_users_not_found_returns_404(client, auth_header):
    response = client.get("/api/v1/users?phone=5599998888", headers=auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_read_users_unauthorized_returns_401(client):
    response = client.get("/api/v1/users", headers={"Authorization": "Bearer invalid"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized token"


def test_get_user_success(client, auth_header, created_user):
    response = client.get(f"/api/v1/users/{created_user.id}", headers=auth_header)

    assert response.status_code == 200
    assert response.json()["id"] == created_user.id


def test_get_user_missing_returns_404(client, auth_header):
    response = client.get("/api/v1/users/9999", headers=auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_user_with_prompts_success(client, auth_header, created_user, created_prompt):
    response = client.get(f"/api/v1/users/prompts/{created_user.id}", headers=auth_header)

    assert response.status_code == 200
    assert response.json()["id"] == created_user.id
    assert len(response.json()["prompts"]) == 1
    assert response.json()["prompts"][0]["id"] == created_prompt.id


def test_get_user_with_prompts_missing_returns_404(client, auth_header):
    response = client.get("/api/v1/users/prompts/9999", headers=auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user_success(client, auth_header, created_user, db_session):
    payload = {
        "username": created_user.username,
        "name": "UPDATED",
        "last_name": "USER",
        "phone": 5599990000,
        "email": "updated_user@example.com",
        "hashed_password": "new_password",
    }

    response = client.put(f"/api/v1/users/{created_user.id}", json=payload, headers=auth_header)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "updated"
    assert body["last_name"] == "user"
    assert body["phone"] == 5599990000
    assert body["email"] == "updated_user@example.com"

    updated = db_session.get(User, created_user.id)
    assert sha256_crypt.verify("new_password", updated.hashed_password)


def test_update_user_missing_returns_404(client, auth_header):
    payload = {
        "username": "missing",
        "name": "Missing",
        "last_name": "User",
        "phone": 5511112222,
        "email": "missing_user@example.com",
        "hashed_password": "password",
    }

    response = client.put("/api/v1/users/9999", json=payload, headers=auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user_duplicate_username_returns_400(client, auth_header, created_user, db_session):
    another_user = User(
        username="taken_username",
        name="Another",
        last_name="User",
        phone=5500000090,
        email="another_user@example.com",
        hashed_password=sha256_crypt.hash("password"),
    )
    db_session.add(another_user)
    db_session.commit()

    payload = {
        "username": "taken_username",
        "name": "Updated",
        "last_name": "User",
        "phone": created_user.phone,
        "email": "updated_conflict@example.com",
        "hashed_password": "new_password",
    }

    response = client.put(f"/api/v1/users/{created_user.id}", json=payload, headers=auth_header)

    assert response.status_code == 400
    assert response.json()["detail"] == "username already taken"


def test_delete_user_success(client, auth_header, created_user):
    response = client.delete(f"/api/v1/users/{created_user.id}", headers=auth_header)

    assert response.status_code == 200
    assert response.json()["id"] == created_user.id


def test_delete_user_missing_returns_404(client, auth_header):
    response = client.delete("/api/v1/users/9999", headers=auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found to delete"


def test_delete_user_commit_exception_returns_500(client, auth_header, created_user, monkeypatch):
    from db.db_connection import get_session
    from main import myapp

    override = myapp.dependency_overrides[get_session]
    session = next(override())

    original_commit = session.commit

    def fail_commit():
        raise Exception("forced commit error")

    monkeypatch.setattr(session, "commit", fail_commit)

    response = client.delete(f"/api/v1/users/{created_user.id}", headers=auth_header)

    monkeypatch.setattr(session, "commit", original_commit)

    assert response.status_code == 500
    assert "forced commit error" in response.json()["detail"]
