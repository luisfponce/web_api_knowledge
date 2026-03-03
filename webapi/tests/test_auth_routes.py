import base64

from passlib.hash import sha256_crypt
from sqlmodel import select

from models.user import User
import api.endpoints.v1.auths as auths_module


def test_signup_success(client, user_payload, db_session):
    response = client.post("/api/v1/auth/signup", json=user_payload)

    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}

    created = db_session.exec(select(User).where(User.username == user_payload["username"])).first()
    assert created is not None
    assert created.hashed_password != user_payload["hashed_password"]
    assert sha256_crypt.verify(user_payload["hashed_password"], created.hashed_password)


def test_signup_duplicate_username_returns_400(client, db_session):
    db_session.add(
        User(
            username="dup_user",
            name="dup",
            last_name="user",
            phone=5500000010,
            email="dup_user@example.com",
            hashed_password=sha256_crypt.hash("password"),
        )
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "dup_user",
            "name": "new",
            "last_name": "user",
            "phone": 5500000011,
            "email": "new_dup_user@example.com",
            "hashed_password": "password",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "username already taken"


def test_login_success_returns_token(client, user_payload):
    client.post("/api/v1/auth/signup", json=user_payload)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": user_payload["username"], "password": user_payload["hashed_password"]},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert isinstance(response.json()["access_token"], str)


def test_login_invalid_credentials_returns_401(client, db_session):
    db_session.add(
        User(
            username="known_user",
            name="known",
            last_name="user",
            phone=5500000012,
            email="known_user@example.com",
            hashed_password=sha256_crypt.hash("right_password"),
        )
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "known_user", "password": "wrong_password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_profile_success(client, auth_header, created_user):
    response = client.get("/api/v1/auth/profile", headers=auth_header)

    assert response.status_code == 200
    assert response.json()["profile darta"]["sub"] == created_user.username


def test_profile_invalid_token_returns_401(client):
    response = client.get("/api/v1/auth/profile", headers={"Authorization": "Token abc"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized token"


def test_generate_password_user_not_found_returns_404(client):
    response = client.post("/api/v1/auth/generate", params={"username": "missing_user"})

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_generate_password_key_exists_returns_400(client, db_session, fake_redis, monkeypatch):
    user = User(
        username="recover_user",
        name="recover",
        last_name="user",
        phone=5500000013,
        email="recover_user@example.com",
        hashed_password=sha256_crypt.hash("original_password"),
    )
    db_session.add(user)
    db_session.commit()

    monkeypatch.setattr(auths_module.secrets, "token_hex", lambda n: "fixedhex")
    encoded = base64.b64encode(user.username.encode("utf-8")).decode("utf-8")
    fake_redis.store[f"fixedhex.{encoded}"] = "already_exists"

    response = client.post("/api/v1/auth/generate", params={"username": user.username})

    assert response.status_code == 400
    assert response.json()["detail"] == "Key already exists"


def test_generate_password_success_saves_password_and_calls_email(client, db_session, fake_redis, monkeypatch):
    user = User(
        username="mail_user",
        name="mail",
        last_name="user",
        phone=5500000014,
        email="mail_user@example.com",
        hashed_password=sha256_crypt.hash("old_password"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    called = {"value": False}

    async def fake_send_email(to, username, body):
        called["value"] = True
        assert to == user.email
        assert username == user.username
        assert "recovery key" in body

    monkeypatch.setattr(auths_module.secrets, "token_hex", lambda n: "fixedhex2")
    monkeypatch.setattr(auths_module.secrets, "token_urlsafe", lambda n: "temporary_pwd")
    monkeypatch.setattr(auths_module, "send_email", fake_send_email)

    response = client.post("/api/v1/auth/generate", params={"username": user.username, "ttl": 600})

    assert response.status_code == 200
    assert called["value"] is True

    encoded = base64.b64encode(user.username.encode("utf-8")).decode("utf-8")
    key = f"fixedhex2.{encoded}"
    assert fake_redis.get(key) == "temporary_pwd"

    updated = db_session.get(User, user.id)
    assert sha256_crypt.verify("temporary_pwd", updated.hashed_password)


def test_generate_password_email_failure_returns_500(client, db_session, monkeypatch):
    user = User(
        username="mail_fail_user",
        name="mail",
        last_name="fail",
        phone=5500000015,
        email="mail_fail_user@example.com",
        hashed_password=sha256_crypt.hash("old_password"),
    )
    db_session.add(user)
    db_session.commit()

    async def failing_send_email(*args, **kwargs):
        raise Exception("smtp unavailable")

    monkeypatch.setattr(auths_module, "send_email", failing_send_email)

    response = client.post("/api/v1/auth/generate", params={"username": user.username})

    assert response.status_code == 500


def test_recover_invalid_key_format_returns_401(client):
    response = client.post("/api/v1/auth/recover", params={"key": "invalid_key_without_dot"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid key format"


def test_recover_decode_error_returns_401(client, monkeypatch):
    def broken_decode(_value):
        raise auths_module.binascii.Error("bad base64")

    monkeypatch.setattr(auths_module.base64, "b64decode", broken_decode)

    response = client.post("/api/v1/auth/recover", params={"key": "prefix.encoded"})

    assert response.status_code == 401
    assert response.json()["detail"].startswith("Decode error:")


def test_recover_user_not_found_returns_404(client):
    encoded = base64.b64encode("ghost_user".encode("utf-8")).decode("utf-8")
    response = client.post("/api/v1/auth/recover", params={"key": f"anyprefix.{encoded}"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Key corrputed"


def test_recover_password_not_found_in_redis_returns_404(client, db_session):
    user = User(
        username="recover_missing_pwd",
        name="recover",
        last_name="missing",
        phone=5500000016,
        email="recover_missing_pwd@example.com",
        hashed_password=sha256_crypt.hash("old_password"),
    )
    db_session.add(user)
    db_session.commit()

    encoded = base64.b64encode(user.username.encode("utf-8")).decode("utf-8")
    response = client.post("/api/v1/auth/recover", params={"key": f"anyprefix.{encoded}"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Password not found in redis or expired"


def test_recover_success_returns_key_and_password(client, db_session, fake_redis):
    user = User(
        username="recover_ok",
        name="recover",
        last_name="ok",
        phone=5500000017,
        email="recover_ok@example.com",
        hashed_password=sha256_crypt.hash("old_password"),
    )
    db_session.add(user)
    db_session.commit()

    encoded = base64.b64encode(user.username.encode("utf-8")).decode("utf-8")
    key = f"keyprefix.{encoded}"
    fake_redis.store[key] = "temporary_pwd"

    response = client.post("/api/v1/auth/recover", params={"key": key})

    assert response.status_code == 200
    assert response.json() == {"key": key, "password": "temporary_pwd"}
